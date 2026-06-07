# B Improved - S1 CJK 阅读器输出摘要

## 字体栈
```css
--font-sans: -apple-system, "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif;
--font-serif: "Newsreader", "Georgia", "Songti SC", "Noto Serif SC", serif;
```
→ Latin 前置，CJK 后补，serif 含 Songti SC ✓

## 行高
- paragraph: line-height: serif ? 1.9 : 1.75
- lead: line-height: serif ? 1.85 : 1.75
→ 均 ≥ 1.7 ✓

## lang 属性
- html[lang="zh"] ✓
- h1 title: lang="zh" ✓
- 每段 body block: lang={block.lang}（data.jsx 里每段标注了 lang）✓

## Babel 多文件
- CDN: react@18.3.1 + integrity hash ✓
- data.jsx 末尾: Object.assign(window, { ARTICLES, CATEGORY_COLORS }) ✓
- app.jsx 用 window.ARTICLES 消费 ✓
- 样式命名：listStyles / readerStyles，无 const styles 冲突 ✓
- 预览命令：python3 -m http.server 4311 ✓

## Dark mode
- :root + [data-theme="dark"] CSS 变量 ✓
- React state 只存 "light"|"dark" 字符串 ✓
- document.documentElement.setAttribute 切换 ✓
