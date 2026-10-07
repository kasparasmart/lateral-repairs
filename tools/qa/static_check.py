#!/usr/bin/env python3
"""
Static QA of the deployment package (default: deployment/public_html).

  python3 tools/qa/static_check.py [package_dir]

Checks every page as plain Apache would serve it: local references (case-sensitive),
fragments, canonical/sitemap/robots/Open Graph URLs, forbidden dev/Vercel URLs,
package contents vs. source and manifest, TO CONFIRM markers, contact-form state and
basic accessibility. Exit code 1 if any BLOCKER is found.
"""
import collections
import hashlib
import os
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

REPO = pathlib.Path(__file__).resolve().parents[2]
PKG = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / "deployment" / "public_html"
SITE = "https://lateralrepairs.com"
FORBIDDEN = re.compile(r"vercel\.app|vercel\.com|localhost|127\.0\.0\.1|0\.0\.0\.0")
NOT_ALLOWED_IN_PKG = re.compile(r"(^|/)(\.htaccess|\.git.*|vercel\.json|\.vercelignore|README\.md|.*\.py|.*\.md|.*\.conf)$")

blockers, warnings, passes = [], [], []


def block(msg): blockers.append(msg)
def warn(msg): warnings.append(msg)
def ok(msg): passes.append(msg)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.imgs, self.heads, self.labels, self.ctrl, self.blank = [], [], [], [], [], []
        self.ids = collections.Counter()
        self.meta, self.links, self.forms = {}, [], []
        self._h = None
        self.lang, self.title, self._in_title, self.external = None, "", False, []

    def handle_data(self, data):
        if self._in_title: self.title += data

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self._in_title = True
        if tag == "a" and (a.get("href") or "").startswith(("http://", "https://")): self.external.append(a["href"])
        if "id" in a: self.ids[a["id"]] += 1
        for k in ("href", "src", "action", "poster"):
            if a.get(k): self.refs.append((tag, k, a[k]))
        if tag == "img": self.imgs.append((a.get("src"), a.get("alt")))
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"): self.heads.append(tag)
        if tag == "meta" and (a.get("name") or a.get("property")): self.meta[a.get("name") or a.get("property")] = a.get("content")
        if tag == "link": self.links.append((a.get("rel"), a.get("href")))
        if tag == "label" and a.get("for"): self.labels.append(a["for"])
        for k in ("aria-controls", "aria-labelledby", "aria-describedby"):
            if a.get(k): self.ctrl.append((k, a[k]))
        if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""): self.blank.append(a.get("href"))
        if tag == "form": self.forms.append(a)


def exists_case(rel):
    cur = PKG
    for comp in [c for c in rel.split("/") if c not in ("", ".")]:
        if comp == ".." or not cur.is_dir() or comp not in os.listdir(cur):
            return False
        cur = cur / comp
    return cur.is_file()


def site_url_to_file(url):
    if not url.startswith(SITE + "/"):
        return None
    path = urlsplit(url).path.lstrip("/")
    return "index.html" if path == "" else path


