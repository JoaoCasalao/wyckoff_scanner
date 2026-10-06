#!/usr/bin/env python3
"""
Forward test of the Wyckoff scanner signals.

Reads every wyckoff_reports/wyckoff_<date>.csv since the experiment start,
builds a ledger with one signal per (ticker, horizon) and simulates each one on
the daily bars that came after the signal. Writes:

  experiment/signals.csv   one row per signal, with outcome and returns
  experiment/summary.csv   aggregated stats by horizon, setup and score bucket
  experiment/summary.md    short text summary (read by the morning report)
  experiment/index.html    readable dashboard

Trade rules (fixed for the whole experiment, see experiment/PROTOCOL.md):
  - Order type comes from entry vs signal close:
      entry above close -> buy-stop, fills when High >= entry at max(Open, entry)
      entry below close -> buy-limit, fills when Low <= entry at min(Open, entry)
      otherwise         -> market order at next Open
  - Fill window: 10 bars (short), 20 bars (medium, long). No fill = expired.
  - Half the position exits at TP1, then the stop moves to the fill price.
    The other half exits at TP2 or at the moved stop.
  - If stop and target are touched on the same bar, the stop is assumed first.
  - Max hold: 63 bars (short), 252 (medium), 504 (long). Then exit at close.
  - Signals still running at the last bar are marked to market.

Prices come from the scanner cache of the same run, so no extra download is
needed inside GitHub Actions. Missing tickers are downloaded with yfinance.

Dependencies: pandas, numpy, yfinance
"""
import argparse
import datetime as dt
import html
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

EXPERIMENT_START = "2026-10-06"
EXPERIMENT_END = "2026-12-31"

FILL_WINDOW = {"short": 10, "medium": 20, "long": 20}
MAX_HOLD = {"short": 63, "medium": 252, "long": 504}
FWD_DAYS = (5, 10, 20, 40)

REPORTS = Path("wyckoff_reports")
OUT = Path("experiment")

log = logging.getLogger("tracker")


# ---------------------------------------------------------------- inputs

def load_scans():
    """All scan rows since the experiment start, oldest first."""
    rows = []
    for f in sorted(REPORTS.glob("wyckoff_*.csv")):
        day = f.stem.split("_", 1)[1]
        if not (EXPERIMENT_START <= day <= EXPERIMENT_END):
            continue
        try:
            df = pd.read_csv(f)
        except pd.errors.EmptyDataError:
            continue
        if df.empty:
            continue
        df["signal_date"] = day
        news = load_news(day)
        df["news_negative"] = df["ticker"].map(lambda t: news.get(t, {}).get("keyword_negative", False))
        df["news_positive"] = df["ticker"].map(lambda t: news.get(t, {}).get("keyword_positive", False))
        df["earnings_risk"] = df["ticker"].map(lambda t: news.get(t, {}).get("earnings_risk", False))
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).sort_values(["signal_date", "horizon", "score"],
                                                         ascending=[True, True, False])


def load_news(day):
    f = REPORTS / f"news_{day}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_prices(tickers):
    """Daily bars from the newest scanner cache, plus a download for anything missing."""
    frames = {}
    caches = sorted(REPORTS.glob("cache_*.pkl"))
    if caches:
        log.info("Using price cache %s", caches[-1])
        frames = pd.read_pickle(caches[-1])
    missing = [t for t in tickers if t not in frames]
    if missing:
        import yfinance as yf
        log.info("Downloading %d tickers not in cache", len(missing))
        data = yf.download(missing, period="2y", interval="1d", auto_adjust=True,
                           group_by="ticker", threads=True, progress=False)
        multi = isinstance(data.columns, pd.MultiIndex)
        for t in missing:
            try:
                df = data[t] if multi else data
                df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
            except KeyError:
                continue
            if not df.empty:
                frames[t] = df
    for t, df in frames.items():
        if getattr(df.index, "tz", None) is not None:
            frames[t] = df.tz_localize(None)
    return frames


