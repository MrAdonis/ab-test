我需要一个命令行工具 `fmlint`，用来检查一个目录下所有 Markdown 文件的 frontmatter 是否合规。

背景：我的知识库有一百多篇 md，每篇 frontmatter 应该有 title / updated / type / tags 四个字段。type 只能是 concept / method / tool 之一，updated 必须是 YYYY-MM-DD 格式，tags 必须是非空数组。现在人工检查太累，而且我还想让 CI 和其他 agent 脚本能直接调它、读它的结果做后续处理。

请用 Python 实现，放在 `fmlint/` 目录里，带上测试。跑 `python -m fmlint <dir>` 能用。

验收：
- 能正确识别缺字段、字段格式错、type 取值非法这三类问题
- 没有 frontmatter 的文件、空文件、frontmatter 语法坏掉的文件都不能让工具崩掉
- 我能一条命令跑测试，确认它是好的
