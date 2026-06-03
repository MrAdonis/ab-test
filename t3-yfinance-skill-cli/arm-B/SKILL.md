---
name: yfinance-data
description: >
  Fetch financial and market data using the yfinance Python library.
  Use for: stock prices, historical data, financial statements, options chains, dividends,
  earnings, analyst recommendations, or any single-stock / multi-stock data retrieval.
  Triggers: ticker symbol (AAPL, MSFT, TSLA, etc.), "get me the financials", "show earnings",
  "what's the price of", "download stock data", "options chain", "dividend history",
  "balance sheet", "income statement", "cash flow", "analyst targets", "institutional holders",
  "screen for stocks", or any request involving Yahoo Finance data.
  NOT for: stock correlation/pair analysis (→ stock-correlation), options payoff charts (→ options-payoff).
  When user only provides a ticker, infer intent from context.
paths: ["**/*.py", "**/*.ipynb"]
---

# yfinance Data Skill

Fetches financial and market data from Yahoo Finance using the [yfinance](https://github.com/ranaroussi/yfinance) Python library.

**Important**: yfinance is not affiliated with Yahoo, Inc. Data is for research and educational purposes.

---

## Core principle: prefer the CLI, fall back to code

The stable, high-frequency operations are already固化 in `scripts/fetch.py` — a CLI that
constructs the Ticker, handles errors, and returns a fixed JSON envelope. **Do NOT regenerate
that boilerplate inline.** Only write Python by hand for the open-ended long tail that the CLI
does not cover (screener, sector/industry, custom EquityQuery, search, ESG).

`fetch.py` output contract (every subcommand, success or failure):

```json
{"success": true|false, "command": "<cmd>", "data": <any>|null, "error": "<str>"|null}
```

Read `data`. **Never parse stdout as plain text.** On `success:false`, show the `error` string — do not retry blindly.

---

## Step 1: Ensure yfinance Is Available

```
!`python3 -c "import yfinance" 2>/dev/null && echo OK || echo "YFINANCE_NOT_INSTALLED — run: pip install -q yfinance"`
```

---

## Step 2: Route — does the CLI cover this request?

Match the request to a subcommand below. If it matches, **run the CLI** (one Bash call, no code).
The script lives at `~/.claude/skills/yfinance-data/scripts/fetch.py`.

| User Request | Command |
|---|---|
| Current price / quote | `python3 .../fetch.py price AAPL` |
| Company overview / sector / summary | `python3 .../fetch.py info AAPL` (add `--all` for every field) |
| Price history / chart data | `python3 .../fetch.py history AAPL --period 1y --interval 1d` (or `--start/--end`) |
| Income statement / revenue | `python3 .../fetch.py financials AAPL income` (`--quarterly` for quarterly) |
| Balance sheet | `python3 .../fetch.py financials AAPL balance` |
| Cash flow | `python3 .../fetch.py financials AAPL cashflow` |
| Options expirations | `python3 .../fetch.py options AAPL` |
| Options chain for a date | `python3 .../fetch.py options AAPL --date 2026-06-21 --limit 20` |
| Dividend history | `python3 .../fetch.py dividends AAPL` |
| Analyst targets / recommendations | `python3 .../fetch.py analyst AAPL` |
| Institutional / major holders | `python3 .../fetch.py holders AAPL` |
| Recent news | `python3 .../fetch.py news AAPL` |
| Compare multiple tickers (bulk) | `python3 .../fetch.py download "AAPL MSFT GOOGL" --period 1y` (`--full` for series) |

Discovery: `python3 .../fetch.py --help` lists commands; `<cmd> --help` shows flags;
`python3 .../fetch.py selftest` verifies the tool works.

**The CLI returns structured JSON, not formatted text.** After it returns, summarize the
relevant numbers for the user (Step 4) — do not just dump the JSON.

---

## Step 3: Long tail — write code (only when the CLI doesn't cover it)

These are NOT in the CLI because they are open-ended; write Python using
`references/api_reference.md`:

- **Screening / filtering** stocks (`yf.Screener` + `yf.EquityQuery`)
- **Sector / industry** data (`yf.Sector`, `yf.Industry`)
- **Search** by company name (`yf.Search`)
- **Shares outstanding over time** (`ticker.get_shares_full`)
- **ESG / sustainability** (`ticker.sustainability`)
- Any combination/transform the CLI subcommands can't express (e.g. custom multi-metric joins)

Pattern when writing code:

```python
import yfinance as yf
try:
    # ... use the method from references/api_reference.md
except Exception as e:
    print(f"Error: {e}")
```

Rules: wrap in try/except; `yf.download()` for multi-ticker; list `ticker.options` before
`option_chain(date)`; intraday limits (1m ~7d, 1h ~730d).

---

## Step 4: Present the Data

1. **Summarize key numbers** in a brief text response (price, market cap, P/E, etc.)
2. **Show tabular data** formatted for readability when the user wants detail
3. **Highlight notable items** — earnings beats/misses, unusual volume, dividend changes
4. **Provide context** — sector averages, historical ranges, analyst consensus when relevant

---

## Reference Files

- `scripts/fetch.py` — agent-native CLI for the stable ops (price/history/financials/options/dividends/analyst/holders/news/download). Run `--help` / `selftest`.
- `references/api_reference.md` — full yfinance API for the long-tail code path (screener/sector/search/ESG).
