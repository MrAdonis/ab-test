#!/bin/bash
# run-trial.sh <A|B> <trial-n> — 按臂放 CLAUDE.md，headless sonnet 审 fixture，存 review 文本
set -uo pipefail
ARM="$1"; N="$2"
T="$(cd "$(dirname "$0")" && pwd)"
W="$(mktemp -d "/tmp/t57-${ARM}${N}.XXXX")"

cp "$T/fixture/assistant_tools.py" "$W/"
cp "$T/prompts/CLAUDE-${ARM}.md" "$W/CLAUDE.md"
cd "$W"

cat "$T/prompts/task.md" | claude -p --model sonnet --permission-mode bypassPermissions \
  --add-dir "$W" --output-format text > "$T/outputs/${ARM}${N}-review.md" 2>&1
echo "done ${ARM}${N} -> outputs/${ARM}${N}-review.md ($(wc -l < "$T/outputs/${ARM}${N}-review.md") lines)"
