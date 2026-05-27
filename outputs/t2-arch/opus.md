# <project> 模块耦合诊断

扫描范围：`` 下 23 个 Python 模块（不含 tests/、archived/）。

---

## 1. 严重耦合（必须重构）

### 1.1 `config.py` ↔ `adapter_loader.py` 模块级循环依赖（import-time side effect）

`config.py` 在模块加载时调用 `adapter_loader.get_source_ids()`，而 `adapter_loader.py` 又会被几乎所有 fetch_* 模块导入。这意味着：**任何 `from config import ...` 都会触发文件系统 IO**（扫描 `adapters/*.yaml` + `yaml.safe_load` 每个文件）。

```python
# config.py:24-28
from adapter_loader import get_source_ids

FINANCE_SOURCES = get_source_ids(category="finance")
TECH_SOURCES = get_source_ids(category="tech")
ALL_SOURCES = FINANCE_SOURCES + TECH_SOURCES
```

```python
# adapter_loader.py:30-42
def load_adapters(category: str | None = None) -> list[dict]:
    adapters = []
    for f in sorted(ADAPTERS_DIR.glob("*.yaml")):
        ...
        with open(f) as fh:
            adapter = yaml.safe_load(fh)
```

`config.py` 注释自己写着「以下列表由 adapter_loader 自动生成，保持向后兼容」（config.py:23）—— 兼容层导致 import 即扫盘。13 个文件 `from config import ...`（grep 已确认），每个 entry point 启动都付一次 YAML 扫描代价。

如果 adapter_loader 后续需要从 config 拿任何常量（比如 `NEWSNOW_BASE`），就会真的形成 import-time 死循环（Python 会抛 `ImportError: cannot import name`）。目前没崩纯粹因为 `adapter_loader.py` 没反向 import `config`。

### 1.2 `generate.py` 集所有职责于一身（915 行，11 类职责）

`generate.py` 是项目里最大的文件（915 行，第二名 `index.py` 只有 324 行），但单职责违反程度比行数本身严重。它同时承担：

```python
# generate.py:1-35（imports + 模块级 IO）
from config import (...)
from fetch_news import get_candidates, load_seen, save_seen
from fetch_grok_intel import get_grok_candidates, ack_grok
from adapter_loader import get_display
from post_x import save_draft_x
from generate_news_card import generate_news_card
from validator import (...)
import index as pub_index

INSTRUCTIONS = (PROMPTS_DIR / "instructions.md").read_text()
BUILDER_INSTRUCTIONS = (PROMPTS_DIR / "builder.md").read_text()
```

11 项职责清单（每项都有独立的代码块）：

| 职责 | 行号 | 备注 |
|------|------|------|
| 英文媒体搜索 + 关键词提取 | generate.py:41-83 | 该独立成 `search_english.py` |
| Playwright 截图 + 去噪 JS | generate.py:86-185 | 该并入 `generate_news_card.py` |
| Claude CLI 包装 | generate.py:188-196 | 该上提到 `claude_cli.py` |
| Prompt 拼接（4 种变体） | generate.py:199-291 | 已抽 `_generate_validated` 但散在文件里 |
| Schema 校验重试循环 | generate.py:220-254 | 同上 |
| save_output JSON | generate.py:313-350 | 两个几乎一样的 `save_output` |
| Playwright 草稿调用兜底 | generate.py:353-364 | 错误信息直接 print |
| 发布后多写入点（pub_index/seen/backlog） | generate.py:367-410 | 三个 try/except 串联，无事务边界 |
| pbcopy 剪贴板 | generate.py:413-418 | 杂项 utility |
| 交互式 pick UI | generate.py:421-435 | TUI 逻辑 |
| 7 个 handler（news/aihot/linuxdo/podcast/builder/bookmarks/grok） | generate.py:463-881 | 每个 60-100 行，结构 95% 雷同 |
| Grok 排序键 + 优先级表 | generate.py:791-825 | Grok 专属业务规则 |

7 个 handler 的结构几乎一字不差（grep `def handle_` 拿到 generate.py:463/529/572/615/664/741/828）：① `print("拉取...")` → ② `get_candidates()` → ③ 空检查 → ④ `if args.pick` 列表 → ⑤ `_pick_one` → ⑥ 打印已选 → ⑦ `write_*_tweet` → ⑧ `_build_image` → ⑨ `save_*_output` → ⑩ `if args.dry_run` 返回 → ⑪ `safe_save_draft` → ⑫ `_record_published`。

