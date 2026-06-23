---
name: md-to-pdf
description: Convert a Markdown file to a clean, well-typeset PDF. Triggers when the user says "export to PDF", "convert to PDF", "generate PDF from markdown", or provides a .md file and asks for a PDF output.
---

## Pre-flight Check (REQUIRED)

Before running, verify the required tool is available:

```bash
which pandoc && pandoc --version | head -1 || echo "MISSING"
```

If pandoc is **not installed**, **MUST stop** and tell the user:

```bash
brew install pandoc
# Also install a LaTeX engine for PDF rendering:
brew install --cask basictex
# After install, add to PATH:
eval "$(/usr/libexec/path_helper)"
```

Do **NOT** fall back to other tools (wkhtmltopdf, puppeteer, etc.) without telling the user — the output quality differs significantly.

## Workflow

### Step 1 — Resolve inputs

Collect two things before running anything:

1. **Source file** — absolute path to the `.md` file. If the user gave a relative path, resolve it: `realpath <path>`.
2. **Output path** — default is same directory as source, same filename, `.pdf` extension. Ask only if the user specified a different location.

```bash
INPUT="/absolute/path/to/input.md"
OUTPUT="${INPUT%.md}.pdf"
```

### Step 2 — Choose rendering engine

Pick based on what's installed and what the user needs:

| Scenario | Engine | Flag |
|----------|--------|------|
| Default (clean, reliable) | pdflatex via pandoc | *(default)* |
| CJK characters (Chinese/Japanese/Korean) | xelatex | `--pdf-engine=xelatex` |
| Web-style layout (CSS-driven) | weasyprint or wkhtmltopdf | `--pdf-engine=weasyprint` |

**Good** — detecting CJK content before choosing engine:
```bash
grep -qP '[\x{4e00}-\x{9fff}]' "$INPUT" && ENGINE="--pdf-engine=xelatex" || ENGINE=""
```

**Bad** — always using pdflatex when file contains Chinese:
```bash
pandoc "$INPUT" -o "$OUTPUT"   # will produce garbled output or fail on CJK
```

### Step 3 — Run conversion

**Standard (no CJK):**
```bash
pandoc "$INPUT" \
  -o "$OUTPUT" \
  --variable geometry:margin=1in \
  --variable fontsize=12pt \
  --variable linestretch=1.4 \
  --highlight-style=tango \
  --standalone
```

**With CJK (xelatex):**
```bash
pandoc "$INPUT" \
  -o "$OUTPUT" \
  --pdf-engine=xelatex \
  --variable CJKmainfont="PingFang SC" \
  --variable geometry:margin=1in \
  --variable fontsize=12pt \
  --variable linestretch=1.4 \
  --highlight-style=tango \
  --standalone
```

### Step 4 — Verify output

```bash
[ -f "$OUTPUT" ] && ls -lh "$OUTPUT" || echo "ERROR: PDF not created"
```

Check that file size is > 1 KB. A file that exists but is 0–100 bytes means pandoc silently failed — read stderr carefully.

**Output contract**: the PDF is at `$OUTPUT`. Report the absolute path to the user. Do not open it automatically.

## Options Reference

Pass these as additional flags when the user requests them explicitly:

| User request | Flag to add |
|-------------|-------------|
| "Use a custom template" | `--template=/path/to/template.tex` |
| "Add a table of contents" | `--toc --toc-depth=3` |
| "Numbered sections" | `--number-sections` |
| "Include bibliography / citations" | `--citeproc --bibliography=/path/to/refs.bib` |
| "Wider/narrower margins" | `--variable geometry:margin=0.75in` |
| "Different font" | `--variable mainfont="Georgia"` (xelatex only) |
| "Syntax highlighting style" | `--highlight-style=pygments` (options: pygments, kate, monochrome, espresso, zenburn, haddock, tango) |

Do **not** add options the user did not request. Default output should be clean and readable without customization.

## Not Applicable (When to Use Something Else)

- **User wants HTML output** → skip this skill entirely, use `pandoc "$INPUT" -o output.html --standalone`
- **User wants editable Word/DOCX** → use the `/docx` skill
- **User wants a designed poster / infographic** → use `/baoyu-infographic`; pandoc PDF is for document-style content, not visual compositions
- **Source is already PDF, user wants to modify it** → use the `/pdf` skill (pypdf/pdfplumber)
- **User needs pixel-perfect CSS layout** (e.g. matching a brand stylesheet) → weasyprint with a custom CSS file is better than LaTeX; this workflow supports it via `--pdf-engine=weasyprint --css=style.css`

## Rules

- Always output the absolute path of the generated PDF.
- Never modify the source `.md` file.
- If pandoc exits with a non-zero code, show the full stderr to the user — do not summarize or hide it.
- CJK detection is mandatory before picking the engine. Do not assume the file is ASCII.
- If the user gave a filename without a path (e.g. `report.md`), ask for the directory or resolve relative to cwd using `pwd`.

## Gotchas

> Only real failures that have been root-caused.

- **`pdflatex` not found after `basictex` install** → root cause: BasicTeX installs to `/Library/TeX/texbin/` which is not in `$PATH` until `eval "$(/usr/libexec/path_helper)"` is run in the current shell → fix: run `export PATH="/Library/TeX/texbin:$PATH"` before calling pandoc, or open a new terminal
- **CJK characters render as boxes or cause compile error** → root cause: default pdflatex engine has no CJK font support → fix: always use `--pdf-engine=xelatex` + `--variable CJKmainfont="PingFang SC"` when source contains Chinese/Japanese/Korean
- **PDF created but is 2–3 KB and visually blank** → root cause: LaTeX compilation error was swallowed; pandoc exited 0 but wrote an empty shell → fix: always check file size after generation; re-run with `--verbose` to see LaTeX log
- **Unicode math symbols (∑, →, ≥) disappear in pdflatex** → root cause: pdflatex requires explicit LaTeX math mode; pandoc converts them only with `--mathml` or when xelatex is used → fix: switch to xelatex engine
- **Output file permission denied** → root cause: output path is inside a TCC-protected directory (Desktop, Documents) when running via a sandboxed agent → fix: write to `/tmp/` or `~/Developer/` instead, then show the user the path
