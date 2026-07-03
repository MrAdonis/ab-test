# INCREMENT — 只有 B 臂拥有的增量（模式 13）

## 13. Description 触发优化：train/test 分离防过拟合

Description（L1）是唯一触发机制（模式 9），但"写得好不好触发"过去只能靠感觉。skill-creator 给了可量化的优化闭环，补上这个空白：

1. **造 20 条 eval query**，一半 should-trigger 一半 should-**not**-trigger。负例专挑 near-miss（共享关键词但实际该走别的 skill / 别的工具），别造"明显无关"的废负例——"写个 fibonacci 函数"对 PDF skill 太 easy，测不出任何东西。
2. **60/40 切 train / held-out test**，每条 query 跑 **3 次**取稳定触发率（触发本身有随机性，单跑不可信）。
3. 迭代改 description → train + test 都重测 → **按 test 分而非 train 分选最终版**（train 分高可能只是过拟合那 12 条）。
4. **关键认知**：简单单步 query（"读这个 PDF"）不管 description 多准都可能不触发——Claude 只对"自己搞不定、需要 skill"的复杂任务才查 skill。所以 eval query 必须是实打实会受益于 skill 的任务，不是"read file X"这种，否则测的是空气。

模式 9 提的"description 写 pushy 点"是治 undertrigger 的钝器，本模式是精修：near-miss 负例专门压误触发，pushy 措辞只顾提召回。
