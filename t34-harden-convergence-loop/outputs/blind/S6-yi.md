# 导出 CSV 功能：硬化后规格

---

## 收敛过程

### 第 1 轮：列举漏洞

**V1 — 大数据量流式未封顶，OOM 仍有路**
- 什么会坏：`getOrders(userId)` 已有分页，但方案没说流式 CSV 是分批拉取还是把所有分页全迭代完再流出。如果实现是"把所有页数据一次迭代到生成器/stream 里"，内存峰值 = 总数据量，流式只是推迟写入而不是减少驻留。
- 条件：用户订单量极大（如数万条），且实现者把分页全量展开后再接 pipe。
- 标注：这是假设，因没读 `getOrders` 实现，不知道它是否返回 cursor 或一次性数组。

**V2 — 没有行数/文件大小上限**
- 什么会坏：单次导出无封顶，超大导出占用数据库连接时间过长、网关超时（通常 30s~60s）、响应被截断但浏览器仍触发"下载完成"，用户拿到残缺 CSV 无感知。
- 条件：订单量达到万级以上，或数据库慢查询场景。

**V3 — Content-Disposition 文件名时间戳编码问题**
- 什么会坏：`Content-Disposition: attachment; filename="orders_2026-06-23T12:00:00.000Z.csv"` 中的冒号在部分浏览器/操作系统（Windows 文件系统）是非法字符，下载时文件名被截断或替换。
- 条件：Windows 用户使用 Chrome/Edge 下载时。

**V4 — 鉴权中间件与流式响应的兼容性（假设）**
- 什么会坏：`withAuth` 如果在 handler 之前读完整 response body（某些框架下鉴权中间件会消费 stream），可能与流式写入冲突，导致 handler 已开始 pipe 后鉴权才报 401，浏览器已收到 200 但 body 被截断。
- 条件：`withAuth` 使用了 `res.end()` 或 buffer 模式而非 next() 透传。
- 标注：假设，未读 withAuth 实现。

**V5 — 并发导出未限速**
- 什么会坏：同一用户（或攻击者用有效 token）并发发起多个导出请求，每个都持有数据库连接 + 流式管道，连接池耗尽。
- 条件：用户快速双击按钮，或脚本重复调用。

**V6 — CSV 注入（公式注入）**
- 什么会坏：若订单字段（如备注、商品名称）包含以 `=`、`+`、`-`、`@` 开头的字符串，Excel/LibreOffice 打开时将其解析为公式。团队审过"没有敏感字段"，但公式注入与字段敏感性无关——任何用户可控的文本字段都是潜在载体。
- 条件：商品名/备注允许用户自由输入，且含上述前缀字符。

**V7 — 空结果表头的列顺序不稳定（假设）**
- 什么会坏：方案要求空时返回只有表头的 CSV，但如果表头是从 `getOrders` 返回的第一行动态推断的，空结果时没有数据行，表头来源不明确，可能返回空文件或报错。
- 条件：实现用 `Object.keys(rows[0])` 推断表头，rows 为空时崩溃。
- 标注：假设。

---

### 第 1 轮：修复或接受

**V1 → 修复**：方案明确要求 `getOrders` 必须以 cursor/offset 模式分批拉取，每批写入流后释放，不得一次性展开所有分页到内存。如果 `getOrders` 当前只返回完整数组，需在 export handler 内改为按页循环调用并逐批 pipe，而不是重用现有的一次性调用。

**V2 → 修复**：增加行数硬上限（如 50,000 行）。超限时：在写入上限行后关闭流，并在 HTTP trailer 或最后一行写入一条注释行（`# Export truncated at 50000 rows`）；同时在按钮侧展示提示"数据量过大，已导出前 50,000 条"。上限值在服务端配置，不硬编码。

**V3 → 修复**：文件名时间戳改用对 Windows 文件系统安全的格式，将 `T` 和 `:` 替换：`orders_20260623_120000.csv`（`YYYYMMDD_HHmmss`），去掉毫秒和时区后缀。

