---
name: hero-palette
description: Generate multiple hero section color scheme options for a landing page so the user can pick one to use in their project. Triggers when user asks for hero color schemes, palette options, color variations, or "give me some color choices for the hero."
---

## When To Use

Trigger on: "给我几个 hero 配色方案" / "hero 区配色选项" / "来几套配色让我挑" / "hero color options" / "landing page color schemes."

Do NOT use this skill when:
- User already has a chosen color and asks to apply or tweak it → edit CSS/tokens directly, skip this skill
- Project has a `DESIGN.md` with a locked color system → read that first, check if palette generation is still needed
- User asks for the full design system (typography, spacing, components) → this skill only covers hero palette, hand off to design-system skill after selection

## Workflow

### Step 1 — Gather Context (required before generating)

Read these inputs if available. Do not ask the user to provide them; locate them yourself:

1. Project `DESIGN.md` or `tailwind.config.*` or CSS custom properties — extract any existing brand colors or forbidden combinations
2. The hero section file (HTML/JSX/Vue/Astro) — note current background, text, and CTA colors
3. Any stated brand personality in the repo (e.g., README, `about` page copy) — note adjectives like "professional," "playful," "dark," "minimal"

If none of the above exist, proceed with defaults: neutral base, no existing constraints.

### Step 2 — Generate 3–5 Named Schemes

Output exactly 3–5 schemes. Each scheme must have:

- A short personality name (e.g., "Midnight Tech," "Warm Authority," "Clean Slate")
- `bg` — hero background hex
- `text` — primary heading hex
- `subtext` — secondary/body text hex
- `cta_bg` — CTA button background hex
- `cta_text` — CTA button text hex
- `accent` — optional highlight/border/icon color hex (one value, not a range)
- `mood` — one sentence describing the emotional register

Format each scheme as a fenced code block labeled `palette:<name>` so the user can copy it directly.

**Good — structured, copyable output:**

~~~
```palette:Midnight Tech
bg:        #0A0F1E
text:      #F0F4FF
subtext:   #8B9CC8
cta_bg:    #4F6EF7
cta_text:  #FFFFFF
accent:    #7B93FF
mood:      "Focused and technical. Signals deep expertise without aggression."
```
~~~

**Bad — prose description only:**
> "A dark navy background with blue accents and white text, giving a technical feel."

Prose descriptions force the user to translate back to hex values. Always output raw values.

### Step 3 — Pause for User Selection

After presenting all schemes, output exactly this line and stop:

```
→ 选哪套？回复序号或名称，我把它写进项目。
```

Do NOT write any files, do NOT modify CSS/tokens until the user selects.

### Step 4 — Apply Selected Scheme

Once the user picks one:

1. If project has CSS custom properties: update `--color-*` or equivalent tokens in the variables file
2. If project uses Tailwind: update `theme.extend.colors` in `tailwind.config.*`
3. If neither: write a `/* Hero Palette: <name> */` comment block at the top of the hero component file with CSS variables ready to drop in
4. Do NOT change any other section's colors — scope is hero only

Confirm by listing which file(s) were changed and which hex values were written.

## Color Quality Rules

These rules apply when generating all schemes. They are constraints, not suggestions.

**Contrast (WCAG AA minimum, AAA preferred):**
- `text` on `bg`: contrast ratio ≥ 4.5:1 (AA) — verify mentally or note if uncertain
- `cta_text` on `cta_bg`: contrast ratio ≥ 4.5:1 (AA required; ≥ 7:1 = AAA preferred for primary CTA)
- `subtext` on `bg`: contrast ratio ≥ 3:1 (AA Large, acceptable for secondary text)

Basis: WCAG 2.1 §1.4.3 (Contrast Minimum) and §1.4.6 (Contrast Enhanced).

**Hue count per scheme:**
- Maximum 3 distinct hues per scheme (bg family + cta family + accent). Basis: Cleveland & McGill (1984) established that human color discrimination under attention degrades beyond 5–7 categories; for hero sections with a single focal point, 3 hues is the functional ceiling before visual competition.
- `subtext` must be a tint/shade of `text`, not a new hue.

**Saturation discipline:**
- At least one of {bg, text} must be near-neutral (saturation < 15% in HSL). Basis: Calimari Rule — high perceived quality correlates with restraint; one anchor neutral prevents "crayon" appearance.
- `accent` may be fully saturated; it is the only slot permitted to be.

**Scheme differentiation:**
- Each scheme must differ from all others by ≥ 30° on the hue wheel for `bg` OR by switching between light/dark base. Presenting five schemes with bg values clustered in the same blue family is not five options — it is one option with minor tweaks.

**What cannot be quantified (keep as text guidance):**
- Emotional coherence: `mood` should match the brand personality extracted in Step 1. A "playful" brand should not receive a monochrome gray scheme even if it passes all contrast gates.
- Brand distance: if the user's existing brand color appears in the repo, at least one scheme should incorporate it as `cta_bg` or `accent` — providing a familiar anchor.

## Output Format Summary

```
Scheme 1 — <name>
palette block (fenced)

Scheme 2 — <name>
palette block (fenced)

... up to 5

→ 选哪套？回复序号或名称，我把它写进项目。
```

No prose between schemes. No "here are your options" preamble. Start directly with Scheme 1.

## Not In Scope

This skill covers hero palette only. After the user selects, if they ask about:
- Full page color system → hand off to design-system skill
- Typography → separate task
- Illustration / imagery style → `/baoyu-infographic` or `/diagram`
- Dark mode variants → separate task (generate light scheme first, dark variant is a follow-up)

## Gotchas

> Only real failures encountered during execution. Not general best practices.

- **Generating schemes without checking existing CSS first** → produces palettes that clash with nav/footer colors already in the project. Always do Step 1 before Step 2, even if it feels like overhead.
- **Writing files before user confirms selection** → wastes a write and creates a diff the user didn't ask for. Step 3's pause is a hard stop, not a suggestion.
- **Tailwind purge eating custom hex values** → if the project uses Tailwind JIT and you write arbitrary hex values directly in JSX (e.g., `bg-[#0A0F1E]`), they purge cleanly. But if you write them only in a config comment, they won't be generated. Always update `tailwind.config.*` or use a CSS layer — not inline comments.
