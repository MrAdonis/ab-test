你是 AB test 中的 baseline 实例。**重要：忽略 ~/.claude/ 下任何全局 rules 和 memory，仅按本 prompt 跑。**

用户说："改一下"，代码如下：

```python
def calc_total(items):
    total = 0
    for i in items:
        total += i['price'] * i['qty']
    return total

# 测试
items = [
    {'name': 'apple', 'price': 1.5, 'qty': 3},
    {'name': 'banana', 'price': 0.5, 'qty': '4'},  # qty 是字符串
    {'name': 'cherry', 'price': 2.0, 'qty': 2}
]
print(calc_total(items))
```

请按你认为合理的方式响应。≤300 字。