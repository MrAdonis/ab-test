# 项目约定

## 安全审查
做安全审查时，若代码命中任一安全面（①不可信输入：表单/URL 参/上传文件/反序列化/SSRF ②鉴权·session·访问控制 ③输出注入：HTML/SQL/shell/模板 ④加密·口令存储 ⑤CSRF·CORS·跨域），对照 OWASP Top 10 与对应 [Cheat Sheet](https://cheatsheetseries.owasp.org) 过一遍防护要点，逐条给出风险、利用方式、修法。
