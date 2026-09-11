#!/usr/bin/env python3
"""每个埋点一组关键词，命中任一即算"提到"。粗估发现率，不判归因。先于模型评审跑。"""
import re, glob, os
K = {
 "task1-membership": {
  "C1": r"31", "C2": r"顺延|原到期|剩余天|覆盖.*到期|到期.*覆盖", "C3": r"验签|签名|sign",
  "S1": r"关闭.*回调|回调.*关闭|closed|扣了钱|已支付.*关单|关单后", "S2": r"多端|多设备|另一台|旧设备|互踢|踢下线|单设备|同时登录",
  "S3": r"价格|1990|19900|定价|PRICE"},
 "task2-csv-export": {
  "C1": r"取消|cancelled|pending", "C2": r"toFixed|两位小数|一位小数", "C3": r"含当天|结束日|end.*不含|< end|包含结束",
  "S1": r"BOM|乱码|GBK|编码", "S2": r"时区|UTC|北京时间|toISOString",
  "S3": r"中文标签|枚举|英文|已支付.*已发货|状态.*映射|映射.*状态"}}
here = os.path.dirname(os.path.abspath(__file__))
print(f"{'file':28} hits items")
for f in sorted(glob.glob(f"{here}/outputs/*.md")):
    base = os.path.basename(f)[:-3]; task = re.sub(r"-[A-Z]\d$", "", base)
    txt = open(f).read()
    hit = [k for k, pat in K[task].items() if re.search(pat, txt, re.I)]
    print(f"{base:28} {len(hit):<4} {' '.join(hit)}")
