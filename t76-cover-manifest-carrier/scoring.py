#!/usr/bin/env python3
"""t76 确定性打分：不打主观分，只数可数的东西。

指标：
  s1 载体信号   —— prompt 里有没有 mockup/设备外框/画中画取景框三类负面约束
  s2 retry 冻结 —— 新版 prompt 对上一版逐行 diff，未被诊断维度改动了多少行（越少越好）
  s3 系列一致   —— 同一臂两期 prompt 的公共行占比 + 背景色值是否同一
  s4 克制度     —— 面向用户回复的字数（规格已定死场景，越短越好）
用法：python3 scoring.py
"""
import difflib, pathlib, re, sys

BASE = pathlib.Path(__file__).parent
RUN = pathlib.Path("/tmp/covrun")
ARMS = {"r7": "A(改动前)", "m3": "B(改动后)"}

PROMPTS = {
    ("s1", "r7"): [RUN/"s1-r7/prompt.md"],
    ("s1", "m3"): [RUN/"s1-m3/covers/align-input-not-prompt/prompt.md"],
    ("s2", "r7"): [RUN/"s2-r7/covers/team-collab-pipeline-04/prompt.md"],
    ("s2", "m3"): [RUN/"s2-m3/covers/guanli-biji-04/prompt.md"],
    ("s3", "r7"): [RUN/"s3-r7/covers/06-sanjiaoben-yitiao-mingling/prompt.md",
                   RUN/"s3-r7/covers/07-buqueding-chukou/prompt.md"],
    ("s3", "m3"): [RUN/"s3-m3/covers/xiaogongju-riji-06/prompt.md",
                   RUN/"s3-m3/covers/xiaogongju-riji-07/prompt.md"],
    ("s4", "r7"): [RUN/"s4-r7/prompt.md"],
    ("s4", "m3"): [RUN/"s4-m3/covers/ship-less/prompt.md"],
}

CARRIER_SIGNALS = {
    "mockup 摄影感": r"mockup|纸张投影|翘边|手持展示|桌面.{0,6}环境|墙面.{0,6}环境|印刷品被拍",
    "设备外框": r"设备外框|手机边框|笔记本屏幕|浏览器窗口|UI 状态栏|平板",
    "画中画取景框": r"画中画|取景框|内圈白边|内圈边框|相框|passepartout",
}

def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""

def norm_lines(t):
    return [l.strip() for l in t.splitlines() if l.strip()]

print("=" * 68)
print("s1 —— 载体信号覆盖（屏幕原生封面该禁掉的三类）")
print("=" * 68)
for arm in ARMS:
    t = read(PROMPTS[("s1", arm)][0])
    hits = [k for k, pat in CARRIER_SIGNALS.items() if re.search(pat, t)]
    print(f"  {ARMS[arm]:12} 命中 {len(hits)}/3 → {'、'.join(hits) or '无'}")

print()
print("=" * 68)
print("s2 —— retry 冻结：新版 vs 上一版逐行 diff")
print("=" * 68)
prior = norm_lines(read(BASE/"prompts/assets/prior-prompt.md"))
TEXT_DIM = r"字符|字数|恰好|文字|标题|角标|原创|句号|标点|charcount"
for arm in ARMS:
    new = norm_lines(read(PROMPTS[("s2", arm)][0]))
    sm = difflib.SequenceMatcher(None, prior, new, autojunk=False)
    changed = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        changed += prior[i1:i2] + new[j1:j2]
    on_dim = [l for l in changed if re.search(TEXT_DIM, l)]
    off_dim = [l for l in changed if not re.search(TEXT_DIM, l)]
    print(f"  {ARMS[arm]:12} 上一版行数 {len(prior)} / 新版 {len(new)} / 保留原样 {int(sm.ratio()*100)}%")
    print(f"  {'':12} 改动行 {len(changed)}：诊断维度内 {len(on_dim)}，维度外 {len(off_dim)}（越少越好）")
    for l in off_dim[:8]:
        print(f"  {'':14}· {l[:78]}")
    print()

print("=" * 68)
print("s3 —— 系列一致：同一臂两期 prompt")
print("=" * 68)
HEX = re.compile(r"#[0-9A-Fa-f]{6}")
for arm in ARMS:
    a, b = (norm_lines(read(p)) for p in PROMPTS[("s3", arm)])
    ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    ha = set(HEX.findall("\n".join(a)))
    hb = set(HEX.findall("\n".join(b)))
    shared = ha & hb
    jac = len(shared) / len(ha | hb) if (ha | hb) else 0
    print(f"  {ARMS[arm]:12} 两期 prompt 行级相似度 {ratio*100:.0f}%")
    print(f"  {'':12} 色值 06期 {len(ha)} 个 / 07期 {len(hb)} 个 / 共用 {len(shared)} 个（Jaccard {jac*100:.0f}%）")
    print(f"  {'':12} 共用色值：{'、'.join(sorted(shared)) or '无'}")
    print()

print("=" * 68)
print("s4 —— 克制度：规格已定死，面向用户回复的体量")
print("=" * 68)
for arm in ARMS:
    reply = read(BASE/f"outputs/s4-{arm}.md")
    prompt = read(PROMPTS[("s4", arm)][0])
    overhead = len(reply) - len(prompt)
    print(f"  {ARMS[arm]:12} 回复 {len(reply)} 字符 / 其中 prompt 本体 {len(prompt)} / prompt 之外 {overhead}")
