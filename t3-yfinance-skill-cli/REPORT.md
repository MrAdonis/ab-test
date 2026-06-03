# t3 评分报告：yfinance skill 工程化（内联代码 vs 固化 CLI）

> 测试日期 2026-06-02 · yfinance 1.2.0 · 评分者独立对照 outputs/run-log.md
> A = 现行 SKILL（每次现场写 Python）· B = 工程化 SKILL（top-op 走 `fetch.py` CLI，长尾才写代码）

## 评分维度（每场景 0-10）

正确性(0-3) + Token 经济(0-3) + 稳定性(0-2) + 路由正确(0-2)

## 矩阵

| 场景 | 类型 | arm-A | arm-B | 差距来源 |
|------|------|------:|------:|----------|
| S1 NVDA 价格+PE | top-op | 7.5 | 10 | A 现写 4 行 + 调重量级 `.info`；B 一条命令走 fast_info |
| S2 TSLA 利润表 | top-op | 7.5 | 10 | 同上，B 命令 + 固定 JSON |
| S3 AMD 期权链 | top-op×2步 | 7.0 | 9.5 | 2 步链 A 代码量翻倍；B 两条干净命令 |
| S4 三股对比 | top-op | 7.0 | 10 | A 要手处理 MultiIndex df（易错）；B 直接给 summary |
| S5 科技股筛选 | 长尾 | 8.0 | 8.0 | **平手**——两 arm 都正确路由到写代码，screener 不稳对两者平等 |
| **总分** | | **37.0** | **47.5** | |

## 结论：B > A（+10.5 / 50），落地

- **优势全集中在高频 top-op（S1-S4）**：固化 CLI 把「构造 Ticker + try/except + 格式化 + 选字段」从每次重写降为一条命令，正确性持平的前提下省 token、提稳定性（同一份代码每次跑，无字段选择方差如 `info` vs `fast_info`）。
- **长尾平手（S5）是健康信号**：arm-B 的 SKILL 显式把 screener/sector/search/ESG 列为「CLI 不覆盖、写代码」，没有为了好看硬塞 CLI。工程化只在该工程化的地方拿分，不在长尾造假优势。
- **设计验证**：「prefer the CLI, fall back to code」的分层是对的——把确定性的 80% 固化，把开放式的 20% 留给代码。

## 可复现

1. 部署 arm-B 的 `arm-B/fetch.py` 到 PATH，确认 `yfinance` 已装（`python3 -c "import yfinance"`）。
2. 按 `scenarios.md` 的 S1-S5，arm-B 跑对应 `fetch.py` 子命令，arm-A 现写等价内联 Python。
3. 对照 `scenarios.md` 的 ground truth 与评分维度打分。
4. 注意：价格类 ground truth 会漂移；correctness 看方法/字段是否正确，不卡历史精确值。

样本量小（5 场景），结论是方向性证据，不是 benchmark。
