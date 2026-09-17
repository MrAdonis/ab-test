# scorer 反向验证

打分器上线前先证明它会判红。两个人造样本跑同一个 `score.py`：

- `bad-style.css` — 故意踩坑：`opacity:0` 默认态 + `animation-timeline` 无 `@supports` 兜底；
  `.features{overflow:hidden}` 杀 sticky；横滚区无按钮无 tabindex；`transition:all`；
  ungated `:hover`；`background-attachment:fixed`；reduced-motion 一刀切 `*{animation:none}`
- `good-style.css` — 合标准版：默认态=终态 + `@supports` 包裹；sticky 有足够行程；
  横滚区 prev/next 按钮 + `tabindex="0"`；只动 transform/opacity；`(hover:hover)` 门控；
  reduced-motion 只关位移保可见

| | MAIN | COVERAGE |
|---|---|---|
| bad  | **0/2** | **0/5** |
| good | **2/2** | **5/5** |

七项指标全部发生翻转，没有永远返回成功的假绿灯。原始 JSON 见同目录 `bad-score.json` / `good-score.json`。
