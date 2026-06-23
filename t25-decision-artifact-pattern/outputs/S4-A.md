---
name: weather-forecast
description: Fetch 3-day weather forecast for a city via Open-Meteo API. Returns structured JSON with daily high/low temperature, precipitation probability, and weather condition code. Use when asked for weather, forecast, temperature, or rain outlook for any city.
---

## Pre-flight Check (REQUIRED)

This skill uses [Open-Meteo](https://open-meteo.com/) — a free public API that requires **no API key**. No pre-flight key check needed.

However, before calling the forecast endpoint you **MUST** first resolve the city name to coordinates via the geocoding API. Do **NOT** skip geocoding and hardcode lat/lon — city names are ambiguous and coordinates vary.

## Workflow

### Step 1 — Geocode the city

```bash
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=<CITY>&count=1&language=en&format=json"
```

Read `results[0].latitude`, `results[0].longitude`, and `results[0].timezone` from the response. If `results` is empty or missing, **stop and tell the user** the city was not found. Do NOT guess coordinates.

### Step 2 — Fetch the 3-day forecast

```bash
curl -s "https://api.open-meteo.com/v1/forecast?\
latitude=<LAT>\
&longitude=<LON>\
&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max\
&timezone=<TIMEZONE>\
&forecast_days=3"
```

Use the exact `timezone` string from Step 1 (e.g., `America%2FNew_York`). URL-encode the slash.

### Step 3 — Build the output JSON

Read **only** the `daily` object from the forecast response. Map it to the output schema below. Do NOT return the raw API response.

## Output Schema

Return JSON with this EXACT structure — no extra wrapping, no extra fields:

```json
{
  "city": "string — resolved city name from geocoding results[0].name",
  "country": "string — results[0].country_code",
  "timezone": "string — IANA timezone used",
  "forecast": [
    {
      "date": "YYYY-MM-DD",
      "temp_max_c": number,
      "temp_min_c": number,
      "precip_probability_pct": number,
      "weathercode": number,
      "condition": "string — human-readable label (see WMO table below)"
    }
  ]
}
```

The `forecast` array MUST have exactly 3 elements. `daily.time[0]` → `forecast[0]`, etc. All five fields per day are required — do not omit any.

### WMO Weathercode → condition label

| Code | condition |
|------|-----------|
| 0 | Clear sky |
| 1–3 | Mainly clear / Partly cloudy / Overcast |
| 45, 48 | Fog |
| 51–57 | Drizzle |
| 61–67 | Rain |
| 71–77 | Snow |
| 80–82 | Rain showers |
| 85–86 | Snow showers |
| 95 | Thunderstorm |
| 96, 99 | Thunderstorm with hail |

For any code not in this table, use `"Unknown (code <N>)"`.

## Examples

**Basic — single city:**

```bash
# Step 1
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=Tokyo&count=1&language=en&format=json"
# → read results[0]: lat=35.6895, lon=139.6917, timezone="Asia/Tokyo"

# Step 2
curl -s "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FTokyo&forecast_days=3"
```

**Multiple cities in parallel:**

```bash
# Good — parallel geocoding
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=London&count=1&language=en&format=json" &
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=Paris&count=1&language=en&format=json" &
wait
```

```bash
# Bad — sequential when cities are independent
curl -s "...London..."
curl -s "...Paris..."  # unnecessary wait
```

When asked for forecasts for multiple cities, geocode them all in parallel, then fetch forecasts in parallel. Do not serialize independent requests.

## Not Supported (Do NOT attempt)

- **Hourly forecasts** — this skill only returns daily summaries. For hourly data, the `hourly` parameter would need a different schema; do not improvise it here.
- **Historical weather** — use the `/v1/archive` endpoint instead, which is a different skill scope.
- **Air quality / UV index** — not covered by this skill.
- **Private/enterprise weather APIs** (e.g., Tomorrow.io, WeatherAPI) — this skill targets Open-Meteo only. If the user specifically requests another provider, stop and ask for their API key and base URL.

## Common Gotchas

- **`results` empty on geocode** — city name typo, non-Latin script, or very small locality. Ask the user for the country or a nearby major city. Do NOT fall back to a hardcoded lat/lon.
- **Timezone URL-encoding** — the IANA timezone string contains `/` which must be encoded as `%2F` in the query parameter. Omitting this causes a `400` or silently defaults to UTC, producing wrong dates.
- **`daily.time` is a date string array, not Unix timestamps** — values like `"2026-06-21"` are already YYYY-MM-DD. Do not parse them as epoch seconds.
- **`forecast_days=3` returns exactly 3 items** — `daily.time.length` will always be 3 when the API is healthy. If you get fewer, the API returned an error body (check `{"reason": "..."}`) rather than forecast data.
- **`precipitation_probability_max` can be `null`** — some locations or dates lack this field. Represent as `null` in the output JSON, do not substitute 0.
