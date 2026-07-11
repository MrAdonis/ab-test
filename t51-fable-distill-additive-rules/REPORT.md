# t51 — Fable 蒸馏三条 rules 增补的验证（A 组）

**背景**：把 Fable 5 在各会话做过的仲裁/根因判断蒸馏成 Sonnet/Opus 可执行条目，A 组三条落到 rules 层、标了「未 AB 2026-07-08」。本轮补 AB，验证「clean Sonnet 5 baseline 是否已自发做出同样判断」——是则规则是堆料，按 wiki-lifecycle §5④ + t31/t49「baseline 不蠢就别加」回滚。

**变体设计**：ADD-behavior 规则用两臂盲测（非 FORBIDDEN 退役的单臂）。A 臂 = 最小工程师 persona（clean，无规则）；B 臂 = 同 persona + 该规则原文。单变量 = 规则本身。任务写成真实用户请求，零评测字样。

**模型/隔离**：Sonnet 5 生成臂（`claude -p --model sonnet --safe-mode --system-prompt <persona>`，clean cwd `/tmp/t51-clean`），3 trial/臂。Canary 探针确认 clean baseline 返回 `NO_CUSTOM_RULES`（无全局规则泄漏）。

## 被测三条

| 条目 | 落点 | 规则内容 |
|------|------|---------|
| A1 缓存误判 | coding.md Rationalization Watch 新增行 | "两次运行输出完全相同" → 疑缓存/没真重跑，校验时间戳/插 nonce 确认真执行 |
| A2 mock-auth 门控 | coding-dod.md appsec ②鉴权条 | mock/测试登录端点必须环境门控，无门控 mock-auth 按 P0 账户接管报 |
| A3 写入前矛盾检查 | wiki-lifecycle.md Supersession 前 | 写 memory 前检索邻近旧条目，矛盾走 supersession |

## 评分标准（跑前预登记）

两条各设一个真实请求场景，内嵌规则针对的失败陷阱。判每臂输出是否抓到目标失败：
- **A1 场景**：改帧率参数后重跑两次输出一字不差，问「生效了吗，可批量跑吗」。C1 识别"完全相同=危险信号"(4) / C2 给出证伪真执行的手段(4) / C3 验证前不轻率批准批量(2)。
- **A2 场景**：review 一段含无环境门控 `/dev-login`（任意 email 免密拿 session）的 Express 代码。C1 识别 mock 登录=账户接管(4) / C2 抓到缺环境门控·生产可达是关键(4) / C3 定级 P0/阻断上线(2)。

**判定**：B 均分 − A 均分 ≥ 2 且 A 臂 C1+C2 未普遍满分 → KEEP；否则（A 臂 baseline 已满分）→ REJECT 回滚。A3 见下方特判。

## 结果（2026-07-09）

### A3：不测，直接回滚（重复 t49 已拒方向）

A3「写入前矛盾检查」与 t49 刚 REJECT 的「落盘前先查重复与矛盾写入闸」是同一方向。memory `feedback_contradiction_gate_rejected`（high）已定论：旧 supersession 段让 baseline 六臂满分，写入闸句零增益，且明确「不再往该段加'写入前检查'类措辞」。A3 恰是被点名禁止的方向。按 rejected-edit buffer「下次别重复同方向」，直接回滚，不重跑（重跑只会复现 t49）。

### A1：REJECT — baseline 三臂全满分

| 臂 | C1(4) | C2(4) | C3(2) | 合计 |
|----|----|----|----|----|
| A-1 | 4 | 4 | 2 | 10 |
| A-2 | 4 | 4 | 2 | 10 |
| A-3 | 4 | 4 | 2 | 10 |
| B-1 | 4 | 4 | 2 | 10 |
| B-2 | 4 | 4 | 2 | 10 |
| B-3 | 4 | 4 | 2 | 10 |

**B − A = 0。** clean baseline 三次全部：明确把"两次完全一样"点为警报信号而非安心点、点名缓存命中/续跑跳过/进程没重启为成因、要求批量前先打印运行时值·清缓存·查 mtime 证伪执行。B 臂只多冒出"nonce"一词（规则原文用词），检测与处置行为零增量。

### A2：REJECT — baseline 三臂全满分

| 臂 | C1(4) | C2(4) | C3(2) | 合计 |
|----|----|----|----|----|
| A-1 | 4 | 4 | 2 | 10 |
| A-2 | 4 | 4 | 2 | 10 |
| A-3 | 4 | 4 | 2 | 10 |
| B-1 | 4 | 4 | 2 | 10 |
| B-2 | 4 | 4 | 2 | 10 |
| B-3 | 4 | 4 | 2 | 10 |

**B − A = 0。** clean baseline 三次全部：把 `/dev-login` 判为 P0/阻断上线的无密码账户接管后门、明确点名"没有 NODE_ENV/环境门控·生产天然可达"、建议物理移除或环境变量强门控（优于加 if 判断）。B 臂只是复用规则原文措辞（"P0 账户接管""未做环境门控"），检测行为零增量。

## 结论：A 组三条全部 REJECT，全回滚

Sonnet 5 baseline 在代表性场景里已自发做出与 Fable 相同的缓存疑判与 mock-auth 安全判断。这是本轮蒸馏的合法产出——验证了底模强度足够、拦住了配置膨胀，正是 AB 闸的用途。

**动作**：A1（coding.md 行）、A2（coding-dod.md appsec 嵌入）、A3（wiki-lifecycle.md 段）三处已全部回滚至原状。B/C/D/E 组（references / wiki / skill Gotchas / 项目 memory）非行为规则、不与 baseline 竞争，不受本轮影响，保留。A4（coding.md 指向 `[[hidden-bug-patterns]]` 的指针）属参考增强非行为规则，保留。

**局限**：两个场景都是"请求里已隐含要找问题"（问生效吗/review 安全）。规则在"没让找、agent 顺手漏检"的场景是否有边际价值未测——但那属检索/主动性问题，且按 t49 先例「除非有真实漏检案例否则不翻案」，无实际漏检证据不据此保留。
