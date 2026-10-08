#!/usr/bin/env python3
"""
Before/after test of the production .htaccess merge on a local Apache (dev machine only).

  sudo python3 tools/qa/apache_check.py /path/to/production.htaccess

Needs root, apache2 (with mod_ssl) and openssl. The production .htaccess is passed in and is
never committed (this repository is public). For each scenario the script builds a throwaway
docroot with CGI stand-ins for the CMS PHP files named in the .htaccess allow-list, serves it
over HTTP+HTTPS as lateralrepairs.com / www.lateralrepairs.com, and records each response:

  baseline  original .htaccess, no new frontend files (today's production behaviour)
  merged-A  merged .htaccess + deployment/public_html, DirectoryIndex index.php index.html
  merged-B  merged .htaccess + deployment/public_html, DirectoryIndex index.html index.php

Pass criteria: every CMS/backend request answers exactly as in the baseline, the root URL
serves the new homepage only where intended, and both DirectoryIndex orders behave the same.
"""
import http.client
import pathlib
import shutil
import ssl
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
PKG = REPO / "deployment" / "public_html"
T = pathlib.Path("/srv/lr-apache-test")
M = "/usr/lib/apache2/modules"
WWW, BARE = "www.lateralrepairs.com", "lateralrepairs.com"

CGI = """#!/bin/sh
cat >/dev/null
printf '%sContent-Type: text/plain\\r\\n\\r\\n'
echo "SERVED-BY: {name}"
echo "METHOD: $REQUEST_METHOD"
echo "QUERY: $QUERY_STRING"
"""
FAKES = {  # path -> (label, extra CGI header)
    "index.php": ("CMS index.php", ""), "admin/index.php": ("CMS admin/index.php", ""),
    "admin/login.php": ("CMS admin/login.php", ""), "ajax.php": ("ajax.php", ""),
    "get_order_file.php": ("get_order_file.php", ""), "download_invoice.php": ("download_invoice.php", ""),
    "modules/TinyMCE/stylesheet.php": ("TinyMCE stylesheet.php", ""),
    "modules/Other/action.php": ("SHOULD-BE-DENIED module php", ""), "config.php": ("SHOULD-BE-DENIED config.php", ""),
    "lib/secret.php": ("SHOULD-BE-DENIED lib php", ""),
    "error_403.php": ("CMS error_403.php", "Status: 403 Forbidden\\r\\n"),
    "error_301.php": ("CMS error_301.php", ""),
}

