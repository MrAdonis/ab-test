# <project> 模块耦合诊断报告

---

## 1. 严重耦合（必须重构）

### 1.1 `config.py` 在模块加载时执行副作用代码

**文件**：`config.py:11-13`

```python
OUTPUT_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True, parents=True)
```

任何 `import config` 都会立即在文件系统创建三个目录。测试环境、CI 环境、脚本导入全部受影响。这是配置模块做了执行层的事，违反"import 无副作用"原则。

---

### 1.2 `config.py` 在模块顶层执行业务逻辑（调用 `adapter_loader`）

**文件**：`config.py:24-28`

```python
from adapter_loader import get_source_ids

FINANCE_SOURCES = get_source_ids(category="finance")
TECH_SOURCES = get_source_ids(category="tech")
ALL_SOURCES = FINANCE_SOURCES + TECH_SOURCES
```

`config.py` 在模块加载时调用 `adapter_loader.get_source_ids()`，后者会读取 `adapters/` 目录下所有 YAML 文件（`adapter_loader.py:33-42`）。任何依赖 `config` 的模块（共 10+ 个文件）都会触发 YAML 文件 I/O。导致：
- 测试环境无法 mock YAML
- 真实文件系统不存在时整个 import 链条崩溃

---

### 1.3 `generate.py` 在模块顶层读取 prompt 文件

**文件**：`generate.py:37-38`

```python
INSTRUCTIONS = (PROMPTS_DIR / "instructions.md").read_text()
BUILDER_INSTRUCTIONS = (PROMPTS_DIR / "builder.md").read_text()
```

`generate_card.py:26` 同样：

```python
CARD_PROMPT = (PROMPTS_DIR / "card_top10.md").read_text()
```

模块导入时就读取磁盘文件。`prompts/` 目录不存在或任一文件缺失，所有下游 `import generate` 立即抛 `FileNotFoundError`，而不是在调用时失败。测试中的 `import generate` 也依赖真实文件系统。

---

### 1.4 `backlog.py` 在运行时内部 import `fetch_news`（不对称依赖）

**文件**：`backlog.py:26-27`

```python
from fetch_news import load_seen
seen = load_seen()
```

`backlog.py` 依赖 `fetch_news.py` 取 `load_seen`，而 `fetch_news.py` 依赖 `config.py`，`config.py` 又依赖 `adapter_loader.py`。这条链路隐藏在 `load_backlog()` 的函数体内（而非模块顶层 import），意味着 `backlog.py` 的调用者感知不到这个传递依赖。任何对 `backlog.load_backlog()` 的调用都会静默拉起完整的 YAML 加载链。

---

### 1.5 7 个 `handle_*` 函数在 `generate.py` 中重复相同结构（单一职责违反）

**文件**：`generate.py:463,529,572,615,664,741,828`

每个 `handle_news/aihot/linuxdo/podcast/builder/bookmarks/grok` 都重复了以下五步：
1. 拉候选 + 过滤
2. 交互式选择（`--pick` 分支）
3. 调用写推文函数
4. 调用 `_build_image`
5. 调用 `save_output` + `safe_save_draft` + `_record_published`

步骤 3-5 跨 7 个函数基本相同，代码分散在 463-915 行之间（452 行）。`generate.py` 单文件承担了入口调度、推文生成、图片生成、草稿保存、索引写入全部职责。

---

## 2. 中等耦合（建议重构）

### 2.1 `fetch_news.load_seen` 被 7 个模块直接调用

`load_seen` 的实现定义在 `fetch_news.py:23`，但被以下文件全部直接依赖：

| 文件 | 引用方式 |
|------|---------|
| `backlog.py:26` | 函数内 import |
| `fetch_builder.py:20` | 顶层 import |
| `fetch_aihot.py:22` | 顶层 import |
| `fetch_bookmarks.py:15` | 顶层 import |
| `fetch_linuxdo.py:34` | 顶层 import |
| `fetch_x_kol.py:27` | 顶层 import |
| `fetch_podcast.py:23` | 顶层 import |
| `generate.py:27` | 顶层 import |

`load_seen`/`save_seen` 是全局共享状态管理，逻辑上属于独立的 seen-store 层，但语义上归属在 `fetch_news.py` 里（一个专门做新闻拉取的模块）。所有 fetch 模块都耦合到 `fetch_news` 只是为了访问 seen 状态。

---

### 2.2 `fetch_builder.py` 和 `fetch_aihot.py` 导入了从不使用的 `SEEN_FILE`

**文件**：`fetch_builder.py:18`

```python
from config import NEWSNOW_BASE, SEEN_FILE
```

**文件**：`fetch_aihot.py:21`

```python
from config import SEEN_FILE
```

两个文件都导入了 `SEEN_FILE`，但实际上两者都通过 `fetch_news.load_seen()` 访问 seen 数据，`SEEN_FILE` 路径变量从未被直接使用（同样的问题出现在 `fetch_x_kol.py:26` 和 `generate.py:23`，AST 分析确认 `generate.py` 中 `SEEN_FILE` 0 次使用）。

---

### 2.3 `fetch_podcast.py` 中存在死代码 `generate_summary`

**文件**：`fetch_podcast.py:120-137`

```python
def generate_summary(title: str, transcript: str, source_name: str) -> str:
    """用 Claude 生成播客摘要推文"""
    instructions = (PROMPTS_DIR / "podcast.md").read_text()
    prompt = (...)
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", "claude-opus-4-6"],
        ...
    )
```

