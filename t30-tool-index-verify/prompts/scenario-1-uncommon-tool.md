# 场景 1 — 调用不常用本机工具（B 应占优）

> 跑法：A 臂 = `SHARED-BASE.md` + 本场景；B 臂 = `SHARED-BASE.md` + `INCREMENT.md` + 本场景。生成用 Sonnet。

## 任务 prompt（原样喂给被测模型）

我要查一个中文金融微观结构的冷门概念（「指定做市商的报价义务豁免」在 A 股的具体规则），通用搜索抓不到中文专业源。请直接给出你要执行的完整命令，并说明为什么用这个工具、怎么确认它能用。

另外这次还想顺带搜一下：我之前在哪次会话里讨论过「做市商」相关的内容——也给出命令。

---

## 考察点（评分时参考，不喂给被测模型）

- 升级搜索该走 `~/.claude/scripts/anysearch.sh`，中文要加 `--zone cn --lang zh-CN`——路径和参数对不对，还是猜了个 `websearch`/裸 curl？
- 搜会话该走 `~/.claude/scripts/session-grep.py <词>`——路径对不对，还是猜了个 grep transcript 目录的命令？
- 用前有没有 verify 这两个脚本可执行，还是假设存在直接给命令？
- B 臂预期：引用清单真实路径 + verify；A 臂预期：路径可能对（rules 里写过 anysearch）但 session-grep 容易猜错形态，且通常不 verify。
