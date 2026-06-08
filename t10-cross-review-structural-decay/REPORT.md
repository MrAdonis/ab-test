# t10 — cross-review v3 vs v4：结构腐化检测层

**日期**：2026-06-08
**场景**：S4-ext — UserService.update_profile（10行 Python）
**对比**：4-Agent Swarm（v3）vs 5-Agent Swarm + 结构腐化 Agent（v4）

## 背景

cross-review v3 跑4个并行 Agent 做 runtime 代码审查（行为回归、安全、性能、契约）。

brooks-lint（github.com/hyhmrright/brooks-lint）基于12本经典工程书提炼出六维架构腐化诊断，每个发现强制走完 Symptom → Source → Consequence → Remedy 四步（Iron Law），并为每个维度定义了 What Not to Flag 防假阳性。

v4 从 brooks-lint 吸收了诊断层（`decay-risks.md`，295行）和 Iron Law 约束，作为第5个 Agent 加入 swarm，不引入 brooks-lint 的配置体系、历史追踪和多模式系统。改动量：diff 不超过150行。

## 结果

| 维度 | v3.0 | v4.0 | delta |
|------|------|------|-------|
| 审查覆盖度（runtime + structure）| 3/5 | 5/5 | +2 |
| 结构腐化覆盖（R1-R6）| 0/5 | 5/5 | +5 |
| 格式一致性（S→S→C→R）| 2/5 | 5/5 | +3 |
| 误报控制 | 4/5 | 5/5 | +1 |
| 输出可行动性 | 3/5 | 5/5 | +2 |
| 结构健康分输出 | 0/5 | 5/5 | +5 |
| **总分** | **12/30** | **30/30** | **+18** |

## 关键发现

预期应检出的 5 项全部命中：

- [x] Runtime: email silent bug
- [x] Security: SQL injection
- [x] R2 Divergent Change — loyalty 积分逻辑混入 profile 更新（**v3 盲区**）
- [x] R5 DIP 违反（**v3 盲区**）
- [x] R6 name/avatar_url 静默丢弃 + email 条件永假（**v3 盲区**）

最关键的 R2 发现（v3 完全看不见）：

```
Symptom：loyalty 积分计算（login_count×10+500）和 loyalty 表 UPDATE
         出现在 update_profile 函数体内

Source：R2 Change Propagation，Divergent Change

Consequence：积分倍率调整、活动 bonus 上线、积分上限规则变更，
             每一次都必须修改 UserService，
             误伤 profile 逻辑的风险随迭代次数增长

Remedy：提取 LoyaltyService.record_profile_update()，
        通过 domain event ProfileUpdated 解耦，各自独立演进
```

结构健康分：50/100（R6×2 各 −15，R2 −15，R5 −5）

## 结论

**保留 v4.0**。

核心收益在 Agent 5：Iron Law + S→S→C→R 格式命中了 v3 完全漏掉的3个架构维度（R2/R5/R6）。结构腐化发现有可操作的 Remedy，结构健康分（50/100）提供了量化的腐化程度信号。

吸收策略有效：只取诊断层，不取基础设施，改动量极小，效果差距显著。
