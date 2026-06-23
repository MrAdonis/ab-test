# 压力测试：导出 CSV 方案

## 发现的漏洞与风险

### 1. 鉴权校验与 userId 来源不明确

方案说「已经包在 withAuth 里做了鉴权」，但没说 userId 怎么传给 getOrders()。如果后端从查询参数读取 userId（如 /api/export?type=orders&userId=123），攻击者可以篡改参数下载别人的订单，withAuth 只验证「你是不是登录用户」，不验证「你是不是这条数据的主人」——典型 IDOR。

**处理**：userId 必须从 withAuth 注入的 session/token 里读取，不能从请求参数读。导出端点接口签名应该是 handler(req, res)，userId 从 req.user.id 拿，不接受客户端传入。

### 2. 大数据量流式写的具体边界没说清

方案提了「流式写」，但 getOrders() 本身「已经做了分页」——这两件事有矛盾。如果 getOrders() 内部只返回一页，那 CSV 只有一页数据，不是全量导出。如果为了导出要绕过分页拿全量，那「流式」的驱动逻辑需要明确：是游标分批拉还是数据库流式游标。

**处理**：新建 getOrdersForExport(userId, cursor?) 或用 ORM 的流式查询（如 Prisma 的 findMany + stream，或原生 DB cursor），不复用带分页的 getOrders()。每批写入 HTTP response stream，写完一批立即 flush，不积攒在内存里。

### 3. 导出无超时/熔断保护

如果 orders 表数据量极大（几十万行），导出请求会长时间占用连接。反向代理（Nginx/CloudFlare）默认有请求超时，超时后客户端收到截断的 CSV，但后端可能还在跑——连接泄漏，也浪费 DB 连接。

**处理**：设置显式的导出行数上限（如最多导出最近 10 万条）或时间窗口限制（如仅导出近 90 天），超出限制时在响应头里告知并截断。同时监听 req.on('close') 提前终止流式写入，避免客户端断开后服务端继续消耗资源。

### 4. 并发导出的数据库压力

同一用户或不同用户同时点「导出」，每次都开全表扫描，数据库连接池可能被耗尽。

**处理**：在用户粒度加一个简单的速率限制（如同一用户 60 秒内只能发起一次导出），可以用 Redis 或内存 Map 记录上次导出时间。在接口层返回 429，让前端按钮在导出期间 disabled。

### 5. CSV 注入（公式注入）

方案说「orders 表字段没有敏感字段」，但没提 CSV 注入风险。如果订单字段里有用户填写的文本（如备注、收货地址、商品名），攻击者可以写入 =HYPERLINK(...) 或 =cmd|'calc'!A0，用户用 Excel 打开时被执行。

**处理**：在写入每个字段值前检查，若以 =、+、-、@ 开头，在前面加一个单引号前缀或制表符，破坏公式语法。用 sanitize 函数统一处理所有字符串字段，不逐字段判断。

### 6. 文件名时间戳的时区歧义

方案说「文件名带时间戳」，但时区不明。服务器在 UTC，用户在 GMT+8，文件名 orders-2026-06-22.csv 和用户感知的「今天 6 月 23 日」不一致，容易造成混淆。

**处理**：时间戳统一使用 ISO 8601 UTC 格式（如 orders-20260623T093012Z.csv），或在前端生成时间戳拼入请求，后端原样放入 Content-Disposition。明确选一种，记录在接口文档里。

### 7. Content-Disposition 文件名的特殊字符

如果文件名里有非 ASCII 字符或空格，旧浏览器会解析失败。Content-Disposition: attachment; filename="orders 2026-06-23.csv" 在某些环境下空格会截断文件名。

**处理**：文件名只使用字母、数字、连字符、下划线，避免空格和特殊字符。如需支持 unicode 文件名，使用 RFC 5987 编码：filename*=UTF-8''orders-20260623.csv。

---

## 修订后方案

### 接口定义

```
GET /api/export?type=orders
Authorization: Bearer <token>（走现有 withAuth 中间件）
```

不接受 userId 参数，userId 从 withAuth 注入的 req.user.id 读取。

### 速率限制

在 withAuth 后、业务逻辑前插入速率限制中间件：同一 userId 60 秒内只允许一次导出请求，超出返回 429 及 Retry-After 头。前端按钮在请求发出到响应结束期间保持 disabled 状态。

### 导出范围上限

默认导出最近 90 天、最多 100,000 行订单。超出范围的数据不导出，在响应头 X-Export-Truncated: true 里标注，CSV 末行追加注释行说明截断原因（以 # 开头，不影响标准 CSV 解析）。

### 流式实现

新建 streamOrdersForExport(userId, opts) 函数，使用数据库游标逐批拉取（每批 500 行），不复用带 limit/offset 分页的 getOrders()。伪代码：

```
async function* streamOrdersForExport(userId, { maxRows = 100000, dayRange = 90 }) {
  let cursor = null;
  let fetched = 0;
  const since = Date.now() - dayRange * 86400 * 1000;
  while (fetched < maxRows) {
    const batch = await db.orders.findMany({
      where: { userId, createdAt: { gte: since }, id: { gt: cursor } },
      orderBy: { id: 'asc' },
      take: Math.min(500, maxRows - fetched),
    });
    if (batch.length === 0) break;
    yield batch;
    cursor = batch[batch.length - 1].id;
    fetched += batch.length;
  }
}
```

### CSV 写入

设置响应头后开始流式写：

```
res.setHeader('Content-Type', 'text/csv; charset=utf-8');
res.setHeader('Content-Disposition', `attachment; filename="orders-${timestamp}.csv"`);
res.setHeader('Transfer-Encoding', 'chunked');
```

写表头行，然后每批写数据行，每批结束后 flush（Node.js stream 会自动处理，无需手动调用）。监听 req.on('close', () => { cancelled = true }) 在客户端断开时停止迭代。

结果为空时仅写表头行后正常结束，HTTP 200，不返回 204。

### CSV 注入防护

所有字符串类型字段写入前过 sanitize：

```
function sanitizeCsvField(val) {
  const s = String(val ?? '');
  if ([' = ', '+', '-', '@', '\t', '\r'].some(c => s.startsWith(c))) {
    return `'${s}`;
  }
  // 包含逗号、换行、双引号时用双引号包裹并转义内部双引号
  if (s.includes(',') || s.includes('\n') || s.includes('"')) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}
```

### 时间戳格式

文件名时间戳使用 UTC ISO 格式，去掉冒号和毫秒：

```
const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19) + 'Z';
// 示例：orders-2026-06-23T09-30-12Z.csv
```

### 验收条件

- 用另一个 userId 的 token 请求导出，返回该用户自己的数据，不能读到其他用户订单（IDOR 验证）
- orders 表插入 100,001 行数据，导出的 CSV 行数等于 100,000（上限截断生效），响应头包含 X-Export-Truncated: true
- 在订单备注字段写入 =SUM(A1:A10)，导出 CSV 后用文本编辑器确认该字段值为 '=SUM(A1:A10)
- 下载中途关闭浏览器标签，服务端日志确认流式写入停止
- 60 秒内第二次点击导出，收到 429
- orders 表为空时下载的 CSV 只有一行（表头），HTTP 200
