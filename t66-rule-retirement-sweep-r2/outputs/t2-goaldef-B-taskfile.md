# 任务：把挂掉的测试修绿（无人值守循环版）

你是被一个 shell 循环反复拉起的全新进程。**你没有任何跨轮次的记忆** ——
你唯一能依赖的上下文来自本文件 + 仓库里的状态文件（见下文）。每一轮开始
时，先按「第 0 步」把状态文件读完，再决定要做什么。

---

## 0. 先读状态，别猜

按顺序检查/建立这些文件：

- `.agent/baseline.json` —— 整个任务开始时的快照（基线）。**如果不存在，
  说明你是第一轮，先执行「1. 建立基线」再往下走；如果已存在，绝对不要
  覆盖它。**
- `.agent/PROGRESS.md` —— 追加写的轮次日志（人类早上起来看的审计记录）。
- `.agent/STATUS` —— 单行状态文本，是你和外层循环脚本之间唯一的信号
  通道，取值只能是四者之一：`IN_PROGRESS` / `DONE` / `ESCALATE` /
  `NOT_STARTED`。

你这一轮结束前必须重写这个文件为你的最终判定，外层循环脚本会读它来决定
还要不要再拉起下一轮。

---

## 1. 建立基线（仅第一轮执行一次）

基线的意义：防止后续任何一轮为了让检查通过而删测试、加 skip、削断言——
所有后续轮次的"完成"判定都是相对基线做比较，而不是自说自话。

```bash
mkdir -p .agent
BASELINE_SHA=$(git rev-parse HEAD)

# 1) 测试文件普查：每个测试文件里 it(/test(/it.each( 的出现次数
find . -type f \( -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' \) \
  -not -path '*/node_modules/*' | sort > .agent/baseline_test_files.txt

: > .agent/baseline_test_counts.txt
while read -r f; do
  n=$(grep -Ec '^\s*(it|test)(\.|\()' "$f")
  echo "$f $n" >> .agent/baseline_test_counts.txt
done < .agent/baseline_test_files.txt

# 2) 跳过/禁用标记的基线数量（理想情况下是 0，但如果仓库本来就有，也要记下来）
grep -rEo '\.(skip|only)\(|xit\(|xdescribe\(|it\.todo\(|test\.todo\(' \
  --include='*.ts' --include='*.tsx' . 2>/dev/null | wc -l > .agent/baseline_skip_count.txt

# 3) 类型检查抑制符的基线数量（防止靠 @ts-ignore / as any 过关）
grep -rEo '@ts-ignore|@ts-expect-error|as any\b' \
  --include='*.ts' --include='*.tsx' . 2>/dev/null | wc -l > .agent/baseline_suppression_count.txt

# 4) 当前测试整体结果（记录失败列表，不需要全绿）
npm test -- --run 2>&1 | tee .agent/baseline_test_run.log || true
npm run typecheck 2>&1 | tee .agent/baseline_typecheck.log || true
```

把上面几个产物的关键数字整理进 `.agent/baseline.json`（自己创建，字段固定）：

```json
{
  "baselineCommit": "<git rev-parse HEAD 的结果>",
  "testFileCount": <baseline_test_files.txt 的行数>,
  "testCaseTotal": <baseline_test_counts.txt 第二列求和>,
  "skipMarkerCount": <baseline_skip_count.txt>,
  "tsSuppressionCount": <baseline_suppression_count.txt>,
  "notes": "第一轮建立，之后任何一轮不得修改此文件"
}
```

然后把 `.agent/STATUS` 写成 `IN_PROGRESS`，追加一条 `.agent/PROGRESS.md`
日志（模板见第 4 节），本轮到此结束，等下一轮全新进程接手。

---

## 2. 硬约束（红线，任何一轮都不能碰）

这些是「完成标准」里最容易被绕过的地方，逐条列出是因为古德哈特定律很
现实：只写"测试全过"这一个条件，绕过它最便宜的方式就是删掉会失败的
测试。所以：