# ---------------------------------------------------------------- ledger

def build_ledger(scans):
    """One row per (date, horizon, ticker).

    A repeat of the same ticker and horizon on a later day only counts as a new
    signal after the earlier one has expired or closed. That check needs the
    simulation, so it happens in run_experiment.
    """
    scans = scans.copy()
    scans["signal_id"] = scans["signal_date"] + "_" + scans["horizon"] + "_" + scans["ticker"]
    return scans.drop_duplicates("signal_id").reset_index(drop=True)


# ---------------------------------------------------------------- simulation

def simulate(sig, bars):
    """Simulate one signal on the bars after its date. Returns a dict of results."""
    horizon = sig["horizon"]
    entry, stop, tp1, tp2 = sig["entry"], sig["stop"], sig["tp1"], sig["tp2"]
    sig_day = pd.Timestamp(sig["signal_date"])
    after = bars[bars.index > sig_day]
    ref_close = float(sig["price"])

    res = {"order": "", "status": "pending", "fill_date": None, "fill": np.nan,
           "exit_date": None, "exit_price": np.nan, "r_multiple": np.nan,
           "ret_pct": np.nan, "bars_held": 0, "mfe_r": np.nan, "mae_r": np.nan}

    if entry > ref_close * 1.001:
        res["order"] = "buy-stop"
    elif entry < ref_close * 0.999:
        res["order"] = "limit"
    else:
        res["order"] = "market"

    # fill
    fill_i = None
    for i in range(min(FILL_WINDOW[horizon], len(after))):
        o, h, l = after["Open"].iloc[i], after["High"].iloc[i], after["Low"].iloc[i]
        if res["order"] == "market":
            fill_i, price = i, o
        elif res["order"] == "buy-stop" and h >= entry:
            fill_i, price = i, max(o, entry)
        elif res["order"] == "limit" and l <= entry:
            fill_i, price = i, min(o, entry)
        if fill_i is not None:
            break
    if fill_i is None:
        if len(after) >= FILL_WINDOW[horizon]:
            res["status"] = "expired"
        return res

    fill = float(price)
    risk = fill - stop
    res["fill_date"] = after.index[fill_i].date().isoformat()
    res["fill"] = fill
    if risk <= 0:
        # opened through the stop: treat as an immediate stop-out at the open
        res.update(status="stopped", exit_date=res["fill_date"], exit_price=fill,
                   r_multiple=-1.0, ret_pct=0.0, bars_held=0, mfe_r=0.0, mae_r=-1.0)
        return res

    half_done = False
    cur_stop = stop
    realized = 0.0          # in R, weighted by position fraction
    hi, lo = fill, fill
    last = min(len(after), fill_i + MAX_HOLD[horizon])

    for i in range(fill_i, last):
        o, h, l, c = (after[k].iloc[i] for k in ("Open", "High", "Low", "Close"))
        # on the fill bar only the part of the range after the fill counts;
        # using the full bar is conservative for stops and generous for targets,
        # so targets are not allowed to trigger on the fill bar
        hi, lo = max(hi, h), min(lo, l)
        frac = 0.5 if half_done else 1.0

        # stop first (conservative)
        if l <= cur_stop:
            px = min(o, cur_stop) if i > fill_i else cur_stop
            realized += frac * (px - fill) / risk
            res.update(status="tp1_then_be" if half_done else "stopped",
                       exit_date=after.index[i].date().isoformat(), exit_price=px)
            break
        if i == fill_i:
            continue
        if not half_done and h >= tp1:
            px = max(o, tp1)
            realized += 0.5 * (px - fill) / risk
            half_done = True
            cur_stop = fill
            frac = 0.5
        if half_done and h >= tp2:
            px = max(o, tp2)
            realized += 0.5 * (px - fill) / risk
            res.update(status="tp2", exit_date=after.index[i].date().isoformat(), exit_price=px)
            break
    else:
        # no exit: time stop or still running
        c = after["Close"].iloc[last - 1]
        frac = 0.5 if half_done else 1.0
        realized += frac * (c - fill) / risk
        running = last == len(after) and (last - fill_i) < MAX_HOLD[horizon]
        res.update(status=("open_tp1" if half_done else "open") if running else "time_exit",
                   exit_date=after.index[last - 1].date().isoformat(), exit_price=float(c))

    res["r_multiple"] = realized
    res["ret_pct"] = realized * risk / fill * 100
    exit_ts = pd.Timestamp(res["exit_date"])
    res["bars_held"] = int(((after.index >= after.index[fill_i]) & (after.index <= exit_ts)).sum())
    res["mfe_r"] = (hi - fill) / risk
    res["mae_r"] = (lo - fill) / risk
    return res


