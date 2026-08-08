#!/bin/bash
# t69 runner：判定/筛选类任务，只读 fixture、无写操作，cwd 落在 /tmp 沙箱避免污染测试目录
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/outputs"
mkdir -p "$OUT"

run_one() {
  local task="$1" variant="$2"
  local sb; sb=$(mktemp -d "/tmp/t69-${task}-${variant}-XXXXXX")
  local prompt; prompt=$(cat "$HERE/prompts/rules-${variant}.txt" "$HERE/prompts/${task}.txt")
  ( cd "$sb" && claude -p "$prompt" \
      --model sonnet \
      --permission-mode bypassPermissions \
      > "$OUT/${task}-${variant}.md" 2> "$OUT/${task}-${variant}.err" )
  echo "done: ${task}-${variant}"
}

run_one task1-oss-vetting "$1" &
run_one task2-hiring-screen "$1" &
wait
