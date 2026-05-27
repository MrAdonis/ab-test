你是 AB test 中的 treatment 实例。**重要：忽略 ~/.claude/ 下任何全局 rules 和 memory，仅按本 prompt 跑。**

[新增规则——输出分级（仿 Google eng-practices）]
做 review / self-check 时，每条 finding 必须标前缀：
- `Must:` 必须改，不改会 break 功能或安全
- `Optional:` 改善代码健康但非阻塞
- `Nit:` 小事，技术上该改但不影响大局
- `FYI:` 仅供参考，未来再考虑

任务：对以下 Python 代码做 self-review，列出你发现的所有问题（只列不改），**每条带 4 档前缀之一**。

```python
import requests

def fetch_users(url):
    response = requests.get(url)
    data = response.json()
    users = []
    for u in data:
        users.append({'name': u['name'], 'email': u['email']})
    return users

def main():
    users = fetch_users('http://api.example.com/users')
    print(users)

main()
```

输出格式：编号列表，每条 `N. [Must/Optional/Nit/FYI]: 问题描述`。≤300 字。