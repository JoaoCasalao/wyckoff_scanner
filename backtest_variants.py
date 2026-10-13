#!/usr/bin/env python3
"""
Backtest of three published additions to the Wyckoff scanner.

Variants (parameters fixed from the papers, no tuning):
  base      live scanner, top 10 by score per date and horizon
  hi52      short and medium re-ranked by close / 52-week high (George and Hwang, 2004)
  resmom    candidates kept only if their residual momentum is in the top third of all
            eligible stocks that date, then top 10 by score (Blitz, Huij and Martens, 2011)
  hi52_res  both: resmom filter, then ranked by 52-week high
  trend     base, but no new signals while SPY is below its 10-month average (Faber, 2007)

Every variant is scored like the live experiment (TP1 before stop inside the
horizon window) and compared with random eligible stocks on the same date with
the same % levels. Results are split into 2019-2022 and 2023-2026.

Point-in-time rules
  - Scan functions come from wyckoff_scanner.py unchanged, via backtest.py.
  - 52-week high uses the 252 daily bars up to the scan date.
  - Residual momentum uses completed months only: 36 monthly returns regressed on SPY,
    residuals summed over months t-12 to t-2 and divided by their standard deviation.
  - The trend filter uses completed month-end closes of SPY.

Usage
  python backtest_variants.py
  python backtest_variants.py --limit 100 --cache backtest_cache.pkl

Dependencies: pandas, numpy, yfinance
"""
import argparse
import logging
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

import backtest as bt
import signal_tracker as st
import wyckoff_scanner as ws

OUT = Path("backtest_variants")
TOP_N = ws.CONFIG["top_n"]
PERIODS = (("2019-2022", "2019-01-01", "2022-12-31"), ("2023-2026", "2023-01-01", "2026-12-31"))

log = logging.getLogger("variants")

SPY_M = None   # SPY month-end closes, set before the pool starts


# ---------------------------------------------------------------- features

def monthly_returns(m_close):
    """Stock and SPY returns per completed month, aligned."""
    return pd.concat([m_close.pct_change(), SPY_M.pct_change()], axis=1, keys=["r", "m"]).dropna()


def residual_momentum(mr, fri):
    """Blitz-Huij-Martens residual momentum from completed months up to fri."""
    df = mr[mr.index <= fri].iloc[-36:]
    if len(df) < 36:
        return np.nan
    x = df["m"].values
    y = df["r"].values
    xm = x - x.mean()
    beta = (xm * (y - y.mean())).sum() / (xm ** 2).sum()
    alpha = y.mean() - beta * x.mean()
    e = y - alpha - beta * x
    form = e[-12:-1]
    sd = form.std(ddof=1)
    return float(form.sum() / sd) if sd > 0 else np.nan


def scan_ticker(t):
    """Same replay as backtest.scan_ticker, plus point-in-time features."""
    ws.to_weekly = bt._weekly_cut
    d_full = bt.FRAMES[t]
    w_full = bt._ORIG_TO_WEEKLY(d_full)
    mr = monthly_returns(d_full["Close"].resample("ME").last())
    dollar_vol = (d_full["Close"] * d_full["Volume"]).rolling(20).mean()
    picks, eligible = [], []

    for fri in bt.DATES:
        d = d_full.loc[:fri]
        if d.empty or (fri - d.index[-1]).days > 6:
            continue
        d = d.iloc[-bt.LOOKBACK:]
        if len(d) < 250:
            continue
        last = d.index[-1]
        close = float(d["Close"].iloc[-1])
        if close < ws.CONFIG["min_price"] or not dollar_vol.loc[last] >= ws.CONFIG["min_dollar_vol"]:
            continue
        w = w_full.loc[d.index[0]:fri]
        assert d.index[-1] <= fri and w.index[-1] <= fri, f"leak {t} {fri}"
        hi52 = close / float(d["High"].iloc[-252:].max())
        rmom = residual_momentum(mr, fri)
        eligible.append((fri, t, close, last, hi52, rmom))
        bt._CUR["w"] = w
        spy = bt.SPY_C.loc[:fri]
        for key, (_, fn) in ws.SCANS.items():
            try:
                r = fn(d, spy)
            except Exception:
                continue
            if r:
                r.update(ticker=t, horizon=key, scan_file_date=fri.date().isoformat(),
                         bar_date=last.date().isoformat(), hi52=hi52, resmom=rmom)
                picks.append(r)
    return picks, eligible


def replay(tickers, processes):
    with mp.get_context("fork").Pool(processes) as pool:
        results = pool.map(scan_ticker, tickers, chunksize=8)
    picks = pd.DataFrame([p for ps, _ in results for p in ps])
    elig = pd.DataFrame([e for _, es in results for e in es],
                        columns=["fri", "ticker", "close", "bar", "hi52", "resmom"])
    return picks, elig


# ---------------------------------------------------------------- variants

