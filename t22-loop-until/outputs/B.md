## S1

**修 CI 到绿**

五字段：

- **Goal**：PR 上所有 CI checks 的 conclusion = success，`gh pr checks` 输出里无 fail/pending 行。
- **Check 命令**：`gh pr checks <PR_NUMBER> --watch=false` 并检查是否有 `fail` 字样；配合 `gh run view <run_id> --log-failed` 拿具体失败日志。
- **Exit when**：`gh pr checks` 输出中所有行 conclusion 均为 `pass`（exit 0，且 grep fail 无命中）。
- **Max iterations**：8。
- **边界**：禁止跳过或注释掉任何 CI step；禁止修改 workflow yml 把失败 step 标 `continue-on-error: true` 或直接删除；禁止在 check 命令里过滤掉失败输出来凑绿——必须真修到 job pass。

循环跑法：第 1 轮先跑 `gh pr checks` 拿当前红色 job 列表，再用 `gh run view --log-failed` 定位根因（编译错/测试失败/lint/type check）。每轮针对一类错误做修改，commit push，等 CI 触发，跑 check 命令读结果。若同一错误连续两轮没收敛，切换假设（参 coding.md 假设驱动调试）。

收口：resolved——check 命令 grep 无 fail，截 `gh pr checks` 输出作证据。若最终绕了根因（如临时降级某个依赖），resolved with caveats，写明绕过了什么、后续要补。到 Max 还红：blocked，列清每类 check 的失败原因和已试方案，告诉用户下一步需要什么（权限/密钥/外部服务状态）。

---

## S2

**重构后验证**

五字段：

- **Goal**：auth 模块相关的构建、lint、类型检查、单测全部通过；手动冒烟验证登录/登出/鉴权拒绝三条路径行为与重构前一致。
- **Check 命令**：`npm run build && npm run lint && npx tsc --noEmit && npm test -- --testPathPattern=auth`（或对应项目命令）；冒烟用 `curl -fsS <auth-endpoint>/health` 或 headless 集成脚本。
- **Exit when**：上述命令链 exit 0，且冒烟端点返回 200（或对应健康码）；测试行数不减少（`grep -c "test\|it(" tests/auth` 与重构前基线持平）。
- **Max iterations**：8。
- **边界**：禁止删除或跳过任何 auth 相关测试；禁止为让 tsc 过而添加 `@ts-ignore` 或 `any` 类型标注；禁止修改 check 命令的 `--testPathPattern` 缩小覆盖范围——必须真让重构后代码通过原有测试集。

循环跑法：第 1 轮跑完整 check 链，把失败分类（类型错 / import 路径变更 / 接口契约漂移 / 业务逻辑）。每轮修一类，优先修编译错（阻塞后续），再修类型，最后修测试。跑 check 命令确认当类消除后进下一类。冒烟留到单测全过后跑一次。

收口：resolved——check 命令链全 exit 0 + 冒烟 200 + 测试行数基线持平，附一轮完整 check 输出截取作证据。若某条冒烟路径因重构行为变更需要更新文档而非回滚，resolved with caveats，说明变更是有意为之。到 Max 未过：blocked，说明卡在哪个 check step、根因假设是什么、需要用户提供什么（原始接口文档/生产环境 token/外部依赖状态）。

---

## S3

**测试全过**

五字段：

- **Goal**：`npm test`（或对应命令）输出 0 failed，原有 3 个失败测试全部 pass，且总测试数不少于修复前。
- **Check 命令**：`npm test -- --verbose 2>&1 | tail -30`（看 fail/pass 汇总）；每轮聚焦失败测试：`npm test -- --testNamePattern="<failing test name>"`。
- **Exit when**：`npm test` exit 0，输出中 `0 failed`（grep 命中），且测试总数 ≥ 修复前基线数（防删测试凑绿）。
- **Max iterations**：8。
- **边界**：禁止删除任何失败测试；禁止用 `test.skip` / `xit` / `xdescribe` 跳过；禁止修改断言使其永真（如把 `expect(x).toBe(3)` 改成 `expect(x).toBeDefined()`）；禁止修改 check 命令的 `--testPathPattern` 排除失败测试——必须让原始断言在真实代码下通过。

循环跑法：第 1 轮跑完整测试套件，拿到 3 个失败测试的名称、断言内容、actual vs expected。对每个失败分析：是测试写错（期望值过时）还是实现有 bug——如果是前者，修测试要走正常 review；如果是后者，修实现。每轮处理一个失败测试，修完跑单测确认 pass 后才进下一个（单变量原则，避免改动互相干扰）。第 3 轮后跑完整套件确认无回归。

收口：resolved——`npm test` exit 0，`0 failed`，测试总数与修复前一致，附最后一轮完整输出最后 20 行作证据。若某个测试断言本身写错（测试期望值过时）而非代码 bug，属 resolved with caveats，写明修改了哪条断言、原因，供 code review 确认。到 Max 未过：blocked，列出每个仍失败的测试名称、已试假设、卡点（依赖外部服务/环境变量缺失/flaky race condition），告诉用户需要什么才能继续。