`generate.py:274` 中有功能完全相同的 `write_podcast_tweet`（带 Schema 校验重试循环）。`generate_summary` 在整个项目中没有任何调用方（`grep -rn "generate_summary"` 仅命中该定义行），是过时的重复实现。

---

### 2.4 `generate_card.py` 和 `generate_news_card.py` 存在完全相同的 `build_html` 函数

**文件**：`generate_card.py:108-113` 和 `generate_news_card.py:78-83`

两处代码逐行完全相同：

```python
def build_html(card_data: dict) -> str:
    """把卡片数据注入 HTML 模板。"""
    template = TEMPLATE_PATH.read_text()
    data_json = json.dumps(card_data, ensure_ascii=False)
    return template.replace("__CARD_DATA__", data_json)
```

唯一区别是各自引用的 `TEMPLATE_PATH` 不同（`card_top10.html` vs `card_news.html`）。模板注入逻辑本身是重复实现。

---

### 2.5 `generate_radar.py` 导入了从不直接使用的 `BACKLOG_FILE`

**文件**：`generate_radar.py:17`

```python
from config import BUILDER_SCORE_THRESHOLD, BACKLOG_FILE
```

`BACKLOG_FILE` 在 `generate_radar.py` 中无任何使用（函数体里通过 `from backlog import load_backlog` 访问 backlog，不需要直接操作文件路径）。`BUILDER_SCORE_THRESHOLD` 同样只出现在 import 语句，实际代码用的是 `B_THRESHOLD = 7`（`generate_radar.py:26-33`）。

---

### 2.6 两套独立的"去重"机制边界不清晰

项目同时维护：
- `seen.json`（`fetch_news.py:23-56`）：URL 集合，候选拉取时过滤
- `publisher.db`（`index.py`）：SQLite 全文索引，发布后写入

`index.has_url`（`index.py:220`）功能是检查 URL 是否已发布，但从未被任何 fetch 模块调用。所有过滤逻辑都走 `seen.json`，`publisher.db` 仅作为历史检索用途。两套机制目的重叠但行为不一致：seen.json 7 天过期，publisher.db 永久保留。调用方无法从接口层感知到哪一套是"去重权威源"。

---

## 3. 轻微耦合（可接受）

### 3.1 `score_builder.py` 的 `__main__` 块中内联 `fetch_builder` 导入

**文件**：`score_builder.py:238`

```python
if __name__ == "__main__":
    from fetch_builder import get_candidates
```

仅在直接运行时触发，不影响模块作为库使用。可接受的调试便利设计。

---

### 3.2 `generate.py` 中部分 handler 的 import 延迟到函数体内

**文件**：`generate.py:472,530,573,616,665,742,898`

```python
async def handle_news(args) -> None:
    ...
    from prescore import prescore, save_prescore_dump
```

这是刻意的懒加载设计，减少非该路径时的模块加载开销。结构上没问题，但与顶层 import 的其他模块（如 `fetch_grok_intel`）风格不一致。

---

### 3.3 `config.py` 的 `PODCAST_SOURCES` 列表硬编码了外部服务句柄

**文件**：`config.py:35-51`

播客来源（YouTube 频道 handle）直接写在 `config.py`，`fetch_podcast.py:155` 直接读取。和 adapters/ 的声明式 YAML 设计风格不一致，但规模小（3 条），尚在可接受范围。

---

### 3.4 `search.py` 直接 import `index` 模块（正常设计）

**文件**：`search.py:16`

```python
import index
```

`search.py` 是 `index.py` 的 CLI 包装，单向依赖，无问题。

---

## 4. 总结

### 架构健康度评分：4 / 10

**主要扣分点**：
- `config.py` 在导入时执行文件 I/O 和业务逻辑（YAML 加载），污染所有下游模块的测试边界
- `generate.py` 超过 900 行，承担 7 种来源的调度、生成、图片、发布、索引全部职责，单文件过大
- `seen.json` 状态管理散落在 `fetch_news.py` 中，被 7 个不相关模块直接依赖
- 多处死代码（`generate_summary`、`has_url`）和幽灵导入（`SEEN_FILE`、`BACKLOG_FILE`）说明模块演化中的清理工作被省略

### 最该先动的三个地方

**第一优先：`config.py` 去副作用**

`config.py:11-13` 的 `mkdir` 和 `config.py:24-28` 的 YAML 加载移出顶层。`mkdir` 改为懒加载（首次使用时），`FINANCE_SOURCES`/`TECH_SOURCES` 改为函数返回而非模块级常量。影响：所有模块的 import 变纯净，测试可以无副作用地 `import config`。

**第二优先：提取 `seen.py` 独立模块**

将 `fetch_news.py:23-56` 的 `load_seen`/`save_seen` 移到独立的 `seen.py`。当前 7 个 fetch 模块因为 `load_seen` 而耦合到 `fetch_news`，一个新闻拉取模块不应该是全局状态管理者。提取后，`fetch_news` 改为 `from seen import load_seen`，其余模块也一并改。

**第三优先：拆分 `generate.py`**

`generate.py` 的 7 个 `handle_*` 函数共享 5 步相同的流程骨架，可抽出一个通用的 `run_pipeline(fetch_fn, write_fn, args)` 函数，或将 7 个 handler 各自移到对应的 `fetch_*.py` 旁边。`generate.py` 应只保留 `main()` 入口调度，不承载业务逻辑。
