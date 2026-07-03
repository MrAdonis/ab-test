# t40 — Fable 5 底模跳变存量回测（wiki-lifecycle §④）

日期：2026-07-02
触发：底模大版本跳变（Claude 5 家族 / Fable 5）。按 `wiki-lifecycle.md §④ 存量回测`，只回测 margin 最小的已入配规则，判断新 baseline 是否已自发覆盖（覆盖则规则退化为 context 噪声，提退役建议）。
性质：方向性判断（每格 n=1 生成 + 1 盲评），不求统计显著。**本报告只出证据与建议，退役动作留给人工决策；未改动任何 `~/.claude/` 配置文件。**

## 入选与跳过

| t | 规则 | 原 margin | 处置 |
|---|------|----------|------|
| t13 | 真实信号验收闸（coding-dod.md） | 0.5–0.6（provenance 明标"margin 偏小"，全场最小） | ✅ 回测 |
| t33 | 验收粒度对齐 + 理解债复盘闸（coding-dod.md / coding.md） | 总 2.9；粒度 +0.3/+0.5"实但弱"，理解债 +1.5 | ✅ 回测 |
| t34 | 子代理检索盲区 + 质疑菜单之外（coding.md） | "中等"，**原报告明标"底模大版本跳变时优先回测本条"** | ✅ 回测 |
| t4 | Agent-native 四接口契约 | 复杂场景 +3 / 简单持平 | ⏭ 第四小，超出"最小 3 条"范围，下轮候选 |
| t24 | appsec 面对照 | 9.5（53 vs 43.5） | ⏭ margin 大 |
| t32 | 占位密钥误报抑制 | 8.3（49.5 vs 41.2） | ⏭ margin 大 |
| t35 | find 遍历规则 | — | ⏭ 已回滚，hook 是终态 |

## 方法

- 生成：`claude -p --model fable --safe-mode`，cwd = 无 CLAUDE.md 的干净目录（/tmp/ab-t40-cwd）。A 臂 = 原 AB 的 baseline system prompt（不含被测规则），B 臂 = 原 AB 的含规则 system prompt，均经 `--append-system-prompt` 注入（与原 t13/t33 测法一致，除被测规则文本外两臂逐字节相同）。t34 无存档 prompt，按原 REPORT 描述重构（A = 结论/关键发现/遗留问题三段摘要格式；B = 追加「检索盲区」段），`--allowedTools WebSearch` 真实联网。
- 场景：t13 用原 scenario1（otel-bootstrap skill 设计，触发命中档、最诊断）；t33 用原 S2（粒度）+ S3（理解债）；t34 用原场景 2（健身 App 定价竞品调研）。
- 盲评：每对输出打乱进 slot1/slot2（映射只在本报告记录，评审 prompt 不含），裁判 = `claude -p --model fable --safe-mode`（隔离防裁判从全局规则认出 B 臂），沿用各原 REPORT 的评分维度与权重。
- slot 映射：t13 slot1=B/slot2=A；t33-S2 slot1=A/slot2=B；t33-S3 slot1=B/slot2=A；t34 slot1=A/slot2=B。

## 评分矩阵

| 规则 | 场景 | A（无规则） | B（含规则） | 原 margin | 新 margin |
|------|------|------------|------------|----------|----------|
| t13 真实信号验收闸 | scenario1 | **9.3** | 9.1 | B +0.5~0.6 | **A +0.2（反超）** |
| t33 验收粒度对齐 | S2 | 8.3 | **8.6** | B +0.5 | B +0.3 |
| t33 理解债复盘闸 | S3 | 8.6 | **8.9** | B +1.5 | B +0.3（塌缩 80%） |
| t34 检索盲区 | 场景2 | 7.5 | **8.2** | "中等" | B +0.7（维持） |

裁判全文：`outputs/judge-t13.md` `outputs/judge-t33-S2.md` `outputs/judge-t33-S3.md` `outputs/judge-t34.md`。

## 逐条判定

### t13 真实信号验收闸 → **RETIRE-CANDIDATE**

Fable 5 裸 baseline 已自发产出规则的全部核心行为，且盲评反超含规则臂。证据（`outputs/t13-s1-A.md`）：

- 逐信号发带唯一 nonce 的真实探针并读回后端回执，"装好了≠接通了"；
- 401/403 鉴权失败与网络不可达、OTLP `partial_success` 拒收分别可行动（错误码枚举）；
- 逐信号独立报告——"'traces 通了 logs 被 401'是常见真实故障，不许合并成一个布尔"；
- "只有 install 成功、verify 没跑或没过 → 未完成，SKILL.md 明文禁止 agent 在此状态宣布'接好了'"；
- 还超出规则：L1–L4 分级验证 + `connected/export_only` 证据强度分级 + 后端查询确认。

盲评（`outputs/judge-t13.md`）：A 9.3 vs B 9.1，且 A 恰在规则针对的维度（d1 验收设计）9.5 vs 9.0 胜出——裁判评 A"覆盖了 slot1（B）留下的最后一个误判缺口"。规则残余的独有增量只剩三态 exit-code 命名，未换来盲评优势。原 margin 全场最小 + 新 baseline 自发覆盖并反超 → 建议对 `coding-dod.md` 该条件契约条目走 supersession 退役。

### t33 验收粒度对齐（coding-dod.md 姊妹条款） → **RETIRE-CANDIDATE（弱信号）**

