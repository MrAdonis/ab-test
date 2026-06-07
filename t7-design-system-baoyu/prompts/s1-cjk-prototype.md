# Scenario 1：CJK 双语阅读器 UI 原型

## Prompt（两个版本用同一 prompt）

做一个 iOS 阅读器 App 的 UI 原型（HTML + React）。

功能：
- 文章列表页 + 文章阅读页
- 中英文混合内容（标题中文、正文段落中英混杂）
- 两种阅读模式：Sans（浏览）和 Serif（深阅读），页面内切换
- 深色/浅色主题切换

技术要求：
- React + Babel inline（不用构建工具）
- 多个 .jsx 文件拆分
- 本地预览

## 评分维度（各 0-10）

### CJK 字体栈（0/5/10）
- 0：完全没有 CJK fallback，直接用 Inter/Roboto/sans-serif
- 5：有 PingFang SC 或 Noto Sans SC 但 Latin 没前置，或缺 lang 属性
- 10：`-apple-system, "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif` 结构正确，Latin 前置 CJK 后补

### CJK 行高（0/5/10）
- 0：line-height ≤ 1.5（默认值）
- 5：1.6（稍好但仍不够）
- 10：正文 line-height ≥ 1.7，且 CJK 和 Latin 段落区分对待

### Serif 模式 CJK fallback（0/5/10）
- 0：serif 模式只有 Latin serif，中文静默回退 sans
- 5：有 Noto Serif SC 但未配 "Songti SC"
- 10：`"Newsreader", "Songti SC", "Noto Serif SC", serif` 完整配对

### lang 属性（0/5/10）
- 0：完全没有 lang 属性
- 5：只在 html 根元素加了 lang，内容块没区分
- 10：中文内容块 lang="zh"，英文段落 lang="en" 正确标注

### React Babel 多文件约束（0/5/10）
- 0：const styles 在多个文件重名，或没有 Object.assign(window, ...) 共享组件
- 5：没有 const styles 冲突，但组件共享方式不对（用了 import）
- 10：唯一命名 styles，Object.assign(window, {...}) 正确导出，加载顺序合理

### Dark mode 实现方式（0/5/10）
- 0：用 React state 条件渲染 `dark ? colorA : colorB`
- 5：CSS 类切换但没用 CSS 变量
- 10：`:root` + `[data-theme="dark"]` CSS 变量，一个属性翻转

**总分：/60**
