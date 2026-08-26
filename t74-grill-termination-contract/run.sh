#!/bin/bash
# t74 runner：2 任务 × 2 臂，4 条多轮对话并行。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HERE/outputs"

for task in 1-membership 2-retainer; do
  for arm in A B; do
    python3 "$HERE/driver.py" "$task" "$arm" \
      > "$HERE/outputs/${task}-${arm}.log" 2>&1 &
  done
done
wait
echo "=== all done ==="
cat "$HERE"/outputs/*.log
