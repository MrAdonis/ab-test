# 任务:把项目里挂掉的测试修绿(无人值守循环版)

## 0. 你的运行方式(必读)

你是被一个 shell 循环反复拉起的**全新进程**——每一轮都不记得上一轮做了什么。你和"上一轮的你"之间唯一的沟通渠道是磁盘上的文件(`.loop/` 目录 + git 历史)。所以本任务的第一步永远是**读状态、跑命令拿到真实现状**,禁止凭"应该已经修好了"这种记忆/直觉去下结论——你没有记忆,只有仓库当前的真实状态。

每一轮结束前,必须做完"收尾三件套"(见第 4 节),否则下一轮的你(以及外层循环)将无法判断当前处于什么状态。

## 1. 完成标准(唯一权威判定,逐条机器可验证)

**只有以下 6 条同时成立,才算 DONE。缺一不可,不接受"大体上过了"。**

1. `npm run typecheck` 退出码为 0。
2. `npm test`(非 watch、一次性退出模式)退出码为 0。
3. 测试用例总数 **不小于** `.loop/baseline.json` 里记录的初始总数。
   - 依据(古德哈特定律边界条件):"测试全过"是残缺的目标定义——删掉失败的测试、比"真的把 bug 修好"更省事,且能让第 1、2 条同时满足。**这是要严防的头号作弊路径。**
4. 相对 baseline,`.skip` / `.todo` / `xit` / `xdescribe` / `it.skip` / `describe.skip` / `test.skip` 之类的跳过标记**数量没有增加**(用 grep 统计前后对比,记录在 progress log 里)。
5. vitest 配置(`vitest.config.*` / `vite.config.*` 里的 test 字段)的 `include`/`exclude`/`testPathIgnorePatterns` 相对 baseline **没有被扩大**去把失败测试文件排除在外。
6. 相对 baseline,`@ts-ignore` / `@ts-expect-error` / `as any` 的出现次数,以及 `tsconfig.json` 里任何 strict 相关选项(`strict`、`noImplicitAny`、`strictNullChecks` 等)**没有被新增/放宽**用来掩盖 typecheck 报错。

**允许的修改范围:**
- 优先改源码,修真正的 bug / 根因。
- 只有在**确认是测试本身写错**(断言与需求明显矛盾、测试在验证一个已经不存在的旧行为等)时,才可以改测试文件本身——且必须在 commit message 和 `.loop/progress.md` 里写清楚:测试错在哪、正确的预期应该是什么、依据是什么(需求文档/类型定义/相邻测试的一致行为等)。
  - 如果你不确定实现和测试哪个才是"对的",**不要猜、不要改测试去迁就一个可能有 bug 的实现**——按第 3 节判 `BLOCKED`,交给人判断。
- 严禁为了通过检查而做的操作:`git commit --no-verify`、`git push --force`、临时关掉某个 lint/hook、删除/注释掉失败用例、把断言从精确匹配改成宽松匹配(如 `toEqual` 改 `toBeDefined`)来迁就当前实现。
- 不要顺手改动本任务无关的代码(不相关的"优化"、格式化整个文件等)。

## 2. 每轮启动协议

1. 检查 `.loop/` 目录是否存在。
   - **不存在**(说明这是第 1 轮):创建它,写 `.loop/baseline.json`,记录:
     - 当前 `npm test` 输出的总用例数、通过数、失败数
     - 当前 `npm run typecheck` 的报错数
     - 当前 `.skip`/`.todo` 等跳过标记的 grep 计数
     - 当前 `@ts-ignore`/`@ts-expect-error`/`as any` 的 grep 计数
     - 当前 `git rev-parse HEAD`
     - 时间戳
     - 同时创建空的 `.loop/progress.md`(表头即可)和 `.loop/round`(内容 `0`)
   - **已存在**:读 `.loop/baseline.json` 和 `.loop/progress.md` 的**最近 5 轮记录**(不必全读),了解目前卡在哪些测试上、上一轮做过什么尝试、避免重复无效动作。
2. 跑 `npm run typecheck`,记录退出码和报错数。
3. 跑 `npm test`(确保是一次性退出模式,不是 watch),记录退出码、总数/通过/失败,以及**具体哪些测试用例名字失败**(不只是数量——数量相同不代表是同一批测试)。
4. 对照第 1 节的 6 条标准,判定本轮状态属于 `DONE` / `BLOCKED` / `CONTINUE` 三者之一(判定逻辑见第 3 节)。

## 3. 状态判定与止损

### DONE
第 1 节 6 条全部满足 → 判 `DONE`。不再做任何修改,直接进入第 4 节收尾,`.loop/STATUS` 写 `DONE`。

### BLOCKED(需要人介入,不要再自己猜)
满足以下任一 → 判 `BLOCKED`:
- **卡住**:连续 3 轮,失败测试的**具体名单**(不是数量)完全没有变化——说明当前思路无效,继续跑只是浪费时间。
- **需要人类决策**:某个失败的根因是"测试期望 vs 实现,不确定哪个对"、需要外部凭证/密钥/网络访问、需要产品侧决策(比如某个功能该保留旧行为还是新行为)。
- **触碰了危险操作边界**:修复必须删除/大幅改写某个测试才能通过,但你无法 100%确认这是"测试写错"而不是"功能被测试正确地捕获了一个真实回归"。
- 达到本文件约定的**轮次上限 30**(与外层循环脚本的上限保持一致;如两边数字不一致,以更小值为准,并在 progress.md 里提醒人类核对)。

判 `BLOCKED` 时:在 `.loop/NEEDS_HUMAN.md` 写清楚——卡在哪个/哪些测试、已经尝试过什么、为什么无法再继续、你的怀疑和证据。然后进入收尾,`.loop/STATUS` 写 `BLOCKED`,**这一轮到此为止,不要再动代码**。

### CONTINUE
都不满足 → 正常修复:挑失败列表里 1~3 个相关的问题动手改源码,改完重新跑一遍 typecheck + test 确认没有引入新的失败,然后进入收尾,`.loop/STATUS` 写 `CONTINUE`。

## 4. 每轮收尾(不管 DONE / BLOCKED / CONTINUE 都必须做)

1. **更新日志**:在 `.loop/progress.md` 追加一条记录(不要覆盖历史),至少包含:
   - 轮次号(读 `.loop/round`,+1 后写回)、时间戳
   - typecheck 结果(退出码/报错数)、test 结果(通过/失败/总数)
   - 本轮做了什么改动、为什么这么改
   - 第 1 节 6 条标准逐条打勾/打叉
   - 最终判定:DONE / BLOCKED / CONTINUE
2. **提交改动**:`git add` 本轮涉及的文件 + `.loop/` 状态文件,`git commit`,message 里带轮次号(如 `round 7: fix xxx`)。不使用 `--no-verify`,不强推。
3. **写状态文件** `.loop/STATUS`,内容为**且仅为**以下三者之一:`DONE` / `BLOCKED` / `CONTINUE`。这是外层 shell 循环判断"要不要再拉起下一轮"的唯一依据。

## 5. 给外层循环脚本的约定(供参考,不是本文件要执行的内容)

外层脚本每轮跑完 `claude -p` 后,应该读 `.loop/STATUS`:
- `CONTINUE` → 继续下一轮
- `DONE` 或 `BLOCKED` → 停止循环,`BLOCKED` 时早上优先看 `.loop/NEEDS_HUMAN.md`

示例:
```bash
while true; do
  claude -p "$(cat unattended-fix-tests-task.md)"
  status=$(cat .loop/STATUS 2>/dev/null)
  [ "$status" = "CONTINUE" ] || break
done
```
