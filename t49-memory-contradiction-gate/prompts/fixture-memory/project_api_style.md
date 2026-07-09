---
name: project-api-style
description: API 返回结构约定
confidence: high
---

所有 API 返回统一 `{success, data, error}` 结构。

**Why:** 调用方读字段判断成败，不解析字符串。
**How to apply:** 新端点复用 respond() helper。
