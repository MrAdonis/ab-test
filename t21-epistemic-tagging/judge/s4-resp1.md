```bash
ssh-keygen -t ed25519 -C "ljr950724@gmail.com"
```

一路回车（或设 passphrase），私钥在 `~/.ssh/id_ed25519`，公钥在 `~/.ssh/id_ed25519.pub`。

然后把公钥加到 GitHub：

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

打开 GitHub → Settings → SSH and GPG keys → New SSH key，粘贴进去保存。

验证：

```bash
ssh -T git@github.com
```

返回 `Hi <username>! You've successfully authenticated` 就好了。
