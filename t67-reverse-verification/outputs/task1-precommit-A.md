本地 `.env` 文件还在(138 字节,原样),只是从 git 索引移除了,不影响本地跑 `npm start`。

现在所有改动都已 staged 但**没有提交**——按惯例改动不擅自 commit,留给你确认。做完的事和用法说明如下:

## 加了什么

**`scripts/check-secrets.js`** — 实际检查逻辑(纯 Node,零依赖):
- **文件名拦截**:`.env` / `.env.*`(除了 `.env.example`/`.sample`/`.template`)、`*.pem`、`*.key`、`*.p12/.pfx`、`id_rsa` 等 SSH 私钥、`credentials.json`、`*service-account*.json` —— 这类文件本身一旦出现在暂存区就直接拦,不管内容
- **内容扫描**:只扫本次新增的行(`git diff --cached -U0`),命中 Stripe live key(`sk_live_`/`rk_live_`)、AWS Access Key、GitHub token、Slack token、Google API key、PEM 私钥块、以及 `apiKey/secret/token/password = "一串很长的字符串"` 这类硬编码赋值模式就拦。终端只打印脱敏后的片段(`sk_l****...0001`),不会把完整密钥回显到终端历史里

**`.githooks/pre-commit`** — git 钩子入口,调用上面的脚本

**`package.json`** 加了 `"prepare": "git config core.hooksPath .githooks"` —— 这样任何人 `npm install` 时会自动把 hooks 目录指过去,不用额外装 husky 之类的包。我也在当前仓库手动跑了这行,现在就是生效状态

**`.gitignore`** 补了 `.env` / `.env.*`(留 `!.env.example` 例外)——这是最根本的一道防线:之前它压根没在 `.gitignore` 里,所以 `git add .` 才会顺手带上真的 `.env`。加了这条以后普通 `git add -A` 不会再碰到它,pre-commit 脚本是防"手滑 `-f` 强推"的第二道

**顺手清理**:发现当前仓库 HEAD 里 `.env`(带占位 Stripe key)其实一直被 track 着——防线等于形同虚设。已经 `git rm --cached .env` 把它移出版本控制(本地文件没删,`npm start` 不受影响)。

## 已验证

- 正常改动(比如这次的几个文件)照常能过
- 手工造了一条 `sk_live_...` 硬编码测试,确认会被拦下并给出脱敏提示,已清理测试文件

## 怎么用

- 现在这个仓库已经生效(我手动跑过 `git config core.hooksPath .githooks`),其他人 clone 后跑一次 `npm install` 会自动配好
- 真拦到东西时会告诉你 `文件:行号 + 原因`,提示 `git restore --staged <file>` 撤销暂存后再改
- 真的误报可以 `git commit --no-verify` 跳过,但这是留了个口子,不建议养成习惯

所有改动目前是 **staged 未 commit** 状态,你可以先 `git diff --cached` 看一遍,确认没问题了告诉我要不要帮你 commit。
