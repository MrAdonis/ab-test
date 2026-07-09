# Memory 维护规范

- 记忆文件 frontmatter 必须包含 `confidence: high/medium/low`；frontmatter 只放稳定事实属性，不放运行状态
- 新建记忆默认 `confidence: medium`，经过多次验证有效后升为 high
- MEMORY.md 是索引：一条记忆一行 `- [Title](file.md) — hook`，按 confidence 分组 high → medium → low
- 每条记忆一个文件：frontmatter（name/description/confidence）+ 正文（事实 + **Why:** + **How to apply:**）

## Supersession（知识替换）
- **落盘前先查重复与矛盾**（写入闸）：新建/更新 memory 前先 grep 相关旧 memory，区分**补充**（扩展旧信息→直接编辑）和**替代**（否定旧信息核心主张→当场走 supersession）——矛盾不留到下次撞见，两条打架的记忆同时被召回会让下游判断随机
- Supersession 流程：新文件加 `supersedes: old.md`，旧文件加 `superseded_by: new.md` + confidence 降为 low
- 读取带 `superseded_by` 的 memory 时，跳转到替代文件
