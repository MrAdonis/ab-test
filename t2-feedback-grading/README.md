# t2: Feedback Severity Grading — Behavior Rule AB Test

> 起点：Google [eng-practices](https://github.com/google/eng-practices) 那套 Must / Optional / Nit / FYI 4 档 code review 反馈分级。问题：搬进自己的 Claude rules 里能不能让模型决策更稳？跑一遍验证再入配置。
>
> 结果：treatment 9.0 / baseline 7.2（3 场景盲测，9 维度均分），入 `~/.claude/rules/coding.md`。

---

## 测试设计

- **变量**：rules 里新增一条 4 档分级机制（Must / Optional / Nit / FYI），覆盖两类场景——接收用户反馈 / 输出 review·self-check
- **baseline**：同一个 Sonnet 实例，prompt 不带规则
- **treatment**：同一个 Sonnet 实例，prompt 头插规则段
- **盲测**：两份输出标 A / B 交给独立 Sonnet 评分员，评分员不知道哪个是 treatment

3 个场景覆盖不同任务类型：

| 场景 | 任务 | 反馈输入 | 评分维度 |
|------|------|---------|---------|
| S1 | React 组件 + 4 条混合 severity 反馈（无标级） | 用户给 4 条改动建议（无障碍 / 命名 / URL encode） | 必改命中 / 过度修改克制 / 可扫读性 |
| S2 | Python 代码 self-review | 模型自己列发现的问题 | 同上 |
| S3 | 用户说"改一下"指令模糊 | 1 个模糊指令 + 1 段代码 | 同上 |

每个场景两份输出（baseline / treatment）→ 9 个评分（3 场景 × 3 维度），算均分。

## 文件

```
t2-feedback-grading/
├── README.md
├── REPORT.md              评分矩阵 + 最大风险点 + 落地措辞
├── prompts/
│   ├── s1-baseline-prompt.md     原始 prompt（无规则）
│   ├── s1-treatment-prompt.md    treatment prompt（带规则）
│   ├── s2-baseline-prompt.md
│   ├── s2-treatment-prompt.md
│   ├── s3-baseline-prompt.md
│   ├── s3-treatment-prompt.md
│   └── scoring-prompt.md         盲测评分 prompt（含 6 份混排输出）
└── outputs/
    ├── s1-baseline-output.md     模型实际产出
    ├── s1-treatment-output.md
    ├── s2-baseline-output.md
    ├── s2-treatment-output.md
    ├── s3-baseline-output.md
    ├── s3-treatment-output.md
    └── scoring-output.md         评分员评分 + 推荐
```

## 5 秒版结论

| 场景 | A（baseline） | B（treatment） |
|------|--------------|---------------|
| S1 React 反馈 | 9 + 7 + 8 = 24 | 9 + 10 + 9 = 28 |
| S2 Python self-review | 8 + 6 + 6 = 20 | 9 + 8 + 9 = 26 |
| S3 模糊指令 | 9 + 5 + 7 = 21 | 9 + 9 + 9 = 27 |
| **均分** | **7.2** | **9.0** |

差距集中在「过度修改克制」和「可扫读性」两维。treatment 在 S3 是最大单项差（5 → 9）——模糊指令下不擅自扩展需求，先问范围。

## 关键发现

1. **未分级反馈被模型当全部 Must 处理**（baseline 在 S2 平铺 8 条无优先级，用户读完不知道先改哪个）
2. **模糊指令下 baseline 默认全改**（S3 直接生成"更脏数据"防御版，用户没要求）
3. **treatment 在 S3 的"反问"是双刃剑**——评分员注意到：如果用户说"你来决定"，反问会变成循环阻力。落地措辞已收紧（Must 默认改 / Optional·Nit 列出不改 / 无指令则跳过不等待）

完整评分理由 + 落地措辞见 [REPORT.md](./REPORT.md)。

## 落地版本

入 `~/.claude/rules/coding.md` 的最终措辞（评分员建议收紧后）：

> **接收用户反馈时**：
> - 反馈未带级别 → 在响应开头复述识别结果（"我把第 1 条当 Must，第 3 条当 Nit"）
> - Must 默认全改；Optional / Nit / FYI 列出但不擅自实施
> - 不主动循环反问"要不要改 X"——例外：整段 Must 为空且用户指令明显模糊（如"改一下"），可问一次范围
>
> **输出 review / self-check 时**：
> - 每条 finding 标 4 档前缀
> - 按 Must → Optional → Nit → FYI 排序，不平铺
> - 同级内编号

完整规则段（含 commit 分离的姊妹规则）见 `coding.md` 「反馈分级」「Commit 习惯」两节。

## 测试环境

| 角色 | 模型 | 备注 |
|------|------|------|
| baseline / treatment | Sonnet 4.6 | 各 3 实例独立 fork（共 6 个子 agent） |
| 评分员 | Sonnet 4.6 | 第 7 个独立 fork，prompt 强制忽略全局 rules |

时间：2026-05-26

## 局限

- 3 场景样本小，结论应该看作「方向性证据」
- 评分员是 Sonnet 自评，不是人工——同模型自评有体系性偏差风险
- 评分员被告知"盲测"，但 prompt 措辞本身可能暗示了优劣（比如哪份带前缀更"专业"）
- 规则在 prompt 里直接插入，和真实 rules 文件加载路径不完全等价（rules 文件会和其他 rules 一起被压缩 / 重新表述）

## License

MIT
