**Design Read：个人开发者品牌站 hero section，作者身份锚定 + 产品入口，VARIANCE 7, MOTION 5, DENSITY 3**

---

## 规则节选用

适用**品牌落地页**（VARIANCE 7-9, MOTION 6-8, DENSITY 2-4），但因有功能性产品入口，MOTION 从中间取 5——避免动效喧宾夺主盖过产品 CTA。VARIANCE 取 7 而非 9，因开发者受众对过度破格有审美疲劳，精准感比视觉爆炸更有说服力。

---

## 布局策略

**版心宽度**：max-width 1280px，左右 padding clamp(24px, 5vw, 96px)。不居中对称——主标题左对齐，右侧留白 40%，构建不对称张力。

**主标题字号**：`clamp(48px, 7vw, 96px)`，字重 700-800，行高 1.05。副标题 16-18px，字重 400，颜色降至 60% opacity，形成三层信息层级（标题 → 定语 → CTA）。

**动效方向**：只做 entrance，不做 scroll parallax。标题 + 产品卡片 staggered fade-up（translateY 16px → 0，duration 0.5s，ease-out），不加 blur/scale。鼠标 hover 产品卡片：border 颜色过渡 0.15s，无位移。

---

## 反 AI 审美禁忌

1. **禁渐变标题**：`bg-clip-text` + `text-transparent` + 彩色 gradient 是 AI 生成 UI 最强视觉 tell。纯色 + 高对比即可，颜色张力来自背景色块，不是文字本身。

2. **禁50/50 split 构图**：左文右图各半屏是 AI 默认答案，对称=无设计决策。用不等比分割（如 60/40 或全宽 hero + 产品卡片沉在下方），迫使视线有一条明确的阅读路径。

3. **禁三层浮动卡片阴影**：多个产品入口用叠加投影卡片（`shadow-md` / `shadow-xl` / `shadow-2xl` 堆栈）是 AI 生成 SaaS 落地页标配。替换方案：产品入口用描边卡片或纯色背景色块区分，去掉所有 drop-shadow，用 border + 负空间代替深度。
