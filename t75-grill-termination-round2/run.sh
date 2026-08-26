#!/bin/bash
# t75：4 任务 × 2 臂，全部并行。3/4 为技术方案类（有可验证终点），5/6 为主观决策类。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HERE/outputs" "$HERE/logs"

for task in 3-ratelimit 4-search 5-pricing 6-hire; do
  for arm in A B; do
    python3 "$HERE/driver.py" "$task" "$arm" \
      > "$HERE/logs/${task}-${arm}.log" 2>&1 &
  done
done
wait

echo "=== all runs done ==="
tail -n 2 "$HERE"/logs/*.log
