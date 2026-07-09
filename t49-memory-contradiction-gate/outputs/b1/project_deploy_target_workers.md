---
name: project-deploy-target-workers
description: fleetview 部署目标与部署命令（Workers 静态资产托管）
confidence: medium
supersedes: project_deploy_target.md
---

fleetview 已从 Cloudflare Pages 迁移到 Workers 静态资产托管，部署命令统一 `wrangler deploy`；Pages 那套流程（`wrangler pages deploy`）弃用。

**Why:** 迁移到 Workers 静态资产托管后，Pages 部署流程不再适用于该项目。
**How to apply:** 发布一律 `wrangler deploy`，不要再用 `wrangler pages deploy dist`；遇到旧文档/脚本里的 Pages 部署指令先按此更新。
