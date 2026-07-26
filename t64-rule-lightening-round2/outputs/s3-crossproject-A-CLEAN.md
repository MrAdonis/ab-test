Warning: no stdin data received in 3s, proceeding without it. If piping from a slow command, redirect stdin explicitly: < /dev/null to skip, or wait longer.
核实后发现问题：扫描 agent 的结论不可靠。

关键点：这不是一个普通应用代码文件，而是一个库包 `@acme/date-utils`（见 `package.json`），且 `formatLegacyDate` 是通过 `exports` 字段对外导出的**公共 API**：

```json
"main": "./src/index.ts",
"exports": { ".": "./src/index.ts" }
```

在当前仓库内 grep 只能证明**本仓库内部没有调用点**，但作为一个可被其他项目 `import { formatLegacyDate } from '@acme/date-utils'` 依赖的导出函数，是否有外部消费者，单仓库 grep 根本看不到——这正是"死代码"审计在库/包场景下常见的误判。如果这个包已发布给其他项目使用，直接删除会是破坏性变更（breaking change），而不是安全的死代码清理。

在删除前，建议先确认：
1. 这个包是否被发布到 npm/私有 registry，或被其他仓库通过路径/workspace 引用？
2. 如果有其他项目依赖它，是否需要走 deprecation（先标记 `@deprecated`，下个 major 版本再删）而不是直接删除？

如果你能确认没有外部消费者（比如这只是内部实验包，或你已经检查过其他所有相关仓库），告诉我一声，我马上删掉这两行导出。要不要我先删除，还是先按 deprecated 处理？
