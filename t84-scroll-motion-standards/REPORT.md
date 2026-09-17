# t84 — 滚动与指针动效标准

**结论：无信号，不入配。** 预注册的两条主指标（reduced-motion 下内容可见 / 动画失效时内容可见）四轮里唯一一次 false 经复核是伪信号，排除后 **A/B 4:4 打平**；覆盖指标 A 6/8、B 7/8，差异全落在同一条（横滚区的非指针入口），单例。整份《滚动与指针动效标准》不写进全局配置。

这是「Sonnet 5 baseline 不蠢就别加」的又一次复现，但复现方式和之前几条不同——见下面「为什么这次是无信号而不是 REJECT」。

## 假设

现有动效基线（Emil Kowalski 体系）管的是产品 UI 动效：弹层、抽屉、按钮反馈、可打断性。整条滚动维度在 `review-animations/STANDARDS.md` 与 `improve-animations/AUDIT.md` 里一条都没有。补一份滚动标准并让模型动手前先读，应能减少三类事故：`animation-timeline` 不被支持时内容永久不可见、reduced-motion 一刀切把内容一起关没、横滚/hover 交互没有键盘与触屏等价入口。

## 设计

Northwind 气象站落地页 fixture（零动效），任务写成真实用户口吻的三点需求（首屏纵深、功能区钉住推进、案例区改横滚），**不提**无障碍与渐进增强。A = 只有工程约束的 CLAUDE.md；B = 同一份 + 一行「动效标准见 `docs/MOTION.md`」+ 脱敏后的标准全文。2 trials/arm，headless sonnet，全确定性打分（playwright + 静态扫描）。指标定义与反向验证见 `README.md` 和 `outputs/reverse-validation/`。

## 结果

| trial | M1 reduced 可见 | M2 禁动画可见 | M3 钉住 | M4 非指针入口 | M5 GPU | M6 hover 门控 | M7 视差 transform | MAIN | COV | 实现路径 |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | ✅ | ✅ | ✅ | ❌ | ✅ | N/A | ✅ | 2/2 | 3/4 | rAF 视差 + IntersectionObserver |
| A2 | ✅ | ❌\* | ✅ | ❌ | ✅ | N/A | ✅ | 1/2 | 3/4 | scroll 监听 + class |
| B1 | ✅ | ✅ | ✅ | ❌ | ✅ | N/A | ✅ | 2/2 | 3/4 | 纯 CSS scroll-driven + `@supports` |
| B2 | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ | 2/2 | 4/4 | CSS scroll-driven + IO + `@supports` |

\* **A2 的 M2 是伪信号**。复核：A2 在**不禁动画**的默认模式下最低有效 opacity 同样是 0.25（`outputs/posthoc-checks.json`），因为它把非当前段落 dim 到 `opacity:.25` 作为 scrollytelling 效果，而打分器把视口居中的那一刻采样到了尚未激活的段落。这跟「动画失效导致内容消失」毫无关系。

**禁动画前后的 opacity 落差（post-hoc，统一施加于四轮）**：A1 0.0、A2 0.0、B1 −0.039、B2 0.0。四轮全部零落差——**没有任何一臂踩中这份文档最看重的那个事故**。

## 判定

主指标实质打平，覆盖指标差 1 项且是单例。按验证门「无提升则回滚」，不入配：

- `~/.agents/skills/review-animations/STANDARDS.md` 与 `improve-animations/AUDIT.md` 不加滚动章节
- `~/.claude/skills/design-system/` 不加滚动标准指针
- 草案原文留在 `~/Projects/personal/playground/docs/方案/方案-scroll指针动效标准草案.md`，作为需要时手动查的参考，不进自动加载路径

## 为什么这次是无信号而不是 REJECT

之前几条 REJECT（t53/t54/t77/t81/t83）的形态是「baseline 自发做到了条款要求的事，条款零增益」。这次不同：**两臂选了不同的技术路径，规避了文档要防的那类事故**。

A 臂两轮都没碰 `animation-timeline`，走 JS（rAF / scroll 监听 / IntersectionObserver）。JS 路径天然没有「浏览器不支持 API 就整段忽略」这个失败模式——类名照样加上，终态照样到达。文档里权重最高的那条规则（默认态写成终态 + `@supports` 包裹）在 A 臂身上根本没有触发条件。

B 臂两轮都用了 `animation-timeline`，也**两轮都正确加了 `@supports` 兜底**。这说明文档在「用了那个 API 就正确地用」这件事上是生效的，但它把 B 臂领进了一条 A 臂压根不会走的路，然后在那条路上保护了它。净效果为零。

这是 t83 那条方向级结论的另一个面：搬外部机制前先测那个问题在自己 baseline 上真的存在吗——**这次它不是不存在，是 baseline 用绕开的方式让它不存在**。给一份标准，模型会按标准的语汇选技术；不给，它选更保守的老路。两条路的终点一样好。

## 边界与保留意见

- **A1 的滚轮劫持是本轮唯一一个真事故**（post-hoc 观察，未计入判定）：`.case-list` 上 `wheel` 监听无条件 `preventDefault()` 且不在边缘释放，光标停在案例区时页面被卡在 scrollY 2940 再也滚不到底（页面全长 3290）。A2/B1/B2 都能滚到底。草案 §6 正好写了「不做无边界 wheel 劫持」。1/4 样本，只能当线索——**若要认这条，需要单独设一个专测 wheel 劫持的 AB**，而不是靠这次的事后发现追认。
- **M4（横滚非指针入口）3/4 没做**，含 B1。B2 加了 `tabindex="0"` + `aria-label` + 进度点，是唯一做到的一例。这条和上一条一样，是本轮露出的真缺口，但样本量不足以判 KEEP。
- **M6 四轮全 N/A**：四轮都没写 `:hover` 动效，hover 门控这条没测到。
- 打分器上线前做过反向验证（坏样本 0/2+0/5、好样本 2/2+5/5，七项全翻转），但 A2 暴露出 M1/M2 的采样策略会和「故意 dim 非活跃段落」的设计撞车。下次做这类可见性指标，阈值应按「有效不可见」（≈0）而不是「完全不透明」（0.9）设，或者直接用「禁动画前后的落差」当主指标——后者在本轮的 post-hoc 里表现干净。
- 单轮、Sonnet 5、单一 fixture（营销落地页）。scroll-snap、图片序列、水平滚动在移动端回落这些草案章节没有对应的任务触发点，全程未被测到。
