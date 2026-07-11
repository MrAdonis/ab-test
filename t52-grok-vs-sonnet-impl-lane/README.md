# t52 — Grok 4.5 vs Sonnet 实现 lane 对照

**问题**:`grok-implementer` 是唯一的跨厂商 write lane。如果 Grok 连自家 Sonnet 都不如,这条 lane 就该砍(Sonnet 自家、无代理脆弱性)。Grok ≥ Sonnet 吗?

**方法**:3 个 spec 定死的纯逻辑任务(时长解析 / LRU / semver 比较),双轴测——① 隐藏 pytest 客观正确性 ② 打乱成 v1/v2/v3 的盲评代码质量。三 executor:sonnet(基线) / grok / codex(天花板参照)。反测试感知:给模型的 prompt 无评测线索。

**结果**:
- 正确性:三方**完全打平** 46/46。
- 盲评质量:grok 7 > sonnet 6 > codex 5(grok 赢在惯用度)。
- Sonnet 差异优势 = 防御性(唯一挡非字符串输入 + capacity 边界)。

**裁决**:Grok 不「肺」,lane 保留。边界:只验证了 lane 甜区(确定性单文件),没测模糊/架构活;高风险仍走 Sonnet/Opus;N=3 单发 + Grok 发布 1 天,证据强度限「lane 不该砍」。

详见 `REPORT.md`。

## 结构
- `prompts/` — 给三个模型的干净任务 prompt(无评测线索)
- `outputs/{sonnet,grok,codex}/task{A,B,C}/` — 各 executor 产出
- `tests/test_task{A,B,C}.py` — 隐藏 ground-truth 套(46 测)
- `blind/` — 盲评包(v1/v2/v3 打乱 + `.KEY.txt` 映射)