def main():
    if not PKG.is_dir():
        raise SystemExit(f"package not found: {PKG} (run tools/build-deploy.py)")
    files = sorted(p.relative_to(PKG).as_posix() for p in PKG.rglob("*") if p.is_file())
    pages = [f for f in files if f.endswith(".html")]
    parsed = {}
    for f in pages:
        pg = Page(); pg.feed((PKG / f).read_text(encoding="utf-8")); parsed[f] = pg

    # ---- package contents --------------------------------------------------
    bad = [f for f in files if NOT_ALLOWED_IN_PKG.search(f)]
    block(f"files that must not be uploaded are in the package: {bad}") if bad else ok("package contains no config/tooling/docs/.htaccess files")
    manifest = REPO / "deployment" / "MANIFEST.sha256"
    if manifest.exists():
        listed = dict(reversed(l.split("  ", 1)) for l in manifest.read_text().splitlines() if l.strip())
        mism = [f for f in files if listed.get(f) != hashlib.sha256((PKG / f).read_bytes()).hexdigest()]
        extra = set(listed) - set(files)
        (block(f"MANIFEST.sha256 out of sync: {mism[:5]} {sorted(extra)[:5]}") if mism or extra
         else ok(f"MANIFEST.sha256 matches all {len(files)} packaged files"))
    else:
        block("deployment/MANIFEST.sha256 missing")
    drift = [f for f in files if (REPO / f).is_file() and (REPO / f).read_bytes() != (PKG / f).read_bytes()]
    block(f"package differs from repo source (rebuild with tools/build-deploy.py): {drift[:8]}") if drift else ok("package is identical to repo source files")

    # ---- forbidden URLs ----------------------------------------------------
    hits = []
    for f in files:
        if f.endswith((".html", ".css", ".js", ".txt", ".xml")) and f != "assets/vendor/three.min.js":
            for n, line in enumerate((PKG / f).read_text(encoding="utf-8").splitlines(), 1):
                m = FORBIDDEN.search(line)
                if m: hits.append(f"{f}:{n} {m.group(0)}")
    block(f"Vercel/localhost/dev URLs found: {hits}") if hits else ok("no Vercel/localhost/dev URLs in any packaged file")

    # ---- local references --------------------------------------------------
    missing, frags, extless = [], [], []
    for f, pg in parsed.items():
        for tag, k, url in pg.refs:
            if url.startswith(("mailto:", "tel:", "data:", "#")) and not (url.startswith("#") and len(url) > 1):
                continue
            sp = urlsplit(url)
            if sp.scheme or url.startswith("//"):
                continue
            path = unquote(sp.path)
            tgt = f if path == "" else os.path.normpath(os.path.join(os.path.dirname(f), path)).replace("\\", "/")
            if tgt.startswith(".."):
                missing.append(f"{f}: {url} (escapes document root)"); continue
            if not exists_case(tgt):
                missing.append(f"{f}: {url}"); continue
            if tag == "a" and "." not in os.path.basename(tgt):
                extless.append(f"{f}: {url}")
            if sp.fragment and tgt.endswith(".html") and sp.fragment != "top" and sp.fragment not in parsed[tgt].ids:
                frags.append(f"{f}: {url}")
    block(f"missing local files (404 on Apache): {missing}") if missing else ok("every local href/src resolves to a packaged file (case-sensitive)")
    block(f"broken #fragment targets: {frags}") if frags else ok("every #fragment link has a matching id")
    block(f"extensionless internal links need rewrites: {extless}") if extless else ok("all internal links use real .html paths")

    # ---- canonical / OG / sitemap / robots ---------------------------------
    canon_bad, og_bad = [], []
    for f, pg in parsed.items():
        canon = [h for r, h in pg.links if r and "canonical" in r]
        expected = SITE + "/" + ("" if f == "index.html" else f)
        if canon != [expected]:
            canon_bad.append(f"{f}: {canon} (expected {expected})")
        for prop in ("og:url", "og:image"):
            v = pg.meta.get(prop)
            if v and (not site_url_to_file(v) or not exists_case(site_url_to_file(v))):
                og_bad.append(f"{f}: {prop}={v}")
    block(f"canonical problems: {canon_bad}") if canon_bad else ok(f"all {len(parsed)} canonicals are {SITE}/… and map to the page's own .html file")
    block(f"Open Graph URLs that don't resolve: {og_bad}") if og_bad else ok("all og:url / og:image URLs resolve to packaged files")

    sm = (PKG / "sitemap.xml").read_text(encoding="utf-8") if exists_case("sitemap.xml") else ""
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    sm_files = [site_url_to_file(u) for u in locs]
    sm_bad = [u for u, t in zip(locs, sm_files) if not t or not exists_case(t)]
    indexable = sorted(f for f, pg in parsed.items() if "noindex" not in (pg.meta.get("robots") or ""))
    missing_from_sm = sorted(set(indexable) - set(sm_files))
    if not locs: block("sitemap.xml missing or empty")
    elif sm_bad: block(f"sitemap URLs that would 404: {sm_bad}")
    else: ok(f"sitemap.xml: all {len(locs)} URLs map to packaged files")
    warn(f"indexable pages not in sitemap: {missing_from_sm}") if missing_from_sm else ok("every indexable page is listed in sitemap.xml")
    noindex_listed = [t for t in sm_files if t in parsed and "noindex" in (parsed[t].meta.get("robots") or "")]
    block(f"noindex pages listed in sitemap.xml: {noindex_listed}") if noindex_listed else ok("sitemap.xml lists no noindex pages")
    robots = (PKG / "robots.txt").read_text(encoding="utf-8") if exists_case("robots.txt") else ""
    (ok("robots.txt points to the production sitemap") if f"Sitemap: {SITE}/sitemap.xml" in robots
     else block("robots.txt does not reference the production sitemap"))

    # ---- unresolved facts ----------------------------------------------------
    markers = [f"{f}: {m}" for f in pages for m in re.findall(r"\[TO CONFIRM[^\]]*\]", (PKG / f).read_text(encoding="utf-8"))]
    block(f"{len(markers)} unresolved TO CONFIRM marker(s): {markers}") if markers else ok("no unresolved TO CONFIRM markers")

    # ---- contact form ------------------------------------------------------
    for f, pg in parsed.items():
        for form in pg.forms:
            if not form.get("action"):
                status = form.get("data-form-status")
                block(f"{f}: contact form NOT CONNECTED (no action; data-form-status={status!r}). Needs the production PHP endpoint.")
            else:
                warn(f"{f}: contact form posts to {form['action']} — NOT VERIFIED until tested against the production backend")

    # ---- accessibility / markup --------------------------------------------
    for f, pg in parsed.items():
        d = [i for i, c in pg.ids.items() if c > 1]
        if d: block(f"{f}: duplicate ids {d}")
        noalt = [s for s, a in pg.imgs if a is None]
        if noalt: block(f"{f}: images without alt {noalt}")
        dangling = [f"{k}={v}" for k, v in pg.ctrl for r in v.split() if r not in pg.ids]
        if dangling: block(f"{f}: aria references to missing ids {dangling}")
        nolabel = [l for l in pg.labels if l not in pg.ids]
        if nolabel: block(f"{f}: <label for> missing target {nolabel}")
        if pg.blank: block(f"{f}: target=_blank without rel=noopener {pg.blank}")
        if pg.heads.count("h1") != 1: block(f"{f}: {pg.heads.count('h1')} h1 elements")
        prev = 1
        for h in pg.heads:
            if int(h[1]) > prev + 1: warn(f"{f}: heading level skip h{prev}->{h}")
            prev = int(h[1])
    ok("ids unique, all images have alt, aria/label references resolve, one h1 per page") if not any(
        x for x in blockers if "duplicate ids" in x or "alt" in x or "aria" in x or "label" in x or "h1" in x) else None

    # ---- SEO basics per page ---------------------------------------------------
    seo = []
    for f, pg in parsed.items():
        if not pg.lang: seo.append(f"{f}: <html> has no lang")
        if not pg.title.strip(): seo.append(f"{f}: empty <title>")
        if not pg.meta.get("description"): seo.append(f"{f}: no meta description")
        if "width=device-width" not in (pg.meta.get("viewport") or ""): seo.append(f"{f}: no responsive viewport meta")
    block(f"SEO basics missing: {seo}") if seo else ok("every page has lang, <title>, meta description and viewport")
    for label, key in (("title", lambda pg: pg.title.strip()), ("meta description", lambda pg: pg.meta.get("description"))):
        seen = collections.defaultdict(list)
        for f, pg in parsed.items(): seen[key(pg)].append(f)
        dup = {k: v for k, v in seen.items() if len(v) > 1}
        warn(f"duplicate {label}: {dup}") if dup else ok(f"every page has a unique {label}")
    insecure = sorted({u for pg in parsed.values() for u in pg.external if u.startswith("http://")})
    block(f"external links over plain http: {insecure}") if insecure else ok(
        f"all {len({u for pg in parsed.values() for u in pg.external})} distinct external links use https "
        "(reachability NOT VERIFIED offline)")

    # ---- PDFs / images ---------------------------------------------------------
    badpdf = [f for f in files if f.endswith(".pdf") and ((PKG / f).read_bytes()[:5] != b"%PDF-" or b"%%EOF" not in (PKG / f).read_bytes()[-2048:])]
    block(f"invalid or truncated PDF files: {badpdf}") if badpdf else ok(f"all {sum(f.endswith('.pdf') for f in files)} PDFs have a valid header and end-of-file marker")
    try:
        from PIL import Image
        badimg = []
        for f in files:
            if f.endswith((".jpg", ".jpeg", ".png")):
                try:
                    with Image.open(PKG / f) as im: im.load()
                except Exception as e: badimg.append(f"{f}: {e}")
        block(f"images that fail to decode: {badimg}") if badimg else ok(f"all {sum(f.endswith(('.jpg', '.jpeg', '.png')) for f in files)} raster images decode fully")
    except ImportError:
        warn("Pillow not installed — raster images not decoded (pip install Pillow)")
    linked = {os.path.normpath(os.path.join(os.path.dirname(f), urlsplit(u).path)).replace("\\", "/")
              for f, pg in parsed.items() for t, k, u in pg.refs if u.endswith(".pdf")}
    orphan = [f for f in files if f.endswith(".pdf") and f not in linked]
    warn(f"PDFs packaged but not linked: {orphan}") if orphan else ok("every packaged PDF is linked from a page")

    print(f"Static QA of {PKG.relative_to(REPO) if PKG.is_relative_to(REPO) else PKG}: {len(files)} files, {len(pages)} pages\n")
    for p in passes: print("PASS    " + p)
    for w in warnings: print("WARN    " + w)
    for b in blockers: print("BLOCKER " + b)
    print(f"\n{len(passes)} pass, {len(warnings)} warning(s), {len(blockers)} blocker(s)")
    sys.exit(1 if blockers else 0)


if __name__ == "__main__":
    main()
