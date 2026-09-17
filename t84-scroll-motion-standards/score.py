#!/usr/bin/env python3
"""t84 确定性打分器。

用法: python3 score.py <site-dir> <out.json>

主指标（硬，0/1，与实现路径无关）
  M1 reduced-motion 下关键内容仍可见   —— 降级不能变成"内容消失"
  M2 动画引擎失效时关键内容仍可见       —— animation-timeline 不被支持 / 入场动画没跑 的兜底

覆盖指标（0/1）
  M3 功能区确实被钉住（sticky 或等价）
  M4 横向滚动区有非指针等价入口（按钮 / 可聚焦容器）
  M5 只动 GPU 属性（无 transition:all / 无动画 layout 属性）
  M6 hover 动效有 (hover:hover) 门控（无 hover 动效则 N/A）
  M7 视差用 transform（无 background-attachment:fixed / top / margin 驱动）
"""
import json, re, subprocess, sys, threading, time, http.server, socketserver, functools, pathlib

KEY_SELECTORS = ["h1", ".step p", ".case p"]


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(dirpath):
    handler = functools.partial(_Quiet, directory=str(dirpath))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def visible_after_scroll(pw, url, reduced, kill_anim):
    """滚完整页后，关键内容元素的最小 opacity。"""
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 800},
                        reduced_motion="reduce" if reduced else "no-preference")
    if kill_anim:
        ctx.add_init_script("""
          document.addEventListener('DOMContentLoaded', () => {
            const s = document.createElement('style');
            s.textContent = '*,*::before,*::after{animation:none !important;animation-timeline:none !important}';
            document.head.appendChild(s);
          });
        """)
    pg = ctx.new_page()
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(600)
    worst, detail = 1.0, {}
    for sel in KEY_SELECTORS:
        for el in pg.query_selector_all(sel):
            try:
                el.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass
            pg.wait_for_timeout(450)
            info = el.evaluate("""e => {
              let node = e, eff = 1;
              while (node && node.nodeType === 1) {
                const cs = getComputedStyle(node);
                eff *= parseFloat(cs.opacity);
                if (cs.visibility === 'hidden' || cs.display === 'none') eff = 0;
                node = node.parentElement;
              }
              const r = e.getBoundingClientRect();
              return {eff, w: r.width, h: r.height, text: (e.textContent||'').slice(0,12)};
            }""")
            eff = info["eff"] if info["w"] > 0 and info["h"] > 0 else 0.0
            if eff < worst:
                worst, detail = eff, info
    b.close()
    return round(worst, 3), detail


def pinned(pw, url):
    """功能区滚动时左侧视觉元素被钉住的行程 >= 0.8 屏高即算做到。"""
    VH = 800
    b = pw.chromium.launch()
    pg = b.new_context(viewport={"width": 1280, "height": VH}).new_page()
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(500)
    box = pg.evaluate("""() => {
      const s = document.querySelector('#features');
      if (!s) return null;
      const r = s.getBoundingClientRect();
      return {top: r.top + scrollY, h: r.height};
    }""")
    if not box:
        b.close()
        return False, {"err": "no #features"}
    start, end = box["top"], box["top"] + box["h"] - VH
    if end <= start:
        b.close()
        return False, {"err": "section shorter than viewport", "section_h": round(box["h"])}
    N = 12
    step = (end - start) / (N - 1)
    tops = []
    for i in range(N):
        pg.evaluate(f"scrollTo(0, {start + step * i})")
        pg.wait_for_timeout(250)
        tops.append(pg.evaluate("""() => {
          const el = document.querySelector('.feature-visual') || document.querySelector('#features > *');
          if (!el) return null;
          return el.getBoundingClientRect().top;
        }"""))
    b.close()
    if any(t is None for t in tops):
        return False, {"err": "no visual el"}
    best = cur = 0.0
    for i in range(1, N):
        if abs(tops[i] - tops[i - 1]) <= 24:
            cur += step
            best = max(best, cur)
        else:
            cur = 0.0
    return best >= 0.8 * VH, {"pinned_px": round(best), "need": round(0.8 * VH),
                              "section_h": round(box["h"]), "tops": [round(t) for t in tops]}


def h_scroll_equiv(pw, url):
    b = pw.chromium.launch()
    pg = b.new_context(viewport={"width": 1280, "height": 800}).new_page()
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(500)
    res = pg.evaluate("""() => {
      const cases = document.querySelector('#cases');
      if (!cases) return {scroller:false};
      const all = [cases, ...cases.querySelectorAll('*')];
      const sc = all.find(e => {
        const cs = getComputedStyle(e);
        return /auto|scroll/.test(cs.overflowX) && e.scrollWidth > e.clientWidth + 8;
      });
      const btns = cases.querySelectorAll('button, [role="button"]').length;
      return {
        scroller: !!sc,
        tabindex: sc ? sc.getAttribute('tabindex') : null,
        buttons: btns,
      };
    }""")
    b.close()
    ok = bool(res.get("scroller")) and (res.get("buttons", 0) >= 2 or res.get("tabindex") is not None)
    return ok, res


