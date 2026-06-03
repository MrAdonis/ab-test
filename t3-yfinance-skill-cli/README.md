# t3 · yfinance skill 工程化：内联代码 vs 固化 CLI

验证一个 skill 设计问题：高频数据操作，是每次让 agent **现场写 Python**，还是**固化成一个 CLI**、只在长尾才写代码？

- **arm-A**（baseline）= 现行 SKILL：每次请求现写 `yf.Ticker(...)` + try/except + 格式化代码。
- **arm-B**（treatment）= 工程化 SKILL：top-op（价格/历史/财报/期权/对比等）走 `fetch.py` 子命令拿固定 JSON 信封；screener / sector / search / ESG 等开放式长尾才写代码。

## 结论

**B 47.5 / A 37（/50）**，B 落地。优势全集中在高频 top-op（S1-S4），长尾（S5）平手——工程化只在该工程化的地方拿分。完整矩阵见 [`REPORT.md`](./REPORT.md)。

## 文件

- [`scenarios.md`](./scenarios.md) — 5 个场景 + ground truth + 评分维度
- [`arm-A/`](./arm-A/) — baseline SKILL（`SKILL.md` + `api_reference.md`）
- [`arm-B/`](./arm-B/) — treatment SKILL（`SKILL.md` + `fetch.py` + `references/`）
- [`outputs/run-log.md`](./outputs/run-log.md) — 两 arm 实跑原始输出
- [`REPORT.md`](./REPORT.md) — 评分矩阵 + 结论

## 复现方式

1. 确认 `python3 -c "import yfinance"` 通过（本次 1.2.0）。
2. arm-B：把 `arm-B/fetch.py` 放到 PATH，按 `scenarios.md` 跑对应子命令。
3. arm-A：按同样场景现写等价内联 Python。
4. 对照 `scenarios.md` 的 ground truth + 4 维度打分，比你的分数和 `REPORT.md`。

价格类 ground truth 随行情漂移，correctness 看方法/字段正确性，不卡历史精确值。样本量小（5 场景），方向性证据，非 benchmark。
