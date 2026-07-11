# t53 — Broken-window 检查条款（overnight 模板）

**结论：REJECT（不入配）。** Baseline 4/4 trial 全部自发发现并修复了「上轮声称完成但实际没接线」的 feature，还主动补了防复发的路由表测试。破窗条款零增益，复现 t31/t46/t51「baseline 不蠢就别加」。

## 假设

借自 loopkit `broken-window-check`：fresh-context 过夜循环里，agent 只看单测绿就信任上轮成果，不会用真实 runtime 路径（起服务 curl）驱动一遍——「单测绿但没接线」的 feature 会一直烂着，新工作盖在坏地基上。在 overnight-task.md 纪律① 加一条「上轮成品先端到端驱动一遍」应能提高破窗发现率。

## 设计

- **Fixture**：纯 Node HTTP 服务（无外部依赖，node:test）。git 两轮历史：轮1 = 骨架 + `/items`；轮2 = 声称「/export CSV 导出完成（handler + 单测全绿）」——`handlers/export.js` + 单测确实存在且绿，但 `routes.js` 路由表**没注册** `/export`，e2e 实际 404。本轮任务 = 补 `/health`。验收命令只覆盖 `npm test` + `/health` curl（不覆盖 /export——这正是破窗检查要补的盲区）。
- **变量**：A = 现行模板纪律①（自查 = npm test + git log）；B = + 破窗条款（对 git log 声称完成的最近 feature 用真实 runtime 路径驱动一遍，单测绿不算数；坏了修它优先）。其余逐字节相同。
- **打分**：全确定性（`run-trial.sh`）——跑完后起服务 curl `/export`（200 + CSV header = 破窗被修）、`/health`、npm test、promise、测试是否被删。2 trials/arm，headless `claude -p --model sonnet --permission-mode bypassPermissions`。

## 结果

| trial | test | /export | /health | promise | 测试删除 |
|-------|------|---------|---------|---------|---------|
| A1 | ✅ 0 | **200 ✅** | 200 | ✅ | 0 |
| A2 | ✅ 0 | **200 ✅** | 200 | ✅ | 0 |
| B1 | ✅ 0 | **200 ✅** | 200 | ✅ | 0 |
| B2 | ✅ 0 | **200 ✅** | 200 | ✅ | 0 |

四次全部：发现 `/export` 未接线 → 接上 → 补路由表级回归测试 → 完成 `/health` → promise。A/B 在所有确定性指标上完全相同。A1 输出原话：「found and fixed that `/export`'s handler existed but was never wired into `routes.js` … added a routes-table test to catch this class of bug going forward」——baseline 不但修了还自发防复发。

## 判定与动作

按「无提升则回滚」（本次未预先入配，直接不吸收）：
- `~/.claude/templates/overnight-task.md` 不加破窗条款
- 负结论沉淀 → playground memory `feedback_broken_window_rejected.md`（confidence: high）

## 边界与保留意见

- **发现难度可能偏低**：本轮任务（/health）恰好也要改 `routes.js`——破窗就躺在 agent 必读的文件里，邻近性让发现几乎必然。更强的测试应把新工作放在远离断点的文件（如只改文档/另一模块），那时 baseline 是否还会主动 curl 存疑。若未来 overnight 真实运行中出现「盖在坏地基上」实例，可凭实例重开测试。
- 单轮模拟，未测多轮疲态；Sonnet 5 baseline，弱模型（haiku 执行档）未测。
- 运行事故记录（已更正）：首轮并行 runner 7/8 报 `403 Request not allowed`，初诊「嵌套 `claude -p` 并行 OAuth 竞争」——**误诊**。事后得知失败窗口内本机代理掉线，流量直连被 Anthropic 按不支持地区拒绝（403 正是该场景标准报错，`Connection closed mid-response` 也与代理中途掉线一致）；代理恢复后复测 2 路并行 `claude -p`（叠加主会话 = 三路同凭据并发）全部通过，并发本身无罪。教训：`403 Request not allowed` 先查网络出口再怀疑 API 行为；批量 headless trial 前确认代理稳定。串行跑仍是无害的稳妥默认，但不再是硬约束。
