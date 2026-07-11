#!/bin/bash
# run-trial.sh <arm A|B> <trial-n> — 复制 fixture、按臂放 CLAUDE.md、跑 headless sonnet、确定性打分
# 打分全部脚本化（账本字段 diff / exit code / curl 状态码），无主观项。
set -uo pipefail
ARM="$1"; N="$2"
T="$(cd "$(dirname "$0")" && pwd)"
W="$(mktemp -d "/tmp/shoplist-${ARM}${N}.XXXX")"

cp -R "$T/fixture/." "$W/"
cp "$T/prompts/CLAUDE-${ARM}.md" "$W/CLAUDE.md"
cd "$W"
git init -q && git -c user.email=dev@local -c user.name=dev add -A && git -c user.email=dev@local -c user.name=dev commit -qm baseline

cat "$T/prompts/task.md" | claude -p --model sonnet --permission-mode bypassPermissions \
  --add-dir "$W" --output-format text > "$W/agent-out.log" 2>&1
RC=$?

# ── 确定性打分 ──
PORT=$((3400 + $( [ "$ARM" = "A" ] && echo 10 || echo 20 ) + N))
npm test > "$W/score-test.log" 2>&1; TEST_RC=$?
PORT=$PORT node server.js > "$W/score-server.log" 2>&1 &
SRV=$!
sleep 1
EXPORT_CODE=$(curl -s -o "$W/score-export.out" -w '%{http_code}' "http://localhost:$PORT/export" || echo 000)
EXPORT_HEADER=$(head -1 "$W/score-export.out" | grep -cF 'id,name,qty' || true)
kill "$SRV" 2>/dev/null
LEDGER=$(python3 "$T/score-ledger.py" "$T/fixture/task_plan.md" "$W/task_plan.md" 2>/dev/null || echo '{"ledger_parse_ok":false}')

printf '{"arm":"%s","trial":%s,"claude_rc":%s,"test_rc":%s,"export_http":%s,"export_header_ok":%s,"ledger":%s,"workdir":"%s"}\n' \
  "$ARM" "$N" "$RC" "$TEST_RC" "$EXPORT_CODE" "$EXPORT_HEADER" "$LEDGER" "$W" \
  | tee "$T/outputs/${ARM}${N}-score.json"
git diff > "$T/outputs/${ARM}${N}-diff.patch"
cp "$W/task_plan.md" "$T/outputs/${ARM}${N}-task_plan-after.md"
cp "$W/agent-out.log" "$T/outputs/${ARM}${N}-agent-out.log"
