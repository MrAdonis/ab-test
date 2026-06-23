# 过夜任务：实现 src/calc.js 的算术表达式求值器，跑通全部测试

## 目标

让 `src/calc.js` 的 `evaluate(expr)` 通过 `tests/calc.test.js` 的全部 12 个用例：
四则运算 + 优先级 + 嵌套括号 + 一元负号 + 小数 + 忽略空白 + 除零抛 `Error("division by zero")`。
完成后 `npm test` 全绿。

## 每轮开工前先自查（纪律①）

每轮第一件事是核当前真实状态，只补没做完的：

```bash
npm test 2>&1 | tail -20    # 看哪些 case 还红
git diff --stat             # 看上一轮改了什么
```

- 全绿 → 直接输出下方 promise，不再改动。
- 部分红 → 只修未通过的 case，注意别让已绿的回归。
- 上一轮改动让更多 case 变红 → 先回退该改动再继续。

## 验收标准（纪律②：可跑命令）

```bash
npm test            # 期望：12 passed, 0 failed，退出码 0
```

- `npm test` → 退出码 0 且 "12 passed"。

## 边界条件（纪律④）

- 禁止修改、删除、跳过 `tests/` 下任何文件，禁止 `.skip`/`.only`/改断言。
- 禁止改 `package.json` 的 test 脚本或加 `--no-verify` 类跳过。
- 禁止 `git reset --hard` / 丢弃改动来制造干净状态。
- 只动 `src/calc.js`，不碰其他文件。

## 跨轮小结（仅当挂了 --scratch 时生效）

每轮在输出末尾追加：

```
### SCRATCH_NOTE
- 本轮改了什么：<一两句>
- 现在还红的 case：<具体测试名>
- 试过但没用的方向：<让下一轮别重复的死路>
- 下一轮该先做什么：<一句>
### END_SCRATCH_NOTE
```

只写事实 + 失败路径 + 下一步，不写主观「快好了」。

## 完成标记（纪律③）

当且仅当 `npm test` 12 个全过、且没违反任何边界时，最后单独打印一行：

```
OVERNIGHT_COMPLETE
```

未全过不要输出这一行。

## 备注

- 这是一个 vitest + ESM 项目（`"type": "module"`），`npm test` 即 `vitest run`。
- node_modules 已由 run-ab.sh 预装好，不要重新 npm install。
