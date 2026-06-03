#!/usr/bin/env python3
"""yfinance-data fetch CLI — agent-native wrapper over the stable, high-frequency
yfinance operations. Covers the ~80% of calls that are fully deterministic so the
agent does NOT regenerate boilerplate (Ticker construction, try/except, formatting)
on every request.

Output contract (ALWAYS this shape, every subcommand, success or failure):
    {"success": bool, "command": str, "data": <any> | null, "error": str | null}

Agents: read the `data` field. NEVER parse stdout as plain text. On failure,
`success` is false and `error` is a string — do not crash, do not guess.

Long-tail / open-ended operations (screener, sector/industry, custom EquityQuery,
search, get_shares_full, ESG) are intentionally NOT here — write code for those.

Run `fetch.py --help` or `fetch.py <cmd> --help` for usage.
Run `fetch.py selftest` to verify the tool works end to end.
"""
import argparse
import json
import sys


def _emit(command, data=None, error=None):
    """Emit the unified JSON envelope and exit with the right code."""
    ok = error is None
    print(json.dumps(
        {"success": ok, "command": command, "data": data, "error": error},
        ensure_ascii=False, default=str
    ))
    sys.exit(0 if ok else 1)


def _import_yf():
    try:
        import yfinance as yf  # noqa
        return yf
    except ImportError:
        _emit("import", error="yfinance not installed — run: pip install -q yfinance")


def _df_records(df, max_rows=None):
    """DataFrame -> list[dict] with the index preserved as a column."""
    if df is None or getattr(df, "empty", True):
        return []
    d = df.copy()
    d.index = d.index.astype(str)
    d = d.reset_index()
    if max_rows:
        d = d.head(max_rows)
    return json.loads(d.to_json(orient="records", date_format="iso"))


# ---------- subcommands ----------

def _fi_get(fi, key):
    """fast_info raises (not returns None) for delisted/invalid symbols."""
    try:
        return fi.get(key)
    except Exception:
        return None


