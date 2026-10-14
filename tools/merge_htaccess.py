#!/usr/bin/env python3
"""
Merge the Lateral Repairs frontend rules into a LOCAL copy of the production .htaccess.

  python3 tools/merge_htaccess.py production.htaccess merged.htaccess

Reads/writes local files only, never the server. The production file is not modified; the
merged copy is written to the second path and the exact diff is printed. Existing lines are
never changed or removed: the tool only inserts one block after the CMS "index.php" redirect
and appends one block at the end. It refuses to run if the anchor is missing or ambiguous,
or if the file already contains the Lateral Repairs blocks.
"""
import difflib
import pathlib
import re
import sys

MARK = "Lateral Repairs static frontend"

# Inserted directly AFTER the CMS rule that strips /index.php, i.e. after the existing www and
# HTTPS redirects (so they still apply to "/") and BEFORE the CMS trailing-slash and page rules.
ROOT_BLOCK = f"""
  # ---- {MARK}: homepage ----
  # GET/HEAD of "/" with no query string, or only ad/analytics tracking parameters -> new index.html.
  # Only while index.html exists: merging this file changes nothing until index.html is uploaded,
  # and deleting index.html alone restores the CMS homepage.
  RewriteCond %{{QUERY_STRING}} ^$ [OR]
  RewriteCond %{{QUERY_STRING}} ^((utm_[a-z]+|fbclid|gclid|gbraid|wbraid|msclkid|mc_cid|mc_eid|_ga|_gl)=[^&]*&?)+$
  RewriteCond %{{REQUEST_METHOD}} ^(GET|HEAD)$
  RewriteCond %{{DOCUMENT_ROOT}}/index.html -f
  RewriteRule ^$ index.html [L]
  # Every other request for "/" (CMS ?mact= / ?page= parameters, POST) stays with the CMS
  # index.php, independent of the server's DirectoryIndex order.
  RewriteRule ^$ index.php [L]
  # ---- end {MARK} ----
"""

# Appended at the END. Overrides the site-wide "private, max-age=35316000" ONLY for the new
# frontend's HTML and PDFs, so later fixes reach returning visitors. CMS pages are untouched.
CACHE_BLOCK = f"""
# ---- {MARK}: caching for the new files only ----
<If "%{{REQUEST_URI}} =~ m#^/(index\\.html|privacy\\.html|cookies\\.html|sitemap-lr\\.xml|products/[a-z0-9-]+\\.html)?$#">
    Header set Cache-Control "no-cache"
</If>
<If "%{{REQUEST_URI}} =~ m#^/lr-assets/(datasheets|certs)/#">
    Header set Cache-Control "public, max-age=3600"
</If>
# ---- end {MARK} ----
"""

ANCHOR = re.compile(r"^[ \t]*RewriteRule[ \t]+\^\(\.\*\)index\.php\$[ \t]+/\$1[ \t]+\[R=301,L\][ \t]*$")
WWW_REDIRECT = re.compile(r"RewriteRule\s+\^\(\.\*\)\$\s+https://www\.%\{HTTP_HOST\}/\$1")
CMS_ROUTE = re.compile(r"RewriteRule\s+\^\(\.\+\)\$\s+index\.php\?page=\$1")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    raw = src.read_bytes()
    if MARK.encode() in raw:
        raise SystemExit("refusing: the file already contains the Lateral Repairs blocks")
    # Split on LF only and keep every original byte (the production file mixes CRLF and CR CR LF;
    # Apache tolerates both, so nothing existing may be re-encoded).
    lines = raw.split(b"\n")
    text = [l.decode("utf-8").rstrip("\r") for l in lines]

    hits = [i for i, l in enumerate(text) if ANCHOR.match(l)]
    if len(hits) != 1:
        raise SystemExit(f"refusing: expected exactly 1 anchor line 'RewriteRule ^(.*)index.php$ /$1 [R=301,L]', found {len(hits)}")
    at = hits[0]
    www = [i for i, l in enumerate(text) if WWW_REDIRECT.search(l)]
    cms = [i for i, l in enumerate(text) if CMS_ROUTE.search(l)]
    if not www or www[0] > at:
        raise SystemExit("refusing: the www redirect is not before the anchor - layout differs from the analysed file")
    if not cms or cms[-1] < at:
        raise SystemExit("refusing: the CMS page rule is not after the anchor - layout differs from the analysed file")

    eol = b"\r" if lines[at].endswith(b"\r") else b""          # new lines end CRLF like the anchor line
    block = [l.encode() + eol for l in ROOT_BLOCK.strip("\n").split("\n")]
    tail = [l.encode() + eol for l in CACHE_BLOCK.strip("\n").split("\n")]
    if lines[-1] == b"":                                          # file ends with a newline
        out = lines[: at + 1] + block + lines[at + 1 : -1] + [eol] + tail + [b""]
    else:
        out = lines[: at + 1] + block + lines[at + 1 :] + [eol] + tail
    merged = b"\n".join(out)
    dst.write_bytes(merged)

    # proof: removing exactly the added lines must give back the original bytes
    added = set(range(at + 1, at + 1 + len(block)))
    base = len(lines) - (1 if lines[-1] == b"" else 0) + len(block)
    added |= set(range(base, base + 1 + len(tail)))
    restored = b"\n".join(l for i, l in enumerate(out) if i not in added)
    if restored != raw:
        dst.unlink()
        raise SystemExit("internal check failed: merge would alter existing bytes; nothing written")

    print(f"anchor at line {at + 1}; inserted {len(block)} lines after it, appended {len(tail) + 1} lines at the end; "
          f"existing bytes unchanged (verified)")
    print(f"wrote {dst}\n")
    old_t = [l.decode("utf-8").rstrip("\r") + "\n" for l in lines]
    new_t = [l.decode("utf-8").rstrip("\r") + "\n" for l in out]
    sys.stdout.writelines(difflib.unified_diff(old_t, new_t, fromfile=f"{src.name} (production)", tofile=f"{dst.name} (merged)", n=2))


if __name__ == "__main__":
    main()
