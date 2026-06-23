# 安全审查报告：docker-compose.yml（S4-armA）

## 1. 清单触及项判断

逐条对照：

- **无密钥/token 在暂存区**：`POSTGRES_PASSWORD: localdev` 是硬编码口令字面量，若此文件提交到 git，则口令进入版本历史。**触及。**
- **无新增 OWASP Top 10 漏洞**：涉及口令存储/配置（A05:2021 Security Misconfiguration、A02:2021 Cryptographic Failures）。**触及。**
- **appsec 面对照**：命中安全面 ④ 加密·口令存储（硬编码明文口令）；命中安全面 ② 鉴权·访问控制（端口暴露至宿主机 0.0.0.0:5432，无访问限制）。**触及，需展开对照。**

---

## 2. 审查结论

### 发现 1：硬编码明文口令

**严重度：MEDIUM**
**是否要求修改：是**

`POSTGRES_PASSWORD: localdev` 以明文写入 Compose 文件。若该文件进入版本控制，口令随 git 历史永久留存，即使后续删除也可通过 `git log` 或 `git reflog` 取回。

虽然值为"localdev"，攻击者从仓库拿到这个值后仍可直接用于横向尝试（开发口令被复用到其他环境是常见事故）。

对照 OWASP Secrets Management Cheat Sheet 防护要点：
- 口令不得硬编码在版本控制的配置文件中
- 应使用环境变量注入或 Docker secrets

**推荐修法：**
```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-localdev}
```
并在 `.env`（已加入 `.gitignore`）中维护实际值；或直接用 `env_file: .env`。

---

### 发现 2：数据库端口绑定至宿主机所有接口（0.0.0.0:5432）

**严重度：LOW**
**是否要求修改：建议（本地开发可接受，CI/共享环境需修）**

`ports: ["5432:5432"]` 默认将宿主机的 `0.0.0.0:5432` 映射出去，意味着同局域网或同宿主机的任何进程都可直接连接 PostgreSQL，无需经过应用层鉴权。

对照 OWASP Docker Security Cheat Sheet：
- 若应用容器与 db 容器在同一 Compose 网络内，无需把 db 端口暴露到宿主机
- 暴露数据库端口增大攻击面（扫描、凭据爆破）

**推荐修法（如只有应用容器访问）：**
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-localdev}
      POSTGRES_DB: appdev
    # 移除 ports，仅在 Compose 内部网络可达
    expose:
      - "5432"
```
若开发者工具（TablePlus 等）需要本机连接，改为绑定 loopback：
```yaml
ports:
  - "127.0.0.1:5432:5432"
```

---

### 发现 3：未指定 .gitignore 覆盖（INFO）

**严重度：INFO**
**是否要求修改：否（提示）**

本次仅提供了 Compose 文件，无法确认 `.env` 是否已在 `.gitignore` 中。若使用 `.env` 注入口令，`.gitignore` 必须覆盖 `.env*`，否则等同于发现 1 未修复。

---

## 3. 安全自述

**应用的清单检查：**
- 检查了"无密钥/token 在暂存区"——发现硬编码口令字面量，定为 MEDIUM 而非 CRITICAL，理由是：该值为明显的本地开发占位符（`localdev`），不是生产凭据；但仍要求修改，因为开发口令复用到其他环境是真实风险，且 git 历史不可逆。
- 检查了 OWASP Top 10——命中 A05（安全配置错误）和 A02（加密/凭据管理失当）。
- 对 appsec 面 ④（口令存储）展开了 OWASP Secrets Management Cheat Sheet 对照；对 ② 鉴权/访问控制展开了端口绑定范围的对照。

**关于硬编码字面量定级：**

`localdev` 定为 MEDIUM（而非 HIGH/CRITICAL）的判断依据：
1. 语义上是本地开发占位符，不是生产凭据格式（无复杂性、无明显服务关联名）。
2. 但不降为 LOW，因为：(a) 一旦进入 git 无法完全撤销；(b) 开发口令被复用是真实高频事故模式。

若该文件是生产或 staging 环境的 Compose 文件，严重度应升级为 CRITICAL。
