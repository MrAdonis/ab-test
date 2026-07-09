---
name: project-package-manager
description: fleetview 包管理器选择
confidence: medium
---

fleetview 包管理统一用 pnpm，不用 npm。

**Why:** npm 和 pnpm 混用会导致 lockfile 冲突，已踩坑。
**How to apply:** 安装依赖、跑脚本一律用 `pnpm install` / `pnpm run`，不生成 `package-lock.json`。
