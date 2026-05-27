# Opus 4.7 vs Sonnet 4.6 vs Codex (GPT-5.5) — AB Test

> 4 tasks × 3 models × identical self-contained prompts, no cross-reference between runs.
>
> Triggered by [this post by leon7hao](https://x.com/leon7hao/status/2059191435753410630) on "Opus for frontend / GPT for architecture / Codex for bugs" not matching daily hands-on experience.
>
> 中文: [README.md](./README.md)

![Routing table](./screenshots/routing-table-v2.png)

---

## Method

Three models ran the same prompt independently. Prompts are self-contained (no project context dependency) to keep the starting line level.

| Task | Tests | Prompt |
|------|-------|--------|
| T1 | FAQ accordion HTML component — frontend & aesthetics | [prompts/t1-prompt.md](./prompts/t1-prompt.md) |
| T2 | 33-file Python project coupling scan — architectural insight | [prompts/t2-prompt.md](./prompts/t2-prompt.md) |
| T3 | JS Promise cache race debug — root cause & production awareness | [prompts/t3-prompt.md](./prompts/t3-prompt.md) |
| T4 | R2 vs S3 Chinese tweet, 280-400 chars — Chinese writing judgment | [prompts/t4-prompt.md](./prompts/t4-prompt.md) |

Raw outputs at `outputs/<task>/<model>.<ext>`.

## Scoring axes (per task)

- **T1** — visual style + code volume + design restraint (eyeball screenshots `screenshots/t1-*.png` + line count)
- **T2** — total findings + coverage matrix (who caught what / who missed what)
- **T3** — root-cause correctness + fix completeness + reasoning-path depth (does it back-validate)
- **T4** — hook strength / judgment clarity / X-native voice / forbidden-word hits

T2 targets a private project, so paths are redacted to `<project>/` but finding content is preserved. Substitute any of your own 5+ file projects to reproduce.

## Headline findings

| Task | Best | Note |
|------|------|------|
| Frontend (complex) | Opus / Codex tied at 9/10 | Codex used ~20% less code |
| Architecture (large) | Opus deepest | Codex framing strong but fewer findings; Sonnet caught Opus-missed mkdir / ghost imports |
| Deep debug | Opus (production awareness) / Codex complementary | Only Opus flagged "move `img.src` after `onload` binding" — a real production gotcha |
| Chinese writing | Opus 9 / Sonnet 8 / **Codex 5** | Codex monolithic paragraphs, academic tone — banned for tweets |

Full scoring matrix + 8-claim leon7hao comparison table + routing recommendations in **[REPORT.md](./REPORT.md)** (Chinese).

## Four hard constraints (from data)

1. **Codex banned for Chinese long-form** — academic tone, scored 5/10
2. **Don't underestimate Sonnet** — for small/medium tasks, T2 showed Sonnet catching low-hanging fruit Opus missed
3. **GPT-5.5 frontend ≥ Opus** — 9/10 with 20% less code; "GPT isn't good at frontend" is outdated
4. **Opus 4.7 has no weak axis** — top or tied-top on architecture / debug / writing / frontend

## Repo layout

```
ab-test/
├── README.md / README.en.md
├── REPORT.md              full scoring matrix + leon7hao claim comparison + routing
├── prompts/               4 prompts as-given
├── outputs/
│   ├── t1-accordion/      3 model HTML outputs
│   ├── t2-arch/           3 model architecture findings
│   ├── t3-debug/          buggy.js (input) + 3 model analyses
│   └── t4-chinese/        source.md (facts brief) + 3 model tweets
└── screenshots/           T1 renders + routing table image
```

## Environment

| Model | Channel | Plan |
|-------|---------|------|
| Opus 4.7 | Claude Code (`/model opus`) | Claude Max |
| Sonnet 4.6 | Claude Code (default) | Claude Max |
| Codex GPT-5.5 | Codex CLI 0.133.0-alpha.1, `reasoning=high`, `-s read-only` | Codex Pro |

Date: 2026-05-26.
Scoring: manual.

## Limitations

- N=4 tasks × 3 models is small. Treat as directional evidence, not benchmark.
- Scoring is manual (mine) with subjective elements. T2 / T3 finding counts and coverage matrices are the most objective hard data.
- T2's target is a private project, not directly reproducible. The other three are self-contained.
- Codex ran with `reasoning=high` + `read-only`; different reasoning levels behave differently.
- 2026-05-26 snapshot. Models keep shipping. Conclusions will age.

## License

MIT
