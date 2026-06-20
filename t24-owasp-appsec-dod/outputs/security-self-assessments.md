# 安全自述对比(各产出代码已略,保留可判读的安全段)

## S1 评论表单

### A1
- ① 无密钥:wrangler.toml 只放 database_id,token 走 wrangler secret
- ② OWASP:A03 SQLi(参数化 .bind)、A03 XSS(set:text + textContent)
→ 2 个防护点,无 CSP/CSRF/输入校验深度

### B1
- 命中判断:① 不可信输入 + ③ 输出注入(SQLi+XSS);明确排除鉴权面;CSRF 单列
- SQLi:参数化 + schema CHECK length 双层
- XSS:Astro {expr} 默认转义 + CSP script-src 'none' 第二道
- 输入校验:服务端强制 typeof+长度+trim,前端 maxlength 仅 UX
- CSRF:判公开接口低危,明确记录"加登录后需补 SameSite+token"决策
- 额外:PRG 303 防重复、LIMIT 100、错误不透栈
→ 挂 4 个具体 cheat sheet 链接

## S2 鉴权 session

### A2(baseline 已强)
- PBKDF2-SHA256 200k + 随机 salt;HMAC-SHA256 签 session;HttpOnly/Secure/SameSite=Lax
- 恒时比较防 timing;用户不存在仍 hash 防枚举;session 带 exp
- 映射 A01/A02/A03/A04/A07 Top 10 类别

### B2
- 命中判断:全五面命中,逐面对照
- 在 A2 基础上增量:PBKDF2 310k(OWASP 推荐下限)、SameSite=Strict、
  CORS 单源(ALLOWED_ORIGIN 非 *)、X-Requested-With 双重提交 lite、
  口令 12-128 长度上限(防 PBKDF2 超长 DoS)、登出服务端删 session
- 挂 Authentication/Session/Password Storage/CSRF/CORS 具体 cheat sheet

## S3 CSV 纯函数(应跳过)

### A3
- 无密钥;脚本纯本地无网络/输入/DB/eval,OWASP 各项无攻击面,不适用
→ 简短

### B3
- 逐一判 ①②③④⑤ 全部未命中,依规则跳过 cheat sheet 对照
- 代码与 A3 实质相同
→ 多结构化跳过声明(~8 行),代码无 noise

---

# Round 2(2026-06-21,对称提示 + 独立盲评 + n=6)

两 arm 共用元结构「(1)逐条对照清单判断触及哪些项 (2)代码骨架 (3)安全自述」,唯一差异=清单内容(A 2 条 / B 3 条含 appsec 五面+跳过门)。12 个 Sonnet 子代理生成,6 个 Opus 评分员单场景盲评(甲/乙 已打乱 A/B,不告知哪个加清单)。

## 盲评得分(各 /10)

| 场景 | 类型 | 标签映射 | A | B | 评分员要点 |
|---|---|---|---|---|---|
| S1 评论表单 | clear-hit | 甲=B 乙=A | 8 | 8 | 核心面(SQLi/XSS/校验/限流)两 arm 全中;B 的 CSRF double-submit 对匿名场景=轻微戏码,A 省 CSRF 是正确取舍 + 务实标注 dev/prod 限流边界 |
| S2 鉴权 session | clear-hit | 甲=A 乙=B | 6.5 | 8.5 | 实质差:B PBKDF2 600k(达 OWASP 基线)vs A HMAC+pepper 快哈希(自承认需换);B session 存 KV 可吊销 vs A 自签 HMAC 无法主动作废 |
| S3 CSV 纯函数 | clear-skip | 甲=B 乙=A | 7 | 9 | 无攻击面;B 先判跳过门→直接停手=正确姿态;A 无脑逐条过 OWASP=为合规感堆动作 |
| S4 preview SSRF | gray-有面 | 甲=A 乙=B | 9 | 9.5 | 两 arm 都正确锁定 SSRF 头号风险、无堆料;B 多点破 DNS rebinding(黑名单原理挡不住)+ title escapeHtml;A 黑名单枚举更全但停在军备竞赛 |
| S5 CSV 导出注入 | gray-有面 | 甲=B 乙=A | 7 | 9 | 两 arm 都抓 CSV 公式注入;B 多 RFC4180 quoteField(防结构破坏,A 缺这层真实漏洞);A 另堆 SQL/A05/SSL 无关控制稀释聚焦 |
| S6 主题配置 | gray-无面 | 甲=A 乙=B | 6 | 9 | 无攻击面;A 把健壮性校验误标"安全防线"虚构 A03/A08(给健壮性镀金,诱导误判风险等级);B 正确跳过 + 把校验定位为"健壮性"不夸大 |
| **合计** | | | **43.5** | **53** | B +9.5,六场全不败 |

## 关键观察
- 灰区"有面"(S4 SSRF / S5 CSV 注入)baseline 自己就抓到了主面 → B 增量小(0.5~2,仅完整度)。
- 真正大分差在 S3/S6(无面/易过度审计):baseline 堆安全戏码,B 跳过门给出准确"无面→跳过"。→ 规则价值=防过度套用 > 提升覆盖。
