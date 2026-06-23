缩放的原因是防止点积值过大导致 softmax 进入梯度消失区。

原文的论证在 3.2.1 节。点积注意力的计算是 QK^T 除以 √d_k 再做 softmax，原文解释说：当 d_k（每个 head 的维度）较大时，点积的量级会随之增大，把 softmax 推到梯度极小的饱和区，反向传播时梯度几乎为零，训练困难。除以 √d_k 把点积压回量级合理的范围，softmax 仍在敏感区间工作。

原文具体说："We suspect that for large values of d_k, the dot products grow large in magnitude, pushing the softmax function into regions where it has very small gradients. To counteract this effect, we scale the dot products by 1/√d_k."

为什么是 √d_k 而不是别的？原文给了统计直觉：假设 Q 和 K 的分量是均值 0、方差 1 的独立随机变量，那么点积 q·k = Σ q_i k_i 的均值是 0，方差是 d_k。标准差就是 √d_k，所以除以 √d_k 把方差归一化回 1，点积分布不随维度增大而撑开。

多头的动机是另一回事——原文说单头注意力在 d_model 维度下做一次，不如把它投影到 h 个低维子空间分别做注意力再拼接，让模型从不同表示子空间联合关注不同位置的信息。缩放是点积注意力本身的数值稳定手段，和多头无关，两件事不要混。
