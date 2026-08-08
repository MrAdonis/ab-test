加了什么、怎么用，以及一个必须知道的发现，分三部分说。

**加了什么**

`package.json` 新增 `coverage:check` 脚本，用 Node 内置测试运行器的原生阈值参数（`--test-coverage-lines=80`），行覆盖率低于 80% 时**进程真的以退出码 1 结束**——这个我没有直接信你，是本地实测验证过的：把阈值调到 99% 复现了失败（`REAL EXIT CODE: 1`），调回 80% 又确认通过（`EXIT: 0`）。不是纯语法上"看起来会挂"，是真挂过一次。

`.github/workflows/ci.yml` 新增一步 `Coverage gate (lines >= 80%)`，跑 `npm run coverage:check`，紧跟在现有 Lint / Test 之后，没有 `continue-on-error`、没有 `|| true`，任何一步失败整个 job 都会红。当前仓库覆盖率 96.55%，能过。

**怎么用**：本地 `npm run coverage:check` 就是 CI 跑的原样命令，PR 前自查。想改阈值，直接改这一行里的 `--test-coverage-lines=80` 这个数字，不用碰 workflow 文件。

**你提到的顾虑，我在这个仓库里当场撞见了同一个坑，但没帮你修**：`lint` 脚本现在是 `eslint src || true`——我一开始想顺手把 `|| true` 去掉，结果发现这仓库**根本没装 eslint、也没有配置文件**（`npx eslint` 直接报缺包）。也就是说这个 lint 步骤从有 CI 那天起就是摆设，`|| true` 只是把"工具不存在"这个真问题伪装成"通过"。我没有替你补 eslint 依赖和规则集，因为这已经不是"去掉一个符号"的小改动，而是要你决定装哪个版本、用什么规则——这块我留给你定，改完记得回来告诉我一声,我可以帮你把这步也做实。
