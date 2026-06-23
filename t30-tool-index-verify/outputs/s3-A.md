查看 git 状态、最近提交、以及统计 ts 文件，三条命令并行跑。

```bash
git status
git log --oneline -5
find src -name "*.ts" | wc -l
```

**git status**

```
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  t21-epistemic-tagging/
  t22-loop-until/
  t23-punk-fusion-imagebase/
  t25-decision-artifact-pattern/
  t25-overnight-scratch/
  t25-ui-microcopy/
  t26-graceful-degradation/
  t27-platform-threshold-exempt/
  t28-rewrite-subtraction-discipline/
  t29-cover-diagnosis-absorb/
  t30-tool-index-verify/
```

分支干净，11 个未跟踪目录待 `git add`。

**最近 5 条提交**

```
ff333af t24: OWASP appsec 条件项入 coding-dod 安全段 — 严格重测证成 KEEP
53f83b7 archive: t5-t20 AB test results + cover images
3a4a66f t17: image-base 局部修改路由条目 AB（keep, B 8 vs A 7）
6b67513 add t14: frontend-design 增量吸收 design-system AB（平手 8.07 vs 8.03，不吸收，插件卸载）
302167a t10: cross-review v3 vs v4 结构腐化检测层 AB test
```

**src 下 .ts 文件数量**

`src` 目录不存在（或为空），计数为 **0**。
