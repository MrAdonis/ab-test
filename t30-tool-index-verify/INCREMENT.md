# INCREMENT — t30（仅 B 臂）

> 源自 `zhaoxuya520/reverse-skill` 的「按需自举工具链」三件套（`bootstrap-manifest.json` + `tool-index.md` + 用前校验协议），已 macOS 化、并对齐「路径已散落写进 rules」的现状。唯一新增的东西 = 下面这段协议 + 一份示例 tool-index 片段。

## 工具用前校验协议

调用任何**本机 CLI 工具或自定义脚本**前，按顺序：

1. **查清单拿真实路径**：先查 tool-index（下方示例片段 / 真实版在 `~/.claude/tool-index.md`）拿绝对路径 + 用法，**禁止凭训练知识猜命令名、子命令、参数或路径**。清单里有 = 用清单的事实；清单里没有 = 进第 4 步。
2. **用前 verify**：执行主任务前先跑 `verify` 命令（如 `command -v <tool>` / `<tool> --version`）确认真的可用且版本对得上，不假设「应该装了」。
3. **MCP 特例**：MCP 工具「本机有 runtime（node/npx/python）」≠「已在 Claude Code 注册并启用」。verify 要确认的是注册启用状态，不是 runtime 存在。
4. **缺失 → 声明式补装**：工具不在清单或 verify 失败时，按声明的 `bootstrapKind` 给确定性补装步骤（macOS：`brew-formula` / `pip-package` / `npm-mcp` / `script-local`），装完刷新清单 + 重跑 verify，再继续；自动装失败则输出结构化手动引导，**不裸跑赌它能成**。

## 跳过条件（防过度套用）

下列情况**不查清单、不 verify**，直接用：

- POSIX/coreutils 标准命令（`ls` `cat` `grep` `git` `find` `cd` `echo` `wc` `sed` 等显然存在的）。
- 已在当前会话里成功跑过、路径已确认的同一工具。
- 纯只读、失败无副作用、且命令名是众所周知标准形态的一次性调用。

> 原则：校验成本只花在「猜错会真出错」的工具上（自定义脚本、第三方 CLI、MCP、非标准路径/参数）。对标准命令套校验 = 仪式噪声，等于没遵守协议。

## 示例 tool-index 片段（B 臂参考用，非全量）

| 工具 | 用途 | 真实路径/调用 | verify | 缺失补装(bootstrapKind) |
|------|------|--------------|--------|----------------------|
| anysearch | 升级搜索（中文深度/primary source） | `~/.claude/scripts/anysearch.sh "query"` | `test -x ~/.claude/scripts/anysearch.sh` | script-local（脚本已在仓库，缺=检查 ~/.claude git） |
| session-grep | 跨工具搜 transcript | `~/.claude/scripts/session-grep.py <词>` | `python3 ~/.claude/scripts/session-grep.py --help` | script-local |
| autocli | 结构化数据提取 | `autocli <site> <command>` | `command -v autocli` | brew-formula / 见 routing.md |
| scrapling | CF 被动指纹站抓取（Layer 1.5） | `python3 -c "import scrapling"` | `python3 -c "import scrapling"` | pip-package：`pip install "scrapling[fetchers]"` |
| chromafs MCP | 跨项目文档检索 | MCP: vfs_grep/vfs_cat 等 | 确认 `/mcp` 列表里 connected | npm-mcp：见 `reference_chromafs_revival` |
| proxy.edonqai.com | CF 代理抓取 | `curl "https://proxy.edonqai.com/?url=目标&token=TOKEN"` | `curl -sI https://proxy.edonqai.com` | n/a（远端服务，缺=检查 token/到期） |

> 真实落地时这份清单由一个扫描脚本（`refresh-tool-index.sh` 的 macOS 版）生成真实绝对路径 + 版本，本片段仅供 AB 测协议价值。