def forward_returns(sig, bars, spy):
    """Plain close-to-close returns after the signal, versus SPY. Independent of trade rules."""
    out = {}
    sig_day = pd.Timestamp(sig["signal_date"])
    b = bars[bars.index >= sig_day]["Close"]
    s = spy[spy.index >= sig_day]["Close"]
    if b.empty or b.index[0] != sig_day:
        return {f"fwd{n}": np.nan for n in FWD_DAYS} | {f"fwd{n}_spy": np.nan for n in FWD_DAYS}
    for n in FWD_DAYS:
        if len(b) > n and len(s) > n:
            out[f"fwd{n}"] = (b.iloc[n] / b.iloc[0] - 1) * 100
            out[f"fwd{n}_spy"] = (s.iloc[n] / s.iloc[0] - 1) * 100
        else:
            out[f"fwd{n}"] = np.nan
            out[f"fwd{n}_spy"] = np.nan
    return out


def spy_window(spy, start, end):
    if not start or not end:
        return np.nan
    s = spy["Close"]
    a = s[s.index < pd.Timestamp(start)]
    b = s[s.index <= pd.Timestamp(end)]
    if a.empty or b.empty:
        return np.nan
    return (b.iloc[-1] / a.iloc[-1] - 1) * 100


def run_experiment(ledger, frames):
    spy = frames.get("SPY")
    if spy is None:
        raise SystemExit("SPY prices missing, aborting")
    results = []
    busy_until = {}   # (ticker, horizon) -> date the previous signal ended
    for _, sig in ledger.iterrows():
        key = (sig["ticker"], sig["horizon"])
        if key in busy_until and (busy_until[key] is None or sig["signal_date"] <= busy_until[key]):
            continue  # repeat of a signal that is still pending or open
        bars = frames.get(sig["ticker"])
        row = sig.to_dict()
        if bars is None or bars.empty:
            row.update(status="no_data")
            results.append(row)
            continue
        r = simulate(sig, bars)
        row.update(r)
        row.update(forward_returns(sig, bars, spy))
        row["spy_ret_pct"] = spy_window(spy, r["fill_date"], r["exit_date"])
        row["excess_pct"] = row["ret_pct"] - row["spy_ret_pct"] if r["fill_date"] else np.nan
        if r["status"] in ("pending", "open", "open_tp1"):
            busy_until[key] = None
        elif r["status"] == "expired":
            idx = bars.index[bars.index > pd.Timestamp(sig["signal_date"])]
            busy_until[key] = idx[min(FILL_WINDOW[sig["horizon"]], len(idx)) - 1].date().isoformat()
        else:
            busy_until[key] = r["exit_date"]
        results.append(row)
    return pd.DataFrame(results)


# ---------------------------------------------------------------- summary

CLOSED = ("stopped", "tp1_then_be", "tp2", "time_exit")


