# t30 — 工具用前校验机制吸收（reverse-skill 按需自举工具链）

日期：2026-06-23
来源：github.com/zhaoxuya520/reverse-skill（逆向/渗透安全技能路由包，2.7k star，MIT）的「按需自举工具链」三件套：`bootstrap-manifest.json` + `tool-index.md` + 用前校验协议
被改对象（若 KEEP）：候选落点 = 新增 `~/.claude/tool-index.md` + 在 `rules/coding.md` 或 `routing.md` 补一段「工具用前校验协议」；待 AB 结果定

状态：**已跑（2026-06-23，Sonnet 生成 + Sonnet 盲评）→ 结论 KEEP**

## 假设

把 reverse-skill 的「声明式工具清单 + 用前校验路径 + 缺失声明式补装」协议，从 Windows/安全场景蒸馏成一段通用的「本机工具用前校验」规则补进配置。增量与现状的关系：现状是「路径散落写进各条 rule（inline code 绝对路径）」，本增量是「集中式可查清单 + 用前 verify + 缺失补装」一层。

## 单变量设计

- 共用基底 `SHARED-BASE.md`（现状的工具路由摘要 + 环境事实，A/B 都拿到）。
- 增量 `INCREMENT.md`（用前校验协议 4 步 + 防过度套用跳过条件 + 示例 tool-index 片段），仅 B 臂。
- 唯一变量 = 有无「工具清单 + 用前校验」协议段。生成与评分均用 Sonnet。

## 场景（3 个，含 1 个过度套用风险场景）

1. **调用不常用本机工具**（B 应占优）：冷门中文金融概念升级搜索 + 搜历史会话，考察是否引用真实脚本路径（anysearch.sh / session-grep.py）并用前 verify，还是猜命令形态。
2. **工具缺失/未注册**（测自举补装）：抓 Cloudflare 被动指纹站（g2.com），正解 Scrapling 但默认没装，考察是否 verify→发现缺→声明式补装，还是假设已装裸跑。
3. **标准命令**（过度套用风险）：git status / log / 数 .ts 文件，全是 coreutils+git 标准命令，考察 B 会不会对显然存在的命令画蛇添足套校验仪式。

## 关键张力（本测要回答的真问题）

baseline **不弱**——用户的 rules/memory 里到处是 inline code 绝对路径，AI 靠 rules 本身就能答准不少工具路径。所以本测的真问题不是「校验有没有用」，而是「在路径已散落写进 rules 的前提下，再加一层集中清单 + 用前 verify，是真增量还是堆料」。若 A 臂靠现有 rules 就答得准、B 没拉开差距 → 按编辑纪律判 ROLLBACK。

## 结果（独立盲评，甲/乙 跨场景交换位置消除位置偏差）

| | Arm-A | Arm-B | 差 |
|-|-------|-------|----|
| 场景 1 不常用工具 | 40 | **43** | +3 |
| 场景 2 缺失补装 | 33 | **44** | +11 |
| 场景 3 标准命令 | 49 | 49 | 0 |
| **总计** | 122 | **136** | **+14** |

逐场景盲评要点：
- **场景 1（+3，最干净的机制信号）**：两臂路径/参数都准（baseline 靠 rules 里写过 anysearch 路径就答对了，印证 baseline 不弱）。差距全在校验纪律轴——B 用 `test -x` 检可执行 + `--help` 确认脚本可用 + `python3` 显式调用避开 shebang 坑；A 把 anysearch 验证写成跑一条真查询（成本高），且 session-grep 完全跳过校验直接给命令。**这是协议「用前 verify」的纯信号。**
- **场景 2（+11，但需打折）**：B 全面领先（缺失处理/校验纪律/可执行性），但 +11 里很大一块是 A 栽在 `Fetcher.get(url, ...)` 类方法误写（Scrapling 实际是实例方法，用户照抄报 TypeError）——这是**生成方差**不是纯协议功劳。即便扣掉这一项，B 的「verify→缺→确定性补装→重 verify」结构仍比 A 完整，真实增量约 +3~5。
- **场景 3（0，过度套用防御通过）**：两臂都 49，B 完全没对 git/find/wc 套校验仪式。证明 INCREMENT 的「跳过条件」写得够清，模型对标准命令真的克制——**这是 KEEP 的前提，没翻车。**

## 结论：KEEP

判定标准（`JUDGE.md`）：B 在场景 1+2 实质胜出 + 场景 3 不输/微输（≤1）= KEEP。实测 B 净胜 14，场景 3 零差且零噪声，达成 dominant-ish baseline。

**诚实备注**：场景 2 的大分差被一次生成方差（A 的 API 误写）放大，不能全记协议头上。真正稳的两个信号是 ①场景 1 的 verify 纪律（+3 纯净）②场景 3 的过度套用防御通过（标准命令零仪式）。机制核心价值——「用前 verify + 跳过条件防过度套用」——在最该测的两处都成立，故 KEEP，但落地时把 always-loaded 足迹压到最小（见下），不堆料。

## 落地（KEEP 后）

- 新建 `~/.claude/tool-index.md`：自含「工具用前校验协议」4 步 + 跳过条件 + 初始工具清单表（按需读，不常驻 context）。
- `rules/coding.md`「工具调用」处加 1 行指针（唯一的 always-loaded 净增），触发条件 = 调用不常用本机工具/自定义脚本前读 tool-index。
- memory 记一条 `feedback_tool_index_verify.md`（confidence: high，AB 验证过）。
- 编辑纪律（wiki-lifecycle §5）：always-loaded 仅 +1 行指针，主体放按需文件，避免膨胀。

## 怎么跑（执行步骤）

1. 对每个场景，分别用 Sonnet 跑 A 臂（喂 SHARED-BASE + scenario）和 B 臂（喂 SHARED-BASE + INCREMENT + scenario），产出存 `outputs/s{N}-{A,B}.md`。
2. 用 Sonnet 按 `JUDGE.md` 盲评（不告知哪臂是 A/B），填上表。
3. 按判定标准下 KEEP/ROLLBACK 结论，回填本文件。
4. KEEP → 落地 + 在 memory 记一条；ROLLBACK → 记 `*_rejected.md` 负反馈（见 `rules/wiki-lifecycle.md` §5 rejected-edit buffer）。
