三条命令直接跑：

```bash
# 1. 仓库状态
git status

# 2. 最近 5 条提交
git log --oneline -5

# 3. src 下 .ts 文件数
find src -name "*.ts" | wc -l
```

结果：仓库在 main 分支，与 origin 同步，有 11 个未跟踪目录（t21~t30 的测试目录）。最近 5 条提交是 t24/t17/t14/t10 等 AB test 记录。`src` 目录不存在，`.ts` 文件数为 0。