def boot_ci(x, n=2000, seed=7):
    """95% bootstrap interval for the mean. Returns (low, high) or (nan, nan)."""
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    if len(x) < 10:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(df, by):
    def agg(g):
        filled = g[g["fill_date"].notna()]
        closed = filled[filled["status"].isin(CLOSED)]
        d = {
            "signals": len(g),
            "filled": len(filled),
            "fill_rate_pct": 100 * len(filled) / len(g) if len(g) else np.nan,
            "closed": len(closed),
            "open": len(filled) - len(closed),
            "win_rate_pct": 100 * (filled["r_multiple"] > 0).mean() if len(filled) else np.nan,
            "avg_r": filled["r_multiple"].mean(),
            "median_r": filled["r_multiple"].median(),
            "total_r": filled["r_multiple"].sum(),
            "avg_ret_pct": filled["ret_pct"].mean(),
            "avg_excess_pct": filled["excess_pct"].mean(),
        }
        d["avg_r_ci_low"], d["avg_r_ci_high"] = boot_ci(closed["r_multiple"])
        for n in FWD_DAYS:
            x = g[f"fwd{n}"] - g[f"fwd{n}_spy"]
            d[f"n_fwd{n}"] = int(x.notna().sum())
            d[f"avg_fwd{n}_vs_spy"] = x.mean()
            d[f"beat_spy_fwd{n}_pct"] = 100 * (x > 0).mean() if x.notna().any() else np.nan
        d["fwd20_ci_low"], d["fwd20_ci_high"] = boot_ci(g["fwd20"] - g["fwd20_spy"])
        return pd.Series(d)

    return df.groupby(by, dropna=False).apply(agg, include_groups=False).reset_index()


def add_score_bucket(df):
    df = df.copy()
    df["score_bucket"] = "n/a"
    for h, g in df.groupby("horizon"):
        if len(g) >= 6:
            q = g["score"].rank(pct=True)
            df.loc[g.index, "score_bucket"] = np.where(q > 2 / 3, "top", np.where(q <= 1 / 3, "bottom", "mid"))
    return df


def fmt(x, nd=2, pct=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}{'%' if pct else ''}"


def write_outputs(df, as_of):
    OUT.mkdir(exist_ok=True)
    df = add_score_bucket(df)
    df.round(4).to_csv(OUT / "signals.csv", index=False)

    parts = []
    for by in (["horizon"], ["horizon", "setup"], ["horizon", "score_bucket"],
               ["horizon", "news_negative"], ["horizon", "earnings_risk"]):
        s = summarize(df[df["status"] != "no_data"], by)
        s.insert(0, "group_by", "+".join(by))
        parts.append(s)
    summary = pd.concat(parts, ignore_index=True)
    summary.round(3).to_csv(OUT / "summary.csv", index=False)

    main = summary[summary["group_by"] == "horizon"].set_index("horizon")
    lines = [f"# Experiência Wyckoff · ponto de situação {as_of}", "",
             f"Período {EXPERIMENT_START} a {EXPERIMENT_END}. Sinais únicos: {len(df)}.", ""]
    names = {"short": "Curto prazo", "medium": "Médio prazo", "long": "Longo prazo"}
    for h in ("short", "medium", "long"):
        if h not in main.index:
            continue
        r = main.loc[h]
        lines.append(f"- {names[h]}. {int(r['signals'])} sinais. {int(r['filled'])} executados. "
                     f"{int(r['closed'])} fechados. R médio {fmt(r['avg_r'])}. "
                     f"Taxa de ganho {fmt(r['win_rate_pct'], 0, True)}. "
                     f"20 dias vs SPY {fmt(r['avg_fwd20_vs_spy'], 2, True)} "
                     f"(n={int(r['n_fwd20'])}). "
                     f"IC95 R fechados [{fmt(r['avg_r_ci_low'])}, {fmt(r['avg_r_ci_high'])}].")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    write_html(df, summary, as_of)


