---
name: project-deploy-target-workers
description: fleetview 部署目标与部署命令（迁移后）
confidence: medium
supersedes: project_deploy_target.md
---

fleetview 已从 Cloudflare Pages 迁移到 Cloudflare Workers 静态资产托管，部署命令统一用 `wrangler deploy`。Pages 那套流程（`wrangler pages deploy dist`）已弃用。

**Why:** 项目迁移到 Workers 静态资产托管后，Pages 部署链路不再适用。
**How to apply:** 发布一律 `wrangler deploy`，不要再用 `wrangler pages deploy`。
