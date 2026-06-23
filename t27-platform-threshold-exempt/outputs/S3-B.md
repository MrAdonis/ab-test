---
name: html-email-template
description: Generate production-ready HTML email templates. Use when asked to create, design, or convert any email into HTML — marketing emails, transactional emails, newsletters, onboarding sequences. Enforces email client compatibility constraints (600px table layout, inline CSS) and aesthetic quality thresholds simultaneously.
---

# HTML Email Template Skill

## When to Use

Triggered when the user wants to:
- Create a new HTML email template from scratch
- Convert a plain-text or design brief into a sendable HTML email
- Review or fix an existing HTML email for client compatibility

**Not for:** email sequence strategy, copywriting from zero (bring copy or at least a brief), ESP-specific drag-and-drop editors.

---

## Platform Constraints (Hard — no exceptions)

These come from email client behavior facts, not design opinion. **Do not deviate.**

| Constraint | Value | Source |
|---|---|---|
| Max content width | **600px** | Email client rendering standard — wider layouts break in Outlook and Gmail web |
| Layout method | **`<table>` only** | Flexbox/Grid/CSS floats ignored by Outlook 2016+ (Word rendering engine) |
| CSS delivery | **Inline `style=""`** | `<style>` blocks stripped by Gmail, Yahoo Mail |
| `<link>` stylesheets | **Forbidden** | External CSS not fetched in most clients |
| `width` attribute | Both `width=""` (HTML attr) AND `style="width:"` | Outlook reads HTML attribute, Gmail reads inline style — need both |
| Images | Always include `alt=""` | Images blocked by default in Outlook, many corp firewalls |
| Background color | Set on both `<body>` AND outermost `<table>` | Different clients read one or the other |

**Good — width set correctly for cross-client:**
```html
<table width="600" style="width:600px; max-width:600px;" cellpadding="0" cellspacing="0" border="0">
```

**Bad — CSS-only width, breaks Outlook:**
```html
<div style="width:600px; max-width:600px;">
```

---

## Aesthetic Thresholds (Quantified — with rationale)

### Typography

| Rule | Value | Rationale |
|---|---|---|
| Body font size | ≥ 16px | iOS Mail minimum tap-safe size; below 16px iOS auto-scales text unpredictably |
| Line height | 1.5–1.6 | Typographic convention: ~1.5× body size is optimal reading rhythm (Bringhurst) |
| Heading / body size ratio | ≥ 1.5× (e.g., 24px h1 / 16px body) | Visible hierarchy at a glance; smaller ratios blend together |
| Font weight levels | ≤ 3 distinct weights in one template | More than 3 weight levels creates visual noise without adding hierarchy |
| Font family | Web-safe stack: `Arial, Helvetica, sans-serif` or `Georgia, serif` | Custom fonts need `@font-face` which is stripped by most clients; web-safe stack is the safe fallback |

### Color

| Rule | Value | Rationale |
|---|---|---|
| Primary brand colors | ≤ 2 | Cleveland & McGill (1984): color discrimination ceiling for quick visual parsing is 5–7; email context is skim-read, ≤2 reads as intentional |
| Text-on-background contrast | ≥ 4.5:1 for body, ≥ 3:1 for large text | WCAG AA — legal baseline in many jurisdictions, also practical for dark mode |
| CTA button contrast | ≥ 7:1 | WCAG AAA — CTA is the highest-value tap target, deserves maximum legibility |
| Dark mode consideration | Add `@media (prefers-color-scheme: dark)` in `<style>` block for clients that support it (Apple Mail, iOS Mail) | These clients do support `<style>` blocks in `<head>` even though most don't |

*Note: the `<style>` block in `<head>` is used only for the dark mode media query — it will be ignored by Gmail but respected by Apple Mail/iOS. All layout-critical CSS must still be inline.*

### Spacing & Layout

| Rule | Value | Rationale |
|---|---|---|
| Minimum padding inside content cells | 20px sides | Calimari Rule: lower information density reads as higher quality; cramped = cheap |
| Section spacing | ≥ 24px vertical gap between content blocks | Visual breathing room; less than 24px and sections merge perceptually |
| Single-column layout | Default | Multi-column works only above ~480px width; mobile renders single-column anyway — start there |
| Max content blocks per email | ≤ 5 distinct sections | More than 5 = reader loses the thread; each section must earn its place |

**[Cannot be quantified — kept as text]**
Hierarchy legibility: the single most important piece of information in the email (the CTA or the core message) must be visually dominant. If a reader glances for 2 seconds, they should immediately know what you want them to do. Avoid designs where headline, subheadline, body, and CTA all look equally weighted.

