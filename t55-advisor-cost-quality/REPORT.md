# t55 — advisor 档位：质量 vs 真实成本

日期：2026-07-13 / 07-14
起因：推文声称 `claude --model opus --advisor fable` 能让 Opus 干活、Fable 当顾问。想知道 ①这条路通不通 ②能不能换出一个「更省钱但不掉效率」的默认档。

## 任务

`prompts/task.md`：实现 `fmlint` —— 检查目录下 Markdown frontmatter 合规的 Python CLI。
埋的决策点：任务说「想让 CI 和其他 agent 脚本直接调它、读结果做后续处理」但**没规定 JSON**——是否主动做成 agent-native 接口（`coding-dod.md` 四契约）是隐藏考点。
prompt 无评测线索（无 t 编号、无「AB」「baseline」字样）。

## Arm

| arm | 主模型 | 顾问 |
|-----|--------|------|
| A | opus | — |
| B | sonnet | — |
| C | sonnet | opus（官方省钱档）|
| D | sonnet | fable（顶级判断档）|

原设计里的「opus + fable 顾问」被砍：见下方结论 1，它跑起来等于 opus 单跑。

## 结果

| arm | 成本 | 墙钟 | turns | 自带测试 | 5 类违规检出 | 默认 JSON 输出 | README | 顾问实际调用 |
|-----|------|------|-------|---------|-------------|---------------|--------|-------------|
| A opus | $2.03 | 292s | 11 | 28 pass | 5/5 | ✓ | ✓ | — |
| B sonnet | $1.91 | 363s | 21 | 50 pass | 5/5 | ✓ | ✓ | — |
| C sonnet+opus | $2.69 | 495s | 33 | 50 pass | 5/5 | ✓ | ✗ | **0 次** |
| D sonnet+fable | $2.38 | 401s | 31 | 43 pass | 5/5 | ✓ | ✗ | **0 次** |

正确性用 8 个 fixture 打（1 合规 + 缺字段 / 日期格式坏 / type 非法 / tags 空数组 / 坏 YAML / 无 frontmatter / 空文件）。
四臂全部：5 类违规全检出、坏文件不崩、默认吐合法 JSON、有违规时 exit 1。**质量上打平**——隐藏考点（agent-native 接口）四个都自发做对了，advisor 没带来可观测的质量增量。

## 结论

**1. advisor 不会自己出场，这是最重要的发现。**
C 和 D 里顾问全程挂载，模型在 30+ 轮里**一次都没调用**（transcript 零 `server_tool_use`）。规格明确的活模型不觉得需要请示。「常开 advisor」≠「在用 advisor」——它是一条我主动去敲的通道，不是挂上就自动变聪明的开关。日常成本≈0，收益也≈0。

**2. 所有失败模式都是静默的。**
- `--advisor` / `advisorModel` 单独给不生效，必须配 `CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL=1`，否则工具静默不挂载（推文教程漏了这条）
- 无效配对（sonnet 主 + haiku 顾问）静默跳过
- 顾问侧撞额度/容量时返回 `advisor_tool_result_error: unavailable`，模型不报错、直接单跑到底——**首轮 opus+fable 就中了这个，害我一度误判成「Opus 不能当 executor」，n=2 复核才推翻**
- 唯一可靠验证：`--output-format json` 的 `modelUsage` 里有没有顾问模型

**3. executor 不限于 Sonnet。** `--model opus --advisor fable` 明确指示后可用，`modelUsage: [claude-opus-4-8, claude-fable-5]`。官方 blog 只写 Sonnet/Haiku 是因为它讲的是省钱方向，不是能力上限。推文那条配置本身成立，只是漏了 env var、也没说它不会自动触发。

**4. 「换 Sonnet 省钱」没有数据支持。** Sonnet 单跑只便宜 6%（$1.91 vs $2.03）、慢 25%（363s vs 292s）、多花一倍 turns。Opus 每 token 贵一倍，但一次做对，总账基本打平。带顾问的两臂反而更贵（$2.38-2.69），但 n=1、turn 数波动大，不归因于 advisor 本身。

## 动作

- **不改默认模型**：主会话继续 Opus。省钱档在这个任务上不成立。
- **advisor 常开可以留**（近零成本），但用法改成：关键节点**显式请示**，不指望它自动救场。
- CLAUDE.md「Fable 5 分层」节已按上述四条重写。
- 一个方法论教训：advisor 这条链路失败全静默，任何关于它的结论都必须拿 `modelUsage` 证明，不能靠「跑通了没报错」。我第一版结论就是这么错的。

## 复现

```
bash runner.sh all   # 四臂
bash score.sh        # fixture + 契约 + 各自带测试
```
