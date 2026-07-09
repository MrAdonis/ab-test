---
name: project-deploy-target-workers
description: fleetview 部署目标与部署命令（Workers 静态资产托管）
confidence: medium
supersedes: project_deploy_target.md
---

fleetview 已从 Cloudflare Pages 迁移到 Workers 静态资产托管，部署命令统一为 `wrangler deploy`。原 Pages 流程（`wrangler pages deploy dist`）弃用。

**Why:** 迁移到 Workers 静态资产托管后，Pages 那套部署流程不再适用，需用新命令避免误部署到旧目标。
**How to apply:** 发布一律 `wrangler deploy`，不要再用 `wrangler pages deploy`；遇到旧脚本/文档里的 Pages 部署命令按此更新。