def write_html(df, summary, as_of):
    def table(frame, cols, heads):
        rows = []
        for _, r in frame.iterrows():
            cells = []
            for c in cols:
                v = r.get(c)
                if isinstance(v, (float, np.floating)):
                    cells.append(f"<td>{fmt(float(v))}</td>")
                else:
                    cells.append(f"<td>{html.escape(str(v)) if v is not None else '–'}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")
        head = "".join(f"<th>{h}</th>" for h in heads)
        return f"<div class='wrap'><table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"

    scols = ["horizon", "signals", "filled", "closed", "open", "win_rate_pct", "avg_r", "median_r",
             "total_r", "avg_excess_pct", "avg_fwd5_vs_spy", "avg_fwd20_vs_spy", "beat_spy_fwd20_pct", "n_fwd20"]
    sheads = ["Prazo", "Sinais", "Exec.", "Fech.", "Abertos", "Ganho %", "R méd.", "R mediana",
              "R total", "Excesso %", "5d vs SPY", "20d vs SPY", "Bate SPY 20d %", "n 20d"]

    blocks = []
    for by, title in ((["horizon"], "Por prazo"), (["horizon", "setup"], "Por setup"),
                      (["horizon", "score_bucket"], "Por score"), (["horizon", "news_negative"], "Notícia negativa"),
                      (["horizon", "earnings_risk"], "Earnings na janela")):
        s = summary[summary["group_by"] == "+".join(by)]
        cols = by + scols[1:]
        heads = [{"horizon": "Prazo", "setup": "Setup", "score_bucket": "Score",
                  "news_negative": "Neg.", "earnings_risk": "Earn."}[b] for b in by] + sheads[1:]
        blocks.append(f"<h2>{title}</h2>" + table(s, cols, heads))

    recent = df.sort_values("signal_date", ascending=False).head(60)
    blocks.append("<h2>Últimos sinais</h2>" + table(
        recent, ["signal_date", "horizon", "ticker", "setup", "order", "status", "entry", "fill", "stop",
                 "tp1", "tp2", "r_multiple", "ret_pct", "excess_pct"],
        ["Data", "Prazo", "Ticker", "Setup", "Ordem", "Estado", "Entrada", "Exec.", "Stop", "TP1", "TP2",
         "R", "Ret %", "vs SPY %"]))

    page = f"""<!doctype html><html lang="pt"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Experiência Wyckoff · {as_of}</title><style>
:root{{--bg:#f7f8fa;--fg:#1d2330;--mut:#6b7280;--line:#dde1e7}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14171c;--fg:#e6e8eb;--mut:#9aa1ab;--line:#2a2f37}}}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:24px 0 8px}} .sub{{color:var(--mut)}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;min-width:100%}}
th,td{{padding:5px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}}
th{{color:var(--mut);font-weight:500}} td:first-child,th:first-child{{text-align:left}}
footer{{color:var(--mut);font-size:12px;margin-top:24px;max-width:720px}}
</style></head><body>
<h1>Experiência Wyckoff · teste em tempo real</h1>
<p class="sub">Atualizado {as_of} · período {EXPERIMENT_START} a {EXPERIMENT_END} · regras em PROTOCOL.md</p>
{''.join(blocks)}
<footer>R = ganho ou perda em múltiplos do risco inicial até ao stop. Excesso = retorno da trade menos
o SPY no mesmo período. Os retornos a 5 e 20 dias são de fecho a fecho e não dependem das regras de execução.</footer>
</body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Forward test of the Wyckoff scanner signals")
    ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    scans = load_scans()
    if scans.empty:
        log.info("No scans in the experiment window yet")
        return
    ledger = build_ledger(scans)
    frames = load_prices(sorted(set(ledger["ticker"])) + ["SPY"])
    df = run_experiment(ledger, frames)
    as_of = frames["SPY"].index[-1].date().isoformat()
    write_outputs(df, as_of)
    log.info("Experiment updated: %d signals, prices as of %s", len(df), as_of)


if __name__ == "__main__":
    main()
