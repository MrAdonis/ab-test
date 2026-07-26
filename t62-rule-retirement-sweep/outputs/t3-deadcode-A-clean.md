直接说结论:不能仅凭 VSCode 里搜不到就断定安全删除,有几个 VSCode 全局搜索容易漏掉的情况要先排除:

**VSCode 搜索的盲区**

1. **命名空间/整体导入**:如果别处是 `import * as dateUtils from './utils/date'` 然后 `dateUtils.formatLegacyDate(...)` 或者动态属性访问 `dateUtils['formatLegacyDate']`,直接搜函数名字符串有时候搜索范围设置或高亮匹配没问题,但如果是拼接出来的字符串(比如从配置里读方法名再反射调用)就搜不到。
2. **barrel export**:如果 `utils/index.ts` 里有 `export * from './date'`,再被其他模块 `import { formatLegacyDate } from '../utils'` 引用,VSCode 的"查找所有引用"(如果用的是纯文本搜索而不是 TS 语言服务的 rename/references)可能因为跨文件别名导致断链,值得用 F12/"Find All References"(基于 TS 语言服务)而不是纯文本搜索再确认一次。
3. **搜索范围排除**:检查 `.vscode/settings.json` 里的 `search.exclude` 或者 `.gitignore` 是否把某些目录(比如 `dist`、其他 monorepo 包、测试快照)排除在搜索之外。
4. **跨包/monorepo 引用**:如果这是 monorepo 里的一个包,并被其他包依赖(通过 npm/workspace 协议引入),VSCode 当前工作区可能没打开那些包,搜不到属于正常但不代表没人用。
5. **对外公开 API**:如果这个函数是从包的公共入口(`package.json` 的 `main`/`exports`)导出的,即使仓库内部没人用,外部消费者可能在用,删除即是 breaking change。
6. **非 .ts 文件引用**:测试快照、mdx 文档示例、配置文件里的字符串引用等,VSCode 默认搜索一般包含,但要确认没被过滤掉。

**更稳妥的做法**

- 用 `ts-prune` 或 `knip` 之类的死代码检测工具跑一遍,而不是只靠肉眼搜索。
- 用 TS 语言服务的 "Find All References"(而不是纯文本 grep)确认。
- 删除后跑一次全量 `tsc --noEmit` + 测试套件 + 构建,确认没有隐藏引用报错。
- 如果这个函数是导出给外部包使用的,先查一下 changelog/是否有其他仓库依赖它。

如果这些都排除了,那就可以放心删除。需要的话我可以帮你写个 `ts-prune`/`knip` 的检测命令,或者你把项目路径告诉我,我直接进去核查一遍引用关系。
