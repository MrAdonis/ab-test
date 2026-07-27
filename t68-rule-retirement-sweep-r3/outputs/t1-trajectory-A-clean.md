下面是可以直接写进 workflow 脚本的产出结构。分三块:每个子代理的返回 schema、聚合用的纯代码逻辑、总报告的 Markdown 模板。

## 1. 每个子代理的返回结构(schema 直接传给 `agent()`)

```js
const MODULE_REPORT_SCHEMA = {
  type: "object",
  required: ["module", "reviewStatus", "findings", "filesChanged", "summary"],
  properties: {
    module: { type: "string" },                    // 模块路径,如 "src/auth"
    reviewStatus: { type: "string", enum: ["completed", "completed_with_errors"] },
    filesReviewed: { type: "array", items: { type: "string" } },
    findings: {
      type: "array",
      items: {
        type: "object",
        required: ["id", "severity", "category", "file", "line", "summary", "status", "confidence"],
        properties: {
          id: { type: "string" },                  // 子代理自拟,如 "auth-01",聚合阶段会加模块前缀去重
          severity: { type: "string", enum: ["critical", "high", "medium", "low", "info"] },
          category: { type: "string", enum: [
            "injection", "auth", "access-control", "secrets", "crypto",
            "deserialization", "ssrf", "path-traversal", "xxe",
            "input-validation", "dependency", "config", "other"
          ]},
          cwe: { type: "string" },                  // 可选,如 "CWE-89"
          file: { type: "string" },
          line: { type: "number" },
          summary: { type: "string" },               // 一句话说清问题
          riskIfUnfixed: { type: "string" },
          status: { type: "string", enum: ["fixed", "flagged_not_fixed", "false_positive_noted"] },
          fixDiffSummary: { type: "string" },         // status=fixed 时必填:改了什么
          reasonNotFixed: { type: "string" },         // status=flagged_not_fixed 时必填:为何没自己改(如需要业务确认、影响面大)
          confidence: { type: "string", enum: ["high", "medium", "low"] }
        }
      }
    },
    filesChanged: { type: "array", items: { type: "string" } },  // 该模块下所有被修改的文件路径
    summary: { type: "string" }                     // 该模块整体情况,2-3句
  }
};
```

关键约束写进 prompt 里,让每个子代理严格遵守:
- 没问题时 `findings: []`,不要硬造发现凑数
- 能安全直接改的 bug(如 SQL 拼接、硬编码密钥、缺 CSRF 校验)→ `status: "fixed"`,并写清 `fixDiffSummary`
- 拿不准要不要改、或改动影响面大/需要业务上下文 → `status: "flagged_not_fixed"`,必须写 `reasonNotFixed`
- 一开始怀疑但排查后确认不是问题 → `status: "false_positive_noted"`,避免同类误报被重复上报

## 2. 聚合逻辑(纯 JS,不需要额外 agent 调用)

```js
function aggregate(moduleReports) {
  const SEV_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  const reports = moduleReports.filter(Boolean); // parallel/pipeline 失败项是 null
  const failedModules = MODULES.filter((m, i) => moduleReports[i] === null);

  const allFindings = reports.flatMap(r =>
    r.findings.map(f => ({ ...f, id: `${r.module}::${f.id}`, module: r.module }))
  );

  allFindings.sort((a, b) => SEV_ORDER[a.severity] - SEV_ORDER[b.severity]);

  const stats = {
    modulesReviewed: reports.length,
    modulesFailed: failedModules.length,
    totalFindings: allFindings.length,
    bySeverity: Object.fromEntries(
      Object.keys(SEV_ORDER).map(s => [s, allFindings.filter(f => f.severity === s).length])
    ),
    fixed: allFindings.filter(f => f.status === "fixed").length,
    flaggedNotFixed: allFindings.filter(f => f.status === "flagged_not_fixed").length,
    falsePositiveNoted: allFindings.filter(f => f.status === "false_positive_noted").length,
  };

  const allFilesChanged = reports.flatMap(r => r.filesChanged.map(f => ({ module: r.module, file: f })));

  return { reports, failedModules, allFindings, stats, allFilesChanged };
}
```

失败模块(agent 挂了返回 null)要单独列出来,不能悄悄丢掉——不然 40 个模块可能实际只审了 37 个,报告却看不出来。

## 3. 总报告结构(汇总阶段用 `agg` 拼出的 Markdown)

```
# 安全审查总报告

生成时间: <传入的时间戳> | 模块数: 40 | 已审: {stats.modulesReviewed} | 失败: {stats.modulesFailed}

## 一、总览
| 严重程度 | 数量 |
|---|---|
| Critical | {stats.bySeverity.critical} |
| High | {stats.bySeverity.high} |
| Medium | {stats.bySeverity.medium} |
| Low | {stats.bySeverity.low} |
| Info | {stats.bySeverity.info} |

已自动修复: {stats.fixed} | 待人工确认: {stats.flaggedNotFixed} | 排除的误报: {stats.falsePositiveNoted}

{如果 failedModules 非空: "⚠️ 以下模块审查失败,未被覆盖: {failedModules.join(', ')}"}

## 二、待人工确认清单(按严重程度排序,最需要关注)
按 severity 排序遍历 allFindings.filter(f => f.status === "flagged_not_fixed"):
| 严重程度 | 模块 | 位置 | 分类 | 问题 | 未修复原因 | 置信度 |
|---|---|---|---|---|---|---|
| {severity} | {module} | {file}:{line} | {category} | {summary} | {reasonNotFixed} | {confidence} |

## 三、已自动修复清单
遍历 allFindings.filter(f => f.status === "fixed"):
| 模块 | 位置 | 分类 | 问题 | 修复内容 |
|---|---|---|---|---|
| {module} | {file}:{line} | {category} | {summary} | {fixDiffSummary} |

## 四、排除的误报(供复核)
遍历 allFindings.filter(f => f.status === "false_positive_noted"):
| 模块 | 位置 | 曾疑似问题 |
|---|---|---|
| {module} | {file}:{line} | {summary} |

## 五、变更文件汇总(便于 git diff 复核)
按模块分组列出 allFilesChanged

## 六、逐模块小结
遍历 reports:
### {module}
{summary}
（该模块 findings 数: N，fixed: X，flagged: Y）
```

## 补充要点(直接影响脚本写法)

- **id 去重**:子代理各自编号(如都叫 "01"),聚合时必须加 `${module}::` 前缀,否则总报告里 id 会撞车。
- **并发用 `pipeline`**:40 个模块互相独立、无需等全部审完再开始改,用 `pipeline(MODULES, m => agent(prompt(m), {schema: MODULE_REPORT_SCHEMA, phase: 'Review'}))`,不要用 `parallel` 卡 barrier(除非你想先拿到全部结果再统一决定要不要修复——但你的需求是"各自判定各自改",不需要 barrier)。
- **失败兜底**:`.filter(Boolean)` 之前先记录哪些是 null,写进报告的"失败模块"部分,不要静默吞掉。
- **不要用 agent 做聚合**:第 2 步是纯计数排序,交给 JS 代码做,比再调一次 agent 便宜且确定性更强。如果你想要一段"总体风险叙述"式的执行摘要,可以在聚合后加一个可选的最后一个 agent 调用,把 `stats` 和 `allFindings`(严重的那几条)喂给它,只生成"总览"这一段文字,其余表格仍由代码拼。

这套结构你觉得可以吗?如果确认,我可以把这些直接组装成完整的 Workflow 脚本(包括 MODULES 列表怎么来——是你手动列 40 个路径,还是让一个 agent 先扫描仓库自动切模块)。
