# t9 测试场景：mattpocock/skills 吸收前后

测试目标：量化 /caveman、/grill-me、/diagnose 三个新 skill 对响应质量的提升。

## S1 — caveman（响应冗长度）

**场景**：技术问答，考验"去废话保信息"的能力。

**Prompt**：
> Redis 持久化有几种方式？各自适合什么场景？

**A（baseline）**：Claude 正常回答，无任何 caveman 指令
**B（caveman）**：激活 /caveman 后的回答
**评分维度**：
- 信息完整度（关键点有没有漏，0-5）
- 废话密度（开头废话/过渡词/重复，越低越好，0-5，5=无废话）
- 可执行性（结论能直接用，0-5）

---

## S2 — grill-me vs Assumptions 前置（需求探索）

**场景**：用户提出模糊新功能，考验需求澄清质量。

**Prompt**：
> 我想给 edonspace 博客加一个 newsletter 订阅功能，帮我想清楚需求。

**A（baseline）**：按 coding.md「Assumptions 前置」——批量列出假设+推荐答案，等用户一次性确认
**B（grill-me）**：按 /grill-me——逐问题 Socratic 式，每题带推荐答案，一次问一个
**评分维度**：
- 需求覆盖深度（是否问到了关键决策点，0-5）
- 可执行性（用户确认后能直接开工，0-5）
- 用户体验（操作摩擦，批量确认 vs 逐问互动，0-5）

---

## S3 — diagnose vs 假设驱动调试（调试规划）

**场景**：间歇性 bug，考验调试方法论质量。

**Prompt**：
> 我的 Next.js API route /api/notifications 随机 500，日志里没有报错，本地不能复现，生产偶发，没有规律可言。

**A（baseline）**：按 coding.md「假设驱动调试」——OBSERVE→HYPOTHESIZE→EXPERIMENT→CONCLUDE
**B（diagnose）**：按 /diagnose——Phase 1 先建可跑 feedback loop，再进假设测试
**评分维度**：
- 反馈环建设（有没有给出可跑的验证命令，0-5）
- 假设多样性（是否覆盖了多个根因方向，0-5）
- 可操作性（下一步行动具体程度，0-5）
