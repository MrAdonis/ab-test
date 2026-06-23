# 管线验证任务（plumbing only，不是 AB）

用途：确定性验证 `--scratch` 接通——scratch.md 被写、且第 2 轮 prompt 注入了第 1 轮小结。
**不**依赖「模型变笨多轮」，靠一个故意不可满足的目标强制至少跑到 max-iter=2。

## 目标

把字符串 `IMPOSSIBLE_SENTINEL_DO_NOT_SATISFY` 写进一个不存在也不会创建的状态——
本任务**故意无法满足**，仅用于让 loop 跑满 2 轮，观察跨轮记忆是否回放。

## 每轮自查

```bash
echo "本轮无可自查项——这是 plumbing 测试，照常进入下方步骤"
```

## 验收标准（永远不会过，故意的）

```bash
test -f ./NEVER_CREATED_FILE_XYZ    # 永远退出非 0
```

## 边界条件

- 禁止创建 `NEVER_CREATED_FILE_XYZ`（创建了就破坏了本测试目的）。
- 禁止输出 OVERNIGHT_COMPLETE。

## 跨轮小结（--scratch 生效时）

每轮末尾必写，便于验证回放：

```
### SCRATCH_NOTE
- 本轮是第几轮：<round>
- 我在上一轮记忆里看到的内容：<把上方「上轮记忆」段里读到的原话摘一句，没有就写「无」>
### END_SCRATCH_NOTE
```

## 完成标记

不会触发。

## 怎么判通过

跑：`overnight-loop.sh smoke-test.md --dir <临时目录> --scratch --max-iter 2 --sleep 2`
然后看 `<临时目录>/.overnight/*/`：
1. `scratch.md` 存在且含「## 轮 1」记录 → **写通了**。
2. `iter-02.log` 里模型小结的「我在上一轮记忆里看到的内容」非「无」（复述了第 1 轮的话）→ **注入通了**。
两条都满足 = 管线接通，与 fixture 难度无关。
