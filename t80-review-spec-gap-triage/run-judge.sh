#!/bin/bash
# t80 judge：单篇独立对账（opus），每份输出一份 verdict
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/judge/verdicts"; mkdir -p "$OUT"
judge_one() {
  local task="$1" tag="$2"
  local src="$HERE/outputs/${task}-${tag}.md"
  [ -s "$src" ] || { echo "skip (empty): $src"; return; }
  local sb; sb=$(mktemp -d "/tmp/t80j-XXXXXX")
  local p; p="$(cat "$HERE/judge/rubric-single.md")

## 答案键

$(cat "$HERE/judge/key-${task}.md")

## 需求单原文

$(cat "$HERE/fixtures/${task}/SPEC.md")

## 待评 review 报告

$(cat "$src")"
  ( cd "$sb" && claude -p "$p" --model opus --permission-mode bypassPermissions \
      > "$OUT/${task}-${tag}.md" 2> "$OUT/${task}-${tag}.err" )
  echo "judged: ${task}-${tag}"
}
TAGS="${*:-A1 A2 B1 B2}"
for t in task1-membership task2-csv-export; do for tag in $TAGS; do
  judge_one "$t" "$tag" &
done; done
wait
echo DONE
