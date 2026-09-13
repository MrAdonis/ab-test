#!/bin/bash
D=/Users/edon/Projects/personal/ab-test/t82-context-bloat-slimming
for p in 01 02 03 04 05 06; do
  task=$(python3 -c "import json;print(json.load(open('$D/judge/_key.json'))['piece_$p']['task'])")
  (
    cd /tmp || exit
    claude -p "$(cat "$D/judge/rubric_$task.txt")

===== 待评内容开始 =====
$(cat "$D/judge/piece_$p.txt")
===== 待评内容结束 =====" \
      --safe-mode --model opus --permission-prompts none \
      --no-session-persistence > "$D/judge/score_$p.txt" 2>&1
  ) &
done
wait
echo JUDGEDONE
