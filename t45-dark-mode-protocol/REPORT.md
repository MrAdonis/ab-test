# t45 — 暗色模式协议章节 AB Test

**日期**: 2026-07-04
**被测改动**: `~/.claude/skills/design-system/SKILL.md` 新增「## 暗色模式协议」章节(+15 行,蒸馏自 Leonxlnx/taste-skill v2 §8 Dark Mode Protocol + §4.11 Page Theme Lock + §6.C,对照现有配置判定为真缺口——此前仅交付清单一行「暗色模式如适用验证对比度」)
**判定规则**: 加权均分 B > A 即 keep;B ≤ A 按「无提升则回滚」不加该章节
**结论**: **KEEP**(B 8.31 > A 7.49,+0.82,三场全胜)

## 缺口来源

推文热度带回 tasteskill.dev(= Leonxlnx/taste-skill,同一项目)复查。我们已吸收其 Redesign 协议(t18)和 6 条确定性检查(design-lint.sh taste-checks.mjs),全量对照 v2 后剩两个真缺口:暗色模式协议(本次)和 Brief→设计系统映射(候选,未测)。现有 skill 对 dark mode 的覆盖仅一行清单项,无协议级章节——双模式默认、token 策略、层级 parity、主题锁、系统偏好全部缺失。

## 设置

- **Variant A**: 当前 SKILL.md(405 行,含 2026-07-04 的 html paths 修复)— `variant-A.md`
- **Variant B**: A + 暗色模式协议章节(420 行)— `variant-B.md`
- 唯一变量 = 该章节;python 单锚点插入(`## 技术护栏` 前),diff 验证 `277a278,292` 单段
- **生成**: 6 × Sonnet 子代理(3 场景 × A/B),每个只读自己的 variant,brief 内联,禁读 ~/.claude/ 与 ~/.agents/
- **评审**: 3 × Sonnet 盲评 judge,中性副本 `judge/sN-design{1,2}.html`,映射 S1:1=B / S2:1=A / S3:1=B(judge 不可见,禁读 MAPPING.txt)

## 场景

| 场景 | 类型 | 测什么 |
|------|------|--------|
| S1 协作 SaaS 仪表盘(显式要求双模式) | 靶场 | token 统一/对比度独立/parity/无纯黑白/主题锁/系统偏好 |
| S2 阅读 App「夜航」landing(brief 不提模式) | 靶场 | 「默认双模式」条款自发性 + 实现质量 |
| S3 书店编辑风纸面 landing | 控制 | 协议豁免仿印刷编辑风——B 是否泄漏暗色噪音破坏纸感 |

## 结果

| 场景 | A | B | margin | 胜者 |
|------|-----|-----|--------|------|
| S1 仪表盘(靶场) | 7.57 | **8.58** | +1.01 | B |
| S2 消费 landing(靶场) | 7.10 | **8.20** | +1.10 | B |
| S3 编辑风控制 | 7.80 | **8.15** | +0.35 | B |
| **均分** | 7.49 | **8.31** | **+0.82** | **B** |

## 分析

**S1 胜因精确命中协议条款**:A 在 HTML 硬编码 `data-theme="light"`,完全不理系统偏好;B 的 CSS 媒体查询让 `prefers-color-scheme` 首屏即生效——正是「默认跟随系统」条款的直接产物。诚实记录 B 的短板:A 用 `--accent-contrast` token 把一处文字压色块对比度做到 8.96:1,B 同位置只有 3.03:1(协议要求「暗色对比度独立验证」,B 侧生成代理执行不完全);A 另有 Google Fonts CDN 破坏单文件自包含、但有更好的移动响应式和 localStorage 持久化。净差 +1.01 主要由系统偏好这条基础分决定。

**S2 是本次最有价值的验证——「默认双模式」条款在 brief 静默时起效**:brief 一字不提颜色模式,A 出了纯暗色单模式(深夜炭蓝贴「夜航」品牌,有理由但没有任何系统偏好考量,白天访问可用性受损),B 自发做双模式(暖纸白/近黑藏青双 token + 系统检测 + 手动覆盖 + 两模式保持琥珀强调色可识别)。judge 判 B 「完整的专业级处理」,A 靠文案和字体工程追回部分分,仍差 1.10。这正是章节存在的意义:模型默认不会自发双模式,条款把它变成默认。

**S3 控制组干净且反向加分**:B 侧生成代理明确判定「仿印刷编辑风,不触发暗色模式协议」(引自其决策记录),零 JS 纯印刷结构;A 反而加了滚动 JS 淡入(与印刷品气质冲突 + 无 JS 兜底内容隐藏风险)。B +0.35 与协议无因果(A 败因是自己的 JS 决策),关键结论是**豁免边界起效、零泄漏**。

**与 t18/t25 的一致性**:第三例新领域章节 AB 通过,且首次三场全胜(t18/t25 均为 2/3)。「饱和的是 greenfield 设计规则密度,新任务类型/新协议域仍能通过」的收窄判据三度确证。

## 落地

- **KEEP**: 章节写入真实 `~/.claude/skills/design-system/SKILL.md`,插在 §组件状态规范 与 §技术护栏 之间
- lint 层暂无新增:纯黑纯白/硬编码 theme 属确定性可检,但需先在 design-lint.sh 引擎里评估是否有干净落点,另行处理不混入本次
- memory: `feedback_design_system_distill_rejected` 追加 t45 为第三例
- 候选 2(Brief→设计系统映射表)留待下次,不与本次混测

## 文件

- variants: `variant-A.md` / `variant-B.md`;章节草稿 `dark-mode-section.md`
- 场景: `prompts/scenarios.md`
- 产出: `outputs/s{1,2,3}-{A,B}.html`
- 盲评: `judge/s{1,2,3}-verdict.md`(中性副本 + `judge/MAPPING.txt`)
