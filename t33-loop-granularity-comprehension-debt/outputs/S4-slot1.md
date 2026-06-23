# S4 · B 臂回答

**用户问题：设计一个 workflow，让 agent 批量给我仓库里 40 个还没有测试的文件补单元测试。输出和验收要求应该是什么？**

---

## Workflow 设计

**单轮粒度：一轮只动一个文件。**

40 个文件分 40 轮，每轮 agent 拿到一个目标文件，读懂它，写对应的测试文件，提交，然后把结果写进 `progress.json`（`{file, status, test_path, lines_added}`）。不要一轮塞多个文件——动作幅度越大，验收盲区越大，编得过的语义错误对 loop 全部隐形。

**Checker 和 Maker 分离。**

执行测试的 agent 不能自己判断"我好了"。每轮结束后由独立 checker 脚本跑验收，不是让写测试的 agent 自我报告。

**每轮开始先自查状态。**

```bash
git status && pytest path/to/test_file.py -x 2>&1 | tail -20
```

已经有测试且通过的跳过，不重复写。

---

## 输出要求

每轮产出两样东西：

1. **测试文件本身**（`tests/test_<source_file>.py` 或项目约定路径）
2. **一条 progress.json 记录**：
   ```json
   {
     "file": "src/utils/parser.py",
     "test_path": "tests/test_parser.py",
     "status": "done",
     "lines_added": 87,
     "cases": ["test_parse_empty", "test_parse_malformed", "test_parse_normal"],
     "verdict_cmd": "pytest tests/test_parser.py -v --tb=short",
     "verdict_exit": 0
   }
   ```
   `verdict_cmd` 和 `verdict_exit` 是审判依据，不是自我声明——任何人拿这条记录都能重新跑一遍验证。

---

## 验收要求

验收条件必须同时带边界，防止 agent 针对验证器优化：

### 整体完成定义

```
pytest tests/ --tb=short 全部通过
  AND 测试文件数量 == 40（不能少）
  AND 每个测试文件行数 >= 20（不能是空壳）
  AND 禁止删除或跳过（skip/xfail）任何既有测试
  AND tsc --noEmit 零报错（如果是 TS 项目）
```

用命令验证，不是"感觉做完了"：

```bash
# 测试全过
pytest tests/ -q

# 测试文件数量
find tests/ -name "test_*.py" | wc -l

# 没有空壳（每个文件至少 20 行）
for f in tests/test_*.py; do wc -l < "$f"; done | awk '$1 < 20 {exit 1}'

# 没有被跳过的用例
pytest tests/ -v 2>&1 | grep -c "SKIPPED" | awk '$1 > 0 {exit 1}'
```

### 单轮验收（checker 脚本，每轮结束自动跑）

```bash
pytest "$TEST_PATH" -v --tb=short
# exit 0 = 完成，继续下一轮
# exit 1 = 测试失败，当前轮标 failed，不继续
```

三态分流：exit 0 继续，exit 1 标记失败文件等人工介入，import error / 语法错误视为 bug 停轮报警。

### 可复盘要求

loop 结束后必须能回答：

- 哪个文件的测试是什么时候写的、跑过几个 case、当时 exit code 是多少
- 如果某个测试文件现在失败了，能追溯到是哪轮写的、写时依据什么

`progress.json` 里的 `verdict_cmd` 就是这个"审判依据"。没有这个字段的记录不算完成，只算跑过。

---

## 防御边界（写进 loop 任务文件）

- 禁止删除 `tests/` 下已有文件
- 禁止用 `@pytest.mark.skip` 或 `unittest.skip` 绕过
- 禁止写 `assert True` 或只有 `pass` 的测试函数
- 测试必须真实调用被测函数，不是 mock 掉所有逻辑后断言 mock 被调用了