7 份近似复制 = 加新源要改 generate.py 主文件 + 改 args choices + 改 handlers dict + 抄一份 handler。

### 1.3 `fetch_news.load_seen / save_seen` 是事实上的全局可变状态，被 6 个模块共享

`seen.json` 是 URL 去重的唯一权威源。生产/消费方分散：

- 写：`fetch_news.save_seen` (fetch_news.py:34-56) 在 `generate._record_published` (generate.py:387-401) 内调用
- 读：6 个模块导入 `load_seen`（grep 已确认）：
  - `fetch_news.py:23`（定义 + get_candidates 内调用 fetch_news.py:87）
  - `fetch_aihot.py:22` → fetch_aihot.py:51
  - `fetch_x_kol.py:27` → fetch_x_kol.py:224
  - `fetch_linuxdo.py:34` → fetch_linuxdo.py:171
  - `fetch_bookmarks.py:15` → fetch_bookmarks.py:34
  - `fetch_builder.py:20` → fetch_builder.py:34
  - `backlog.py:26`（lazy import）→ backlog.py:27

没有锁、没有事务、没有原子写。`save_seen` 的实现还做了 "合并 + 7 天清理 + 截前 2000 条" 三件事：

```python
# fetch_news.py:46-56
for url in seen:
    if url not in existing:
        existing[url] = now
# 清理 7 天以上的老数据，最多保留 2000 条
cutoff = now - 7 * 86400
existing = {u: ts for u, ts in existing.items() if ts >= cutoff}
sorted_urls = sorted(existing.items(), key=lambda x: x[1], reverse=True)[:2000]
SEEN_FILE.write_text(json.dumps(
    {"urls": dict(sorted_urls)}, ensure_ascii=False, indent=2,
))
```

每次 save 都把全表 sort + 截断 + 重写整文件。两个并发 fetch_* 进程同时写 = race condition，会丢 URL → 下次重复发推。

`generate.py:393-401` 的 print 已经承认这点："seen.json 写入失败 → 下次运行可能重复发布本条"。已知风险被告警化，没被结构化解决。

### 1.4 `generate_card.py` 与 `generate_news_card.py` —— 同一职责两套实现

两份独立的 "build_html → Playwright headless 截图" 流程：

```python
# generate_news_card.py:78-82
def build_html(card_data: dict) -> str:
    template = TEMPLATE_PATH.read_text()
    data_json = json.dumps(card_data, ensure_ascii=False)
    return template.replace("__CARD_DATA__", data_json)
```

```python
# generate_card.py:108-112
def build_html(card_data: dict) -> str:
    template = TEMPLATE_PATH.read_text()
    data_json = json.dumps(card_data, ensure_ascii=False)
    return template.replace("__CARD_DATA__", data_json)
```

逐字一样。截图代码也几乎一样：

- generate_news_card.py:85-111（async `generate_news_card`，1200x675）
- generate_card.py:115-137（async `screenshot_card`，1200x800）

只差 viewport 大小和模板路径。差异不足以解释为什么各自独立。

---

## 2. 中等耦合（建议重构）

### 2.1 三个 LLM-JSON 提取函数，三套写法

三个文件各自实现一份 "从 Claude stdout 抠 JSON" 的容错逻辑，互不调用：

```python
# prescore.py:51-67
def _extract_json_array(raw: str) -> list[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if not m:
        raise ValueError(f"找不到 JSON 数组：{raw[:200]}")
    return json.loads(m.group(0))
```

```python
# score_builder.py:97-108
def _parse_scores(output: str, count: int) -> list[dict]:
    match = re.search(r'\[[\s\S]*\]', output, re.DOTALL)
    if not match:
        return []
    try:
        scores = json.loads(match.group())
        ...
```

```python
# generate_card.py:81-99
json_match = re.search(r"\{[\s\S]*\}", raw)
...
json_str = json_match.group()
try:
    data = json.loads(json_str)
except json.JSONDecodeError:
    # LLM 有时在 detail 里用了未转义的引号，用 Claude 修复
    fix_result = subprocess.run(
        ["claude", "-p",
         "修复以下 JSON 的语法错误...",
         "--model", "claude-haiku-4-5-20251001"],
```

三套行为微妙不同（prescore 处理 fence、score_builder 不处理、generate_card 走 LLM repair fallback）。新增源时复制最近一份继续魔改是必然路径。

### 2.2 Claude CLI 调用散落 6 处，参数/timeout/model 不统一

`_run_claude_cli` 在 generate.py:188-196 已抽出，但其他 5 处仍直接调 subprocess：

