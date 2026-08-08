#!/bin/bash
# t67 runner：每个 run 独立 mktemp 沙箱（cwd 绝不落在本测试目录——t65 污染事故教训）
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/outputs"
mkdir -p "$OUT"

run_one() {
  local task="$1" fixture="$2" variant="$3"
  local sb; sb=$(mktemp -d "/tmp/t67-${task}-${variant}-XXXXXX")
  cp -R "$HERE/fixtures/$fixture" "$sb/"
  local prompt; prompt=$(cat "$HERE/prompts/rules-${variant}.txt" "$HERE/prompts/${task}.txt")
  echo "$sb" > "$OUT/${task}-${variant}.sandbox"
  ( cd "$sb/$fixture" && claude -p "$prompt" \
      --model sonnet \
      --permission-mode bypassPermissions \
      > "$OUT/${task}-${variant}.md" 2> "$OUT/${task}-${variant}.err" )
  echo "done: ${task}-${variant} -> $sb"
}

run_one task1-precommit apilog "$1" &
run_one task2-coverage pricecalc "$1" &
wait
