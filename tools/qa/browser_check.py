#!/usr/bin/env python3
"""
Browser QA (headless Chromium via Playwright).

  pip install playwright            # Chromium must be available to Playwright
  python3 tools/qa/browser_check.py                         # serves deployment/public_html locally
  python3 tools/qa/browser_check.py https://lateralrepairs.com/   # after deployment

Loads every page, checks JS errors / failed requests / images / horizontal overflow at
9 widths, and exercises every interactive component. Exit code 1 on any FAIL.
"""
import functools
import os
import http.server
import pathlib
import re
import sys
import threading
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parents[2]
PKG = REPO / "deployment" / "public_html"
SITE = "https://www.lateralrepairs.com/"
WIDTHS = [320, 375, 390, 414, 768, 1024, 1280, 1440, 1920]
LAUNCH_ARGS = ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"]

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((bool(ok), name, detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  — {detail}" if detail and not ok else ""), flush=True)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(directory):
    handler = functools.partial(QuietHandler, directory=str(directory))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/"


OVERFLOW_JS = """() => {
  const vw = document.documentElement.clientWidth, off = [];
  document.querySelectorAll('body *').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height || (r.right <= vw + 1 && r.left >= -1)) return;
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const o = getComputedStyle(p);
      if (o.position === 'fixed' || o.visibility === 'hidden') return;
      if (/(hidden|clip|auto|scroll)/.test(o.overflowX)) { const pr = p.getBoundingClientRect(); if (pr.right <= vw + 1 && pr.left >= -1) return; }
    }
    off.push(el.tagName.toLowerCase() + '.' + String(el.className).split(' ')[0] + ` [${Math.round(r.left)}..${Math.round(r.right)}]`);
  });
  return {sw: document.documentElement.scrollWidth, vw, off: off.slice(0, 4), n: off.length};
}"""

# The site uses scroll-behavior:smooth, so test scrolling must be instant or checks run mid-scroll.
SCROLL_JS = """async () => {
  const go = y => window.scrollTo({top: y, behavior: 'instant'});
  for (let y = 0; y <= document.documentElement.scrollHeight; y += Math.round(innerHeight * 0.6)) {
    go(y); await new Promise(r => setTimeout(r, 60)); }
  go(document.documentElement.scrollHeight); await new Promise(r => setTimeout(r, 400));
  go(0); await new Promise(r => setTimeout(r, 250));
}"""

VISIBLE_JS = "(sel) => { const e = document.querySelector(sel); if (!e) return false; const cs = getComputedStyle(e); const r = e.getBoundingClientRect(); return !e.hidden && cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0; }"


def pages_from_sitemap(ctx, base):
    xml = ctx.request.get(urljoin(base, "sitemap-lr.xml")).text()
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    return [u.replace(SITE, base) for u in urls]


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else serve(PKG)
    if not base.endswith("/"):
        base += "/"
    print(f"Browser QA against {base}\n")
    with sync_playwright() as p:
        b = p.chromium.launch(args=LAUNCH_ARGS)
        if os.environ.get("LR_INSECURE_TLS"):  # local HTTPS test server with a self-signed certificate
            _orig = b.new_context
            b.new_context = lambda **kw: _orig(ignore_https_errors=True, **kw)

        # ===================== every page, desktop =====================
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        listed = pages_from_sitemap(ctx, base)
        check("sitemap lists the 18 indexable pages (home + 17 products)", len(listed) == 18, str(len(listed)))
        # noindex legal pages are not in the sitemap but are tested like every other page
        pages = listed + [base + "privacy.html", base + "cookies.html"]
        for url in pages:
            rel = url[len(base):] or "/"
            r = ctx.request.get(url)
            pg = ctx.new_page()
            errs, failed = [], []
            pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
            pg.on("console", lambda m, errs=errs: errs.append("console.error: " + m.text) if m.type == "error" else None)
            pg.on("requestfailed", lambda q, failed=failed: failed.append(f"{q.url} {q.failure}") if "youtube" not in q.url else None)
            pg.on("response", lambda q, failed=failed: failed.append(f"{q.status} {q.url}") if q.status >= 400 else None)
            pg.goto(url, wait_until="load")
            pg.evaluate(SCROLL_JS)
            badimg = pg.evaluate("() => [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'))")
            canon = pg.evaluate("() => document.querySelector('link[rel=canonical]')?.href")
            canon_status = ctx.request.get(canon.replace(SITE, base)).status if canon else None
            has_settings = pg.evaluate("() => !!document.getElementById('cookieSettings') && !!document.getElementById('consent')")
            check(f"[{rel}] HTTP 200, no JS errors, no failed requests, no broken images, canonical resolves, Cookie settings present",
                  r.status == 200 and not errs and not failed and not badimg and canon_status == 200 and has_settings,
                  f"status={r.status} errs={errs[:2]} failed={failed[:2]} badimg={badimg} canonical={canon}->{canon_status} cookieSettings={has_settings}")
            pg.close()
        ctx.close()

        # ===================== responsive =====================
        bad = []
        for w in WIDTHS:
            mobile = w <= 414
            c = b.new_context(viewport={"width": w, "height": 740 if mobile else 850}, is_mobile=mobile, has_touch=mobile,
                              device_scale_factor=2 if mobile else 1)
            for url in pages:
                pg = c.new_page(); errs = []
                pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
                pg.goto(url, wait_until="load"); pg.evaluate(SCROLL_JS)
                o = pg.evaluate(OVERFLOW_JS)
                if o["sw"] > o["vw"] or o["n"] or errs:
                    bad.append(f"{w}px {url[len(base):] or '/'}: sw={o['sw']} vw={o['vw']} off={o['off']} errs={errs[:1]}")
                pg.close()
            c.close()
        check(f"no horizontal overflow / clipped elements / JS errors on 20 pages × {len(WIDTHS)} widths ({WIDTHS[0]}–{WIDTHS[-1]}px)", not bad, "; ".join(bad[:6]))

        # ===================== home page, desktop =====================
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        home = base
        pg = ctx.new_page(); perr = []
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.goto(home, wait_until="load"); pg.wait_for_timeout(600)
        pg.evaluate(SCROLL_JS)
        unrev = pg.evaluate("() => [...document.querySelectorAll('.reveal:not(.in)')].filter(e => e.offsetParent !== null).length")
        check("all visible .reveal sections are revealed after scrolling", unrev == 0, f"{unrev} unrevealed")
        gl = pg.evaluate("() => document.getElementById('pipe3d').width")
        check("3D hero canvas initialised (WebGL)", gl > 300, f"canvas width {gl}")
        t0 = pg.evaluate("() => document.querySelector('.nav__logo .brand__mark').style.transform")
        pg.evaluate("window.scrollTo({top: 900, behavior: 'instant'})"); pg.wait_for_timeout(400)
        t1 = pg.evaluate("() => document.querySelector('.nav__logo .brand__mark').style.transform")
        pg.evaluate("window.scrollTo({top: 0, behavior: 'instant'})"); pg.wait_for_timeout(300)
        check("hero logo starts in the hero and docks into the nav on scroll", "scale" in t0 and t1 == "", f"top={t0!r} scrolled={t1!r}")

        # mega-menu (mouse)
        pg.hover("#megaTrigger"); pg.wait_for_timeout(400)
        check("mega-menu opens on hover", pg.evaluate(VISIBLE_JS, "#megaMenu"))
        pg.hover("[data-mega-cat=resins]"); pg.wait_for_timeout(200)
        check("mega-menu category switch", pg.evaluate("() => document.querySelector('[data-mega-panel=resins]').classList.contains('is-active')"))
        n = pg.evaluate("() => document.querySelectorAll('#megaMenu a[href^=\"products/\"]').length")
        check("mega-menu lists all 17 product pages", n == 17, str(n))
        # closing runs a 160 ms leave-delay + 280 ms fade before [hidden] is set
        pg.keyboard.press("Escape"); pg.wait_for_timeout(1000)
        esc = pg.evaluate("() => ({visible: (" + VISIBLE_JS + ")('#megaMenu'), open: document.querySelector('[data-mega-root]').classList.contains('is-open'), active: document.activeElement.id})")
        check("Escape closes the mega-menu (mouse-opened) and it stays closed",
              not esc["visible"] and not esc["open"] and esc["active"] == "megaTrigger", str(esc))
        pg.mouse.move(700, 600); pg.wait_for_timeout(300)

        # mega-menu (keyboard)
        k = ctx.new_page(); k.goto(home, wait_until="load"); k.wait_for_timeout(400)
        for _ in range(20):
            k.keyboard.press("Tab")
            if k.evaluate("() => document.activeElement.id") == "megaTrigger":
                break
        k.wait_for_timeout(350)
        check("keyboard: focusing Products opens the mega-menu", k.evaluate(VISIBLE_JS, "#megaMenu"))
        k.keyboard.press("Tab"); k.keyboard.press("Tab"); k.wait_for_timeout(100)
        inside = k.evaluate("() => !!document.activeElement.closest('#megaMenu')")
        k.keyboard.press("Escape"); k.wait_for_timeout(700)
        check("keyboard: Escape from inside the mega-menu closes it and returns focus to Products",
              inside and not k.evaluate(VISIBLE_JS, "#megaMenu") and k.evaluate("() => document.activeElement.id") == "megaTrigger")
        k.hover("#megaTrigger"); k.wait_for_timeout(300); k.hover("[data-mega-cat=consumables]"); k.wait_for_timeout(200)
        with k.expect_navigation():
            k.click("[data-mega-panel=consumables] a[href='products/end-cap-glue.html']")
        check("mega-menu product link navigates", k.url.endswith("products/end-cap-glue.html"), k.url)
        k.close()

        # catalogue picker (mouse)
        pg.evaluate("document.getElementById('products').scrollIntoView({behavior: 'instant'})"); pg.wait_for_timeout(400)
        pg.click("#pickerBtn"); pg.wait_for_timeout(150)
        opened = pg.evaluate("() => document.querySelector('[data-picker]').hasAttribute('data-open')")
        pg.click("[data-pick=resins]"); pg.wait_for_timeout(150)
        st = pg.evaluate("() => ({lab: document.getElementById('pickerLabel').textContent, act: document.querySelector('[data-cat-panel=resins]').classList.contains('is-active'), open: document.querySelector('[data-picker]').hasAttribute('data-open'), cards: document.querySelectorAll('[data-cat-panel=resins] a.pcard').length})")
        check("picker (mouse): opens, selects Resins, closes, shows 5 cards", opened and st["act"] and not st["open"] and st["lab"] == "Resins" and st["cards"] == 5, str(st))

        # catalogue picker (keyboard)
        q = ctx.new_page(); q.goto(home, wait_until="load"); q.wait_for_timeout(400)
        q.focus("#pickerBtn"); q.keyboard.press("Enter"); q.wait_for_timeout(150)
        a1 = q.evaluate("() => [document.querySelector('[data-picker]').hasAttribute('data-open'), document.activeElement.getAttribute('data-pick')]")
        q.keyboard.press("ArrowDown"); q.wait_for_timeout(80)
        a2 = q.evaluate("() => document.activeElement.getAttribute('data-pick')")
        q.keyboard.press("ArrowDown"); q.keyboard.press("ArrowDown"); q.wait_for_timeout(80)
        a3 = q.evaluate("() => document.activeElement.getAttribute('data-pick')")  # wraps to liners
        q.keyboard.press("End"); q.wait_for_timeout(80)
        a4 = q.evaluate("() => document.activeElement.getAttribute('data-pick')")
        q.keyboard.press("Enter"); q.wait_for_timeout(150)
        a5 = q.evaluate("() => [document.getElementById('pickerLabel').textContent, document.querySelector('[data-cat-panel=consumables]').classList.contains('is-active'), document.querySelector('[data-picker]').hasAttribute('data-open'), document.activeElement.id]")
        check("picker (keyboard): Enter opens & focuses selected option; arrows/End move; Enter selects; focus returns",
              a1 == [True, "liners"] and a2 == "resins" and a3 == "liners" and a4 == "consumables" and a5 == ["Other consumables", True, False, "pickerBtn"],
              f"{a1} {a2} {a3} {a4} {a5}")
        q.keyboard.press("ArrowDown"); q.wait_for_timeout(120)
        b1 = q.evaluate("() => [document.querySelector('[data-picker]').hasAttribute('data-open'), document.activeElement.getAttribute('data-pick')]")
        q.keyboard.press("Escape"); q.wait_for_timeout(120)
        b2 = q.evaluate("() => [document.querySelector('[data-picker]').hasAttribute('data-open'), document.activeElement.id]")
        q.keyboard.press("Enter"); q.wait_for_timeout(120); q.keyboard.press("Tab"); q.wait_for_timeout(120)
        b3 = q.evaluate("() => document.querySelector('[data-picker]').hasAttribute('data-open')")
        check("picker (keyboard): ArrowDown on button opens; Escape closes to button; Tab closes",
              b1 == [True, "consumables"] and b2 == [False, "pickerBtn"] and b3 is False, f"{b1} {b2} {b3}")
        q.close()

        d = ctx.new_page(); d.goto(home + "#products-consumables", wait_until="load"); d.wait_for_timeout(300)
        check("deep link #products-consumables opens that category", d.evaluate("() => document.querySelector('[data-cat-panel=consumables]').classList.contains('is-active')"))
        d.close()

        pg.evaluate("document.querySelector('.num[data-count]').scrollIntoView({behavior: 'instant'})"); pg.wait_for_timeout(2200)
        nums = pg.evaluate("() => [...document.querySelectorAll('.num[data-count]')].map(n => [n.textContent.trim(), n.dataset.count + (n.dataset.suffix || '')])")
        check("count-up stats reach their targets", all(a == b_ for a, b_ in nums), str(nums))

        # keyboard tab order on representative pages: never lands on hidden things, always visible focus
        for path in ["", "products/calibration-hoses.html", "privacy.html"]:
            t = ctx.new_page(); t.goto(base + path, wait_until="load"); t.wait_for_timeout(400)
            stops = []
            for _ in range(45):
                t.keyboard.press("Tab")
                st_ = t.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null;
                  const cs = getComputedStyle(e), r = e.getBoundingClientRect();
                  let hidden = false; for (let x = e; x; x = x.parentElement) { const s = getComputedStyle(x); if (s.visibility === 'hidden' || s.display === 'none' || x.hidden) hidden = true; }
                  return {id: e.id || e.tagName + ':' + (e.textContent || '').trim().slice(0, 20), hidden, onscreen: r.width > 0 && r.right > 0 && r.left < innerWidth,
                          ring: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none'}; }""")
                if st_: stops.append(st_)
            hid = [x for x in stops if x["hidden"] or not x["onscreen"]]
            noring = [x for x in stops if not x["ring"]]
            check(f"keyboard [/{path}]: {len(stops)} Tab stops — none hidden/off-screen, all show a focus indicator",
                  len(stops) >= 10 and not hid and not noring, f"hidden={hid[:3]} no-ring={noring[:3]}")
            t.close()
        check("no uncaught JS errors during home-page interaction tests", not perr, str(perr[:2]))
        ctx.close()

        # ===================== consent / cookie settings =====================
        for path in ["", "privacy.html", "cookies.html", "products/multiline-flex.html"]:
            c = b.new_context(viewport={"width": 1280, "height": 800}); cp = c.new_page()
            cp.goto(base + path, wait_until="load"); cp.wait_for_timeout(400)
            first = cp.evaluate(VISIBLE_JS, "#consent")
            cp.click("#consentNecessary"); cp.wait_for_timeout(200)
            hidden_after = not cp.evaluate(VISIBLE_JS, "#consent")
            cp.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})"); cp.wait_for_timeout(200)
            cp.click("#cookieSettings"); cp.wait_for_timeout(400)
            reopened = cp.evaluate(VISIBLE_JS, "#consent") and cp.evaluate("() => document.activeElement.id") == "consentAccept"
            check(f"[/{path}] consent banner on first visit; 'Necessary only' hides it; footer Cookie settings reopens it",
                  first and hidden_after and reopened, f"first={first} hidden_after={hidden_after} reopened={reopened}")
            c.close()
        c = b.new_context(viewport={"width": 1280, "height": 800}); cp = c.new_page()
        cp.goto(base + "products/multiline-core.html", wait_until="load"); cp.wait_for_timeout(300)
        cp.click("#consentAccept"); cp.goto(base, wait_until="load"); cp.wait_for_timeout(300)
        check("a choice made on a product page applies on the home page (site-wide)", not cp.evaluate(VISIBLE_JS, "#consent"))
        c.close()

        c = b.new_context(viewport={"width": 1280, "height": 800}); cp = c.new_page(); yt = []
        cp.on("request", lambda r: yt.append(r.url) if re.search(r"^https?://[^/]*(youtube|google|gstatic|doubleclick)", r.url) else None)
        cp.goto(base, wait_until="load"); cp.wait_for_timeout(300); cp.click("#consentNecessary")
        cp.evaluate("document.getElementById('video').scrollIntoView({behavior: 'instant'})"); cp.wait_for_timeout(400)
        no_req = not yt
        cp.click(".video-poster"); cp.wait_for_timeout(300)
        prompt = cp.evaluate("() => !!document.querySelector('.video-consent') && !document.querySelector('iframe')")
        cp.click(".video-consent button"); cp.wait_for_timeout(400)
        src = cp.evaluate("() => document.querySelector('iframe')?.src || ''")
        check("video: no Google/YouTube request before consent; prompt shown; 'Allow & play' embeds youtube-nocookie",
              no_req and prompt and "youtube-nocookie.com/embed/" in src, f"early requests={yt[:2]} prompt={prompt} src={src}")
        c.close()

        # ===================== contact form =====================
        c = b.new_context(viewport={"width": 1280, "height": 800}); f = c.new_page(); sent = []
        f.on("request", lambda r: sent.append(f"{r.method} {r.url}") if r.method != "GET" else None)
        f.goto(base, wait_until="load"); f.wait_for_timeout(300); f.click("#consentNecessary")
        f.evaluate("document.getElementById('contact').scrollIntoView({behavior: 'instant'})"); f.wait_for_timeout(500)
        info = f.evaluate("() => { const x = document.querySelector('form.form'); return {action: x.getAttribute('action'), status: x.dataset.formStatus, notice: x.querySelector('.form__notice')?.innerText || ''}; }")
        check("contact form is visibly marked NOT CONNECTED (no action attribute)",
              not info["action"] and info["status"] == "not-connected" and "NOT CONNECTED" in info["notice"], str(info))
        f.click("form.form button[type=submit]"); f.wait_for_timeout(300)
        e1 = f.evaluate("() => ({valid: document.querySelector('form.form').checkValidity(), status: !document.getElementById('formStatus').hidden})")
        f.fill("#name", "QA Test"); f.fill("#email", "not-an-email"); f.click("form.form button[type=submit]"); f.wait_for_timeout(300)
        e2 = f.evaluate("() => !document.getElementById('formStatus').hidden")
        check("empty form / invalid email are blocked by validation (no status, nothing sent)", e1 == {"valid": False, "status": False} and not e2, f"{e1} {e2}")
        f.fill("#email", "qa@example.com"); f.fill("#msg", "DN150, 40 m"); f.click("form.form button[type=submit]"); f.wait_for_timeout(500)
        st = f.evaluate("() => ({shown: !document.getElementById('formStatus').hidden, text: document.getElementById('formStatus').innerText, focused: document.activeElement.id, thanks: document.body.innerText.includes('Thanks')})")
        check("valid submission says 'NOT sent', claims no success, sends no request",
              st["shown"] and "NOT sent" in st["text"] and st["focused"] == "formStatus" and not st["thanks"] and not sent, f"{st} requests={sent}")
        c.close()

        # ===================== mobile drawer =====================
        for path in ["", "products/multiline-flex.html"]:
            m = b.new_context(viewport={"width": 375, "height": 740}, is_mobile=True, has_touch=True, device_scale_factor=2)
            mp = m.new_page(); merr = []
            mp.on("pageerror", lambda e: merr.append(str(e)))
            mp.goto(base + path, wait_until="load"); mp.wait_for_timeout(400); mp.tap("#consentNecessary")
            tag = f"[/{path} 375px]"
            closed = mp.evaluate("""() => { const d = document.getElementById('drawer'), a = d.querySelector('a'); a.focus();
                return {vis: getComputedStyle(d).visibility, focusable: document.activeElement === a, inert: 'inert' in d ? d.inert : 'n/a'}; }""")
            check(f"{tag} closed drawer is hidden from focus (visibility:hidden, inert)", closed["vis"] == "hidden" and not closed["focusable"], str(closed))
            mp.tap("#burger"); mp.wait_for_timeout(500)
            op = mp.evaluate("() => { const r = document.getElementById('drawer').getBoundingClientRect(); return {open: document.body.classList.contains('drawer-open'), l: Math.round(r.left), r: Math.round(r.right), vw: innerWidth, focus: document.activeElement.id, vis: getComputedStyle(document.getElementById('drawer')).visibility}; }")
            check(f"{tag} burger opens drawer inside viewport, focus moves to Close", op["open"] and op["l"] >= 0 and op["r"] <= op["vw"] + 1 and op["focus"] == "drawerClose" and op["vis"] == "visible", str(op))
            coll = mp.evaluate("() => { const a = document.querySelector('.dgroup__items a'); a.focus(); return document.activeElement === a; }")
            check(f"{tag} links in collapsed accordion groups are not focusable", not coll)
            mp.tap(".dgroup__btn >> nth=0"); mp.wait_for_timeout(450)
            h = mp.evaluate("() => document.querySelectorAll('.dgroup__items')[0].getBoundingClientRect().height")
            mp.tap(".dgroup__btn >> nth=1"); mp.wait_for_timeout(450)
            h0 = mp.evaluate("() => document.querySelectorAll('.dgroup__items')[0].getBoundingClientRect().height")
            check(f"{tag} accordion expands; opening another collapses the first", h > 100 and h0 < 2, f"{h} {h0}")
            trap = mp.evaluate("""() => { const d = document.getElementById('drawer');
                const items = [...d.querySelectorAll('a[href], button')].filter(e => e.getClientRects().length && getComputedStyle(e).visibility === 'visible');
                items[items.length - 1].focus(); return items.length; }""")
            mp.keyboard.press("Tab"); mp.wait_for_timeout(80)
            wrap_fwd = mp.evaluate("() => document.activeElement.id")
            mp.keyboard.press("Shift+Tab"); mp.wait_for_timeout(80)
            wrap_back = mp.evaluate("() => document.activeElement.classList.contains('drawer__cta')")
            check(f"{tag} Tab focus is trapped inside the open drawer", trap > 3 and wrap_fwd in ("drawerClose", "") and wrap_back, f"items={trap} fwd={wrap_fwd} back={wrap_back}")

            mp.keyboard.press("Escape"); mp.wait_for_timeout(500)
            esc = mp.evaluate("() => [document.body.classList.contains('drawer-open'), getComputedStyle(document.getElementById('drawer')).visibility, document.activeElement.id]")
            check(f"{tag} Escape closes drawer, hides it again, returns focus to burger", esc == [False, "hidden", "burger"], str(esc))
            mp.tap("#burger"); mp.wait_for_timeout(400); mp.tap("#drawerScrim", position={"x": 15, "y": 300}); mp.wait_for_timeout(400)
            check(f"{tag} tapping the scrim closes the drawer", not mp.evaluate("() => document.body.classList.contains('drawer-open')"))
            mp.tap("#burger"); mp.wait_for_timeout(400); mp.tap(".dgroup__btn >> nth=2"); mp.wait_for_timeout(400)
            with mp.expect_navigation():
                mp.tap("#drawer a:has-text('Calibration hoses')")
            check(f"{tag} drawer product link navigates", "calibration-hoses" in mp.url, mp.url)
            check(f"{tag} no JS errors", not merr, str(merr[:2]))
            m.close()

        # scroll lock: real wheel input in a narrow (drawer-mode) viewport; closed-drawer baseline must scroll
        for path in ["", "products/multiline-flex.html"]:
            w = b.new_context(viewport={"width": 400, "height": 760}); wp = w.new_page()
            wp.goto(base + path, wait_until="load"); wp.wait_for_timeout(400); wp.click("#consentNecessary")
            wp.mouse.move(30, 400); y0 = wp.evaluate("scrollY"); wp.mouse.wheel(0, 500); wp.wait_for_timeout(700)
            base_moved = wp.evaluate("scrollY") - y0
            wp.click("#burger"); wp.wait_for_timeout(500); wp.mouse.move(20, 400)
            y1 = wp.evaluate("scrollY"); wp.mouse.wheel(0, 500); wp.wait_for_timeout(700)
            locked_moved = wp.evaluate("scrollY") - y1
            check(f"[/{path} 400px] page behind the open drawer does not scroll (wheel)", base_moved > 0 and locked_moved == 0,
                  f"closed-drawer baseline moved {base_moved}px, open-drawer moved {locked_moved}px")
            w.close()

        # ===================== reduced motion / no JS =====================
        rm = b.new_context(viewport={"width": 1280, "height": 800}, reduced_motion="reduce"); r = rm.new_page()
        r.goto(base, wait_until="load"); r.wait_for_timeout(400)
        st = r.evaluate("() => ({unrev: document.querySelectorAll('.reveal:not(.in)').length, canvas: getComputedStyle(document.getElementById('pipe3d')).display, docked: document.querySelector('.nav__logo .brand__mark').style.transform})")
        check("prefers-reduced-motion: everything revealed, 3D hero off, no logo flight", st["unrev"] == 0 and st["canvas"] == "none" and st["docked"] == "", str(st))
        rm.close()
        nj = b.new_context(viewport={"width": 1280, "height": 800}, java_script_enabled=False)
        for path in ["", "products/multiline-flex.html", "privacy.html"]:
            q = nj.new_page(); q.goto(base + path, wait_until="load")
            try:
                loader = q.locator("#loader").is_visible() if q.locator("#loader").count() else False
                h1 = q.locator("h1").first.is_visible()
                check(f"[/{path}] without JavaScript: no loader overlay, content visible", not loader and h1, f"loader={loader} h1={h1}")
            except Exception as ex:  # pragma: no cover
                check(f"[/{path}] without JavaScript", False, str(ex)[:120])
            q.close()
        nj.close()
        b.close()

    fails = [x for x in RESULTS if not x[0]]
    print(f"\n{len(RESULTS) - len(fails)} pass, {len(fails)} fail")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
