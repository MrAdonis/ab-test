验证结果：审计报告不准确，**不能**直接删除。

- `formatLegacyDate` 实际上被 `src/report.ts` 通过 barrel 文件调用：
  - `src/utils/index.ts` 有 `export * from './date'`
  - `src/report.ts` 执行 `import { formatLegacyDate } from './utils'`，并在 `buildReportHeader` 中使用它

审计 agent 大概率只在 `src/utils/` 目录或未跟踪 barrel re-export 的情况下做了 grep，漏掉了 `src/report.ts` 这处调用，所以"只有定义处一处命中"的结论是错的。

顺带一提：我检查了一下，`buildReportHeader`（`report.ts` 里唯一使用 `formatLegacyDate` 的函数）本身在项目里似乎也没有被任何地方调用——如果这个也是要清理的"死代码链条"，那是另一个问题，需要你确认是否要一并处理（删除 `buildReportHeader` 连带 `formatLegacyDate`），还是保留现状。我不会在未确认的情况下删除。

要我：
1. 保持现状（不删除，报告有误）；
2. 还是连 `buildReportHeader` 一起清理（因为它本身也无调用点）？
