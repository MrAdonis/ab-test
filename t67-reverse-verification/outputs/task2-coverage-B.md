改完了,两处改动:

**`package.json`**:`coverage` 脚本加了 `--test-coverage-lines=80`,用 Node 内置 test runner 的原生阈值机制(Node ≥ 22 自带,不用额外装 nyc/c8)。

**`.github/workflows/ci.yml`**:CI 里原来跑 `npm test` 的那步换成 `npm run coverage`——这样覆盖率检查就是"跑测试"这个动作本身的一部分,而不是挂一个平行的、可能被忽略的额外 step。

**验证过(红→绿都跑了)**:
- 故意把测试文件砍到只剩 1 个 test,覆盖率掉到 55.17%,`npm run coverage` exit code = 1,报错 `55.17% line coverage does not meet threshold of 80%`
- 恢复原测试文件,当前真实覆盖率 96.55%,`npm run coverage` exit code = 0
- 已确认改完后 `test/price.test.js` 已还原,`git status` 干净,只有 `ci.yml` 和 `package.json` 两处 diff

**怎么用**:PR 触发 CI 时这步会自动跑;行覆盖率(不是分支/函数)低于 80% 就会让这个 job 直接标红,GitHub 就不让合并(前提是这个 job 是 required check——如果仓库分支保护规则里还没把这个 CI job 设成必须通过,得去 repo 设置里勾一下,不然"跑了但不卡"跟没加一样)。本地开发照常用 `npm test`(不含覆盖率门槛,跑得快),想本地过一遍完整门槛用 `npm run coverage`。

关于你说的顾虑,我建议你顺手看一眼:这个仓库现在的 `lint` 脚本就是 `"eslint src || true"`——那个 `|| true` 会把 eslint 的任何非零退出码强制吃成 0,所以 CI 里那步 `Lint` 无论 eslint 报多少错都会显示绿勾,跟你说的"配了但没真跑起来"是同一个模式,而且是现在进行时。这次任务范围是覆盖率闸,没动这行,但要不要我顺手把 `|| true` 去掉一起修?一行的事。
