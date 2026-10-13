#!/usr/bin/env python3
"""
Point-in-time backtest of the Wyckoff scanner.

Replays the live scanner every Friday over past data and scores each signal the
same way as the live experiment: does price touch TP1 before the stop inside the
horizon window? Signals are compared with two baselines:

  random walk  chance of TP1 before stop for a driftless walk, (P - stop) / (TP1 - stop)
  control      random eligible stocks on the same date with the same % distance to
               stop and targets; this absorbs market drift, regime and universe bias

Leakage controls
  - The scan functions are imported from wyckoff_scanner.py, unchanged.
  - On each scan date every ticker sees only bars up to that date, trimmed to the
    same 5-year lookback the live scanner downloads. An assertion checks this.
  - Weekly bars are built from the full series once and cut at the scan week.
    A weekly bar never holds a day after the scan date.
  - Liquidity, price filters and the top-10 ranking use only scan-date values.
  - Prices are split-adjusted only (auto_adjust=False), so later dividends do not
    leak into earlier price levels.
  - Outcomes use only bars after the scan date.

Known bias that cannot be removed with free data
  - The universe is today's NYSE list. Delisted names are missing. The control
    group shares this bias, so the signal-versus-control gap is the fairer number.

Usage
  python backtest.py                     # full run
  python backtest.py --limit 100         # quick test
  python backtest.py --start 2019-01-01

Dependencies: pandas, numpy, yfinance
"""
import argparse
import logging
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

import signal_tracker as st
import wyckoff_scanner as ws

OUT = Path("backtest")
LOOKBACK = 1260          # ~5 years of daily bars, same as the live download
HISTORY = "10y"
N_CONTROLS = 3
SEED = 42

log = logging.getLogger("backtest")

# shared state for worker processes (inherited through fork)
FRAMES = {}
SPY_C = None
DATES = []
_CUR = {}

_ORIG_TO_WEEKLY = ws.to_weekly


def _weekly_cut(_df):
    """Replacement for ws.to_weekly inside the replay. Returns the weekly bars cut at the scan week."""
    return _CUR["w"]


# ---------------------------------------------------------------- data