**V4 → 接受的风险**：`withAuth` 已在现有路由中广泛使用，团队无反馈其与流式响应不兼容。如果框架本身支持流式（Node.js `res.write` 或 Web Streams API），`withAuth` 作为 next() 模式不会消费 body。若后续发现兼容问题，解决方案是将鉴权提前到流开始之前同步完成（先验证 token，再开流）。范围：需等实际遇到再修，现有路由无此报告。

**V5 → 修复**：在 export 端点加每用户并发锁，同一 userId 同一时刻只允许 1 个活跃导出请求。用内存 Set 存储活跃 userId，请求开始时加锁，流结束/出错时释放。实现 5 行以内，不引入新依赖。

**V6 → 修复**：CSV 写入时，对每个字段值做公式前缀检测：若字符串以 `=`、`+`、`-`、`@`、`\t`、`\r` 开头，在值外加双引号并在首字符前加单引号（`'`），使其被 Excel 作文本处理。这是 OWASP CSV 注入防护的标准做法，与字段是否"敏感"无关。

**V7 → 修复**：表头必须静态定义，不从运行时数据推断。在代码中维护一个有序的列名数组（如 `['id', 'userId', 'status', 'amount', 'createdAt', ...]`），空结果时直接写这个数组为表头行，不依赖 `rows[0]`。

---

### 第 2 轮：重查修复是否引入新漏洞

**检查 V1 修复（分批拉取）**：按页循环调用 `getOrders(userId, page, pageSize)` 时，如果在循环过程中用户新增了订单，可能导致"幻影行"（新订单插入到已扫描页的排序位置，被跳过或重复）。
→ 这是标准分页一致性问题。修复：在导出开始时记录 `exportStartTime`，每次调用 `getOrders` 传入 `before: exportStartTime` 条件，只导出导出启动前的快照。这需要 `getOrders` 支持时间过滤参数（假设：如不支持，接受风险，记录于下方）。

**检查 V2 修复（行数上限）**：截断后的 CSV 是合法 CSV（有完整表头 + 前 N 行数据 + 注释行），不会破坏文件格式。注释行以 `#` 开头在 Excel 中会作为数据行，可能令用户困惑。
→ 改：超限不写注释行，而是在 HTTP 响应头加自定义 header `X-Export-Truncated: true` 和 `X-Export-Row-Limit: 50000`，前端检测此 header 在下载完成后弹提示。CSV 文件本身保持干净。

**检查 V5 修复（并发锁）**：内存 Set 在多实例部署下失效（进程 A 加锁，请求落到进程 B，锁不共享）。
→ 接受风险：此端点并发压力来自同一用户的误操作（双击），不是高并发攻击向量。多实例场景下最坏情况是同一用户跑 2 个并发导出，数据库连接占用加倍但不会级联崩溃。若未来横向扩展规模需要，升级为 Redis 分布式锁。单实例或小规模部署下内存锁足够。

**检查 V6 修复（公式注入防护）**：加了单引号前缀的字段在 CSV 中形如 `"'=SUM(A1)"`，用编程方式（pandas/csv 库）读取时会带着单引号，可能影响下游数据处理。
→ 接受风险：此端点的主要消费者是人工下载到 Excel/Sheets 查看，不是程序消费。若有程序消费场景，调用方可自行去掉首字符单引号。在 API 文档中注明此防护行为。

**检查 V7 修复（静态表头）**：静态列名数组与数据库实际字段需保持同步，字段改名或新增时容易漂移。
→ 修复：在集成测试中加一个断言：用 `getOrders` 拉一行数据，验证静态列名数组中的每个字段都存在于返回对象的 keys 中。这个测试在字段改名时会失败，强迫人工同步列名。

**检查时间快照修复（分页一致性）**：若 `getOrders` 不支持 `before` 时间过滤，退化为无快照分页，存在幻影行风险。
→ 接受风险：订单表是追加写入的（新订单不改变旧订单的排序），按 `id` 升序分页时幻影行仅在用户在导出进行中下单才出现，且影响仅为该新订单可能被跳过或重复，不影响已有历史订单的完整性。如果 `getOrders` 当前不支持时间过滤，记录为已知限制，不为此改 `getOrders` 接口（范围外）。

