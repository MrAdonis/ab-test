# t73 — 翻案腔「禁动作不禁字面」+ 七类变形表 vs 现行 3-regex 版

**结论：REJECT（1:1 平手，margin 低于噪声基线，变形表未能压制自身列举的变形）**

日期：2026-08-08 · 模型：sonnet（生成）/ opus（盲评）· 来源：KKKKhazix/human-writing revision.md 蒸馏候选

## 设置

- A = 现行 writing.md FORBIDDEN #6（setup-reveal 3-regex 版）+ 相关禁令节选
- B = 同上，但 #6 升级为「禁的是修辞动作不是字面」+ 七类变形表（字面/省字/跨句/换字/以为体/让转体/抬价体）
- 任务 1：800 字远程办公观点短文（用户论点本身是翻案形状，诱惑复读）
- 任务 2：1000 字创业复盘（"写得有洞察一点"，诱惑洞察路标）
- 盲评：opus，甲/乙标签，映射 task1 甲=A 乙=B / task2 甲=B 乙=A

## 结果

| 任务 | 翻案计数（裁判） | 胜者 |
|------|----------------|------|
| task1 远程办公 | A 4 次 vs B 4 次（B 开头 60 字连打两拍，密度更差） | **A** |
| task2 创业复盘 | B 3硬2软 vs A 4硬1软（A 的硬命中砸在结论段） | **B** |

确定性计数（check_prose.py，/tmp/human-writing）：翻案变形 A 合计 2 vs B 1，洞察路标 A 7 vs B 4，硬停词 A 1 vs B 0——B 方向性略优但量级小。

## 为什么 REJECT

1. **1:1 平手且单场 margin 薄**（t65 噪声基线 ±12%，本轮分差在噪声内）。
2. **变形表压不住自己列举的变形**：B 在 task1 照写「真正拖后腿的，是……」（抬价体，且开头连打），在 task2 照写「真正的问题出在」「真正的根源是」。把变形样本喂给模型不等于模型能在生成时自查——这类否定式枚举对 Sonnet 5 的边际约束力≈0。
3. **两变体共有的顽固残留**：「真正该做的是……而不是指望……」两篇几乎同构出现，裁判点名为模型默认腔。这说明瓶颈不在规则条文粒度，在生成时自查机制——该残留应由审核层（write-review / check_prose.py 类确定性计数）兜底，而非继续加粗生成层条文。

## 方向级结论

给已有「负例式禁令」追加更细的变形枚举，对强 baseline 预期无增益（同向证据：t57 五面枚举 REJECT、t51 蒸馏规则 REJECT）。翻案腔的下一步改进空间在**审核层确定性计数**（check_prose.py 的翻案变形 pattern 已可用），不在生成层条文。

## 文件

- prompts/：rules-A.txt / rules-B.txt / task1-remote-work.txt / task2-startup-lesson.txt
- outputs/：4 篇生成稿
- judge/：rubric.md / mapping.txt / input-*.txt / verdict-*.md（opus 盲评原文）
