[P0] Bare cover/poster requests still have no decision procedure. Branches ① AI image gen and ③ design constraints both plausibly match `做个海报` / `make me a cover`, so the row relabels the original ambiguity instead of resolving it. Fix: add a default/tiebreaker, e.g. “finished visual asset → ①; developer parameter/spec request → ③; formal printable document → ②.”

[P1] Cross-row precedence is undefined. `做一个可视化海报` can hit both `封面 / KV / 海报 / 一页纸 → pick one of three` and `可视化需求 → diagram`; `做个海报设计稿 / poster mockup` can also collide with the UI mockup row. Fix: add precedence rules by primary artifact: chart/diagram output → visualization row; static poster/cover/KV → new row; app/screen/prototype → UI mockup row.

[P1] Multi-output requests fall through the “pick one” structure. `做一张小红书封面，并给开发实现参数规范` needs both ① AI image gen and ③ design constraints, but the row forces a single route. Fix: allow combined routing when the user asks for both a generated asset and implementation/spec handoff.

[P2] Header/branch terms are incoherent. `一页纸` only belongs to ② and is not really a cover/KV/poster; `KV` appears in the trigger but has no explicit branch home. Fix: map `KV` explicitly to the finished visual/default branch and split `一页纸` into the HTML/formal-doc wording.

Verdict: **REWORK**. Smallest change: replace “pick one of three” with explicit intent-based routing defaults, especially “bare cover/poster/KV = finished visual asset → AI image gen unless the user asks for formal document layout or developer constraints.”
