分析这段 JavaScript 代码：

```javascript
// 图片缓存：同一个 URL 只加载一次，并发请求复用结果
const cache = new Map();

async function loadImage(url) {
  if (cache.has(url)) {
    return cache.get(url);
  }

  const img = new Image();
  img.src = url;
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
  });

  cache.set(url, img);
  return img;
}

// 并发调用场景：
async function preload() {
  // 用户进入页面，瀑布流同时请求 10 张同 URL 的封面图
  const promises = Array(10).fill(0).map(() => loadImage('/hero.jpg'));
  await Promise.all(promises);
}
```

监控数据观察到：每次 preload() 实际触发了 10 次 /hero.jpg 的网络请求，
不是预期的 1 次。cache 也确实工作了——第二次调用 preload() 时是 0 次请求。

请按以下结构回答：

## 1. 根因（机制层面，不只是「哪行错了」）
精确到事件循环顺序，解释为什么会有 10 次请求。

## 2. 为什么 cache 第二次能命中、第一次不能？
解释 cache 在第一次 preload 期间的状态变化时间线。

## 3. 修复方案
给出完整修复后的代码。

## 4. 推理路径
展示你是怎么从「10 次请求」这个症状推到根因的——你的诊断思路。

只输出回答，不要重复 prompt。