# (label, method, host, scheme, path)  — scheme "http" goes to port 80
REQS = [
    ("bare http root",            "GET",  BARE, "http",  "/"),
    ("bare https root",           "GET",  BARE, "https", "/"),
    ("www http root",             "GET",  WWW,  "http",  "/"),
    ("bare https product page",   "GET",  BARE, "https", "/products/multiline-flex.html"),
    ("root",                      "GET",  WWW,  "https", "/"),
    ("root HEAD",                 "HEAD", WWW,  "https", "/"),
    ("root ?fbclid",              "GET",  WWW,  "https", "/?fbclid=IwAR0abc"),
    ("root ?utm_*",               "GET",  WWW,  "https", "/?utm_source=newsletter&utm_medium=email"),
    ("root ?mact (module action)", "GET", WWW,  "https", "/?mact=Cart,cntnt01,add,0&cntnt01qty=1"),
    ("root ?page=about",          "GET",  WWW,  "https", "/?page=about"),
    ("root ?q (unknown param)",   "GET",  WWW,  "https", "/?q=liner"),
    ("root POST",                 "POST", WWW,  "https", "/"),
    ("/index.php",                "GET",  WWW,  "https", "/index.php"),
    ("/index.php?mact",           "GET",  WWW,  "https", "/index.php?mact=News,m1,default,0"),
    ("CMS pretty URL",            "GET",  WWW,  "https", "/about-us/"),
    ("CMS URL without slash",     "GET",  WWW,  "https", "/about-us"),
    ("CMS nested URL",            "GET",  WWW,  "https", "/lt/kainos/"),
    ("admin/",                    "GET",  WWW,  "https", "/admin/"),
    ("admin login GET",           "GET",  WWW,  "https", "/admin/login.php"),
    ("admin login POST",          "POST", WWW,  "https", "/admin/login.php"),
    ("ajax.php GET",              "GET",  WWW,  "https", "/ajax.php?x=1"),
    ("ajax.php POST",             "POST", WWW,  "https", "/ajax.php"),
    ("get_order_file.php",        "GET",  WWW,  "https", "/get_order_file.php?id=1"),
    ("download_invoice.php",      "GET",  WWW,  "https", "/download_invoice.php"),
    ("TinyMCE stylesheet.php",    "GET",  WWW,  "https", "/modules/TinyMCE/stylesheet.php"),
    ("denied module php",         "GET",  WWW,  "https", "/modules/Other/action.php"),
    ("denied config.php",         "GET",  WWW,  "https", "/config.php"),
    ("denied lib php",            "GET",  WWW,  "https", "/lib/secret.php"),
    ("CMS assets/ file",          "GET",  WWW,  "https", "/assets/templates/demo.tpl"),
    ("uploads/ file",             "GET",  WWW,  "https", "/uploads/images/old.txt"),
    # new frontend
    ("new privacy.html",          "GET",  WWW,  "https", "/privacy.html"),
    ("new product page",          "GET",  WWW,  "https", "/products/multiline-flex.html"),
    ("new products/ folder",      "GET",  WWW,  "https", "/products/"),
    ("new main.js",               "GET",  WWW,  "https", "/lr-assets/js/main.js?v=16"),
    ("new datasheet PDF",         "GET",  WWW,  "https", "/lr-assets/datasheets/LR_MULTIline_FLEX.pdf"),
    ("new font",                  "GET",  WWW,  "https", "/lr-assets/fonts/inter-latin-400-normal.woff2"),
    ("new sitemap-lr.xml",        "GET",  WWW,  "https", "/sitemap-lr.xml"),
    ("missing lr-assets file",    "GET",  WWW,  "https", "/lr-assets/js/nope.js"),
]
NEW_FRONTEND = {"new privacy.html", "new product page", "new products/ folder", "new main.js", "new datasheet PDF",
                "new font", "new sitemap-lr.xml", "missing lr-assets file"}
HOMEPAGE = {"root", "root HEAD", "root ?fbclid", "root ?utm_*"}


