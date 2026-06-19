生成 ED25519 密钥：

```bash
ssh-keygen -t ed25519 -C "ljr950724@gmail.com"
```

一路回车（或设 passphrase）。生成后把公钥复制到剪贴板：

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

加到 SSH agent：

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

然后去 GitHub → Settings → SSH and GPG keys → New SSH key，粘贴进去保存。

验证：

```bash
ssh -T git@github.com
```

看到 `Hi <用户名>! You've successfully authenticated` 就通了。
