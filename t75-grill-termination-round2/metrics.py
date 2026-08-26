#!/usr/bin/env python3
"""t75 确定性指标：从 outputs/*.json 算终止行为与追问结构，不做质量判断。"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
Q = re.compile(r"[?？]")

rows = []
for path in sorted(glob.glob(f"{HERE}/outputs/*.json")):
    d = json.load(open(path))
    m, tr = d["meta"], d["transcript"]
    advisor = [t for r, t in tr if r == "advisor"]
    noinfo = m["noinfo_turns"]
    first_noinfo = noinfo[0] if noinfo else None
    rows.append({
        "run": f"{m['task']}-{m['arm']}",
        "turns": m["turns"],
        "self_stopped": m["stopped"],
        "noinfo_turns": noinfo,
        # 用户第一次答不出之后，顾问还追问了几轮
        "asks_after_first_noinfo": (m["turns"] - first_noinfo) if first_noinfo else 0,
        "questions_total": sum(len(Q.findall(a)) for a in advisor),
        "avg_advisor_chars": round(sum(len(a) for a in advisor) / max(len(advisor), 1)),
    })

w = max(len(r["run"]) for r in rows)
print(f"{'run'.ljust(w)}  turns  stop?  noinfo轮次        空转轮数  问号数  均长")
for r in rows:
    print(f"{r['run'].ljust(w)}  {r['turns']:5}  {str(r['self_stopped']):5}  "
          f"{str(r['noinfo_turns']).ljust(16)}  {r['asks_after_first_noinfo']:8}  "
          f"{r['questions_total']:6}  {r['avg_advisor_chars']:4}")
