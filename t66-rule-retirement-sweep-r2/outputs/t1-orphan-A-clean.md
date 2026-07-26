项目里没有这个真实路径,按你贴的代码直接改好:

```js
// src/render/post.js
import dayjs from 'dayjs'
import { legacyEscapeHtml } from '../utils/legacy'

// 旧版编辑器时代的标题清洗,处理富文本粘贴进来的转义
function sanitizeLegacyTitle(raw) {
  return legacyEscapeHtml(raw).replace(/\s+/g, ' ').trim()
}

export function renderPost(post) {
  return [
    `<article>`,
    `  <h1>${post.title}</h1>`,
    `  <time datetime="${post.createdAt}">${dayjs(post.createdAt).fromNow()}</time>`,
    `  <div class="body">${post.html}</div>`,
    `</article>`,
  ].join('\n')
}
```

改动说明:
- 去掉了 `formatDate`/`parseDate` 及中间变量 `d`,直接用 `dayjs(post.createdAt).fromNow()` 生成"3 天前"这类相对时间。
- `datetime` 属性保留原始 ISO 时间(`post.createdAt`),这是 `<time>` 标签的规范用法,机器可读时间和展示文案本来就该分开。
- `sanitizeLegacyTitle`/`legacyEscapeHtml` 与日期无关,原样保留。
