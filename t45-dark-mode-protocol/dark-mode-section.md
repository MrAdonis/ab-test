## 暗色模式协议

**适用范围**：产品 UI / 后台 / 消费级 web 页面。海报封面（走 §海报 的暗色成套规则）、仿印刷编辑风页面、一次性 PNG mockup 不触发本节。

- **默认双模式**：consumer-facing 页面从第一行代码起按亮暗双模式设计，不默认 light-only 或 dark-only。例外：brief 显式锁定单模式，或页面本质是仿印刷编辑风
- **Token 策略二选一，全项目统一不混用**：① Tailwind `dark:` variant（utility-first 项目默认）——每个颜色 utility 配对暗色变体（`bg-white dark:bg-zinc-950`）；② CSS 语义变量（shadcn/ui、Radix 等带主题的组件库）——定义 `--surface` / `--surface-elevated` / `--text-primary` / `--accent` 语义 token，在 `[data-theme="dark"]` 或 `@media (prefers-color-scheme: dark)` 下换值
- **本节不规定具体颜色**——具体色值由 brief 和品牌决定。协议只强制四条硬约束：
  1. **对比度**：正文 WCAG AA 起步，hero 主文案冲 AAA；暗色模式独立验证对比度，不假设亮色值可直接复用
  2. **层级 parity**：亮色下突出的 CTA 在暗色下同样突出，视觉层级在两模式下一致
  3. **品牌保真**：主品牌色在两模式下都可识别，不把品牌色淡化成一片灰
  4. **禁纯黑纯白**：`#000000` / `#ffffff` 杀深度感，用 off-black（zinc-950 一类近黑暖灰）和 off-white
- **页面主题锁**：一页只有一个主题，section 之间不反转——暗色页面所有 section 都暗色，不在中间夹一段米白（反之亦然）；同主题家族内的背景微差允许（`zinc-950` 旁边放 `zinc-900` 没问题，中间翻成 `amber-50` 是坏的）。用带主题系统的库（shadcn `<Theme>` / Radix Themes）时在页面根设一次主题，单个 section 不覆写。刻意的「整页主题切换」叙事装置（一次强转场）每页最多出现一次
- **默认跟随系统**：尊重 `prefers-color-scheme`；只有当某一模式会丢失关键品牌表达时才加手动 toggle
- **两模式都看过才算完**：交付前在两个模式下各自打开检查，只在一个模式下看过的页面不交付
