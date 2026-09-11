## P0（静默错误数据）

- **权限受限目录被静默吞掉，产出的统计"看起来完整但实际残缺"**：`collect_stats` 用 `os.walk(root_path)`，未传 `onerror` 回调，`os.walk` 默认 `onerror=None` 会静默吞掉 `scandir` 抛出的 `PermissionError` 等异常，被拒目录直接跳过、不计入、不报错。极端情况下如果 **root 本身**不可读，`os.walk` 会静默返回空结果，此时 `collect_stats` 返回 `{}`，与"真的是空目录"完全无法区分——调用方拿到 `success: true, total_files: 0` 却不知道数据是残缺的。这正好命中 coding-dod 定义的"静默错误数据"红线，且测试套件里没有任何用例覆盖这个分支（无法证明当前行为是有意为之）。

## P1（正确性边界）

- **符号链接语义不一致，且可能与用户直觉（如 `du`/`ls`）不符**：`file_path.stat()`（第 57 行）默认 `follow_symlinks=True`，会把符号链接解析到目标文件后取其体积计入统计，但 `os.walk` 默认 `followlinks=False` 又会跳过符号链接目录。也就是"文件型软链接"被跟随计数（可能把目录外任意大小的文件算进来，或造成硬链接/软链接重复计数），"目录型软链接"却被忽略。这是未声明、未测试的行为组合，容易在真实文件树（如带 `node_modules` 符号链接的项目)上产生反直觉的总字节数。

## P2（标题）

- 异常类命名冗余：`NotADirectoryDirstatError` 中间夹带 "Dirstat" 不一致于同级的 `PathNotFoundError`，纯风格问题
- 隐藏文件（如 `.gitignore`）因 `Path.suffix` 特性被归入 `<no-ext>`，属于 pathlib 标准行为但未在 SPEC/文档/测试中说明，属边界澄清缺口

## 总体评估

核心功能（递归统计、`--json`、结构化报错、pytest 覆盖）已按 SPEC 落地且测试可跑通，但存在一个静默产出错误数据的 P0 缺口（权限受限目录/根目录被吞不报错）和一个未声明的符号链接语义不一致问题，建议修复后再合入。
