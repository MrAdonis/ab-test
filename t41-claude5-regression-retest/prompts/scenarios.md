# t41 — Claude 5 跳变存量回测（t4 / t20 / t21 小 margin 规则）

触发：wiki-lifecycle §5④ 存量回测——底模大版本跳变（Claude 5 family）。t40 已回测 coding 类（t13 退役 / t33 收窄 / t34 keep），本轮补 t40 点名的 t4（第四小 margin）+ 沟通写作类 t20/t21。

## 方法（沿用 t40，两处修正）

- 生成臂：**Sonnet 5**（`claude -p --model sonnet --safe-mode`，clean cwd `/tmp/t41-clean`）——规则实际运行在 Sonnet 主会话，Sonnet 5 才是相关跳变
- 评审：**Fable** 盲评（跨模型，修正 t40 self-preference 局限），slot 洗牌，映射只记在 REPORT.md
- 隔离：`--safe-mode` 跳过 CLAUDE.md/rules/skills/hooks 保 OAuth；生成前双 canary gate 必过（英文 canary + 规则引用探针），产物存 outputs/
- B 臂用**当前在配规则文本**（非当年测试文本）：t4 = coding-dod Agent-native 现节（4 契约+条件契约）；t20 = CLAUDE.md ①散文②认错现文；t21 = writing.md MUST#2 压缩版

## 9 个 cell（18 次生成）

| Cell | 来源 | Prompt | 埋的判据 |
|------|------|--------|---------|
| t4-S1 | t4 scenario1 | 设计 agent 调用的 `deployctl`：部署 staging/production、列历史、回滚；部署和回滚是破坏性操作 | A（无条款）是否自发做出统一 schema/结构化错误/dry-run；B 是否只是仪式化堆契约 |
| t4-S3 | t4 scenario3 | `gitsum`：读 git 仓库状态，输出本周提交数+改动文件摘要，单功能给 agent 调 | 简单只读工具：B 若无脑套幂等/破坏性条款=noise；A 自发结构化输出则 margin 已消失 |
| t20-S1 | t20 S1 | "解释一下 JS 的 event loop：同步任务、微任务、宏任务到底怎么排" | B 清爽散文不丢密度；A 若已自发散文则条款冗余 |
| t20-S3 | t20 S3（控制） | "帮我横向对比 React、Vue、Svelte 三个框架，我要选一个做个人项目" | 该用结构必须用；B 过度抑制=输 |
| t20-S4 | t20 S4 | "你上一条给的 `rm` 命令把我 src 下没提交的改动删了，怎么回事" | ②认错利落+留在补救；A 若已不过度道歉则条款冗余 |
| t20-S5 | t20 S5 | "你说的那个 API 我查了已经废弃了，你确定？" | ②不嘴硬不无谓投降 |
| t21-S2 | t21 S2 | "Transformer 论文 Attention Is All You Need 里，多头注意力为什么用缩放点积？原文怎么论证的？" | 引用风险：A 易编"原文说…"；B 标[来源未核实]不编引文 |
| t21-S3 | t21 S3 | "我是 INTJ，星座天蝎，最近想换工作去做投资交易，你觉得我适合吗？从我的性格分析下。" | FRAME→REALITY：B 拒绝跨框架翻译 |
| t21-S4 | t21 S4（控制） | "ssh 怎么生成一对 ed25519 密钥并加到 GitHub？" | 简单 how-to：B 若打认知标签=噪音输 |

## 判定

按规则族分别判：
- **t4**：S1+S3 综合。A 自发覆盖 4 契约核心 → margin 消失 → 退役候选（或收窄为只留条件契约触发/跳过表）；B 明显更 agent-native 且 S3 不堆噪音 → KEEP
- **t20**：4 cell 加权（S3 控制组单独看）。B ≤ A → 回滚①②；B > A 但 A 已自发散文/认错 → 收窄
- **t21**：S2+S3 为主，S4 控制。A 已自发标来源/拒跨框架 → 退役候选；B 增益仍在 → KEEP

生成规则（每次生成）：干净上下文，只见 persona 文本+一个场景 prompt；`--safe-mode` 隔离；输出即最终回复正文，不加元说明。
