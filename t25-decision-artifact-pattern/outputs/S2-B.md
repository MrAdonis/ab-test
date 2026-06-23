---
name: name-generator
description: Generate naming candidates for a new product or project, including domain availability checks, so the user can pick from a curated shortlist. Trigger when the user says "help me name", "generate names", "find a name for", "naming candidates", "domain check", or describes starting a new product/project and needs a name.
---

# Name Generator

Produces 8–12 naming candidates for a new product or project, evaluates domain availability, and presents a comparison table so the user can pick one without extra legwork.

## When To Use

Triggered when the user needs to name something new: product, startup, tool, side project, open-source library, newsletter, or brand. The skill covers ideation, shortlisting, and domain triage in one pass.

**Not this skill** (use something else instead):

- Renaming an existing brand with established recognition → that's a rebrand strategy task; naming alone will lose context.
- Need a logo, tagline, or full brand identity system → out of scope here; hand off to design after a name is chosen.
- The project already has a name and you only need domain alternatives → skip to Step 3 directly.
- Legal trademark clearance → this skill does lightweight triage only; formal trademark search requires a lawyer or a dedicated service (USPTO, TMview).

## Inputs to Collect Before Starting

Ask for these if not already provided. Do not start generating until you have at least items 1–3:

1. **One-line description** — what does this product/project do, for whom?
2. **Tone** — pick the closest: playful / serious / techy / friendly / premium / neutral
3. **Language constraints** — English only? bilingual? coined words OK?
4. **Hard constraints** — maximum characters, must-include syllables, words to avoid
5. **Domain priority** — `.com` required, or is `.io / .app / .co / .dev` acceptable?

## Workflow

### Step 1 — Generate Raw Candidates

Produce **20 raw candidates** across these six directions. Vary direction so the shortlist is not all the same flavor:

| Direction | Description | Example pattern |
|-----------|-------------|-----------------|
| **Descriptive** | Says what it does | `TaskFlow`, `DataSync` |
| **Metaphor / Concept** | Borrows from another domain | `Anchor`, `Prism`, `Forge` |
| **Portmanteau** | Merges two meaningful roots | `Clarifai`, `Braintrust` |
| **Coined / invented** | Novel word, no prior meaning | `Vercel`, `Figma`, `Zora` |
| **Action / Verb** | Energetic, imperative feel | `Amplify`, `Relay`, `Launch` |
| **Short + Punchy** | ≤6 characters, easy to spell aloud | `Navi`, `Kern`, `Helm` |

Aim for ≥2 candidates per direction. Do not filter yet.

### Step 2 — Shortlist to 8–12

Apply these filters in order to trim the 20 raw candidates:

1. **Pronounceable** — a native speaker of the target language can say it without coaching.
2. **Spellable from sound** — if someone hears the name, they can type it correctly on the first try (no ambiguous double-letters or homophones that map to wrong spellings).
3. **Memorable** — ≤3 syllables preferred; unusual phoneme combination or strong consonant helps recall.
4. **No obvious collision** — quick mental check: does this name strongly evoke a known brand, a negative connotation, or an inappropriate word in a major language? If yes, drop.
5. **Domain plausibility** — does a plausible domain form exist (even if not yet confirmed available)? `.com` / `.io` / `.app` / `.co` / `.dev` all count.

Retain 8–12 survivors. **Default is 10.** Fewer than 6 doesn't give meaningful choice; more than 12 causes decision fatigue (Nielsen, 1994 — cognitive load increases non-linearly beyond ~7 options).

### Step 3 — Domain Availability Triage

For each shortlisted name, check domain availability using `whois` or a DNS probe:

```bash
# Quick DNS probe — NXDOMAIN = likely available, resolves = taken
for name in name1 name2 name3; do
  host "${name}.com" 2>/dev/null | grep -q "NXDOMAIN" \
    && echo "${name}.com — likely AVAILABLE" \
    || echo "${name}.com — TAKEN or resolves"
done
```

Check at minimum: `.com`. If `.com` is taken, also check `.io`, `.app`, `.co`, `.dev` for that name.

