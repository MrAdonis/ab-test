# Memory 维护规范

- 记忆文件 frontmatter 必须包含 `confidence: high/medium/low`；frontmatter 只放稳定事实属性，不放运行状态；写入时已知会过期的事实（订阅额度/临时节点/可用性前提/复审承诺）加 `review_by: YYYY-MM-DD`（到期日写入时已知，属稳定属性）——过期未复审默认按休眠处理，健康检查脚本每次会话点名
- 新建记忆默认 `confidence: medium`，经过多次验证有效后升为 high
- MEMORY.md 是索引：一条记忆一行 `- [Title](file.md) — hook`，按 confidence 分组 high → medium → low
- 每条记忆一个文件：frontmatter（name/description/confidence）+ 正文（事实 + **Why:** + **How to apply:**）

## Supersession（知识替换）
- 更新 memory 时区分**补充**（扩展旧信息→直接编辑）和**替代**（否定旧信息核心主张→走 supersession）
- Supersession 流程：新文件加 `supersedes: old.md`，旧文件加 `superseded_by: new.md` + confidence 降为 low
- 读取带 `superseded_by` 的 memory 时，跳转到替代文件
