# Release runbook: new frontend on www.lateralrepairs.com (Serveriai.lt, CMS Made Simple)

The new static frontend is added **next to** the existing CMS Made Simple site. The CMS, admin,
shop scripts, database, modules, uploads and the existing `.htaccess` rules all stay as they
are. One small block is **added** to `.htaccess` (nothing existing is changed or removed). From
the moment `index.html` is uploaded, `https://www.lateralrepairs.com/` shows the new homepage.

| | Status |
| --- | --- |
| Frontend package | Passes full QA, **except 3 `[TO CONFIRM]` facts in `privacy.html`** (§2) |
| Contact form | **NOT CONNECTED**: visibly marked; visitors are sent to email/phone (§12) |
| Server configuration | **Production `.htaccess` analysed and tested** on Apache 2.4.58 (§1, §7). The live server itself is NOT VERIFIED until the §9 tests run. |

Canonical URL: **`https://www.lateralrepairs.com/`** (the production `.htaccess` redirects every
bare-domain request to `www`). Server folder: `domains/lateralrepairs.com/public_html/`.

---

## 1. What the production `.htaccess` does (analysed)

| Lines | Rule | Effect on the new frontend |
| --- | --- | --- |
| 7–391 | `FilesMatch .php` → deny all, then `<If>` allow-list (`/index.php`, `/ajax.php`, `/get_order_file.php`, `/admin/*.php`, …) | none: the package has **no PHP** |
| 400, 419–421 | HSTS (`includeSubDomains; preload`), `X-Frame-Options`, `nosniff`, `X-XSS-Protection` | already cover the new pages; nothing to add |
| 402 | `Cache-Control: private, max-age=35316000, must-revalidate` on **every** response | would cache the new HTML for ~409 days → overridden for the new HTML/PDFs only (BLOCK 2) |
| 406 | Content-Security-Policy | **commented out**, so no CSP is active; `privacy.html` no longer claims one |
| 410, 432–436 | gzip for HTML/CSS/JS/XML/SVG | already compresses the new files (three.min.js 669,884 → ~167,000 bytes) |
| 398 | `AddType application/x-font-woff2 .woff2` | new fonts load fine (browser-tested) |
| 449–450 | bare domain → `https://www.` (301) | hence **www is canonical** |
| 452–456 | `/?page=x` → `/x` (301) | unchanged |
| 457–458 | HTTP → HTTPS (301) | unchanged |
| 459–460 | any request containing `/index.php` → `/` (301) | the old homepage URL `/index.php` now leads to the new homepage |
| 463–464 | non-file path without trailing slash → add `/` (301) | the new files are real files, so not affected |
| 468–470 | not a file/dir → `index.php?page=$1` (CMS routing) | the new files are served directly; all CMS URLs unchanged |
| 439, 441 | `ErrorDocument 403 /error_403.php`, `ErrorDocument 301 /error_301.php` | unchanged (see §13 for an existing side effect) |

**Root URL today:** no rewrite rule matches `/`, so the server-level `DirectoryIndex` (not in
`.htaccess`, so unknown) decides. Because CMS module actions arrive as `/?mact=…` (rule
459–460 turns `/index.php?mact=…` into `/?mact=…`), the root must stay with `index.php` for
everything except a plain page view. Uploading an `index.html` **without** the `.htaccess`
block would let an HTML-first `DirectoryIndex` send those requests to the static page.

## 2. Before release (5 minutes, in the repo)

Replace the 3 highlighted placeholders in `privacy.html` with plain text:

1. **Publication date**.
2. **Legal name of the hosting company behind Serveriai.lt, and the country of its servers.**
3. **Server log retention period** (from Serveriai.lt).

```bash
python3 tools/build-products.py && python3 tools/build-deploy.py && python3 tools/qa/static_check.py
```
This must end with **0 blocker(s)**. The contact form shows as `KNOWN`.

## 3. Exact files to upload

The **contents** of `deployment/public_html/`: 86 files, 11.2 MB, SHA-256 list in
`deployment/MANIFEST.sha256`. Only these names appear in the document root:

