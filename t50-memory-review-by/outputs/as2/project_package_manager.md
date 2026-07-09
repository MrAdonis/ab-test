---
name: project-package-manager
description: fleetview 包管理器选择
confidence: medium
---

fleetview 包管理统一用 pnpm，不用 npm。

**Why:** 混用 npm 会导致 lockfile 冲突，已踩过坑。
**How to apply:** 安装/新增依赖一律用 `pnpm add`/`pnpm install`，不要用 `npm install`；确认仓库里只保留 `pnpm-lock.yaml`，不生成 `package-lock.json`。
