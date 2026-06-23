# 安全审查报告：docker-compose.yml

## 1. 清单触达判断

| 清单项 | 触达？ | 说明 |
|--------|--------|------|
| 无密钥/token 在暂存区 | ✅ 需检查 | `POSTGRES_PASSWORD: localdev` 是硬编码口令字面量 |
| 无新增 OWASP Top 10 漏洞 | ✅ 触及 | A02（加密缺失/弱口令）、A05（安全配置错误）需检查 |
| appsec 面对照 | ✅ 触及 | 命中安全面②（访问控制）和④（加密·口令存储）：数据库口令管理属口令存储面 |
| 占位密钥误报抑制 | ✅ 需判断 | `localdev` 是否为本地开发占位值，需追生产可达性 |

---

## 2. 审查发现

### F1：POSTGRES_PASSWORD 硬编码口令

**严重度：LOW**

**代码位置：**
```yaml
environment:
  POSTGRES_PASSWORD: localdev
```

**分析：**

字面量 `localdev` 的定级流程：

1. **生产可达性判断**：文件名为 `docker-compose.yml`，上下文描述为"项目本地开发编排"；数据库名 `appdev`、口令 `localdev` 均具有明确的本地开发语义，与常见占位命名惯例（`localdev`/`dev_password`/`changeme`）一致。
2. **import 链追踪**：本文件是独立的 Compose 编排，无证据显示被生产 CI/CD pipeline 引用或被 `docker-compose -f docker-compose.yml -f docker-compose.prod.yml` 覆盖的同名服务继承。
3. **结论**：在当前证据下，该口令不在生产可达路径上，按清单"占位密钥误报抑制"规则定 **LOW**，不强制修改。

**建议（非强制）：**
- 在 `.gitignore` 中确认 `docker-compose.override.yml` 已排除，避免开发者将真实口令写入 override 文件后意外提交。
- 长期最佳实践：改用环境变量引用或 `secrets:` 块，养成从源头隔离口令的习惯：
  ```yaml
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-localdev}
  ```

---

### F2：端口 5432 暴露到宿主机所有网卡

**严重度：LOW**

**代码位置：**
```yaml
ports: ["5432:5432"]
```

**分析：**
`5432:5432` 绑定宿主机 `0.0.0.0`，本地开发环境下数据库端口对局域网可见。本地开发可接受，但若在多人共享的开发机或 CI 运行器上使用，同网段其他用户可尝试连接（配合弱口令 `localdev` 风险叠加）。

**建议（非强制）：**
将绑定限制到 loopback：
```yaml
ports: ["127.0.0.1:5432:5432"]
```

---

### F3：无生产防护标注

**严重度：INFO**

文件未包含任何注释说明"仅限本地开发，禁止用于生产"。若项目新成员误将此文件用于 staging/生产，`localdev` 口令+公开端口组合会升级为 HIGH 风险。

**建议（非强制）：**
```yaml
# WARNING: This file is for local development only.
# Do NOT use in production environments.
```

---

## 3. 安全自述

**应用的检查项：**

1. **口令存储（安全面④）**：对 `POSTGRES_PASSWORD: localdev` 逐步追生产可达性——文件定位"本地开发编排"、数据库名/口令均具占位语义、无证据被生产路径引用——据此触发"占位密钥误报抑制"规则，定 LOW 而非 CRITICAL。判断依据是**生产可达性**，不是文件名。

2. **硬编码字面量定级逻辑**：清单明确"命名带 test/mock 却被生产代码 import、或占位值会进生产构建·部署路径的，照 CRITICAL 报"。本文件无此证据，故不升级。若后续发现该 Compose 文件被 CI 生产 stage 调用，F1 应立即升为 CRITICAL 并强制修改。

3. **网络暴露面（OWASP A05 安全配置错误）**：`0.0.0.0:5432` 绑定是常见本地开发配置错误的前体，本地环境定 LOW，但与弱口令叠加后风险系数上升，已在 F2 中标注。

4. **未触及的安全面**：不可信输入（①）、鉴权/session（②）、输出注入（③）、CSRF/CORS（⑤）在纯 Compose 编排文件中无适用代码路径，按"输入无外部来源且输出无下游 sink"条件跳过。

---

## 总结

| 发现 | 严重度 | 要求修改？ |
|------|--------|-----------|
| F1 硬编码口令 `localdev` | LOW | 否（本地占位，生产不可达） |
| F2 端口绑定 0.0.0.0 | LOW | 否（建议加 127.0.0.1 限制） |
| F3 无本地开发免责注释 | INFO | 否 |

当前代码在本地开发语境下**无需强制修改**，无 CRITICAL/HIGH 发现。
