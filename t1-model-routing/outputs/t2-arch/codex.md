## 1. 严重耦合（必须重构）

### Finding 1: `generate.py` 是全流程中心，入口、抓取、生成、配图、发 X、记录发布状态都耦合在一个 915 行文件里
依赖点：`generate.py -> config/fetch_news/fetch_grok_intel/adapter_loader/post_x/generate_news_card/validator/index`，且 handler 内继续动态 import 多个源模块。静态扫描未发现循环依赖，但这里是高扇出强耦合中心。

[generate.py](generate.py:22)
```python
from config import (
    PROMPTS_DIR, OUTPUT_DIR, IMAGES_DIR, SEEN_FILE,
    MIN_CHARS, MAX_CHARS, BUILDER_MIN_CHARS, BUILDER_MAX_CHARS,
    PODCAST_MIN_CHARS, PODCAST_MAX_CHARS,
)
```

[generate.py](generate.py:902)
```python
handlers = {
    "news": handle_news,
    "podcast": handle_podcast,
    "builder": handle_builder,
    "bookmarks": handle_bookmarks,
```

### Finding 2: `config.py` 不是纯配置，import 时创建目录并反向依赖 `adapter_loader`
这让所有 import `config` 的模块都触发文件系统副作用，并让“配置层”依赖“加载器层”。`fetch_news.py`、`fetch_builder.py` 又同时依赖 `config` 和 `adapter_loader`，边界不清晰。

[config.py](config.py:11)
```python
OUTPUT_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True, parents=True)
```

[config.py](config.py:22)
```python
# 数据源现在由 adapters/*.yaml 声明式管理
# 以下列表由 adapter_loader 自动生成，保持向后兼容
from adapter_loader import get_source_ids
```

### Finding 3: `seen.json` 是全局发布状态，但所有权落在 `fetch_news.py`
多个源模块、backlog、发布记录都依赖 `fetch_news.load_seen/save_seen`。这把“新闻抓取模块”变成了全局状态服务，模块边界严重混杂。

[fetch_news.py](fetch_news.py:23)
```python
def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        data = json.loads(SEEN_FILE.read_text())
        urls = data.get("urls", [])
```

[generate.py](generate.py:387)
```python
try:
    seen = load_seen()
    seen.add(item["url"])
    save_seen(seen)
```

[backlog.py](backlog.py:25)
```python
try:
    from fetch_news import load_seen
    seen = load_seen()
    before = len(items)
```

## 2. 中等耦合（建议重构）

### Finding 4: 普通新闻和 builder 源抓取流程重复，且都直接耦合 adapter、HTTP、seen、去重
`fetch_news.py` 与 `fetch_builder.py` 都在做 adapter 加载、HTTP client、sleep、seen 过滤、候选结构化，只是分类和排序不同。

[fetch_news.py](fetch_news.py:92)
```python
adapters = load_adapters()

with httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (compatible; NewsReader/1.0)"},
```

[fetch_builder.py](fetch_builder.py:34)
```python
seen = load_seen()
adapters = load_adapters(category="builder")
all_items = []
```

### Finding 5: RSS/XML 解析逻辑重复分散在多个 fetcher
`fetch_aihot.py`、`fetch_linuxdo.py`、`fetch_x_kol.py` 都直接处理 `ET.fromstring`、`item` 遍历、字段抽取、日期转换，统一 item schema 靠约定维持。

[fetch_aihot.py](fetch_aihot.py:66)
```python
for item in root.iterfind(".//item"):
    title = (item.findtext("title") or "").strip()
    url = (item.findtext("link") or "").strip()
    summary = (item.findtext("description") or "").strip()
```

[fetch_linuxdo.py](fetch_linuxdo.py:122)
```python
for node in root.iterfind(".//item"):
    title = (node.findtext("title") or "").strip()
    url = (node.findtext("link") or "").strip()
    if not title or not url:
```

### Finding 6: Claude CLI 调用与 JSON 抽取重复实现
`generate.py`、`score_builder.py`、`prescore.py`、`generate_card.py`、`fetch_podcast.py` 都各自封装 `subprocess.run(["claude", ...])` 或 JSON 容错解析。

[generate.py](generate.py:188)
```python
def _run_claude_cli(prompt: str, model: str = "claude-opus-4-6", timeout: int = 120) -> str:
    """统一的 Claude CLI 调用。订阅模式，不是 API。"""
    result = subprocess.run(
```

[score_builder.py](score_builder.py:97)
```python
def _parse_scores(output: str, count: int) -> list[dict]:
    """从 Claude 输出中提取 JSON 数组"""
    match = re.search(r'\[[\s\S]*\]', output, re.DOTALL)
```

