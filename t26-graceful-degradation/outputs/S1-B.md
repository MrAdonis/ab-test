---
name: fetch-webpage
description: >
  Fetch the main text content of a webpage and return clean Markdown.
  Primary path: r.jina.ai proxy. Fallback chain: defuddle → bare curl.
  Use when you need to read a public URL as clean Markdown text.
---

# fetch-webpage

抓取网页正文，返回干净 Markdown。主路径 `r.jina.ai`，失败依次回退 `defuddle`，再失败裸 `curl`。

## When to Use

- 读公开文章/文档/帖子的正文内容
- 用于分析、摘要、翻译、引用的单页抓取
- 目标是人类可读正文（不是 JSON API、不是列表批量抓）

## Not For（自我排除）

- **需要登录态**的页面（DM、付费墙后、私有内容）→ 走 `routing.md` Layer 3a byob（`browser_read`）
- **X/Twitter 推文**（`x.com/*/status/*`）→ 首选 byob `browser_read`，byob 不可用才降级第三方代理
- **批量抓取 20+ 页面**→ 走 `routing.md` Layer 4 TinyFish
- **需要滚动/交互才能加载的动态内容**→ 走 Layer 3b web-access
- **Cloudflare 被动指纹保护站**（403 返回）→ 先尝试本 skill；若 jina 451 ban + defuddle 403 同时出现，升 Layer 1.5 Scrapling 或 Layer 4 TinyFish

## Workflow

执行顺序固定，不跳步骤，不自行判断哪条先有可能成功。

### Step 1 — 尝试 r.jina.ai

```bash
curl -sL "https://r.jina.ai/<TARGET_URL>" | head -c 8000
```

判断成功：返回内容长度 > 200 字符，且不包含 `"code":451`、`SecurityCompromiseError`、`DDoS attack suspected`。

**jina 失败信号（命中任一 → 跳 Step 2）**：
- HTTP 451（全局 abuse ban）
- 返回 JSON 含 `"code":451`
- 内容 < 200 字符（空壳响应）
- `curl` 连接超时或返回 403

### Step 2 — 回退 defuddle

```bash
curl -sL "https://defuddle.md/<TARGET_URL>" | head -c 8000
```

判断成功：返回内容长度 > 200 字符，且无明显错误消息（`error`、`failed`、`blocked`）。

**defuddle 失败信号（命中任一 → 跳 Step 3）**：
- 连接超时（defuddle 常见）
- 返回 403 / 空内容
- 内容长度 < 200 字符

### Step 3 — 裸 curl（最终回退）

```bash
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" "<TARGET_URL>" | head -c 8000
```

裸 curl 返回 HTML，需要从中提取正文（用 `grep` / 简单文本处理去掉 `<script>`、`<style>`、HTML 标签），输出尽量接近 Markdown 纯文本。

**整条链失败**：三步全部失败后，停下告知用户：
- 已尝试的路径和各自失败原因
- 建议使用 byob `browser_read` 或手动复制正文

## 输出契约

返回内容必须是 **Markdown 纯文本**。不返回 HTML 标签、不返回 JSON wrapper、不返回导航栏/页脚残渣。

截断规则：
- 默认 `| head -c 8000`（普通文章 8KB 足够覆盖正文）
- 用户明确要求全文时去掉截断，但先 `| wc -c` 估量再决定

成功返回结构：
```
[来源]：jina / defuddle / curl（告知用户走了哪条路）
[正文 Markdown]
```

失败返回结构：
```
[失败]：
- Step 1 jina：<失败原因>
- Step 2 defuddle：<失败原因>  
- Step 3 curl：<失败原因>
[建议]：<下一步操作>
```

## Good vs Bad

**Good** — 按顺序逐步尝试，每步有明确成功/失败判断：
```bash
# Step 1
result=$(curl -sL "https://r.jina.ai/https://example.com/article" | head -c 8000)
echo "$result" | wc -c  # 检查长度
echo "$result" | grep -c "451"  # 检查 ban 信号

# 确认失败后 Step 2
result=$(curl -sL "https://defuddle.md/https://example.com/article" | head -c 8000)
```

**Bad** — 三条同时发出，用第一个成功的（绕过了降级逻辑，无法正确记录走了哪条路）：
```bash
curl "https://r.jina.ai/..." || curl "https://defuddle.md/..." || curl "..."
# 这样 agent 不知道哪条成功，也无法给用户准确的错误诊断
```

## Gotchas

> 只记真实踩过的坑，不记假设。

- **jina 451 是域名级全局 ban，非临时限流** → 根因：jina 免费代理因滥用整体封禁某域名，持续数小时至数天。规避：命中 451 直接跳 Step 2，不重试 jina。
- **defuddle 常见连接超时，不是内容问题** → 根因：defuddle 服务本身稳定性较差。规避：timeout 设 10s（`curl --max-time 10`），超时即判失败跳 Step 3。
- **裸 curl 返回 HTML 不是 Markdown** → 根因：没有代理层做正文提取。规避：Step 3 的输出需要额外去除 `<script>`/`<style>` 标签后再展示，明确告知用户这是降级后的粗提取。
- **截断默认 8000 字节，长文会被砍断** → 根因：代理层动辄返回几十 KB（导航残渣 + 推荐内容）。规避：默认截断是正确的，长文归档/完整翻译时才去掉截断（先 `wc -c` 估量）。
- **联网相关的 Cloudflare ban / 反爬坑** → 见 `rules/routing.md`「jina 451 陷阱」和「Layer 1.5 Scrapling」段。
