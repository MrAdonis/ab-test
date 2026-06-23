---
name: md-to-pdf
description: Convert a Markdown file to a clean, print-ready PDF. Triggers when the user says "convert to PDF", "export as PDF", "生成 PDF", or points at a .md file and asks for a PDF output.
---

## Pre-flight Check (REQUIRED)

Before running any conversion, verify the input file exists:

```bash
[ -f "$MD_FILE" ] && echo "ok" || echo "FILE NOT FOUND"
```

If the file does not exist, **MUST stop and ask the user for the correct path**. Do **NOT** guess a fallback path or fabricate the file.

Also check that at least one PDF engine is available:

```bash
command -v pandoc >/dev/null && echo "pandoc ok" || \
command -v weasyprint >/dev/null && echo "weasyprint ok" || \
echo "NO ENGINE — install pandoc or weasyprint"
```

If no engine is found, stop and tell the user to run `brew install pandoc` (preferred) or `pip install weasyprint`.

## Workflow

### Step 1 — Resolve paths

Confirm:
- `$MD_FILE`: absolute path to the input `.md` file
- `$OUT_PDF`: output path — default is same directory as input, same stem, `.pdf` extension

```bash
MD_FILE="/absolute/path/to/input.md"
OUT_PDF="${MD_FILE%.md}.pdf"
```

### Step 2 — Choose engine

Use **pandoc** if available; fall back to **weasyprint** only if pandoc is missing.

**Good — pandoc (preferred):**
```bash
pandoc "$MD_FILE" \
  -o "$OUT_PDF" \
  --pdf-engine=xelatex \
  -V geometry:margin=2cm \
  -V mainfont="Helvetica Neue" \
  -V fontsize=11pt \
  --highlight-style=tango
```

**Fallback — weasyprint (no LaTeX required):**
```bash
# Step 1: convert MD → HTML
pandoc "$MD_FILE" -o /tmp/_md2pdf_temp.html --standalone --self-contained
# Step 2: HTML → PDF
weasyprint /tmp/_md2pdf_temp.html "$OUT_PDF"
rm /tmp/_md2pdf_temp.html
```

**Bad — do not use:**
```bash
# Bad: wkhtmltopdf is deprecated and produces inconsistent output on macOS
wkhtmltopdf "$MD_FILE" "$OUT_PDF"

# Bad: markdown-pdf npm tool silently fails on non-ASCII headers
npx markdown-pdf "$MD_FILE"
```

### Step 3 — Verify output

```bash
[ -f "$OUT_PDF" ] && \
  echo "PDF written: $OUT_PDF ($(du -h "$OUT_PDF" | cut -f1))" || \
  echo "FAILED: output file not found"
```

**A non-zero exit code from pandoc does not guarantee failure** — always check that `$OUT_PDF` exists and has non-zero size. An empty PDF (< 2 KB) means pandoc ran but the content was not rendered.

### Step 4 — Report to user

Tell the user:
- Absolute path to the output file
- File size
- Engine used
- Any warnings printed to stderr (font substitution warnings are common and usually harmless)

## Common Options

| Goal | Flag to add |
|------|-------------|
| Chinese / CJK content | `--pdf-engine=xelatex -V CJKmainfont="PingFang SC"` |
| Custom CSS (weasyprint path) | skip pandoc; use `weasyprint` with a `-s style.css` flag |
| Include table of contents | `--toc --toc-depth=3` |
| Syntax highlighting off | `--no-highlight` |
| Landscape orientation | `-V geometry:landscape` |
| Letter paper (US) | `-V papersize=letter` (default is A4) |

## Typography Rules

These apply when the user does not specify a custom style. Do not invent values; these are derived from standard print typography:

- Margin: 2 cm all sides (ISO 216 A4 safe zone)
- Body font size: 11 pt (book body standard; 10 pt is the minimum for comfortable print reading — Bringhurst, *Elements of Typographic Style*)
- Line height: pandoc/LaTeX default (≈1.2–1.4× for LaTeX, adequate for body text)
- Code blocks: monospace, highlighted — do not strip syntax highlighting unless the user asks
- Page numbers: not added by default; add `-V pagestyle=plain` to enable

[Cannot quantify] Heading hierarchy should feel visually distinct — pandoc's default LaTeX heading sizes (section / subsection / subsubsection) are adequate; do not override unless the user provides a custom template.

## Not Applicable Here

This skill converts a single Markdown file to a single PDF. It does **not**:

- Merge multiple Markdown files (use `cat *.md | pandoc -o out.pdf` manually)
- Apply custom branding / logos — go to `/paper-layout` for that
- Generate slide decks — go to `/pptx` or `reveal.js` for that
- Handle Word `.docx` input — go to `/docx`
- Produce interactive HTML — this is a print/PDF pipeline only

## Gotchas

> Only confirmed failures with root-cause diagnosis.

- **CJK characters render as boxes or are missing** → root cause: pandoc defaults to pdflatex which has no CJK font support → fix: switch to `--pdf-engine=xelatex` and add `-V CJKmainfont="PingFang SC"` (macOS) or `"Noto Sans CJK SC"` (Linux)

- **`xelatex` not found even after installing pandoc** → root cause: pandoc ships without a TeX distribution; xelatex comes from MacTeX or TeX Live → fix: `brew install --cask mactex-no-gui` (installs ~600 MB); use weasyprint fallback if disk space is constrained

- **Output PDF is 0 KB or < 2 KB** → root cause: pandoc exited 0 but LaTeX failed silently on a malformed table or math block → fix: re-run with `--verbose` and check the LaTeX log in `/tmp/`; simplify the offending block

- **Weasyprint font warnings flood stderr** → root cause: weasyprint tries to load system fonts and logs every miss → these are harmless; only flag if the output PDF is visually broken

- **Relative image paths in Markdown break** → root cause: pandoc resolves images relative to the CWD, not the input file's directory → fix: always `cd` to the input file's directory before running, or use `--resource-path="$(dirname "$MD_FILE")"`
