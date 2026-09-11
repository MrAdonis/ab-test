# t79 — 禁隐喻替直陈（mannered prose ban）

**结论：不入配（无信号平手）。** 8 次盲评 + 2 套评审协议 + 确定性词频，三条证据线都落在噪声带内。候选条款不写进 `~/.claude/rules/writing.md`。

## 候选来源

Anthropic《Prompting Claude Fable 5.1》文档 `## Writing density` 节，原文主张：

> Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." … The phrases exist to display the writer, not to convey the idea, and readers can tell. … It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.

短版：`Please remove all mannered prose.`

这条在 `writing.md` FORBIDDEN 里确实没有对应轴——已有的 setup-reveal（第 6 条）、em-dash（第 7）、替读者说话（第 8）、虚构百分比（第 9）都不覆盖「用比喻替直陈」。所以候选是真缺口，值得测。

## 设置

- **A 臂**：`writing.md` 现有最近邻规则原文（角色定义 + ALLOWED + FORBIDDEN 1-8 + 反例对照表 + 收尾/目标）
- **B 臂**：A + 候选第 9 条（禁隐喻替直陈，含「旋钮/护城河/飞轮」示例与自查法）
- 测增量非测有无。生成 sonnet，评审 opus，各臂独立 `claude -p` 沙箱跑
- 两个任务：①800 字公众号文章（窄场景 vs 通用助手，给 4 条素材）②350-400 字官网首页文案（客服知识库，给 3 个卖点）
- 两轮生成（r1 / r2），共 8 篇

## 结果

### 协议一：并排盲评（甲/乙，轮间翻转映射）

| 轮次 | 任务 | 甲 | 乙 | 映射 | A | B |
|------|------|----|----|------|---|---|
| r1 | task1 | 32 | 39 | 甲=B 乙=A | **39** | 32 |
| r1 | task2 | 35 | 22 | 甲=A 乙=B | **35** | 22 |
| r2 | task1 | 27 | 38 | 甲=A 乙=B | 27 | **38** |
| r2 | task2 | 36 | 27 | 甲=B 乙=A | 27 | **36** |
| | | | | **合计** | **128** | **128** |

**这一轮的结果是槽位决定的，不是臂决定的**：两轮里 task1 永远是「乙」赢（39 / 38），task2 永远是「甲」赢（35 / 36），跟哪个臂坐在那个位置无关，且同槽位分数跨轮几乎不动。映射翻转本来是防位置偏置的，结果正好把它照出来了——并排评审在这个任务上零分辨力。

### 协议二：单篇独立盲评（无对照，绝对标准）

去掉并排对比这个变量，8 篇各自单跑：

| 轮次 | 任务 | A | B |
|------|------|---|---|
| r1 | task1 | **38** | 31 |
| r1 | task2 | **30** | 26 |
| r2 | task1 | 27 | **41** |
| r2 | task2 | 33 | 33 |
| | **合计** | 128 | **131** |

靶向维度①（隐喻替直陈密度，越高越干净）：A = 5/5/4/6 = 20，B = 4/4/8/7 = 23。

换了协议，结论没换：**主导变量是轮次不是臂**。r1 里 A 全赢，r2 里 B 全赢，同一臂跨轮的分差（task1 的 A：38→27，B：31→41）比任何 A-vs-B 分差都大。单次 `claude -p` 的生成方差把规则效应吃掉了。

### 协议三：确定性词频（不经模型）

数 rubric 列举的隐喻载体（护城河/飞轮/资产/原材料/坑/砸钱/及格线/变厚/困在/沉淀…）：

| | task1 | task2 | 合计 |
|---|---|---|---|
| A | 2 + 2 | 4 + 3 | **11** |
| B | 6 + 1 | 3 + 4 | **14** |

B 反而多 3 处。方向上和 t73/t77 一脉（负例枚举把品类 prime 出来了——B 的 r1-task1 稿子里「坑×2 / 砸钱 / 及格线 / 打法」全是 rubric 列举过的载体），但 3/8 篇的差距撑不起结论。

## 关键证据

**规则没能压住它自己点名的东西**。B 臂 prompt 里写了「旋钮→参数」这类替换示例，r1-task1-B 的成稿仍然写出「这些坑是具体的，能一个一个填」「通用助手的坑是抽象的，填一个又冒出十个」——同一意象连用三次，正是候选条款要禁的形态。同一轮 A 臂那篇只用了「摆设/赛道」两处。

**但 r2 完全反过来**：r2-task1-B 全篇只剩一个「赛道」（还是素材原文里的词），是 8 篇里最干净的；同轮 A 用了「及格线/赛道」。

两条观察互相抵消。

## 判读

按 `HELDOUT.md` 的噪声基线（单跑单评轮间方差可达 ±12%，整轮反转在 t65 / t72-H2 都出现过并判为噪声），本次：

- 并排协议 128 : 128（0%）
- 单篇协议 128 : 131（+2.3%）
- 靶向维度 20 : 23（+3.8% 但方向与并排协议相反）
- 确定性词频 A 优 3 处（方向又与前两条相反）

四条线互相矛盾且全在噪声带内 = **无信号**。既不能判 KEEP，也不能判「反噬」——中途我一度按 r1 结果说过「A 臂两战全胜，且赢在靶向维度上，方向和预期相反」，r2 把这句话推翻了，那是单轮结论，作废。

**处置：不入配。** 按「无提升则回滚」，`writing.md` 不动。

## 方法论产出（比结论值钱的部分）

1. **并排盲评有槽位效应，翻转映射只能照出它、不能消除它。** 靶向维度可数的任务，默认改用单篇独立盲评；把「翻转后同槽位分数是否稳定」当成协议健康检查——同槽位跨轮分数几乎不变，就说明裁判在评位置不在评文本。
2. **单跑单评的生成方差可以大到淹没规则效应。** 本次同臂跨轮分差最大 14/50（28%），远超候选规则可能带来的增量。以后靶向维度细的候选，每格至少 2 次生成再进评审，别拿 1 篇代表 1 个臂。
3. **确定性词频应该在模型评审之前先跑。** 它零成本、零方差，本次三个协议里唯一不受裁判情绪影响的一条；如果它先跑出 11 : 14 这种数，就该意识到样本量不够、直接加轮而不是先烧 8 次 opus 评审。

## 文件清单

```
prompts/rules-A.txt  rules-B.txt  task1-narrow-scope.txt  task2-landing-copy.txt
run.sh  run-r2.sh  run-judge-single.sh
outputs/      outputs-r2/          # 各 4 篇成稿
judge/        judge-r2/            # 并排盲评（rubric.md / mapping.txt / verdict-*.md）
judge/rubric-single.md
judge-single/                      # 单篇独立盲评 8 份
REPORT.md
```