[prescore.py](prescore.py:51)
```python
def _extract_json_array(raw: str) -> list[dict]:
    """从 claude 输出里抠出 JSON 数组。容错 markdown fence 和前缀文字。"""
    raw = raw.strip()
```

### Finding 7: 卡片 HTML 注入和 Playwright 截图重复
`generate_card.py` 和 `generate_news_card.py` 都负责模板读取、`__CARD_DATA__` 替换、临时 HTML、Playwright 截图。

[generate_card.py](generate_card.py:108)
```python
def build_html(card_data: dict) -> str:
    """把卡片数据注入 HTML 模板。"""
    template = TEMPLATE_PATH.read_text()
```

[generate_news_card.py](generate_news_card.py:78)
```python
def build_html(card_data: dict) -> str:
    """把卡片数据注入 HTML 模板。"""
    template = TEMPLATE_PATH.read_text()
```

### Finding 8: 输出 JSON 持久化有两套相似实现
`save_output` 和 `save_builder_output` 都负责 timestamp、output 文件名、公共字段、图片、quote_url，只是少数字段不同。

[generate.py](generate.py:313)
```python
def save_output(item: dict, tweet: str, images: list[str] | None = None) -> tuple[Path, str]:
    """写 output JSON。不再写数据库——pub_index 在草稿成功后写。返回 (Path, timestamp)。"""
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
```

[generate.py](generate.py:331)
```python
def save_builder_output(item: dict, tweet: str, images: list[str] | None = None) -> tuple[Path, str]:
    """同 save_output，用于 builder / bookmarks 流。返回 (Path, timestamp)。"""
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
```

### Finding 9: `index.py` 同时承担 DB 初始化、写入、搜索、相似度、统计、历史导入
这是单一职责偏离。`generate.py`、`generate_radar.py`、`search.py` 都直接依赖该模块作为历史索引层。

[index.py](index.py:22)
```python
DB_PATH = Path(__file__).parent / "publisher.db"
_initialized = False
```

[index.py](index.py:291)
```python
def import_outputs(output_dir: Path | None = None) -> int:
    """扫描 output/*.json 批量导入历史产出。返回新增条数。"""
    if output_dir is None:
```

### Finding 10: `generate_radar.py` 混合 dashboard 数据生成和个人 wiki 归档
同一入口既生成 `radar_data.json`，又写入用户 home 下的知识库目录，项目边界外泄。

[generate_radar.py](generate_radar.py:107)
```python
OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(f"\n✓ 写入 {OUTPUT}")
print(f"  S:{counts['S']}  A:{counts['A']}  B:{counts['B']}  共 {len(items)} 条通过")
```

[generate_radar.py](generate_radar.py:115)
```python
def archive_to_wiki(items: list[dict], date_str: str):
    """A/S 级条目写入 wiki _inbox 作为主题候选，B 级跳过。"""
    wiki_inbox = Path.home() / "Documents" / "brain" / "01-Wiki" / "_inbox"
```

## 3. 轻微耦合（可接受）

### Finding 11: X session 配置被多个脚本共享，耦合明确但范围较小
`post_x.py`、`setup_sessions.py`、`diag_x_session.py` 都通过 `SESSION_FILES["x"]` 共享登录态路径，属于清晰的基础设施耦合。

[post_x.py](post_x.py:45)
```python
session_file = SESSION_FILES["x"]
if not session_file.exists():
    raise FileNotFoundError("未找到 X session，请先运行 setup_sessions.py x")
```

[setup_sessions.py](setup_sessions.py:14)
```python
async def save_session_x():
    session_file = SESSION_FILES["x"]
```

### Finding 12: `adapter_loader.py` 有模块级 display cache，全局状态较小但会隐藏 adapter 变更
`_DISPLAY_INDEX` 是进程内缓存，适合短命令脚本，但它让 adapter 文件变化不会在同进程内自然反映。

[adapter_loader.py](adapter_loader.py:56)
```python
_DISPLAY_INDEX: dict[tuple[str, str], str] | None = None
```

[adapter_loader.py](adapter_loader.py:59)
```python
def _build_display_index() -> dict[tuple[str, str], str]:
    global _DISPLAY_INDEX
    if _DISPLAY_INDEX is None:
```

## 4. 总结

静态 import 图：未发现 Python 模块级循环依赖。主要问题不是显式循环，而是高扇出中心、共享文件状态、重复 pipeline 和职责混杂。

架构健康度：**5.5 / 10**

三个最该先动的地方：

1. `generate.py` 的全流程中心化问题。
2. `seen.json` / `fetch_news.load_seen` 的全局状态所有权问题。
3. `config.py` import 副作用和 `config -> adapter_loader` 的层级反向依赖。

补充：按仓库指令运行了 `practical-check` 上下文脚本；由于当前只读沙箱，`git status` 相关命令触发 macOS `xcrun` 临时缓存写入警告，但本次没有修改文件。