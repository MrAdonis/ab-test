# SHARED-BASE — 两臂共享的 skill description 设计基线

以下是 `~/.claude/references/skill-design-patterns.md` 中与「skill 触发 / description」直接相关的现有模式。两个臂（A 和 B）都拥有这些。

## 模式 8：不要让 agent "自己判断要不要"

含糊的触发条件会被 agent 跳过或滥用。写死：

- ❌ "需要时使用 stealth profile"
- ✅ "遇到 Cloudflare / captcha / 403 且目标内容**不在**登录墙后时，加 `browser_profile: stealth` 重试一次"

触发条件 = 可观测的页面特征 + 可枚举的动作，不是"判断力"。

## 模式 9：Progressive Disclosure 三层加载（节选）

| 层级 | 内容 | 何时加载 | 大小约束 |
|------|------|---------|---------|
| **L1 Metadata** | frontmatter: name + description | 始终在 context（决定是否触发） | < 100 词 |
| **L2 SKILL.md body** | 触发后加载的核心指令 | skill 被触发时 | < 500 行 |
| **L3 references/scripts/assets** | 按需加载 | agent 在 L2 中被告知路径 | 无限制 |

**关键规则**：
- description（L1）是唯一触发机制。body 里写 "When to Use" 是无效的——触发后才加载
- Claude 倾向 **undertrigger**（该用 skill 时不用）。对抗办法：description 写得"pushy"一点。例如不写 "How to build a dashboard"，而写 "...Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"

## 自检清单相关项

- [ ] 触发条件是可观测特征，不是"按需判断"？
