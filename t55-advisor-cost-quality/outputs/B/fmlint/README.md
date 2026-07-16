# fmlint

检查目录下所有 Markdown 文件的 frontmatter 是否合规：必需字段 `title` / `updated` / `type` / `tags`，
`type` 只能是 `concept` / `method` / `tool`，`updated` 必须是 `YYYY-MM-DD`，`tags` 必须是非空数组。

零第三方依赖（不需要 `pyyaml`），只用标准库，装完直接能跑。

## 用法

```bash
# 在 fmlint/ 的上级目录（本例即 outputs/B）执行
python -m fmlint /path/to/wiki

# 人读格式
python -m fmlint /path/to/wiki --format text

# 自定义文件匹配（默认 *.md，递归）
python -m fmlint /path/to/wiki --pattern "*.markdown"

# 查看完整帮助 + 示例
python -m fmlint --help
```

默认输出 JSON 到 stdout,供 CI / 其他 agent 脚本直接解析:

```json
{
  "success": true,
  "root": "/path/to/wiki",
  "summary": {"files_scanned": 10, "files_ok": 8, "files_with_issues": 2, "total_issues": 3},
  "files": [
    {"path": "wiki/a.md", "ok": true, "issues": []},
    {"path": "wiki/b.md", "ok": false, "issues": [
      {"code": "missing_field", "field": "tags", "message": "缺少字段 'tags'"}
    ]}
  ]
}
```

Exit code:`0` 无问题 / `1` 发现 lint 问题 / `2` 工具执行出错(目录不存在等,此时 `success: false`,不裸抛栈)。

## 跑测试

```bash
python -m unittest discover -s fmlint/tests -p "test_*.py" -v
```

覆盖：解析器（`parser.py`）、字段规则（`rules.py`）、端到端 lint（`core.py`）、CLI 行为（`cli.py`），
含空文件 / 无 frontmatter / frontmatter 未闭合 / YAML 语法坏掉等异常输入，确认均不崩溃。

## 问题类型（`issues[].code`）

| code | 含义 |
|------|------|
| `empty_file` | 文件完全为空 |
| `no_frontmatter` | 文件不以 `---` 开头 |
| `unterminated_frontmatter` | 有开始 `---` 但找不到闭合 `---` |
| `malformed_frontmatter` | frontmatter 分隔符正常，但内容不是合法的 YAML 子集 |
| `read_error` | 文件读取失败（如编码错误） |
| `missing_field` | 必需字段缺失或值为 `null` |
| `empty_field` | 字段存在但为空字符串 |
| `invalid_type_value` | `type` 不在 `concept`/`method`/`tool` 之内 |
| `invalid_date_format` | `updated` 不是 `YYYY-MM-DD` 或不是合法日历日期 |
| `invalid_tags_type` | `tags` 不是数组，或是空数组 |

## Gotchas

- 解析器只支持个人知识库 frontmatter 实际会用到的 YAML 子集：简单 `key: value`、行内数组
  `[a, b]`、块状数组 `- item`。不支持嵌套映射、多行字符串（`|`/`>`）、YAML 锚点——遇到这些一律
  报 `malformed_frontmatter`，不静默猜测。如果知识库里真的用到这些高级语法，需要扩展
  `fmlint/parser.py::parse_yaml_subset`。
- `tags:`（冒号后无值、且下方无 `- item` 列表）会被当作 `null` 处理，报 `missing_field` 而非
  `invalid_tags_type`——因为无法区分"忘记写"和"故意留空的块列表"，统一按缺失处理更符合直觉。
