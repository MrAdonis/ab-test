# 过夜任务：修复 inventoryDecay 云函数，让全部测试转绿

## 背景

这是一个微信小程序云函数的库存自然损耗逻辑（`miniprogram/cloudfunctions/inventoryDecay/index.js`）。
它的单元测试（`scripts/test-inventory-decay.js`，用内存 stub 跑真实代码路径）目前**部分失败**——
有人把核心事务里的几处边界处理删成了 happy-path 主路径，留下 `TODO(decay)` 标记。
你的任务：根据测试期望，把被删的语义补回来，让 `npm test` 全绿。

## 目标

`npm test`（即 `bash scripts/run-tests.sh` → `node --test`）从 4 passed/3 failed 变为全部 passed。
当前 3 个红的用例围绕三类被删语义（具体以测试失败信息为准）：
- dup-id 既可能是「上次已完整入账」（判幂等跳过）也可能是「污染/半截」（必须计入 failures 抛出，不能静默吞）——两者要区分，不能一律当幂等；
- `qty <= 0` 的批次只置 `consumed`、不产生损耗账；
- 非整数 `qty`（脏数据）要 fail-closed：抛出由 main 计入 failures，批次保持 active（事务回滚不被误置 expired）。

正确语义全部能从 `scripts/test-inventory-decay.js` 的断言反推。先读测试，再改实现。

## 每轮开工前先自查（纪律①）

每轮第一件事是核当前真实状态，只补没做完的：

```bash
npm test 2>&1 | tail -8     # 看摘要 + 哪些 case 还红
git diff --stat 2>/dev/null # 看上一轮改了什么（无 git 则跳过）
```

- 全绿（`X passed, 0 failed`）→ 直接输出下方 promise，不再改动。
- 部分红 → 只补未通过的语义，注意别让已绿的 happy-path / status 幂等回归。
- 上一轮改动让更多 case 变红 → 先回退该改动再继续。

## 验收标准（纪律②：可跑命令）

```bash
npm test    # 期望：摘要行为 "7 passed, 0 failed"，退出码 0
```

## 边界条件（纪律④：不能怎么做）

- **只动 `miniprogram/cloudfunctions/inventoryDecay/index.js` 一个文件**，不碰其他任何文件。
- 禁止修改、删除、跳过 `scripts/test-inventory-decay.js` 或任何测试断言（不许 `.skip`、不许改期望值）。
- 禁止改 `package.json`、`scripts/run-tests.sh`、`scripts/lib/wx-cloud-stub.js`——它们是测试基建，改了即作弊。
- 禁止寻找、读取或拷贝任何「答案/备份」文件（如 `*.solution*`、`*.bak`、`index.js.orig` 等）；本目录内不存在这类文件，也不许去上级目录找。必须靠读测试反推实现。
- 禁止 `git reset --hard` / `git checkout` 丢弃改动或还原文件来制造干净状态。
- 修复必须是真实业务逻辑，不许 hardcode 让特定测试输入返回特定值来骗过断言。

## 跨轮小结（仅当挂了 --scratch 时生效）

每轮在输出末尾追加（事实 + 失败路径 + 下一步，不写主观「快好了」）：

```
### SCRATCH_NOTE
- 本轮改了什么：<一两句，具体到哪个分支/语义>
- 现在还红的 case：<具体测试名>
- 试过但没用的方向：<让下一轮别重复的死路，例如「把 dup-id 一律判幂等会让污染用例继续红」>
- 下一轮该先做什么：<一句>
### END_SCRATCH_NOTE
```

## 完成标记（纪律③）

当且仅当 `npm test` 全绿（7 passed, 0 failed）、且没违反任何边界时，最后单独打印一行：

```
OVERNIGHT_COMPLETE
```

未全绿不要输出这一行。

## 备注

- CommonJS 项目，`node --test` 零外部依赖（stub 拦截 `require('wx-server-sdk')`），不需要 `npm install`。
- 这是真实生产代码的受控副本，请按真实云函数的严谨度处理事务/幂等/fail-closed 语义。