| 文件:行 | model | timeout | 重试 |
|---------|-------|---------|------|
| generate.py:54-60 | haiku-4-5 | 30 | 无 |
| generate.py:190-193（_run_claude_cli） | opus-4-6 | 120 | 上层 _generate_validated 做 |
| fetch_podcast.py:131-134 | opus-4-6 | 180 | 无 |
| score_builder.py:182-185 | sonnet-4-6 | 120 | 循环 max_retries=1 |
| prescore.py:83-86 | haiku-4-5 | 90 | 无 |
| generate_card.py:72-77 | sonnet-4-6 | 180 | 无 |
| generate_card.py:90-95 | haiku-4-5 | 30 | 无（JSON 修复用） |

`fetch_podcast.generate_summary` (fetch_podcast.py:120-137) 在 `generate.write_podcast_tweet` (generate.py:274-291) 出现后已经死代码 —— 两份都读 `podcast.md`、都拼几乎一样的 prompt，但 `fetch_podcast.generate_summary` 没人调用（grep `generate_summary` 0 命中外部调用方）。注释/CLAUDE.md 没说它被废弃。

### 2.3 `generate.save_output` 和 `save_builder_output` 高度重复

```python
# generate.py:313-328
def save_output(item: dict, tweet: str, images: list[str] | None = None) -> tuple[Path, str]:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = OUTPUT_DIR / f"{ts}.json"
    data = {
        "source_id": item["source_id"],
        "title": item["title"],
        "url": item["url"],
        "tweet": tweet,
        ...
```

```python
# generate.py:331-350
def save_builder_output(item: dict, tweet: str, images: list[str] | None = None) -> tuple[Path, str]:
    """同 save_output，用于 builder / bookmarks 流。返回 (Path, timestamp)。"""
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = OUTPUT_DIR / f"builder_{ts}.json"
    ...
```

差异只有：① 文件名前缀 `builder_` ② 多 3 个字段 `content_type/score/reply_links`。docstring 自己写「同 save_output」。一个 `prefix=` 参数 + 可选字段就能合并。

### 2.4 `fetch_builder` 和 `fetch_x_kol` 各自抄了一套 URL 去重 key

```python
# fetch_builder.py:23-26
def _url_key(url: str) -> str:
    """提取 URL 的域名+路径作为去重 key"""
    parsed = urlparse(url)
    return f"{parsed.netloc}{parsed.path}".rstrip("/")
```

```python
# fetch_x_kol.py:246-247
parsed = urlparse(url)
key = f"{parsed.netloc}{parsed.path}".rstrip("/")
```

逐字一致，没共享。第三个源用就抄第三份。

### 2.5 User-Agent / Playwright launch 配置散落 5 处

UA 字符串有 3 个不同版本：

- `"Mozilla/5.0 (compatible) <project>/0.1"` — fetch_aihot.py:30, fetch_linuxdo.py:55
- `"Mozilla/5.0 (compatible; NewsReader/1.0)"` — fetch_builder.py:39, fetch_news.py:95
- `"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."` Chrome 131 — diag_x_session.py:22, post_x.py:60, setup_sessions.py:24, generate.py:149

`--disable-blink-features=AutomationControlled` 在 generate.py:145, post_x.py:57, setup_sessions.py:21, diag_x_session.py:18 各写一遍。改 Chrome 版本号或反封号策略要同步改 4 处。

### 2.6 `generate_radar.py` 反向依赖 `generate.py` 的同一批组件，但路径不一致

```python
# generate_radar.py:18-21
from fetch_builder import get_candidates
from fetch_x_kol import get_x_kol_candidates
from score_builder import score_candidates
import index as pub_index
```

`generate.handle_builder` 也调 `fetch_builder.get_candidates` + `score_builder.score_candidates`（generate.py:665-682），但 generate_radar.py 是 dashboard 数据生成入口、generate.py 是发推入口，两条路径在 "拉 + 打分" 上重复，分歧只在后续做什么。`generate_radar.archive_to_wiki` (generate_radar.py:115-174) 写 wiki，发推流不写，反过来也成立。两条 pipeline 没有共享的「候选源 + 打分结果」中间表示。

---

## 3. 轻微耦合（可接受）

### 3.1 `config.py` 作为常量库被广泛 import

13 个文件 `from config import ...`。这是合理的中心化常量定义，不算耦合问题——前提是 config.py 不再做 import-time 副作用（见 1.1）。

