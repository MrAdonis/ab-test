#!/usr/bin/env python3
"""事实核查预筛层——在模型上场之前把能算的都算掉。

借的是 dasheng(lib/align.js) 的思路：模型只被问「对齐对不上的那几处」。
这里 reference = research 底本，heard = 稿件，对齐单位是数值断言。

三档输出，只有前两档值得送模型：
  MISMATCH    稿件给了某指标一个数，research 里同一指标是另一个数  → 强嫌疑
  UNVERIFIED  这个数在 research 全文里根本找不到                  → 待核实
  MATCHED     数值在 research 里逐位对上                          → 算术判过，不问模型

用法：
  prefilter.py <draft.txt> <research.txt> [--json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 稿件里的指标写法 → research 底本里的写法。项目特定（stock-daily-report），
# 换项目要换这张表；表没覆盖到的 label 自动降级成全文匹配，不会漏判成 MATCHED。
ALIASES = {
    "标普500": ["^GSPC", "S&P 500", "标普"],
    "标普": ["^GSPC", "S&P 500", "标普"],
    "纳指": ["^IXIC", "纳斯达克", "纳指"],
    "纳斯达克": ["^IXIC", "纳斯达克", "纳指"],
    "道指": ["^DJI", "道指"],
    "VIX": ["^VIX", "VIX"],
    "十年期": ["^TNX", "10年期美债", "十年期"],
    "10年期美债收益率": ["^TNX", "10年期美债"],
    "WTI": ["CL=F", "WTI"],
    "美元指数": ["DX-Y.NYB", "美元指数"],
    "标普期货": ["ES=F"],
    "纳指期货": ["NQ=F"],
    "道指期货": ["YM=F"],
    "布伦特": ["BZ=F", "布伦特"],
}

NUM = re.compile(r"(?<![\d.])(\d[\d,]*(?:\.\d+)?)\s*(%)?")
# 数值前面这一小段里找 label：中文词、大写 ticker、或 VIX/WTI 这类全大写缩写
LABEL = re.compile(r"([一-鿿]{2,10}|[A-Z][A-Za-z^=.\-]{1,12})\s*$")
# label 尾部粘上的动词/助词，剥掉才能跟 ALIASES 精确对齐（"标普期货涨" → "标普期货"）
TAIL = "涨跌报收到在的是为约共有只已至过前后计新"
# 不是事实断言的数值，按后文判定：11 月合约、2026 年、第三个周五。
# 用后文而不是数值本身——"70 万桶/日" 的 70 也是两位数，不能一刀切。
SKIP_AFTER = re.compile(r"^\s*[月年日号点]")
DATEISH = re.compile(r"^\d{4}\.\d{1,2}")


def norm(raw: str) -> str:
    """去千分位，去尾零，让 7,650.50 和 7650.5 视为同一个数。"""
    v = raw.replace(",", "")
    try:
        f = float(v)
    except ValueError:
        return v
    return f"{f:.10f}".rstrip("0").rstrip(".")


def extract(text: str):
    """抽 (label, 原始数值, 归一化值, 是否百分比, 上下文) 列表。"""
    out = []
    for m in NUM.finditer(text):
        raw, pct = m.group(1), bool(m.group(2))
        tail = text[m.end():m.end() + 3]
        if not pct and (SKIP_AFTER.match(tail) or DATEISH.match(text[m.start():])):
            continue
        head = text[max(0, m.start() - 24):m.start()]
        lm = LABEL.search(head.replace("（", " ").replace("(", " "))
        label = lm.group(1).rstrip(TAIL) if lm else ""
        ctx = text[max(0, m.start() - 30):m.end() + 16].replace("\n", " ")
        out.append({
            "label": label,
            "raw": raw + ("%" if pct else ""),
            "norm": norm(raw),
            "pct": pct,
            "context": ctx.strip(),
        })
    return out


def research_lines_for(label: str, research: str):
    """找 research 里描述这个指标的行。找不到返回 []。"""
    # 空 label 直接放弃绑定：早先版本用双向子串匹配，空串是任何串的子串，
    # 于是每个没识别出 label 的数值都被绑到第一条 alias 上，全判 MISMATCH。
    if not label:
        return []
    keys = ALIASES.get(label)
    if not keys:
        # 只认后缀精确匹配（"美股标普" → "标普"），不做双向模糊，
        # 否则 "给的标普支撑" 也会被绑到 ^GSPC 上。
        for k, v in ALIASES.items():
            if label.endswith(k):
                keys = v
                break
    if not keys:
        return []
    hits = []
    for i, line in enumerate(research.splitlines(), 1):
        if any(k in line for k in keys):
            hits.append((i, line.strip()))
    return hits


def classify(draft: str, research: str):
    research_nums = {n["norm"] for n in extract(research)}
    rows = []
    for item in extract(draft):
        lines = research_lines_for(item["label"], research)
        if lines:
            authority = {n["norm"] for ln in lines for n in extract(ln[1])}
            if item["norm"] in authority:
                verdict, evidence = "MATCHED", f"L{lines[0][0]}"
            else:
                verdict = "MISMATCH"
                evidence = " / ".join(f"L{i}: {t}" for i, t in lines[:2])
        elif item["norm"] in research_nums:
            verdict, evidence = "MATCHED", "全文命中（未绑定指标）"
        else:
            verdict, evidence = "UNVERIFIED", "research 全文无此数值"
        rows.append({**item, "verdict": verdict, "evidence": evidence})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("research")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    draft = Path(a.draft).read_text(encoding="utf-8")
    research = Path(a.research).read_text(encoding="utf-8")
    rows = classify(draft, research)

    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    order = {"MISMATCH": 0, "UNVERIFIED": 1, "MATCHED": 2}
    rows.sort(key=lambda r: order[r["verdict"]])
    counts = {k: sum(1 for r in rows if r["verdict"] == k) for k in order}

    print(f"# 预筛结果：{Path(a.draft).name}")
    print(f"共 {len(rows)} 个数值断言 — "
          f"MISMATCH {counts['MISMATCH']} · "
          f"UNVERIFIED {counts['UNVERIFIED']} · "
          f"MATCHED {counts['MATCHED']}")
    print()
    for tag in ("MISMATCH", "UNVERIFIED"):
        group = [r for r in rows if r["verdict"] == tag]
        if not group:
            continue
        print(f"## {tag}（{len(group)}）")
        for r in group:
            print(f"- [{r['label'] or '?'}] {r['raw']}  ·  …{r['context']}…")
            print(f"    底本：{r['evidence']}")
        print()
    print(f"## MATCHED（{counts['MATCHED']}）— 逐位对上，无需复核")
    for r in rows:
        if r["verdict"] == "MATCHED":
            print(f"- [{r['label'] or '?'}] {r['raw']}  ({r['evidence']})")


if __name__ == "__main__":
    sys.exit(main())
