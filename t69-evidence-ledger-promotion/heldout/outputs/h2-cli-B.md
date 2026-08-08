权限拒绝了 `rm -rf`,无妨——`.venv` 只是我用来跑测试验证的临时环境,不影响交付物,留着也无害。

已在 `/private/tmp/t69h-h2-cli-B-po0GLW/dirstat.py` 和 `/private/tmp/t69h-h2-cli-B-po0GLW/test_dirstat.py` 写好并跑通(12 个测试全过)。

要点:
- `collect_stats()` 递归统计各扩展名的文件数和字节数,无扩展名的文件归入 `<no ext>`
- CLI 默认输出人类可读表格,`--json` 输出统一 schema `{"success": bool, "data"/"error": ...}`
- 目录不存在或路径不是目录时返回结构化错误(JSON 模式下走 stdout JSON,非 JSON 模式下走 stderr 文字),退出码 1,不抛裸 traceback
- `--help` 里带真实调用示例
- 测试覆盖正常统计、递归子目录、无扩展名分组、空目录、路径解析、不存在目录、路径是文件而非目录、CLI 人类输出、CLI JSON 输出、CLI 两种模式下的结构化报错

跑测试需要 `pytest`(环境里没装,本机是 Homebrew 管理的 externally-managed Python,建议 `python3 -m venv .venv && .venv/bin/pip install pytest && .venv/bin/python -m pytest test_dirstat.py -v`)。
