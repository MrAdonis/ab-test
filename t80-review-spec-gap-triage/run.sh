#!/bin/bash
# t80 runner：每个 (task, variant, gen) 独立沙箱，fixture 拷进去，输出落 outputs/
# 用法：./run.sh A|B|H [gens=2] [start=1]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/outputs"; mkdir -p "$OUT"
V="$1"; GENS="${2:-2}"; START="${3:-1}"
run_one() {
  local task="$1" variant="$2" g="$3"
  local sb; sb=$(mktemp -d "/tmp/t80-${task}-${variant}${g}-XXXXXX")
  cp -R "$HERE/fixtures/${task}/." "$sb/"
  local prompt; prompt=$(cat "$HERE/prompts/rules-${variant}.txt" "$HERE/prompts/${task}.txt")
  ( cd "$sb" && claude -p "$prompt" --model sonnet --permission-mode bypassPermissions \
      > "$OUT/${task}-${variant}${g}.md" 2> "$OUT/${task}-${variant}${g}.err" )
  echo "done: ${task}-${variant}${g}"
}
for g in $(seq "$START" "$GENS"); do
  run_one task1-membership "$V" "$g" &
  run_one task2-csv-export "$V" "$g" &
done
wait
