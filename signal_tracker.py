#!/usr/bin/env python3
"""
Forward test of the Wyckoff scanner signals.

The question is whether each signal behaved as expected: did price reach the
target inside the horizon window without touching the stop first? There is no
trade simulation. Every signal starts at the close of its scan day.

For each signal the tracker walks the daily bars that follow and records:
  - which level came first: TP1 or stop
  - sessions until TP1 / stop, and whether TP1 came inside the window
  - whether TP2 was also reached before the stop
  - how far price went toward TP1 and toward the stop (progress, 0-100%)

Baseline. For a driftless random walk, the chance of reaching TP1 before the
stop, starting at price P, is (P - stop) / (TP1 - stop). Summing that over the
signals gives the number of TP1 hits expected by chance. The method shows an
edge only if the observed hits beat that number by a clear margin.

Outputs:
  experiment/signals.csv   one row per signal
  experiment/summary.csv   stats by horizon, setup, score bucket, news flags
  experiment/summary.md    short text summary (read by the morning report)
  experiment/index.html    readable dashboard

Prices come from the scanner cache of the same run. Missing tickers are
downloaded with yfinance.

Dependencies: pandas, numpy, yfinance
"""
import html
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

EXPERIMENT_START = "2026-10-06"
EXPERIMENT_END = "2026-12-31"

# sessions in which the move is expected to happen
WINDOW = {"short": 63, "medium": 252, "long": 504}
CHECKPOINTS = (20, 40, 60)

REPORTS = Path("wyckoff_reports")
OUT = Path("experiment")

log = logging.getLogger("tracker")


# ---------------------------------------------------------------- inputs

def load_news(day):
    f = REPORTS / f"news_{day}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_scans():
    """All scan rows inside the experiment window, oldest first."""
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
        df["scan_file_date"] = day
        news = load_news(day)
        df["news_negative"] = df["ticker"].map(lambda t: bool(news.get(t, {}).get("keyword_negative", False)))
        df["news_positive"] = df["ticker"].map(lambda t: bool(news.get(t, {}).get("keyword_positive", False)))
        df["earnings_risk"] = df["ticker"].map(lambda t: bool(news.get(t, {}).get("earnings_risk", False)))
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).sort_values(
        ["scan_file_date", "horizon", "score"], ascending=[True, True, False]).reset_index(drop=True)


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
    for t, df in list(frames.items()):
        if getattr(df.index, "tz", None) is not None:
            frames[t] = df.tz_localize(None)
    return frames


# ---------------------------------------------------------------- evaluation

def signal_bar(bars, file_date, price):
    """Date of the bar the scan used.

    The CSV is named with the UTC run date. A late run can carry the next day's
    date while the last bar is the previous session. Pick the latest bar on or
    before the file date whose close matches the scan price.
    """
    upto = bars[bars.index <= pd.Timestamp(file_date)]
    if upto.empty:
        return None
    tail = upto.iloc[-3:]
    match = tail[(tail["Close"] / price - 1).abs() < 0.005]
    return (match.index[-1] if not match.empty else upto.index[-1])


