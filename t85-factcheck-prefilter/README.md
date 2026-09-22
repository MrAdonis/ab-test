# t85 — 事实核查预筛层（REJECT）

给 content-audit 加一层确定性数值预筛（模型只判对不上的那几处），看检出率会不会涨。**不会**：两臂 12/12 打平、误报都是 0，加了预筛的那臂还多花 2.5% token、8.6% 时间。

完整分析见 [REPORT.md](./REPORT.md)。

## 文件

| 路径 | 是什么 |
|------|--------|
| `mutate.py` | 生成变异语料 + `ground-truth.json`。12 处注入 + 3 个误报陷阱全在文件顶部明文写着 |
| `prefilter.py` | 被测的那一层。稿件数值 → 底本指标行，出 MISMATCH / UNVERIFIED / MATCHED 三档 |
| `score.py` | 确定性打分。11 处按唯一数值标记搜 P0 段，第 12 处（方向反转）走人工 |
| `prompts/arm-a.md` | A 臂（现行 content-audit 流程） |
| `prompts/arm-b.md` | B 臂（逐字相同 + 预筛结果一段，含盲区声明） |
| `prefilter-reports/` | 三天的预筛输出，B 臂读的就是这个 |
| `outputs/` | 6 份原始审核结果 |
| `score.json` | 打分结果 |

语料本身（变异后的稿件 + research 底本）没进仓库——它来自本机 `~/Projects/personal/stock-daily-report/output/`，`mutate.py` 跑一遍就能复现。

## 复现方式

```bash
/opt/homebrew/bin/python3 mutate.py                        # → /tmp/audit-corpus/
/opt/homebrew/bin/python3 prefilter.py /tmp/audit-corpus/2026-09-18.txt \
                                       /tmp/audit-corpus/2026-09-18_research.txt \
                                       > /tmp/audit-prefilter/2026-09-18_prefilter.md
# prompts/ 下两份模板替换 {date} / {out}，起 6 个非 fork sonnet 子代理
/opt/homebrew/bin/python3 score.py /tmp/audit-out
```

拿自己的语料跑：改 `mutate.py` 顶部的 `MUTATIONS` 和 `TRAPS`，改 `prefilter.py` 的 `ALIASES`（那张表是 stock-daily-report 专用的）。

## 防污染措施

- 两臂 prompt 无 t 编号、无「AB」「baseline」「评测」字样，写成真实审核请求
- 子代理非 fork —— fork 会继承主会话里的注入清单
- 语料目录只放稿件和底本，预筛报告单独放另一个目录，A 臂 `ls` 也撞不到 AB 痕迹
- B 臂 prompt 显式声明预筛的盲区，不声明就是诱导它偷懒、测出来的优势是假的
- `score.py` 做过反向验证（故意造漏判和误报，确认它变红），红绿输出都贴在 REPORT.md 里