```
public_html/
├── index.html        ← upload LAST (§8): it switches the homepage on
├── privacy.html
├── cookies.html
├── sitemap-lr.xml    (own name: the CMS's SiteMapMadeSimple may own /sitemap.xml)
├── products/         17 product pages
└── lr-assets/        all CSS, JS, fonts, images, datasheet PDFs, ISO certificate
```

`robots.txt` is **not** in the upload (§6 C).

## 4. Files that must NOT be uploaded

Everything outside `deployment/public_html/`, in particular:

- `.git/`, `.gitignore`, `.vercelignore`, `vercel.json`;
- `README.md`, `tools/`;
- `deployment/DEPLOY.md`, `deployment/MANIFEST.sha256`, `deployment/htaccess-additions.conf`,
  `deployment/inspect-server-readonly.sh`;
- `deployment/robots.txt` (only per §6 C).

The package builder refuses to include any PHP file, `.htaccess`, `config.php`, SQL dump, or
anything under `admin/`, `modules/`, `plugins/`, `vendor/`, `uploads/`, `lib/`, `tmp/`,
`doc/`, `install/` or `assets/`.

## 5. Existing files that must remain (untouched)

Everything already in `public_html/`. In particular: `index.php`, `config.php`, `fileloc.php`,
`include.php`, `redir.php`, `ajax.php`, `get_order_file.php`, `download_invoice.php`,
`reload_cart.php`, `prod_img.php`, `Image.php`, `akc_fixer.php`, `vcard.php`, `StripeFixer.php`,
`secure.php`, `error_403.php`, `error_301.php`, and the folders `admin/`, `modules/`,
`plugins/`, `lib/`, `tmp/`, `uploads/`, `import/`, `assets/` (CMS). The PHP names come from the
`.htaccess` allow-list and `index.php`. Whether each one exists is NOT VERIFIED; whatever
exists simply stays. The `.htaccess` is only **added to** (§7).

## 6. Pre-upload checks (read-only, ~10 minutes)

| # | Check | If… |
| --- | --- | --- |
| A | In `public_html/`, do `index.html`, `privacy.html`, `cookies.html`, `sitemap-lr.xml`, `products/` or `lr-assets/` already exist? (FTP listing) | any exists → **STOP and tell me** |
| B | `curl -s -o /dev/null -w '%{http_code}\n' https://www.lateralrepairs.com/products/` | `200` = a CMS page lives at `/products/`; after the upload that exact URL becomes `403` (child pages `/products/…/` keep working). Tell me if `/products/` must keep working. |
| C | Does `public_html/robots.txt` exist? | **yes** → don't replace it; add one line at its end: `Sitemap: https://www.lateralrepairs.com/sitemap-lr.xml`. **no** → upload `deployment/robots.txt` as `robots.txt`. |
| D | Download the **current** live `.htaccess` (tomorrow, not an old copy) and run `python3 tools/merge_htaccess.py production.htaccess merged.htaccess` | the tool refuses (anchor missing or changed) → **STOP and send me the file** |
| E | `curl -sI https://www.lateralrepairs.com/ \| grep -i cache-control` | shows `max-age=35316000` → returning visitors may still see the **old** homepage from their own browser cache until they reload. This can't be undone server-side; for information only. |
| F | Business check: the `.htaccess` allow-list (cart, orders, invoices, Stripe, stock import) shows the CMS runs a shop. Those pages keep working at their URLs, but the **new homepage does not link to them**. | confirm this is acceptable for the release |

## 7. `.htaccess` change: add 2 blocks, change nothing else

**Preferred:** let the tool do it (local files only, byte-exact; the CR/CRLF mix in the current
file is preserved):

```bash
python3 tools/merge_htaccess.py production.htaccess merged.htaccess
```
It inserts BLOCK 1 after the anchor line, appends BLOCK 2, prints the diff and verifies that the
original bytes are untouched. Upload `merged.htaccess` as `public_html/.htaccess`.

**Manual alternative:** `deployment/htaccess-additions.conf` holds the same two blocks.

BLOCK 1 goes directly **after** line 460, `RewriteRule ^(.*)index.php$ /$1 [R=301,L]`. That is
after the www / HTTPS / `index.php` redirects, so they still apply to `/`, and before the CMS
rules:

