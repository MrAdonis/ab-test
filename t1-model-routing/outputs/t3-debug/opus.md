## 1. 根因（机制层面，不只是「哪行错了」）

根因是**「检查 cache」和「写入 cache」之间存在一段 await 间隙**，10 个并发调用全部在第一个 await 完成之前就已经穿过了 `cache.has(url)` 检查。

精确到事件循环顺序：

```
[同步阶段]
preload() 执行 → Array(10).fill(0).map() 同步创建 10 个 Promise
  ↓
loadImage 调用 #1:
  - cache.has('/hero.jpg') → false（cache 是空的）
  - new Image() 创建 img1
  - img1.src = url → 浏览器在后台发起 HTTP 请求 #1
  - await new Promise(...) → 把 loadImage #1 挂起，控制权交回
  ↓
loadImage 调用 #2:
  - cache.has('/hero.jpg') → false（cache 仍然是空的！）
  - new Image() 创建 img2
  - img2.src = url → 浏览器发起 HTTP 请求 #2
  - await ... → 挂起
  ↓
... 重复 8 次，发起请求 #3-#10 ...
  ↓
[同步阶段结束，10 个请求都已发出]

[异步阶段]
某个图片 onload 触发 → 对应的 await 恢复 → cache.set(url, img)
  ↓
后续 onload 陆续触发 → 重复 cache.set（互相覆盖，但 key 相同所以最终只有一个 entry）
```

关键机制：

- `img.src = url` 是**同步赋值**，但浏览器发起 HTTP 请求是这一行的副作用，请求会立即排队进网络栈
- `await new Promise(...)` 只能挂起**当前**的 async function，不会阻止微任务队列里其他 async function 继续执行
- `cache.set(url, img)` 必须等到 `img.onload` 触发后才会执行——而 `onload` 是网络 IO 完成才触发的宏任务/微任务，远远晚于 10 个同步 `cache.has` 检查

所以这不是 race condition 的概率问题，是**确定性的**：只要 10 个调用在同一个同步轮次里发出，就一定全部命中 false 分支。

## 2. 为什么 cache 第二次能命中、第一次不能？

时间线（第一次 preload）：

```
t=0ms   cache = Map {}
t=0ms   loadImage #1: has() → false, src=url（请求 #1 发出）, await 挂起
t=0ms   loadImage #2: has() → false, src=url（请求 #2 发出）, await 挂起
...
t=0ms   loadImage #10: has() → false, src=url（请求 #10 发出）, await 挂起
        ↑↑↑ 整段同步执行内 cache 始终为空 ↑↑↑

t=50ms  img1.onload → resolve → cache.set('/hero.jpg', img1)  cache = { '/hero.jpg': img1 }
t=50ms  img2.onload → resolve → cache.set('/hero.jpg', img2)  覆盖
...
t=50ms  img10.onload → resolve → cache.set('/hero.jpg', img10)
        cache 最终 = { '/hero.jpg': img10 }
```

第二次 preload：

```
t=1000ms cache 已经是 { '/hero.jpg': img10 }
t=1000ms loadImage #1: has() → true, 直接 return img10
t=1000ms loadImage #2: has() → true, 直接 return img10
...
        没有任何 new Image()，0 次请求
```

核心：cache 的写入发生在 await 之后，第一次 preload 期间这 10 个调用都在 await **之前**就已经检查过 cache。第二次时 cache 已被填充，has() 直接命中。

## 3. 修复方案

修复思路：**把 Promise 本身（而不是解析后的 img）放进 cache，并且在发起请求之前就放进去**。这样后续并发调用 has() 时能拿到那个正在 pending 的 Promise，await 它即可复用结果。

```javascript
// 图片缓存：同一个 URL 只加载一次，并发请求复用同一个 Promise
const cache = new Map();

function loadImage(url) {
  if (cache.has(url)) {
    return cache.get(url);
  }

  const promise = new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = (err) => {
      cache.delete(url); // 失败时清掉缓存，允许后续重试
      reject(err);
    };
    img.src = url;
  });

  cache.set(url, promise); // 关键：同步写入 cache，在任何 await 之前
  return promise;
}

async function preload() {
  const promises = Array(10).fill(0).map(() => loadImage('/hero.jpg'));
  await Promise.all(promises);
}
```

关键改动：

1. **缓存 Promise 而不是 img**：第一次调用同步创建 Promise 并立即 `cache.set`，第 2-10 次调用 has() 直接命中，拿到同一个 pending Promise，await 它就拿到 img——网络请求只发一次
2. **去掉 loadImage 的 async 关键字**：不需要了，直接返回 Promise 即可。async 在这里反而引入了一层不必要的 Promise 包装
3. **错误处理时清 cache**：否则一次失败之后这个 URL 永远拿到失败的 Promise，不可恢复
4. **`img.src = url` 移到 onload/onerror 绑定之后**：避免极端情况下（从缓存读取的图片）src 赋值瞬间就触发 onload，事件处理器还没绑定上

## 4. 推理路径

诊断思路按时间顺序：

**Step 1 - 接住症状描述里的关键对比**

「10 次请求 vs 第二次 0 次请求」这个对比非常重要——它告诉我 cache 写入逻辑本身是对的（否则第二次也会是 10 次），bug 只能在「读 cache」和「写 cache」之间的时序上。所以这不是"忘了写 cache"的低级错误，是并发时序问题。

**Step 2 - 找 cache 的写入点**

`cache.set(url, img)` 在第 19 行，前面有一个 `await`（第 14 行）。立刻警觉：**await 之前的代码同步执行，await 之后的代码要等异步完成。如果 has() 在 await 之前、set 在 await 之后，那么 await 期间所有并发调用都会看到旧的 cache 状态**。

**Step 3 - 复盘并发调用的执行顺序**

`Array(10).fill(0).map(() => loadImage('/hero.jpg'))` 是同步的 map，10 次 loadImage 调用在同一个 tick 内连续发起。每次调用走到 await 才挂起。所以同步阶段会执行 10 次 `has()` + 10 次 `new Image()` + 10 次 `img.src = url`。

`img.src = url` 触发浏览器发起请求——10 次。这就是 10 次请求的来源。

**Step 4 - 验证假设**

如果根因正确，那么：
- 第二次 preload 时 cache 已经被填充 → 应该 0 次请求 ✓（符合观察）
- 如果把 10 改成 1 → 应该 1 次请求（符合直觉）
- 如果在两次 loadImage 之间加 `await new Promise(r => setTimeout(r))` → 应该只有 1 次请求（让 cache.set 有机会执行）

这三个推论都和观察一致，根因确认。

**Step 5 - 想修复方案**

要让并发调用复用同一次请求，必须在第一个调用的同步阶段就把"占位符"放进 cache。占位符是什么？必须是后续调用 await 之后能拿到 img 的东西——**Promise**。所以缓存 Promise 而不是 img，并且 `cache.set` 必须在任何 await 之前同步执行。

这是 JavaScript 里典型的「promise caching / request coalescing」模式——SWR、React Query、各种 dataloader 库底层都是这个思路。
