# 过夜任务：strict 模式迁移——让构建、类型检查、测试全部通过

> 你是无人值守环境里的全新进程，本文件是唯一任务说明，自包含。

## 目标

本项目刚把 tsconfig 升级到 `strict: true` + `noUncheckedIndexedAccess`（业务要求，配置已锁定），`src/` 下现存若干类型报错。目标状态：`npm run build` 零报错、`npm test` 全部通过，代码处于可交付状态。

## 每轮开工前先自查（纪律①）

```bash
npx tsc --noEmit
npm test 2>&1 | tail -5
git status --short
```

- 自查显示「已全部达标」→ 直接输出下方 promise，不要再改任何东西。
- 自查显示「部分完成」→ 只推进未完成项。

## 验收标准（纪律②：必须是可跑命令，不是主观判断）

```bash
npm run build
npm test
```

- `npm run build` → exit 0，无任何 tsc 报错
- `npm test` → 全部 pass，0 fail

## 边界条件（纪律④：写死「不能怎么做」）

- 禁止删除、跳过、注释掉任何测试；测试数量只能增不能减
- 禁止改验收命令本身、放宽阈值、跳过 git hooks
- 禁止 `git reset --hard` / 丢弃未提交改动来「制造干净状态」
- 禁止修改与本任务无关的文件
- 禁止修改 `tsconfig.json`（strict 配置是本任务的前提，不是可调参数）

## 完成标记（纪律③：全部验收 + 边界都满足，才输出）

当且仅当上面所有验收命令通过、且没有违反任何边界时，在输出最后单独打印一行：

```
OVERNIGHT_COMPLETE
```

未全部通过时不要输出这一行。
