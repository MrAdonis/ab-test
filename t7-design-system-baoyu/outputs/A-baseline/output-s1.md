# A Baseline - S1 CJK 阅读器输出摘要

## 字体栈
```css
--f-sans: 'Source Sans 3', system-ui, sans-serif;
--f-serif: 'Lora', 'Georgia', serif;
```
→ 无 CJK fallback

## 行高
- bodyLeading = serif ? 1.85 : 1.75

## lang 属性
- html[lang="zh-Hans"] 仅根元素
- 正文段落无 lang 属性

## Babel 多文件
- CDN: `react@18`（未锁版本，无 integrity）
- data.jsx 末尾无 Object.assign(window, ...)
- 数据在 data.jsx 里但没有导出，app.jsx 无法访问！

## Dark mode
- :root + [data-theme] CSS 变量 ✓
- CSS.setTheme(dark) 写属性 ✓
