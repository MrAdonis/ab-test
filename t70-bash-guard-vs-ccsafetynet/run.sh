#!/bin/bash
# t70 runner —— A(pre-bash-guard) vs B(cc-safety-net) vs A+B 串联
# 只喂 stdin JSON 读 permissionDecision，**从不执行语料里的命令**
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CORPUS="$HERE/prompts/corpus.tsv"
A="$HOME/.claude/scripts/pre-bash-guard.sh"
CCSN_DIR="/tmp/dsh/ccsn"
OUT="$HERE/outputs"
mkdir -p "$OUT"

run_a() {  # $1=command
  printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.stdin.read()},"session_id":"t70"}))' \
    | bash "$A" 2>/dev/null | grep -q '"permissionDecision": *"deny"' && echo BLOCK || echo ALLOW
}

run_b() {  # $1=command  $2=mode(default|paranoid)
  local envs=()
  [ "$2" = paranoid ] && envs=(CC_SAFETY_NET_PARANOID=1)
  printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":sys.stdin.read()},"session_id":"t70","cwd":"/tmp/dsh"}))' \
    | (cd "$CCSN_DIR" && env "${envs[@]:-IGNORE=1}" bun run src/bin/cc-safety-net.ts --claude-code 2>/dev/null) \
    | grep -qiE '"permissionDecision" *: *"deny"|"decision" *: *"block"' && echo BLOCK || echo ALLOW
}

printf 'id\tset\texpect\tA\tB_default\tB_paranoid\tAB\tcommand\n' > "$OUT/results.tsv"
while IFS=$'\t' read -r id set expect cmd; do
  [ -z "${id:-}" ] && continue
  ra=$(run_a "$cmd")
  rbd=$(run_b "$cmd" default)
  rbp=$(run_b "$cmd" paranoid)
  if [ "$ra" = BLOCK ] || [ "$rbd" = BLOCK ]; then ab=BLOCK; else ab=ALLOW; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$set" "$expect" "$ra" "$rbd" "$rbp" "$ab" "$cmd" >> "$OUT/results.tsv"
  printf '%-4s %-2s exp=%-5s A=%-5s Bd=%-5s Bp=%-5s AB=%-5s\n' "$id" "$set" "$expect" "$ra" "$rbd" "$rbp" "$ab"
done < "$CORPUS"
echo "written: $OUT/results.tsv"