第 2 轮未发现新的实质性漏洞，所有新发现均已处理或接受。收敛。

---

## 关闭的漏洞

- `getOrders` 全量展开到内存 → 改为 cursor/分批循环调用，每批写入流后释放
- 无行数上限导致网关超时/文件截断无感知 → 服务端 50,000 行硬上限 + 响应头 `X-Export-Truncated` 通知前端
- 文件名含冒号在 Windows 非法 → 改为 `orders_YYYYMMDD_HHmmss.csv` 格式
- 同一用户并发导出耗尽连接池 → 每用户内存并发锁，同时最多 1 个活跃导出
- 用户可控字段触发 Excel 公式注入 → 以 `=+−@\t\r` 开头的字段值加单引号前缀并双引号包裹
- 空结果时表头来源不定/崩溃 → 表头改为代码中静态定义的有序列名数组
- 静态列名与数据库字段漂移 → 集成测试断言列名数组与 `getOrders` 返回 keys 匹配
- 分页导出中新订单插入导致幻影行 → 导出开始时记录时间戳，若 `getOrders` 支持则传 `before` 过滤
- 截断注释行污染 CSV 格式 → 改用响应头传递截断信息，CSV 本体保持干净

## 接受的风险

- `withAuth` 与流式响应兼容性 → 现有路由无此问题报告，实际遇到时解法明确（先同步鉴权再开流），概率低
- 多实例部署下并发锁失效 → 最坏情况同一用户跑 2 并发，不级联；规模扩展时升 Redis 分布式锁
- 公式防护单引号前缀影响程序消费 → 主要消费者是人工 Excel 查看；程序消费方可自行剥离，API 文档注明
- `getOrders` 不支持时间过滤时的幻影行 → 影响仅限导出期间新下的订单，不影响历史数据完整性；记为已知限制

---

## 最终方案

### 功能范围

在订单列表页增加"导出 CSV"按钮，点击后下载当前用户全部历史订单为 CSV 文件。导出上限 50,000 行，超限时文件仍合法，前端从响应头读取截断标记并提示用户。

### 后端：`GET /api/export?type=orders`

**鉴权**：复用现有 `withAuth` 中间件包裹 handler，在任何流写入之前完成 token 验证。若鉴权失败，返回 401 JSON，不开流。

**并发锁**：模块级维护 `const activeExports = new Set<string>()`（存 userId）。请求进入后先检查 `activeExports.has(userId)`，若已有活跃导出返回 429 `{ error: 'Export already in progress' }`。否则 `activeExports.add(userId)`，在 `finally` 块（流结束或异常）中 `activeExports.delete(userId)`。

**响应头**（在写入任何 body 之前设置）：
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="orders_20260623_143000.csv"
Transfer-Encoding: chunked
Cache-Control: no-store
```
文件名时间戳格式：`orders_YYYYMMDD_HHmmss.csv`，用服务器当前 UTC 时间生成，无冒号、无毫秒、无时区后缀。

**表头**：静态定义列名数组，与 `getOrders` 返回对象字段对应（示例，以实际 orders 表字段为准）：
```js
const EXPORT_COLUMNS = ['id', 'userId', 'status', 'amount', 'currency', 'createdAt', 'updatedAt'];
```
第一个写入流的行是这个数组 join 后的表头行。

**分批拉取与流式写入**：
```js
const PAGE_SIZE = 500;
const MAX_ROWS = 50_000;
const exportStartTime = new Date().toISOString(); // 快照时间点

let page = 0;
let rowsWritten = 0;
let truncated = false;

// 写表头
stream.write(EXPORT_COLUMNS.join(',') + '\r\n');

