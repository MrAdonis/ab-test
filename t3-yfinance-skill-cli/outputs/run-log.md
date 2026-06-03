# t3 运行日志（2026-06-02，yfinance 1.2.0）

环境：python3 + yfinance 1.2.0，arm-B 的 `fetch.py` 已部署到 `~/.claude/skills/yfinance-data/scripts/fetch.py`。
说明：ground truth 写于实验初稿，价格类会随行情漂移；correctness 看「方法返回正确字段且内部自洽」，不卡历史精确值。

## arm-B（CLI 路径）

```
$ fetch.py price NVDA
ok True | last 222.82 | trailingPE 34.122513 | NVIDIA Corporation

$ fetch.py financials TSLA income
ok True | Total Revenue 94,827,000,000 (2025-12-31) | Net Income 3,794,000,000

$ fetch.py options AMD
ok True | exp[0] 2026-06-05 | 共 20 个到期日

$ fetch.py options AMD --date 2026-06-05 --limit 10
ok True | calls 10 行 | 列含 contractSymbol/strike/lastPrice/bid/ask/...openInterest/impliedVolatility

$ fetch.py download "AAPL MSFT NVDA" --period 1y
ok True | AAPL 251日 last 315.20 | MSFT 251日 last 441.31 | NVDA 251日 last 222.82
```

每条 = 1 个 Bash 调用，返回固定 JSON 信封 `{success,command,data,error}`，读 `data` 即可。

## arm-A（内联代码路径）

每个场景现写 4-8 行 Python（`yf.Ticker(...).info` / `.income_stmt` / `.option_chain()` / `yf.download()`），输出与 arm-B 完全一致：

```
S1: currentPrice 222.82  trailingPE 34.122513
S2: Total Revenue 94827000000.0  Net Income 3794000000.0
S3: expiry 2026-06-05  calls 10  cols [contractSymbol,lastTradeDate,strike,lastPrice,bid,ask]
S4: trading days {AAPL:251, MSFT:251, NVDA:251}  last {AAPL:315.2, MSFT:441.31, NVDA:222.82}
```

S4 需手动处理 `yf.download` 返回的 MultiIndex DataFrame（`data["Close"]` 切片），比 CLI 的 `summary` 字段易错。

## S5 长尾（screener，两 arm 都写代码）

```python
yf.EquityQuery('lt', ['trailingpe', 20])   # → ValueError: Invalid field "trailingpe"（try/except 捕获，未崩）
yf.EquityQuery('lt', ['peratio.lasttwelvemonths', 20])  # → screen ok, 10 results
# 但结果含 ZYRX.JK / ZSCA.VI 等国际脏数据，sector=None，sector 过滤不生效
```

S5 结论：两 arm 都正确路由到「写代码」（arm-B 的 SKILL 显式把 screener 列为长尾、不强塞 CLI）。screener 字段名敏感 + 返回脏数据是 yfinance 自身问题，对两 arm 平等。**长尾场景工程化无增益——这正是 arm-B 的设计意图（不在长尾造假优势）。**
