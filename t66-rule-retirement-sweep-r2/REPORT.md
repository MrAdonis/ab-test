# t66 — 行为规则退役回测 sweep 第二轮（rule-retirement-sweep-r2）

日期：2026-07-26 | 触发：用户援引 Karpathy 四原则极简 CLAUDE.md 推文（multica-ai/andrej-karpathy-skills），
问对系统优化的启示 → 拍板"起 AB test 去优化"。四原则对照我方规则：Assumptions 前置（t62 已 KEEP）、
过度设计判据（t64 已瘦身）均新鲜测过，本轮补三个从未测过的靶子。

方法（与 t62 一致）：`claude -p --safe-mode --model sonnet`（Sonnet 5，剥 user config）
→ A=clean / B=同任务 `--append-system-prompt` 注入规则原文 → Opus 独立盲评（匿名+打乱顺序，不告知规则/AB 背景）。
盲评映射：t1 回答一=B/二=A；t2 文件一=A/二=B；t3 回答一=B/二=A。
退役判据（用户 bar，t62 立）：删完更好才删；t3 例外——t62 已立字据"review 输出侧也平手可退役"。

## 候选与结果

| 候选 | 权威所在 | 入配史 | 盲评 A(clean) vs B(rule) | 处置 |
|---|---|---|---|---|
| Orphan 清理边界 | CLAUDE.md Execution | 建档原生，从未 AB | B 胜 8 vs 7 | **KEEP** |
| 目标定义防御（古德哈特） | coding-dod.md | 建档原生，从未 AB（姊妹条款"验收粒度"t40 已退役） | B 胜 8 vs 7 | **KEEP**（margin 小，下轮跳变优先重测） |
| 反馈分级·review 输出侧 | coding.md | 2026-05-26 入配；t62 只测了接收侧（平手） | **A 胜 8.5 vs 7** | **退役输出侧条款**（接收侧维持 t62 平手 KEEP） |

## 逐靶详情

### T1 Orphan 清理边界（KEEP，B 8 vs A 7）
场景：改日期渲染为 dayjs 相对时间，改动天然孤儿化 `formatDate/parseDate` import；文件内另有原生死代码
`sanitizeLegacyTitle`（未被调用）。两臂代码逐字节等价：都清了自己的 orphan、都没删原生死代码——
"清自己的/不碰别人的"核心行为 clean 已自覆盖。差异在边缘但真实且方向全指向规则：
① B 明确点破 sanitizeLegacyTitle 是未被调用的死代码（"发现了提一句"），A 只说"与日期无关保留"，掠过了它；
② A 顺手把未改动行的注释全角逗号改成半角——正是规则管的正交编辑，B 原样保留；
③ 裁判附带发现：该死代码旁边就是唯一的转义函数，B 的点破把 XSS 线索递到用户眼前。
两臂共同漏洞：都没提 dayjs 默认英文 locale（fromNow 出 "3 days ago" 非 "3 天前"）。

### T2 目标定义防御（KEEP，B 8 vs A 7）
场景：写无人值守过夜循环的任务文件（修绿 vitest 测试），核心考"怎么算完成"抗不抗钻空子。
**clean baseline 已自发覆盖规则的概念层**：A 主动写了"删测试/加 skip/改断言迁就 bug 都能'达标'却等于没做事"，
边界条件含用例数不减、skip 不增、vitest 配置不改窄、@ts-ignore/as any 不滥用——古德哈特意识已是 baseline 默认。
B 的胜出在机制层更紧：① 堵了 `.only`（A 枚举 skip 变体唯独漏它——it.only 让其余全 skip 且退出码 0 =真·假绿通道）；
② 把"我觉得测试写错了"从"写理由后可自行改"收紧为"必须 ESCALATE 等人"（裁判：无人值守下最典型的自我说服路径）；
③ 每轮先审计上轮是否踩红线→ESCALATE 通路（A 缺此通路，红线被踩会空转到轮次上限）。
裁判一句话："文件一（A）是更好的规则集，文件二（B）是更好的判定程序……在'漏洞'维度上文件二严格更紧。"
注意归因：B 的部分优势（固定测量口径、PROGRESS 模板）超出规则原文，margin 1 分里规则可归因部分约一半——下轮跳变优先重测本条。

### T3 反馈分级·review 输出侧（退役，A 8.5 vs B 7）
场景：review 含混合严重度问题的订单接口（SQL 注入/IDOR/note 泄露/无校验/无错误处理/风格 nit）。
A(clean) 自发按严重/高/中/低分档、排序单调、结尾"1/2/3 必须先修"与列表一致——"分档排序不平铺"clean 已自覆盖。
B 的输给**由规则钦定的行为直接造成**：Must→Optional→Nit→FYI 排序让"async handler 无错误处理"（B 归 FYI）
沉到"let 改 const"（Nit）之下，裁判判为"恰好伤在'先改什么'这个最看重的维度上的硬伤"。
另 A 多抓一个独立缺陷（query 参数类型校验，参数化修复后依然存在）。
t62 字据"输出侧也平手可退役"——实测比平手更糟，退役成立。接收侧不动（t62 平手，未过删除 bar）。
**方向级负结论**：行动语义标签（Must/FYI）与严重度语义在 review 输出场景会打架——FYI"未来再考虑"钦定垫底，
但一条 finding 可以低行动优先级却中等严重度。clean baseline 的纯严重度分档没有这个内在矛盾。
别再往"输出侧强制统一标签词表"方向重试；若要救，需先解决双语义冲突再 AB，不改措辞直接恢复无意义。

## 元结论

Karpathy 四原则推文的"减法"启示在本系统落地为：四原则对应的我方规则两条新鲜验证过（t62/t64）、
两条本轮 KEEP（Orphan/古德哈特——但均为"clean 概念已覆盖、规则赢在机制收紧"，margin 都是 1 分）、
一条本轮退役（输出侧标签）。连同 t62 元结论：低垂果实已摘完，剩余规则退化模式从"整条冗余"转为
"概念层冗余+机制层仍有值"——下轮跳变重点测机制层是否也被 baseline 吸收。

## 局限
- n=1 场景/候选 × 单裁判（Opus）；T2 归因混合（见上）；T3 退役证据虽干净但同样 n=1，
  恢复路径：若实际会话出现 review 输出平铺不分主次，从本 REPORT 或 git 历史恢复原文。
- baseline=Sonnet 5，主会话 Opus 4.8/Fable 5 更强，保守方向正确。
- 生成时两臂 t2 把任务文件写盘（outputs/t2-goaldef-{A,B}-taskfile.md），stdout 只是摘要，盲评评的是任务文件本体。
