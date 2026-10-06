#!/usr/bin/env python3
"""
Wyckoff NYSE scanner.

Pulls the full NYSE common-stock universe every run, scores Wyckoff setups on
three horizons and writes an HTML + CSV report with entry, stop and two targets.

Horizons
  short  (~3 months)   daily bars. Spring (+ test) or SOS followed by LPS
                       inside a recent trading range.
  medium (6-12 months) weekly bars. End of a 6-month accumulation base after a
                       markdown, price above a rising 30-week MA.
  long   (~2 years)    weekly bars. Long base after a deep markdown (>40%),
                       no new lows for 20+ weeks, accumulation volume signature.

Targets use Wyckoff-style measured moves (range height projected from the
breakout) and, for the long horizon, retracements of the prior markdown.

Dependencies: pandas, numpy, yfinance
Usage:
  python wyckoff_scanner.py                 # full run
  python wyckoff_scanner.py --limit 200     # quick test on 200 tickers
"""
import argparse
import datetime as dt
import html
import io
import logging
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

UNIVERSE_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

CONFIG = {
    "min_price": 5.0,          # skip penny stocks
    "min_dollar_vol": 5e6,     # 20-day average dollar volume
    "history": "5y",
    "batch_size": 150,
    "top_n": 10,
    "max_risk_short": 0.12,    # max distance entry -> stop
    "max_risk_medium": 0.20,
    "max_risk_long": 0.35,
    "min_rr": 1.5,             # min reward/risk to first target
}

EXCLUDE_NAME_WORDS = ("Warrant", "Unit", "Right", "Preferred", "Notes", "Debenture",
                      "Trust Preferred", "% ", "Fixed-to-Floating")

log = logging.getLogger("wyckoff")


# ---------------------------------------------------------------- universe

def load_nyse_universe():
    """Return {yahoo_ticker: security_name} for NYSE common stocks."""
    with urllib.request.urlopen(UNIVERSE_URL, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="ignore")
    df = pd.read_csv(io.StringIO(text), sep="|", dtype=str)
    df = df[(df["Exchange"] == "N") & (df["ETF"] == "N") & (df["Test Issue"] == "N")]

    out = {}
    for sym, name in zip(df["ACT Symbol"], df["Security Name"]):
        if not isinstance(sym, str) or "$" in sym:
            continue  # preferred shares
        if any(w in str(name) for w in EXCLUDE_NAME_WORDS):
            continue
        if "." in sym:
            base, suffix = sym.split(".", 1)
            if suffix not in ("A", "B", "C"):
                continue  # warrants, units, rights
            sym = f"{base}-{suffix}"  # Yahoo format for class shares
        out[sym] = str(name)
    log.info("NYSE universe: %d common stocks", len(out))
    return out


# ---------------------------------------------------------------- data