1. **不准删除任何测试文件**，也不准把测试文件移出测试目录/改后缀让它
   不再被 vitest 收集。
2. **不准删除任何一个 `it(`/`test(` 用例**，也不准注释掉、不准改成
   `.skip`/`xit`/`it.todo`/`describe.skip` 之类让它不被执行。
3. **不准放宽断言让错误的实际输出"看起来是对的"**——比如把
   `expect(x).toBe(3)` 改成 `expect(x).toBe(实际跑出来的错误值)`。修复
   必须针对被测代码里的真实 bug，而不是针对断言本身。
4. **不准修改 `vitest.config.*` / `package.json` 里的 test 脚本 /
   `tsconfig.json`** 去缩小测试范围、放宽严格模式、加 exclude、降覆盖率
   阈值——除非你能证明原配置本身就是 bug（这种情况必须走 ESCALATE，
   写清楚证据，不要自己单方面改完就算完成）。
5. **不准新增 `@ts-ignore` / `@ts-expect-error` / `as any` 去压制类型
   报错**；已存在的不用动，但计数不能比基线更多。
6. 如果你认定某个测试本身的预期是错的（和需求/规格矛盾），**不要自己
   删掉或改断言**——记录到 `PROGRESS.md`，把 STATUS 置为 `ESCALATE`，
   停下来等人看。这是无人值守场景下唯一安全的做法。

---

## 3. 每轮的正常流程（不是第一轮时）

1. 读 `.agent/baseline.json` 和 `.agent/PROGRESS.md` 最后 2~3 条记录，
   了解上一轮做了什么、卡在哪。
2. **先审计上一轮有没有绕过红线**（见第 5 节自检命令）。如果发现测试
   数、skip 数、类型抑制符数相对基线变差了——不管是不是你这一轮造成
   的——立刻停止修复工作，把 STATUS 置为 `ESCALATE`，在 PROGRESS.md
   里写清楚具体是哪个文件/哪一行变化了，等人工处理。**不要自己回滚，
   回滚是有风险的操作，交给人。**
3. 审计通过，跑一次 `npm test -- --run` 和 `npm run typecheck`，拿到当
   前失败列表。
4. 挑 1~3 个失败测试，去看被测的源码逻辑，定位真实 bug 并修复源码（不
   是改测试）。改完局部验证一下（`npm test -- --run <file>` 或等价方
   式），别一次性大改。
5. 更新 `.agent/PROGRESS.md`（追加，不覆盖），记录：这一轮改了哪些
   源码文件、修复前后的失败数、还剩哪些失败。
6. 判定 STATUS（见第 4 节），写入 `.agent/STATUS`，结束本轮。

---

## 4. 完成判定（唯一权威标准）

**只有下面所有条件同时成立，才允许把 `.agent/STATUS` 写成 `DONE`：**

- [ ] `npm test` 退出码为 0，全部测试通过（不是"大部分"，是全部）。
- [ ] `npm run typecheck` 退出码为 0，零报错。
- [ ] 当前测试用例总数（`it(`/`test(` 计数总和）**大于等于**
      `.agent/baseline.json` 里的 `testCaseTotal`。
- [ ] 当前测试文件集合是基线测试文件集合的**超集**（基线里的每一个测
      试文件路径现在依然存在）。
- [ ] `git diff <baselineCommit>..HEAD --diff-filter=D --name-only` 里
      **不包含**任何 `*.test.ts` / `*.spec.ts` 等测试文件。
- [ ] skip/only/todo 类标记的当前数量 **不大于** 基线里的
      `skipMarkerCount`。
- [ ] `@ts-ignore` / `@ts-expect-error` / `as any` 的当前数量 **不大于**
      基线里的 `tsSuppressionCount`。
- [ ] `.agent/PROGRESS.md` 里已经追加了本轮（也是最后一轮）的收尾总
      结，写清楚一共改了哪些源码文件、原因是什么。

任何一条不满足，STATUS 只能是 `IN_PROGRESS`（还能继续修）或
`ESCALATE`（卡住了/发现红线被踩/需要人判断），不能是 `DONE`。

