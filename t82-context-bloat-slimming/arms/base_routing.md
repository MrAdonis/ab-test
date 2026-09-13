---
description: URL 抓取路由和文件处理路由规则
---

# 联网与网页操作

按目标类型分流，不按域名猜工具。Layer 3 用本地登录态 Chrome，按操作复杂度分 byob (MCP) 和 web-access (Playwright 脚本)。

> **边界（routing.md 不覆盖的，走 Codex C lane）**：本四层只管「可脚本化/结构化」的联网与抓取。**原生 app GUI**（macOS 应用窗口）和**探索性/视觉驱动、不可预先脚本化的浏览器交互**（边看边点、布局会变、需临场判断——如 客户A 那类「跟着界面走」的搭建）→ 走 Codex computer_use lane（`~/Developer/cmux-agent-bridge/`），不是这里的 Layer 3。判断口诀：能提前把步骤写死成脚本 = 留在 routing.md；要靠看屏幕临场决定下一步 = Codex C lane。完整 lane 路由见 `~/.claude/references/codex-workflow.md`「Codex 三条 lane 与路由」。

## 四层路由

| Layer | 定位 | 适合 | 不适合 |
|-------|------|------|--------|
| **1. autocli** | 结构化数据提取（内建 50+ adapter + AI 生成自定义 adapter + autocli.ai 社区共享） | 对象/列表/元数据，结构化 JSON/table；理论上覆盖任意网站 | 登录态私密内容、临场交互探索 |
| **2. fetch layer** | 公开正文轻量抓取 | 文章、文档、帖子、一次性读取 | 登录态、强反爬、重 JS 动态渲染 |
| **3a. byob MCP** | 用户 Chrome + 10 个标准 MCP tools（`browser_read` / `browser_click` / `browser_get_cookies` 等） | **单步操作**：读页面、截图、点击、填字、取 cookie、列 tab、切 tab；轻量临场探索 | 多步脚本化序列、复杂流程控制 |
| **3b. web-access CDP** | 用户 Chrome + Playwright 脚本（一次执行多步） | **多步流程**：登录→填表→提交→读结果、批量交互、复杂状态机 | 一次性单步操作（用 3a 更轻、token 省） |
| **4. TinyFish cloud** | 云端 agent + stealth/proxy/vault（付费，按 step 计费，需 `TINYFISH_API_KEY`） | 批量并发（几十/上百站同时跑）、强反爬无登录态场景、无人值守定时任务、用户 Chrome 不可用时的远程 fallback | Layer 1-3 能完成的单次/少量任务；需要实时临场探索 |

**默认顺序**：autocli → fetch layer → 3a byob (单步) / 3b web-access (多步) → TinyFish → 告知用户手动操作

### Layer 1.5 旁路：Scrapling（Cloudflare 被动指纹站专用）

「Cloudflare 被动指纹挡住的公开结构化数据站」（g2/crunchbase 类，curl/jina/defuddle 全 403）是四层唯一弱格，Scrapling 的 `curl_cffi` TLS 指纹伪装免费补格，**不进默认顺序**。**三条全满足才用**：① 公开数据（无需登录态）② CF 被动指纹挡住 curl（裸抓 403）③ 需要写 Python 批量抓 / 目标站频繁改版；任一不满足回四层。实测证据、能力边界、安装命令见 `~/.claude/references/scrapling-cf-bypass.md`（装前过 hard-gates 安装审查）。

### Layer 3 内部选择：byob vs web-access

| 信号 | 选 byob (3a) | 选 web-access (3b) |
|------|-------------|-------------------|
| 步骤数 | ≤ 3 步独立操作 | ≥ 4 步且需保持状态 |
| 接口形式 | AI agent 通过 MCP tool 一次调一个 | 写一段 Playwright 脚本一次跑完 |
| 典型场景 | 截图、读单页、取 cookie、点一个按钮 | 完整登录流程、低代码搭建、多页面流转 |
| Token 成本 | 低（每个 tool call 独立） | 极低（脚本一次执行，无 round-trip） |
| 失败恢复 | 容易（重试单个 tool） | 需重跑整段脚本 |

