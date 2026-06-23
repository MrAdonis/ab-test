---
name: fetch-webpage
description: Fetch the main text content of a webpage and return clean Markdown. Primary path: r.jina.ai proxy. Fallback 1: defuddle. Fallback 2: bare curl. Use when you need to extract article body, documentation, or post content from a URL.
---

# fetch-webpage

Fetches a URL and returns clean Markdown body text. Three-tier graceful degradation — no API key required, no pre-flight gate needed.

## When Not to Use

- X/Twitter URLs → use `browser_read` via byob (login-required, jina returns 451 ban)
- Login-walled content (paywall, auth-gated pages) → use Layer 3a byob (`browser_read`) instead
- WeChat 公众号 → use `autocli weixin download <url>` or `proxy.edonqai.com`
- Cloudflare-fingerprinted sites (g2, crunchbase) where curl returns 403 → use Scrapling Layer 1.5
- Pages requiring JavaScript rendering (SPAs with no SSR) → use Layer 3b web-access CDP

(Full routing decision table: `~/.claude/rules/routing.md`)

## Workflow

Execute the three tiers in order. Stop at the first success. A response is a **success** when: HTTP 2xx AND body length > 200 chars AND body is not a login/error page.

### Tier 1 — jina proxy (primary)

```bash
curl -sL "https://r.jina.ai/<URL>" | head -c 8000
```

Replace `<URL>` with the full target URL (no extra encoding needed, jina accepts it directly in the path).

**Success signal**: Output contains actual article text, not an error string.

**Fail signals — move to Tier 2 immediately, do NOT retry**:
- HTTP 451 (`SecurityCompromiseError`, `DDoS attack suspected`) — jina has globally banned this domain
- HTTP 4xx/5xx response code
- Response body is empty or < 200 chars
- Response body contains "access denied", "captcha", "blocked", "please log in"

### Tier 2 — defuddle (fallback)

```bash
curl -sL "https://defuddle.md/<URL>" | head -c 8000
```

**Success/fail signals**: same as Tier 1.

**Fail signals — move to Tier 3 immediately**:
- Connection timeout (defuddle frequently goes down)
- Same 4xx/5xx/empty/login-wall signals as Tier 1

### Tier 3 — bare curl (last resort)

```bash
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" "<URL>" | head -c 8000
```

Bare curl with a real browser UA. Many sites that block jina/defuddle serve raw HTML fine to a curl with UA.

**After bare curl**: the output is raw HTML — strip tags mentally or pipe through a simple extractor. Return whatever readable body text you can extract. If the output is still a login wall or CAPTCHA page, stop and tell the user which tiers failed and why.

## Output Contract

Return the fetched content as:

```
**Source**: <URL>
**Via**: jina | defuddle | bare curl
**Content**:

<Markdown body text>
```

- Strip navigation, footers, ads, comment sections — return article/doc body only
- Do NOT summarize or paraphrase — return the raw fetched text
- Truncate at 8000 chars (already handled by `head -c 8000`); if user needs full content, say so and offer to re-fetch without truncation

## Good vs Bad

**Good** — check the actual response before declaring success:
```bash
BODY=$(curl -sL "https://r.jina.ai/https://example.com/article" | head -c 8000)
# Check: is $BODY meaningful content?
# "please log in" → not success, move to Tier 2
# 400 chars of real article text → success
```

**Bad** — treating exit code 0 as success:
```bash
curl -sL "https://r.jina.ai/https://example.com/article"
# curl exits 0 even when jina returns a 451 error page
# Do NOT declare success just because curl didn't error
```

## Gotchas

> Only confirmed failures with root cause.

- **jina 451 `SecurityCompromiseError`** → root cause: jina globally bans domains flagged for DDoS/abuse (affects finviz, g2, and others in waves lasting hours to days); the ban is domain-scoped not IP-scoped. Avoid: skip jina entirely for these domains, go straight to Tier 3 bare curl.

- **defuddle connection timeout** → root cause: defuddle is a third-party single point of failure that goes down without notice. Avoid: set a short timeout (`curl --max-time 10`) and move to Tier 3 immediately on timeout, do not retry.

- **jina/defuddle return 200 but body is a login wall** → root cause: the proxy fetches the redirect destination and returns whatever HTML it gets, including auth gates. The HTTP status is 200 because the proxy itself succeeded. Avoid: always check body content, not just HTTP code. See `rules/routing.md` §"陷阱：`r.jina.ai` 的全局 abuse ban" for domain-level guidance.

- **bare curl returns raw HTML with heavy JS** → root cause: SPA pages have no meaningful SSR content; `<body>` contains only a `<div id="app">` shell. Avoid: if bare curl output is < 300 chars of visible text, stop and tell the user this URL requires browser rendering (Layer 3 byob).

- **`head -c 8000` truncates mid-word or mid-link** → this is intentional and acceptable for most use cases. If the user needs full content (translation, archiving), re-run without `head -c 8000` and warn about context size before inlining.
