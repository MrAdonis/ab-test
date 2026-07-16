#!/bin/bash
# t55: advisor 档位对比 —— 同一任务四个 arm，测质量 + 真实成本
#
# 前置实测结论（2026-07-13）：Opus 不能当 advisor 的 executor。
#   --model opus --advisor fable 会静默返回 advisor_tool_result_error: unavailable，
#   降级成 opus 单跑。所以「opus + 顾问」不成立，不做 arm。
#
# A: opus 单跑              —— 现主力基线（订阅内）
# B: sonnet 单跑            —— 地板线，用来隔离 advisor 的净增益
# C: sonnet 主 + opus 顾问  —— 官方主推省钱档（全订阅内，零 credits）
# D: sonnet 主 + fable 顾问 —— 顶级判断档（顾问 token 走 credits $10/$50）
set -uo pipefail

ROOT="/Users/edon/Projects/personal/ab-test/t55-advisor-cost-quality"
TASK="$ROOT/prompts/task.md"
OUT="$ROOT/outputs"
mkdir -p "$OUT"

run_arm() {
  local arm="$1" model="$2" advisor="$3"
  local dir="$OUT/$arm"
  rm -rf "$dir"; mkdir -p "$dir"

  # 注意：--add-dir 是变长参数，若它是最后一个 flag 会把 prompt 当目录吞掉。
  # 所以 prompt 一律走 stdin，不做位置参数。
  local -a args=(-p --add-dir "$dir" --model "$model"
                 --permission-mode bypassPermissions --output-format json)
  local want_advisor=""
  if [ "$advisor" != "none" ]; then
    args+=(--advisor "$advisor")
    want_advisor="$advisor"
  fi

  echo "=== [$arm] model=$model advisor=$advisor ==="
  local start=$SECONDS
  (
    cd "$dir" || exit 1
    if [ -n "$want_advisor" ]; then
      export CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL=1
    fi
    timeout 900 claude "${args[@]}" < "$TASK" > "$dir/_result.json" 2> "$dir/_stderr.log"
  )
  local rc=$?
  local elapsed=$((SECONDS - start))
  echo "  exit=$rc  wall=${elapsed}s"
  echo "$elapsed" > "$dir/_wall_seconds.txt"

  python3 - "$dir/_result.json" "$arm" "$want_advisor" <<'PY'
import json, sys, pathlib
p, arm, want = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
try:
    d = json.loads(p.read_text())
except Exception as e:
    print(f"  [!] 无法解析 result.json: {e}"); sys.exit(0)
u = d.get("usage") or {}
keys = ["input_tokens","output_tokens","cache_creation_input_tokens","cache_read_input_tokens"]
print("  usage:", {k: u.get(k) for k in keys})
print("  cost_usd:", d.get("total_cost_usd"), " turns:", d.get("num_turns"))
mu = d.get("modelUsage") or {}
print("  modelUsage:", list(mu.keys()))
# advisor 全链路失败都是静默的 —— 唯一可靠验证就是顾问模型有没有进 modelUsage
if want:
    hit = any(want.split("-")[0] in k for k in mu)
    print(f"  ADVISOR_ACTIVE: {'YES' if hit else 'NO —— 静默失效，本 arm 数据作废'}")
PY
  echo ""
}

case "${1:-all}" in
  A) run_arm A opus none ;;
  B) run_arm B sonnet none ;;
  C) run_arm C sonnet opus ;;
  D) run_arm D sonnet fable ;;
  all)
    run_arm A opus none
    run_arm B sonnet none
    run_arm C sonnet opus
    run_arm D sonnet fable
    ;;
esac
