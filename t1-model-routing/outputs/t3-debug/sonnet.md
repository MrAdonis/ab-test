## 1. 根因（机制层面）

问题在于 `cache.set(url, img)` 发生在异步等待**之后**，而 10 个并发调用在 `cache.set` 执行前全部通过了 `cache.has(url)` 检查。

事件循环顺序：

1. `preload()` 用 `.map()` 同步创建 10 个 Promise，10 次调用 `loadImage('/hero.jpg')` 在**同一个同步微任务帧**里依次发起
2. 第 1 次调用执行 `cache.has(url)` → 返回 `false`，创建 `new Image()`，设置 `img.src`（触发第 1 次网络请求），然后 `await new Promise(...)` 挂起，**把控制权还给调用栈**
3. 第 2 次调用立刻执行，此时 `cache.has(url)` 仍然是 `false`（`cache.set` 还没跑到），再次创建 `new Image()`、再次设置 `img.src`（第 2 次网络请求），挂起
4. 第 3 到第 10 次调用重复相同流程——共触发 10 次 `img.src = url`，即 10 次网络请求
5. 等第 1 张图片加载完，`onload` 回调进入微任务队列，恢复第 1 个 `await`，执行 `cache.set(url, img)`——此时才写入缓存，但 9 个并发请求早就发出去了

根因一句话：**`cache.set` 在异步边界（`await`）之后执行，而多个调用者在缓存写入前就已经完成了"命中检查"**，导致 N 个调用各自独立走完了创建-请求-等待全流程。

---

## 2. 为什么第二次 preload 能命中、第一次不能？

第一次 `preload()` 的状态时间线：

| 阶段 | cache 状态 |
|------|-----------|
| 10 个 `loadImage` 全部执行 `cache.has` | `false`（cache 为空） |
| 10 个 `img.src = url` 发出，10 个 `await` 挂起 | 仍为空 |
| 第 1 张图加载完，`cache.set(url, img)` 执行 | 写入第 1 条 |
| 第 2-10 张图陆续加载完，各自 `cache.set` | 后 9 次 set 用相同 key 覆盖，最终 cache 有 1 条 |

第二次 `preload()` 时，`cache` 已有 `/hero.jpg` 的记录，10 个 `loadImage` 调用执行 `cache.has(url)` 全部命中，直接 `return cache.get(url)`，不创建 `Image` 对象，不触发网络请求。

关键差异：**第一次所有"读缓存"操作都发生在"写缓存"之前**；第二次则相反。

---

## 3. 修复方案

将正在进行中的 Promise 本身存入缓存（而不是等加载完再存结果），这样并发请求拿到的是同一个 Promise，只有一次真实的网络请求。

```javascript
const cache = new Map();

async function loadImage(url) {
  if (cache.has(url)) {
    return cache.get(url);
  }

  const promise = new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });

  // 立即写入缓存（在任何 await 之前），后续并发请求复用同一个 Promise
  cache.set(url, promise);

  return promise;
}

async function preload() {
  const promises = Array(10).fill(0).map(() => loadImage('/hero.jpg'));
  await Promise.all(promises);
}
```

修复要点：
- 把 Promise 对象在**同步路径**上立刻 `cache.set`，不等异步完成
- 第 1 次调用写入 `promise`；第 2-10 次调用读到同一个 `promise`，直接返回——只创建了 1 个 `Image` 对象，触发 1 次网络请求
- `onload` 里把 `img` 传给 `resolve`，保持原接口语义（返回 HTMLImageElement）

---

## 4. 推理路径

**症状**：10 次并发调用触发 10 次网络请求；第二次调用是 0 次。

**第一步——排除缓存完全失效**：第二次 0 次请求说明 `cache` 本身工作正常，`Map` 读写没有问题。所以不是 key 生成错误、不是 Map 被清空，也不是逻辑判断写反。

**第二步——缩小到时序问题**：`cache` 在第一次 preload 结束后确实有数据，但 10 次并发全都没命中。唯一能解释"缓存存在但同批次没命中"的场景，是**写入时机晚于所有读取时机**。

**第三步——找写入时机**：`cache.set` 在 `await new Promise(...)` 之后——这是一个异步边界。`await` 会挂起当前函数、把控制权交回调用栈。

**第四步——还原事件循环**：`.map()` 是同步循环，10 个 `loadImage` 在一个同步帧里依次执行。每次执行到 `await` 就挂起，**下一次 map 回调立刻开始**。10 次回调全部在第一个 `await` 恢复（即第一次 `cache.set`）之前执行完毕。

**第五步——得出根因**：10 次 `cache.has` 都在 `cache.set` 之前运行，结果都是 `false`，各自创建 `Image`，各自发网络请求。

**修复方向**：把缓存写入从"异步完成后"提前到"发起异步前"，即缓存 Promise 而非结果。这是标准的"Promise coalescing"模式，常见于 HTTP 请求去重、资源预加载等场景。
