#!/bin/bash
set -u
H="$(cd "$(dirname "$0")" && pwd)"
sb=$(mktemp -d /tmp/hi-gen-XXXXXX)
( cd "$sb" && claude -p "把「MCP 和 Skills 的区别」写成一条 260 字以内的中文推文，读者是天天用 Claude Code 的开发者，别写成科普腔，要有自己的判断。只输出推文正文，不要任何前后说明。" \
    --model sonnet --permission-mode bypassPermissions > "$H/artifact.txt" 2>/dev/null )
{ echo; echo "---"; echo;
  echo "帮我审一下这条推文，去掉 AI 味，然后给我改写版本。";
  echo; echo "这是发在 X 上的技术推文，读者是天天用 Claude Code 的开发者。";
  echo; echo "---"; echo; cat "$H/artifact.txt"; } > "$H/task-tweet.txt"
for v in A B; do
  sbx=$(mktemp -d "/tmp/hi-$v-XXXXXX")
  p=$(cat "$H/../prompts/rules-$v.txt" "$H/task-tweet.txt")
  ( cd "$sbx" && claude -p "$p" --model sonnet --permission-mode bypassPermissions > "$H/review-$v.md" 2>/dev/null ) &
done
wait
echo "heldin done"