**byob 独有的快路径**：`browser_get_cookies` 导出登录态 cookie，配合 `curl` 抓需要 auth 的端点（绕过整个浏览器开销）。比如抓 X timeline 数据：byob 取 cookie → curl 直调 API。

### autocli adapter 三来源

| 来源 | 命令 | 说明 |
|------|------|------|
| **内建** | `autocli <site> <command>` | 50+ 站点：twitter（无 `x` 别名）、weixin、xiaohongshu、reddit、youtube、zhihu、hackernews、instagram、linkedin、bilibili、weibo、xueqiu、yahoo-finance、github(gh)、obsidian、readwise、docker、kubectl、gws 等 |
| **社区** | `autocli search <url>` | 搜索 autocli.ai 共享 adapter，选择后直接可用 |
| **AI 生成** | `autocli generate <url> --goal <goal> --ai` | AI 分析页面自动生成 adapter YAML；优先搜现有再生成 |

**无内建 adapter 时的路由**：`autocli search <url>` → 有社区 adapter 则用 → 无则 `autocli generate <url> --goal <goal> --ai` → 生成失败再降级到 fetch layer

**辅助命令**：
- `autocli explore <url>` — 探索网站 API 表面，发现可用端点
- `autocli cascade <url>` — 自动检测认证策略（PUBLIC → COOKIE → HEADER）
- `autocli auth` — 认证 autocli.ai 账户（AI 生成和社区功能依赖此）

### fetch layer 内部路由

| 目标特征 | 工具 |
|----------|------|
| 公众号文章（mp.weixin.qq.com URL 已知） | `autocli weixin download <url>`（需 Chrome 扩展连接）→ Markdown；扩展不通时 fallback `proxy.edonqai.com` |
| IP 受限 / 无直链 / 需统一出口 | `proxy.edonqai.com`（CF Worker 临时节点，约 2027 年到期；`curl -H "Authorization: Bearer $TOKEN" "https://proxy.edonqai.com/?url=目标"`，公众号加 `&platform=wechat`）。**token 只走请求头，`?token=` 已于 2026-08-05 删除**（CWE-598：URL 里的 token 会落进 CF 日志/history/Referer）。**源码 = CF worker `helloworld`**（默认名易误认，本地副本在 `~/Projects/personal/edonqai-proxy/src/worker.js`）。安全性质=token-gated 开放中继：拿到 token 即可用 CF IP 抓任意公网站，token 是唯一命门、勿上客户端 |
| X 单条公开推文（`x.com/*/status/*` 或 `twitter.com/*/status/*`） | 见下方「**X 推文首选 byob**」段（权威版，含 fallback 命令与截断规则） |
| JS 重渲染页（CSR/SPA），无需登录态——尤其 headless/无人值守没本机 Chrome 时 | Kitesurf playground：`curl "https://kitesurf.cloudflare.app/html?url=<URL编码>"`（另有 `/screenshot` `/pdf`；免鉴权，每次导航 20s CPU / 60s wall）。2026-08-08 实测：React CSR 全渲染、截图 1.9s、X 单推文数据中心 IP 也能过。**演示站属性，挂了不奇怪**；正式档 = 账户 Browser Run REST（token 已建存 api_keys.env `CLOUDFLARE_API_TOKEN`；429 code 2001 先查 dashboard Runs tab 日配额——Free 10 min/天，dashboard Playground 试玩也烧它），细节见 memory `reference_kitesurf_browser_run` |
| 普通文章，要干净 Markdown | `r.jina.ai` 或 `markdown-proxy` |
| 正文提取 + 去噪 | `defuddle` |
| 需 agent 判断结构 | `agent-fetch` |
| 简单公开页面 | `WebFetch` |

**X 推文首选 byob，不要赌第三方代理。** X 对未登录请求返回 402 / 残缺 HTML / 登录墙，所以别用 `WebFetch`。第三方 HTML 代理（jina/defuddle）和 JSON API（fxtwitter）全是第三方单点，实测会同时挂（jina 451 ban + defuddle 超时），不可托底。**自己的登录态 Chrome 才是稳定资产**：

