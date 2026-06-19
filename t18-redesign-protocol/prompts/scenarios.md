# t18 场景与评分定义

测试对象：design-system SKILL.md 新增「Redesign 协议（改版已有站点）」章节是否带来可测提升。

- Variant A：无 Redesign 协议（原版）
- Variant B：含 Redesign 协议（+15 行）
- 生成：6 个 Sonnet 子代理（3 场景 × A/B），只读各自 variant
- 评审：3 个 Sonnet 盲评 judge，双盲（设计稿 1/2，顺序每场景随机）

## S1 — 含糊 redesign brief（核心场景）

**Brief 给生成代理**：「这是我们公司的官网（Lumeo 播客数据分析），2019 年做的，现在看着太过时了，帮我现代化一下。」+ `fixtures/s1-site.html` 全文内联。用户不在场，如需澄清，写出判断与依据后继续。

**埋的陷阱**：
- 品牌紫 `#6d28d9`（"AI 默认紫"禁色 vs 品牌事实——协议说品牌事实优先）
- 健康的 SEO 基线（title/description/OG/JSON-LD）
- nav 的 URL slug（/features /pricing /customers）与文案
- 两处表单的字段名（work_email / show_name）
- 已有 focus-visible 样式（a11y 成果只进不退）
- ICP 备案号（法务文案）

**评分（满分 10）**：
1. 判型与声明（30%）：是否显式判 preserve/overhaul 并给依据；含糊 brief 下是否选择品牌演进而非推倒重来；是否先给旧站打读数再演进
2. 保留纪律（30%）：品牌紫保留？slug/nav 文案/表单字段名/meta+JSON-LD/focus 态/ICP 是否被无故改动（每改一处扣分）
3. 现代化质量（25%）：字体/间距/配色再校准是否到位，是否反 AI Tell（参照 skill 共有规则）
4. 可用性硬指标（15%）：对比度、focus、移动端、语义结构

## S2 — 显式 overhaul 但内容必须全留

**Brief**：「这个佳膳食堂的网站视觉上推倒重来，做成现代的，但上面的内容一个都不能丢——菜单、价格、订餐表单、资质信息都得在。」+ `fixtures/s2-site.html` 全文内联。

**埋的陷阱**：
- 全部内容文案（菜品/价格/服务说明/公告）
- 订餐表单字段名（name/phone/company/meal_plan/quantity）与 action
- 法务信息（ICP 备案、食品经营许可证号、电话）
- nav 的 .html slug
- 图片 alt 文本

**评分**：
1. 内容与 IA 保留（35%）：上述内容是否一字不丢；表单字段名/action 是否原样；法务信息完整
2. 视觉重做质量（30%）：是否真正脱离原站审美做出现代设计（不是小修）
3. 反 AI Tell（20%）：不落 cream+brass / 紫渐变 / 模板节奏等
4. 可用性（15%）：对比度、focus、移动端

## S3 — 控制场景：greenfield 新站（协议不该触发）

**Brief**：「为一个新的独立开发者工具 Tidewatch（网站 uptime 监控，免费 10 个监控点）做一个英文 landing page，品牌还没定，你来定方向。」无 fixture。

**评分**：
1. 设计质量与方向感（40%）：量化 dial 声明、美学方向、记忆点
2. 无噪音（25%）：是否出现与 greenfield 无关的 redesign 审计/preserve 提问等协议泄漏
3. 反 AI Tell（20%）
4. 可用性（15%）

## 盲评映射（judge 不可见）

| 场景 | 设计稿1 | 设计稿2 |
|------|---------|---------|
| S1 | B | A |
| S2 | A | B |
| S3 | B | A |

## 判定

加权均分 B > A 即 keep；B ≤ A 按「无提升则回滚」删除 SKILL.md 新章节（lint 规则不在回滚范围）。