### 3.2 `fetch_news.fetch_source` 是历史兼容 shim

```python
# fetch_news.py:59-62
def fetch_source(source_id: str, client: httpx.Client) -> list[dict]:
    """兼容旧调用方式，内部委托给 adapter_loader"""
    adapter = {"strategy": "newsnow", "source_id": source_id, "site": source_id}
    return fetch_adapter(adapter, client, newsnow_base=NEWSNOW_BASE)
```

`grep fetch_source` 在源码里 0 外部调用方。属于「装着没用」的死代码，但不主动伤害架构，可保留作过渡。

### 3.3 `index.py` 模块级 `_initialized` 状态 + 文件级 DB_PATH

```python
# index.py:22-23
DB_PATH = Path(__file__).parent / "publisher.db"
_initialized = False
```

`_initialized` 是模块级全局，但只控制 schema 创建，幂等。`DB_PATH` 硬编码限制了测试隔离（tests/test_record_published.py 想换 DB 要 monkey-patch）。可接受，但写测试时需要 awareness。

### 3.4 `validator.py` 完全独立

`validator.py` 只 import 标准库（re/sys/dataclasses/typing），不依赖项目其他模块。这是项目里最干净的模块，反衬出 generate.py 的混乱。

### 3.5 `setup_sessions.py` 和 `diag_x_session.py` 各自独立

两个诊断/初始化脚本，独立运行，各自只依赖 `config.SESSION_FILES`。属于合理的工具脚本分离。

---

## 4. 总结

### 架构健康度评分：**4 / 10**

加分项：
- adapter 化的 YAML 源配置（`adapter_loader.py`）方向正确，已经把数据源声明式管理（+1）
- `validator.py` 单一职责干净（+0.5）
- `index.py` 用 SQLite FTS5 + 触发器维护索引，封装合理（+0.5）
- 有 tests/ 目录覆盖关键模块（+0.5）
- 已经识别了部分共性并抽了 `_generate_validated` / `_record_published` / `_pick_one` 等工具（+0.5）

扣分项：
- `generate.py` 915 行承担 11 类职责，7 个 handler 95% 重复（-2）
- 全局可变状态 `seen.json` 被 6 个模块直写，无锁无事务，已知会丢数据（-1.5）
- `config.py` import 时副作用（YAML 扫描），13 个 caller 每次启动都付代价（-1）
- 同职责双实现：`generate_card.py` vs `generate_news_card.py`、`fetch_podcast.generate_summary` vs `generate.write_podcast_tweet`（-0.5）
- 3 份独立的 LLM-JSON 解析、6 处 subprocess.run claude CLI、3 个 UA 字符串散落（-0.5）

### 三个最该先动的地方

1. **拆 `generate.py`**（1.2 + 2.3 + 2.2 一起做）
   - 把 7 个 handler 抽象成 `SourceHandler` 接口：每个源只需声明 `fetch` / `prompt_template` / `image_strategy` 三个钩子
   - 把 `screenshot_article` + `_NOISE_HIDE_JS` + `find_english_articles` 移到独立的 `image_pipeline.py`
   - `_run_claude_cli` 上提到 `claude_cli.py`，让 fetch_podcast/score_builder/prescore/generate_card 都用它
   - 收益：915 行 → 估计 200 行主流程 + 7 个 50 行的源配置；加新源不改主文件

2. **`seen.json` → 进 `index.py` 的 SQLite**（1.3 一刀解决）
   - 现成的 publisher.db 已经在用 SQLite，多一张 `seen_urls(url PRIMARY KEY, seen_at)` 表零成本
   - 原子写、可索引、跨进程安全
   - `load_seen` / `save_seen` 替换为 `seen.contains(url)` / `seen.mark(url)`，调用方零改动
   - 顺便清掉 generate.py:393-401 那段「seen 写失败可能重复发布」的告警代码

3. **打破 `config.py` 的 import-time 副作用**（1.1）
   - `FINANCE_SOURCES` / `TECH_SOURCES` / `ALL_SOURCES` 改成 `@functools.cache` 装饰的函数（lazy）
   - 或直接 grep 找出谁还在用这三个常量（看注释「保持向后兼容」，估计已无人）—— 没人用就删掉，循环依赖隐患同时消失
   - 影响面：config.py 30 行内的改动，不动调用方

不动这三处的话，加第 8 个源（很可能很快发生 —— 已有 7 个）会被 generate.py 的复制成本拖死；并发跑 fetch_* 会丢 seen；冷启动 import config 会逐步变慢。
