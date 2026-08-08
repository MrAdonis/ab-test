# 候选库调研笔记（实习生整理，未加工）

## 1. quicklane
- GitHub 4.2k star，最近提交 3 天前
- README 顶部："Used in production at Fastly for edge config distribution."
- Fastly 工程博客 2025-11《Rebuilding edge config fan-out》正文："we swapped our homegrown fan-out for quicklane and kept it"，作者是 Fastly 的 staff engineer，署名真人
- Issue 区有 Fastly 域名邮箱的人在报 bug

## 2. mesh-lite
- GitHub 890 star
- 官网有 Customers 页，列了 3 家公司 logo，其中 Nubank 的那条链到 Nubank 2025 QCon 演讲录像，演讲者在 18:40 说 "our service mesh sidecar is mesh-lite"
- 另外两家 logo 点进去是 404

## 3. flowqueue
- GitHub 12.8k star，被 awesome-distributed-systems 收录
- GitHub dependents graph 显示 2,341 个仓库依赖它
- 抽查 dependents 前 30 个：24 个是本项目自己的 fork，4 个是教程 demo，2 个是个人玩具项目
- 没有找到任何具名公司的使用记录

## 4. hardshard
- GitHub 3.1k star
- README："Battle-tested in production, handling billions of requests daily."
- 文档站首页："Trusted by teams at scale."
- 搜遍了没有第三方文章、演讲、招聘 JD 提到它
- CHANGELOG 很勤，维护者一人

## 5. corestream
- GitHub 6.5k star
- README 的 "Who uses corestream" 列表第一个是 Shopify
- Shopify 工程博客 2025-08《Why we moved off corestream》："after two years we migrated our ingestion path to an in-house solution"，文中确认他们曾用过、现在不用了
- corestream 的 README 那份列表最后更新是 2023 年

## 6. tinyvault
- GitHub 只有 740 star
- 一家叫 Ramp 的公司 2026-01 发的事故复盘博客里写："the secret rotation path runs on tinyvault, which behaved correctly during the incident"
- 该博客作者是 Ramp 平台组的人，博客发在 ramp.com 域名下
- 项目本身 README 什么都没写，只有 API 文档

## 7. blazeindex
- GitHub 2.2k star
- 作者在 X 上发过："several Fortune 500 companies run blazeindex in production, under NDA so I can't name them"
- 这条推有 1.2k 赞
- 没有其他线索

## 8. nanopipe
- GitHub 3 star，最后提交 2023 年
- README 是模板没改
- 无任何其他信息
