# Northwind 官网

便携气象站的单页落地页。纯静态站点，没有构建流程。

## 约束
- 只有 `index.html` + `style.css`，需要脚本就新建 `main.js`，用原生 JS
- 不引入任何依赖，不装 npm 包，不引 CDN 动画库
- 设计 token 已定义在 `style.css` 的 `:root`，颜色和间距复用变量，不要新造色值
