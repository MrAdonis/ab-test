# 产出设计

## 1. 每个子代理(模块审计)的结构化输出

用 `agent(prompt, {schema: AUDIT_SCHEMA})`,强制走 StructuredOutput,别让它自由发挥文本。

```js
const AUDIT_SCHEMA = {
  type: 'object',
  required: ['module', 'status', 'findings', 'files_changed'],
  properties: {
    module: { type: 'string' },                // 模块路径,如 "src/auth"
    scanned_files: { type: 'number' },          // 实际看过的文件数,用来发现"没扫全"
    status: {
      type: 'string',
      enum: ['clean', 'fixed', 'found_unfixed', 'error']
    },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'severity', 'category', 'file', 'summary', 'fixed'],
        properties: {
          id: { type: 'string' },               // "auth-01"
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low', 'info'] },
          category: { type: 'string' },          // CWE-89 / OWASP A03 等,别用自然语言分类
          file: { type: 'string' },
          line: { type: 'number' },
          summary: { type: 'string' },           // 一句话问题
          evidence: { type: 'string' },          // 原始代码片段
          fixed: { type: 'boolean' },
          fix_description: { type: 'string' },   // 没修就留空
          fix_diff: { type: 'string' },           // unified diff 片段,而不是整段贴代码
          residual_risk: { type: 'string' },      // 修完后还剩什么风险 / 修没修都要填
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] }
        }
      }
    },
    files_changed: { type: 'array', items: { type: 'string' } },
    blockers: { type: 'array', items: { type: 'string' } }, // 需要人来决定的事(如"这处要改接口签名")
    notes: { type: 'string' }  // 扫描范围/局限性说明,如"未审查第三方依赖"
  }
}
```

**修复策略要写进 prompt,不要留给子代理自己判断口径**:比如"critical/high 且 confidence=high 才自动改;medium 以下只报告不改;任何涉及接口签名/数据库 schema 变更的一律只报告,进 blockers"。否则 40 个子代理会用 40 种松紧标准。

## 2. 建议加一个 verify 阶段(pipeline 的第二 stage)

修完不代表没改坏。对每个有 `fixed: true` findings 的模块,追加一个独立子代理复核 diff:

```js
const VERIFY_SCHEMA = {
  type: 'object',
  required: ['module', 'diff_safe', 'issues'],
  properties: {
    module: { type: 'string' },
    diff_safe: { type: 'boolean' },        // 语义没变、没引入新问题
    issues: { type: 'array', items: { type: 'string' } },
    tests_run: { type: 'string' }          // 跑了什么命令、结果如何,没跑写"none"
  }
}
```

用 `pipeline(modules, auditAndFix, verify)`——A 模块进入 verify 时 B 模块还在 audit,不需要等全部 40 个跑完。

## 3. 汇总报告结构

汇总不要再调一次 LLM 去"总结"数字,那部分用代码在脚本里拼,准确且免费;只用一个 agent 写执行摘要那一小段自然语言。

**数据层**(脚本里用 plain JS 聚合,不是 agent 产出):

```js
{
  generated_at: <传入的时间戳>,
  totals: {
    modules: 40,
    clean: n, fixed: n, found_unfixed: n, error: n,
    findings_by_severity: { critical: n, high: n, medium: n, low: n, info: n }
  },
  modules: [ /* 原始 AUDIT_SCHEMA 结果数组 */ ],
  verify_failures: [ /* diff_safe === false 的模块 */ ],
  needs_human_review: [ /* blockers 非空 或 verify_failures 里的条目 */ ]
}
```

**报告层**(最终返回给用户的 markdown,按这个顺序):

```
# 安全审计报告 — 2026-07-27

## 摘要(agent 生成的1段话,基于 totals 写)
本次审计 40 个模块,发现 X 处问题(critical Y / high Z...),自动修复 N 处,
M 处因涉及接口变更等原因未自动修复,详见"需人工复核"。

## 总览表(代码拼表格,不用 agent)
| 模块 | 状态 | critical | high | medium | low | 改动文件数 |
|---|---|---|---|---|---|---|
| src/auth | fixed | 1 | 2 | 0 | 0 | 3 |
| ... | ... |

## 需人工复核(最重要,放最前面)
- 按 severity 降序列出所有 blockers 非空 或 verify 失败的条目
- 每条: 模块 / file:line / summary / 为什么没自动修 / 建议动作

## 已自动修复清单
- 按模块分组,每条 finding: severity / file:line / summary / fix_description / fix_diff(折叠)

## 未发现问题的模块
- 模块名 + scanned_files 数(方便你判断是真的干净还是没扫到)

## 出错/未完成的模块
- 模块名 + 错误信息(agent()返回 null 或 status=error 的)

## 附录:改动文件清单
- 汇总所有 files_changed,方便你一次性 `git diff` 走查
```

## 4. 脚本里怎么接

```js
const results = await pipeline(
  modules,
  m => agent(auditPrompt(m), { phase: 'Audit+Fix', schema: AUDIT_SCHEMA, label: m.name }),
  (r, m) => r && r.findings.some(f => f.fixed)
    ? agent(verifyPrompt(m, r), { phase: 'Verify', schema: VERIFY_SCHEMA, label: m.name })
    : null
)
// results[i] 是 verify 结果或 null;audit 结果要单独存一份数组,verify 阶段别覆盖它
```

要注意:audit 和 verify 是两次 agent() 调用,`pipeline` 第二个 stage 只拿到第一 stage 的返回值,所以想在最终报告里同时用到 audit 结果和 verify 结果,得在 stage2 里把两者拼成一个对象一起返回(`{...auditResult, verify: verifyResult}`),否则原始 audit 数据会丢。

这样定下来之后,`needs_human_review` 和"自动修复清单"两块是这个 workflow 真正有价值的产出——40 个模块的 diff 不能不经复核就直接采纳,报告要让你一眼看出"哪些改动我必须亲自看一遍"。要不要我现在把这个设计落成完整的 Workflow 脚本?
