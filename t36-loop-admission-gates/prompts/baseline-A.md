# A 组规则（现有 loop 选型规则，无候选）

你在判断"要不要建自动化循环（loop）/ 怎么建"时，遵循以下已有规则：

**四类 loop，按轻量度选——in-context 是默认**：
1. in-context 自配速 loop `/loop-until`——最轻：零安装/零新进程，本质一段五字段提示，agent 不丢上下文、自己掐退出条件。默认用它。
2. Ralph / overnight-loop.sh——每轮全新进程。升级触发：上下文会被污染或装不下、无人值守过夜。
3. Workflow 工具——脚本化编排 20+ 独立子任务、流程固定不用中途讨论。
4. 内置 /loop——按死时间间隔重跑，不看结果（最弱，只在纯轮询场景用）。

**五字段模板**：Goal（可验证终点禁主观词）/ Check 命令（每轮跑的反馈命令，无可跑 check=没有 loop）/ Exit when（基于 exit code 非主观）/ Max iterations（默认 8）/ 边界（古德哈特防御，禁删跳测试凑数）。三态收口 resolved/caveats/blocked。

**核心洞察**：壳越轻越好，效果由退出条件决定——必须是可跑命令不是"看起来做完了"。古德哈特防守最好焊进 Exit when 本身，别靠 agent 自觉。

一次性脚本、单点修复不套 loop 纪律。
