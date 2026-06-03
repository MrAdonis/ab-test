# Claude AB Test 公开仓库

> 我自己跑过的 AB test 公开放这里。每个测试一个文件夹，自带 prompt + 原始输出 + 评分矩阵，可直接复现。
>
> 维护：[@MrAdonis](https://github.com/MrAdonis) · 时间戳跟模型在迭代，结论会过期

---

## 测试列表

| 编号 | 主题 | 验证 | 结论 |
|------|------|------|------|
| [t1](./t1-model-routing/) | Opus 4.7 / Sonnet 4.6 / Codex GPT-5.5 模型分流 | 4 任务 × 3 模型，找各模型最优场景 | Codex 中文 5/10 禁推文；GPT-5.5 前端已和 Opus 持平 |
| [t2](./t2-feedback-grading/) | Code Review 反馈 4 档分级（Must/Optional/Nit/FYI） | 同 Sonnet 加/不加规则对比，3 场景盲测 | Treatment 9.0 / baseline 7.2，入 `~/.claude/rules/coding.md` |
| [t3](./t3-yfinance-skill-cli/) | yfinance skill：每次现写 Python vs 固化成 CLI | 5 场景跑两 arm，对照 ground truth 评分 | 固化 CLI 47.5 / 内联代码 37；优势全在高频 top-op，长尾平手 |

每个文件夹自带 `README.md` + `REPORT.md` + 测试用例（`prompts/` 或 `scenarios.md`） + `outputs/`。

## 这个仓库做什么

- 我学到的"最佳实践"喂进自己的配置前，先 AB test 验证一遍——结论无提升就回滚
- 测试用例公开放出来，别人想验证我的结论 / 改 prompt 重跑 / 拿去做自己的 AB，都行
- 不写"我觉得 X 更好"的主观博客文章——只放跑过的输出 + 评分矩阵

## 复现方式

每个测试文件夹的 `README.md` 里有 "复现方式" 章节，列出 prompt 路径 + 评分方法。基本上是：

1. 把 `prompts/` 下的文件喂给对应模型（Opus / Sonnet / Codex）
2. 把输出按 `scoring-prompt.md` 的格式塞进评分 prompt
3. 跑独立模型评分
4. 对比你的分数和本仓库 `REPORT.md` 的分数

样本量都小（4-6 个产出），结论应作为方向性证据，不是 benchmark。

## License

MIT