Mark each name with one of three statuses:

- **✅ Available** — DNS returns NXDOMAIN for .com (or preferred TLD)
- **⚠️ Taken (.com)** — .com resolves; note which alternative TLDs are free
- **❌ All major TLDs taken** — .com / .io / .app / .co / .dev all resolve

> DNS probe is a lightweight signal, not a purchase guarantee. Registrar confirmation before buying is the user's responsibility.

### Step 4 — Comparison Table (the main deliverable)

Present all shortlisted names in a single markdown table. This is the artifact the user reads to make their decision — do not scatter names across paragraphs.

**Required columns:**

| Name | Domain Status | Direction | Syllables | Notes |
|------|--------------|-----------|-----------|-------|
| Prism | ✅ prism.io available | Metaphor | 2 | Strong visual connotation; works for analytics, design, or optics-adjacent products |
| Forgekit | ⚠️ .com taken; forgekit.io ✅ | Portmanteau | 3 | "Kit" signals toolbox; "Forge" implies craftsmanship |
| Navi | ❌ all major TLDs taken | Short+Punchy | 2 | Clean; known from gaming (Legend of Zelda) — could be asset or liability |

Notes column: one sentence max. Say what the name implies and flag any risk.

### Step 5 — Stress-Test Pass

Before handing off, run each ✅ / ⚠️ name through the three most common real-world failure modes for product names:

1. **Verbal clarity** — say it aloud in a sentence: "I'm using [Name] to…". Does it sound natural or awkward?
2. **Email / handle truncation** — does a 20-character truncation (e.g., `hello@[name].com`) still read correctly, or does it cut mid-word into something weird?
3. **Pluralization / verb form** — "I [name]d it", "[name]ing", "[name]s" — do these feel usable or forced?

Flag any name that fails two or more stress-test items with a ⚠️ in the Notes column.

### Step 6 — Present and Wait

Output the comparison table and stress-test notes. Then stop and ask:

> "Which number(s) do you want to explore further, or should I swap out any directions and regenerate?"

**Do not register a domain, create accounts, or take any production action before the user selects a name.**

## Output Format

```
## Name Candidates for [Product Description]

[Comparison table — Step 4]

### Stress-Test Notes
[Any flags from Step 5, one line each]

### Next Steps
Once you pick a name:
- Confirm domain availability via registrar (Cloudflare Registrar / Namecheap)
- Check @[name] handle availability on relevant social platforms
- Optional: lightweight trademark search on USPTO.gov or TMview.org
```

## Rules

- **Candidate count**: default 10, minimum 6, maximum 12. Never produce a number outside this range unless the user explicitly overrides.
- **One table, not N files**: all candidates appear in a single comparison table. Do not create separate files per candidate.
- **Statuses are tri-state**: ✅ / ⚠️ / ❌ only. Do not write "probably available" in prose — put it in the Status column with the correct symbol.
- **No production actions before selection**: do not purchase domains, create GitHub repos, register accounts, or write config files until the user explicitly picks a name and asks you to proceed.
- **Direction diversity**: the shortlist must contain candidates from ≥4 distinct directions (see Step 1 table). A table of 10 descriptive names is a bad shortlist.
- **Notes ≤ 1 sentence per name**: the table is for scanning, not reading. Longer analysis belongs outside the table.

## Gotchas

> Only real failures recorded here. No hypothetical warnings.

- **`whois` rate-limits on rapid sequential calls** → use the DNS probe (`host` / `dig`) instead of `whois` for bulk checks; `whois` is fine for confirming a single name.
- **NXDOMAIN ≠ definitely purchasable** → some registries park names with DNS wildcards that resolve everything; always note "confirm via registrar" in the output.
- **Portmanteau names hit trademark more than coined words** → if two real brand names are glued together (e.g., `SlackJira`), mention trademark risk explicitly in Notes.
- **Short names (≤4 chars) are almost always taken on .com** → set user expectation early; probe `.io` / `.app` / `.co` automatically for any name ≤4 characters.
