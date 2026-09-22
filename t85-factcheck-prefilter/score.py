#!/usr/bin/env python3
"""对照 ground truth 给两臂打分。

判定尽量确定性：每个注入点有唯一的 marker 数值，在该臂输出的 P0 段里
搜到即算检出。同时报全文命中数——两者不等说明模型看见了但没定成 P0，
那是「降级」不是「漏判」，人工要区别对待。

用法：score.py [输出目录，默认 /tmp/audit-out]
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
TRUTH = json.loads((HERE / "ground-truth.json").read_text(encoding="utf-8"))

# P0 段：从提到 P0 的标题行，到下一个提到 P1/P2/P3 的标题行
P0_START = re.compile(r"^#{1,4}.*P0|^\*{0,2}P0", re.M)
P0_END = re.compile(r"^#{1,4}.*P[123]|^\*{0,2}P[123]", re.M)

TRAP_MARKERS = {
    "2026-09-20": "100.30",
    "2026-09-18": "67.64",
    "2026-09-21": "52%",
}


def p0_section(text: str):
    """切出 P0 段。切不出来返回 (None, 全文)。"""
    m = P0_START.search(text)
    if not m:
        return None, text
    rest = text[m.end():]
    e = P0_END.search(rest)
    return text[m.start(): m.end() + (e.start() if e else len(rest))], text


def grade(arm: str, out_dir: Path):
    rows = []
    missing = []
    for date in TRUTH["dates"]:
        f = out_dir / f"{arm}-{date}.md"
        if not f.exists():
            missing.append(f.name)
            continue
        text = f.read_text(encoding="utf-8")
        sec, full = p0_section(text)
        scope = sec if sec is not None else full
        for inj in TRUTH["injected"]:
            if inj["date"] != date:
                continue
            if inj["marker"] == "MANUAL":
                rows.append({**inj, "arm": arm, "in_p0": None, "in_full": None,
                             "section_found": sec is not None})
                continue
            rows.append({
                **inj, "arm": arm,
                "in_p0": inj["marker"] in scope,
                "in_full": inj["marker"] in full,
                "section_found": sec is not None,
            })
    return rows, missing


def traps(arm: str, out_dir: Path):
    hits = []
    for date, marker in TRAP_MARKERS.items():
        f = out_dir / f"{arm}-{date}.md"
        if not f.exists():
            continue
        sec, full = p0_section(f.read_text(encoding="utf-8"))
        if sec and marker in sec:
            hits.append({"date": date, "marker": marker})
    return hits


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/audit-out")
    report = {}
    for arm in ("A", "B"):
        rows, missing = grade(arm, out_dir)
        auto = [r for r in rows if r["marker"] != "MANUAL"]
        report[arm] = {
            "missing_files": missing,
            "auto_total": len(auto),
            "caught_p0": sum(1 for r in auto if r["in_p0"]),
            "caught_anywhere": sum(1 for r in auto if r["in_full"]),
            "misses": [r["id"] + " " + r["note"] for r in auto if not r["in_full"]],
            "downgraded": [r["id"] + " " + r["note"]
                           for r in auto if r["in_full"] and not r["in_p0"]],
            "false_positives": traps(arm, out_dir),
            "manual_pending": [r["id"] for r in rows if r["marker"] == "MANUAL"],
        }

    print("# t85 评分\n")
    for arm, r in report.items():
        if r["missing_files"]:
            print(f"## {arm} 臂 —— 缺输出：{r['missing_files']}")
            continue
        print(f"## {arm} 臂")
        print(f"- 自动判定检出（P0 段内）：{r['caught_p0']}/{r['auto_total']}")
        print(f"- 出现在输出任何位置：  {r['caught_anywhere']}/{r['auto_total']}")
        print(f"- 误报（陷阱被判 P0）：  {len(r['false_positives'])} "
              f"{r['false_positives'] or ''}")
        if r["downgraded"]:
            print("- 提到但没定成 P0：")
            for d in r["downgraded"]:
                print(f"    · {d}")
        if r["misses"]:
            print("- 完全漏判：")
            for d in r["misses"]:
                print(f"    · {d}")
        print(f"- 待人工判定：{r['manual_pending']}（方向反转，无唯一数值可搜）")
        print()

    (HERE / "score.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
