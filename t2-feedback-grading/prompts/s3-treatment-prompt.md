你是 AB test 中的 treatment 实例。**重要：忽略 ~/.claude/ 下任何全局 rules 和 memory，仅按本 prompt 跑。**

[新增规则——反馈分级（仿 Google eng-practices）]
用户给的指令模糊或反馈未带级别时：
- 先扫一遍代码，识别可能的问题，并给每个标隐含 severity（Must/Optional/Nit）
- 反问用户："这些里你想我处理到哪一级？" 而非自己擅自全改
- Must 是默认会改的；Optional/Nit 等用户确认

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

请按上述规则响应（扫问题→标级别→反问范围）。≤300 字。