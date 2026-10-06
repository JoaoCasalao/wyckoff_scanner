#!/usr/bin/env python3
"""
News check for the Wyckoff scanner picks.

Reads wyckoff_reports/wyckoff_<date>.csv, pulls recent Yahoo news and the next
earnings date for each ticker, applies keyword flags and writes
wyckoff_reports/news_<date>.json for the agent to validate.

Dependencies: pandas, yfinance
"""
import datetime as dt
import json
import logging
import sys
from pathlib import Path

import pandas as pd
import yfinance as yf

NEWS_DAYS = 7
EARNINGS_WINDOW = {"short": 21, "medium": 45, "long": 45}  # days ahead that count as event risk

NEGATIVE = ("offering", "dilut", "downgrade", "investigation", "lawsuit", "sec ", "subpoena",
            "lowers guidance", "cuts guidance", "guidance cut", "misses", "bankruptcy", "delist",
            "recall", "short seller", "restatement", "resigns", "going concern", "default")
POSITIVE = ("upgrade", "buyback", "repurchase", "beats", "raises guidance", "acquire",
            "acquisition", "approval", "approves", "contract", "insider buy", "record revenue")

log = logging.getLogger("news_check")


def parse_news(items, cutoff):
    out = []
    for it in items or []:
        c = it.get("content", it)
        title = c.get("title") or ""
        ts = c.get("pubDate") or it.get("providerPublishTime")
        if isinstance(ts, (int, float)):
            when = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
        elif ts:
            when = pd.to_datetime(ts, utc=True).to_pydatetime()
        else:
            continue
        if when < cutoff:
            continue
        provider = (c.get("provider") or {}).get("displayName") or it.get("publisher", "")
        url = (c.get("canonicalUrl") or {}).get("url") or it.get("link", "")
        low = title.lower()
        out.append({
            "date": when.date().isoformat(),
            "title": title,
            "source": provider,
            "url": url,
            "neg_hits": [k.strip() for k in NEGATIVE if k in low],
            "pos_hits": [k.strip() for k in POSITIVE if k in low],
        })
    return out


def next_earnings(tk):
    try:
        cal = tk.calendar
        dates = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if dates:
            return pd.to_datetime(dates[0]).date()
    except Exception as exc:
        log.debug("calendar failed: %s", exc)
    return None


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_date = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    out = Path("wyckoff_reports")
    path = out / f"news_{run_date}.json"
    try:
        picks = pd.read_csv(out / f"wyckoff_{run_date}.csv")
    except pd.errors.EmptyDataError:
        picks = pd.DataFrame(columns=["ticker", "horizon"])  # no setups passed the filters today
    if picks.empty:
        path.write_text("{}", encoding="utf-8")
        log.info("No picks on %s, wrote empty %s", run_date, path)
        return
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=NEWS_DAYS)
    today = dt.date.fromisoformat(run_date)

    report = {}
    for t, grp in picks.groupby("ticker"):
        tk = yf.Ticker(t)
        try:
            news = parse_news(tk.news, cutoff)
        except Exception as exc:
            log.warning("%s news failed: %s", t, exc)
            news = []
        ed = next_earnings(tk)
        horizons = sorted(grp["horizon"].unique())
        days_to_earn = (ed - today).days if ed else None
        earn_risk = days_to_earn is not None and 0 <= days_to_earn <= max(EARNINGS_WINDOW[h] for h in horizons)
        report[t] = {
            "horizons": horizons,
            "next_earnings": ed.isoformat() if ed else None,
            "days_to_earnings": days_to_earn,
            "earnings_risk": earn_risk,
            "news": news,
            "keyword_negative": any(n["neg_hits"] for n in news),
            "keyword_positive": any(n["pos_hits"] for n in news),
        }
        log.info("%s: %d news, earnings %s", t, len(news), ed)

    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("News file written to %s", path)


if __name__ == "__main__":
    main()
