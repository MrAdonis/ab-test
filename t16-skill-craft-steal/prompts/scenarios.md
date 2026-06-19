# t16 场景 — 偷 xiaohu/xiaohu-video-translate 的两个 skill 封装手法

来源：github.com/xiaohuailabs/xiaohu-video-translate（@xiaohu 开源视频翻译 skill 套件）。
方法：Sonnet 生成 A（基线 = 现有 skill-design-patterns 指导）/ B（+ 注入手法）输出，Sonnet 盲评委按 5 维打分。B>A 才落地 live config，否则回滚 + 记 rejected buffer。

## Track 1（#2）：description 字段做"触发 + 防半途"双重防御

测的注入：见 `injection-track1.md`。

### S1-deploy（pipeline 型，半途即失败）
> 写一个「部署 Astro 站到 Cloudflare Pages」skill 的 frontmatter `description` 字段（只写 description，不写 body）。
> 这个 skill 的完整管线是：build → 部署 → 部署后验证（curl 首页 200 + 检查关键路由）→ 给回滚命令。
> 已知失败模式：agent 经常 build 完或部署完就报"成功"，跳过验证和回滚说明。
> 用户可能的说法：部署、上线、发布、deploy、推到 Pages、上 CF。

### S2-report（generate→审核→发布，半途即失败）
> 写一个「美股每日小报」skill 的 frontmatter `description` 字段（只写 description）。
> 完整管线：抓数据 → 生成稿件 → 对照来源审核（P0-P3）→ 发布 → 记账。
> 已知失败模式：agent 生成完稿件就停，跳过审核直接当完成；或审核完不发布。
> 用户可能的说法：写今天的小报、出小报、生成小报、跑日更、来一篇美股。

## Track 2（#4）：主观品味目标 → 拆成可测规则

测的注入：见 `injection-track2.md`。

### S3-cover（品味目标 = "封面要高级、有设计感"）
> 写一个「给技术文章生成封面图」skill 的「核心规则」段（不写 frontmatter，只写规则正文）。
> 这个 skill 的品质目标用户表述为："封面要高级、有设计感、不像 AI 随手生成的廉价图"。
> 你要把这个主观目标转成可执行的核心规则。

### S4-chart（品味目标 = "图表要清晰好读"）
> 写一个「把一组数据画成对比图表」skill 的「核心规则」段（只写规则正文）。
> 品质目标用户表述为："图表要清晰、一眼能看懂、专业不花哨"。
> 你要把这个主观目标转成可执行的核心规则。

## 评分（每场景满分 50，5 维 × 10）

### Track 1 维度
1. 触发可靠性：枚举了用户的多种说法，欠触发概率低
2. 防半途执行：明文写了"必须完整管线/不能只做到 X 就结束"
3. 不过度触发：没有宽到把无关请求也吸进来
4. 可观测/具体：触发条件和完整管线是具体动作，不是"按需判断"
5. 简洁：description 没臃肿，仍是一段可读的 L1（< ~100 词中文）

### Track 2 维度
1. 可执行性：规则能照着做，不是"要好看"这类空话
2. 真实性/依据：规则有可信依据（实测/常识性设计原理），不是为凑数编的伪精确数字
3. 覆盖品味目标：把"高级感/清晰"拆得够全，没漏关键维度
4. 留对自由度：真无法量化的部分保持文字描述，没硬塞假阈值
5. 简洁：规则不冗余堆砌，密度高
