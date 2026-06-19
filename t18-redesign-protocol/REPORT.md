# t18 — Redesign 协议章节 AB Test

**日期**: 2026-06-12
**被测改动**: `~/.claude/skills/design-system/SKILL.md` 新增「## Redesign 协议（改版已有站点）」章节（~15 行，源自 Leonxlnx/taste-skill 缺口 1）
**判定规则**: 加权均分 B > A 即 keep；B ≤ A 回滚该 prose 章节（lint 6 条规则在脚本层，不在本测范围）
**结论**: **KEEP**（B 8.59 > A 8.13，+0.46）

## 设置

- **Variant A**: 当前 SKILL.md 移除 Redesign 章节（372 行）— `variant-A.md`
- **Variant B**: 当前 SKILL.md 完整版含 Redesign 章节（387 行）— `variant-B.md`
- 唯一变量 = 该章节；python 切片生成并验证
- **生成**: 6 × Sonnet 子代理（3 场景 × A/B），每个只读自己的 variant，fixture HTML 内联进 prompt（防 design-system auto-load 泄漏），禁读 ~/.claude/
- **评审**: 3 × Sonnet 盲评 judge，双盲（输出复制为 `judge/sN-design1/2.md` 中性文件名，映射 S1:1=B / S2:1=A / S3:1=B，judge 不可见）

## 场景

| 场景 | 设计意图 | 埋的陷阱 |
|------|---------|---------|
| S1 Lumeo 播客分析站 | 含糊 brief「现代化一下」，测判型+保留纪律 | 品牌紫 #6d28d9、完整 SEO 基线（title/meta/OG/JSON-LD）、nav slug、表单字段名 work_email/show_name、focus-visible、ICP 备案 |
| S2 佳膳食堂团餐 | 显式 overhaul 但内容全留，测内容保留 | 全部菜单/价格/服务文案、表单字段名+action+option value、法务三件（ICP/食品许可证/电话） |
| S3 Tidewatch（控制组） | greenfield 英文 landing，测协议是否产生噪音 | 无 fixture——redesign 协议不该出现任何痕迹 |

## 结果

| 场景 | A | B | margin | 胜者 |
|------|-----|-----|--------|------|
| S1 含糊 redesign | 6.98 | **8.58** | +1.60 | B |
| S2 显式 overhaul | **9.35** | 8.55 | −0.80 | A |
| S3 greenfield 控制 | 8.05 | **8.63** | +0.58 | B |
| **均分** | 8.13 | **8.59** | **+0.46** | **B** |

## 分析

**S1（协议核心靶场）是决定性差距，且败因精确命中协议主张**：
- 判型与声明（30%）：B 9 vs A 6——B 明确声明 overhaul 判型+依据+保留/改动对照清单（协议的「判型」+「永不改清单」直接起效）；A 不声不响直接重做
- 保留纪律（30%）：B 8.5 vs A 5.5——**A 丢了 CTA 表单的 `show_name` 字段（后端会断，重扣）**+ 品牌紫漂移 + login 改 CTA 语义；B 全项通过（SEO/slug/表单/ICP 逐字保留），仅品牌色 lighten 未声明扣 0.5
- 这两个维度合计 60% 权重，正是协议「动手前审计」「永不改清单」「品牌事实优先」三条主张的直接产物

**S2 B 输 0.8，但败因与协议无关**：内容保留 B 9.0 vs A 9.5 基本持平（协议管的部分没输）；差距全在反 AI Tell（7.5 vs 9.5）——B 用了 emoji 图标四格 + 三列等宽卡片，是生成代理的设计品味波动，不是 Redesign 章节导致。单跑噪声范畴。

**S3 控制组干净**：B 没有把 redesign 流程仪式带进 greenfield 任务（无噪音 8.5，扣分点是 eyebrow 规则自证——那来自 base skill 的 eyebrow 限额，A/B 共有，反而 A 侧也被点名同类问题），协议章节零污染，B 还以品牌判断小胜。

## 落地

- **KEEP**: SKILL.md Redesign 章节保留，不回滚
- lint 6 条规则（缺口 2）不在本测范围，已独立验证（violations fixture 6/6 命中、clean 零误报、edonspace 回归通过）
- memory 备注：`feedback_design_system_distill_rejected.md` 的「prose 规则密度已饱和」需收窄——饱和的是 greenfield 设计规则；**新领域章节（redesign 流程）是首个 AB 通过的 prose 增量**（t18 vs 之前 Impeccable 蒸馏、t14 frontend-design 两次失败）

## 文件

- variants: `variant-A.md` / `variant-B.md`
- fixtures: `fixtures/s1-site.html` / `fixtures/s2-site.html`
- 场景定义: `prompts/scenarios.md`
- 产出: `outputs/s{1,2,3}-{A,B}.md`
- 盲评: `judge/s{1,2,3}-verdict.md`（副本 `judge/sN-design{1,2}.md`）