def sh(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build(htaccess: pathlib.Path, with_frontend: bool, dirindex: str):
    stop()
    shutil.rmtree(T, ignore_errors=True)
    doc = T / "public_html"
    if with_frontend:
        shutil.copytree(PKG, doc)
    else:
        doc.mkdir(parents=True)
    for rel, (label, extra) in FAKES.items():
        f = doc / rel; f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(CGI.replace("{name}", label) % extra); f.chmod(0o755)
    (doc / "assets/templates").mkdir(parents=True); (doc / "assets/templates/demo.tpl").write_text("cmsms template\n")
    (doc / "uploads/images").mkdir(parents=True); (doc / "uploads/images/old.txt").write_text("old upload\n")
    shutil.copyfile(htaccess, doc / ".htaccess")
    sh("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2", "-subj", f"/CN={WWW}",
       "-addext", f"subjectAltName=DNS:{WWW},DNS:{BARE}", "-keyout", str(T / "key.pem"), "-out", str(T / "cert.pem"))
    mods = ["mpm_event", "authz_core", "authz_host", "access_compat", "mime", "dir", "rewrite", "headers", "filter",
            "deflate", "expires", "setenvif", "socache_shmcb", "ssl", "cgid"]
    conf = [f'ServerRoot "/etc/apache2"', f"PidFile {T}/httpd.pid", "User www-data", "Group www-data",
            f"ErrorLog {T}/error.log", "LogLevel warn", f"ScriptSock {T}/cgisock", "TypesConfig /etc/mime.types",
            "Listen 127.0.0.1:80", "Listen 127.0.0.1:443", f"ServerName {WWW}"]
    conf += [f"LoadModule {m}_module {M}/mod_{m}.so" for m in mods]
    common = f"""  ServerName {WWW}
  ServerAlias {BARE}
  DocumentRoot {doc}
  DirectoryIndex {dirindex}
  <Directory {doc}>
    AllowOverride All
    Options +ExecCGI
    AddHandler cgi-script .php
    Require all granted
  </Directory>"""
    conf += [f"<VirtualHost 127.0.0.1:80>\n{common}\n</VirtualHost>",
             f"<VirtualHost 127.0.0.1:443>\n{common}\n  SSLEngine on\n  SSLCertificateFile {T}/cert.pem\n"
             f"  SSLCertificateKeyFile {T}/key.pem\n</VirtualHost>"]
    (T / "httpd.conf").write_text("\n".join(conf) + "\n")
    sh("chown", "-R", "www-data:www-data", str(T))
    subprocess.run(["apache2", "-f", str(T / "httpd.conf"), "-k", "start"], check=True)
    time.sleep(1.2)


def stop():
    if (T / "httpd.pid").exists():
        subprocess.run(["apache2", "-f", str(T / "httpd.conf"), "-k", "stop"], stderr=subprocess.DEVNULL)
        time.sleep(1)


def fetch(method, host, scheme, path):
    if scheme == "https":
        ctx = ssl._create_unverified_context()
        c = http.client.HTTPSConnection("127.0.0.1", 443, context=ctx, timeout=10)
        c._tunnel_host = None
        c.sock = ctx.wrap_socket(__import__("socket").create_connection(("127.0.0.1", 443), 10), server_hostname=host)
    else:
        c = http.client.HTTPConnection("127.0.0.1", 80, timeout=10)
    body = b"x=1" if method == "POST" else None
    hdrs = {"Host": host, "Accept-Encoding": "gzip"}
    if body: hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    c.request(method, path, body=body, headers=hdrs)
    r = c.getresponse(); data = r.read(); c.close()
    h = {k.lower(): v for k, v in r.getheaders()}
    text = data.decode("utf-8", "replace") if h.get("content-encoding") != "gzip" else __import__("gzip").decompress(data).decode("utf-8", "replace")
    who = next((l[len("SERVED-BY: "):] for l in text.splitlines() if l.startswith("SERVED-BY: ")), None)
    if who is None:
        who = "NEW index.html" if "<title>Lateral Repairs — CIPP" in text else ("NEW page" if "lr-assets/" in text else (text.strip()[:30] or "(empty)"))
        if method == "HEAD" and "text/html" in h.get("content-type", "") and r.status == 200:
            who = "html (HEAD)"
    q = next((l[len("QUERY: "):] for l in text.splitlines() if l.startswith("QUERY: ")), "")
    m = next((l[len("METHOD: "):] for l in text.splitlines() if l.startswith("METHOD: ")), "")
    return {"status": r.status, "location": h.get("location", ""), "who": who, "query": q, "method": m,
            "cache": h.get("cache-control", ""), "hsts": "strict-transport-security" in h,
            "xfo": h.get("x-frame-options", ""), "ctype": h.get("content-type", "").split(";")[0],
            "gzip": h.get("content-encoding", "") == "gzip", "bytes": len(data)}


def run(name, htaccess, with_frontend, dirindex):
    build(htaccess, with_frontend, dirindex)
    res = {label: fetch(m, host, sch, path) for label, m, host, sch, path in REQS}
    errs = (T / "error.log").read_text(errors="replace")
    errs = [l for l in errs.splitlines() if "[core:error]" in l or "[rewrite:" in l or "alert" in l]
    stop()
    return res, errs


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    prod = pathlib.Path(sys.argv[1]).resolve()
    merged = T.parent / "lr-merged.htaccess"
    subprocess.run([sys.executable, "-I", str(REPO / "tools/merge_htaccess.py"), str(prod), str(merged)],
                   check=True, stdout=subprocess.DEVNULL)
    base, e0 = run("baseline", prod, False, "index.php index.html")
    a, e1 = run("merged-A", merged, True, "index.php index.html")
    b, e2 = run("merged-B", merged, True, "index.html index.php")
    c, e3 = run("merged-no-files", merged, False, "index.html index.php")   # .htaccess merged BEFORE upload
    merged.unlink()
    shutil.rmtree(T, ignore_errors=True)

    fails = 0
    def check(ok, label, detail):
        nonlocal fails
        fails += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + f"{label:30s} {detail}")

    keys = ("status", "location", "who", "query", "method", "cache")
    print("== CMS / backend requests: merged must equal today's baseline (both DirectoryIndex orders)")
    for label, *_ in REQS:
        if label in NEW_FRONTEND or label in HOMEPAGE:
            continue
        same = all(base[label][k] == a[label][k] == b[label][k] for k in keys)
        r = base[label]
        check(same, label, f"{r['status']} {r['who']}{' -> ' + r['location'] if r['location'] else ''}"
                           f"{'  q=' + r['query'] if r['query'] else ''}"
                           + ("" if same else f"   MERGED-A={ {k: a[label][k] for k in keys} } MERGED-B={ {k: b[label][k] for k in keys} }"))
    print("== merged .htaccess but frontend not uploaded yet: EVERY request must equal today's baseline")
    inert = [l for l, *_ in REQS if l not in NEW_FRONTEND and any(base[l][k] != c[l][k] for k in keys + ("ctype",))]
    check(not inert, "merge alone is inert", f"{len(REQS) - len(NEW_FRONTEND)} requests identical to baseline"
          + (f"; differs: {inert}" if inert else ""))
    print("== homepage: today CMS index.php, after merge the new index.html (both DirectoryIndex orders)")
    for label in sorted(HOMEPAGE):
        cms_before = base[label]["who"] == "CMS index.php" or (label == "root HEAD" and base[label]["ctype"] == "text/plain")
        ok = cms_before and a[label]["who"] in ("NEW index.html", "html (HEAD)") \
             and a[label]["who"] == b[label]["who"] and a[label]["status"] == 200 and a[label]["cache"] == "no-cache"
        before = base[label]["who"] if label != "root HEAD" else f"CMS ({base[label]['ctype']})"
        check(ok, label, f"before: {before} | after: {a[label]['status']} {a[label]['who']} cache={a[label]['cache']!r}")
    print("== new frontend files (after merge)")
    exp = {"new privacy.html": (200, "text/html", "no-cache"), "new product page": (200, "text/html", "no-cache"),
           "new products/ folder": (403, None, None), "new main.js": (200, None, "private, max-age=35316000, must-revalidate"),
           "new datasheet PDF": (200, "application/pdf", "public, max-age=3600"),
           "new font": (200, None, "private, max-age=35316000, must-revalidate"),
           "new sitemap-lr.xml": (200, None, "no-cache"), "missing lr-assets file": (301, None, None)}
    for label, (st, ct, cc) in exp.items():
        r, rb = a[label], b[label]
        ok = r["status"] == st and (ct is None or r["ctype"] == ct) and (cc is None or r["cache"] == cc) \
             and all(r[k] == rb[k] for k in ("status", "cache", "who", "location"))
        check(ok, label, f"{r['status']} {r['ctype']} cache={r['cache']!r}{' -> ' + r['location'] if r['location'] else ''}")
    hs = a["root"]
    check(hs["hsts"] and hs["xfo"] == "SAMEORIGIN", "existing security headers", f"HSTS={hs['hsts']} X-Frame-Options={hs['xfo']!r} on new homepage")
    check(a["new main.js"]["gzip"], "existing compression", f"main.js gzip={a['new main.js']['gzip']}")
    # The baseline already logs AH00124 loops: "ErrorDocument 301 /error_301.php" re-enters the www/https
    # redirect rules. Redirects still answer 301 + Location. The merge must not add any NEW error.
    check(max(len(e1), len(e2), len(e3)) <= len(e0), "no new apache errors",
          f"baseline {len(e0)} (pre-existing ErrorDocument 301 loop) / merged {len(e1)} / {len(e2)} / {len(e3)}")
    print(f"\n== {fails} fail")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
