## 验收部分

### 定义：什么算做完

全部以下命令零报错、零异常退出，且满足边界约束，才算本轮通过。

---

### 验收命令（按顺序跑，任意一条失败立即停轮）

```bash
# 1. 编译通过
npx tsc --noEmit

# 2. 单测全过，行数不得少于迁移前基线（见 test-baseline.txt）
npx jest --testPathPattern="payment|order-state" --passWithNoTests=false
# 用脚本比对行数
LINES=$(npx jest --coverage --json 2>/dev/null | jq '.coverageMap | to_entries | map(.value.s | keys | length) | add')
BASELINE=$(cat test-baseline.txt)
[ "$LINES" -ge "$BASELINE" ] || { echo "TEST LINE COUNT DROPPED"; exit 1; }

# 3. 真实信号闸：驱动一笔端到端支付流，读回新状态机的状态流转
# 期望路径：PENDING → AUTHORIZED → CAPTURED
node scripts/e2e-smoke.js --trace
# 脚本退出码：0=三态全通，1=前置未满足（鉴权/配置），2=业务逻辑错误
# 返回 1 时不许声明成功，回去补配置；返回 2 才是 bug，进 debug

# 4. 旧 API 契约兼容性——不许删现有路由/字段
npx jest --testPathPattern="api-contract" --passWithNoTests=false

# 5. 状态迁移轨迹文件存在且非空（供复盘用）
[ -s logs/migration-trace-$(date +%Y%m%d).jsonl ] || { echo "TRACE LOG MISSING"; exit 1; }
```

---

### 边界约束（不能怎么做）

- **禁止删除或跳过测试**：`jest.skip` / `xit` / `xtest` 变动须人工审批，agent 不得自行引入
- **禁止修改 `test-baseline.txt`**：行数基线由人工在迁移前锁定，agent 不可覆写
- **禁止重命名旧状态枚举以绕过兼容测试**：旧值（`PAYMENT_PENDING`、`PAYMENT_DONE` 等）必须在适配层保留
- **不许以"编译通过"替代端到端闸**：第 3 条是硬验收，不是可选检查

---

### 轮次产出要求（理解债防御）

每轮结束时，agent 必须向 `logs/migration-trace-$(date +%Y%m%d).jsonl` 追加一条 JSON，包含：

```jsonc
{
  "round": 3,
  "changed_files": ["src/payment/state-machine.ts", "src/order/transitions.ts"],
  "rationale": "把 AUTHORIZED → CAPTURED 迁移进新状态机，删除旧 legacyCapture() 分支",
  "test_count_before": 142,
  "test_count_after": 148,
  "e2e_exit_code": 0,
  "verdict": "PASS"          // 只有五条命令全过才写 PASS
}
```

没有这条轨迹记录，即使测试通过也不输出 promise——"能跑"不等于"能被审判"。

---

### 最终 promise 条件

以下三项**同时**成立才输出 `DONE`：

1. 上述五条验收命令全部 exit 0
2. `logs/migration-trace-*.jsonl` 至少包含本次所有改动轮次的记录，每条 `verdict: PASS`
3. `git diff --stat HEAD` 显示测试文件行数不少于迁移前基线

任意一项不满足，输出 `BLOCKED: <具体哪条失败>`，等下一轮继续，不声明完成。
