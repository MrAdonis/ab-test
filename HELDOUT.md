# HELDOUT — KEEP 入配前的固定回归任务集

KEEP 结论要写进 rules/skill（slow-state）之前，拿获胜变体把下面三个任务各跑一遍，与 clean baseline（无该规则）产出盲评对比。判定标准：

- **held-in**：与本次 t 同类型的任务，获胜变体仍应赢或平——优势消失说明 AB 结果不稳，暂缓入配
- **held-out**：其余类型的任务，获胜变体不得输——输了 = 新规则在别处引入回归，回滚或收窄触发条件

普通 t 不强制，只有入 slow-state 的 KEEP 走这道闸。运行时**只把任务文本喂给模型**（复制下面引用块内文字，不带本文件其他内容），prompt 卫生规则照适用：不出现 t 编号 /「AB」/「评测」字样。

## 任务集 v1（2026-07-11 建，绑定底模大版本跳变换血）

### H1 · 内容写作

> 把「MCP 和 Skills 的区别」写成一条 260 字以内的中文推文，读者是天天用 Claude Code 的开发者，别写成科普腔，要有自己的判断。

评法：两份产出打乱标签盲评（hook 强度 / 信息密度 / AI 腔），可辅以 `/write-review` 分数。

### H2 · 代码工具

> 写一个 Python CLI `dirstat.py`：输入一个目录路径，统计各扩展名的文件数和总字节数。要能被脚本调用（支持 `--json`），目录不存在时给结构化报错而不是裸 traceback，附带能跑的 pytest。

评法：pytest 通过为前提，再按 agent-native 四契约（统一 schema / 结构化错误 / 自带测试 / `--help` 自描述）逐项对照 + 盲评代码质量。

### H3 · 诊断判断

> 我的静态站部署到 Cloudflare Pages 之后所有图片 404，本地 dev server 完全正常。给我一个排查方案，说清你觉得最可能的原因和验证顺序。

评法：盲评假设质量（是否多假设分列、有没有可执行的验证步骤、是否先验证后下结论），不看有没有猜中"标准答案"。

## 换血规则

- **触发**：底模大版本跳变（与 wiki-lifecycle §④ 存量回测同节点），或某任务被连续 3 次 KEEP 当作 held-in 同类（说明它已不够"out"）
- 换血时新任务仍保持三类型覆盖（写作 / 代码 / 判断），旧版本任务保留在本文件历史区不删，供旧结论复核

## 溯源

2026-07-11 由「生产回放」条款升级而来（CLAUDE.md Verification ②），源自 Lilian Weng《Harness Engineering for Self-Improvement》中 Self-Harness 的 held-in/held-out 双重回归验证。未 AB，观察到误伤（合理 KEEP 被 held-out 挡住且人工复核认为是误杀）即回滚为生产回放。
