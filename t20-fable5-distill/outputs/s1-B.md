JS 引擎是单线程的，所有代码在一个主线程上跑，但浏览器环境有额外的任务队列机制让异步代码"看起来"并发。

执行顺序的核心规则是：同步代码全跑完 → 清空微任务队列 → 取一个宏任务跑 → 再清空微任务队列 → 取下一个宏任务……循环往复，这就是 event loop。

**同步任务**就是普通代码，在调用栈里按顺序执行，没什么可说的。

**微任务（microtask）**主要是 `Promise.then/catch/finally`、`queueMicrotask()`、`MutationObserver` 回调。每次调用栈清空后，引擎会把微任务队列里的所有任务一口气全跑完——注意是"全部"，如果一个微任务里又产生了新的微任务，新的也会在当前这轮全部执行，不会等到下一轮。

**宏任务（macrotask/task）**是 `setTimeout`、`setInterval`、`setImmediate`（Node.js）、`MessageChannel`、I/O 回调、用户事件等。每轮 event loop 只取队列里**一个**宏任务执行，执行完后去清空微任务队列，再取下一个宏任务。

一个典型例子：

```js
console.log('1')

setTimeout(() => console.log('2'), 0)

Promise.resolve().then(() => console.log('3'))

console.log('4')
```

输出顺序是 1 → 4 → 3 → 2。同步的 1、4 先跑；`setTimeout` 回调进宏任务队列；`Promise.then` 进微任务队列；调用栈清空后先跑微任务得到 3；再取宏任务得到 2。

`setTimeout(fn, 0)` 之所以不是"立刻执行"，原因就在这里——它只是把 fn 放进宏任务队列，得等当前同步代码和所有微任务都跑完才轮到它。