def evaluate(sig, bars):
    """Walk the bars after the signal and record what happened first."""
    p, stop, tp1, tp2 = float(sig["price"]), float(sig["stop"]), float(sig["tp1"]), float(sig["tp2"])
    window = WINDOW[sig["horizon"]]
    res = {"signal_date": None, "status": "no_data", "sessions": 0,
           "tp1_day": np.nan, "stop_day": np.nan, "tp2_day": np.nan,
           "same_bar": False, "entry_touched": False,
           "progress_tp1_pct": np.nan, "progress_stop_pct": np.nan,
           "p_random": np.nan, "ret_last_pct": np.nan}

    ref = signal_bar(bars, sig["scan_file_date"], p)
    if ref is None or not (stop < p < tp1):
        return res
    res["signal_date"] = ref.date().isoformat()
    res["p_random"] = (p - stop) / (tp1 - stop)

    after = bars[bars.index > ref].iloc[:window]
    res["sessions"] = len(after)
    if after.empty:
        res["status"] = "running"
        return res

    hi = after["High"].cummax()
    lo = after["Low"].cummin()
    hit_tp1 = np.flatnonzero(after["High"].values >= tp1)
    hit_stop = np.flatnonzero(after["Low"].values <= stop)
    hit_tp2 = np.flatnonzero(after["High"].values >= tp2)
    hit_entry = np.flatnonzero(after["High"].values >= sig["entry"]) if sig["entry"] > p else np.array([0])

    first_tp1 = hit_tp1[0] if hit_tp1.size else None
    first_stop = hit_stop[0] if hit_stop.size else None
    res["entry_touched"] = bool(hit_entry.size)

    if first_tp1 is not None and (first_stop is None or first_tp1 < first_stop):
        res["status"] = "tp1_first"
        res["tp1_day"] = first_tp1 + 1
        if hit_tp2.size and (first_stop is None or hit_tp2[0] < first_stop):
            res["tp2_day"] = hit_tp2[0] + 1
        if first_stop is not None:
            res["stop_day"] = first_stop + 1
    elif first_stop is not None:
        # a bar that touches both levels counts as stop first (conservative)
        res["status"] = "stop_first"
        res["stop_day"] = first_stop + 1
        res["same_bar"] = first_tp1 is not None and first_tp1 == first_stop
    elif len(after) >= window:
        res["status"] = "window_expired"
    else:
        res["status"] = "running"

    # how far price travelled toward each level before resolution
    cut = len(after)
    for d in (first_tp1, first_stop):
        if d is not None:
            cut = min(cut, d + 1)
    res["progress_tp1_pct"] = float(min(1.0, max(0.0, (hi.iloc[cut - 1] - p) / (tp1 - p)))) * 100
    res["progress_stop_pct"] = float(min(1.0, max(0.0, (p - lo.iloc[cut - 1]) / (p - stop)))) * 100
    res["ret_last_pct"] = (after["Close"].iloc[-1] / p - 1) * 100

    # fixed checkpoints, only for signals with enough history
    for n in CHECKPOINTS:
        if len(after) >= n:
            t = first_tp1 is not None and first_tp1 < n and (first_stop is None or first_tp1 < first_stop)
            s = first_stop is not None and first_stop < n and not t
            res[f"cp{n}"] = "tp1" if t else ("stop" if s else "none")
        else:
            res[f"cp{n}"] = ""
    return res


def run_experiment(scans, frames):
    """One signal per (ticker, horizon) while the earlier one is still unresolved."""
    out = []
    open_until = {}  # (ticker, horizon) -> date the earlier signal resolved, or None if still open
    for _, sig in scans.iterrows():
        key = (sig["ticker"], sig["horizon"])
        if key in open_until:
            end = open_until[key]
            if end is None or sig["scan_file_date"] <= end:
                continue
        bars = frames.get(sig["ticker"])
        row = sig.to_dict()
        if bars is None or bars.empty:
            row.update(status="no_data")
            out.append(row)
            continue
        r = evaluate(sig, bars)
        row.update(r)
        if r["status"] in ("running", "no_data"):
            open_until[key] = None
        else:
            days = [d for d in (r["tp1_day"], r["stop_day"]) if np.isfinite(d)]
            n = int(min(days)) if days and r["status"] != "window_expired" else WINDOW[sig["horizon"]]
            after = bars[bars.index > pd.Timestamp(r["signal_date"])]
            open_until[key] = after.index[min(n, len(after)) - 1].date().isoformat()
        out.append(row)
    df = pd.DataFrame(out)
    df["signal_id"] = df["signal_date"].astype(str) + "_" + df["horizon"] + "_" + df["ticker"]
    return df


# ---------------------------------------------------------------- summary

