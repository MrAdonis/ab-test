#!/bin/bash
# 跑 node --test 并把汇总转成 round-eval（convergent-execution）能解析的 pytest 风格摘要。
# round-eval 的 parse_test_result 只认 "X passed, Y failed"（pytest/jest），不认 node --test 的 TAP，
# 所以这里转译一层。退出码遵循真实结果：有 fail → 非 0。
# 任务约束：模型只跑 `npm test`，不需也不许改本文件 / package.json。
set -uo pipefail
cd "$(dirname "$0")/.."

out=$(node --test scripts/test-inventory-decay.js 2>&1)
code=$?
echo "$out"

# node --test 汇总行：spec reporter 为「ℹ pass N / ℹ fail N」，tap reporter 为「# pass N / # fail N」
pass=$(echo "$out" | grep -oE '(ℹ|#) pass [0-9]+' | grep -oE '[0-9]+' | tail -1)
fail=$(echo "$out" | grep -oE '(ℹ|#) fail [0-9]+' | grep -oE '[0-9]+' | tail -1)
echo ""
echo "${pass:-0} passed, ${fail:-0} failed"

[ "${fail:-0}" -eq 0 ] && [ "$code" -eq 0 ] || exit 1
exit 0
