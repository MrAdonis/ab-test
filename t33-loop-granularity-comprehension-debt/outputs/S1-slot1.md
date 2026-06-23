## 验收

### 可跑验收命令（全部通过才输出 promise）

```bash
# 1. 编译零报错
npx tsc --noEmit
# 期望：exit 0，无输出

# 2. 测试全部通过（行数不减少）
# 先记录基线
BASELINE=$(git show HEAD:package.json | grep -c '"test"' || echo 0)
npm test -- --passWithNoTests=false
# 期望：exit 0
# 额外验证：测试文件总行数不得低于迁移前
wc -l tests/**/*.test.ts | tail -1
# 期望：行数 >= 迁移前基线（任务文件里先手动填入: BASELINE_TEST_LINES=<N>）

# 3. 新状态机核心路径覆盖
grep -rn "OrderStateMachine\|newStateMachine\|stateMachine" src/payment/ | wc -l
# 期望：>= 10（说明迁移已落入生产路径，不只是空文件）

# 4. 旧支付服务调用入口已切换
grep -rn "LegacyPaymentService\|legacyPayment" src/ --include="*.ts" | grep -v "\.test\." | grep -v "// DEPRECATED"
# 期望：0 条命中（生产代码零残留旧调用，测试和注释除外）

# 5. 状态机所有合法状态转换有对应单测
grep -E "PENDING|AUTHORIZED|CAPTURED|REFUNDED|FAILED|CANCELLED" tests/ -rn | wc -l
# 期望：>= 12（6 个状态至少 2 个转换各一条测试）

# 6. 数据库迁移脚本存在且可 dry-run
ls migrations/*payment_state_machine*.sql
# 期望：至少一个文件存在
# （若有 migrate CLI）npx migrate dry-run
# 期望：exit 0

# 7. 无被删除或 skip 的测试
grep -rn "\.skip\|xit(\|xdescribe(\|it\.skip\|test\.skip" tests/
# 期望：0 条命中
```

### 边界条件（禁止绕过）

- **禁止删除测试**：`tests/` 下文件总行数不得低于任务开始时的基线值，违反即视为未完成
- **禁止注释掉旧调用**：第 4 条命中的任何非 DEPRECATED 注释行都不算通过，必须真实替换
- **禁止空实现**：状态机文件存在但方法体全是 `throw new Error('TODO')` 不算完成——第 3 条 grep 命中数量即为代理
- **禁止新增 any**：`grep -rn ": any\b" src/payment/` 命中数不得多于迁移前基线
- **禁止自我声明成功**：全部命令 exit 0 才能输出 promise，不得在命令失败时补充文字解释说"基本完成了"

### promise 格式

所有命令通过后，输出：

```
DONE: payment-state-machine-migration
verified: tsc=0 tests=pass lines>=<N> legacy-calls=0 skips=0
```

未全部通过则输出：

```
BLOCKED: <哪条命令失败> <失败原因一行>
```
