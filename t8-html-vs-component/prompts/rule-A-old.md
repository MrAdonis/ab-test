# 路由规则（版本 A · 旧）

## UI 原型/设计稿默认 HTML

做 UI mockup / 设计稿 / interactive prototype / 给客户或同事看的视觉方案时，默认让 Claude 输出 **HTML 文件**（inline CSS + 必要时 SVG/JS 交互），不出"描述设计的 markdown"。HTML 信息密度高（表格/SVG/CSS/交互一起装）、浏览器直开免转换、可做 sliders+knobs 的参数闭环（copy-as-prompt 带回 Claude Code）；markdown 描述设计稿对方读完仍想象不出来。

**适用**：mockup、prototype、设计 review、parametric 调参（颜色/动画/布局可拖动）、给客户或同事预览的视觉方案、spec 文档要带可视化时

**不适用**（仍走原工具）：
- 真实组件代码 → 项目框架（React/Vue/Astro），不是 HTML 单文件
- 结构化工程图（流程/架构/ER/时序/甘特等）→ `/diagram`（SVG 确定性渲染）
- 数据/统计图表 → `/diagram`（精确）或 `/baoyu-infographic`（视觉强）
- 设计 tokens / CSS variables → 项目 design system，不是临时 HTML
- 引擎食粮（`task_plan.md` / `HANDOFF.md` / `MEMORY.md` / `rules/`）→ 保持 markdown
