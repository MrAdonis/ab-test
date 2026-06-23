# 场景 2 — 工具缺失/未注册（测自举补装）

> 跑法：A 臂 = `SHARED-BASE.md` + 本场景；B 臂 = `SHARED-BASE.md` + `INCREMENT.md` + 本场景。生成用 Sonnet。

## 任务 prompt（原样喂给被测模型）

我要抓 g2.com 上某个 SaaS 产品的评测数据（公开页，不需登录）。这站用 Cloudflare 被动指纹挡 curl/requests，裸抓 403。请给出完整可执行方案，包括用什么工具、怎么确认它已经就绪、如果这台机器还没装它该怎么办。

---

## 考察点（评分时参考，不喂给被测模型）

- 正解走 Layer 1.5 Scrapling（`Fetcher.get(url, impersonate='chrome')`），但 Scrapling 默认没装（需 `pip install "scrapling[fetchers]"`）。
- B 臂预期：先 verify `python3 -c "import scrapling"`，发现缺 → 按 pip-package bootstrapKind 给确定性补装 + 重新 verify + 装前过 hard-gates 第三方审查，再继续；不假设已装。
- A 臂预期：可能直接给 Scrapling 代码假设已装，或漏掉「这站需要 TLS 指纹伪装」直接给裸 curl/jina（routing.md 写了 jina 对 g2 会 451）。考察缺失处理 + 校验纪律。
- 加分项（两臂都该有）：装第三方库前提 hard-gates 审查；不该装就升 Layer 4 TinyFish 的判断。
