---
name: name-generator
description: Generate product/project naming candidates with domain availability assessment. Trigger when user says "give me name ideas", "help name my product/project", "generate names for", "come up with a name", or "what should I call". Produces a structured shortlist with domain signals for the user to choose from.
---

## When To Use

This skill activates when the user needs naming candidates for a new product, project, startup, tool, or feature. It does NOT trigger for renaming existing things (handle that inline) or for personal names/brand aliases.

## Not For (Boundary Declaration)

- Renaming existing products with established user bases — the switching cost analysis outweighs naming creativity; handle inline
- Single-word domain snipes where user already has a name and just wants to check one specific domain — use `whois` or `dig` directly
- Naming a character, persona, or fictional entity — no domain constraint applies, skip the domain phase
- Legal trademark search — this skill surfaces domain signals only; trademark clearance requires a lawyer

## Pre-flight: Gather Context First

Before generating anything, collect these inputs in a single message if not already provided:

1. **What it does** — one sentence, plain language (no buzzwords)
2. **Target audience** — who uses it, and roughly where (global / EN / CN / niche community)
3. **Vibe** — pick 1-2: playful / serious / technical / poetic / minimal / bold / approachable / premium
4. **Hard constraints** — max syllables, must-avoid words, must-have language (EN only / bilingual / etc.)
5. **Domain TLDs cared about** — default: `.com` primary; note if `.io`, `.ai`, `.co`, `.app` or country TLDs matter

If the user has already provided enough context, skip straight to generation. Do not ask twice.

## Workflow

### Step 1 — Generate 12-15 Raw Candidates

Produce candidates across these four buckets (3-4 per bucket). Each bucket serves a different naming strategy:

**A. Descriptive compounds** — combine what-it-does words into something readable (`TaskFlow`, `DataBridge`, `SwiftDeploy`)

**B. Invented / portmanteau** — blend or truncate real words into a new word that still feels pronounceable (`Zapier`, `Figma`, `Loom` style: short, 1-2 syllables, vowel somewhere)

**C. Metaphor / concept** — pick a metaphor that fits the product's core feeling (`Compass`, `Anchor`, `Forge`, `Prism` style: one concrete noun with the right connotation)

**D. Abstract / sonic** — names chosen for how they sound and look rather than meaning (`Notion`, `Linear`, `Vercel` style: short, clean, ends consonant or soft vowel, easy to Google)

For each candidate write one line explaining the reasoning. Do not pad.

### Step 2 — Domain Signal Check

For each candidate, run a basic availability probe. Use `whois` via bash or a dig check. The signal is binary per TLD:

```bash
# Check .com availability signal (NXDOMAIN = likely available, NOERROR = registered)
dig +short <name>.com | wc -l
# 0 lines → likely unregistered (not guaranteed — always verify at registrar)
# >0 lines → registered
```

Run checks in parallel for speed:

```bash
# Good — parallel checks
for name in NameA NameB NameC; do
  dig +short ${name}.com | wc -l | awk -v n="$name" '{print n, ($1>0 ? "TAKEN" : "maybe-free")}' &
done
wait
```

```bash
# Bad — sequential, slow
dig +short NameA.com
dig +short NameB.com
# ... one at a time
```

DNS probe is a fast filter only. "maybe-free" means no A/NS record — the domain may still be registered with no DNS set up. Tell the user to confirm at a registrar before acting on it.

### Step 3 — Produce the Decision Table

Output a markdown table with exactly these columns:

| Name | Bucket | .com | Other TLDs | Score | Notes |
|------|--------|------|-----------|-------|-------|

**Score** is a 1-5 integer, assessed on four axes (equal weight):
- **Memorability**: Can someone who heard it once repeat it correctly? Short, distinct, no silent letters.
- **Clarity**: Does it give a hint toward the product space without being too on-the-nose?
- **Googleability**: Is it unique enough that a search would surface the product, not noise?
- **Domain picture**: Is `.com` or a strong alt TLD available or at least plausible?

Score = average of four axes, rounded to nearest integer. Write the per-axis breakdown in Notes only when the score is 2 or 5 (outliers worth explaining).

Then add a **Top 3 picks** block below the table — one sentence each on why, not a bulleted list.

### Step 4 — Present and Pause

After the table and Top 3, stop. Do not move to step 5 until the user responds.

Ask one focused question:
> "Which of these resonates, or should I explore a different direction / vibe / length?"

### Step 5 — Iterate on Chosen Direction

If the user picks a name: confirm domain signal, suggest 2-3 close variants (different suffix, slight spelling tweak), done.

If the user picks a direction but not a name: generate 8-10 more candidates narrowed to that bucket/vibe, re-run the table, pause again.

If none resonate: ask what specifically felt off (too corporate / too playful / sounds like something else / wrong length), then regenerate with that constraint baked in.

## Output Contract

The decision table is the primary artifact. It must:
- Have every candidate from Step 1 present (no silent dropping)
- Show actual DNS probe result, not a guess — if the probe fails, write `probe-failed` and say so
- Use consistent column order; do not rename columns between iterations
- Be the only table in the response — no second "runner-up" table below it

Scores are integers 1-5. Do not use decimals. Do not use emoji in the Score column.

## Rules

**On generation**: Avoid filler words that have lost meaning — `smart`, `go`, `my`, `easy`, `pro`, `hub`, `ly` suffix unless it genuinely fits the vibe. If you use one, justify it in Notes.

**On domain signals**: Never say a domain "is available" — say "DNS probe shows no record; verify at registrar." The difference matters because parked domains and Cloudflare-proxied domains often have no A record.

**On names in other languages**: If the audience is global or CN-inclusive, flag any English name that has an unintended meaning in Mandarin. Do the check; don't assume.

**On length**: Default target is 1-2 syllables for the core word. 3 syllables are acceptable if the rhythm is strong. 4+ syllables are almost always wrong for a product name — flag any candidate over 3.

**On iteration depth**: Maximum 3 rounds of iteration before asking the user if they want to step back and redefine the vibe/constraints entirely. Iterating on a bad brief in circles wastes time.

## Gotchas

> Only real failures observed during execution, not general advice.

- **`dig` not available in some sandboxed environments** → fallback: `nslookup <name>.com 2>&1 | grep -c 'Address'` — zero count = likely unregistered. If both fail, write `probe-failed` in the table and note the environment issue.
- **Short dictionary words almost always have .com taken** — `forge.com`, `arc.com`, `prism.com` are gone. For Bucket C (metaphor/concept) candidates, default to checking `.io`, `.app`, `.co` as primary TLDs, not `.com`.
- **Invented words that look pronounceable in English can be hard to say in other languages** — `Vrello`, `Xmit`, `Qlio` — if the audience is non-English, run a quick "how would a Spanish/Mandarin speaker say this" check before including it in Top 3.
- **DNS NXDOMAIN is not a purchase signal** — dropped/expired domains can briefly return NXDOMAIN while still in redemption period. If a candidate clears DNS and the user wants to move on it, recommend checking at a registrar with WHOIS detail, not just the probe result.
