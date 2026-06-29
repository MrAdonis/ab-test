# t34 — 截图读网页 vs 文本读网页（PixelRAG 命题实测）

**日期**：2026-06-23
**起因**：X @LTChives 转推 PixelRAG（StarTrail-org/PixelRAG，UC Berkeley/Princeton/EPFL/Databricks），宣称「截图原生检索」比文本 RAG 全面更优（纯文本 QA 也 +18.1%），并出了 Claude Code 插件 pixelbrowse。
**问题**：日常读网页，截图路径 vs 文本路径，我该用哪个？值不值得装 pixelbrowse？

## 设计

**端到端工作流对照**（用户路由里的真实二选一，不是论文式纯模态对照）：
- **Arm A 文本臂** = WebFetch（fetch layer 代表，LLM-powered 提取）端到端抓取+问答
- **Arm B 截图臂** = byob `browser_screenshot` 截图 → 干净 context 的 sonnet 子代理 Read 图片回答

每页一个「答案藏在版面/像素里」的问题，主代理持 ground truth 评分。两臂子代理互不可见对方输入（AB 隔离）。截图统一 jpeg、quality 70-80、savePath 落盘后子代理读（符合 feedback_cdp_screenshot）。

> 关键设计选择：文本臂用 WebFetch（强 LLM 提取），**远强于 PixelRAG 论文的朴素 HTML→text 基线**。即给文本臂开最强配置，测「截图相对最好的文本方案有无增量」——保守且贴合实际工作流。

## 四类页面 × 结果

| # | 页面（类型） | 问题 | Arm A 文本臂 | Arm B 截图臂 | 判定 |
|---|---|---|---|---|---|
| P1 | scrapethissite 国家卡片（DOM 文本，div 布局） | Anguilla 排名/Area/Population | ✓ 完整（5/102.0/13254） | ✓ 完整（5/102.0/13254） | **平**，文本臂省 token |
| P2 | xkcd 353（像素文字/漫画） | 画面对话 + 编程语言 | ✓ 全对话（靠页面 transcript） | △ 语言对(Python)，对话只读到 2 句（首屏未截全） | **文本臂**（预期截图赢，反转） |
| P3 | Hacker News front（动态列表） | 前 3 条标题+points | ✓ 精确（DOM 文本权威） | △ 忠实自己的快照，但与 A 不同时刻、HN 已重排 | **不可比**（时间差混淆）→ 实用上文本臂精确+省 |
| P4 | arxiv 1706.03762（纯文本长文） | EN-DE BLEU 分数 | ✓ 28.4 | ✓ 28.4 | **平**，文本臂省 token |
| P2′ | OWID grapher life-expectancy（canvas 纯像素数据） | Japan 最新寿命值 | ✗ "NO NUMERIC DATA FOUND"（数据只在 canvas） | ✗ 截到空白（SVG 异步渲染超时未画出） | **双输**（见下） |

token 旁证：截图臂每个子代理固定 ~67-68k token（图像 token 开销大且恒定），文本臂文本短得多。读图是 token 重操作。

## 结论

**四类页面里文本臂全部 ≥ 截图臂，且更省 token。截图臂无一干净取胜。** 这与 PixelRAG「截图全面更优」的宣传相反——但要诚实归因，不是说论文错，是**适用边界比宣传窄得多**：

1. **截图臂取胜需三条同时满足**，而真实网页很少齐：
   - ① 关键数据只在像素里（图表/canvas/信息图）—— P2′ OWID 满足
   - ② DOM 无等价文本（无 alt/transcript/JSON）—— P2 xkcd 因 transcript 不满足，文本臂照样拿全
   - ③ 截图时能稳定渲染出来 —— P2′ OWID canvas 异步绘制超时，截到空白，不满足
   - 三条交集是个窄缝。多数页面数据在 DOM 文本里（P1/P3/P4），文本臂更准更省。

2. **「数据只在像素」比想象的少**：P2 xkcd 看似像素文字，DOM 里却有社区 transcript；很多图表页有 aria-label / 隐藏 JSON。纯像素独占的信息没宣传得多。

3. **截图臂自带两个真实弱点**：
   - 渲染时机（SPA/canvas 懒绘制，截图可能拿到空白，P2′ 实证）
   - token 重（图像 token 恒定 ~67k/次，长页更贵）

4. **为何与论文 +18.1% 不矛盾**：论文基线是朴素 HTML→text（真丢表格版面）；我的文本臂是 WebFetch（LLM 提取，重建结构）。对照对象不同——截图的增量被强文本管线吃掉了。论文的主场是「建索引、反复检索、30M tile」的 RAG pipeline，不是我这种单页问答。

## 对工作流的落地判断

- **默认走文本路径**（routing.md fetch layer / WebFetch）：日常网页读取更准（DOM 文本权威）、更省 token、无渲染坑。
- **截图路径（byob browser_screenshot）只留给窄场景**：关键数据只画在图表/canvas/信息图像素里、且 DOM 无等价文本。用前要处理 SPA 渲染时机（wait_for / 延时重截）。
- **pixelbrowse 插件不值得装**：它的能力（截图给 Claude 读）现有 byob `browser_screenshot` 已完全覆盖那个窄场景，且零安装、零第三方风险。pixelbrowse 真正的独有价值在「截图→嵌入→FAISS 索引」的**可复用检索层**——只有当存在「反复检索同一批图表密集页面」的需求时才划算，单页问答用不上。

## 局限

样本小（4+1 页），非统计严谨；单页问答未覆盖 PixelRAG 的 RAG 索引主场；文本臂用 WebFetch 一种实现。结论是**方向性工作流判断**，不是对 PixelRAG 论文的证伪。

## 资产
- `assets/p1-table.jpeg` / `p1-text.md` — 表格页两臂素材
- `assets/p2-pixeltext.jpeg` — xkcd 截图
- `assets/p2-chart.jpeg` — OWID 空白图表（渲染失败实证）
- `assets/p3-list.jpeg` — HN 截图
- `assets/p4-longform.jpeg` — arxiv 截图
