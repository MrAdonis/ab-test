---
name: project-package-manager
description: fleetview 包管理器选择
confidence: medium
---

fleetview 包管理统一用 pnpm，不用 npm。

**Why:** 混用 npm 会导致 lockfile 冲突，已踩过坑。
**How to apply:** 装依赖、跑脚本一律用 `pnpm install` / `pnpm run`，不要用 `npm install`；发现 `package-lock.json` 应删除，只保留 `pnpm-lock.yaml`。
