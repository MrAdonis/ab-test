# 抓 g2.com 评测数据：完整方案

g2.com 用 Cloudflare 被动指纹挡住了 curl/requests，走 Layer 1.5 旁路：**Scrapling**（curl_cffi TLS 指纹伪装）。

---

## 1. 确认环境是否已就绪

```bash
python3 -c "from scrapling.fetchers import Fetcher; print('ok')"
```

输出 `ok` = 已就绪，跳到第 3 步。报 `ModuleNotFoundError` = 需要安装。

---

## 2. 安装（如果还没装）

```bash
pip install "scrapling[fetchers]"
```

注意：Python 3.14 下纯 `pip install scrapling` 只给 parser，HTTP 抓取需要 `[fetchers]` extra（补全 curl_cffi/playwright/browserforge 等约 15 个包）。

装完再跑一遍确认命令验证。

---

## 3. 抓取代码

```python
from scrapling.fetchers import Fetcher

url = "https://www.g2.com/products/<your-product>/reviews"  # 替换为目标页 URL

page = Fetcher.get(url, impersonate="chrome")
print(page.status)   # 应为 200
print(len(page.content))  # 真实正文字节数

# 提取评测数据（根据页面结构写选择器）
reviews = page.css(".review-card")  # 示例，按实际 DOM 调整
for r in reviews:
    print(r.text)
```

---

## 4. 如果 200 但返回空壳

少数情况下 Cloudflare 会要求 JS 挑战（不是被动指纹，是交互挑战）。这时 `impersonate='chrome'` 不够用，升级用 StealthyFetcher：

```bash
scrapling install  # 下载 camoufox + chromium，几百 MB
```

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(url, headless=True)
```

但 g2.com 实测 Fetcher（非 StealthyFetcher）就能过，先试普通版。

---

## 5. 批量抓多页

```python
from scrapling.fetchers import Fetcher

base_url = "https://www.g2.com/products/<product>/reviews?page={}"

for page_num in range(1, 6):  # 抓前 5 页
    page = Fetcher.get(base_url.format(page_num), impersonate="chrome")
    if page.status != 200:
        print(f"页 {page_num} 失败，状态码 {page.status}")
        break
    # 解析逻辑...
```

---

## 快速验证命令（一行）

```bash
python3 -c "
from scrapling.fetchers import Fetcher
p = Fetcher.get('https://www.g2.com/products/notion/reviews', impersonate='chrome')
print(p.status, len(p.content), 'bytes')
"
```

预期输出：`200 413000 bytes`（数量级对即可）。如果状态码是 200 且字节数 > 100KB，数据是真实的。
