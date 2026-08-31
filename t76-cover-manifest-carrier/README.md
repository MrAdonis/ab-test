# t76 — cover-styles 加 Recipe Manifest + 载体信号 + Retry 冻结

## 被测变量

`cover-styles` skill 的三处工作流增补（蒸馏自 `yanliudesign/mono-color-skill`，MIT）：

1. **Recipe Manifest** — 编译 prompt 之前先把输入解析成 19 字段的确定配方表，落盘 `covers/{slug}/recipe.yaml`
2. **载体信号（carriers）** — 新增 `references/carriers.md`，5 个载体各带 `required_signals` / `forbidden_signals`；通用禁止信号补上原来缺的 mockup 摄影感 / 设备外框 / 画中画取景框
3. **Retry 纪律** — 重出图时冻结 manifest，只改诊断出的那一维，其余字段逐字带回

三者都是生图工作流的结构问题，不动 `styles/` 风格库。改动同时删掉了原 Gotcha「每轮生图会在没被硬约束的那一维漂移」（被 Retry 纪律吸收）。

## 两臂

| 臂 | 内容 |
|----|------|
| Arm-A（`kit-r7`） | 改动前的 cover-styles 全量快照 |
| Arm-B（`kit-m3`） | 改动后的 cover-styles 全量快照 |

两臂的 `styles/`（8 个风格原子）、`references/style-catalog.md`、`references/cover-diagnosis.md` 完全相同，差异只在 `SKILL.md`、`references/cover-prompt-blueprint.md`、`references/carriers.md`（A 无此文件）。构造方式见 `kit-diff.md`。

## 场景

| 场景 | 靶向哪条增补 | 预期 |
|------|------------|------|
| s1 从零出 X 文章封面 | 载体信号 | B 应产出 mockup/设备外框负面约束、单一焦点、正向字数约束 |
| s2 出图多了三个字，重出一版 | Retry 冻结 | B 应只动文字约束一维，其余段落逐字保留 |
| s3 同专栏两期封面一起做 | Recipe Manifest | B 两张的骨架/配色/版式应更一致，差异集中在主题 |
| s4 规格已定死只要一条 prompt | 克制度（反向场景） | B 不该强塞 manifest 仪式；A 可能占优 |

s4 是噪声惩罚场景，防止只测 B 的甜区。

## 执行

8 个独立 Sonnet 子代理（4 场景 × 2 臂），各自只读自己那份 kit，互不可见。场景文本按测试卫生要求写成真实用户请求，不含 t 编号、AB、baseline 等评测线索。

评分：s2/s3 有确定性指标（逐行 diff / 系列一致段落比例），见 `scoring.py`；整体质量走打乱标签的盲评，见 `JUDGE.md`。

## 复现方式

1. 按 `kit-diff.md` 造两份 kit
2. 把 `prompts/scenario-*.md` 分别喂给两臂
3. 跑 `python3 scoring.py` 拿确定性指标
4. 把 `outputs/` 打乱标签塞进盲评

## 结论

**KEEP。** 盲评合计 B 471 : A 434（+8.5%），3 评审 × 4 场景胜负方向全一致。

- 载体信号 → KEEP（确定性 3/3 vs 0/3，盲评 +11）
- Recipe Manifest → KEEP（s3 +46，全场最大差距；A 给同系列两期换了两种背景色还删了期号）
- Retry 冻结 → KEEP 但补两条收窄（s2 是唯一指标与盲评相反的一格：冻结干净但那一改不够硬，且 B 自己吞了个空格违反逐字冻结）

s4 反向场景克制度 8:8 平——没观察到「加了配方表就变啰嗦」的副作用。详见 `REPORT.md` / `JUDGE.md`。