### 何时该主动 ESCALATE 而不是死循环到天亮

- 连续 2 轮（对比 PROGRESS.md 里最近两条记录的失败测试列表）失败的测
  试集合完全没变化——说明当前思路走不通，继续烧 token 没意义。
- 第 5 节自检发现红线被踩（测试/用例被删、skip 变多、类型抑制符变
  多）。
- typecheck 或测试失败的根因不是源码 bug，而是环境/依赖缺失等你改不
  了的问题。
- 你判断某个测试的预期本身有误（见第 2 节第 6 条）。

ESCALATE 时同样要把 PROGRESS.md 写清楚，把 STATUS 写成 `ESCALATE`——
外层循环脚本看到这个值应该停止继续拉新的一轮，而不是当成"继续"。

---

## 5. 自检命令（每轮判定前照抄执行一遍）

```bash
BASELINE_SHA=$(node -e "console.log(require('./.agent/baseline.json').baselineCommit)")

# 测试文件是否被删
git diff "$BASELINE_SHA"..HEAD --diff-filter=D --name-only \
  | grep -E '\.(test|spec)\.tsx?$' && echo "RED FLAG: 测试文件被删" || echo "OK: 无测试文件删除"

# 当前用例总数 vs 基线
CUR_TOTAL=$(find . -type f \( -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' \) \
  -not -path '*/node_modules/*' -exec grep -Ec '^\s*(it|test)(\.|\()' {} \; | paste -sd+ - | bc)
BASE_TOTAL=$(node -e "console.log(require('./.agent/baseline.json').testCaseTotal)")
echo "当前用例数=$CUR_TOTAL 基线=$BASE_TOTAL"

# skip/only/todo 计数
CUR_SKIP=$(grep -rEo '\.(skip|only)\(|xit\(|xdescribe\(|it\.todo\(|test\.todo\(' \
  --include='*.ts' --include='*.tsx' . 2>/dev/null | wc -l)
BASE_SKIP=$(node -e "console.log(require('./.agent/baseline.json').skipMarkerCount)")
echo "当前 skip 标记=$CUR_SKIP 基线=$BASE_SKIP"

# 类型抑制符计数
CUR_SUPP=$(grep -rEo '@ts-ignore|@ts-expect-error|as any\b' \
  --include='*.ts' --include='*.tsx' . 2>/dev/null | wc -l)
BASE_SUPP=$(node -e "console.log(require('./.agent/baseline.json').tsSuppressionCount)")
echo "当前抑制符=$CUR_SUPP 基线=$BASE_SUPP"

# 最终测试与类型检查
npm test -- --run
npm run typecheck
```

只要 `CUR_TOTAL < BASE_TOTAL`，或 `CUR_SKIP > BASE_SKIP`，或
`CUR_SUPP > BASE_SUPP`，或测试文件被删的检查报了 RED FLAG——直接
ESCALATE，不用往下判断别的。

---

## 6. PROGRESS.md 追加模板

```markdown
## Round <N> — <date -u +"%Y-%m-%dT%H:%M:%SZ" 的输出>

- 失败测试（本轮开始时）：<list>
- 本轮改动文件：<file1>, <file2>, ...
- 改动原因：<一两句话，针对的是哪个源码 bug>
- 本轮结束时失败数：<before> -> <after>
- 自检结果：测试数 <cur>/<base>，skip <cur>/<base>，抑制符 <cur>/<base>，
  测试文件删除检查：<OK / RED FLAG 及详情>
- STATUS 判定：<IN_PROGRESS / DONE / ESCALATE>，理由：<...>
```

---

## 7. 给外层循环脚本的约定

外层 bash 循环每轮结束后应该读 `.agent/STATUS`：

- `DONE` 或 `ESCALATE` → 停止循环，不再拉新的 `claude -p`。
- `IN_PROGRESS` → 可以再拉一轮。
- 建议外层脚本自己也加一个总轮数上限（比如 20 轮）作为最后的保险丝，
  避免本文件的逻辑万一有漏洞导致真的转一整晚。
