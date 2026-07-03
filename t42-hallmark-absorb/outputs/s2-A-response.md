Reading this as: **brand-new consumer landing (品牌/营销落地页)** for **coffee-curious buyers deciding whether to trust an unknown roaster with their money**, with a **industrial-editorial, ember-and-charcoal** language, leaning toward **native CSS + serif/mono/sans type trio, no framework**.

Dial: VARIANCE 8 / MOTION 6 / DENSITY 3 (品牌营销页基线，偏高破格因为品类里"温暖咖啡棕+拿铁拉花照片"是训练数据概率中心，需要更大幅度才能推开)。

## The one idea

Emberline's whole pitch is a refusal: everyone else in small-batch coffee moved to electric drums with profiling software — load a curve, walk away, get an identical batch every time. Emberline kept the gas flame and the cast iron on purpose. So the page is built around **the roast curve as the hero graphic** — not a bag of beans, not a latte, not a founder photo. An SVG temperature readout (charge → yellowing → first crack → drop, real-ish temps and timestamps) sits where a lifestyle photo would normally go, and it draws itself in on load like an instrument warming up. That's the thing this page should be remembered for: it reads like a roast log, not a coffee-shop menu.

Everything else — the "no roast software" spec strip, the process section broken into the same four stages, the ticket-styled subscription block — reinforces that one refusal instead of introducing new decorative ideas.

## What I excluded and why

- **No hero photography / lifestyle imagery** — none was supplied, and per the rules a fabricated "artisan roaster at work" stock-photo stand-in would be exactly the AI-slop move this brief is trying to avoid. The roast-curve SVG carries the hero instead — it's real content (the brand's actual technical stance), not decoration.
- **No customer testimonials** — Emberline is a brand-new studio with no real customers yet. Inventing quotes with fake names would violate the no-fabricated-social-proof rule, so the page leans harder on process and product instead of manufacturing trust signals it hasn't earned.
- **No custom/hosted display font** — brief requires zero external dependencies, so I didn't fake a Fraunces/Cabinet-Grotesk look with a web font. Instead the personality comes from contrast between three system-safe voices: Georgia-based serif for headlines/pull-quotes, system sans for body, and a monospace stack for all data (temps, prices, specs) — the mono voice doubles as the "technical readout" motif carried through the whole page.
- **No icon/illustration for the studio section** — a hand-drawn line-art "roastery" icon would be exactly the decorative-SVG-illustration pattern the ruleset flags. Used a large low-opacity typographic watermark ("Portland, OR") instead — ornament made of type, not iconography.
- **No centered hero, no repeated card grids** — hero is an asymmetric split (headline+CTA left, roast chart right); the four page sections after it use four different layout families (editorial split-quote, divide-y list with one featured row, four-column stage timeline, paper-inverted "ticket" block) so no layout repeats per the section-family rule.
- **Single accent color** — one desaturated ember orange (`hsl` ≈ 16°, ~64% sat, contrast-checked ≥4.5:1 on both the dark and paper backgrounds), used only for the roast curve, price, and interactive states. No second accent color anywhere.

## Content specifics (all invented but concrete, per brief)

- Philosophy: direct-fire, 12kg cast-iron drum batches, no PID/no profiling software, hand-tracked by probe + ear.
- Winter lineup, 4 lots: Guji Natural micro-lot ($23/12oz, featured), Yirgacheffe Kochere ($22), Huila Reserve ($19), Cerrado Mineiro ($17) — each with origin, elevation, process, tasting notes, roast level, roast loss %.
- Roast stages with real-ish timestamps/temps: Charge 0:00/204°C → Yellowing 4:30/160°C → First Crack 9:15/196°C → Drop 11:40/218°C.
- Subscription ("The Standing Order"): $68/quarter, 4 shipments/year on solstice/equinox, two 12oz bags of the roaster's seasonal pick, cancel anytime.
- Studio info: 2214 SE Division St, Portland OR 97202 (roasting floor, no walk-in retail), roasts Tue/Fri, ships within 48h of roast via USPS, free Thursday bike-courier delivery inside Portland city limits.
- CTAs use `mailto:order@emberlinecoffee.com` with pre-filled subject lines — a real, working action for a one-page brochure site with no backend, rather than a dead `href="#"`.

## Build notes

Single HTML file, inline CSS, system font stacks only (Georgia / -apple-system / ui-monospace with fallbacks), no build step, no external requests. Motion budget: one entrance sequence (hero + roast-curve path draws in via `getTotalLength()`), scroll-triggered reveals on every section plus a draw-in progress line in the Process section, and standard interactive states (button hover/active/focus-visible, bean-row hover). All motion is transform/opacity only and degrades cleanly under `prefers-reduced-motion`. Grid-based responsive layout (no flex-percent math), 44px minimum touch targets, focus-visible outlines on every interactive element, and contrast-checked type (body ≥6.7:1, accent-on-dark ≥6.9:1, accent-on-paper ≥5.2:1 — all comfortably above the 4.5:1/3:1 gates).

I did one self-review pass after the first draft: fixed an invalid `dt`/`dd` markup issue in the studio section (was missing the wrapping `<dl>`) so the description-list semantics are correct for assistive tech. I wasn't able to get a live browser screenshot in this session (the shared Chrome DevTools profile was locked by a concurrent session), so this pass was a careful manual read-through of the markup/CSS rather than a rendered visual QA — worth a quick look in an actual browser before this goes live, particularly the hero split and the ticket layout at the 760–960px range where several breakpoints land close together.

File: `/Users/edon/Projects/personal/ab-test/t42-hallmark-absorb/outputs/s2-A.html`
