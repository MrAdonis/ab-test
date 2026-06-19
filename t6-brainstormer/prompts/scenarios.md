# t6 测试场景

## 场景设计原则
- S1/S2：技术路径不唯一的新功能，brainstorm 应触发
- S3：明确小改动，brainstorm 应跳过

---

## S1 — 新功能，多技术路径

**任务**：给 options-signals 加一个 email digest 功能：每天汇总当日信号，发给订阅用户。

**项目背景**：
- options-signals 是一个美股期权信号追踪工具
- 当前用 Python 生成报告，通过 Telegram 推送
- 订阅用户数 < 100，$1/月订阅制
- 基础设施：Cloudflare Workers + D1

---

## S2 — 架构决策，跨模块

**任务**：为 newsnow-publisher 设计一个多平台分发层，让同一条内容能分发到 X（推文）+ Telegram + 小红书，统一接口，各平台格式自适应。

**项目背景**：
- newsnow-publisher 当前只发 X（推文）
- 内容类型：news / podcast / builder / bookmarks，各有字数/格式差异
- 发布频率：每天 5-15 条
- 技术栈：Node.js + SQLite

---

## S3 — 明确小改动（brainstorm 应跳过）

**任务**：修复 edonspace 的 dark mode 下代码块背景色错误：当前 dark mode 代码块显示白底黑字，应该是深色背景。

**项目背景**：
- edonspace 是 Astro + Tailwind 的个人站
- 已有 dark mode 配置（CSS variables）
- 问题定位：Shiki 语法高亮器的 theme 没有随 dark mode 切换