def cmd_price(a, yf):
    t = yf.Ticker(a.ticker)
    fi = t.fast_info
    info = {}
    try:
        info = t.info or {}
    except Exception:
        pass
    last = _fi_get(fi, "lastPrice")
    if last is None:
        _emit("price", error=f"no price data for '{a.ticker}' — check the symbol")
    data = {
        "ticker": a.ticker.upper(),
        "lastPrice": last,
        "previousClose": _fi_get(fi, "previousClose"),
        "open": _fi_get(fi, "open"),
        "dayHigh": _fi_get(fi, "dayHigh"),
        "dayLow": _fi_get(fi, "dayLow"),
        "marketCap": _fi_get(fi, "marketCap"),
        "currency": _fi_get(fi, "currency"),
        "fiftyDayAverage": _fi_get(fi, "fiftyDayAverage"),
        "twoHundredDayAverage": _fi_get(fi, "twoHundredDayAverage"),
        "shortName": info.get("shortName"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
    }
    _emit("price", data=data)


def cmd_info(a, yf):
    t = yf.Ticker(a.ticker)
    try:
        info = t.info or {}
    except Exception as e:
        _emit("info", error=f"info fetch failed for '{a.ticker}': {e}")
    if not info:
        _emit("info", error=f"no info for '{a.ticker}' — check the symbol")
    keys = ["shortName", "longName", "sector", "industry", "country", "website",
            "marketCap", "currentPrice", "previousClose", "trailingPE", "forwardPE",
            "dividendYield", "beta", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
            "averageVolume", "sharesOutstanding", "longBusinessSummary"]
    data = {k: info.get(k) for k in keys}
    if a.all:
        data = info
    _emit("info", data=data)


def cmd_history(a, yf):
    t = yf.Ticker(a.ticker)
    kwargs = {"interval": a.interval, "auto_adjust": True}
    if a.start:
        kwargs["start"] = a.start
        if a.end:
            kwargs["end"] = a.end
    else:
        kwargs["period"] = a.period
    try:
        hist = t.history(**kwargs)
    except Exception as e:
        _emit("history", error=f"history failed for '{a.ticker}': {e}")
    if hist.empty:
        _emit("history", error=f"empty history for '{a.ticker}' "
                               f"(period/interval/date range out of range?)")
    rows = _df_records(hist, max_rows=a.limit)
    _emit("history", data={"ticker": a.ticker.upper(), "rows": len(rows),
                           "interval": a.interval, "bars": rows})


def cmd_financials(a, yf):
    t = yf.Ticker(a.ticker)
    pref = "quarterly_" if a.quarterly else ""
    attr = {"income": f"{pref}income_stmt",
            "balance": f"{pref}balance_sheet",
            "cashflow": f"{pref}cashflow"}[a.statement]
    try:
        df = getattr(t, attr)
    except Exception as e:
        _emit("financials", error=f"{attr} failed for '{a.ticker}': {e}")
    rows = _df_records(df)
    if not rows:
        _emit("financials", error=f"no {attr} data for '{a.ticker}'")
    _emit("financials", data={"ticker": a.ticker.upper(), "statement": attr,
                              "lines": rows})


def cmd_options(a, yf):
    t = yf.Ticker(a.ticker)
    try:
        expirations = list(t.options)
    except Exception as e:
        _emit("options", error=f"options listing failed for '{a.ticker}': {e}")
    if not expirations:
        _emit("options", error=f"no options for '{a.ticker}'")
    if not a.date:
        # Just list expirations — cheap discovery step.
        _emit("options", data={"ticker": a.ticker.upper(),
                               "expirations": expirations})
    if a.date not in expirations:
        _emit("options", error=f"expiry '{a.date}' not available; "
                               f"valid: {expirations[:8]}{'...' if len(expirations) > 8 else ''}")
    try:
        chain = t.option_chain(a.date)
    except Exception as e:
        _emit("options", error=f"option_chain failed for '{a.ticker}' {a.date}: {e}")
    _emit("options", data={
        "ticker": a.ticker.upper(), "expiration": a.date,
        "calls": _df_records(chain.calls, max_rows=a.limit),
        "puts": _df_records(chain.puts, max_rows=a.limit),
    })


def cmd_dividends(a, yf):
    t = yf.Ticker(a.ticker)
    try:
        div = t.dividends
    except Exception as e:
        _emit("dividends", error=f"dividends failed for '{a.ticker}': {e}")
    if div is None or div.empty:
        _emit("dividends", data={"ticker": a.ticker.upper(), "dividends": []})
    s = div.copy()
    s.index = s.index.astype(str)
    recs = [{"date": k, "amount": v} for k, v in s.tail(a.limit).items()]
    _emit("dividends", data={"ticker": a.ticker.upper(), "dividends": recs})


def cmd_analyst(a, yf):
    t = yf.Ticker(a.ticker)
    out = {"ticker": a.ticker.upper()}
    try:
        out["price_targets"] = t.analyst_price_targets
    except Exception:
        out["price_targets"] = None
    try:
        out["recommendations"] = _df_records(t.recommendations)
    except Exception:
        out["recommendations"] = None
    if out["price_targets"] is None and not out["recommendations"]:
        _emit("analyst", error=f"no analyst data for '{a.ticker}'")
    _emit("analyst", data=out)


def cmd_holders(a, yf):
    t = yf.Ticker(a.ticker)
    out = {"ticker": a.ticker.upper()}
    try:
        out["major_holders"] = _df_records(t.major_holders)
    except Exception:
        out["major_holders"] = None
    try:
        out["institutional_holders"] = _df_records(t.institutional_holders, max_rows=a.limit)
    except Exception:
        out["institutional_holders"] = None
    _emit("holders", data=out)


def cmd_news(a, yf):
    t = yf.Ticker(a.ticker)
    try:
        news = t.news or []
    except Exception as e:
        _emit("news", error=f"news failed for '{a.ticker}': {e}")
    items = []
    for n in news[:a.limit]:
        c = n.get("content", n)
        items.append({
            "title": c.get("title") or n.get("title"),
            "publisher": (c.get("provider") or {}).get("displayName") if isinstance(c.get("provider"), dict) else n.get("publisher"),
            "link": (c.get("canonicalUrl") or {}).get("url") if isinstance(c.get("canonicalUrl"), dict) else n.get("link"),
        })
    _emit("news", data={"ticker": a.ticker.upper(), "news": items})


def cmd_download(a, yf):
    tickers = a.tickers.replace(",", " ").split()
    kwargs = {"interval": a.interval, "auto_adjust": True,
              "progress": False, "threads": True, "group_by": "ticker"}
    if a.start:
        kwargs["start"] = a.start
        if a.end:
            kwargs["end"] = a.end
    else:
        kwargs["period"] = a.period
    try:
        data = yf.download(tickers=tickers, **kwargs)
    except Exception as e:
        _emit("download", error=f"download failed for {tickers}: {e}")
    if data is None or data.empty:
        _emit("download", error=f"empty data for {tickers}")
    # Return last close per ticker + row count to keep payload small by default.
    summary = {}
    for tk in tickers:
        try:
            col = data[tk]["Close"] if len(tickers) > 1 else data["Close"]
            col = col.dropna()
            summary[tk.upper()] = {
                "rows": int(col.shape[0]),
                "last_close": float(col.iloc[-1]) if col.shape[0] else None,
                "first_close": float(col.iloc[0]) if col.shape[0] else None,
            }
        except Exception:
            summary[tk.upper()] = {"error": "no Close column"}
    out = {"tickers": [t.upper() for t in tickers], "interval": a.interval,
           "summary": summary}
    if a.full:
        out["closes"] = _df_records(
            data.xs("Close", axis=1, level=1) if len(tickers) > 1 else data[["Close"]],
            max_rows=a.limit)
    _emit("download", data=out)


def cmd_selftest(a, yf):
    """End-to-end smoke test across the stable ops. Proves the tool is usable."""
    results = {}
    checks = [
        ("price", lambda: yf.Ticker("AAPL").fast_info.get("lastPrice") is not None),
        ("history", lambda: not yf.Ticker("AAPL").history(period="5d").empty),
        ("financials", lambda: not yf.Ticker("AAPL").income_stmt.empty),
        ("options_list", lambda: len(yf.Ticker("AAPL").options) > 0),
    ]
    passed = 0
    for name, fn in checks:
        try:
            ok = bool(fn())
            results[name] = "pass" if ok else "fail:empty"
            passed += ok
        except Exception as e:
            results[name] = f"fail:{e}"
    err = None if passed == len(checks) else f"{passed}/{len(checks)} passed"
    _emit("selftest", data={"checks": results, "passed": passed,
                            "total": len(checks)}, error=err)


def build_parser():
    p = argparse.ArgumentParser(
        prog="fetch.py",
        description="Agent-native yfinance CLI. JSON envelope on stdout: "
                    "{success, command, data, error}. Read `data`; never parse text.")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_ticker(sp):
        sp.add_argument("ticker", help="ticker symbol, e.g. AAPL")

    sp = sub.add_parser("price", help="current price + key quote fields")
    add_ticker(sp); sp.set_defaults(fn=cmd_price)

    sp = sub.add_parser("info", help="company overview (key fields, or --all)")
    add_ticker(sp); sp.add_argument("--all", action="store_true")
    sp.set_defaults(fn=cmd_info)

    sp = sub.add_parser("history", help="OHLCV history")
    add_ticker(sp)
    sp.add_argument("--period", default="1mo",
                    help="1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max")
    sp.add_argument("--interval", default="1d",
                    help="1m 5m 15m 30m 60m 1h 1d 1wk 1mo 3mo")
    sp.add_argument("--start"); sp.add_argument("--end")
    sp.add_argument("--limit", type=int, default=None, help="max bars returned")
    sp.set_defaults(fn=cmd_history)

    sp = sub.add_parser("financials", help="income/balance/cashflow statement")
    add_ticker(sp)
    sp.add_argument("statement", choices=["income", "balance", "cashflow"])
    sp.add_argument("--quarterly", action="store_true")
    sp.set_defaults(fn=cmd_financials)

    sp = sub.add_parser("options", help="list expirations, or chain for --date")
    add_ticker(sp)
    sp.add_argument("--date", help="expiration YYYY-MM-DD (omit to list dates)")
    sp.add_argument("--limit", type=int, default=None, help="max rows per side")
    sp.set_defaults(fn=cmd_options)

    sp = sub.add_parser("dividends", help="dividend history")
    add_ticker(sp); sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(fn=cmd_dividends)

    sp = sub.add_parser("analyst", help="price targets + recommendations")
    add_ticker(sp); sp.set_defaults(fn=cmd_analyst)

    sp = sub.add_parser("holders", help="major + institutional holders")
    add_ticker(sp); sp.add_argument("--limit", type=int, default=10)
    sp.set_defaults(fn=cmd_holders)

    sp = sub.add_parser("news", help="recent news headlines")
    add_ticker(sp); sp.add_argument("--limit", type=int, default=10)
    sp.set_defaults(fn=cmd_news)

    sp = sub.add_parser("download", help="multi-ticker bulk close summary")
    sp.add_argument("tickers", help="space/comma separated, e.g. 'AAPL MSFT'")
    sp.add_argument("--period", default="1y")
    sp.add_argument("--interval", default="1d")
    sp.add_argument("--start"); sp.add_argument("--end")
    sp.add_argument("--full", action="store_true", help="include close series")
    sp.add_argument("--limit", type=int, default=None)
    sp.set_defaults(fn=cmd_download)

    sp = sub.add_parser("selftest", help="end-to-end smoke test")
    sp.set_defaults(fn=cmd_selftest)

    return p


def main():
    args = build_parser().parse_args()
    yf = _import_yf()
    try:
        args.fn(args, yf)
    except SystemExit:
        raise
    except Exception as e:
        _emit(args.cmd, error=f"unexpected: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
