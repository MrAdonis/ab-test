#!/bin/bash
# HELDOUT 回归：B（含新增条款）vs clean（无任何规则注入）跑 H1/H2/H3
# 每 run 独立 /tmp 沙箱 cwd，避免污染
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
OUT="$HERE/outputs"
mkdir -p "$OUT"

run_one() {
  local task="$1" variant="$2"
  local sb; sb=$(mktemp -d "/tmp/t69h-${task}-${variant}-XXXXXX")
  local prompt
  if [ "$variant" = "B" ]; then
    prompt=$(cat "$ROOT/prompts/rules-B.txt" "$HERE/${task}.txt")
  else
    prompt=$(cat "$HERE/${task}.txt")
  fi
  ( cd "$sb" && claude -p "$prompt" \
      --model sonnet \
      --permission-mode bypassPermissions \
      > "$OUT/${task}-${variant}.md" 2> "$OUT/${task}-${variant}.err" )
  echo "done: ${task}-${variant} (sandbox $sb)"
}

for t in h1-writing h2-cli h3-diagnose; do
  for v in B C; do
    run_one "$t" "$v" &
  done
done
wait