def static_checks(site):
    css = ""
    for p in pathlib.Path(site).rglob("*.css"):
        css += p.read_text(errors="ignore")
    html = ""
    for p in list(pathlib.Path(site).rglob("*.html")) + list(pathlib.Path(site).rglob("*.js")):
        html += p.read_text(errors="ignore")
    blob = css + "\n" + html

    layout_props = r"\b(top|left|right|bottom|width|height|margin[a-z-]*|padding[a-z-]*|background-position)\b"
    bad_transition = bool(re.search(r"transition\s*:\s*all\b", css))
    trans_layout = [m.group(0) for m in re.finditer(r"transition(?:-property)?\s*:\s*[^;{}]*", css)
                    if re.search(layout_props, m.group(0))]
    kf_layout = []
    for m in re.finditer(r"@keyframes[^{]*\{(?:[^{}]*\{[^{}]*\}\s*)*\}", css):
        body = m.group(0)
        for pm in re.finditer(r"(?m)^\s*([a-z-]+)\s*:", body):
            if re.fullmatch(layout_props, pm.group(1)):
                kf_layout.append(pm.group(1))
    m5 = not bad_transition and not trans_layout and not kf_layout

    hover_motion = re.findall(r":hover[^{]*\{[^}]*(?:transform|animation)\s*:", css)
    hover_gate = bool(re.search(r"@media[^{]*\(\s*hover\s*:\s*hover", css))
    m6 = None if not hover_motion else hover_gate

    bg_fixed = bool(re.search(r"background-attachment\s*:\s*fixed", css))
    parallax_layout = bool(re.search(r"style\.(?:top|marginTop)|setProperty\(\s*['\"](?:top|margin-top)", blob))
    m7 = not bg_fixed and not parallax_layout

    rm_block = re.search(r"@media[^{]*prefers-reduced-motion[^{]*\{", css)
    rm_present = bool(rm_block)
    rm_blanket = bool(re.search(r"prefers-reduced-motion[^{]*\{\s*\*", css))

    return {
        "M5_gpu_only": m5,
        "M5_detail": {"transition_all": bad_transition, "transition_layout": trans_layout[:3],
                      "keyframe_layout": sorted(set(kf_layout))},
        "M6_hover_gated": m6,
        "M6_detail": {"hover_motion_rules": len(hover_motion), "hover_media_query": hover_gate},
        "M7_parallax_transform": m7,
        "M7_detail": {"background_attachment_fixed": bg_fixed, "layout_driven": parallax_layout},
        "reduced_motion_block": rm_present,
        "reduced_motion_blanket_kill": rm_blanket,
        "uses_animation_timeline": bool(re.search(r"animation-timeline\s*:", css)),
        "uses_supports_guard": bool(re.search(r"@supports[^{]*animation-timeline", css)),
        "uses_intersection_observer": "IntersectionObserver" in blob,
    }


def main():
    site, out = sys.argv[1], sys.argv[2]
    from playwright.sync_api import sync_playwright
    httpd, port = serve(site)
    url = f"http://127.0.0.1:{port}/index.html"
    r = {}
    with sync_playwright() as pw:
        op, det = visible_after_scroll(pw, url, reduced=True, kill_anim=False)
        r["M1_reduced_motion_visible"] = op >= 0.9
        r["M1_detail"] = {"min_effective_opacity": op, "worst": det}

        op2, det2 = visible_after_scroll(pw, url, reduced=False, kill_anim=True)
        r["M2_anim_disabled_visible"] = op2 >= 0.9
        r["M2_detail"] = {"min_effective_opacity": op2, "worst": det2}

        ok3, d3 = pinned(pw, url)
        r["M3_features_pinned"], r["M3_detail"] = ok3, d3

        ok4, d4 = h_scroll_equiv(pw, url)
        r["M4_hscroll_nonpointer_entry"], r["M4_detail"] = ok4, d4
    httpd.shutdown()
    r.update(static_checks(site))

    main_score = sum(1 for k in ("M1_reduced_motion_visible", "M2_anim_disabled_visible") if r[k])
    cov_keys = ["M3_features_pinned", "M4_hscroll_nonpointer_entry", "M5_gpu_only",
                "M6_hover_gated", "M7_parallax_transform"]
    cov = sum(1 for k in cov_keys if r[k] is True)
    cov_total = sum(1 for k in cov_keys if r[k] is not None)
    r["MAIN_SCORE"] = f"{main_score}/2"
    r["COVERAGE_SCORE"] = f"{cov}/{cov_total}"
    pathlib.Path(out).write_text(json.dumps(r, ensure_ascii=False, indent=2))
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
