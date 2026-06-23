---
name: tinyfish
description: >
  Use TinyFish to extract structured data from web pages via cloud agent.
  Trigger when: scraping public sites without login state, batch extraction
  (20+ URLs), sites with strong anti-bot (Cloudflare / captcha / 403),
  unattended scheduled tasks, or country-specific proxy needed.
  Requires TINYFISH_API_KEY — paid cloud service, no local fallback.
---

# TinyFish Web Extraction

## Pre-flight Check (REQUIRED)

Before making any API call, **always** run this first:

```bash
[ -n "$TINYFISH_API_KEY" ] && echo "ok" || echo "NOT set — stop here"
```

If the key is **not set**, you **MUST stop and ask the user to configure it**.
Do **NOT** fall back to other tools — TinyFish is the only path for this task.
There is no local equivalent.

**How to set the key (two options):**

**Option 1 — `~/.claude/api_keys.env` (Edon 全局规范):**
```bash
echo 'export TINYFISH_API_KEY="your-key-here"' >> ~/.claude/api_keys.env
source ~/.claude/api_keys.env
```

**Option 2 — Claude Code settings:**
在 `~/.claude/settings.local.json` 添加：
```json
{ "env": { "TINYFISH_API_KEY": "your-key-here" } }
```

500 free steps 耗尽后需付费续充。用量参考：单页提取约 3-10 steps。

---

## When to Use TinyFish

**使用（满足任一）：**
- 20+ 个 URL 并发抓取
- 目标站有 Cloudflare / captcha / 403，且内容不需要登录态
- 无人值守定时任务（用户不在机器前）
- 需要指定国家代理 IP（如 `country_code: "US"`）
- Layer 1-3（autocli / fetch layer / byob）全部失败

**不使用（改走其他路由）：**
- 单次或少量（<5）URL → fetch layer 或 byob，更轻
- 需要真实登录态 cookie → Layer 3a byob（用户 Chrome）
- 探索性/视觉驱动的交互（边看边点）→ Codex computer_use lane
- `TINYFISH_API_KEY` 未配置 → 停止，不降级

---

## API 基础

**Endpoint:**
```
POST https://agent.tinyfish.ai/v1/automation/run-sse
```

**认证 header:**
```
Authorization: Bearer $TINYFISH_API_KEY
Content-Type: application/json
```

**最小可行调用（curl）：**
```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Extract the article title and body text. Return JSON with EXACT schema: {\"title\": string, \"body\": string}",
    "url": "https://example.com/article"
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

返回 SSE 流。每行格式 `data: {...}`。**读最后一个 `"type":"COMPLETE"` 且 `"status":"COMPLETED"` 的事件，数据在 `resultJson` 字段。不要写 parser，直接读原始 SSE 输出。**

---

## 渐进示例

### 1. Basic Extract（单 URL，单字段）

```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Extract the page title. Return JSON: {\"title\": string}",
    "url": "https://news.ycombinator.com"
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

### 2. Structured List（多字段，写死 schema）

```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Extract top 10 posts. Return JSON with EXACT schema, no extra wrapping: {\"items\": [{\"rank\": number, \"title\": string, \"url\": string, \"points\": number, \"comments\": number}]}. Every item must include all five fields — do not return a list of plain strings.",
    "url": "https://news.ycombinator.com"
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

### 3. Stealth Mode（Cloudflare / 403 场景）

遇到以下情况才加 `browser_profile: "stealth"`：目标返回 403 或 CAPTCHA 页面，且内容不在登录墙后。

```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Extract product listings. Return JSON: {\"items\": [{\"name\": string, \"price\": string}]}",
    "url": "https://target-with-cloudflare.com/products",
    "browser_profile": "stealth"
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

### 4. Proxy（指定国家 IP）

```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Extract local pricing data. Return JSON: {\"prices\": [{\"item\": string, \"price\": string}]}",
    "url": "https://regional-site.com",
    "proxy_config": {"country_code": "US"}
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

### 5. Parallel Extraction（20+ URL，并发）

**Good** — 并行发起，不等待前一个完成：
```bash
for url in "${URLS[@]}"; do
  curl -s -N \
    -H "Authorization: Bearer $TINYFISH_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"goal\": \"Extract title and price. Return JSON: {\\\"title\\\": string, \\\"price\\\": string}\", \"url\": \"$url\"}" \
    https://agent.tinyfish.ai/v1/automation/run-sse &
done
wait
```

**Bad** — 单次 prompt 合并多 URL：
```bash
# 不要这样做 — 单次 goal 里塞多个 URL 不可靠，顺序无保证
curl ... -d '{"goal": "从 site1、site2、site3 都抓取数据...", "url": "site1"}'
```

---

## 输出契约

SSE 流中读取规则（**不要写 parser**，直接读原始输出）：

1. 过滤出所有 `data: ` 开头的行
2. 找最后一个 `"type":"COMPLETE"` 且 `"status":"COMPLETED"` 的 JSON 对象
3. 数据在该对象的 `resultJson` 字段（字符串，需二次 JSON.parse）

**Prompt 端写死 schema 的关键词**（必须包含，缺一都会导致结构漂移）：
- `"EXACT schema"`
- `"no extra wrapping"`
- `"do not return a list of plain strings"`
- 列举每个必需字段名和类型

---

## Gotchas

> 只记真实踩过的坑（执行失败并定位过根因的），不记假设。

- **`COMPLETED` ≠ 成功** → 根因：agent 内部 LLM 可能被 captcha / access denied 拦住，状态字段仍报 COMPLETED → 规避：检查 `resultJson` 有无 `"captcha"` / `"blocked"` / `"access denied"` / 空数组（预期不该空时）
- **同 goal 三次返回三种 wrapper key** → 根因：agent 内部 LLM 自由决定返回 shape（实测：`news_items` / `result` / `headlines` 三种）→ 规避：goal 里写 `EXACT schema` + `no extra wrapping`；parser 端递归找第一个非空 list，优先命中 `items/news_items/result/headlines/data`，字段支持别名（`headline or title`、`url or link`）
- **goal 里只写"JSON list"** → 根因：类型不够具体，LLM 只返回字符串数组，字段全丢 → 规避：goal 里明确每个字段名和类型，加 `"Every item must include all five fields"`
- **联网 / 反爬相关坑** → 见 `rules/routing.md` Layer 4 TinyFish 触发细则

---

## 自检（调用完成后）

```bash
# 验证 key 已加载
[ -n "$TINYFISH_API_KEY" ] && echo "key ok" || echo "key missing"

# 验证返回不是空
# 从 SSE 输出找 COMPLETE 事件，检查 resultJson 非空且非错误信号
grep '"type":"COMPLETE"' /tmp/tinyfish-out.txt | \
  python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('data:')[-1]); print('ok' if d.get('resultJson') else 'empty result')"
```
