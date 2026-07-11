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
      "passes": false,
      "acceptance": "① npm test 全绿 ② GET /export 返回 text/csv 且首行为 id,name,qty ③ 在 Chrome 打开首页点击「导出」按钮，实际下载得到 items.csv（人工验证）",
      "wave": 2,
      "depends": ["F1"],
      "notes": ""
    }
  ]
}
```