outer: while (true) {
  const rows = await getOrders(userId, {
    page,
    pageSize: PAGE_SIZE,
    before: exportStartTime,  // 若 getOrders 支持；不支持则省略此参数
  });

  if (rows.length === 0) break;

  for (const row of rows) {
    if (rowsWritten >= MAX_ROWS) {
      truncated = true;
      break outer;
    }
    stream.write(formatCsvRow(row, EXPORT_COLUMNS) + '\r\n');
    rowsWritten++;
  }

  if (rows.length < PAGE_SIZE) break; // 最后一页
  page++;
}

// 写完后在响应 trailer 或 header（需在流结束前 flush）
if (truncated) {
  res.setHeader('X-Export-Truncated', 'true');
  res.setHeader('X-Export-Row-Limit', String(MAX_ROWS));
}
stream.end();
```

注：若框架不支持在流开始后追加 header，将 `X-Export-Truncated` 改为在最终行数写完前提前发送（HTTP/1.1 chunked 允许），或接受 truncated 信息仅靠前端对比行数判断（行数 = MAX_ROWS 即为截断）。

**CSV 字段序列化（`formatCsvRow`）**：
```js
function escapeCsvField(value: unknown): string {
  const str = value == null ? '' : String(value);
  const FORMULA_PREFIXES = ['=', '+', '-', '@', '\t', '\r'];
  
  const needsQuote = str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r');
  const isFormula = FORMULA_PREFIXES.some(p => str.startsWith(p));
  
  if (isFormula) {
    // 防公式注入：加单引号前缀，整体加双引号
    return `"'${str.replace(/"/g, '""')}"`;
  }
  if (needsQuote) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function formatCsvRow(row: Record<string, unknown>, columns: string[]): string {
  return columns.map(col => escapeCsvField(row[col])).join(',');
}
```

**错误处理**：流写入中途出现数据库错误时，调用 `stream.destroy(err)` 中止连接（不写半截文件），并在 `finally` 块释放并发锁。由于响应头已发送（200），无法改回错误状态码，前端应在下载完成后验证文件是否完整（可选：在最后一行写 `# EOF` 标记，前端检查最后一行）。

### 前端：导出按钮

```jsx
const [exporting, setExporting] = useState(false);

async function handleExport() {
  if (exporting) return;
  setExporting(true);
  try {
    const res = await fetch('/api/export?type=orders');
    if (!res.ok) {
      const err = await res.json();
      alert(err.error ?? 'Export failed');
      return;
    }
    
    const truncated = res.headers.get('X-Export-Truncated') === 'true';
    const limit = res.headers.get('X-Export-Row-Limit');
    
    // 触发浏览器下载
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = ''; // 使用服务端 Content-Disposition 的文件名
    a.click();
    URL.revokeObjectURL(url);
    
    if (truncated) {
      alert(`数据量过大，已导出前 ${Number(limit).toLocaleString()} 条订单。如需完整数据，请联系支持。`);
    }
  } finally {
    setExporting(false);
  }
}

<button onClick={handleExport} disabled={exporting}>
  {exporting ? '导出中...' : '导出 CSV'}
</button>
```

### 测试要求

1. **列名漂移测试（集成）**：调用 `getOrders(testUserId)` 拿一行，断言 `EXPORT_COLUMNS` 中每个字段都存在于返回对象的 keys 中。此测试在字段改名时失败，强制同步。

2. **空结果测试**：无订单用户调用 `/api/export?type=orders`，响应为合法 CSV（仅表头行），HTTP 200，无异常。

3. **截断测试**：mock `getOrders` 返回 50,001 行数据，断言响应头含 `X-Export-Truncated: true`，CSV 行数（不含表头）= 50,000。

4. **并发锁测试**：同一 userId 并发发起 2 个请求，第二个应收到 429。

5. **公式注入测试**：订单备注字段值为 `=SUM(A1)`，导出的 CSV 对应字段为 `"'=SUM(A1)"`，不是裸 `=SUM(A1)`。

6. **文件名格式测试**：`Content-Disposition` 文件名匹配正则 `orders_\d{8}_\d{6}\.csv`，无冒号。

---

## 迭代数

2 轮收敛（第 2 轮新发现的幻影行问题和截断注释行问题均已处理，第 2 轮结束后无新实质漏洞）。