```apache
  # ---- Lateral Repairs static frontend: homepage ----
  RewriteCond %{QUERY_STRING} ^$ [OR]
  RewriteCond %{QUERY_STRING} ^((utm_[a-z]+|fbclid|gclid|gbraid|wbraid|msclkid|mc_cid|mc_eid|_ga|_gl)=[^&]*&?)+$
  RewriteCond %{REQUEST_METHOD} ^(GET|HEAD)$
  RewriteCond %{DOCUMENT_ROOT}/index.html -f
  RewriteRule ^$ index.html [L]
  RewriteRule ^$ index.php [L]
  # ---- end Lateral Repairs static frontend ----
```

BLOCK 2 goes at the **end** of the file:

```apache
<If "%{REQUEST_URI} =~ m#^/(index\.html|privacy\.html|cookies\.html|sitemap-lr\.xml|products/[a-z0-9-]+\.html)?$#">
    Header set Cache-Control "no-cache"
</If>
<If "%{REQUEST_URI} =~ m#^/lr-assets/(datasheets|certs)/#">
    Header set Cache-Control "public, max-age=3600"
</If>
```

What BLOCK 1 does:

| Request to `/` | Served by |
| --- | --- |
| plain `GET`/`HEAD`, or only tracking parameters (`?fbclid=`, `?utm_…`, `?gclid=`, …) | **new `index.html`** (while it exists) |
| `?mact=…` (CMS module actions, e.g. cart), any other query, any `POST` | CMS `index.php`, as today, **whatever the `DirectoryIndex` order** |
| `?page=x` | existing 301 → `/x`, as today |

`DirectoryIndex` is **not** changed. `/admin/`, `ajax.php`, all allow-listed PHP, all CMS pretty
URLs and all subdirectories are untouched.

**Tested** (`sudo python3 tools/qa/apache_check.py production.htaccess`). The test runs Apache 2.4.58
over HTTP and HTTPS as `lateralrepairs.com` / `www.lateralrepairs.com`, with CGI stand-ins for the
allow-listed PHP files, and compares 38 requests:

- **baseline vs merged:** your unmodified file without the frontend, against the merged file plus the
  package. All CMS/backend requests are identical under **both** `DirectoryIndex` orders: redirects,
  `?mact`, `?page`, POST, `/index.php`, pretty URLs, `/admin/` GET+POST, `ajax.php`,
  `get_order_file.php`, `download_invoice.php`, the PHP denies, CMS `assets/`, `uploads/`.
- **merged file, nothing uploaded:** all 30 requests are identical to today (the merge alone is inert).
- **full browser suite** against the merged server over HTTPS: **74 pass, 0 fail**.

## 8. Release steps (in this order)

1. §2 done (0 blockers). §6 checks passed. §10 backups taken.
2. **Merge `.htaccess`** (§7) and upload it. This is inert: nothing changes yet. Open
   `https://www.lateralrepairs.com/` and the admin login to confirm the CMS still works. On an
   HTTP 500, restore the backup copy straight away.
3. Upload `products/`, `lr-assets/`, `privacy.html`, `cookies.html`, `sitemap-lr.xml`. The CMS
   homepage is still live.
4. Run test T3 (integrity) for these files.
5. **Upload `index.html` last.** The homepage switches immediately.
6. Run the §9 tests. Do `robots.txt` per §6 C.
7. Google Search Console: submit `https://www.lateralrepairs.com/sitemap-lr.xml`.

## 9. Post-deployment tests

| # | Must pass | Test | Expected |
| --- | --- | --- | --- |
| T1 | yes | `curl -s https://www.lateralrepairs.com/ \| grep -o '<title>[^<]*'` | `<title>Lateral Repairs — CIPP Liners …` |
| T2 | yes | admin login + one CMS page (e.g. a shop page) in the browser | work exactly as before |
| T3 | yes | integrity: block A, run in the repo's `deployment/` folder | `integrity check done`, no `MISMATCH` |
| T4 | yes | block B | 18 × `OK` |
| T5 | yes | `curl -sI https://www.lateralrepairs.com/ \| grep -i cache-control` | `no-cache` |
| T6 | yes | `curl -sI https://lateralrepairs.com/ \| grep -i location` | `https://www.lateralrepairs.com/` |
| T7 | yes | `curl -s 'https://www.lateralrepairs.com/?fbclid=test' \| grep -o '<title>[^<]*'` | the new homepage title |
| T8 | yes | phone (iPhone Safari + Android Chrome): menu drawer, a product page, open a PDF, cookie banner, contact notice | all work, no sideways scrolling |
| T9 | no | `python3 tools/qa/browser_check.py https://www.lateralrepairs.com/` | 0 fail |

