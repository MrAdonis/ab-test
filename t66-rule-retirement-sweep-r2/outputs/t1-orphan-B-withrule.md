仓库里没有 `src/render/post.js` 这个文件（应该是你贴的独立代码片段),所以我直接把改好的内容给你,你贴回项目里替换即可:

```js
// src/render/post.js
import dayjs from 'dayjs'
import { legacyEscapeHtml } from '../utils/legacy'

// 旧版编辑器时代的标题清洗，处理富文本粘贴进来的转义
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
- 去掉了 `formatDate`/`parseDate` 的引用和中间变量 `d`,直接用 `dayjs(post.createdAt).fromNow()` 生成"3 天前"这种相对时间。
- `datetime` 属性保留原始绝对时间(`post.createdAt`),这是 `<time>` 标签的标准做法,不影响显示。
- 顺带提一句:`sanitizeLegacyTitle` 在原文件里就没被调用(标题直接用了 `post.title`),这是原有的死代码,和本次改动无关,我没有动它。
