# SHARED-BASE — t30（A/B 两臂都拿到）

> 这是当前配置里关于「本机工具/脚本路由」的现状摘要，代表 baseline。A 臂只有这段；B 臂在此之上叠加 `INCREMENT.md`。

## 工具/脚本散落写法（现状）

配置里调用本机工具的方式 = **在 rules/memory 各处用 inline code 绝对路径直接点名**，没有集中式清单，没有「用前校验」协议。例：

- 联网抓取走 `rules/routing.md` 四层路由（autocli → fetch layer → byob/web-access → TinyFish）。
- 升级搜索：`~/.claude/scripts/anysearch.sh "query"`（中文深度/primary source 时用）。
- 搜会话：`~/.claude/scripts/session-grep.py <词>`。
- 代理抓取：`proxy.edonqai.com`（CF Worker，`?url=目标&token=TOKEN`）。
- 全局 CLI 用 Homebrew，项目依赖用包管理器（`feedback_install_routing`）。
- 各种维护脚本散在 `~/.claude/scripts/*.sh`（design-lint / session-stats / git-activity-digest / wiki-distill / overnight-loop 等）。

## 现状的隐含约定

- 路径在哪条 rule 里写过，AI 就知道；没写过的工具，AI 凭经验/训练知识猜命令名和参数。
- 工具是否真的装在这台机器（MacBook Air，macOS 25.5）、什么版本、MCP 是否已注册启用——**没有单一可查的事实源**。AI 默认「应该装了」然后裸跑。
- 缺工具时没有声明式补装路径，AI 自行决定 `brew install` 什么 / 怎么验证。

## 环境事实

- 机器：MacBook Air 16GB，macOS Darwin 25.5，zsh。
- 包管理：Homebrew（全局 CLI）。
- 自定义工具集中在 `~/.claude/scripts/`，MCP 配置在 Claude Code settings。
