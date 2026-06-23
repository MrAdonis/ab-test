生成密钥：

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

提示保存路径时直接回车用默认 `~/.ssh/id_ed25519`，然后设一个 passphrase（或直接回车跳过）。

复制公钥：

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

然后去 GitHub → Settings → SSH and GPG keys → New SSH key，粘贴进去，保存。

验证：

```bash
ssh -T git@github.com
```

看到 `Hi username! You've successfully authenticated` 就好了。

如果系统没自动加载密钥，把这两行加进 `~/.ssh/config`：

```
Host github.com
  IdentityFile ~/.ssh/id_ed25519
  AddKeysToAgent yes
```