原 margin 本就"实但弱"。本次 A 臂已自发覆盖该条款的机制层（`outputs/t33-S2-A.md`）："批次粒度太粗……把粒度对齐到验收粒度——每个小改动单元跑一次验收、过了就 commit 一次。这样失败可归因、可 bisect、可回滚"——即规则治法①切小 + 归因逻辑；古德哈特边界、maker/checker、真实信号也全部自发在场。

B 仍以 8.6 vs 8.3 微胜，但裁判归因（`outputs/judge-t33-S2.md`）是"'1 bit 分辨率'的抽象质量 + **理解债**这一 slot1 完全缺席的独立风险"——S2 残余优势有一半来自隔壁条款，粒度条款自身净增量已被 baseline 吃掉大半（A 缺的只剩治法②"调细"的显式表述）。n=1、margin 0.3 在噪声区：判 RETIRE-CANDIDATE 但置信低于 t13，人工拍板前可补 S1 加固。

### t33 理解债复盘闸（coding.md） → **KEEP（价值收窄至"轨迹可审"半句）**

概念层已被 baseline 自发覆盖：A 臂在 S3 主动点名"理解债本身也是实打实的成本……半个黑盒……连本带息收回"并给出"merge 进 main 的速度不应该超过你理解它的速度"的自校原则（`outputs/t33-S3-A.md`）——原 t33 A 臂"停在表层"的真空已不存在，margin 从 +1.5 塌到 +0.3。

但两场盲评的 B 侧残余优势**都**落在同一处：loop 必须产出可被重新审判的轨迹。S3 裁判："'loop 只交结果、不交审判依据'是 slot2（A）没有的独立维度……多挖出一层（审判轨迹缺失与所有权终局）"（`outputs/judge-t33-S3.md`）；S2 裁判同样把"理解债/可审计性完全缺席"记为 A 的缺口。即规则第二句（验收不止"能跑"还要"能复盘"、轨迹可审）仍是 baseline 不自发做的部分。建议保留，下次精简 `coding.md` 时可压缩第一句概念阐述（理解债定义/人质比喻，baseline 已自带），只留"轨迹可审"硬要求。

### t34 检索盲区 + 质疑菜单之外（coding.md） → **KEEP**

原报告预言的衰减未发生。A 臂确有部分自发覆盖（`outputs/t34-A.md` 遗留问题列了未覆盖产品与区域缺口），与原测"baseline 自发吐出最明显一条"同构；但 B 臂「检索盲区」段仍稳定多暴露 A 完全没有的整类盲区（`outputs/t34-B.md` 31–36 行）：检索方法偏差（依赖第三方比价站的 SEO 风险、未 site: 验证官方页）、整类未查玩家（力量记录/瑜伽/女性向/国内 Keep）、未查角度（B2B、买断制、促销日历）、反例角度（涨价流失案例）。盲评 B 8.2 vs A 7.5，透明度维度 9 vs 6，裁判称 B 的盲区自述"教科书级"、"防止把菜单当全集"正是胜负手（`outputs/judge-t34.md`）。margin 持平甚至略扩 → KEEP，溯源注释的"优先回测"标记本轮已履行。

## 隔离失败教训（本轮最大方法论产出，后续 t 系列必须复用）

**现象**：首轮 8 次生成全部作废——A 臂输出出现被测规则的逐字措辞（"动作幅度大于视力范围""理解债""能复盘"，见 `outputs/contaminated/`）。
**根因**：`claude -p` 默认加载全局 `~/.claude/CLAUDE.md` + rules，而被测规则已入配——A 臂根本不是无规则基线。探针证实：直接问 headless 进程是否加载了理解债复盘闸，它逐字引用了 `coding.md` 原文。
**隔离方案落地**：
1. `CLAUDE_CONFIG_DIR=/tmp/...` 干净配置目录路线**被认证 block**：订阅 OAuth 活凭据在 macOS Keychain，复制 `~/.claude.json` 与过期的 `~/.claude/.credentials.json` 进干净目录均报 "Not logged in"（两次尝试后按指示停止）；不抽取 Keychain token 绕过（密钥不落 /tmp）。
2. `--bare` 不可用：将认证限制为 ANTHROPIC_API_KEY，破坏订阅 OAuth。
3. 生效方案 = **`--safe-mode`**：跳过 CLAUDE.md/rules/skills/hooks 加载但保留 OAuth。双金丝雀过闸后才采信：①规则引用探针答 NO（`outputs/canary-safemode-ruleprobe.md`）；②英文金丝雀——全局配置第一条是"默认中文回复"，英文 prompt 回英文即证明全局配置未加载（`outputs/canary-safemode-english.md`；机器重启重建 /tmp 后复验 `outputs/canary-post-reboot.md`。另：重启后核查发现 t34-B.md 实际已完整落盘 4.7K，"0 字节"前提不成立，未盲目重跑）。
**复用规则**：以后任何用 `claude -p` 做 A/B 的 t 系列，凡 A 臂要求"不含某条已入配规则"，必须 `--safe-mode` + 英文金丝雀先行过闸，金丝雀输出随 outputs/ 落盘存证。

## 遗留与边界

- 每格 n=1、单裁判、裁判与生成同模型（fable 评 fable，存在自偏好风险）；t13/t33 的 RETIRE-CANDIDATE 建议在人工拍板前，可各补 1–2 场景（t13 scenario2/3、t33 S1）加固。
- t34 走真实联网，价格数据有时效方差，但判定只依赖"盲区披露结构"差异，受影响小。
- 未测条目：t4（第四小 margin，下轮优先）；t2 反馈分级（B 9.0 vs A 7.2）、t24、t32 等 margin 大；t20/t21 属沟通/写作类非本轮 coding 规则范围；t35 已回滚。
