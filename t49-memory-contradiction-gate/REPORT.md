# t49 — memory 矛盾检查写入闸（借自 mempal VERIFY BEFORE INGEST）

**假设**：在 Supersession 规则前加「落盘前先 grep 查重复与矛盾」写入闸，能提高
「新事实否定旧 high-confidence 记忆时正确走 supersession」的比率。
**变体**：A = 旧句（只区分补充/替代）；B = 新句（写入闸前置）。单变量 = supersession 首行。
**任务**：记录一条与既有 `project_deploy_target.md`（high）核心主张矛盾的新事实（Pages → Workers 迁移）。
**模型**：Sonnet 子代理 × 3 trial/臂。任务 prompt 零评测字样；全局 CLAUDE.md 已临时回滚至旧句。

## 评分标准（跑前预登记）

| 项 | 分值 |
|----|------|
| C1 发现矛盾：识别到 project_deploy_target.md 与新事实冲突 | 3 |
| C2 正确处置：新文件 `supersedes:` + 旧文件 `superseded_by:` + confidence 降 low（三件套全 =4；只改旧文件正文未走链 =2；只建新文件 =0） | 4 |
| C3 MEMORY.md 索引同步（新条目 + 旧条目标注/移组） | 2 |
| C4 无副作用（不动无关文件、frontmatter 合规） | 1 |

**判定**：B 均分 − A 均分 ≥ 2 → KEEP；差距 < 2 或 A 臂 C1+C2 已普遍满分（baseline 不蠢）→ REJECT 回滚。

## 结果

（待填）

## 结果（2026-07-08）

执行：Sonnet 子代理 × 6（A 臂 a1/a2/a3 旧规则，B 臂 b1/b2/b3 新增写入闸句），任务 = fleetview 部署 Pages→Workers 迁移写入 memory（与 fixture 中 confidence: high 的旧记忆正面矛盾）。主代理事后 grep 工作区实际文件打分，不采信子代理自报（证据见 outputs/inspection.txt 与各臂快照）。

| 臂 | C1 发现矛盾(3) | C2 正确处置(4) | C3 索引同步(2) | C4 无副作用(1) | 合计 |
|----|------|------|------|------|------|
| A-a1 | 3 | 4 | 2 | 1 | 10 |
| A-a2 | 3 | 4 | 2 | 1 | 10 |
| A-a3 | 3 | 4 | 2 | 1 | 10 |
| B-b1 | 3 | 4 | 2 | 1 | 10 |
| B-b2 | 3 | 4 | 2 | 1 | 10 |
| B-b3 | 3 | 4 | 2 | 1 | 10 |

六臂全部满分：supersedes + superseded_by + confidence high→low 三件套齐全，MEMORY.md 均正确移组并标注 superseded，无关文件零改动。B−A = 0。

## 判定：REJECT（回滚）

命中预注册否决条件「A 臂 C1+C2 已普遍满分（baseline 不蠢就别加）」。旧 supersession 段（"更新 memory 时区分补充和替代"）已足以让 Sonnet 在正面矛盾场景走完整替换流程；新增的「落盘前先查重复与矛盾」写入闸句是零增益 context 负担。CLAUDE.md 该行保持原句，负结论沉淀 feedback_contradiction_gate_rejected.md（confidence: high）。

局限：本场景矛盾显眼（同名主题文件就在 6 个文件的小库里）。矛盾埋在大库深处、文件名不相关时写入闸是否有增益未测——但那更接近检索问题而非规则问题，不据此翻案。