---

## Workflow

### Step 1 — Gather input
Collect from user (ask if missing):
- **Purpose**: transactional (receipt, reset password) / marketing (promo, newsletter) / onboarding
- **Brand colors** (hex values) or "use defaults"
- **Copy**: subject, headline, body text, CTA label + URL
- **Logo**: URL or "no logo"
- **Tone**: formal / friendly / minimal

### Step 2 — Build structure with correct table skeleton

Always use this outer wrapper:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{{subject}}</title>
  <style>
    /* Only dark mode overrides here — all other CSS must be inline */
    @media (prefers-color-scheme: dark) {
      .email-body { background-color: #1a1a1a !important; }
      .content-cell { background-color: #2d2d2d !important; }
      .body-text { color: #e0e0e0 !important; }
    }
  </style>
</head>
<body class="email-body" style="margin:0; padding:0; background-color:#f4f4f4;">
  <!-- Preheader (hidden preview text) -->
  <div style="display:none; max-height:0; overflow:hidden;">{{preheader_text}}</div>

  <!-- Outer wrapper table -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f4f4;">
    <tr>
      <td align="center" style="padding:20px 0;">

        <!-- Content table — the 600px container -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="width:600px; max-width:600px; background-color:#ffffff;">
          <!-- Content rows go here -->
        </table>

      </td>
    </tr>
  </table>
</body>
</html>
```

### Step 3 — Build sections as `<tr>` rows

Each content block (header, body, CTA, footer) is a separate `<tr>` inside the 600px table.

**Good — CTA button built with table for Outlook:**
```html
<tr>
  <td align="center" style="padding:32px 40px;">
    <table cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td align="center" bgcolor="#0066FF" style="border-radius:4px;">
          <a href="{{cta_url}}"
             style="display:inline-block; padding:14px 32px; font-family:Arial,Helvetica,sans-serif;
                    font-size:16px; font-weight:bold; color:#ffffff; text-decoration:none;">
            {{cta_label}}
          </a>
        </td>
      </tr>
    </table>
  </td>
</tr>
```

**Bad — CSS-only button, ghost in Outlook:**
```html
<div style="background:#0066FF; border-radius:4px; padding:14px 32px;">
  <a href="{{cta_url}}" style="color:#ffffff;">{{cta_label}}</a>
</div>
```

### Step 4 — Apply aesthetic thresholds

Run through the thresholds checklist before outputting:

- [ ] Body font ≥ 16px, line-height 1.5–1.6
- [ ] Heading at least 1.5× body size
- [ ] ≤ 2 primary colors
- [ ] Body contrast ≥ 4.5:1, CTA contrast ≥ 7:1
- [ ] Side padding ≥ 20px in content cells
- [ ] Section gaps ≥ 24px
- [ ] CTA is visually dominant — is it the most prominent element?

### Step 5 — Output

Deliver the complete HTML as a single fenced code block. Include:
1. Full HTML with inline styles on every element
2. A short plain-text fallback version (5–8 lines) the user can paste into the ESP's plain-text field

---

## Gotchas

> Only real failures documented here — not general best practices.

- **Outlook renders `border-radius` on `<td>` but ignores it on `<div>`** → Always apply `border-radius` on `<td>` elements, not wrapper `<div>`. VML round-corner workaround only needed for MSO Outlook desktop if you need guaranteed rounded buttons.

- **`max-width` alone doesn't constrain in Outlook 2016+** → Outlook's Word renderer ignores `max-width`. Must set both the `width=""` HTML attribute AND `style="width:..."` on the table. Missing either breaks desktop Outlook layout.

- **`padding` shorthand on `<td>` breaks Outlook** → Use `padding-top`, `padding-right`, `padding-bottom`, `padding-left` as separate properties, or use `style="padding:20px 40px"` which Outlook parses correctly. The actual failure mode is with 3-value shorthand `padding:20px 40px 10px` — Outlook misreads it.

- **`display:none` preheader text shows in some clients if it's too long** → Keep preheader under 100 characters including spaces. Some clients show text after the hidden preheader up to their character limit, which can bleed visible copy.

- **Dark mode `!important` overrides can fight inline styles** → Use `!important` only in the `@media (prefers-color-scheme: dark)` block. Never put `!important` on inline styles — it breaks the media query override mechanism.

- **Gmail clips emails over ~102KB** → The full email HTML must stay under 102KB. If template is data-heavy (lots of product cards), strip comments, minimize whitespace in final output.
