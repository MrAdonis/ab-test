#!/bin/bash
# held-in：H2 任务中立生成 artifact（sonnet），再用 A/B 两套 reviewer 规则各审一遍
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; T80="$(dirname "$HERE")"
step="${1:-gen}"
if [ "$step" = gen ]; then
  sb=$(mktemp -d /tmp/t80h-gen-XXXXXX)
  ( cd "$sb" && claude -p "$(sed -n 's/^# dirstat.py 需求单//p' /dev/null)$(tail -n +3 "$HERE/fixture/SPEC.md")" --model sonnet --permission-mode bypassPermissions > "$HERE/gen.log" 2>&1 )
  cp "$sb"/dirstat.py "$sb"/test_dirstat.py "$HERE/fixture/" 2>/dev/null; ls "$sb"
  ( cd "$sb" && python3 -m pytest -q 2>&1 | tail -3 ) > "$HERE/pytest.log"
  cat "$HERE/pytest.log"
else
  for V in A B; do (
    sb=$(mktemp -d "/tmp/t80h-rev${V}-XXXXXX"); cp -R "$HERE/fixture/." "$sb/"
    cd "$sb" && claude -p "$(cat "$T80/prompts/rules-${V}.txt" "$HERE/task-review.txt")" --model sonnet --permission-mode bypassPermissions \
      > "$HERE/reviews/review-${V}.md" 2> "$HERE/reviews/review-${V}.err"; echo "done $V"
  ) & done; wait
fi
