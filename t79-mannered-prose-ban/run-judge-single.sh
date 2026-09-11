#!/bin/bash
HERE="/Users/edon/Projects/personal/ab-test/t79-mannered-prose-ban"
OUT="$HERE/judge-single"
judge_one() {
  local round="$1" task="$2" variant="$3"
  local src
  if [ "$round" = "r1" ]; then src="$HERE/outputs/${task}-${variant}.md"; else src="$HERE/outputs-r2/${task}-${variant}.md"; fi
  local sb; sb=$(mktemp -d "/tmp/t79j-XXXXXX")
  local p; p="$(cat "$HERE/judge/rubric-single.md")

## 稿件作者收到的任务

$(cat "$HERE/prompts/${task}.txt")

## 待评稿件

$(cat "$src")"
  ( cd "$sb" && claude -p "$p" --model opus --permission-mode bypassPermissions \
      > "$OUT/${round}-${task}-${variant}.md" 2> "$OUT/${round}-${task}-${variant}.err" )
}
for r in r1 r2; do for t in task1-narrow-scope task2-landing-copy; do for v in A B; do
  judge_one "$r" "$t" "$v" &
done; done; done
wait
echo DONE
