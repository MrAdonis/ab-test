---
name: project-deploy-target
description: fleetview 部署目标与部署命令
confidence: high
---

fleetview 部署在 Cloudflare Pages，部署命令 `wrangler pages deploy dist`，分支预览自动开启。

**Why:** Pages 免运维、预览分支方便客户验收。
**How to apply:** 发布一律 `wrangler pages deploy dist`，不要手动传静态文件。
