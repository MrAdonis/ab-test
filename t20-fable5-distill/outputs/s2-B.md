在终端运行：

```bash
ssh-keygen -t ed25519 -C "ljr950724@gmail.com"
```

一路回车（接受默认路径 `~/.ssh/id_ed25519`，密码可留空或设一个）。然后复制公钥：

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

去 GitHub → Settings → SSH and GPG keys → New SSH key，粘贴进去，保存。验证：

```bash
ssh -T git@github.com
```

看到 `Hi username! You've successfully authenticated` 就通了。
