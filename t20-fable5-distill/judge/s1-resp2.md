JS event loop 执行顺序：

1. **同步任务**：当前调用栈清空。`console.log`、赋值、函数调用全在这里，先跑完。

2. **微任务（Microtask Queue）**：调用栈清空后立刻处理，全部清空才进下一步。包括：
   - `Promise.then / catch / finally`
   - `queueMicrotask()`
   - `MutationObserver`

3. **宏任务（Macrotask / Task Queue）**：每次只取一个执行，执行完再清空微任务队列，再取下一个。包括：
   - `setTimeout / setInterval`
   - `MessageChannel`
   - I/O 回调
   - `requestAnimationFrame`（浏览器）

一轮循环流程：
```
执行同步代码 → 清空微任务队列 → 执行一个宏任务 → 清空微任务队列 → 执行一个宏任务 → ...
```

经典例题验证：
```js
console.log('1');         // 同步

setTimeout(() => {
  console.log('2');       // 宏任务
}, 0);

Promise.resolve().then(() => {
  console.log('3');       // 微任务
});

console.log('4');         // 同步
```
输出：`1 → 4 → 3 → 2`

关键点：`setTimeout(fn, 0)` 不是"立刻跑"，而是下一个宏任务——必然在所有微任务之后。
