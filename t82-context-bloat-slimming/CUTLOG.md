# t82 删减台账（每处删减对应 CRITERIA.md 一条判据）

单位 = 字符数（非字节）。base 列为 D1 后的值，两臂共同起点。

| 源文件 | base | slim 对应段 | 保留率 | 主判据 |
|--------|------|------------|--------|--------|
| CLAUDE.md | 17,220 | 3,933 | 23% | D3 模型路由大表 / D4 指针段 |
| routing.md | 9,104 | 1,811 | 20% | D3 四层路由六张表 |
| hard-gates.md | 2,350 | 1,418 | 60% | K1 保护，仅并合并扫描器四行 |
| coding.md | 13,216 | 6,891 | 52% | D2 反馈分级 / D5 冗余展开 |
| coding-dod.md | 3,462 | 1,532 | 44% | D2 目标定义防御 / D4 Codex 触发指针 |
| writing.md | 5,720 | 3,252 | 57% | D3 风格技法罗列 / D5 反例表压缩 |
| wiki-lifecycle.md | 5,227 | 1,197 | 23% | D3 lint 检查表 / D4 supersession 副本 |
| skill-tiers.md + skill-chains.md | 19,053 | 2,090 | 11% | D4 skill 清单重复 skill description |
| **合计** | **75,352** | **22,166** | **29%** | |

相对未做 D1 的原始 78,643 字符：**−71.8%**。

## 逐条对应

**D1 溯源元信息**（已在 base 阶段执行，两臂共同起点）
78,643 → 75,352，−3,291（4.2%）。确定性收益，不进 AB。

**D2 margin ≤1 或已实测平手**
- coding.md 反馈分级四档：**未全删，压成 1 行**（判据说删，我压缩了）。理由：接收侧 t62 平手，但"Must 默认全改、其余列出不擅自实施"是用户可见的行为承诺，全删会改变交互契约。**这是对判据的偏离，记在此。**
- CLAUDE.md Orphan 清理边界（8v7）：删。
- coding-dod.md 目标定义防御（8v7）：删。

**D3 taxonomy / 罗列表**（本轮最大头，约 −28,000）
- CLAUDE.md 模型路由 14 行任务分流表 + Fable 5 分层三节 + advisor 三坑 → 压成一段散文 + 两条硬约束。
- routing.md 四层路由表 + Layer 3 内部选择表 + adapter 三来源表 + fetch 内部路由表 + 社交站点分流表 + 特殊路由表 → 散文 + 一段特殊路由。
- skill-tiers.md 全部（Daily Core / Specialist / Auto-trigger / Cloudflare 套件 / example-skills / GSAP / Inventory / 拓扑契约 / 装着未路由）→ 删，仅保留"两类 skill"的产品层事实 + 触发速查表精简版。
- writing.md 长文原型 6 行表 + 风格技法 → 压成两段。
- wiki-lifecycle.md lint 检查项表 + inbox 生命周期展开 → 压成两句。

**D4 单一源违反**
- Codex 三 lane 在 CLAUDE.md 和 coding-dod.md 各有一份 → 只留 CLAUDE.md。
- Supersession 在 CLAUDE.md 和 wiki-lifecycle.md 各有一份 → 只留 CLAUDE.md。
- 按需加载方法库指针表在 CLAUDE.md 和 skill-chains.md 各有一份 → 只留 CLAUDE.md。
- skill 清单（skill-tiers.md 全表）与真实 skill description 机制重复 → 删表。**注意这条在本轮 HELDOUT 下测不到**（三任务都不涉及 skill 路由），见 REPORT 局限。

**D5 弱模型脚手架**
- coding.md 四阶段调试循环的 ASCII 流程图 → 删，保留四阶段文字。
- coding.md「规则效果自检」整节 → 删（自我监控指令，非行为规则）。
- coding.md 子代理规范的举例展开 → 收进原句。
- CLAUDE.md「按需加载」各行的括号解释 → 收进表格。
- Rationalization Watch 表保留 7 行（删了"我需要更多行才能测"一行，与单变量硬约束重复）。

## 未删（K 列全项已核）

K1 hard-gates 全部 checklist 项在 slim 中逐条对应存在（四个扫描器合并为一行，但都点名）。
K2 十一条高 margin 条款逐条在 slim 中可 grep 到关键词。
K3 中文回复 / 绝对路径铁律 / 认动词再动手 / 效果优先 四条原文保留。
