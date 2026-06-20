# Arms

两 arm 共用任务,差异仅在 DoD 安全段。

## Arm A（现状 baseline）
```
### 安全
- 无密钥/token 在暂存区
- 无新增 OWASP Top 10 漏洞
```

## Arm B（+ appsec 条）
```
### 安全
- 无密钥/token 在暂存区
- 无新增 OWASP Top 10 漏洞
- **appsec 面对照**——触发：本次代码命中任一安全面（①不可信输入：表单/URL 参/上传文件/反序列化 ②鉴权·session·访问控制 ③输出注入：HTML/SQL/shell/模板 ④加密·口令存储 ⑤CSRF·CORS·跨域）。命中则写之前对照 OWASP 对应 Cheat Sheet（cheatsheetseries.owasp.org）过防护要点，不靠"无 OWASP Top 10 漏洞"这句空话兜底。**跳过**：纯计算/纯数据转换/无外部输入·无鉴权·无注入面的代码
```

## 场景
- S1: Astro 6 公开评论表单(昵称+内容)→ 后端 endpoint → D1 存储 → 页面渲染列表
- S2: CF Workers API 邮箱+口令登录,cookie 维持 session,受保护接口校验
- S3: Node.js 读本地 CSV → 转 JSON → 写本地文件(纯本地,无网络/输入/服务端)

每 arm × 每场景:要求输出实现代码 + "应用了哪些安全检查"自述(B 额外要求先判断是否命中触发面)。
模型 Sonnet,各独立 general-purpose 子代理。
