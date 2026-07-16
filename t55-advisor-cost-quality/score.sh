#!/bin/bash
# t55 客观评分：正确性（跑真实 fixture）+ agent-native 接口契约（coding-dod.md 四契约）
# 主观质量走盲评，不在这里。
set -uo pipefail
ROOT="/Users/edon/Projects/personal/ab-test/t55-advisor-cost-quality"
FIX="$ROOT/fixtures"

# ---- 建 fixture（每 arm 共用同一份，含全部边界情况）----
rm -rf "$FIX"; mkdir -p "$FIX"
cat > "$FIX/ok.md" <<'EOF'
---
title: 好文件
updated: 2026-07-13
type: concept
tags: [a, b]
---
body
EOF
cat > "$FIX/missing_field.md" <<'EOF'
---
title: 缺 tags
updated: 2026-07-13
type: method
---
body
EOF
cat > "$FIX/bad_date.md" <<'EOF'
---
title: 日期格式坏
updated: 2026/07/13
type: tool
tags: [x]
---
body
EOF
cat > "$FIX/bad_type.md" <<'EOF'
---
title: type 非法
updated: 2026-07-13
type: banana
tags: [x]
---
body
EOF
cat > "$FIX/empty_tags.md" <<'EOF'
---
title: tags 空数组
updated: 2026-07-13
type: concept
tags: []
---
body
EOF
printf -- '---\ntitle: [unclosed\n  bad yaml: : :\n---\nbody\n' > "$FIX/broken_yaml.md"
printf -- 'no frontmatter at all\n' > "$FIX/no_fm.md"
: > "$FIX/empty.md"

echo "fixtures: 8 个（1 合规 + 5 各类违规 + 坏 YAML + 空文件）"
echo ""

for arm in A B C D; do
  dir="$ROOT/outputs/$arm"
  [ -d "$dir" ] || continue
  echo "===================== ARM $arm ====================="
  cost=$(python3 -c "import json;print(json.load(open('$dir/_result.json')).get('total_cost_usd'))" 2>/dev/null)
  wall=$(cat "$dir/_wall_seconds.txt" 2>/dev/null)
  models=$(python3 -c "import json;print(list((json.load(open('$dir/_result.json')).get('modelUsage') or {}).keys()))" 2>/dev/null)
  echo "cost=\$$cost  wall=${wall}s  models=$models"

  # C1 能不能跑起来
  echo "-- 运行 python -m fmlint <fixtures>"
  (cd "$dir" && timeout 60 python3 -m fmlint "$FIX" > /tmp/t55_$arm.out 2> /tmp/t55_$arm.err)
  rc=$?
  echo "   exit=$rc  stdout=$(wc -c < /tmp/t55_$arm.out)B  stderr=$(head -c 200 /tmp/t55_$arm.err | tr '\n' ' ')"

  # C2 输出是不是机器可读（JSON）—— agent-native 契约①
  if python3 -c "import json,sys;json.load(open('/tmp/t55_$arm.out'))" 2>/dev/null; then
    echo "   [契约①] stdout 直接是合法 JSON ✓"
  elif (cd "$dir" && timeout 60 python3 -m fmlint --json "$FIX" 2>/dev/null | python3 -c "import json,sys;json.load(sys.stdin)" 2>/dev/null); then
    echo "   [契约①] --json flag 可出合法 JSON ✓（默认非 JSON）"
  else
    echo "   [契约①] ✗ 无机器可读输出"
  fi

  # C3 五类违规是否全部检出
  echo "-- 检出情况（看是否 5 个违规文件都被点名）"
  for f in missing_field bad_date bad_type empty_tags broken_yaml; do
    if grep -q "$f" /tmp/t55_$arm.out 2>/dev/null; then echo "   ✓ $f"; else echo "   ✗ $f 未检出"; fi
  done
  if grep -q "ok.md" /tmp/t55_$arm.out 2>/dev/null; then
    echo "   ! ok.md 出现在输出里（可能误报，需人看是不是仅列举）"
  fi

  # C4 exit code 语义（有违规应非 0）
  echo "   exit code 有违规时 = $rc （期望非 0 便于 CI gate）"

  # C5 自带测试
  echo "-- 跑自带测试"
  (cd "$dir" && timeout 120 python3 -m pytest -q 2>&1 | tail -3 | sed 's/^/   /')

  # C6 发现入口
  ls "$dir"/*.md "$dir"/**/*.md 2>/dev/null | sed 's|.*/|   doc: |' | sort -u
  (cd "$dir" && timeout 30 python3 -m fmlint --help > /tmp/t55_${arm}_help.txt 2>&1) \
    && echo "   --help: $(wc -l < /tmp/t55_${arm}_help.txt) 行，Examples 段: $(grep -ci 'example' /tmp/t55_${arm}_help.txt)"
  echo ""
done
