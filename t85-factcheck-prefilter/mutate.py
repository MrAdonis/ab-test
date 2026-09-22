#!/usr/bin/env python3
"""生成变异语料 + ground truth。

从 stock-daily-report 的真实稿件出发，注入一批已知的事实错误
（数值篡改 / 方向反转 / 单位量级），每一处都与当天 research 底本
里的权威数值明确矛盾。research 本身原样复制，不动。

注入清单写死在 MUTATIONS 里而不是随机生成：AB 两臂要跑同一份语料，
随机化只会让两次运行不可比。
"""

import json
import shutil
import sys
from pathlib import Path

SRC = Path.home() / "Projects/personal/stock-daily-report/output"

# (日期, 原文片段, 变异后片段, 错误类型, research 权威值, 说明, 判定标记)
#
# 判定标记 = 评分脚本在各臂输出里搜的字符串，命中即算「检出」。选的都是
# 变异引入、且在该日稿件内唯一的数值。方向反转那条数值全对、错的是「涨/跌」
# 这个词，没有可搜的唯一数值，标 MANUAL 走人工判。
MUTATIONS = [
    # ---- 2026-09-18 ----
    ("2026-09-18",
     "纳指涨 0.39% 报 26522.54",
     "纳指涨 0.93% 报 26522.54",
     "digit_swap", "^IXIC +0.39%",
     "纳指涨幅 0.39% 被换位成 0.93%，指数点位仍对",
     "0.93"),
    ("2026-09-18",
     "VIX 收 14.81，跌 4.08%",
     "VIX 收 14.81，涨 4.08%",
     "direction_flip", "^VIX 14.81 -4.08%",
     "VIX 当天下跌，稿中改成上涨，方向反了",
     "MANUAL"),
    ("2026-09-18",
     "美元指数收 100.21 基本纹丝不动",
     "美元指数收 101.20 基本纹丝不动",
     "digit_swap", "DX-Y.NYB 100.21",
     "美元指数 100.21 被换位成 101.20",
     "101.20"),
    ("2026-09-18",
     "WTI 单日跌 6.32% 收 95.47 美元",
     "WTI 单日跌 6.32% 收 105.47 美元",
     "magnitude", "CL=F 95.47 -6.32%",
     "WTI 收盘价被抬高 10 美元，与同句跌幅不自洽",
     "105.47"),

    # ---- 2026-09-20 ----
    ("2026-09-20",
     "标普期货涨 0.35%，纳指期货涨 0.54%",
     "标普期货涨 0.53%，纳指期货涨 0.54%",
     "digit_swap", "ES=F +0.35%",
     "标普期货涨幅 0.35% 被换位成 0.53%",
     "0.53"),
    ("2026-09-20",
     "八月只有 70 万桶/日",
     "八月只有 170 万桶/日",
     "magnitude", "JPMorgan：八月仅 70 万桶/日",
     "八月外运量 70 万桶/日被改成 170 万，削弱了对比",
     "170"),
    ("2026-09-20",
     "美联储把联邦基金利率上调 25 个基点到 3.75% 到 4.00%",
     "美联储把联邦基金利率上调 50 个基点到 3.75% 到 4.00%",
     "internal_inconsistency", "加息 25bp 至 3.75%-4.00%",
     "加息幅度改成 50bp，与同句给出的目标区间自相矛盾",
     "50 个基点"),
    ("2026-09-20",
     "Schwab 给的标普支撑在 7600",
     "Schwab 给的标普支撑在 7400",
     "digit_swap", "Schwab：标普支撑 7600",
     "支撑位 7600 被改成 7400，且与末段『7600 就要真的去试』不一致",
     "7400"),

    # ---- 2026-09-21 ----
    ("2026-09-21",
     "纳斯达克 27,122.09 涨 2.26%",
     "纳斯达克 27,122.09 涨 2.62%",
     "digit_swap", "^IXIC +2.26%",
     "纳指涨幅 2.26% 被换位成 2.62%",
     "2.62"),
    ("2026-09-21",
     "道指只涨 0.71% 到 52,048.83",
     "道指只涨 0.17% 到 52,048.83",
     "digit_swap", "^DJI +0.71%",
     "道指涨幅 0.71% 被换位成 0.17%",
     "0.17"),
    ("2026-09-21",
     "10 年期美债收益率 4.96%",
     "10 年期美债收益率 4.69%",
     "digit_swap", "^TNX 4.96",
     "十年期 4.96% 被换位成 4.69%，且与同句『没离开 5% 这个门口』矛盾",
     "4.69"),
    ("2026-09-21",
     "VIX 14.87，基本没动",
     "VIX 15.87，基本没动",
     "magnitude", "^VIX 14.87 +0.41%",
     "VIX 被抬高 1 点，与『基本没动』不符",
     "15.87"),
]

