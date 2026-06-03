# yfinance-data 工程化 AB test — 场景与评分

A = 现行 SKILL（每次现场写 Python）
B = 工程化 SKILL（top-op 走 fetch.py CLI，长尾才写代码）

## 场景

- **S1 (top-op)**：NVDA 现在的股价和 trailing P/E 是多少？
- **S2 (top-op)**：拉 TSLA 最新年度利润表，给出总营收和净利润。
- **S3 (top-op, 2 步)**：列出 AMD 的期权到期日，并取最近到期日的 call 期权链（前 10 行）。
- **S4 (top-op)**：对比 AAPL、MSFT、NVDA 近 1 年价格——各有多少交易日数据、最新收盘价。
- **S5 (long-tail)**：筛选市值 > $10 亿、P/E < 20 的美国科技股（CLI 不覆盖，应走代码）。

## Ground truth（评委对照用）

- S1：NVDA last ≈ 222.36，trailingPE ≈ 34.05
- S2：Total Revenue ≈ 94.827B，Net Income ≈ 3.794B（最新年度列）
- S3：最近到期日 = 2026-06-05；call 链含 strike/lastPrice/openInterest/impliedVolatility 等列
- S4：AAPL/MSFT/NVDA 各 252 个交易日（1y）
- S5：无固定答案（Screener API 可能不稳）；关键是是否走代码路径、是否优雅处理失败

## 评分维度（每场景每 arm，0-10）

1. **正确性 (0-3)**：最终答案是否对上 ground truth
2. **Token 经济 (0-3)**：执行步数 + 生成代码/命令字符量，越少越好
3. **稳定性 (0-2)**：可复现、无幻觉方法、无脆弱内联代码
4. **路由正确 (0-2)**：top-op 是否走了最省的路径；长尾是否未硬塞 CLI

总分 = 5 场景 × 10 = 50/arm。B > A 才落地。
