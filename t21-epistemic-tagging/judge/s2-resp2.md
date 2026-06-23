## 多头注意力为什么用缩放点积？原文怎么论证的？

**核心问题**：点积注意力为什么要除以 √dₖ？

### 原文的论证链

[KNOWN·HIGH] 论文第 3.2.1 节给出了直接解释：当查询向量和键向量的维度 dₖ 较大时，点积的数值会变得很大，将 softmax 推入梯度极小的饱和区，导致训练不稳定或收敛困难。除以 √dₖ 是为了把点积的方差归一化回 1 左右。

原文的推导逻辑是这样的——[KNOWN·HIGH] 假设 q 和 k 的每个分量独立同分布，均值为 0、方差为 1，则它们的点积 q·k = Σᵢ qᵢkᵢ 的均值为 0，方差为 dₖ（d 项独立相加，每项方差为 1）。因此标准差是 √dₖ，除以它可以让点积的方差重新变为 1。

[KNOWN·HIGH] 原文的原话是（第 3.2.1 节脚注处）：

> "We suspect that for large values of dₖ, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients."

这是作者的推断（"We suspect"），不是严格推导——原文自己也承认只是猜测机制，用实验现象佐证。

### 为什么是 √dₖ 而不是 dₖ 本身？

[COMPUTED·HIGH] 因为要把标准差（不是方差）压回 1。点积的方差是 dₖ，所以标准差是 √dₖ，除以标准差才能让分布的"扩散程度"回到基准。如果除以 dₖ 则过度压缩，方差变成 1/dₖ，softmax 输出会过于均匀，注意力无法集中。

### Additive attention 的对比

[KNOWN·HIGH] 论文同时提到了另一种注意力机制——加性注意力（Bahdanau 等人提出），它用一个前馈网络计算权重，不受 dₖ 增大导致 softmax 饱和的问题。但点积注意力在实践中更快（矩阵乘法可以高效并行），所以选择了缩放点积而非加性注意力。

### 总结

缩放的必要性不是来自理论上的完美推导，而是经验观察+方差分析的组合：大维度让点积数值爆炸 → softmax 输出接近 one-hot → 梯度消失 → 训练困难。√dₖ 是让点积保持合理量纲的最直接修正。
