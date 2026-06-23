# t25 场景与评分定义

测试对象：design-system SKILL.md 新增「## UI 微文案（界面文案规范）」章节是否带来可测提升。源自 Vercel Geist design.md 的 `Voice & Content` 节，对照现有配置后判定为真缺口（rules/writing.md 只管内容写作、B2B 段只有一行错误文案规则）。

- Variant A：无 UI 微文案章节（原版 387 行）
- Variant B：含 UI 微文案章节（+18 行 = 405 行）
- 唯一变量 = 该章节（python 切片插入，diff 验证为 229a230,247 单段插入）
- 生成：6 个 Sonnet 子代理（3 场景 × A/B），只读各自 variant 文件，禁读 ~/.claude/
- 评审：3 个 Sonnet 盲评 judge，双盲（设计稿 1/2，顺序每场景随机）

## S1 — 中文 B2B 后台组件（核心靶场，微文案密度最高）

**Brief 给生成代理**：实现一个「团队成员管理」后台页面（中文界面，单 HTML + 内联 CSS/JS）。要求覆盖：成员表格（含一行行级删除按钮）、列表为空时的空状态、数据加载中的状态、删除成员的确认弹窗、删除成功/失败后的反馈提示、顶部「邀请成员」主操作按钮。给出完整可渲染 HTML，并在文末列一份「界面文案清单」（把页面里所有按钮 label / 空状态 / 错误 / toast / 加载文案逐条列出）。

**埋的考点（全是微文案）**：
- 按钮 label 是否动词+名词（`邀请成员`/`删除成员` vs `确定`/`提交`）
- 空状态是否指向 next action（vs `暂无数据`）
- 加载态是否带对象+进行式+省略号（vs `加载中...`/`请稍候`）
- 错误是否「发生什么+怎么办」（vs `删除失败`/`出错了`）
- toast 是否报具体对象、去句号、不带"成功"（vs `成功删除了该成员。`）
- 删除确认是否破坏性语义清晰、不卖萌

**评分（满分 10）**：
1. 微文案质量（45%）：上述 6 类文案逐项核，每类按"功能化精准 vs 通用占位/卖萌/裸词"打分
2. 状态完整性（25%）：empty/loading/error/success/确认 五态是否都实现且文案匹配（与 skill §组件状态、§B2B 四态共有规则）
3. 反 AI Tell + 可用性（20%）：是否落 emoji 图标/假数据/低对比；focus-visible、删除走破坏性确认
4. 代码可渲染（10%）：单文件能直接打开，无报错

## S2 — 英文 SaaS 设置页保存流程（测大小写分工 + 不可逆操作文案）

**Brief**：Build a settings page for a SaaS app (English UI, single HTML + inline CSS/JS). Include: a profile form (display name, email) with a save button and success/error feedback; a "Danger Zone" with an irreversible **Delete Account** action behind a confirmation dialog; an in-progress state while saving. Output full renderable HTML, then list every UI string (button labels / toasts / errors / empty or in-progress states) at the end.

**埋的考点**：
- Title Case 用在 button/label，sentence case 用在 helper/toast
- action=verb+noun（`Save Changes`/`Delete Account` vs `Submit`/`OK`/`Confirm`）
- toast 去 successfully、去句号（`Changes saved` vs `Successfully saved your changes.`）
- 进行态 `Saving…` 现在分词+省略号字符
- 错误 what+how（`Couldn't save. Email already in use. Try another.`）
- 破坏性操作（Delete Account）确认文案清晰、不用裸 `OK`

**评分**：
1. 微文案质量（45%）：大小写分工 / verb+noun / toast 规范 / 进行态 / 错误模板 / 破坏性确认，逐项核
2. 状态完整性（25%）：save 的 idle/in-progress/success/error + 删除确认是否齐全
3. 反 AI Tell + 可用性（20%）：英文场景禁 em-dash（rules/writing.md，A/B 共有基线）、对比度、focus、破坏性走 AlertDialog 语义
4. 代码可渲染（10%）

## S3 — 控制场景：中文营销 landing（章节不该泄漏噪音）

**Brief**：为一个新的笔记类 App「墨记」做一个中文营销落地页（single HTML + 内联 CSS）。品牌方向你来定，要有 hero、核心卖点、CTA。输出完整可渲染 HTML。

**评分**：
1. 设计质量与方向感（40%）：量化 dial 声明、美学方向、记忆点、hero 不堆砌
2. 无噪音（30%）：是否把 UI 微文案规范（toast/空状态/错误/进行态）错误地塞进一个**没有这些控件**的营销页；landing 的标题/CTA 标语是否被微文案"功能化、删形容词"规则误伤成干瘪文案
3. 反 AI Tell（20%）：紫渐变/三列卡片/eyebrow 超额/em-dash
4. 可用性（10%）：对比度、移动端

## 盲评映射（judge 不可见）

| 场景 | 设计稿1 | 设计稿2 |
|------|---------|---------|
| S1 | B | A |
| S2 | A | B |
| S3 | B | A |

## 判定

加权均分 B > A 即 keep（写入 SKILL.md + memory）；B ≤ A 按「无提升则回滚」不加该章节。关注点：S1/S2 是靶场，B 应在微文案维度显著胜；S3 是控制组，B 不得产生噪音（理想 B≈A 或微胜）。败因若集中在非微文案维度（设计品味波动），按单跑噪声处理。
