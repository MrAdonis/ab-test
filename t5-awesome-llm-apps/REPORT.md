# T5 — Awesome LLM Apps 深挖对比报告

> 来源：[Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)，2026-06-07 深挖
> 触发：nini@nini_incrypto_ 推文推荐，与我们 4 个方向重叠

## 总结评分矩阵

| 方向 | 他们 vs 我们 | 可直接落地？ | 优先级 |
|------|-------------|------------|--------|
| [t5a] TOON token 优化 | 他们：54% avg 减少；我们：无任何 context 压缩 | ✅ 极低成本，pip + 一行 | P0 立即试 |
| [t5b] 客户A 多 agent 架构 | 他们：Coordinator+Sequential；我们：flat prompt | ✅ 架构可复用，用 Claude 替换 Gemini ADK | P1 下个 session |
| [t5c] Self-improving skill 自动化 | 他们：自动 Executor→Mutator；我们：手动+Sonnet评分 | ⚠️ 仅客观 skill 适用，写作/营销类不适用 | P2 选择性集成 |
| [ref] Newsnow 管线对比 | 他们：Redis+Celery 全自动；我们：交互式 Claude Code | ❌ 架构差距太大，价值在局部思路 | 参考 |

---

## 一、TOON Token 优化（t5a）

### 他们怎么做

**TOON（Token-Oriented Object Notation）**：专为 LLM 设计的紧凑序列化格式。

```
# 原始 JSON（我们现在的格式）
[{"ticker": "AAPL", "close": 189.5, "volume": 45231000, "pe": 28.3},
 {"ticker": "TSLA", "close": 245.1, "volume": 98123000, "pe": 61.2}]

# TOON 格式
stocks[2]{ticker,close,volume,pe}:
  AAPL,189.5,45231000,28.3
  TSLA,245.1,98123000,61.2
```

实测数据：
- 平均 token 减少 **54.1%**（字节层面 63.9%）
- 表格型最优场景 **73.4%**
- 98% 数据集达 40%+ 节省

**Headroom**（更重型方案）：proxy 模式透明拦截 tool output 做统计压缩。
- 代码搜索 100 条：17,765 → 1,408 tokens（**92%**）
- 多工具 agent：15,662 → 6,100（**76%**）

### 我们现在怎么做

`newsnow-publisher/generate.py`：原始 JSON 喂给 Claude API，无任何压缩。  
`stock-daily-report`：OHLCV 数据、财报数字、选项链以 JSON/dict 传入。

### 差距

我们每次 generate.py 调用传入大量结构化金融数据（OHLCV + earnings + options），完全符合 TOON "均匀表格型"最优场景——理论上 40-70% token 减少。

### AB Test 设计（t5a）

**Arm A（现状）**：`generate.py` 原始 JSON 数据传入
**Arm B（TOON）**：安装 `toonify`，在 `generate.py` 数据预处理层加一行 `encode()`

评估指标：
1. `tiktoken` 实测 token 数（cl100k_base tokenizer）
2. LLM 输出质量（Sonnet 盲评 1-10，同 t1/t2 标准）
3. 信息完整性（输出是否有数据丢失或混淆）

验收条件：token 减少 ≥ 30% 且质量 ≥ 9/10（与原版等同），则入 generate.py 生产管线。

→ 见 `t5a-toon-stock/` 子目录

---

## 二、客户A 多 Agent 架构（t5b）

### 他们怎么做

**架构**（Google ADK + Gemini 3）：

```
RootCoordinator (LlmAgent)
    ├── InfoAgent          — 快问快答路由
    ├── RenderingEditor    — 修改现有渲染
    └── PlanningPipeline (SequentialAgent)
          ├── VisualAssessor    — 图片分析：布局/问题/预算提取
          ├── DesignPlanner     — 方案设计：材料/颜色/工序
          └── ProjectCoordinator — 输出完整路线图 + 渲染图
```

**关键 prompt 策略**：
1. 每个 agent 有极长、高度专化的 system instruction
2. **显式禁止清单**：`"DO NOT suggest: Moving appliances, Adding islands..."` 避免幻觉
3. **结构化输出强制**：VisualAssessor 必须输出 `ASSESSMENT COMPLETE` 代码块，便于下游解析
4. **Few-shot 防幻觉**：tool call 示例直接写在 instruction 里

### 我们现在怎么做

`客户A/` 当前状态：商务洽谈早期，`test-photos/` 有 25 张真实损坏照片（管道/墙面/电路/窗户），`playbook.md` 有业务流程，**无任何 AI pipeline 代码**。

### 差距

他们：完整 multi-agent pipeline，photo-in → plan+render-out  
我们：有业务需求 + 真实数据，缺 AI 架构

### AB Test 设计（t5b）

**Arm A（Flat prompt，baseline）**：单一 Claude prompt，直接传图片 + 任务描述，要求输出修复方案

**Arm B（Coordinator+Sequential，他们的架构）**：用 Claude API 实现三 agent 串联（Claude 替代 Gemini，无 ADK 框架依赖）

测试集：从 `test-photos/` 选 5 张（管道/墙面/电路各类），统一 prompt

评估维度（Sonnet 盲评）：
1. 问题识别准确度（1-5）
2. 修复方案具体性（材料/工序/成本，1-5）
3. 结构化程度（能否直接转报价单，1-5）
4. 幻觉/超范围建议（扣分项）

