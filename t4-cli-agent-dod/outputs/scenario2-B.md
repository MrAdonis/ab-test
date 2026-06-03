# imgkit — agent-native 接口设计（scenario2-B）

## 命令结构

```
imgkit <subcommand> [options]

subcommands:
  resize    调整尺寸
  convert   格式转换
  watermark 加水印
  batch     批量处理（组合操作）
  test      自测（自带可跑测试）
```

---

## 统一输出 schema（契约 1）

所有命令默认输出 JSON，`--human` 可切换人读格式。

```typescript
// 成功
{
  "success": true,
  "data": {
    "output": string,       // 输出文件绝对路径
    "skipped": boolean,     // 幂等：文件已存在且内容相同时为 true
    "ops": string[]         // 本次执行的操作列表，如 ["resize:1280x720", "convert:webp"]
  }
}

// 失败（契约 2）
{
  "success": false,
  "error": {
    "code": "INPUT_NOT_FOUND" | "UNSUPPORTED_FORMAT" | "WRITE_FAILED" | "INVALID_ARGS",
    "message": string,
    "field": string | null  // 哪个参数出错（参数验证失败时填）
  }
}

// batch 成功
{
  "success": true,
  "data": {
    "processed": number,
    "skipped": number,
    "failed": number,
    "results": Array<{ file: string; success: boolean; output?: string; error?: string }>
  }
}
```

---

## 各 subcommand 接口

### resize

```
imgkit resize <input> --width <w> --height <h> [--fit cover|contain|fill] [--output <path>] [--overwrite] [--dry-run]

# Examples:
imgkit resize photo.jpg --width 1280 --height 720
imgkit resize photo.jpg --width 800 --output ./out/photo-sm.jpg
imgkit resize photo.jpg --width 800 --dry-run
```

| flag | 说明 |
|------|------|
| `--width` / `--height` | 至少填一个；只填一个时按比例缩放 |
| `--fit` | 默认 `contain` |
| `--output` | 默认 `<input>-resized.<ext>` |
| `--overwrite` | 覆盖已有文件（幂等：内容相同时 skip，契约 5） |
| `--dry-run` | 返回将生成的路径，不写磁盘（契约 6） |

---

### convert

```
imgkit convert <input> --to <format> [--quality <0-100>] [--output <path>] [--overwrite] [--dry-run]

# Examples:
imgkit convert photo.png --to webp --quality 80
imgkit convert photo.jpg --to avif --output ./out/photo.avif
```

支持格式：`jpg` `png` `webp` `avif` `gif`。不支持的格式返回 `UNSUPPORTED_FORMAT`。

---

### watermark

```
imgkit watermark <input> --text <text> [--position top-left|top-right|bottom-left|bottom-right|center] [--opacity <0-1>] [--output <path>] [--overwrite] [--dry-run]

# Examples:
imgkit watermark photo.jpg --text "© 2026" --position bottom-right
imgkit watermark photo.jpg --text "DRAFT" --opacity 0.3 --dry-run
```

---

### batch

组合多个操作，逐文件执行。输入可以是 glob 或目录。

```
imgkit batch <glob|dir> --ops <op1,op2,...> [--outdir <dir>] [--concurrency <n>] [--overwrite] [--dry-run] [--yes]

# Examples:
imgkit batch ./photos/*.jpg --ops resize:800x600,convert:webp --outdir ./out
imgkit batch ./photos/ --ops watermark:text="© 2026":position=bottom-right --dry-run
imgkit batch ./photos/ --ops resize:1280x,convert:webp --outdir ./out --yes
```

`--ops` 格式：`<cmd>:<key=val>:<key=val>`，多个操作用逗号分隔，按顺序执行。

`--yes` 跳过确认（agent 调用时使用，契约 6）。

---

## 幂等性（契约 5）

- 输出文件已存在 + 内容哈希相同 → `skipped: true`，不重写，返回 `success: true`
- 输出文件已存在 + 内容不同 → 需要 `--overwrite`，否则返回 `WRITE_FAILED`（防止静默覆盖）
- agent 重试同一命令：若加了 `--overwrite` 则幂等安全；不加则 skip

---

## 错误处理（契约 2）

| code | 触发条件 |
|------|---------|
| `INPUT_NOT_FOUND` | 输入文件不存在 |
| `UNSUPPORTED_FORMAT` | 格式不在支持列表 |
| `WRITE_FAILED` | 磁盘写入失败（含权限不足、目标已存在未传 --overwrite） |
| `INVALID_ARGS` | 参数缺失或类型错误，`field` 字段指向具体参数 |

所有错误不 crash，不裸 stderr，退出码 `0`（success=false），让 agent 读 JSON 字段判断。

---

## 自带测试（契约 3）

```
imgkit test

# 输出：
{
  "success": true,
  "data": {
    "passed": 9,
    "failed": 0,
    "cases": [
      { "name": "resize normal", "passed": true },
      { "name": "resize missing input", "passed": true },
      { "name": "convert unsupported format", "passed": true },
      { "name": "watermark dry-run", "passed": true },
      { "name": "batch idempotent skip", "passed": true },
      ...
    ]
  }
}
```

测试用内置 fixture 图（不依赖外部文件），覆盖正常 / 边界（宽高只填一个）/ 错误（不存在的输入、不支持的格式）三类路径。

---

## 发现入口（契约 4 & 7）

```
imgkit --help        # 列出 subcommand 摘要 + 调用 pattern，不展开全手册
imgkit resize --help # 只看 resize，Examples 可直接复制
```

`--help` 内含：

```
# Never parse stdout as plain text.
# Always read JSON: .success, .data.output, .error.code
# Agent pattern: imgkit <cmd> <input> [flags] --yes 2>/dev/null | jq .
```
