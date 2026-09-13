#!/bin/bash
# t81 runner：证据充分性判定类任务，只读 fixture、无写操作。
# fixture 复制进 /tmp 沙箱后再把路径注入 prompt——避免 ab-test 目录名（含 t 编号）泄漏评测线索。
# 用法：./run.sh A   或   ./run.sh B
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/outputs"
mkdir -p "$OUT"

run_one() {
  local task="$1" fixture="$2" variant="$3"
  local sb; sb=$(mktemp -d "/tmp/suff-${task}-${variant}-XXXXXX")
  cp "$HERE/fixtures/${fixture}" "$sb/${fixture}"
  local prompt; prompt=$(cat "$HERE/prompts/rules-${variant}.txt" "$HERE/prompts/${task}.txt" \
    | sed "s#__FIXTURE__#$sb/${fixture}#g")
  ( cd "$sb" && claude -p "$prompt" \
      --model sonnet \
      --permission-mode bypassPermissions \
      > "$OUT/${task}-${variant}.md" 2> "$OUT/${task}-${variant}.err" )
  echo "done: ${task}-${variant}"
}

run_one task1-earnings-lookup northwind-q3-snippets.md "$1" &
run_one task2-claim-check helios-claim-sources.md "$1" &
wait
