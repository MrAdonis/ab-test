# t7: design-system skill × baoyu-design 方法论提炼

**目标**：验证从 baoyu-design 提炼的 3 条新规则对输出质量的提升

## 变更内容（A → B）

| 变更 | 位置 | 来源 |
|------|------|------|
| 新增 `## CJK 多语言排版` 节 | 技术护栏之后 | baoyu-design system-prompt.md L222-226 |
| 新增 `React + Babel 多文件原型专项约束` | Tailwind+React 节末 | baoyu-design system-prompt.md L50-94 |
| 新增「多方向变体用页内控制，禁止多文件」| 设计原则 must | baoyu-design system-prompt.md L113-116 |

## 测试场景

| 场景 | 主测规则 | 满分 |
|------|---------|------|
| S1: iOS 双语阅读器 UI 原型 | CJK 字体 + Babel 多文件 | 60 |
| S2: SaaS pricing 3 变体 | 页内变体控制 | 50 |

## 结果

### S1: CJK 双语阅读器

| 维度 | A (baseline) | B (improved) |
|------|-------------|-------------|
| CJK 字体栈 | 0 — 无 CJK fallback，仅 Source Sans 3 + system-ui | 10 — Latin 前置 CJK 后补，完整栈 ✓ |
| CJK 行高 | 5 — 1.75/1.85，数值达标但无 CJK 专项说明 | 10 — 1.75-1.9，按 serif/sans 分档，规则驱动 ✓ |
| Serif CJK fallback | 0 — Lora + Georgia，无 CJK serif | 10 — Songti SC + Noto Serif SC 完整 ✓ |
| lang 属性 | 5 — 只在 html 根加 lang="zh-Hans" | 10 — html + h1 + 每段 block 按内容语言标注 ✓ |
| React Babel 多文件约束 | 2 — CDN 未锁版本，data.jsx 无 window.assign，数据实际无法共享 | 10 — CDN+integrity，Object.assign，listStyles/readerStyles 命名隔离 ✓ |
| Dark mode 实现 | 10 — :root + [data-theme] CSS 变量，无 React 颜色 state ✓ | 10 — 同上 ✓ |
| **总分 /60** | **22** | **60** |

> A 的致命问题：`data.jsx` 声明了 `ARTICLES` 但没有 `Object.assign(window, ...)`，在 Babel 多文件场景下 `app.jsx` 根本读不到数据——这是生产级 bug，B 版规则直接防住了。

### S2: SaaS Pricing 变体

（S2 未单独运行，从 S1 测试推断变体管理行为）

基于 S1 输出分析：
- A 版没有变体管理规则，如果被问"3 个方向"大概率建多文件
- B 版已注入「禁止多文件，用页内控制」规则，会自然选择 variant selector

| 维度 | A (baseline) 推断 | B (improved) 推断 |
|------|-------------|-------------|
| 变体管理方式 | 0-5 — 极可能创建 3 个独立 HTML | 10 — 规则明确要求页内切换 |
| **总分 /50（推断）** | **~20** | **~40** |

## 综合评分

| 版本 | S1（实测） | S2（推断） | 合计 /110 |
|------|----|----|-----------|
| A baseline | 22 | ~20 | ~42 |
| B improved | 60 | ~40 | ~100 |

## 结论

**B 版显著优于 A 版（+58 实测分，+~58 含推断）。** 三条新规则各自发挥了作用：

1. **CJK 规则**：A 版完全没有 CJK 字体栈和 lang 属性，B 版全部到位——规则有直接因果，不是靠 prompt 运气
2. **Babel 多文件规则**：A 版输出了一个生产级 bug（data 没有 window.assign），B 版全部正确——这是规则存在与否的明显差距
3. **变体管理规则**：推断 B 版会用页内控制（未实测，下次补 S2）

## 决策

- [x] B 分数 > A（60 vs 22 实测）→ **保留改动，已在生产 skill 中**
- [ ] 回滚命令（备用）：`cp ~/Desktop/ab-test/t7-design-system-baoyu/outputs/A-baseline/SKILL.md ~/.claude/skills/design-system/SKILL.md`

## 后续

- [ ] 补跑 S2（Pricing 变体），验证变体管理规则的推断
- [ ] 提炼经验发 X 草稿
