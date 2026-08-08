#!/bin/bash
# t73 runner：写作任务，cwd 落在 /tmp 沙箱，输出落 outputs/
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/outputs"
mkdir -p "$OUT"

run_one() {
  local task="$1" variant="$2"
  local sb; sb=$(mktemp -d "/tmp/t73-${task}-${variant}-XXXXXX")
  local prompt; prompt=$(cat "$HERE/prompts/rules-${variant}.txt" "$HERE/prompts/${task}.txt")
  ( cd "$sb" && claude -p "$prompt" \
      --model sonnet \
      --permission-mode bypassPermissions \
      > "$OUT/${task}-${variant}.md" 2> "$OUT/${task}-${variant}.err" )
  echo "done: ${task}-${variant}"
}

run_one task1-remote-work "$1" &
run_one task2-startup-lesson "$1" &
wait