def summarize(df, by):
    def agg(g):
        resolved = g[g["status"].isin(["tp1_first", "stop_first"])]
        hits = (resolved["status"] == "tp1_first")
        exp = resolved["p_random"]
        var = (exp * (1 - exp)).sum()
        d = {
            "signals": len(g),
            "running": int((g["status"] == "running").sum()),
            "tp1_first": int(hits.sum()),
            "stop_first": int((resolved["status"] == "stop_first").sum()),
            "window_expired": int((g["status"] == "window_expired").sum()),
            "tp2_before_stop": int(g["tp2_day"].notna().sum()),
            "tp1_rate_pct": 100 * hits.mean() if len(resolved) else np.nan,
            "random_rate_pct": 100 * exp.mean() if len(resolved) else np.nan,
            "z_vs_random": (hits.sum() - exp.sum()) / np.sqrt(var) if var > 0 else np.nan,
            "median_days_tp1": g.loc[g["status"] == "tp1_first", "tp1_day"].median(),
            "median_days_stop": g.loc[g["status"] == "stop_first", "stop_day"].median(),
            "avg_progress_tp1_running": g.loc[g["status"] == "running", "progress_tp1_pct"].mean(),
            "avg_progress_stop_running": g.loc[g["status"] == "running", "progress_stop_pct"].mean(),
        }
        for n in CHECKPOINTS:
            c = g[f"cp{n}"] if f"cp{n}" in g else pd.Series(dtype=str)
            c = c[c.isin(["tp1", "stop", "none"])]
            d[f"n_cp{n}"] = len(c)
            d[f"tp1_by{n}_pct"] = 100 * (c == "tp1").mean() if len(c) else np.nan
            d[f"stop_by{n}_pct"] = 100 * (c == "stop").mean() if len(c) else np.nan
        return pd.Series(d)

    return df.groupby(by, dropna=False).apply(agg, include_groups=False).reset_index()


def add_score_bucket(df):
    df = df.copy()
    df["score_bucket"] = "n/a"
    for _, g in df.groupby("horizon"):
        if len(g) >= 6:
            q = g["score"].rank(pct=True)
            df.loc[g.index, "score_bucket"] = np.where(q > 2 / 3, "top", np.where(q <= 1 / 3, "bottom", "mid"))
    return df


def fmt(x, nd=1, pct=False):
    if x is None or (isinstance(x, (float, np.floating)) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}{'%' if pct else ''}"


GROUPS = (["horizon"], ["horizon", "setup"], ["horizon", "score_bucket"],
          ["horizon", "news_negative"], ["horizon", "earnings_risk"])
NAMES = {"short": "Curto prazo", "medium": "Médio prazo", "long": "Longo prazo"}


def write_outputs(df, as_of):
    OUT.mkdir(exist_ok=True)
    df = add_score_bucket(df)
    df.round(4).to_csv(OUT / "signals.csv", index=False)

    valid = df[df["status"] != "no_data"]
    parts = []
    for by in GROUPS:
        s = summarize(valid, by)
        s.insert(0, "group_by", "+".join(by))
        parts.append(s)
    summary = pd.concat(parts, ignore_index=True)
    summary.round(3).to_csv(OUT / "summary.csv", index=False)

    main = summary[summary["group_by"] == "horizon"].set_index("horizon")
    lines = [f"# Experiência Wyckoff · ponto de situação {as_of}", "",
             f"Sinais de {EXPERIMENT_START} a {EXPERIMENT_END}. Sinais únicos: {len(valid)}.", ""]
    for h in ("short", "medium", "long"):
        if h not in main.index:
            continue
        r = main.loc[h]
        res = int(r["tp1_first"] + r["stop_first"])
        lines.append(
            f"- {NAMES[h]}. {int(r['signals'])} sinais. {int(r['running'])} em curso. "
            f"TP1 antes do stop {int(r['tp1_first'])}. Stop primeiro {int(r['stop_first'])}. "
            f"Taxa TP1 {fmt(r['tp1_rate_pct'], 0, True)} contra {fmt(r['random_rate_pct'], 0, True)} ao acaso "
            f"(n={res}, z={fmt(r['z_vs_random'], 2)}). "
            f"Mediana até TP1 {fmt(r['median_days_tp1'], 0)} sessões.")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_html(df, summary, as_of)


