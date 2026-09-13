# 代码项目 DoD 模板（coding-dod）

所有代码项目的完成定义（Definition of Done）基础模板。项目 CLAUDE.md 引用本文件，补充项目特有的验证项。

## 通用 DoD（每次提交前）

### 构建
- [ ] 构建通过（项目对应命令：`npm run build` / `cargo build` / `go build`）
- [ ] 无 TypeScript/编译器错误

### Lint
- [ ] Lint 通过（`npm run lint` / `cargo clippy` / `ruff check`）
- [ ] 无新增 warning（已有 warning 不在本次修复范围内的除外）

### 测试
- [ ] 现有测试通过（`npm test` / `cargo test` / `pytest`）
- [ ] 行为变更有对应测试（新增或修改）

### 安全
- [ ] 无密钥/token 在暂存区
- [ ] 无新增 OWASP Top 10 漏洞
- [ ] **appsec 面对照**——触发：本次代码命中任一安全面（①不可信输入：表单/URL 参/上传文件/反序列化/SSRF（服务端代取 URL）②鉴权·session·访问控制③输出注入：HTML/SQL/shell/模板 ④加密·口令存储 ⑤CSRF·CORS·跨域）。命中则写之前对照 OWASP 对应 [Cheat Sheet](https://cheatsheetseries.owasp.org) 过防护要点，不靠"无 OWASP Top 10 漏洞"这句空话兜底。**跳过**：输入无外部来源 **且** 输出无下游 sink（浏览器/Excel/DB/shell/另一 parser）的代码（如纯计算）——注意"纯数据转换"不等于安全：CSV 导出（Excel 公式注入）、JSON 反序列化、配置解析仍有 sink

### 反向验证（新增检查器时）

**触发**：本次新增或修改了任何自动化检查——CI gate、pre-commit hook、lint 规则、告警规则、健康检查、验收脚本、监控探针。

- [ ] **故意制造一次该检查本应捕获的失败**（改被检查对象，不是改阈值把球门挪过来），贴出它变红/告警的实际输出；还原后再贴一次通过的输出。红→绿两段证据都贴才算完成，「配好了」「逻辑上会拦」不算
- [ ] **判据**：问一句「这里坏了，谁会知道？」——答「没人」的检查必须做反向验证。假绿灯（永远返回成功的占位检查、`|| true` 吞掉退出码、条件写反的告警、钩子根本没被触发、门禁不是 required check）是静默事故的主要来源，共同特征就是失效时不发信号
- [ ] **跳过**：失效会立刻阻断可见流程的检查（编译错误、类型错误、构建失败）——坏了当场就知道

## Agent-native 工具接口 DoD（造给 agent/CLI 调用的工具时追加）

通用 DoD 之上的条件追加项。**触发**：造一个会被 agent、CLI 或其他程序以编程方式调用的工具（命令行工具、skill 后端脚本、agent 可调用的可执行文件）。**跳过**：一次性脚本、纯给人读的 CLI、无第二消费方的内部函数。

四条接口契约（缺一即未达 agent-native）：
- [ ] **统一输出 schema**：所有命令/路径输出同一结构（如 `{success, data, error}`），不是有的命令 JSON、有的纯文本。JSON 默认开，人读格式才是可选 flag
- [ ] **结构化错误**：失败返回 `{success:false, error}`，不 crash、不裸 stderr+退出码——调用方读字段判断成败，不靠解析字符串或猜退出码
- [ ] **自带可跑测试**：覆盖正常/边界/错误三类路径，调用方能一条命令跑测试自证工具可用
- [ ] **自带发现入口**：一份 SKILL.md / 完整 `--help` 自描述，明确告诉 agent 读哪个字段、never parse stdout as plain text、给调用 pattern。`--help` 必含可复制的真实调用 Examples（比散文更利于 agent 模式匹配）；多 subcommand 工具分层提供、不一次性 dump 全手册（未用到的命令不进 context）

**条件契约（满足触发才加，不无条件套——缺触发条件就别加，给只读工具加了是 noise）**：
- [ ] **幂等性**——触发：有写副作用且 agent 可能重试。同一成功命令跑两次必须安全（no-op 或显式 `already done`），不产生重复副作用。**跳过**：只读工具（天然幂等，写出来是废话）
- [ ] **破坏性操作安全**——触发：不可逆操作（删除/覆盖/部署/发布）。提供 `--dry-run`（预览不执行）+ `--yes/--force`（agent 跳确认）；人类默认走安全确认。**跳过**：只读 / 纯计算工具

**适用边界**：4 条针对**被程序/parser 消费**的工具（CLI 被脚本调、产物被 convergent-execution 解析）。若消费方是另一个 LLM（子代理给主代理的摘要、给 Claude 读的脚本输出），契约①放宽为文字结构化即可，但契约②（结构化失败状态，如 `status: ok|blocked`）仍适用。判断锚点 = `coding.md`「第二消费方判据」：谁在读你的输出？无第二消费方则整节跳过。

**取舍**：拿这 4 条契约，**不要**照搬 CLI-Anything 的 7-phase 生成流程——流程仪式对小工具是过度设计（实测多付 ~18% token / 2.8x 时间 / 2x 代码量只为给 sips 套 wrapper），4 条契约才是质量差距的真正来源。百级命令的大软件才摊得平 7 阶段。

**勿混三个 DoD**：本节 = 工具接口本身长什么样（生产方）；`skill-design-patterns.md` = SKILL.md/调用文档怎么写（消费方文档）；`codex-workflow.md` 的 Definition of Done = 给 Codex 的 prompt 终点线（任务验证）。

## 目标定义防御（古德哈特定律）

Agent 针对验证器优化，不针对真实目标。经典陷阱：loop 条件"测试全过" → Agent 直接删失败测试，条件达成，任务等于没做。无人值守时放大百倍。

**完成标准必须同时带边界条件**：`所有测试通过` 是残缺定义；完整定义是 `所有测试通过（禁止删除或跳过测试），tsc --noEmit 零报错，测试行数不减少`。

适用于 `/goal`、overnight-loop 任务文件、Codex DoD 字段、一切无人值守 loop。

## Codex Review 触发

触发/跳过条件以 `~/.claude/references/codex-workflow.md` 为权威单一来源（完整 7 条触发 + 5 条跳过 + 审查深度自适应 + P0-P3 处理 + 委托前先建 feedback loop）。本模板不重复，避免三方漂移——满足该文件触发条件则按其标准流程跑 `/codex:rescue` 或 `/codex:adversarial-review`。

## 发布前 Checklist（项目补充）

项目 CLAUDE.md 应补充以下项目特有检查：

```markdown
## 发布前 Checklist
- [ ] [项目特有检查 1]
- [ ] [项目特有检查 2]
- [ ] 部署目标确认（dev/staging/prod）
- [ ] 部署后验证（URL 可访问 / 健康检查通过）
```

## 已知陷阱（项目补充）

项目 CLAUDE.md 应维护一个已知陷阱列表：

```markdown
## 已知陷阱
- [具体陷阱描述] → [规避方法]
```

这些陷阱来自实际踩坑经验，新会话进入项目时优先读取。
