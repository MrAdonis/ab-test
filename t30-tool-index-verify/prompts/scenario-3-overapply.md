# 场景 3 — 标准命令（过度套用风险，B 臂易翻车）

> 跑法：A 臂 = `SHARED-BASE.md` + 本场景；B 臂 = `SHARED-BASE.md` + `INCREMENT.md` + 本场景。生成用 Sonnet。

## 任务 prompt（原样喂给被测模型）

帮我看一下当前 git 仓库的状态、最近 5 条提交、以及 src 目录下有多少个 .ts 文件。直接给命令。

---

## 考察点（评分时参考，不喂给被测模型）

- 全是 POSIX/coreutils + git 标准命令（`git status` / `git log -5` / `find src -name '*.ts' | wc -l`），属 INCREMENT 明确列出的「跳过校验」范畴。
- B 臂预期（合格）：直接给命令，**不**去查 tool-index、**不**对 git/find/wc 跑 verify、**不**讨论缺失补装。
- B 臂翻车信号（重扣噪声控制轴）：对 `git`/`find`/`wc` 套用「先查清单确认路径」「verify command -v git」之类仪式。
- A 臂预期：直接给命令（baseline 本就不会画蛇添足）。
- 本场景测的是：B 臂的协议有没有把「跳过条件」写清楚到让模型真的克制。若 B ≈ A（都干净利落），过度套用防御通过；若 B 比 A 啰嗦，证明协议会制造噪声 → 不利 KEEP。
