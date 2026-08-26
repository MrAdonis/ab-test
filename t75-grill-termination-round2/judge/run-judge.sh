#!/bin/bash
# t75 盲评：甲乙位置在四个任务间交叉分配，抵消位置偏好。映射见 mapping.txt。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../outputs"

judge_one() {
  local task="$1" jia="$2" yi="$3"
  local input="$HERE/input-${task}.txt"
  {
    cat "$HERE/rubric.md"
    echo -e "\n\n===== 对话甲 =====\n"
    cat "$OUT/${task}-${jia}.md"
    echo -e "\n\n===== 对话乙 =====\n"
    cat "$OUT/${task}-${yi}.md"
  } > "$input"

  claude -p "$(cat "$input")" --model opus \
    --permission-mode bypassPermissions \
    --disallowed-tools "Bash,Read,Glob,Grep,Write,Edit,WebSearch,WebFetch,Task" \
    > "$HERE/verdict-${task}.md" 2> "$HERE/verdict-${task}.err"
  echo "judged: $task"
}

judge_one 3-ratelimit A B &
judge_one 4-search    B A &
judge_one 5-pricing   B A &
judge_one 6-hire      A B &
wait
echo "=== judging done ==="
