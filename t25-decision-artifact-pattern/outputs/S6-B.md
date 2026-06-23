---
name: refactor-plan
description: Analyze a codebase and produce a prioritized refactoring plan with concrete recommendations. Triggers when the user says "重构建议", "refactor plan", "分析代码库", "代码健康度", "技术债", or asks for an architectural review of existing code.
---

# Refactor Plan Skill

## Scope & Self-Exclusion

Use this skill when the goal is **diagnosis + prioritized recommendations** on existing code.

Do NOT use this skill (use something else instead):
- Single-file cleanup or lint fix → just edit the file directly
- Greenfield design (no existing code to analyze) → `/grill-me` + `/plan`
- Performance profiling only (no structural change needed) → `/web-perf` or `/diagnose`
- User already has a plan and just wants implementation → skip to coding

## Phase 1 — Understand the Codebase

Before writing any recommendations, run the project index and gather facts. Do NOT skip this phase.

```bash
# Get structure overview
~/.claude/scripts/project-index.sh 2>/dev/null || (find . -type f | grep -v node_modules | grep -v .git | head -80)

# Recent activity signals: what's been touched most?
git log --since="90 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -30

# Identify test coverage presence
find . -type f \( -name "*.test.*" -o -name "*.spec.*" -o -name "__tests__" \) | head -20

# Dependency health
cat package.json 2>/dev/null || cat pyproject.toml 2>/dev/null || cat go.mod 2>/dev/null | head -60
```

Read the following before forming any opinion:
1. Entry points (main file, router, index)
2. The 3-5 most-changed files from the git log above
3. Any existing `CLAUDE.md`, `README.md`, or architecture docs
4. Test files, if any exist

**Do NOT write recommendations yet.** Finish Phase 1 first.

## Phase 2 — Identify Issues

After reading, categorize findings into these four axes. Every finding must map to exactly one axis:

| Axis | What it covers |
|------|---------------|
| **Structure** | Module boundaries, circular deps, god classes/files, missing seams |
| **Coupling** | Hidden dependencies, shared mutable state, untestable code |
| **Consistency** | Naming conventions, duplicate logic, mixed paradigms |
| **Risk** | Security surface (see appsec check below), dead code, no tests on critical paths |

For each finding, record:
- Observable symptom (what you can see in the code, not what you assume)
- File + approximate line range
- Estimated blast radius if left unaddressed (low / medium / high)

**Appsec check (mandatory if any of these are present):**
- User input flows (forms, URL params, file uploads)
- Auth / session / permission checks
- Output sinks (HTML render, SQL, shell, template engine)
- External URL fetching (SSRF surface)

If any appsec surface is present, cross-check against the relevant OWASP Cheat Sheet before writing the Risk section. Do not just write "no OWASP Top 10 issues" — name the surface and the control.

## Phase 3 — Produce the Refactoring Plan

### Candidate Set Design

Produce **3 to 5 refactoring directions** (default: 3). Fewer than 3 doesn't give the user a real choice; more than 5 creates decision fatigue for a structural plan.

Each direction must be a coherent strategy, not a grab-bag of fixes. Name it concisely (e.g., "Seam-First Extraction", "Domain Boundary Hardening", "Test-First Stabilization").

### Comparison Artifact (required)

After listing the candidates, produce a **side-by-side comparison table** so the user can pick without re-reading each section:

```
| Criterion          | Direction A        | Direction B        | Direction C        |
|--------------------|--------------------|--------------------|---------------------|
| Scope              | ...                | ...                | ...                 |
| Effort (dev-weeks) | ...                | ...                | ...                 |
| Risk during change | low / med / high   | ...                | ...                 |
| Test coverage req  | ...                | ...                | ...                 |
| Reversible?        | yes / partial / no | ...                | ...                 |
| Best if...         | ...                | ...                | ...                 |
```

### Stress-Test Artifact (required)

For each direction, explicitly state how it holds up under the **most likely failure condition** for that codebase. The stress dimension is not generic — pick the one that is most likely to cause the refactor to fail in this specific project:

- Large team + fast feature velocity → "Does this direction work without a feature freeze?"
- No tests → "Can this be done safely without a test suite?"
- Monolith with shared DB → "Does this require a data migration?"
- External API dependencies → "What breaks if an external contract changes mid-refactor?"

State the failure condition explicitly, then say whether the direction survives it (yes / partial / no) and why.

### Per-Direction Format

For each direction:

```markdown
### Direction [N]: [Name]

**Summary:** One sentence — what structural change this makes and why.

**Key moves:**
1. [Concrete action — file or module name, not abstract]
2. ...

**Effort:** [S / M / L / XL, with a rough dev-week estimate]

**Risk:** [low / med / high] — [why, one sentence]

**Stress-test:** [Failure condition] → [Survives? How?]

**Start here:** The first concrete file or function to touch if user picks this direction.
```

### Priority Recommendation

After the comparison table, give a single recommended direction with a one-paragraph rationale. Do not hedge with "it depends on your goals" — commit to a recommendation, then explain the conditions under which a different direction would be better.

## Phase 4 — Immediate Actions (Regardless of Direction)

List up to 5 quick wins that apply no matter which direction the user picks. These should be:
- Completable in under half a day
- Non-breaking (no API changes, no data migrations)
- High-signal (they make the codebase easier to navigate for any future refactor)

Format:
```
- [ ] [Action] — [File/location] — [Why it helps]
```

## Output Contract

The final output must contain, in order:
1. **Findings summary** (bullet list, ≤15 items, each with axis label and file reference)
2. **Comparison table** (3-5 directions, all rows filled)
3. **Per-direction detail** (3-5 blocks, structured as above)
4. **Priority recommendation** (one paragraph, commit to one direction)
5. **Immediate actions** (≤5 items, checkbox format)

Do NOT produce a single long prose essay. The structure above is the contract — every section must be present and in order.

Do NOT begin Phase 3 output until Phase 1 and Phase 2 are complete. "Complete" means you have read at least the entry points, the hot files from git log, and any existing architecture docs.

## Rules

- **Never recommend a direction you haven't stress-tested.** If you cannot identify the primary failure condition for a direction, mark it "stress-test: unknown — insufficient codebase data" and say what you'd need to know.
- **Effort estimates are mandatory.** "It depends" is not an estimate. Give a range (e.g., "2–4 dev-weeks") and state your assumptions.
- **Observable evidence only.** Every finding must cite a file or a code pattern you actually read. Do not infer issues from project type alone.
- **Reversibility must be stated.** A refactor that can be reverted in a day has a different risk profile than one that restructures the data model.
- **User selects direction before any implementation begins.** This skill produces a plan, not code. After delivering the output, pause and ask: "Which direction would you like to pursue, or should I adjust any of the proposals?"

## Gotchas

> Only real failures from executing this skill go here.

- **Git log is empty (new repo or shallow clone)** → skip the hot-files step; ask the user which files change most often, or use `find` + file size as a proxy for "significant" files.
- **No entry point is obvious** → read `package.json scripts`, `Makefile`, or `pyproject.toml [tool.poetry.scripts]` to locate the real start. Do not guess based on file name `index.*` alone.
- **Monorepo with 10+ packages** → scope the analysis to the packages the user mentions, or ask which package is the target. Running Phase 1 across all packages exceeds context budget (DEGRADING at > 60% used).
- **Appsec surface present but no auth code visible** → do not assume auth is handled elsewhere. Explicitly flag "auth enforcement location unknown" in the Risk axis.
