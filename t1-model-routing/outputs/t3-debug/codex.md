## 1. 根因

根因不是 `Map` 失效，而是缓存写入发生在图片加载完成之后，无法覆盖“正在加载”的并发阶段。

事件循环顺序如下：

1. `preload()` 在同一个宏任务里执行。
2. `Array(10).map(...)` 同步连续调用 10 次 `loadImage('/hero.jpg')`。
3. 第 1 次调用 `loadImage`：
   - `cache.has(url)` 是 `false`
   - 创建 `new Image()`
   - 执行 `img.src = url`
   - 浏览器开始调度 `/hero.jpg` 的网络请求
   - 遇到 `await new Promise(...)`，函数挂起，返回一个 pending Promise
   - 注意：此时还没有执行 `cache.set(url, img)`
4. 第 2 次到第 10 次调用发生时，第 1 次还没有等到图片加载完成，`cache` 仍然是空的。
5. 所以每一次调用都会：
   - 判断缓存未命中
   - 创建新的 `Image`
   - 设置 `src`
   - 触发一次新的 `/hero.jpg` 请求
6. 等网络请求完成后，`onload` 作为任务触发，Promise resolve。
7. async 函数的后半段作为微任务继续执行：
   ```js
   cache.set(url, img);
   return img;
   ```
8. 这时缓存才被写入，但已经太晚了，10 个请求都已经发出。

所以第一次并发场景下，缓存没有存“正在进行中的加载任务”，只存了“已经加载完成的图片结果”。

## 2. 为什么 cache 第二次能命中、第一次不能？

第一次 `preload()` 期间的状态是：

```text
开始 preload
cache = empty

第 1 次 loadImage:
  cache miss
  发起请求 #1
  await，挂起
  cache 仍然 empty

第 2 次 loadImage:
  cache miss
  发起请求 #2
  await，挂起
  cache 仍然 empty

...

第 10 次 loadImage:
  cache miss
  发起请求 #10
  await，挂起
  cache 仍然 empty
```

之后图片陆续加载完成：

```text
请求 #1 完成 -> cache.set('/hero.jpg', img1)
请求 #2 完成 -> cache.set('/hero.jpg', img2)
...
请求 #10 完成 -> cache.set('/hero.jpg', img10)
```

最终：

```text
cache = {
  '/hero.jpg' => 最后完成并写入的那一个 img
}
```

所以第一次并发调用期间，缓存一直到请求完成后才有值，挡不住并发请求。

第二次调用 `preload()` 时，`cache` 已经有 `/hero.jpg` 了：

```js
if (cache.has(url)) {
  return cache.get(url);
}
```

因此 10 次都会直接命中，不再触发网络请求。

## 3. 修复方案

关键是缓存 Promise，也就是缓存“正在加载中的任务”，而不是等加载完成后才缓存图片对象。

```javascript
// 图片缓存：缓存正在进行中的 Promise
const cache = new Map();

function loadImage(url) {
  if (cache.has(url)) {
    return cache.get(url);
  }

  const img = new Image();

  const promise = new Promise((resolve, reject) => {
    img.onload = () => {
      resolve(img);
    };

    img.onerror = (error) => {
      cache.delete(url); // 加载失败时清掉缓存，允许后续重试
      reject(error);
    };
  });

  cache.set(url, promise);

  img.src = url;

  return promise;
}

async function preload() {
  const promises = Array(10)
    .fill(0)
    .map(() => loadImage('/hero.jpg'));

  await Promise.all(promises);
}
```

这里第 1 次调用会同步执行：

```js
cache.set(url, promise);
```

因此后续 9 次调用会立即复用同一个 Promise，不会创建新的 `Image`，也不会再次设置 `src`。

## 4. 推理路径

从症状看：

```text
第一次 preload(): 10 次请求
第二次 preload(): 0 次请求
```

这说明两件事：

1. `cache` 本身是有效的。
2. 问题只发生在第一次并发加载期间。

如果缓存完全无效，第二次也会继续请求。如果浏览器缓存或 HTTP 缓存问题是主因，表现也不会严格对应 `preload()` 的第一次和第二次。

所以诊断重点应该放在：

```js
cache.set(url, img);
```

它什么时候发生？

看到它在 `await` 后面：

```js
await new Promise(...);

cache.set(url, img);
```

这意味着缓存写入必须等图片加载完成。

而 `preload()` 里的 10 次 `loadImage` 是同步启动的：

```js
Array(10).fill(0).map(() => loadImage('/hero.jpg'))
```

`map` 不会等待前一个 async 函数完成。每次 `loadImage` 都只执行到第一个 `await`，然后立刻返回 pending Promise，继续下一次调用。

因此可以推出：

```text
10 次 loadImage 调用全部发生在任何一次 cache.set 之前
```

于是 10 次都会看到 `cache.has(url) === false`，各自创建 `Image` 并设置 `src`，最终触发 10 次请求。

修复方向自然就是：第一次发现缓存未命中时，立刻把“正在加载的 Promise”放进缓存，让同一轮并发调用能共享它。