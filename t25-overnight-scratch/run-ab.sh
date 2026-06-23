#!/bin/bash
# run-ab.sh — t25 overnight --scratch AB harness
#
# 对照单一变量：overnight-loop.sh 的 --scratch 开关（跨轮记忆草稿）。
# Arm A = 无 scratch（baseline，纯 fresh-context Ralph）
# Arm B = --scratch（每轮回放前几轮小结）
# 其余完全一致：同一 task.md、同一 fixture 全新副本、同 max-iter / model / sleep。
#
# 每个 arm 在独立的 fixture 副本上跑（loop 会改文件，必须隔离）。
# 模型有随机性 → 单跑噪声大，默认每 arm 重复 REPEAT 次取分布。
#
# 用法：
#   ./run-ab.sh [--reps N] [--max-iter N] [--model sonnet|opus]
#
# 跑完看：./run/REPORT-data.md（自动汇总）+ 各 arm 的 .overnight/*/summary.md

set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
FIXTURE="$ROOT/fixture"
TASK="$ROOT/task.md"
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

[[ -f "$LOOP" ]] || { echo "找不到 overnight-loop.sh: $LOOP" >&2; exit 1; }

RUNROOT="$ROOT/run"
mkdir -p "$RUNROOT"
DATA="$RUNROOT/REPORT-data.md"
{
  echo "# t25 AB 原始数据（自动生成，人工分析填 REPORT.md）"
  echo ""
  echo "- reps/arm: $REPS  max-iter: $MAX_ITER  model: $MODEL"
  echo "- 起始: $(date)"
  echo ""
  echo "| arm | rep | status | rounds | best_badness | 重复失败原因数 |"
  echo "|-----|-----|--------|--------|--------------|----------------|"
} > "$DATA"

run_arm() {
  local arm="$1" rep="$2"; shift 2
  local dir="$RUNROOT/${arm}-rep${rep}"
  rm -rf "$dir"
  cp -r "$FIXTURE" "$dir"
  echo ">>> [$arm rep$rep] npm install ..."
  ( cd "$dir" && npm install --silent --no-audit --no-fund ) || { echo "npm install 失败" >&2; return 1; }

  echo ">>> [$arm rep$rep] overnight-loop（$* ）..."
  bash "$LOOP" "$TASK" --dir "$dir" --max-iter "$MAX_ITER" --model "$MODEL" --sleep "$SLEEP" "$@" >/dev/null 2>&1

  # 取最新一次 run 的 convergence.log
  local conv
  conv="$(ls -t "$dir"/.overnight/*/convergence.log 2>/dev/null | head -1)"
  local status rounds best repeated
  if [[ -n "$conv" ]]; then
    rounds="$(($(wc -l < "$conv") - 1))"
    best="$(tail -n +2 "$conv" | awk -F'\t' '$3 ~ /^[0-9]+$/ {print $3}' | sort -n | head -1)"
    status="$(tail -1 "$conv" | awk -F'\t' '{print $2}')"
    # 重复失败原因：同一 fail_reasons 字符串在多轮出现的去重计数差（粗指标，越小越好）
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