```
# 首选：byob 走真实登录 Chrome，X 对登录用户吐完整内容
browser_read(url="https://x.com/<user>/status/<id>", screens=2)

# fallback（仅 Chrome 没开 / byob 不可用时）——任一可能在挂，逐个试：
curl -sL "https://kitesurf.cloudflare.app/html?url=https%3A%2F%2Fx.com%2F<user>%2Fstatus%2F<id>"  # CF Kitesurf 真渲染，2026-08-08 实测单条公开推文可过（返回 ~110KB HTML，正文在 og:title/描述 meta 里，配合截断/提取用）
curl -sL "https://api.fxtwitter.com/<user>/status/<id>" -o /tmp/tw.json  # JSON: .tweet.text/.author.screen_name/.likes
curl -sL "https://r.jina.ai/http://x.com/<user>/status/<id>"            # HTML 代理，易 451 ban
curl -sL "https://defuddle.md/http://x.com/<user>/status/<id>"          # HTML 代理，易超时
```

**默认截断**：jina / defuddle / 任何 markdown 代理抓正文默认尾接 `| head -c 8000`（单条推文/普通文章 8KB 足够覆盖正文）——这类代理动辄返回几十 KB（导航残渣 + 相关推荐 + 评论流），不截断直接灌爆 context。确需全文（长文归档、整篇翻译、付费墙后完整文档）才去掉截断，且去掉前先 `| wc -c` 估量。

**陷阱：`r.jina.ai` 的全局 abuse ban**

Jina 的免费 markdown 代理会因为"之前有人滥用某域名"把**整个域名全局封禁**（返回 `HTTP 451 SecurityCompromiseError`），持续数小时到数天。典型受害域：`finviz.com`、任何带 screener/数据表的金融站。

识别：`jina.ai` 返回的 JSON 里有 `"code":451` 和 `"DDoS attack suspected: Too many domains"`。

处理：**跳过 jina 直接走 `curl -A "Mozilla/..."`**（多数站点原生 curl 反而通）；仍失败则升 Layer 4 TinyFish。不要在 jina 那里重试。

### 社交站点：按内容类型分流，不按域名一刀切

社交站点（X/Instagram/LinkedIn/Facebook/Threads/微博/Substack/Medium/小红书）**不等于"一律走 CDP"**。按内容类型判断：

| 内容类型 | 路由 |
|---------|------|
| 公开单条内容（带 status/post/note ID，任何人能打开） | X 推文走上方「X 推文首选 byob」段（权威版）；其他站先 fetch layer，失败再升 Layer 3 |
| 登录态内容（DM、Following-only、私人账号、付费墙后） | 直接 Layer 3a byob（读单页/截图） |
| 列表/时间线/搜索结果（需要滚动、懒加载） | Twitter/X：Chrome 扩展在线时 `autocli twitter search/timeline/trending`（带点赞/评论数，平台级直搜）；扩展不在线则 byob/web-access；其他平台优先 autocli；否则 Layer 3b web-access |
| X 全网关键词/语义搜索、舆情、找某话题/某人的讨论（研究检索，无需 Chrome/登录态） | `~/.claude/scripts/grok-search.sh "query"`——grok CLI 原生 `x_keyword/x_semantic/x_user_search/x_thread_fetch`，唯一能做 X 语义检索的路径（autocli 是平台级直搜、要扩展在线；本条 headless 可跑）。wrapper 已剥执行/写/本地读面（只读，防推文注入）。前提：东京住宅代理（到期 2026-11-01），额度吃 Grok 订阅、token 不可观测；节点挂则回 autocli/byob |
| 需要交互（点赞、评论、发帖） | Layer 3b web-access（多步状态机） |
| 需要拿登录态数据走 API | Layer 3a byob `browser_get_cookies` → curl 直调 |

**已实测公开内容走 fetch 能通的**：
- `x.com/*/status/*` — 权威版见上方「X 推文首选 byob」段，本行仅清单占位；两处不一致时以权威段为准
- `x.com` 搜索 / 时间线 / 热搜 — `autocli twitter search/timeline/trending`（需 Chrome 扩展在线，走 autocli daemon port 19925）
- `mp.weixin.qq.com` — `autocli weixin download <url>`（需 Chrome 扩展）；扩展不通则 `proxy.edonqai.com`
- `v2ex.com` — 热门帖 `curl "https://www.v2ex.com/api/topics/hot.json"`；节点帖 `curl "https://www.v2ex.com/api/topics/show.json?node_name=<node>"`；单帖正文 `r.jina.ai`；无需 auth

