# T5 — Awesome LLM Apps 四方向深挖

触发：[nini@nini_incrypto_](https://x.com/nini_incrypto_/status/2063163274577748195) 推文推荐  
来源：[Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)  
日期：2026-06-07

## 结论速查

| 子测试 | 结论 | 落地状态 |
|--------|------|---------|
| t5a TOON token 优化 | 47.8% token 减少（实测），但当前规模月省 $0.06，不急落地 | 待规模化后接入 |
| t5b 客户A 架构 | Sequential pipeline 15/15 vs flat 11/15，超验收门槛 | **客户A v1 采用此架构** |
| t5c self-improving skill | 自动化找到 1 个手动漏掉的问题；客观 skill 适用，写作类不适用 | 为 /diagram 引入自动化循环（P2）|
| newsnow 管线参考 | 整体架构差距大；FAISS 向量去重可单独引入 backlog.py | P3 |

## 测试材料

```
t5a-toon-stock/
  prompts/           # 测试用数据（模拟 generate.py 输入）
  outputs/
    token_benchmark.md   # 10股/20股/期权链 三组实测数字

t5b-clientA-architecture/
  prompts/
    arm_a_flat.md        # 单 prompt 方案
    arm_b_sequential.md  # Coordinator+Sequential 方案（三 agent）
  outputs/
    wall_mold_comparison.md  # wall_mold_1.jpg 双 arm 完整输出 + 盲评分

t5c-self-improving-skill/
  outputs/
    comparison.md    # 手动 vs 自动化循环，/diagram 三场景对比
```

## 复现方式

**t5b（最有价值）**：
1. 取 `客户A/test-photos/` 任意图片
2. 分别用 `prompts/arm_a_flat.md` 和 `arm_b_sequential.md` 跑（Claude vision）
3. Arm B 需串联三次调用：VisualAssessor → RepairPlanner → QuoteGenerator
4. 按 0-15 分评分矩阵打分

**t5a**：
```python
pip install toonify tiktoken
# 参考 outputs/token_benchmark.md 里的测试脚本
```
