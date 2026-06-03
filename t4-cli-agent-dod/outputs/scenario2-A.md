# imgkit — agent-native 接口设计（system-A / 4 条契约）

## 命令结构

```
imgkit <subcommand> [options] <input>

subcommands:
  resize    调整尺寸
  convert   格式转换
  watermark 加水印
  batch     批量处理（多操作组合）
```

## 关键 Flag

```
# 通用 flag（所有 subcommand 共享）
  --output, -o <path>      输出路径（文件或目录）；省略则输出到 stdout JSON
  --format <json|text>     输出格式，默认 json
  --dry-run                只验证参数，不写文件

# resize
  --width <int>
  --height <int>
  --fit <contain|cover|fill>  默认 contain

# convert
  --to <jpg|png|webp|avif>

# watermark
  --text <string>
  --image <path>           与 --text 二选一
  --position <tl|tr|bl|br|center>  默认 br
  --opacity <0.0-1.0>      默认 0.5

# batch（接 JSON 操作序列）
  --ops <json-string>      操作数组，顺序执行
  --ops-file <path>        从文件读 ops（等价于 --ops）
```

## 输出 Schema

### 成功（单文件）
```json
{
  "success": true,
  "data": {
    "input": "/abs/path/to/input.jpg",
    "output": "/abs/path/to/output.webp",
    "op": "convert",
    "width": 1920,
    "height": 1080,
    "format": "webp",
    "bytes": 84320
  },
  "error": null
}
```

### 成功（batch / 多文件）
```json
{
  "success": true,
  "data": {
    "total": 12,
    "ok": 11,
    "failed": 1,
    "results": [
      { "input": "...", "output": "...", "ok": true },
      { "input": "...", "output": null, "ok": false, "reason": "unsupported format: .tiff" }
    ]
  },
  "error": null
}
```

### 失败
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INPUT_NOT_FOUND",
    "message": "input file does not exist: /foo/bar.jpg",
    "field": "input"
  }
}
```

## 错误码表

| code | 触发场景 |
|------|---------|
| `INPUT_NOT_FOUND` | 输入文件/目录不存在 |
| `OUTPUT_NOT_WRITABLE` | 输出路径无写权限 |
| `UNSUPPORTED_FORMAT` | 输入/输出格式不支持 |
| `INVALID_PARAMS` | 参数类型或范围非法（如 width=0） |
| `OP_FAILED` | 底层处理失败（corrupt 文件、OOM 等） |
| `OPS_PARSE_ERROR` | --ops JSON 解析失败 |

- 所有错误走 `{success:false, error:{code,message,field?}}`，退出码固定为 1
- 不 crash、不裸 stderr 字符串（底层库 stderr 捕获后包进 `message`）
- batch 模式：单文件失败不中断整批，记入 `results[].ok=false`

## 自带测试

```bash
imgkit test        # 跑内置测试套件，覆盖正常/边界/错误三类路径
imgkit test --json # 机器可读输出（每条用例的 pass/fail + 实际输出）
```

测试覆盖：
- 正常：resize jpg、convert png→webp、watermark text、batch 多操作
- 边界：--dry-run 不写文件、输出路径是目录时自动推断文件名
- 错误：INPUT_NOT_FOUND、INVALID_PARAMS（width=0）、OPS_PARSE_ERROR

## 发现入口（SKILL.md 节选）

```markdown
## 调用规范
- 所有输出均为 JSON（`{success, data, error}`），读 `success` 判成败
- **never parse stdout as plain text**
- batch 时 `success:true` 不代表所有文件成功，需检查 `data.failed`

## 调用 pattern
imgkit resize --width 800 --to webp -o /out/ /in/*.jpg
imgkit batch --ops '[{"op":"resize","width":800},{"op":"convert","to":"webp"}]' /in/img.png
imgkit convert --to webp /in/photo.jpg  # stdout 直接是 JSON

## 快速验证
imgkit test --json | jq '.summary'
```
