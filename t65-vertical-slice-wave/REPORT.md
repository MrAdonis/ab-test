# t65 — 垂直切片排期条款（vertical-slice-wave）

日期：2026-07-26 | 触发：Kevin Ma 转述 Dex Horthy《Why Software Factories Fail》part 2，
识别出唯一增量 =「垂直切片作为 wave 排序原则」（coding.md task_plan 节现有 wave/depends/must_haves
只管拓扑与验证，不管切片方向），开一轮测 baseline 是否已自会。

## 方法

- A = coding.md 现有「复杂任务管理 + task_plan 量化约束」节选注入；B = 同注入 + 新增「垂直切片排期」条款
- 2 个真实规划任务 × A/B，`claude -p --safe-mode --model sonnet`（Sonnet 5 clean baseline），
  每 run 独立 mktemp 沙箱 cwd；Opus 盲评（方案甲/乙匿名 + 每任务打乱顺序，不告知规则/对比背景）
- 任务设计刻意分两个条件：
  - task1（报销工具全栈规划）：**无任何提示**——纯需求 + 技术栈，测自发行为
  - task2（CLI 加 Web 仪表盘）：**带真实用户式提示**（"最怕做两周拼起来发现图表不对"），测有提示条件
- 顺序映射（盲评标签 → 变体）：task1 甲=B 乙=A；task2 甲=A 乙=B

### ⚠️ 第一轮污染事故（已作废重跑）

第一轮 4 个 run 的 cwd 落在本测试目录，headless agent 自己翻到 `prompts/rules-B.txt` 和历史输出，
在回复里明说"你在做规则集 A/B 对比实验、rules-B 含垂直切片条款"——测试感知污染实锤（Anthropic
J-space 研究预言的场景第一次在本框架真实发生）。4 个 run 全部作废（残迹见 outputs-contaminated-note/），
重跑改为每 run 独立 mktemp 沙箱。**流程教训：headless AB run 的 cwd 永远不能是测试目录本身**，
t62 之前没炸只是因为任务不写文件、agent 没探索目录。

## 结果

| 任务 | 条件 | A(现规则) | B(+条款) | 靶向维度（方向暴露点+每wave可演示） |
|---|---|---|---|---|
| task1 报销工具 | 无提示 | 29/50 | **38/50** | A 4+4，B 8+9 —— 胜差全部来自靶向维度 |
| task2 仪表盘 | 有提示 | 35/50 | 36/50 | A 7+5，B 9+9 —— 总分平手（1 分噪声级） |

行为细节：
- task1-A（无提示 baseline）**水平分层实锤**：脚手架→schema→鉴权→上传API→布局→数据访问层→四个页面→部署，
  6 wave，首个完整用户流程在 wave 5（83% 进度）才第一次可见。裁判原话："交付顾问视角下最贵的失败模式"。
- task1-B：wave1 地基合并成单 feature，其后每 feature 都是端到端用户闭环，4 wave 全可演示。
- task2-A（有提示 baseline）**大幅自覆盖**：自发走 CONTRACT.md 契约确认 + fixture 静态原型先行（wave 2 可见），
  但 wave 1 纯文档、wave 3 纯后端管道，节奏仍慢 B 一拍。
- task2-B：wave 1 第一天浏览器可见 mock 图 + 真实落库，4 拍全可演示；裁判选 B 但只差 1 分，
  且明确说"选的是骨架不是内容"——B 的工程语义有洞（聚合键缺陷、幂等验收不自洽、5 机联调缺失）。

## 关键结论

1. **KEEP（候选，待 held-out）**。无提示条件下 baseline 不自发垂直切片（margin +9，靶向维度 17 vs 8），
   条款正中缺口；有提示条件下 baseline 自覆盖、条款不减分（+1 噪声级）。无提示是生产常态，规则值得入配。
2. **打破连败序列的原因**：t51/t53/t57/t60/t61 连续 REJECT 是"baseline 已自会"，本条测的是**排序偏好**
   而非能力/风险意识——baseline 会垂直切（task2 证明），但默认不这么排（task1 证明）。偏好类规则与
   能力类规则的 baseline 自覆盖率不同，这是方向级洞察。
3. **观察项（非阻塞）**：两任务中 B 版的"约束完整性"维度都略低于 A（7v8、6v8）——切片注意力可能轻微
   挤占工程细节。n=2 不足以定论，入配后若复现，考虑在条款里加一句"切片不豁免量化约束"。

## 拟入配文本（coding.md「task_plan 量化约束」后新增小节）

```
### 垂直切片排期（wave 排序原则）
- feature 切分与 wave 排序按**垂直闭环**组织：每个 feature 是一条端到端、用户可见可验证的最小闭环
  （界面 → 接口 → 数据），不按技术层水平切（先数据库、再服务层、再 API、最后前端）
- 第一个闭环允许 mock：先定接口返回 mock 数据让前端跑通、浏览器里可见，后续 wave 逐层换真实现
  （服务、数据库、异常处理）
- 判据：每个 wave 结束必须存在一个能在浏览器/CLI 里演示的用户可见结果；连续两个 wave 无用户可见
  产出 = 水平分层信号，重切
```

溯源：Dex Horthy《Why Software Factories Fail》pt.2（与 coding.md 已引的 40% 质量拐点同源方法论）。

## 局限

- n=2 任务 × 单裁判单 run；两任务都是"全栈 web + 明确技术栈"形态，未测纯后端/纯 CLI/库开发场景
  （垂直切片对无 UI 项目的适用性未验证，条款判据里"浏览器/CLI 可演示"已尽量覆盖）
- baseline=Sonnet 5，主会话 Fable/Opus 更强；但本条是排序偏好非能力，强模型是否默认垂直切未测——
  保守方向存疑（不像能力类规则可以"弱模型会则强模型必会"推定）
- task2 裁判指出的 B 版工程缺陷提示：单 run 内容质量方差大，靶向维度的结论（切片方向）比总分更可靠
- 入配前置：按 Verification 规则，slow-state KEEP 需先跑 HELDOUT.md 固定任务集（held-in/held-out
  双验证）——本轮未跑，入配前补
