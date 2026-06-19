# Handoff — ab-test 2026-06-08

## 本次完成

- `reference_x_article_cover_prompts.md` 从 2 套扩展到 6 套 @AdrianPunk115 提示词框架，全框架覆盖完毕
  - Style 3：极简黑白编辑风（旗舰版）— 三层文字系统，黑白灰极简基调
  - Style 4：麦肯锡/咨询风 — 封面逻辑/信息图逻辑双模式，15 种商业隐喻
  - Style 5a/5b/5c：Nature/SCI 学术风三套 — 科研信息图 / 期刊封面 / 论文插图（GA）
  - Style 6：时装手稿风 — 图生图，需 `--ref` 传人像照，仅英文标注
- `MEMORY.md` 索引条目同步更新，描述从"两套"改为"六套"

## 当前状态

ab-test 主目录状态：t1-t9 各轮 AB test 结果已存档。内存文件全量更新完毕，下次发文章封面直接查 `reference_x_article_cover_prompts.md` 选风格即可。

封面生成执行命令（存在 memory 文件里，不用另查）：
```bash
set -a && source ~/.claude/api_keys.env && set +a && bun ~/.claude/skills/baoyu-imagine/scripts/main.ts \
  --promptfiles /tmp/cover-prompt.md \
  --image /path/to/cover.png \
  --provider seedream --ar 16:9 --quality 2k
```
Style 6 图生图额外加 `--ref /path/to/photo.jpg`。

## 关键决策

- Style 5（学术风）拆成 3 个独立子风格（5a/5b/5c）而非合并成一套，原因：三者 System role 和 User 变量结构差异大，混用会出错
- Style 6 只含英文标注是原框架硬约束（AdrianPunk115 原推），不能加中文

## 下一步

1. 下次发文章时，从 `~/.claude/projects/-Users-edon/memory/reference_x_article_cover_prompts.md` 查选用判据表 → 按对应模板写 `/tmp/cover-prompt.md` → 执行生成命令
2. t10 cross-review structural decay AB test 已完成（本 session 上半段），若要归档 REPORT.md 可补写到 `t10-cross-review-structural-decay/`

## 已知问题/风险

- Style 4 麦肯锡风的"封面逻辑 vs 信息图逻辑自动切换"依赖用途字段是否填对，填错会出偏（如填"信息图"但期望出封面）
- Style 5 学术风三套均含大量专业术语变量，需要用户自己有领域背景才能准确填写

## 相关文件

- `~/.claude/projects/-Users-edon/memory/reference_x_article_cover_prompts.md` — 六套框架完整模板
- `~/.claude/projects/-Users-edon/memory/MEMORY.md` — 索引（line 36 已更新）
- 原始来源推文：
  - Style 1/2：tweet 2063917216261624030、2058201167633793477
  - Style 3（极简黑白/旗舰版）：tweet 2051879710863573277
  - Style 4（麦肯锡）：tweet 2062080784572534958
  - Style 5（学术科研）：tweet 2063634489604190686
  - Style 6（时装手稿）：tweet 2063133370578796692
