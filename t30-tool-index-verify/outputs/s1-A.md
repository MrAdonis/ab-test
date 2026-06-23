两个任务分开处理。

---

## 1. 查「指定做市商报价义务豁免」A 股规则

用 AnySearch，不用 WebSearch/tavily，原因：这是中文深度专业内容（交易所规则细节），通用搜索的结果会是泛泛介绍文，AnySearch 能挖到交易所官网原文、专业论坛和券商合规部门的一手资料。

命令：

```bash
~/.claude/scripts/anysearch.sh "指定做市商 报价义务豁免 A股 规则" --zone cn --lang zh-CN
```

加 `--zone cn --lang zh-CN` 是因为目标是中文专业源，强制走中文区索引。

**用前确认它能用：**

```bash
ls -l ~/.claude/scripts/anysearch.sh && head -5 ~/.claude/scripts/anysearch.sh
```

脚本存在且有执行权限即可直接跑。如果不确定 API 配置是否正常，可以先用一条简单查询测试：

```bash
~/.claude/scripts/anysearch.sh "做市商" --zone cn --lang zh-CN
```

返回结构化结果而非报错，说明工具可用。

---

## 2. 找之前讨论过「做市商」的会话

用 session-grep，它跨工具搜索 Claude Code 和 Codex 的历史 transcript，比翻记忆可靠得多。

命令：

```bash
~/.claude/scripts/session-grep.py 做市商
```

如果结果太多想缩范围，可以加时间过滤：

```bash
~/.claude/scripts/session-grep.py 做市商 --since 2026-01-01
```

或者只看在特定项目里讨论过的：

```bash
~/.claude/scripts/session-grep.py 做市商 --project stock
```

session-grep 返回的是会话片段和时间戳，能直接定位到当时讨论的上下文。
