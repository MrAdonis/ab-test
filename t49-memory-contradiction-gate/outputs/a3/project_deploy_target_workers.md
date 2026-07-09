---
name: project-deploy-target-workers
description: fleetview 部署目标与部署命令（Workers 静态资产托管，取代 Pages）
confidence: medium
supersedes: project_deploy_target.md
---

fleetview 已从 Cloudflare Pages 迁移到 Workers 静态资产托管，部署命令统一为 `wrangler deploy`。Pages 那套流程（`wrangler pages deploy`）已弃用。

**Why:** 项目迁移到 Workers 静态资产托管后，Pages 部署路径不再生效，继续用旧命令会部署到错误目标或直接失败。
**How to apply:** 发布一律用 `wrangler deploy`，不要再用 `wrangler pages deploy`；涉及分支预览等 Pages 专属能力的旧假设需重新核实是否有 Workers 等价方案。
