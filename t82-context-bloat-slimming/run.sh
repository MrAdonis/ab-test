#!/bin/bash
D=/Users/edon/Projects/personal/ab-test/t82-context-bloat-slimming
mkdir -p "$D/outputs"
i=0
for arm in base slim; do
  for t in H1 H2 H3; do
    i=$((i+1))
    wd="/tmp/wk-$i"
    rm -rf "$wd"; mkdir -p "$wd"
    echo "$arm $t -> $wd" >> "$D/outputs/_map.txt"
    (
      cd "$wd" || exit 1
      claude -p "$(cat "$D/prompts/$t.txt")" \
        --safe-mode --model opus \
        --append-system-prompt "$(cat "$D/arms/$arm.md")" \
        --permission-mode acceptEdits --permission-prompts none \
        --no-session-persistence \
        > "$D/outputs/${arm}_${t}.txt" 2> "$D/outputs/${arm}_${t}.err"
      echo "done $arm $t rc=$?" >> "$D/outputs/_progress.txt"
    ) &
  done
done
wait
echo ALLDONE >> "$D/outputs/_progress.txt"
