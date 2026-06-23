---
name: tinyfish
description: Use TinyFish cloud agent to extract structured data from web pages. Triggers when: scraping multiple sites in parallel (≥20), target has strong anti-bot (Cloudflare Turnstile / IP ban / captcha) and no login required, or headless task runs unattended. Requires TINYFISH_API_KEY.
---

## Pre-flight Check (REQUIRED)

Before making any API call, **always** run this first:

```bash
[ -n "$TINYFISH_API_KEY" ] && echo "ok" || echo "NOT set — stop here"
```

If NOT set, you **MUST stop and tell the user**. Do **NOT** fall back to `curl`, `WebFetch`, `browser_read`, or any other tool — TinyFish is a paid cloud service with no local equivalent. The task cannot proceed without the key.

**Setting the key (two options):**

Option 1 — add to `~/.claude/api_keys.env` (global, all sessions):
```bash
echo 'export TINYFISH_API_KEY="your-key-here"' >> ~/.claude/api_keys.env
source ~/.claude/api_keys.env
```

Option 2 — add to `~/.claude/settings.local.json` (Claude Code only):
```json
{ "env": { "TINYFISH_API_KEY": "your-key-here" } }
```

---

## When NOT to Use This Skill

Use `rules/routing.md` Layer 1-3 first. Switch to TinyFish only when **all three** apply:

- Target is public (no login required) — login-required content → Layer 3 byob (real Chrome)
- Layer 1-3 failed or the task needs ≥20 parallel sites
- The task can tolerate ~30-60s latency per page and the business value justifies per-step cost

**Do NOT use for:** single-page lookups, tasks where user's Chrome is available and logged in, interactive exploration that requires live judgment — those belong to Layer 3.

---

## Endpoint & Auth

```
POST https://agent.tinyfish.ai/v1/automation/run-sse
Authorization: Bearer $TINYFISH_API_KEY
Content-Type: application/json
```

Response is an SSE stream. Read raw lines. The final result is the event where `type == "COMPLETE"` and `status == "COMPLETED"` — data is in the `resultJson` field. Do not write a parser; read raw SSE output directly.

---

## Examples (Progressively Complex)

### 1. Basic Extract — single URL

```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/products",
    "goal": "Extract all product names and prices. Return JSON with this EXACT schema, no extra wrapping: {\"items\": [{\"name\": \"string\", \"price\": \"string\"}]}. Every item must include both fields — do not return a list of plain strings."
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

### 2. Multiple Fields — add more schema keys

Same as above but extend the schema:

```bash
# goal excerpt — keep the EXACT schema instruction:
"goal": "Extract products. Return JSON with this EXACT schema, no extra wrapping:
{\"items\": [{\"name\": \"string\", \"price\": \"string\", \"url\": \"string\", \"in_stock\": true}]}.
Every item must include all four fields."
```

### 3. Stealth Mode — Cloudflare / 403 / captcha

Add `browser_profile: "stealth"` only when you observe: HTTP 403, Cloudflare challenge page, or CAPTCHA in result:

```bash
curl -s -N \
  -H "Authorization: Bearer $TINYFISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://g2.com/products/foo/reviews",
    "goal": "...(same EXACT schema goal)...",
    "browser_profile": "stealth"
  }' \
  https://agent.tinyfish.ai/v1/automation/run-sse
```

Do **not** add stealth by default — use it only when you observe one of the three signals above.

### 4. Proxy — specific country IP

```bash
-d '{
  "url": "...",
  "goal": "...",
  "proxy_config": { "country_code": "US" }
}'
```

### 5. Parallel Extraction — multiple URLs

**Good** — parallel curl calls, each independent:
```bash
for url in "$url1" "$url2" "$url3"; do
  curl -s -N \
    -H "Authorization: Bearer $TINYFISH_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$url\", \"goal\": \"...(EXACT schema)...\"}" \
    https://agent.tinyfish.ai/v1/automation/run-sse &
done
wait
```

**Bad** — single call asking agent to scrape multiple sites:
```bash
# DO NOT DO THIS
-d '{"url": "https://site1.com", "goal": "Also scrape site2.com and site3.com and combine..."}'
# Slow, unreliable, and the agent may silently skip sites
```

---

## Reading the Result

SSE lines look like:
```
data: {"type": "PROGRESS", "message": "Navigating..."}
data: {"type": "COMPLETE", "status": "COMPLETED", "resultJson": "{\"items\": [...]}"}
```

Read the line where `type == "COMPLETE"`. Parse `resultJson` as JSON. That is your data.

**COMPLETED status does not mean the goal succeeded.** Always check `resultJson` for failure signals: `"captcha"`, `"blocked"`, `"access denied"`, empty arrays where non-empty is expected, or plain strings instead of objects.

**Parser-side defensive extraction** (apply when writing code to consume results):
- Recursively find the first non-empty list (handles any wrapper depth)
- Try common wrapper keys in order: `items / result / data / news_items / headlines`
- Field aliases: `headline or title`, `source or publisher`, `url or link`
- Accept a list of plain strings as last resort rather than failing hard

---

## Goal Prompt — Key Rules

The `goal` string is executed by an LLM inside TinyFish. It will freely invent return shapes if you leave any ambiguity.

Three phrases that must appear in every goal with structured output:

1. `"Return JSON with this EXACT schema, no extra wrapping:"`
2. `"{\"items\": [{...all fields...}]}"` — spell out every field
3. `"Every item must include all N fields — do not return a list of plain strings."`

Each phrase blocks a different class of observed failures (wrong wrapper key / missing fields / string-only list).

---

## Latency & Cost

Expected latency: 30-60s per page. Budget ~1-3 steps per page extraction. 500 free steps on new accounts; paid after that.

Gate before calling:
```bash
[ -n "$TINYFISH_API_KEY" ] && echo "ok" || { echo "key missing — stop"; exit 1; }
```

If the key is exhausted or the account has no credits, the SSE stream will return an error event, not a COMPLETE event.

---

## Gotchas

> Only real failures with identified root causes.

- **Same goal, different wrapper keys on consecutive calls** → Root cause: TinyFish agent LLM decides return shape; even identical prompts produce `news_items` / `result` / `headlines` in rotation → Fix: use EXACT schema phrase + defensive parser (see above)
- **`status: COMPLETED` but `resultJson` contains `"blocked"` or `"captcha"`** → Root cause: agent status reflects task completion, not content success → Fix: always check resultJson text, not just status field
- **Parallel curl calls silently dropped** → Root cause: shell background jobs exit before parent reads their output → Fix: redirect each curl to a temp file, then read files after `wait`
```bash
curl ... > /tmp/tf_result_1.json &
curl ... > /tmp/tf_result_2.json &
wait
cat /tmp/tf_result_1.json /tmp/tf_result_2.json
```
- **`403` or empty result on public site** → Root cause: site uses Cloudflare passive fingerprinting → Fix: add `"browser_profile": "stealth"` and retry once. If still blocked, the content is likely login-gated; switch to Layer 3 byob (user's real Chrome)

> Networking / anti-bot patterns beyond TinyFish → `rules/routing.md`
