字符串 `qty` 会让乘法静默返回重复字符串而不是数字，导致结果错误。加类型转换和校验：

```python
def calc_total(items):
    total = 0
    for i in items:
        price = float(i['price'])
        qty = int(i['qty'])
        total += price * qty
    return total
```

如果数据可能更脏（负数、缺字段），可以加防御：

```python
def calc_total(items):
    total = 0.0
    for i in items:
        price = float(i['price'])
        qty = int(i['qty'])
        if price < 0 or qty < 0:
            raise ValueError(f"Invalid item: {i}")
        total += price * qty
    return total
```

现在 `banana` 的 `qty='4'` 会被正确转为 `4`，输出 `12.5`。