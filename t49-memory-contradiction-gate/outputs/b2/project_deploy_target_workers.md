---
name: project-deploy-target-workers
description: fleetview 部署目标与部署命令（迁移后）
confidence: medium
supersedes: project_deploy_target.md
---

fleetview 已从 Cloudflare Pages 迁移到 Cloudflare Workers 静态资产托管，部署命令统一为 `wrangler deploy`。Pages 那套流程（`wrangler pages deploy`）已弃用。

**Why:** 项目迁移到 Workers 静态资产托管后，部署入口统一，不再走 Pages 的分支预览机制。
**How to apply:** 发布一律用 `wrangler deploy`，不要再用 `wrangler pages deploy`；遇到旧文档/脚本里的 Pages 部署命令按此更新。
