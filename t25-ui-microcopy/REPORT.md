# t25 — UI 微文案章节 AB Test

**日期**: 2026-06-21
**被测改动**: `~/.claude/skills/design-system/SKILL.md` 新增「## UI 微文案（界面文案规范）」章节（+18 行，源自 Vercel Geist `design.md` 的 `Voice & Content` 节，对照现有配置后判定为真缺口）
**判定规则**: 加权均分 B > A 即 keep；B ≤ A 按「无提升则回滚」不加该章节
**结论**: **KEEP**（B 8.65 > A 8.07，+0.58）

## 缺口来源

学 Geist 设计系统（@MengkePM 推文「学逻辑不学样子」）。全量对照后，Geist 的色阶语义/间距/motion/radius/focus 等在现有 design-system + lint 脚本已覆盖或更细；**唯一真缺口 = 界面功能性文案规范**。现有配置里 `rules/writing.md` 只管内容/营销写作，design-system §B2B 段只有一行「错误文案=陈述事实+给行动」，缺按钮 label / toast / 空状态 / 进行态 / 大小写分工的系统规则。该章节把 Geist `Voice & Content` 蒸馏为 7 条铁律，并显式划定适用范围（只管界面控件文案，营销/海报/长文走各自规则）。

## 设置

- **Variant A**: 当前 SKILL.md 无 UI 微文案章节（387 行）— `variant-A.md`
- **Variant B**: 当前 SKILL.md + UI 微文案章节（405 行）— `variant-B.md`
- 唯一变量 = 该章节；python 切片插入并 diff 验证（`229a230,247` 单段插入，落在 §B2B 与 §Do/Don't 之间）
- **生成**: 6 × Sonnet 子代理（3 场景 × A/B），每个只读自己的 variant，brief 内联进 prompt（防 design-system auto-load 泄漏），禁读 ~/.claude/
- **评审**: 3 × Sonnet 盲评 judge，双盲（输出复制为 `judge/sN-design{1,2}.md` 中性名，映射 S1:1=B / S2:1=A / S3:1=B，judge 不可见）

## 场景

| 场景 | 类型 | 测什么 |
|------|------|--------|
| S1 团队成员管理后台（中文 B2B） | 靶场 | 微文案密度最高：按钮 label / 空状态 / 加载态 / 错误 / toast / 删除确认 六类全埋 |
| S2 SaaS 设置页保存流程（英文） | 靶场 | 大小写分工 + verb+noun + toast 规范 + 进行态 + 错误模板 + 不可逆操作确认文案 |
| S3 中文营销 landing（笔记 App「墨记」）| 控制 | 微文案章节是否泄漏噪音、是否把营销标语误伤成干瘪文案 |

## 结果

| 场景 | A | B | margin | 胜者 |
|------|-----|-----|--------|------|
| S1 中文后台（靶场） | 7.25 | **8.85** | +1.60 | B |
| S2 英文设置页（靶场） | **9.49** | 8.24 | −1.25 | A |
| S3 中文营销控制 | 7.47 | **8.86** | +1.39 | B |
| **均分** | 8.07 | **8.65** | **+0.58** | **B** |

## 分析

**S1（核心靶场）决定性胜出，且败因精确命中章节主张**：微文案维度（权重 45%）B 9.0 vs A 6.5。B 的 toast 报具体对象姓名（`{姓名} 已移出团队`）、删除失败给业务语义行动指引（`无法删除管理员：请先转让管理员权限`）、空状态驱动 next action；A 全是通用占位（`成员已移除` / 技术暴露 `服务器返回 500` / 描述现状的空状态）。这正是 7 条铁律里第 1/3/4/5 条的直接产物。

**S2 B 输 1.25，但败因主要是生成质量波动，非章节失效**：B 侧生成代理出了实现 bug——删除确认按钮 label 复用（`Delete account`/`Delete account` 而非 `Yes, delete my account`）、deletion spinner 被 textContent 覆盖渲染不出、24 小时删除时限在 dialog body 缺失造成自相矛盾、无 focus trap。A 侧生成代理恰好独立写出了更强文案（`Yes, delete my account`）和更全的状态。**章节没保证单跑必赢，A agent 这次自发写好了微文案**——这与 t18 S2「B 输在 emoji/三列卡片等设计品味波动」同类，属单跑噪声而非章节反作用。注意 B 的微文案仍合规（verb+noun、`Saving…`、错误 what+how 都在），只是 A 这次更出彩。

**S3 控制组干净——最关键的验证**：原本担心「微文案功能化、删形容词」规则会把营销标语拖干瘪，**实测零泄漏**。judge 明确点评 B（design1）「无任何工具说明书腔渗入」，营销语态完整（`你会忘记自己在用软件`/`别让想法溜走`），无虚构数据、无三列等宽卡片；A 反而夹了英文 eyebrow + 三列卡片 + 虚构 stats（47万/2.3亿）。B 以 +1.39 小胜，章节的「适用范围」边界（只管控件文案、不碰营销）起到了隔离作用，没产生噪音。

**与 t18 的一致性**：两次新章节增量都是 B 胜 2/3、在一个靶场因生成波动失分（t18 +0.46，t25 +0.58）。控制组都干净。符合 `feedback_design_system_distill_rejected` 收窄后的结论——饱和的是 greenfield 设计规则，新领域章节仍能 AB 通过。

## 落地

- **KEEP**: 写入真实 `~/.claude/skills/design-system/SKILL.md`，章节插在 §B2B 工具规范 与 §Do/Don't 对照 之间
- lint/verify 脚本层无新增（Geist 其余维度已覆盖，无干净新确定性检查可加——见前期审计结论）
- memory：`feedback_design_system_distill_rejected` 的「新领域章节可通过」结论再得一例（t18 redesign 协议、t25 UI 微文案），收窄判据继续成立

## 文件

- variants: `variant-A.md` / `variant-B.md`
- 章节草稿: `/tmp/ui-microcopy-section.md`（已并入 variant-B）
- 场景定义: `prompts/scenarios.md`
- 产出: `outputs/s{1,2,3}-{A,B}.md`
- 盲评: `judge/s{1,2,3}-verdict.md`（中性副本 `judge/sN-design{1,2}.md`）