def download_prices(tickers, cache_file):
    if cache_file.exists():
        log.info("Loading cached prices from %s", cache_file)
        return pd.read_pickle(cache_file)

    frames = {}
    bs = CONFIG["batch_size"]
    for i in range(0, len(tickers), bs):
        batch = tickers[i:i + bs]
        data = None
        for attempt in range(3):
            try:
                data = yf.download(batch, period=CONFIG["history"], interval="1d",
                                   auto_adjust=True, group_by="ticker",
                                   threads=True, progress=False)
                break
            except Exception as exc:  # network hiccups, rate limits
                log.warning("Batch %d failed (%s), retrying", i // bs, exc)
                time.sleep(5 * (attempt + 1))
        if data is None or data.empty:
            continue

        level0 = set(data.columns.get_level_values(0)) if isinstance(data.columns, pd.MultiIndex) else set()
        for t in batch:
            if level0 and t not in level0:
                continue
            df = data[t] if level0 else data
            df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
            if len(df) >= 250:
                frames[t] = df
        log.info("Downloaded %d / %d", min(i + bs, len(tickers)), len(tickers))
        time.sleep(1)

    pd.to_pickle(frames, cache_file)
    return frames


# ---------------------------------------------------------------- helpers

def atr(df, n=14):
    h, l, c = df["High"], df["Low"], df["Close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def to_weekly(df):
    return df.resample("W-FRI").agg({"Open": "first", "High": "max", "Low": "min",
                                     "Close": "last", "Volume": "sum"}).dropna()


def updown_volume_ratio(df):
    """Volume on up bars / volume on down bars. >1 = demand dominates (accumulation)."""
    chg = df["Close"].diff()
    up = df["Volume"][chg > 0].sum()
    down = df["Volume"][chg < 0].sum()
    return float(up / down) if down > 0 else 2.0


def rel_strength(close, spy_close, n):
    """Change of the stock/SPY ratio over n bars."""
    spy = spy_close.reindex(close.index).ffill()
    ratio = (close / spy).dropna()
    if len(ratio) <= n:
        return 0.0
    return float(ratio.iloc[-1] / ratio.iloc[-n - 1] - 1)


def finish(setup, price, entry, stop, tp1, tp2, max_risk):
    """Validate levels and return common fields, or None if the trade is not viable."""
    if not (stop < entry < tp1 <= tp2):
        return None
    risk = (entry - stop) / entry
    rr = (tp1 - entry) / (entry - stop)
    if risk > max_risk or rr < CONFIG["min_rr"]:
        return None
    return {"setup": setup, "price": price, "entry": entry, "stop": stop,
            "tp1": tp1, "tp2": tp2, "risk_pct": risk * 100, "rr": rr}


# ---------------------------------------------------------------- scans

def scan_short(d, spy_c):
    """Daily. Trading range over bars -80..-10, event in the last 10 bars."""
    if len(d) < 200:
        return None
    c, v = d["Close"], d["Volume"]
    a = atr(d).iloc[-1]
    if not np.isfinite(a) or a <= 0:
        return None
    price = c.iloc[-1]
    vol20 = v.rolling(20).mean()

    rng = d.iloc[-80:-10]
    sup, res = rng["Low"].min(), rng["High"].max()
    height = res - sup
    if not 0.08 <= height / sup <= 0.40:
        return None  # no clean trading range

    recent = d.iloc[-10:]
    ud = updown_volume_ratio(rng)
    rs = rel_strength(c, spy_c, 20)

    if recent["Low"].min() < sup and sup < price < sup + 0.6 * height:
        # Spring: shakeout below support, close back inside the range
        spring_idx = recent["Low"].idxmin()
        spring_low = recent["Low"].min()
        after = d.loc[spring_idx:].iloc[1:]
        test_ok = (len(after) >= 2 and after["Low"].min() > spring_low
                   and after["Volume"].mean() < vol20.loc[spring_idx])
        res_ = finish("Spring + teste" if test_ok else "Spring", price,
                      price, spring_low - 0.5 * a, res, res + height,
                      CONFIG["max_risk_short"])
        base = 45 if test_ok else 32
    elif (recent["Close"] > res).any() and res - 0.5 * a <= price <= res + 1.5 * a:
        # SOS: close above resistance on volume, then LPS: quiet pullback to the creek
        first = recent.index[recent["Close"] > res][0]
        if v.loc[first] / vol20.loc[first] < 1.3:
            return None
        quiet = v.iloc[-3:].mean() / vol20.iloc[-1] < 0.9
        entry = res + 0.25 * a
        stop = min(recent["Low"].iloc[-5:].min(), res - a) - 0.5 * a
        res_ = finish("SOS + LPS" if quiet else "SOS", price, entry, stop,
                      res + height, res + 2 * height, CONFIG["max_risk_short"])
        base = 45 if quiet else 32
    else:
        return None

    if res_ is None:
        return None
    score = (base + 10 * min(ud, 2.0) + float(np.clip(rs * 100, -10, 15))
             + 3.75 * min(res_["rr"], 4.0))
    res_["score"] = min(score, 100)
    res_["note"] = f"Range {sup:.2f}-{res:.2f} · vol up/down {ud:.2f} · RS20 {rs*100:+.1f}%"
    return res_


def scan_medium(d, spy_c):
    """Weekly. 6-month base after a markdown, early markup."""
    w = to_weekly(d)
    if len(w) < 110:
        return None
    c = w["Close"]
    ma30 = c.rolling(30).mean()
    wa = atr(w, 10).iloc[-1]
    price = c.iloc[-1]

    base = w.iloc[-28:-2]
    b_lo, b_hi = base["Low"].min(), base["High"].max()
    height = b_hi - b_lo
    if height / b_lo > 0.50:
        return None
    prior_hi = w.iloc[-110:-28]["High"].max()
    drop = 1 - b_lo / prior_hi
    if drop < 0.20:
        return None  # no markdown before the base
    if price < ma30.iloc[-1] or ma30.iloc[-1] < ma30.iloc[-6]:
        return None  # 30w MA must be flat or rising
    if (price - b_lo) / height < 0.70 or price > b_hi * 1.08:
        return None  # not near the top of the base, or already extended
    ud = updown_volume_ratio(base)
    if ud < 1.0:
        return None
    rs = rel_strength(d["Close"], spy_c, 65)

    broke = price > b_hi
    entry = b_hi if broke else price
    stop = min((b_lo + b_hi) / 2 - 0.5 * wa, entry * 0.93)
    tp1 = b_hi + height
    tp2 = max(b_hi + 2 * height, min(prior_hi, entry * 2))
    res_ = finish("LPS pós-SOS (Fase E)" if broke else "Fim acumulação (Fase D)",
                  price, entry, stop, tp1, tp2, CONFIG["max_risk_medium"])
    if res_ is None:
        return None
    slope = ma30.iloc[-1] / ma30.iloc[-6] - 1
    score = (30 * min(drop / 0.5, 1) + 40 * min(ud - 1, 0.5) + float(np.clip(rs * 100, -10, 15))
             + 10 * min(slope / 0.03, 1) + 2.5 * min(res_["rr"], 4.0))
    res_["score"] = float(np.clip(score, 0, 100))
    res_["note"] = f"Base {b_lo:.2f}-{b_hi:.2f} · queda prévia {drop*100:.0f}% · vol up/down {ud:.2f}"
    return res_


def scan_long(d, spy_c):
    """Weekly. Long base (60w) after a deep markdown, no new lows for 20+ weeks."""
    w = to_weekly(d)
    if len(w) < 140:
        return None
    c = w["Close"]
    ma40 = c.rolling(40).mean()
    wa = atr(w, 10).iloc[-1]
    price = c.iloc[-1]

    base = w.iloc[-60:]
    b_lo, b_hi = base["Low"].min(), base["High"].max()
    weeks_since_low = len(base) - 1 - int(np.argmin(base["Low"].values))
    if weeks_since_low < 20:
        return None  # still making lows, selling not exhausted
    prior_hi = w.iloc[:-60]["High"].max()
    drop = 1 - b_lo / prior_hi
    if drop < 0.40:
        return None
    if (price - b_lo) / (b_hi - b_lo) < 0.5 or price > b_hi * 1.10:
        return None
    if price < ma40.iloc[-1] or ma40.iloc[-1] < ma40.iloc[-9]:
        return None
    ud = updown_volume_ratio(base)
    if ud < 1.05:
        return None
    rets = c.pct_change()
    compress = rets.iloc[-13:].std() / rets.iloc[-60:].std()
    rs = rel_strength(d["Close"], spy_c, 130)

    entry = min(price, b_hi)
    stop = max(b_lo - wa, entry * 0.65)
    tp1 = b_lo + 0.5 * (prior_hi - b_lo)
    tp2 = b_lo + 0.786 * (prior_hi - b_lo)
    if tp1 < entry * 1.3:
        return None
    res_ = finish("Acumulação longa", price, entry, stop, tp1, tp2, CONFIG["max_risk_long"])
    if res_ is None:
        return None
    score = (25 * min(drop / 0.7, 1) + 40 * min(ud - 1, 0.5) + 15 * float(np.clip(1 - compress, 0, 1))
             + float(np.clip(rs * 50, -10, 10)) + 10 * min(weeks_since_low / 40, 1))
    res_["score"] = float(np.clip(score, 0, 100))
    res_["note"] = (f"Queda {drop*100:.0f}% do máx. · {weeks_since_low} sem. sem novo mínimo "
                    f"· vol up/down {ud:.2f}")
    return res_


SCANS = {
    "short": ("Curto prazo · ~3 meses", scan_short),
    "medium": ("Médio prazo · 6 a 12 meses", scan_medium),
    "long": ("Longo prazo · ~2 anos", scan_long),
}


# ---------------------------------------------------------------- report

def market_regime(spy):
    c = spy["Close"]
    ma200 = c.rolling(200).mean().iloc[-1]
    ok = c.iloc[-1] > ma200
    return ok, f"SPY {c.iloc[-1]:.2f} {'acima' if ok else 'abaixo'} da MM200 ({ma200:.2f})"


def write_html(results, names, regime, path, run_date):
    def row(r):
        return (f"<tr><td class='tk'>{r['ticker']}</td>"
                f"<td class='nm'>{html.escape(names.get(r['ticker'], '')[:40])}</td>"
                f"<td>{r['setup']}</td><td>{r['price']:.2f}</td>"
                f"<td class='en'>{r['entry']:.2f}</td><td class='sl'>{r['stop']:.2f}</td>"
                f"<td class='tp'>{r['tp1']:.2f}</td><td class='tp'>{r['tp2']:.2f}</td>"
                f"<td>{r['risk_pct']:.1f}%</td><td>{r['rr']:.1f}</td>"
                f"<td><b>{r['score']:.0f}</b></td>"
                f"<td class='nt'>{html.escape(r['note'])}</td></tr>")

    sections = []
    for key, (title, _) in SCANS.items():
        rows = "".join(row(r) for r in results[key]) or \
            "<tr><td colspan='12'>Nenhum setup passou os filtros hoje.</td></tr>"
        sections.append(
            f"<h2>{title}</h2><div class='wrap'><table><thead><tr>"
            "<th>Ticker</th><th>Nome</th><th>Setup</th><th>Preço</th><th>Entrada</th>"
            "<th>Stop</th><th>TP1</th><th>TP2</th><th>Risco</th><th>R:R</th>"
            f"<th>Score</th><th>Contexto</th></tr></thead><tbody>{rows}</tbody></table></div>")

    ok, txt = regime
    warn = "" if ok else ("<p class='warn'>Mercado em regime defensivo. "
                          "Wyckoff pede cautela com compras contra a tendência do índice.</p>")
    page = f"""<!doctype html><html lang="pt"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wyckoff NYSE · {run_date}</title><style>
:root{{--bg:#f7f8fa;--fg:#1d2330;--mut:#6b7280;--line:#dde1e7;--red:#c0392b;--grn:#1e8449;--blu:#1f5fa8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14171c;--fg:#e6e8eb;--mut:#9aa1ab;--line:#2a2f37;
--red:#ff7b6b;--grn:#5fd18a;--blu:#7fb2ff}}}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0;padding:24px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:17px;margin:28px 0 8px}}
.sub{{color:var(--mut);margin:0}} .warn{{color:var(--red);font-weight:600}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;min-width:980px}}
th,td{{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}}
th{{color:var(--mut);font-weight:500}} td.tk,td.nm,td.nt,th:nth-child(-n+3),td:nth-child(3){{text-align:left}}
.tk{{font-weight:700}} .nm,.nt{{color:var(--mut)}} .sl{{color:var(--red)}} .en{{color:var(--grn)}} .tp{{color:var(--blu)}}
footer{{color:var(--mut);font-size:12px;margin-top:28px;max-width:760px}}
</style></head><body>
<h1>Scanner Wyckoff · NYSE</h1>
<p class="sub">{run_date} · {txt}</p>{warn}
{''.join(sections)}
<footer>Filtro técnico automático. Não substitui análise fundamental, earnings nem notícias.
Confirma cada setup no gráfico antes de entrar. Ajusta o tamanho da posição ao risco até ao stop.</footer>
</body></html>"""
    path.write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Daily Wyckoff scanner for NYSE stocks")
    ap.add_argument("--out", default="wyckoff_reports", help="output folder")
    ap.add_argument("--limit", type=int, default=0, help="scan only the first N tickers (testing)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    run_date = dt.date.today().isoformat()

    names = load_nyse_universe()
    tickers = sorted(names)
    if args.limit:
        tickers = tickers[:args.limit]

    frames = download_prices(tickers + ["SPY"], out / f"cache_{run_date}.pkl")
    spy = frames.pop("SPY", None)
    if spy is None:
        raise SystemExit("Could not download SPY, aborting")
    spy_c = spy["Close"]

    results = {k: [] for k in SCANS}
    for t, d in frames.items():
        c, v = d["Close"], d["Volume"]
        if c.iloc[-1] < CONFIG["min_price"]:
            continue
        if (c * v).rolling(20).mean().iloc[-1] < CONFIG["min_dollar_vol"]:
            continue
        for key, (_, fn) in SCANS.items():
            try:
                r = fn(d, spy_c)
            except Exception as exc:
                log.debug("%s %s failed: %s", t, key, exc)
                continue
            if r:
                r["ticker"] = t
                results[key].append(r)

    for key in results:
        results[key] = sorted(results[key], key=lambda r: r["score"], reverse=True)[:CONFIG["top_n"]]
        log.info("%s: %d picks", key, len(results[key]))

    rows = [{"horizon": k, **r} for k, lst in results.items() for r in lst]
    pd.DataFrame(rows).round(2).to_csv(out / f"wyckoff_{run_date}.csv", index=False)
    html_path = out / f"wyckoff_{run_date}.html"
    write_html(results, names, market_regime(spy), html_path, run_date)
    log.info("Report written to %s", html_path)

    # remove old price caches, keep reports
    for f in out.glob("cache_*.pkl"):
        if f.name != f"cache_{run_date}.pkl":
            f.unlink()


if __name__ == "__main__":
    main()
