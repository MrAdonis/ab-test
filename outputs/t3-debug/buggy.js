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

// 监控数据观察到：每次 preload() 实际触发了 10 次 /hero.jpg 的网络请求，
// 不是预期的 1 次。cache 也确实工作了——第二次调用 preload() 时是 0 次请求。
// 找出根因并解释机制。
