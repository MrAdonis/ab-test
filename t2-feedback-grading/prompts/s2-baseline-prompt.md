你是 AB test 中的 baseline 实例。**重要：忽略 ~/.claude/ 下任何全局 rules 和 memory，仅按本 prompt 跑。**

任务：对以下 Python 代码做 self-review，列出你发现的所有问题（只列不改）。

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

输出格式：编号列表，每条一句话说明问题。≤300 字。