Reading this as: **SaaS 定价页（redesign / preserve）** for **已看过首页、正在评估订阅的独立开发者**, with a **克制商务 + 纸感编辑** language, leaning toward **首页已建立的品牌 token（moss/amber/paper 原生 CSS）延伸**。

量化维度：VARIANCE 6 / MOTION 3 / DENSITY 5——定价页需要清晰的横向比较，密度略高于首页 features，但不做数据驾驶舱级别的压缩。

## 做了什么

`/Users/edon/Projects/personal/ab-test/t42-hallmark-absorb/outputs/s1-A.html`，单文件、内联 CSS、零外部依赖，直接复用首页 `s1-page1.html` 的品牌 token（`--ink/--paper/--moss/--moss-deep/--amber/--line/--radius`）和字体栈，视觉上是同一产品的延续而非另起一套。

结构：Header（导航高亮"定价"）→ 极简 Hero（无 CTA，把决策交给下方卡片，避免和首页 hero 布局家族重复）→ 月付/年付切换 pill → 三档定价卡 → FAQ 手风琴（6 问，超过最低 4 问要求）→ 收尾 CTA band → Footer。

**三档定价**：免费版 ¥0/永久（1 渠道、手工记账）；独立版 ¥29/月（推荐档，5 渠道自动同步、报税导出，年付 ¥296/年≈¥24.7/月，省 ¥52）；工作室版 ¥79/月（无限渠道、多主体、3 个会计协作席位，年付 ¥806/年≈¥67.2/月，省 ¥142）。年付折扣按 85 折精确计算后取整。

**设计取舍**：三张卡没有做成 AI 常见的"等宽三列 + 左边框 accent"套路——独立版故意做成非等宽（1.08fr）+ 上移 12px + 品牌色调阴影，靠视觉重量而不是彩色边框传达"推荐"；特性列表用单条 `border-top` 分隔而不是设计规范明确禁用的"每行上下双边框 spec 表"。强调色 amber 只用在推荐徽章和年付省钱提示两处，符合"一个 view 一种 accent"。

**交互**：月付/年付切换和 FAQ 手风琴都是原生 JS（无框架），FAQ 用 CSS Grid `0fr→1fr` 做平滑展开而不是纯 JS 计算高度；按钮统一 `min-height:44px` 保证触摸目标（这一点比首页原按钮更严格，首页按钮实测高度约 36-38px 不达标，本页做了正向修复但视觉样式没变）。全部交互元素有 `:focus-visible` 环，FAQ 按钮带完整 `aria-expanded`/`aria-controls`/`role="region"`，计费切换带 `aria-pressed`。`prefers-reduced-motion` 降级已处理。

## 已知取舍/未做

未做移动端汉堡菜单（沿用首页做法：≤560px 直接隐藏 nav-links，只留 logo + CTA），如果首页后续加菜单这里要跟进保持一致。未接入真实支付/试用流程，CTA 都是占位 `href="#"`。未做暗色模式（首页没有，保持一致不引入新维度）。

对比度、触摸目标、tag 平衡已做基础自检（Python 脚本核对开闭标签数一致）；未跑 Lighthouse/无障碍工具做最终验证，建议部署后过一遍 `web-quality`。
