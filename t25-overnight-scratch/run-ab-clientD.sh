#!/bin/bash
# run-ab-clientD.sh — t25 overnight --scratch AB（clientD inventoryDecay 真多轮 substrate）
#
# 对照单一变量：overnight-loop.sh 的 --scratch 开关（跨轮记忆草稿）。
#   Arm A = 无 scratch（baseline，纯 fresh-context Ralph）
#   Arm B = --scratch（每轮回放前几轮小结）
# 其余完全一致：同 task-clientD.md、同 clientD-fixture 全新副本、同 max-iter/model/sleep。
#
# substrate：clientD inventoryDecay 云函数被施加受控回归（删了 3 处边界语义，留 TODO），
# 起始态 4 passed/3 failed。任务 = 靠读测试反推、复原全绿。零 npm 依赖（stub 拦截
# require），不跑 npm install。round-eval 经 run-tests.sh 转译能客观判 PASS/FAIL。
#
# 生产 clientD 目录全程只读，本脚本只动 fixture 副本。
#
# 用法：./run-ab-clientD.sh [--reps N] [--max-iter N] [--model sonnet|opus] [--sleep S]

set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
FIXTURE="$ROOT/clientD-fixture"
TASK="$ROOT/task-clientD.md"
LOOP="$HOME/.claude/scripts/overnight-loop.sh"

REPS=3
MAX_ITER=12
MODEL="sonnet"
SLEEP=5

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reps)     REPS="$2"; shift 2 ;;
    --max-iter) MAX_ITER="$2"; shift 2 ;;
    --model)    MODEL="$2"; shift 2 ;;
    --sleep)    SLEEP="$2"; shift 2 ;;
    *) echo "未知参数 $1" >&2; exit 1 ;;
  esac
done

[[ -f "$LOOP" ]]    || { echo "找不到 overnight-loop.sh: $LOOP" >&2; exit 1; }
[[ -d "$FIXTURE" ]] || { echo "找不到 fixture: $FIXTURE" >&2; exit 1; }
[[ -f "$TASK" ]]    || { echo "找不到 task: $TASK" >&2; exit 1; }

RUNROOT="$ROOT/run-clientD"
mkdir -p "$RUNROOT"
DATA="$RUNROOT/REPORT-data.md"
{
  echo "# t25 clientD AB 原始数据（自动生成，人工分析填 REPORT.md）"
  echo ""
  echo "- substrate: clientD inventoryDecay 受控回归（起始 4/3，目标 7/0）"
  echo "- reps/arm: $REPS  max-iter: $MAX_ITER  model: $MODEL"
  echo "- 起始: $(date)"
  echo ""
  echo "| arm | rep | status | rounds | best_badness | FAIL轮数 |"
  echo "|-----|-----|--------|--------|--------------|----------|"
} > "$DATA"

run_arm() {
  local arm="$1" rep="$2"; shift 2
  local dir="$RUNROOT/${arm}-rep${rep}"
  rm -rf "$dir"
  cp -r "$FIXTURE" "$dir"

  # 起始态自检：必须是 red（4/3）。绿了说明副本污染，跳过这一跑。
  local start
  start=$( cd "$dir" && npm test 2>&1 | grep -oE '[0-9]+ passed, [0-9]+ failed' | tail -1 )
  echo ">>> [$arm rep$rep] 起始态: ${start:-未知}"
  if [[ "$start" != *"3 failed"* ]]; then
    echo "| $arm | $rep | BAD_START | - | - | - |" >> "$DATA"
    echo ">>> [$arm rep$rep] 起始态非 4/3，跳过" >&2
    return 1
  fi

  echo ">>> [$arm rep$rep] overnight-loop（$* ）..."
  bash "$LOOP" "$TASK" --dir "$dir" --max-iter "$MAX_ITER" --model "$MODEL" --sleep "$SLEEP" "$@" >/dev/null 2>&1

  local conv
  conv="$(ls -t "$dir"/.overnight/*/convergence.log 2>/dev/null | head -1)"
  local status rounds best repeated
  if [[ -n "$conv" ]]; then
    rounds="$(($(wc -l < "$conv") - 1))"
    best="$(tail -n +2 "$conv" | awk -F'\t' '$3 ~ /^[0-9]+$/ {print $3}' | sort -n | head -1)"
    status="$(tail -1 "$conv" | awk -F'\t' '{print $2}')"
    repeated="$(grep -c "FAIL" "$conv" 2>/dev/null || echo 0)"
  else
    status="NO_LOG"; rounds="-"; best="-"; repeated="-"
  fi
  echo "| $arm | $rep | $status | $rounds | ${best:-?} | $repeated |" >> "$DATA"
  echo ">>> [$arm rep$rep] done: status=$status rounds=$rounds best=${best:-?}"
}

for rep in $(seq 1 "$REPS"); do
  run_arm "armA-noscratch" "$rep"
  run_arm "armB-scratch"   "$rep" --scratch
done

{
  echo ""
  echo "- 结束: $(date)"
} >> "$DATA"

echo ""
echo "==================== 汇总 ===================="
cat "$DATA"
echo ""
echo "原始数据: $DATA"
echo "各 arm 详情: $RUNROOT/<arm>-rep<N>/.overnight/*/summary.md（armB 另有 scratch.md）"