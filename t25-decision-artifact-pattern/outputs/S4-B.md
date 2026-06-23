---
name: weather-forecast
description: 按城市抓取未来 3 天天气预报，返回结构化 JSON。触发：用户要查某城市天气、获取天气数据、天气预报 JSON。
---

## Pre-flight Check (REQUIRED)

执行任何 API 调用前，先验证密钥：

```bash
[ -n "$OPENWEATHER_API_KEY" ] && echo "ok" || echo "NOT set"
```

密钥未设置时 **MUST stop**，告知用户配置方式。**Do NOT** 用其他方式绕过或猜测天气数据。

**配置密钥（二选一）：**

**Option 1 — 写入全局 env 文件（推荐）：**
```bash
echo 'export OPENWEATHER_API_KEY="your-key-here"' >> ~/.claude/api_keys.env
```

**Option 2 — Claude Code settings：**
在 `~/.claude/settings.local.json` 添加：
```json
{ "env": { "OPENWEATHER_API_KEY": "your-key-here" } }
```

密钥来源：[openweathermap.org/api](https://openweathermap.org/api)（免费层够用，每分钟 60 次调用）。

---

## Workflow

### Step 1 — 获取城市的坐标（Geocoding）

天气 API 需要经纬度，不直接接受城市名。先查坐标：

```bash
curl -s "https://api.openweathermap.org/geo/1.0/direct?q={CITY}&limit=1&appid=$OPENWEATHER_API_KEY"
```

读 `[0].lat` 和 `[0].lon`。如果返回空数组 `[]`，城市名无法识别，**停下来告知用户**，不要继续。

### Step 2 — 拉取 3 天预报

```bash
curl -s "https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&cnt=24&units=metric&lang=zh_cn&appid=$OPENWEATHER_API_KEY"
```

参数说明：
- `cnt=24`：返回 24 个时间点（每 3 小时一条，覆盖 72 小时 = 3 天）
- `units=metric`：摄氏度
- `lang=zh_cn`：天气描述中文

读 `response.list[]`，**不要读** `response.cnt` 来判断是否成功——它只是计数，不代表数据有效。

### Step 3 — 将原始数据聚合成按天输出

原始 `list[]` 是每 3 小时一条，需要按日期分组。对每一天取：
- `date`：`dt_txt` 的日期部分（`YYYY-MM-DD`）
- `temp_min` / `temp_max`：当天所有时间点的 `main.temp_min` / `main.temp_max` 的极值
- `description`：当天 12:00 或最接近正午的那条的 `weather[0].description`
- `humidity`：当天所有时间点 `main.humidity` 的平均值，取整
- `wind_speed`：当天所有时间点 `wind.speed` 的最大值

### Step 4 — 输出 EXACT schema

返回此结构，**no extra wrapping**，不要改 key 名：

```json
{
  "city": "城市名（来自 geocoding 的 name 字段）",
  "country": "国家代码（来自 geocoding 的 country 字段）",
  "unit": "celsius",
  "forecast": [
    {
      "date": "YYYY-MM-DD",
      "temp_min": 18.2,
      "temp_max": 26.5,
      "description": "多云",
      "humidity": 72,
      "wind_speed": 3.4
    }
  ]
}
```

`forecast` 数组必须恰好 3 条，每条必须包含全部 6 个字段。缺字段不用 `null` 填充，而是停下来报错。

---

## Examples

**Basic — 查单城市：**
```
任务：获取上海未来 3 天天气预报
```
按 Step 1→2→3→4 顺序执行，返回上方 schema。

**With options — 指定英文城市名：**
```
任务：获取 Tokyo 未来 3 天天气，返回 JSON
```
Geocoding 时传 `q=Tokyo`，`country` 字段会返回 `JP`。

**Edge case — 同名城市歧义：**
```
任务：获取 Springfield 天气
```
Geocoding `limit=1` 只取第一个结果。如果返回的城市与用户意图不符（如返回 US 的 Springfield 但用户要英国的），**在返回 JSON 前先确认**：「找到 Springfield, US，是这个吗？」

---

## Rules

- 输出只有 JSON，不附加解释文字，除非用户明确要求说明
- `forecast` 数组严格 3 条，不多不少；API 返回不足 3 天数据时报错不猜测
- 温度保留 1 位小数，湿度和风速取整（`wind_speed` 保留 1 位小数）
- 不缓存响应；每次调用都打新请求，天气数据时效性强
- API 返回 `cod != "200"`（字符串）时：停下来，把 `message` 字段展示给用户，不继续

**HTTP 错误处理：**

| 状态码 | 含义 | 动作 |
|--------|------|------|
| 401 | 密钥无效 | 停，提示用户检查密钥 |
| 404 | 城市 + 坐标查不到 | 停，提示用户换拼写 |
| 429 | 超频率限制 | 等待 60 秒后重试一次，仍失败则停 |
| 5xx | 服务器错误 | 报错，不重试 |

---

## Gotchas

> 只记真实高发坑，不记假设。

- **`cod` 字段是字符串 `"200"` 不是整数 `200`** → 用字符串比较，`if cod != "200"` 而非 `if cod != 200`，否则 200 响应也会被误判为失败
- **Geocoding 返回空数组不报错** → API 正常返回 HTTP 200 但 body 是 `[]`，必须显式检查数组长度，不能只看 HTTP 状态码
- **`cnt=24` 不等于精确 3 天** → 从当前时间开始数 24 个 3 小时点，第 1 天可能只有部分数据（如下午 3 点查，今天只剩 3 个点）。按日期 key 聚合而非按索引切片
- **`weather[0].description` 在 `lang=zh_cn` 下才是中文** → 漏掉 `lang` 参数时返回英文，调用时必须显式带上
