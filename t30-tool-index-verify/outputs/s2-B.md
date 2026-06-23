# g2.com 评测数据抓取方案

g2.com 用 Cloudflare 被动指纹挡裸请求，属于 Layer 1.5 旁路场景（公开数据 + CF 被动指纹 403 + 需要 Python 抓取）。工具选 **Scrapling**，用 `curl_cffi` 模拟 Chrome TLS 指纹绕过。

---

## 第一步：确认工具是否已就绪

```bash
python3 -c "from scrapling.fetchers import Fetcher; print('ok')"
```

输出 `ok` = 就绪，直接跳到「抓取」。报 `ModuleNotFoundError` = 未装，走下面补装步骤。

---

## 第二步：补装（未装时）

```bash
pip install "scrapling[fetchers]"
```

装完重跑 verify：

```bash
python3 -c "from scrapling.fetchers import Fetcher; print('ok')"
```

> `pip install scrapling`（不带 `[fetchers]`）只装解析层，缺 `curl_cffi`，抓不了网络。必须带 `[fetchers]`。

---

## 第三步：抓取

把下面保存为 `/tmp/g2_scrape.py`，填入目标 URL 再跑：

```python
from scrapling.fetchers import Fetcher

url = "https://www.g2.com/products/<your-product>/reviews"  # 替换实际路径

fetcher = Fetcher(auto_match=False)
page = fetcher.get(url, impersonate="chrome")

print(f"HTTP {page.status}")
print(page.html_content[:3000])  # 先看前 3000 字确认拿到真实正文
```

```bash
python3 /tmp/g2_scrape.py
```

期望看到 `HTTP 200` + 真实 HTML（含 review 文本）。如果仍然 403，说明该页面对 Cloudflare 配了更强规则，升 Layer 3 byob（用本机登录态 Chrome）。

---

## 第四步：解析评测数据

确认 200 后，用内置 CSS 选择器提取评测字段：

```python
from scrapling.fetchers import Fetcher
from scrapling import Adaptor

url = "https://www.g2.com/products/<your-product>/reviews"

fetcher = Fetcher(auto_match=False)
page = fetcher.get(url, impersonate="chrome")

# 用 Scrapling 的 CSS 选择器——自适应选择器加 adaptive=True 可抗页面改版
reviews = page.css("div[itemprop='review']")  # 实际选择器按 DevTools 查真实 DOM 调整
for r in reviews:
    print(r.css_first("[itemprop='name']").text)
    print(r.css_first("[itemprop='reviewBody']").text)
    print("---")
```

选择器需要你先在 Chrome DevTools 里确认 g2 的真实 DOM 结构再填写，别直接跑——g2 DOM 会变，现查现用。

---

## 注意事项

- 不需要代理：CF 被动指纹站用 `impersonate='chrome'` 本地就能过，不用住宅代理
- 批量抓多页时自己加 `time.sleep(2~5)` 间隔，别锤
- 如果需要"评分/星级/时间戳"等结构化字段，先 `print(page.html_content)` 找 JSON-LD（g2 部分页面有结构化数据），比解析 DOM 更稳