def top_by(c, col):
    c = c.sort_values(["scan_file_date", "horizon", col], ascending=[True, True, False])
    c = c.copy()
    c["rank"] = c.groupby(["scan_file_date", "horizon"]).cumcount() + 1
    return c[c["rank"] <= TOP_N]


def spy_trend_up(spy):
    """True on dates when the last completed SPY month-end close is above its 10-month average."""
    m = spy["Close"].resample("ME").last()
    up = (m > m.rolling(10).mean())
    return lambda day: bool(up[up.index <= pd.Timestamp(day)].iloc[-1]) if (up.index <= pd.Timestamp(day)).any() else True


def build_variants(cands, elig, spy):
    cands = cands.copy()
    # residual momentum percentile against every eligible stock that date
    elig = elig.copy()
    elig["rm_pct"] = elig.groupby("fri")["resmom"].rank(pct=True)
    key = elig.assign(scan_file_date=elig["fri"].dt.date.astype(str))[["scan_file_date", "ticker", "rm_pct"]]
    cands = cands.merge(key, on=["scan_file_date", "ticker"], how="left")
    strong = cands["rm_pct"] >= 2 / 3
    sm = cands["horizon"].isin(["short", "medium"])
    up = spy_trend_up(spy)
    trend_ok = cands["scan_file_date"].map(up)

    return {
        "base": top_by(cands, "score"),
        "hi52": top_by(cands[sm], "hi52"),
        "resmom": top_by(cands[strong], "score"),
        "hi52_res": top_by(cands[sm & strong], "hi52"),
        "trend": top_by(cands[trend_ok], "score"),
    }


# ---------------------------------------------------------------- scoring

def resolution_dates(df, cal):
    """Calendar date when each resolved signal hit TP1 or the stop."""
    pos = cal.searchsorted(pd.to_datetime(df["signal_date"]))
    days = df[["tp1_day", "stop_day"]].min(axis=1)
    out = []
    for p, n in zip(pos, days):
        out.append(cal[min(p + int(n), len(cal) - 1)] if np.isfinite(n) else pd.NaT)
    return pd.Series(out, index=df.index)


def max_drawdown_r(df, cal, weight=1.0):
    res = df[df["status"].isin(["tp1_first", "stop_first"])].copy()
    if res.empty:
        return np.nan, np.nan
    res["when"] = resolution_dates(res, cal)
    curve = (res.sort_values("when")["r"] * weight).cumsum()
    dd = (curve.cummax() - curve).max()
    return float(dd), float(curve.iloc[-1])


def paired_gap(sig, ctl, rng, n=4000):
    a = sig[sig["status"].isin(["tp1_first", "stop_first"])].set_index("signal_id")["r"]
    b = ctl[ctl["status"].isin(["tp1_first", "stop_first"])].groupby("signal_id_of")["r"].mean()
    d = (a.to_frame("s").join(b.rename("c"), how="inner")).eval("s - c").values
    if len(d) < 10:
        return np.nan, np.nan, np.nan, len(d)
    m = rng.choice(d, (n, len(d))).mean(axis=1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), len(d)


def score_block(sig, ctl, cal, rng):
    res = sig[sig["status"].isin(["tp1_first", "stop_first"])]
    cres = ctl[ctl["status"].isin(["tp1_first", "stop_first"])]
    p1 = (res["status"] == "tp1_first").mean() if len(res) else np.nan
    p2 = (cres["status"] == "tp1_first").mean() if len(cres) else np.nan
    n1, n2 = len(res), len(cres)
    pp = (p1 * n1 + p2 * n2) / (n1 + n2) if n1 and n2 else np.nan
    se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2)) if n1 and n2 else np.nan
    gap, lo, hi, npair = paired_gap(sig, ctl, rng)
    dd, total = max_drawdown_r(sig, cal)
    cdd, ctotal = max_drawdown_r(ctl, cal, 1 / bt.N_CONTROLS)
    return {
        "signals": len(sig), "resolved": n1,
        "tp1_rate": p1 * 100, "ctl_tp1_rate": p2 * 100,
        "z_vs_ctl": (p1 - p2) / se if se and se > 0 else np.nan,
        "avg_r": res["r"].mean(), "ctl_avg_r": cres["r"].mean(),
        "gap_r": gap, "gap_lo": lo, "gap_hi": hi, "pairs": npair,
        "total_r": total, "max_dd_r": dd, "ctl_total_r": ctotal, "ctl_max_dd_r": cdd,
    }


def keep_verdict(rows):
    """Pre-registered rule: gap above 0 in both periods and full-period 95% interval above 0."""
    p = {r["period"]: r for r in rows}
    ok = all(np.isfinite(p[k]["gap_r"]) and p[k]["gap_r"] > 0 for k in ("2019-2022", "2023-2026"))
    full = p["all"]
    return "keep" if ok and np.isfinite(full["gap_lo"]) and full["gap_lo"] > 0 else "drop"


