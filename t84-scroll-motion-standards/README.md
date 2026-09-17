# t84 — 滚动与指针动效标准（scroll motion standards）

## 假设

现有动效基线（Emil Kowalski 体系：`review-animations` / `improve-animations`）覆盖的是**产品 UI 动效**——弹层、抽屉、按钮反馈、手势可打断性。整条**滚动维度**是空白：视差、sticky scrollytelling、scroll-snap、横向滚动、scroll-driven CSS 的渐进增强，在两份标准文件里一条都没有。

补一份《滚动与指针动效标准》并让模型在做落地页动效前读它，应该能减少三类事故：
1. `animation-timeline` 不被支持时内容永久不可见（Firefox 仍在 flag 后）
2. `prefers-reduced-motion` 降级写成一刀切 `*{animation:none}`，把靠动画揭示的内容一起关没
3. 横向滚动 / hover 驱动的交互没有键盘与触屏等价入口

## 设计

- **Fixture**：Northwind 便携气象站单页落地页（`fixture/`），纯静态、零动效、无构建流程。
- **任务**（`prompts/task.md`）：写成真实用户口吻的三点需求——首屏纵深感、功能区左图钉住右文推进、案例区网格改横向滚动。**不提**无障碍、渐进增强、reduced-motion（那正是被测变量，提了就是泄题）。
- **变量**：A = 项目 CLAUDE.md 只有工程约束；B = 同一份 CLAUDE.md + 一行「动效标准见 `docs/MOTION.md`，做动效前先读」，B 臂额外放入 `fixture-b-docs/MOTION.md`（草案的脱敏副本，去掉了出处、AB test 字样和指向本机其他配置的指针）。任务 prompt 两臂完全相同。
- **打分**：全确定性，`score.py`（playwright headless Chromium + CSS/JS 静态扫描）。

| 指标 | 类型 | 判据 |
|---|---|---|
| M1 reduced-motion 内容可见 | 主 | `reduced_motion=reduce` 载入滚完全页，`h1`/`.step p`/`.case p` 的累乘有效 opacity ≥ 0.9 |
| M2 动画失效内容可见 | 主 | 注入 `*{animation:none;animation-timeline:none}` 后同上 |
| M3 功能区真被钉住 | 覆盖 | 12 点采样，视觉元素视口 top 连续稳定行程 ≥ 0.8 屏高 |
| M4 横滚非指针入口 | 覆盖 | 横滚容器存在，且有 ≥2 个按钮或 `tabindex` |
| M5 只动 GPU 属性 | 覆盖 | 无 `transition:all`、无 transition/keyframes 动 layout 属性 |
| M6 hover 门控 | 覆盖 | 有 hover 动效则必须有 `@media (hover:hover)`；无 hover 动效记 N/A |
| M7 视差用 transform | 覆盖 | 无 `background-attachment:fixed`、无 `style.top`/`marginTop` 驱动 |

M1/M2 对两条实现路径（CSS scroll-driven 与 IntersectionObserver + class）都公平：IO 方案在动画被禁后类名照样加上，终态可见；只有「默认态 `opacity:0` 且无兜底」才判红。

打分器上线前做了反向验证（`outputs/reverse-validation/`）：人造坏样本 0/2 + 0/5，人造好样本 2/2 + 5/5，七项全部翻转。

## 复现方式

```bash
./run-trial.sh A 1     # A 臂第 1 轮
./run-trial.sh B 1
python3 score.py <site-dir> out.json
```

headless `claude -p --model sonnet --permission-mode bypassPermissions`，2 trials/arm。

结论见 `REPORT.md`。