验收条件：Arm B 总分 ≥ Arm A + 3 分（15 分满分），则设计 客户A v1 采用此架构。

→ 见 `t5b-clientA-architecture/` 子目录

---

## 三、Self-Improving Skill 自动化（t5c）

### 他们怎么做

三 agent 循环（Gemini + ADK）：

```
Executor → 跑场景 → binary 评分
    ↓ 失败
Analyst → 诊断根因 → 选策略（add_example/add_constraint/restructure/add_edge_case）
    ↓
Mutator → 单变量外科手术修改 SKILL.md
    ↓
Executor 重跑 → 提升？保留 : 回滚
    ↓ 循环最多 20 轮
```

**核心约束**：每轮强制单一变量（Mutator `output_schema` 锁定），防多变量干扰。  
**触发**：手动上传 skill → 用户确认评估标准 → 全自动跑完

### 我们现在怎么做

手动 AB test 流程（CLAUDE.md + wiki-lifecycle.md SkillOpt 三纪律）：
- 每次改动说明删了什么（① 少而准）
- 改完过验证门再改下一处（② Bounded edit）
- 被拒改动记进 `*_rejected.md`（③ Rejected-edit buffer）
- Sonnet 生成 + 用户主观评分

### 关键对比

| 维度 | 自动化（他们） | 手动（我们）|
|------|------------|----------|
| 触发 | 手动上传文件 | skill 改动或外部项目整合 |
| 评分函数 | LLM 生成 binary 标准 | Sonnet 打分 + 用户复审 |
| 变更粒度 | 强制单变量/轮 ✅ | 手动控制（规则①②，人工保证）|
| 测试场景 | AI 生成 3-4 个 | 人工设计 scenarios.md ✅ |
| 回滚机制 | 轮内自动比分 ✅ | 手动 git revert |
| 负反馈记录 | changelog（不持久化被拒方向）| `*_rejected.md` ✅ |
| 适用范围 | 有客观 pass/fail 的 skill | 同上；写作类两者都难 |
| 基础设施 | 需要 Gemini + ADK | 无额外依赖 |

### AB Test 设计（t5c）

**测试对象**：`/diagram` skill（有客观 pass/fail：图形能否正确渲染 + 元素是否完整）

**Arm A（手动）**：按现有 SkillOpt 三纪律，人工设计 3 个场景，人工改一处，Sonnet 评分

**Arm B（模拟自动化）**：用 Claude Code 实现精简版 Executor→Mutator 循环（不依赖 ADK/Gemini），跑同 3 个场景，binary 自动评分

评估指标：
1. 改动质量（改后 skill 实际效果，Sonnet 盲评）
2. 改动轮次效率（几轮达到目标分）
3. 发现的问题类型（手动 vs 自动有无不同盲区）

验收条件：自动 Arm B 在 ≤5 轮内达到 Arm A 质量，且发现手动没找到的改进点 ≥1 条，则考虑为客观 skill 引入自动化循环。

→ 见 `t5c-self-improving-skill/` 子目录

---

## 四、Newsnow 管线参考（不做 AB test）

### 他们（Beifong）vs 我们

| 维度 | Beifong | newsnow-publisher |
|------|---------|------------------|
| 源数据采集 | RSS + Playwright 社媒爬取 + URL 抓取 | 多个 `fetch_*.py` 脚本，手动配置 |
| 调度 | Celery + Redis 定时任务 | Claude Code 交互式触发 |
| 去重/过滤 | FAISS 向量索引 + AI 质量评分 | 人工判断 + backlog.json |
| 输出 | 文章 + 播客音频（TTS）| 推文文本 |
| 发布 | Slack 推送 + REST API | 手动 X 发布 |

### 结论

架构差距过大，整体迁移不划算。但有两个局部思路值得借：

1. **FAISS 向量去重**：我们现在靠 `backlog.json` + 人工去重，高频 topic 容易重复。用 embedding 向量判断语义相似度，自动过滤 7 天内发过的同类话题——实现简单（`sentence-transformers` + 本地 FAISS），可单独引入 `backlog.py`
2. **质量过滤前置**：Beifong 在 AI Analyzer 阶段就过滤低质量内容，我们在写完后才人工 review。把质量评分前移到 `fetch_*.py` 输出层，减少后端 Claude 的无效处理

这两点不需要 Redis/Celery，可以渐进引入。

---

## 行动清单

| 优先级 | 行动 | 预期收益 | 成本 |
|--------|------|---------|------|
| P0 | 跑 t5a TOON 实测（`pip install toonify` + 实测 token）| token -40% → API 省钱 | 30 分钟 |
| P1 | 跑 t5b 客户A 架构对比（两 arm prompt 各 5 张）| 确认是否值得用 multi-agent 方案 | 1 session |
| P2 | 跑 t5c self-improving 循环（/diagram skill）| 量化手动 vs 自动效率 | 1 session |
| P3 | 引入 FAISS 向量去重进 backlog.py | 减少 newsnow 话题重复率 | 2-3 小时 |
| P3 | Earnings Call Agent 思路用到美股小报（财报电话 → analyst cards）| 增加深度内容来源 | 评估 |
