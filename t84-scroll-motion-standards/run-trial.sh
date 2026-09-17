#!/usr/bin/env bash
# 用法: ./run-trial.sh A 1
set -euo pipefail
ARM="$1"; N="$2"
T="/Users/edon/Projects/personal/ab-test/t84-scroll-motion-standards"
W="/tmp/t84-run/${ARM}${N}"
mkdir -p "$W"
cp -R "$T/fixture/." "$W/"
cp "$T/prompts/CLAUDE-${ARM}.md" "$W/CLAUDE.md"
if [ "$ARM" = "B" ]; then
  mkdir -p "$W/docs"
  cp "$T/fixture-b-docs/MOTION.md" "$W/docs/MOTION.md"
fi

cd "$W"
cat "$T/prompts/task.md" | claude -p --model sonnet --permission-mode bypassPermissions \
  --add-dir "$W" --output-format text > "$W/agent-out.log" 2>&1 || true

mkdir -p "$T/outputs"
cp "$W/agent-out.log" "$T/outputs/${ARM}${N}-agent-out.log"
diff -ruN "$T/fixture" "$W" > "$T/outputs/${ARM}${N}-diff.patch" 2>/dev/null || true
python3 "$T/score.py" "$W" "$T/outputs/${ARM}${N}-score.json" > /dev/null
python3 -c "
import json,sys
d=json.load(open('$T/outputs/${ARM}${N}-score.json'))
print('${ARM}${N}  MAIN', d['MAIN_SCORE'], ' COVERAGE', d['COVERAGE_SCORE'])
for k in ['M1_reduced_motion_visible','M2_anim_disabled_visible','M3_features_pinned','M4_hscroll_nonpointer_entry','M5_gpu_only','M6_hover_gated','M7_parallax_transform','uses_animation_timeline','uses_supports_guard','uses_intersection_observer','reduced_motion_blanket_kill']:
    print('   ',k,'=',d[k])
"