# 天然存在、不应被标成事实错误的陷阱点——用来量误报。
# 这些在原稿里就是对的（或 research 里有显式说明），两臂都不该判 P0。
TRAPS = [
    ("2026-09-20", "WTI 上周五结算在 100.30 美元",
     "research 有换月说明：CL=F previous_close 96.08 ≠ 9/18 日线 100.30，"
     "稿件自己也写了『两个数不能直接相减』"),
    ("2026-09-18", "白银涨 2.34% 到 67.64 美元/盎司",
     "research 新闻段只给了 silver +2.34%，67.64 这个绝对价格底本里没有——"
     "属于无法核实，不等于错误"),
    ("2026-09-21", "Polymarket 上「美联储十月会议后加息 25 个基点」还挂在 52%",
     "research 结构化块里没有 Polymarket，属无法核实，不等于错误"),
]


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/audit-corpus")
    out.mkdir(parents=True, exist_ok=True)

    dates = sorted({m[0] for m in MUTATIONS})
    truth = {"corpus": str(out), "dates": dates, "injected": [], "traps": []}

    for date in dates:
        draft = (SRC / f"{date}.txt").read_text(encoding="utf-8")
        shutil.copy(SRC / f"{date}_research.txt", out / f"{date}_research.txt")

        for i, entry in enumerate(MUTATIONS):
            d, old, new, kind, authority, note, marker = entry
            if d != date:
                continue
            count = draft.count(old)
            if count != 1:
                raise SystemExit(
                    f"注入点在 {date} 命中 {count} 次（要求恰好 1）：{old!r}"
                )
            draft = draft.replace(old, new)
            truth["injected"].append({
                "id": f"{date}#{i}",
                "date": date,
                "kind": kind,
                "original": old,
                "mutated": new,
                "research_authority": authority,
                "note": note,
                "marker": marker,
            })

        (out / f"{date}.txt").write_text(draft, encoding="utf-8")

    # marker 必须在变异稿里唯一，否则评分会把无关命中算成检出
    for inj in truth["injected"]:
        if inj["marker"] == "MANUAL":
            continue
        text = (out / f"{inj['date']}.txt").read_text(encoding="utf-8")
        n = text.count(inj["marker"])
        if n != 1:
            raise SystemExit(
                f"判定标记 {inj['marker']!r} 在 {inj['date']} 稿件里出现 {n} 次（要求 1）"
            )

    for date, span, why in TRAPS:
        truth["traps"].append({"date": date, "span": span, "why": why})

    Path(__file__).with_name("ground-truth.json").write_text(
        json.dumps(truth, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"corpus  -> {out}  ({len(dates)} 天)")
    print(f"injected: {len(truth['injected'])} 处"
          f"（可自动判定 {sum(1 for i in truth['injected'] if i['marker'] != 'MANUAL')}，"
          f"人工判定 {sum(1 for i in truth['injected'] if i['marker'] == 'MANUAL')}）")
    print(f"traps   : {len(truth['traps'])} 处")


if __name__ == "__main__":
    main()
