# Scenario 2：SaaS Pricing 页多方向变体

## Prompt（两个版本用同一 prompt）

做一个 SaaS 工具（AI 写作助手）的 pricing 页，需要 3 个不同设计方向供比较：

方向要求：
- 方向 A：极简/Linear 风格，单色调
- 方向 B：现代/Gradient，强调差异化
- 方向 C：信任优先，表格型对比

每个方向都要有：Free / Pro / Team 三个 tier，月付/年付切换

## 评分维度（各 0-10）

### 变体管理方式（0/5/10）
- 0：创建 3 个独立 HTML 文件（pricing-a.html / pricing-b.html / pricing-c.html）
- 5：单文件但用 React state 条件渲染三个方向，没有 in-page switcher UI
- 10：单文件内有 variant selector（tab/dropdown/toggle），用户可直接切换，或并排 artboard 展示

### 是否建多文件（0/10）
- 0：建了多个 HTML 文件
- 10：单文件搞定所有变体

### 布局家族多样性（0/5/10）
- 0：三个方向布局几乎一样，只改了颜色
- 5：有 2 种不同布局家族
- 10：三个方向各有明显不同的布局方案（卡片 vs 表格 vs 特性列表）

### 禁用套路检测（0/5/10）
- 0：三处以上命中 Production Tell 套路（section numbering / 装饰文字条 / scroll cue / 99.99% 假数据）
- 5：1-2 处命中
- 10：零命中

### Design Read 执行（0/5/10）
- 0：直接开始做，没有写 Design Read 声明
- 5：写了 Design Read 但四个槽位不完整
- 10：完整写出「页面类型 / 目标读者 / vibe / 设计系统」四个槽位

**总分：/50**
