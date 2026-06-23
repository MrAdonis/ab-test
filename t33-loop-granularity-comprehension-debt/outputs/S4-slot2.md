## Workflow 设计

### 阶段划分

**Phase 0：扫描 + 分组（一次性，主代理）**

```bash
# 找出 40 个无测试文件，写入任务清单
python3 scripts/find_untested.py > task_list.json
```

`task_list.json` 格式：每条记录含 `file`（源文件路径）、`status`（pending/done/failed）、`test_file`（预期生成路径）。

**Phase 1：批量补写（40 个子代理并行，每个处理 1 文件）**

每个子代理拿到单条记录，执行：
1. 读源文件，识别导出函数/类
2. 写对应测试文件
3. 跑 `npm test -- <test_file>` 或等效命令，取退出码

子代理把结果回写 `task_list.json`：`status` 改为 `done` 或 `failed`，记录退出码和摘要。子代理不判定自己"成功"——只记录事实。

**Phase 2：独立验收（checker，和写测试的子代理完全独立）**

主代理或专属 checker 脚本逐条验证：

```bash
python3 scripts/verify_tests.py --task-list task_list.json
```

checker 做的事：
- 逐一跑测试，不信子代理自报的退出码
- 统计：源文件行数 → 测试文件行数（测试覆盖率基线）
- 核查测试文件是否有 `skip` / `xit` / `test.todo`（古德哈特防御：通过是因为跳过，不算完成）

---

### 验收要求（可执行命令版）

完成定义是同时满足以下全部条件，缺一不算：

```
✅ 40 个文件全部有对应测试文件（find . -name "*.test.*" | wc -l ≥ 40）
✅ npm test 零失败（exit 0，非靠 --passWithNoTests）
✅ 测试文件无任何 skip/xit/xtest/test.todo（grep -rn "\.skip\|xit\|xtest\|test\.todo" __tests__/ → 零命中）
✅ 测试行数 ≥ 原有总行数的 20%（按 task_list.json 中 min_test_lines 字段验证）
✅ tsc --noEmit 零报错（TypeScript 项目）
✅ 源文件未被修改（git diff --name-only 中不含被测源文件）
```

最后一条是边界条件：agent 不能通过改源代码让测试通过。

---

### 古德哈特防御清单

写进任务描述（每个子代理的 prompt 开头）：

> 禁止：删除测试、注释测试、添加 skip/xit、修改被测源文件、硬编码 mock 使测试永远为真、降低 TypeScript strict 级别。
>
> 如果某函数逻辑复杂无法测试，在测试文件中写明 `// UNTESTABLE: <原因>` 并报告，不要跳过。

---

### 每轮自查（无人值守）

每个子代理启动时先跑：

```bash
cat task_list.json | jq '.[] | select(.status=="pending") | .file'
```

只处理 `pending` 条目，避免重复覆写已完成的测试文件。全部 `done` 后才输出 promise，不提前声明完成。
