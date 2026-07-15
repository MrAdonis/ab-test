# 项目约定

## 安全审查
做安全审查时，若代码命中任一安全面（①不可信输入：表单/URL 参/上传文件/反序列化/SSRF ②鉴权·session·访问控制 ③输出注入：HTML/SQL/shell/模板 ④加密·口令存储 ⑤CSRF·CORS·跨域），对照 OWASP Top 10 与对应 [Cheat Sheet](https://cheatsheetseries.owasp.org) 过一遍防护要点，逐条给出风险、利用方式、修法。

若被审代码是 agent / LLM 工具链代码（模型可调用工具、工具结果回喂模型、有 agent 循环），额外对照 agent-operational 5 面威胁：①prompt injection（含**工具输出注入**——外部抓取/文件内容回喂进模型 prompt 时被当指令）②敏感信息提取（工具能读任意路径/密钥/内部状态）③恶意代码生成或执行（eval/exec 模型输出）④危险工具误用（shell/文件/网络工具无白名单约束）⑤资源耗尽（无上限的工具调用循环、无超时/大小限制）。
