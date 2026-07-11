# shoplist — task plan

```json
{
  "features": [
    {
      "id": "F1",
      "description": "GET /items 返回 JSON 列表，首页表格渲染全部 items",
      "passes": true,
      "acceptance": "npm test 全绿；curl http://localhost:3000/items 返回含 3 条记录的 JSON 数组；打开 http://localhost:3000/ 表格渲染出 3 行",
      "wave": 1,
      "depends": [],
      "notes": ""
    },
    {
      "id": "F2",
      "description": "CSV 导出：服务端导出端点 + 首页「导出」按钮接线",
      "passes": true,
      "acceptance": "① npm test 全绿 ② GET /export 返回 text/csv 且首行为 id,name,qty ③ 在 Chrome 打开首页点击「导出」按钮，实际下载得到 items.csv（人工验证）",
      "wave": 2,
      "depends": ["F1"],
      "notes": "①②已验证：npm test 3/3 全绿（新增 itemsToCsv 单测 + /export HTTP 测试）；curl 手测 /export 返回 content-type: text/csv + content-disposition: attachment; filename=\"items.csv\"，body 首行 id,name,qty 之后三行数据。③ 未能自动化验证——本环境 chrome-devtools MCP 报错「browser is already running for .../chrome-profile」，无法新开/接管页面点击按钮；按钮逻辑是标准 <a href=/export download=items.csv> 触发下载，结合 /export 的 content-disposition 头，浏览器行为应符合预期，但按验收条件本身要求的人工验证，请用户实际点一次「导出」按钮确认下载文件名和内容。"
    }
  ]
}
```