def write_html(df, summary, as_of):
    def table(frame, cols, heads):
        body = []
        for _, r in frame.iterrows():
            cells = []
            for c in cols:
                v = r.get(c)
                if isinstance(v, (float, np.floating)):
                    cells.append(f"<td>{fmt(float(v))}</td>")
                elif v is None or (isinstance(v, float) and np.isnan(v)):
                    cells.append("<td>–</td>")
                else:
                    cells.append(f"<td>{html.escape(str(v))}</td>")
            body.append("<tr>" + "".join(cells) + "</tr>")
        head = "".join(f"<th>{h}</th>" for h in heads)
        return (f"<div class='wrap'><table><thead><tr>{head}</tr></thead>"
                f"<tbody>{''.join(body)}</tbody></table></div>")

    scols = ["signals", "running", "tp1_first", "stop_first", "window_expired", "tp2_before_stop",
             "tp1_rate_pct", "random_rate_pct", "z_vs_random", "median_days_tp1", "median_days_stop",
             "tp1_by20_pct", "stop_by20_pct", "n_cp20"]
    sheads = ["Sinais", "Em curso", "TP1 1.º", "Stop 1.º", "Prazo esgotado", "TP2 s/ stop",
              "Taxa TP1 %", "Acaso %", "z", "Sessões até TP1", "Sessões até stop",
              "TP1 em 20s %", "Stop em 20s %", "n 20s"]
    labels = {"horizon": "Prazo", "setup": "Setup", "score_bucket": "Score",
              "news_negative": "Notícia neg.", "earnings_risk": "Earnings"}
    titles = {"horizon": "Por prazo", "horizon+setup": "Por setup", "horizon+score_bucket": "Por score",
              "horizon+news_negative": "Notícia negativa", "horizon+earnings_risk": "Earnings na janela"}

    blocks = []
    for by in GROUPS:
        key = "+".join(by)
        s = summary[summary["group_by"] == key]
        blocks.append(f"<h2>{titles[key]}</h2>" + table(s, by + scols, [labels[b] for b in by] + sheads))

    recent = df.sort_values(["signal_date", "horizon", "score"], ascending=[False, True, False]).head(80)
    blocks.append("<h2>Sinais</h2>" + table(
        recent, ["signal_date", "horizon", "ticker", "setup", "price", "stop", "tp1", "tp2", "status",
                 "sessions", "tp1_day", "stop_day", "progress_tp1_pct", "progress_stop_pct", "p_random"],
        ["Data", "Prazo", "Ticker", "Setup", "Preço", "Stop", "TP1", "TP2", "Estado", "Sessões",
         "Dia TP1", "Dia stop", "Até TP1 %", "Até stop %", "P acaso"]))

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
<h1>Experiência Wyckoff · comportamento dos sinais</h1>
<p class="sub">Atualizado {as_of} · sinais de {EXPERIMENT_START} a {EXPERIMENT_END} · regras em PROTOCOL.md</p>
{''.join(blocks)}
<footer>Cada sinal começa no fecho do dia do scan. Conta o nível que é tocado primeiro, TP1 ou stop.
Uma sessão que toca os dois conta como stop. "Acaso" é a probabilidade de chegar ao TP1 antes do stop
num passeio aleatório sem tendência. z acima de 2 indica que os sinais batem o acaso com margem clara.</footer>
</body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scans = load_scans()
    if scans.empty:
        log.info("No scans in the experiment window yet")
        return
    frames = load_prices(sorted(set(scans["ticker"])) + ["SPY"])
    df = run_experiment(scans, frames)
    as_of = frames["SPY"].index[-1].date().isoformat() if "SPY" in frames else "?"
    write_outputs(df, as_of)
    log.info("Experiment updated: %d signals, prices as of %s", len(df), as_of)


if __name__ == "__main__":
    main()
