# OSS 候选库生产使用情况核查

核查目标：区分「有第三方可验证的真实生产使用」和「只有项目自述、无法核实」。自述（README/官网/作者推文里说"生产可用""被信任""身经百战"）本身不算证据，无论说得多肯定；能算数的是**独立于项目方的第三方指认**，或者**在可核实场合留下的具体行为痕迹**（事故复盘、会议演讲、issue 区身份可查的反馈）。

---

## 可进入下一轮

**quicklane**
Fastly 工程博客（2025-11，署名 staff engineer 真人）正文明确写"用 quicklane 替换了自研 fan-out 并保留至今"；issue 区另有 fastly.com 域名邮箱的人在报 bug，两条独立线索互相印证。证据最扎实的一个。

**tinyvault**（star 数最低，反而证据最硬）
Ramp 平台组工程师 2026-01 发在 ramp.com 域名下的事故复盘博客，明确点名"secret rotation 路径跑在 tinyvault 上，且在事故中表现正常"。具体到事故场景的操作细节，作者身份和发布渠道都可查，是这批里最难伪造的一类证据。star 只有 740，说明这次筛选不能只看 star 数。

**mesh-lite**（能进，但证据面窄，需注意）
官网 Customers 页列了 3 家，其中 2 家点进去是 404、不能算数；剩下 Nubank 这一条有 2025 QCon 演讲录像佐证，演讲者在 18:40 亲口说"我们的 service mesh sidecar 是 mesh-lite"——公开会议、具名发言人、可查时间点，这条站得住。但目前只坐实了 Nubank 一家，官网其余客户名单的可信度已经打了折扣（2/3 是死链），细看阶段建议重点确认还有没有别的真实用户，别被官网列表的数量误导。

---

## 证据存在但情况复杂，需要团队自己拍板

**corestream**
Shopify 工程博客（2025-08）证实他们**曾经**用 corestream 跑 ingestion，两年后迁移到自研方案，博客原话是"after two years we migrated our ingestion path to an in-house solution"——这是真实的第三方证据，但指向的是"用过，后来放弃了"，不是"现在还在用"。corestream 自己 README 上的"Who uses"名单最后更新是 2023 年，已经滞后于 Shopify 这篇 2025 年的退场博客，说明项目方的宣传材料没跟上真实情况。这条不做非黑即白的判断：库确实经过大厂两年生产验证，但也确实被最大的样板客户主动换掉了，churn 信号本身要不要作为否决项，取决于团队对"被换掉的原因"的容忍度（博客没细说技术原因，只说换成自研）。建议细看阶段单独查一下 Shopify 换掉的具体原因。

---

## 未发现有效证据，不建议进入下一轮

**flowqueue**（star 最高，但查了没查到）
star 12.8k、dependents graph 显示 2,341 个仓库依赖，看着最唬人。但抽查了前 30 个 dependents：24 个是自己仓库的 fork，4 个教程 demo，2 个个人玩具项目——0 个真实生产使用者。抽样已经做了，且结果是空的，star 和 dependents 数字在这个案例里是噪音。

**hardshard**
README 自称"Battle-tested in production, handling billions of requests daily"，文档站首页自称"Trusted by teams at scale"——两条都是项目自己说的，且找遍了没有第三方文章/演讲/招聘 JD 提到它。典型的自证不算证据。

**blazeindex**
唯一线索是作者自己在 X 上发的"several Fortune 500 companies run it in production, under NDA so I can't name them"——这条不仅是自述，还是自述里明确说了"没法验证"（以 NDA 为由拒绝具名），1.2k 赞是社交热度不是生产证据。没有第三方佐证。

**nanopipe**
star 3、最后提交 2023 年、README 模板都没改，没有任何信息支撑，排除没有争议。

---

## 一句话给团队

真正扛得住的证据只有三种：Fastly 工程博客（quicklane）、Ramp 事故复盘（tinyvault）、Nubank QCon 演讲（mesh-lite，但只坐实了这一家）。corestream 有真实历史证据但已被最大客户放弃，需要团队额外判断。flowqueue 的高 star/高 dependents 抽样后查证为空，hardshard 和 blazeindex 是纯自述包装，nanopipe 直接出局。