def download(tickers, cache):
    if cache.exists():
        log.info("Loading cached prices from %s", cache)
        return pd.read_pickle(cache)
    import yfinance as yf
    frames = {}
    bs = 150
    for i in range(0, len(tickers), bs):
        batch = tickers[i:i + bs]
        data = None
        for attempt in range(3):
            try:
                data = yf.download(batch, period=HISTORY, interval="1d", auto_adjust=False,
                                   group_by="ticker", threads=True, progress=False)
                break
            except Exception as exc:
                log.warning("Batch %d failed (%s), retrying", i // bs, exc)
                time.sleep(5 * (attempt + 1))
        if data is None or data.empty:
            continue
        multi = isinstance(data.columns, pd.MultiIndex)
        level0 = set(data.columns.get_level_values(0)) if multi else set()
        for t in batch:
            if multi and t not in level0:
                continue
            df = (data[t] if multi else data)[["Open", "High", "Low", "Close", "Volume"]].dropna()
            if getattr(df.index, "tz", None) is not None:
                df = df.tz_localize(None)
            if len(df) >= 250:
                frames[t] = df
        log.info("Downloaded %d / %d", min(i + bs, len(tickers)), len(tickers))
        time.sleep(1)
    pd.to_pickle(frames, cache)
    return frames


# ---------------------------------------------------------------- replay

def scan_ticker(t):
    """Run the three live scans on one ticker for every scan date. Point-in-time only."""
    ws.to_weekly = _weekly_cut
    d_full = FRAMES[t]
    w_full = _ORIG_TO_WEEKLY(d_full)
    dollar_vol = (d_full["Close"] * d_full["Volume"]).rolling(20).mean()
    picks, eligible = [], []

    for fri in DATES:
        d = d_full.loc[:fri]
        if d.empty or (fri - d.index[-1]).days > 6:
            continue  # not trading that week
        d = d.iloc[-LOOKBACK:]
        if len(d) < 250:
            continue
        last = d.index[-1]
        close = float(d["Close"].iloc[-1])
        if close < ws.CONFIG["min_price"] or not dollar_vol.loc[last] >= ws.CONFIG["min_dollar_vol"]:
            continue
        w = w_full.loc[d.index[0]:fri]
        assert d.index[-1] <= fri and w.index[-1] <= fri, f"leak {t} {fri}"
        eligible.append((fri, t, close, last))
        _CUR["w"] = w
        spy = SPY_C.loc[:fri]
        for key, (_, fn) in ws.SCANS.items():
            try:
                r = fn(d, spy)
            except Exception:
                continue
            if r:
                r.update(ticker=t, horizon=key, scan_file_date=fri.date().isoformat(),
                         bar_date=last.date().isoformat())
                picks.append(r)
    return picks, eligible


def replay(tickers, processes):
    with mp.get_context("fork").Pool(processes) as pool:
        results = pool.map(scan_ticker, tickers, chunksize=8)
    picks = [p for ps, _ in results for p in ps]
    eligible = [e for _, es in results for e in es]
    return pd.DataFrame(picks), pd.DataFrame(eligible, columns=["fri", "ticker", "close", "bar"])


# ---------------------------------------------------------------- scoring

def rank_top(cands):
    cands = cands.sort_values(["scan_file_date", "horizon", "score"], ascending=[True, True, False])
    cands["rank"] = cands.groupby(["scan_file_date", "horizon"]).cumcount() + 1
    return cands


def build_controls(signals, eligible, rng):
    """Same date, random eligible stocks, same % geometry as the signal."""
    by_date = {k: g for k, g in eligible.groupby("fri")}
    rows = []
    for _, s in signals.iterrows():
        pool = by_date.get(pd.Timestamp(s["scan_file_date"]))
        if pool is None:
            continue
        pool = pool[pool["ticker"] != s["ticker"]]
        if pool.empty:
            continue
        pick = pool.sample(min(N_CONTROLS, len(pool)), random_state=int(rng.integers(1 << 31)))
        p = float(s["price"])
        for _, c in pick.iterrows():
            k = c["close"] / p
            rows.append({"ticker": c["ticker"], "horizon": s["horizon"], "setup": s["setup"],
                         "scan_file_date": s["scan_file_date"], "price": c["close"],
                         "entry": s["entry"] * k, "stop": s["stop"] * k, "tp1": s["tp1"] * k,
                         "tp2": s["tp2"] * k, "score": s["score"], "rank": s["rank"],
                         "signal_id_of": s["signal_id"]})
    return pd.DataFrame(rows)


def evaluate_rows(rows, frames):
    out = []
    for _, r in rows.iterrows():
        bars = frames.get(r["ticker"])
        row = r.to_dict()
        if bars is not None:
            row.update(st.evaluate(r, bars))
        else:
            row["status"] = "no_data"
        out.append(row)
    return pd.DataFrame(out)


def payoff_r(df):
    """Outcome in multiples of the stop distance: +reward/risk on TP1 first, -1 on stop first."""
    rr = (df["tp1"] - df["price"]) / (df["price"] - df["stop"])
    return np.where(df["status"] == "tp1_first", rr, np.where(df["status"] == "stop_first", -1.0, np.nan))


def regime(spy):
    c = spy["Close"]
    return (c > c.rolling(200).mean())


# ---------------------------------------------------------------- summary

def stats(g):
    res = g[g["status"].isin(["tp1_first", "stop_first"])]
    hits = res["status"] == "tp1_first"
    exp = res["p_random"]
    var = float((exp * (1 - exp)).sum())
    d = {
        "signals": len(g),
        "resolved": len(res),
        "tp1_first": int(hits.sum()),
        "stop_first": int((~hits).sum()),
        "expired": int((g["status"] == "window_expired").sum()),
        "running": int((g["status"] == "running").sum()),
        "tp1_rate": hits.mean() * 100 if len(res) else np.nan,
        "random_rate": exp.mean() * 100 if len(res) else np.nan,
        "z_random": (hits.sum() - exp.sum()) / np.sqrt(var) if var > 0 else np.nan,
        "avg_r": float(np.nanmean(res["r"])) if len(res) else np.nan,
        "med_days_tp1": g.loc[g["status"] == "tp1_first", "tp1_day"].median(),
        "med_days_stop": g.loc[g["status"] == "stop_first", "stop_day"].median(),
    }
    for n in (20, 60):
        c = g.get(f"cp{n}", pd.Series(dtype=str))
        c = c[c.isin(["tp1", "stop", "none"])]
        d[f"tp1_by{n}"] = (c == "tp1").mean() * 100 if len(c) else np.nan
        d[f"stop_by{n}"] = (c == "stop").mean() * 100 if len(c) else np.nan
    return pd.Series(d)


def compare(sig, ctl, by):
    a = sig.groupby(by).apply(stats, include_groups=False).add_prefix("sig_")
    b = ctl.groupby(by).apply(stats, include_groups=False).add_prefix("ctl_")
    m = a.join(b, how="left")
    # two-proportion z on the TP1-first rate, signal vs control
    p1, n1 = m["sig_tp1_rate"] / 100, m["sig_resolved"]
    p2, n2 = m["ctl_tp1_rate"] / 100, m["ctl_resolved"]
    pp = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    m["z_vs_control"] = (p1 - p2) / se
    m["avg_r_gap"] = m["sig_avg_r"] - m["ctl_avg_r"]
    return m.reset_index()


COLS = ["sig_signals", "sig_resolved", "sig_tp1_rate", "ctl_tp1_rate", "sig_random_rate",
        "z_vs_control", "sig_z_random", "sig_avg_r", "ctl_avg_r", "sig_med_days_tp1",
        "sig_tp1_by20", "ctl_tp1_by20", "sig_stop_by20", "ctl_stop_by20"]


def md_table(df, keys):
    heads = keys + ["n", "resolved", "TP1 1st %", "control %", "random %", "z vs ctl",
                    "z vs random", "avg R", "ctl avg R", "days to TP1", "TP1 by 20 %",
                    "ctl TP1 by 20 %", "stop by 20 %", "ctl stop by 20 %"]
    lines = ["| " + " | ".join(heads) + " |", "|" + "---|" * len(heads)]
    for _, r in df.iterrows():
        cells = [str(r[k]) for k in keys]
        for c in COLS:
            v = r.get(c)
            cells.append("–" if v is None or not np.isfinite(v) else
                         (f"{v:.0f}" if c in ("sig_signals", "sig_resolved", "sig_med_days_tp1") else f"{v:.2f}"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------- main

def main():
    global FRAMES, SPY_C, DATES
    ap = argparse.ArgumentParser(description="Point-in-time backtest of the Wyckoff scanner")
    ap.add_argument("--start", default="2019-01-01", help="first scan date")
    ap.add_argument("--limit", type=int, default=0, help="first N tickers only (testing)")
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
        frames = download(tickers + ["SPY"], cache)
    FRAMES = frames
    spy = frames.pop("SPY")
    SPY_C = spy["Close"]
    end = spy.index[-1]
    DATES = list(pd.date_range(args.start, end, freq="W-FRI"))
    log.info("Replaying %d tickers on %d scan dates", len(frames), len(DATES))

    cands, eligible = replay(sorted(frames), args.processes)
    log.info("Replay done in %.0f s, %d raw candidates", time.time() - t0, len(cands))
    if cands.empty:
        raise SystemExit("No candidates")
    frames["SPY"] = spy
    cands = rank_top(cands)
    top = cands[cands["rank"] <= ws.CONFIG["top_n"]].copy()

    # live dedup rule: a repeat counts only after the earlier signal resolved
    sig_top = st.run_experiment(top, frames)
    sig_all = st.run_experiment(cands, frames)
    sig_top = sig_top[sig_top["status"] != "no_data"]
    sig_all = sig_all[sig_all["status"] != "no_data"]

    rng = np.random.default_rng(SEED)
    ctl = evaluate_rows(build_controls(sig_top, eligible, rng), frames)
    ctl = ctl[ctl["status"] != "no_data"]

    reg = regime(spy)
    for df in (sig_top, sig_all, ctl):
        df["r"] = payoff_r(df)
        df["year"] = df["scan_file_date"].str[:4]
        df["period"] = np.where(df["scan_file_date"] < "2023-01-01", "2019-2022", "2023-2026")
        df["spy_regime"] = df["scan_file_date"].map(
            lambda s: "bull" if bool(reg.asof(pd.Timestamp(s))) else "bear")
        df["rank_bucket"] = np.where(df["rank"] <= 3, "1-3", np.where(df["rank"] <= 6, "4-6", "7-10")) \
            if "rank" in df else "n/a"

    sig_top.round(4).to_csv(OUT / "signals_top10.csv.gz", index=False)
    ctl.round(4).to_csv(OUT / "controls.csv.gz", index=False)
    sig_all.round(4).to_csv(OUT / "signals_all.csv.gz", index=False)

    sections = []
    for by, title in ((["horizon"], "By horizon"), (["horizon", "period"], "By period"),
                      (["horizon", "year"], "By year"), (["horizon", "setup"], "By setup"),
                      (["horizon", "spy_regime"], "By market regime (SPY vs 200-day MA)"),
                      (["horizon", "rank_bucket"], "By rank inside the daily top 10")):
        m = compare(sig_top, ctl, by)
        m.round(3).to_csv(OUT / f"summary_{'_'.join(by)}.csv", index=False)
        sections.append(f"## {title}\n\n{md_table(m, by)}\n")

    all_stats = sig_all.groupby("horizon").apply(stats, include_groups=False).reset_index()
    all_stats.round(3).to_csv(OUT / "summary_all_candidates.csv", index=False)

    head = [f"# Wyckoff scanner backtest", "",
            f"Scan dates: {DATES[0].date()} to {DATES[-1].date()}, every Friday. "
            f"Tickers with data: {len(frames) - 1}. Runtime {time.time() - t0:.0f} s.",
            f"Top-10 signals after dedup: {len(sig_top)}. Controls: {len(ctl)}. "
            f"All candidates after dedup: {len(sig_all)}.", "",
            "Outcome per signal: TP1 touched before the stop inside the horizon window "
            "(63 / 252 / 504 sessions). A bar touching both counts as stop.",
            "avg R: +reward/risk when TP1 comes first, -1 when the stop comes first, resolved signals only.", ""]
    (OUT / "summary.md").write_text("\n".join(head) + "\n" + "\n".join(sections), encoding="utf-8")
    log.info("Backtest written to %s in %.0f s", OUT, time.time() - t0)


if __name__ == "__main__":
    main()