```bash
# A — every uploaded file present and identical (macOS: 'shasum -a 256')
while read -r hash path; do
  got=$(curl -s "https://www.lateralrepairs.com/$path" | sha256sum | cut -d' ' -f1)
  [ "$got" = "$hash" ] || echo "MISMATCH $path"
done < MANIFEST.sha256; echo "integrity check done"

# B — each sitemap URL serves the new page (canonical must equal the URL)
curl -s https://www.lateralrepairs.com/sitemap-lr.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' | while read -r u; do
  c=$(curl -s "$u" | grep -o '<link rel="canonical" href="[^"]*"' | sed 's/.*href="//; s/"$//')
  [ "$c" = "$u" ] && echo "OK    $u" || echo "WRONG $u (canonical: ${c:-none})"
done
```

A missing new file is answered by the CMS (`error404` page), so a status code alone isn't proof
of a complete upload. T3 is.

## 10. Backup (before step 2 of §8)

1. Download the live `public_html/.htaccess` and keep it unchanged as `htaccess-backup`.
2. Back up the files: download `public_html/` via FTP, or use the control panel's backup. With SSH:
   `cd ~/domains/lateralrepairs.com && tar czf ~/backup-public_html-$(date +%Y%m%d-%H%M).tar.gz public_html`
3. Export the database (control panel / phpMyAdmin). Not touched by this release, but the CMS
   and shop depend on it.

## 11. Rollback

| Situation | Action | Effect |
| --- | --- | --- |
| Homepage problem | delete or rename `public_html/index.html` | `/` is served by the CMS again **immediately** (the §7 rule only fires while `index.html` exists) |
| Any doubt about `.htaccess` / HTTP 500 | upload `htaccess-backup` as `.htaccess` | the server is exactly as before the release |
| Remove everything | additionally delete `products/`, `lr-assets/`, `privacy.html`, `cookies.html`, `sitemap-lr.xml` (and the `Sitemap:` line if you added it) | no trace left; never delete anything else |

## 12. Contact form: NOT CONNECTED

The form has no `action` and is marked `data-form-status="not-connected"`. It shows
"NOT CONNECTED YET — please email info@lateralrepairs.com or call +370 698 76581". Submitting
says "NOT sent" and makes no request. The privacy policy states that enquiries currently arrive
by email/phone only.

To connect it later I need the URL of the current CMS contact page, its `<form>…</form>` HTML
(View Source), and which CMS module renders it. CMS module actions on this site go through
`index.php` (`?mact=`). Whether they can be called from a static page is NOT VERIFIED.

## 13. Observed in the existing configuration (not changed by this release)

These are for the CMS owner. This release neither causes nor fixes them:

- `ErrorDocument 301 /error_301.php` re-enters the www/HTTPS redirect rules. In the local test
  every www/HTTPS redirect logged "exceeded 10 internal redirects". The redirects still answer
  correctly (301 + `Location`).
- `SecRuleRemoveById 0:9999999` switches off all ModSecurity (web application firewall) rules
  for the site.
- The site-wide `Cache-Control: private, max-age=35316000` (≈409 days) also applies to CMS pages
  and images (§6 E).
- HSTS is sent with `includeSubDomains; preload`, so every subdomain must support HTTPS.

## 14. Not verified (needs the live server)

- The live `.htaccess` is identical to the analysed copy (§6 D re-checks this automatically).
- The server-level `DirectoryIndex` and `DOCUMENT_ROOT`. If `DOCUMENT_ROOT` isn't the folder
  holding `index.html`, the homepage simply stays on the CMS (safe), and T1 shows it.
- Which of the §5 files and folders exist; whether `/products/` is a CMS page (§6 B); whether
  `robots.txt` exists (§6 C).
- The CMS contact module (§12); the hosting facts for `privacy.html` (§2).