**Substack / Medium 付费文章**：付费墙后内容直接 CDP（需要登录态账号）。公开免费文章可先 fetch。

**小红书**：公开内容先 autocli，登录态内容升 CDP。

**V2EX**：公开 API v1 无需 auth。热门帖 `curl "https://www.v2ex.com/api/topics/hot.json"`；节点 `curl "https://www.v2ex.com/api/topics/show.json?node_name=<node>"`；单帖内容 `r.jina.ai` fetch。无需升 Layer 3。

**判断优先级**：先 URL 模式识别（有 status ID = 单条公开） → fetch layer → 失败再升 Layer 3（按操作复杂度选 3a/3b）。不要看到社交站域名就反射性跳 Layer 3。

### Layer 4：TinyFish 触发细则

付费资源，谨慎使用。满足**任一**条件才考虑：

- **并发规模** ≥ 20 个站点同时抓，且每个任务需要导航/提取
- **强反爬 + 不需登录态**：stealth profile 能解决且不涉及私密内容
- **定时无人值守**：用户不在机器前（CI、cron、webhook 触发）
- **需要指定国家代理** IP（proxy_config.country_code）
- **Layer 1-3 全部失败**且任务有足够商业价值 justify 付费

**不要**用于：单次抓取、少量（< 5）站点、临场探索、用户 Chrome 可用的登录态任务。

**调用**：CLI 形式 `tinyfish agent run "goal" --url <url>`，或 curl 直调 `https://agent.tinyfish.ai/v1/automation/run-sse`。完整参考：`docs.tinyfish.ai/for-coding-agents`。

**Gate**：调用前先 `[ -n "$TINYFISH_API_KEY" ] && echo ok`；未设置就 **停下告诉用户**，不 fallback。500 免费 step 耗尽后切回 Layer 3/手动。

### 特殊路由

| 场景 | 工具 |
|------|------|
| YouTube 转录 | `/baoyu-youtube-transcript` |
| 搜索发现来源（默认） | `WebSearch` / `tavily_search`——按常规习惯走，绝大多数搜索用这个 |
| 搜索发现来源（升级到 AnySearch） | `~/.claude/scripts/anysearch.sh "query"`——遇「难获取的知识」时主动升级，命中任一即用：① **中文深度/专业内容**（金融微观结构、技术细节——WebSearch 是 US-only 抓不到中文专业源，这是 AnySearch 最硬优势）② **要 primary source / 社区信号 / 长尾**（GitHub PR·issue、Reddit、论坛、niche 博客——通用 SERP 会埋掉源头）③ **常规搜首轮只返回泛泛 SERP、没挖到真源**。中文查询加 `--zone cn --lang zh-CN`；瞬时 503/504 重试。英文+官方文档充分的题不必升级（WebSearch 自带综合更顺）。AB 实测依据见 memory `reference_anysearch` |
| CF 官方文档/API/Workers 查询 | `cloudflare-docs` MCP（不走 WebFetch——有索引、更干净、版本准） |
| CF Pages/Workers 日志排查 | `cloudflare-observability` MCP（不翻 dashboard） |

抓取成功后展示标题、来源、摘要，默认保存到 ~/Downloads/{title}.md。

# 文件处理路由

| 类型 | Skill | 关键工具 | 注意 |
|------|-------|---------|------|
| .pdf | `/pdf` | pypdf, pdfplumber, reportlab | 避免 Unicode 上下标（渲染黑框） |
| .docx | `/docx` | docx-js / unpack XML | 用 `ShadingType.CLEAR` 非 `SOLID` |
| .xlsx | `/xlsx` | openpyxl, pandas | 用公式非硬编码值 |
| .pptx | `/pptx` | pptxgenjs / unpack | 每页必须有视觉元素 |