def fmt(v, nd=2):
    return "–" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"


# ---------------------------------------------------------------- main

def main():
    global SPY_M
    ap = argparse.ArgumentParser(description="Backtest of published additions to the Wyckoff scanner")
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--processes", type=int, default=max(1, mp.cpu_count()))
    ap.add_argument("--cache", default="backtest_cache.pkl")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    OUT.mkdir(exist_ok=True)
    t0 = time.time()

    cache = Path(args.cache)
    if cache.exists():
        frames = pd.read_pickle(cache)
    else:
        names = ws.load_nyse_universe()
        tickers = sorted(names)[:args.limit] if args.limit else sorted(names)
        frames = bt.download(tickers + ["SPY"], cache)
    if args.limit:
        keep = sorted(t for t in frames if t != "SPY")[:args.limit]
        frames = {t: frames[t] for t in keep + ["SPY"]}
    spy = frames.pop("SPY")
    bt.FRAMES, bt.SPY_C = frames, spy["Close"]
    bt.DATES = list(pd.date_range(args.start, spy.index[-1], freq="W-FRI"))
    SPY_M = spy["Close"].resample("ME").last()
    log.info("Replaying %d tickers on %d dates", len(frames), len(bt.DATES))

    cands, elig = replay(sorted(frames), args.processes)
    log.info("Replay done in %.0f s, %d candidates", time.time() - t0, len(cands))
    frames["SPY"] = spy
    cal = spy.index
    variants = build_variants(cands, elig, spy)
    elig_ctl = elig[["fri", "ticker", "close", "bar"]]

    rng = np.random.default_rng(bt.SEED)
    rows = []
    for name, top in variants.items():
        sig = st.run_experiment(top, frames)
        sig = sig[sig["status"] != "no_data"].copy()
        ctl = bt.evaluate_rows(bt.build_controls(sig, elig_ctl, np.random.default_rng(bt.SEED)), frames)
        ctl = ctl[ctl["status"] != "no_data"].copy()
        for df in (sig, ctl):
            df["r"] = bt.payoff_r(df)
        sig.round(4).to_csv(OUT / f"signals_{name}.csv.gz", index=False)
        for h in ("short", "medium", "long"):
            sh, ch = sig[sig["horizon"] == h], ctl[ctl["horizon"] == h]
            if sh.empty:
                continue
            block = []
            for label, a, b in PERIODS + (("all", "2000-01-01", "2100-01-01"),):
                s = sh[(sh["scan_file_date"] >= a) & (sh["scan_file_date"] <= b)]
                c = ch[(ch["scan_file_date"] >= a) & (ch["scan_file_date"] <= b)]
                r = {"variant": name, "horizon": h, "period": label, **score_block(s, c, cal, rng)}
                block.append(r)
            v = keep_verdict(block)
            for r in block:
                r["verdict"] = v
            rows.extend(block)
        log.info("Variant %s scored", name)

    table = pd.DataFrame(rows)
    table.round(3).to_csv(OUT / "summary.csv", index=False)

    lines = ["# Wyckoff scanner · variant backtest", "",
             f"Scan dates {bt.DATES[0].date()} to {bt.DATES[-1].date()}, every Friday. "
             f"Tickers {len(frames) - 1}. Runtime {time.time() - t0:.0f} s.", "",
             "Outcome: TP1 before stop inside the horizon window. R: +reward/risk on TP1, -1 on stop.",
             "Control: 3 random eligible stocks per signal, same date, same % levels.",
             "Gap: signal R minus the mean R of its own controls, with a 95% bootstrap interval.",
             "Keep rule, fixed before the run: gap above 0 in both periods and the full-period interval above 0.", ""]
    for h in ("short", "medium", "long"):
        t = table[table["horizon"] == h]
        if t.empty:
            continue
        lines += [f"## {h.capitalize()} term", "",
                  "| Variant | Period | Resolved | TP1 % | Control % | z vs ctl | Avg R | Ctl avg R | Gap R (95%) | Total R | Max DD R | Ctl max DD R | Verdict |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in t.iterrows():
            lines.append(
                f"| {r['variant']} | {r['period']} | {int(r['resolved'])} | {fmt(r['tp1_rate'], 1)} | "
                f"{fmt(r['ctl_tp1_rate'], 1)} | {fmt(r['z_vs_ctl'])} | {fmt(r['avg_r'])} | {fmt(r['ctl_avg_r'])} | "
                f"{fmt(r['gap_r'])} ({fmt(r['gap_lo'])} to {fmt(r['gap_hi'])}) | {fmt(r['total_r'], 0)} | "
                f"{fmt(r['max_dd_r'], 0)} | {fmt(r['ctl_max_dd_r'], 0)} | {r['verdict']} |")
        lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("Variant backtest written to %s in %.0f s", OUT, time.time() - t0)


if __name__ == "__main__":
    main()
