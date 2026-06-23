期权希腊字母 + 沉稳英文风格，走 Style 3（极简黑白编辑风）最合适——文字主导、高级感、"The Greeks" 这个词本身够重量。

直接给 prompt，存文件跑 seedream 就行：

```
Editorial black and white cover, 16:9 landscape. Giant serif display text "THE GREEKS" anchored upper center, high contrast pure white on black background. Below in smaller weight: "Options Risk Metrics Explained". Minimal layout, generous white space on lower half, subtle paper texture grain overlay. No decorative elements, no color. Typography-forward, magazine editorial aesthetic, Vogue/NYT style.
```

执行：

```bash
echo '上面 prompt 内容' > /tmp/the-greeks-cover.txt
baoyu-imagine --promptfiles /tmp/the-greeks-cover.txt --ratio 16:9
```

想偏商业感（带浅色背景 + 深蓝字）的话换 Style 4，说一声我改。
