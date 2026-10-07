# Deploying the Lateral Repairs frontend to Serveriai.lt

Target: `https://lateralrepairs.com/` → server folder `domains/lateralrepairs.com/public_html/`
(relative to the hosting account's home directory — **confirm this path on the server**, §10).

> **Status: NOT READY.**
> 1. The contact form is **not connected**. This repository contains no backend for it (§16).
> 2. `privacy.html` contains **4 `[TO CONFIRM …]` facts** that only you can supply (§3).
> 3. Nothing about the existing server, `.htaccess`, `DirectoryIndex` or PHP application has been
>    seen. Every such item is **UNKNOWN** until §10 is done (full list in §17).
>
> The frontend itself passes the full QA suite (`sh tools/qa/run-all.sh`). Its only red
> items are 1 and 2 above.

This package only **adds or overwrites** the 87 files listed in `MANIFEST.sha256`. It does not
delete, replace or modify any PHP file, database, upload, `.htaccess` or server setting.

---

## 1. What is in the repository

| Category | Files | Production? |
| --- | --- | --- |
| HTML pages | `index.html`, `privacy.html`, `cookies.html` | **yes** |
| Generated product pages | `products/*.html` (17), built by `tools/build-products.py` — never hand-edit | **yes** |
| CSS | `assets/css/styles.css`, `assets/fonts/fonts.css` | **yes** |
| JavaScript | `assets/js/main.js`, `assets/vendor/three.min.js` (self-hosted Three.js) | **yes** |
| Fonts | `assets/fonts/*.woff2` (12, self-hosted Inter + Space Grotesk) | **yes** |
| PDFs | `assets/datasheets/*.pdf` (18), `assets/certs/iso-certificate.pdf` | **yes** |
| Images | `images/` root (8 used + `logo.png` unused), `images/products/` (9), `images/gallery/` (8), `images/certs/` (5) | **yes, except `logo.png`** |
| SEO | `robots.txt`, `sitemap.xml` (generated) | **yes** |
| Generators / tooling | `tools/build-products.py`, `tools/build-deploy.py`, `tools/qa/*` | no |
| Docs | `README.md`, `assets/certs/README.md`, `deployment/DEPLOY.md` | no |
| Vercel preview only | `vercel.json`, `.vercelignore` | no |
| Git | `.git/`, `.gitignore` | no |
| Server helpers (run in your home dir, never in `public_html`) | `deployment/inspect-server-readonly.sh`, `deployment/MANIFEST.sha256`, `deployment/htaccess-additions.conf` | no |

Not present in the repository (verified): `.github/`, `node_modules/`, `package.json`, `composer.json`,
`.env`, any `*.php` file, any `.htaccess`, any `api/` or serverless `functions/` folder.

## 2. Hosting assumptions — verified in the code

| Question | Answer |
| --- | --- |
| Clean (extensionless) URLs | **Not used.** Every internal link, canonical and sitemap URL is a real `.html` path. |
| Rewrites required | **None.** |
| Vercel / serverless functions, API routes | **None.** |
| `fetch` / XHR / `sendBeacon` / WebSocket from the site's code | **None.** (`three.min.js` contains unused loader code; the CSP restricts `connect-src` to `'self'` anyway.) |
| Form submission endpoint | **None.** The form has no `action` and is marked NOT CONNECTED (§16). |
| Externally loaded scripts / styles / fonts / images | **None.** Everything is served from the site's own domain. |
| Third-party content | YouTube video (`youtube-nocookie.com`), loaded **only after** the visitor consents. |
| Outbound links (not loaded, just links) | IMS group companies, Apheon, LinkedIn/Facebook/Instagram, App Store, Google Play, YouTube, Google privacy policy, Lithuanian DPA. All `https`. Reachability is NOT VERIFIED (blocked from the QA sandbox). |
| Paths | All relative, so the site also works from a subfolder (useful for staging, §12). |

## 3. Gates — all must be true before go-live

- [ ] `sh tools/qa/run-all.sh` ends with **ALL CHECKS PASSED**.
- [ ] Contact form: connected to the verified PHP handler and tested end-to-end, **or** a business
      decision to go live with the visible "NOT CONNECTED" notice. Visitors are pointed to email
      and phone; nothing is lost silently.
- [ ] `privacy.html` markers resolved. Replace each `<span class="confirm">[TO CONFIRM …]</span>`
      with confirmed text and remove the span:
      (1) publication date; (2) legal name of the hosting company and server country; (3) server
      log retention period; (4) whether form submissions are stored anywhere besides email.
- [ ] A data processing agreement (GDPR Art. 28) with the hosting provider is confirmed.
- [ ] If the PHP form handler sets cookies (e.g. `PHPSESSID`), `cookies.html` lists them.
- [ ] §10 server inspection done and reviewed. Every "decide" item in §8 is resolved.
- [ ] Canonical host: `https://lateralrepairs.com/` answers 200 and `www` redirects to it, because
      all canonicals and the sitemap use the bare domain.

## 4. Exact upload files

Upload the **contents** of `deployment/public_html/` into `domains/lateralrepairs.com/public_html/`:
87 files, ~11.2 MB. The authoritative list with SHA-256 hashes is `deployment/MANIFEST.sha256`.

```
public_html/
├── index.html
├── privacy.html
├── cookies.html
├── robots.txt                 (overwrites any existing file — backed up in §11)
├── sitemap.xml                (overwrites any existing file — backed up in §11)
├── products/                  17 product pages (*.html)
├── assets/
│   ├── css/styles.css
│   ├── js/main.js
│   ├── vendor/three.min.js
│   ├── fonts/                 fonts.css + 12 *.woff2
│   ├── datasheets/            18 *.pdf
│   └── certs/iso-certificate.pdf
└── images/
    ├── apple-touch-icon.png, icon-192.png, icon-512.png, ims-group.png, wordmark.png,
    │   logo.svg, badge-app-store.svg, badge-google-play.svg
    ├── products/              9 *.jpg
    ├── gallery/               8 *.jpg
    └── certs/                 5 logos
```

Upload in **binary** mode (FileZilla's "auto" is fine). Filenames are case-sensitive; don't
rename them.

## 5. Files that must NOT be uploaded

| File / folder | Why |
| --- | --- |
| the repository root itself | upload only `deployment/public_html/*` (checked and hash-listed) |
| `.git/`, `.gitignore`, `.vercelignore`, `vercel.json` | version control / Vercel preview config, meaningless on Apache |
| `README.md`, `tools/` | development documentation and Python/shell tooling |
| `deployment/DEPLOY.md` | this document |
| `deployment/MANIFEST.sha256`, `deployment/inspect-server-readonly.sh` | go to your **home directory** only (§10, §11, §14, §15) |
| `deployment/htaccess-additions.conf` | **never upload as a file** — its lines are merged into the existing `.htaccess` (§9) |
| `images/logo.png`, `assets/certs/README.md` | unused / internal; already excluded from the package |

## 6. Existing files that must remain

Do **not** delete, rename or overwrite anything that is not in `MANIFEST.sha256`. In particular:

- the PHP application: all `*.php` files, the admin area (e.g. `/admin/`), AJAX endpoints
  (e.g. `ajax.php`), `modules/`, `plugins/`, `vendor/`, `includes/`, config files, and the old
  **contact-form handler**;
- `uploads/` and any folder the backend writes to; the database (not touched by this release);
- the existing **`.htaccess`** (only appended to, §9), `.user.ini` / `php.ini`, `.well-known/`
  (SSL validation), `cgi-bin/`, search-engine verification files (`google*.html`,
  `BingSiteAuth.xml`, …), `favicon.ico`, custom error pages;
- anything belonging to other domains or subdomains.

The folder names above are the usual ones for PHP sites. **Which of them actually exist is
UNKNOWN** until §10 is run.

## 7. Index precedence: `index.html` vs `index.php`

Apache picks the file that answers `/` from the **`DirectoryIndex`** list, first match wins.
That list can be set in the server config (invisible on shared hosting) and/or in `.htaccess`.

| Situation on the server (found in §10) | Effect after upload |
| --- | --- |
| No `index.php` at the root | `/` serves the new `index.html`. |
| `index.php` at the root, `DirectoryIndex` lists `index.html` first | `/` serves the new `index.html`. The old homepage stays reachable at `/index.php` (redirect it, §18 H5). |
| `index.php` at the root, `DirectoryIndex` lists `index.php` first, or the order is unknown | **`/` keeps serving the old site.** The `DirectoryIndex index.html index.php` line from §9 fixes this. |
| A rewrite rule sends **every** request to `index.php` (no `!-f` / `!-d` conditions) | **The new pages are never served.** The rule must be adjusted by whoever owns the PHP site. Don't edit it blindly. |
| Typical front controller: `RewriteCond %{REQUEST_FILENAME} !-f` + `!-d` → `index.php` | Physical files (the new pages, assets, PDFs) are served directly, and other URLs still go to PHP. But `/` may be rewritten to `index.php` before `DirectoryIndex` applies. Test with T1. |

The current order on Serveriai.lt is **UNKNOWN**. Ask support: "What is the effective
`DirectoryIndex` order for lateralrepairs.com?"

## 8. Existing PHP routes and directory collisions

The package creates or uses these top-level names: `index.html`, `privacy.html`, `cookies.html`,
`robots.txt`, `sitemap.xml`, `products/`, `assets/`, `images/`.

- **Same file path exists** (e.g. an old `images/logo.png`): the new file **overwrites** it.
  §11 lists exactly which; check that the old PHP pages that must keep working don't use them.
- **Same folder exists** (e.g. an old `images/` or `assets/` used by the PHP site): the new files
  are added next to the old ones. Harmless unless names collide (previous point).
- **Same name is a PHP route** (e.g. the old site serves `/products/...` through `index.php`):
  with a `!-d` rewrite condition, the new physical `products/` folder **takes over** that URL
  space. Old `/products/...` URLs then return 404, or the bare folder `/products/` returns 403
  or a directory listing. **Decide:** add redirects from the old product URLs (§18 H5), and confirm
  directory listing is off (`Options -Indexes`) or accept a 403 on `/products/`.
- **`/admin/`, AJAX endpoints, `modules/`, `plugins/`, `vendor/`, `uploads/`:** the package
  contains **none** of these names, so no file lands in them. The §9 additions don't change their
  behaviour: headers and caching are path-scoped to the new files, and `DirectoryIndex` keeps
  `index.php` as the fallback. **Re-check after go-live with T10.** One edge case: a backend folder
  holding **both** `index.html` and `index.php` would switch to `index.html`; §10 lists them.

## 9. `.htaccess` changes

**The repository contains no `.htaccess`.** Nothing here can replace the production file, and
nothing should. `deployment/htaccess-additions.conf` holds the lines to **append** to the
existing `public_html/.htaccess`:

| Addition | Purpose | Scope |
| --- | --- | --- |
| `DirectoryIndex index.html index.php` | `/` serves the new homepage (§7) | whole site; `index.php` stays the fallback |
| `AddType font/woff2 .woff2` | correct font MIME type on older Apache | `.woff2` files |
| `mod_deflate` compression | ~660 KB → ~170–200 KB for `three.min.js` | text/CSS/JS/SVG/XML responses |
| Security headers (CSP, nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy) | parity with `privacy.html` §4 claims | **only** the new pages (`<If>` on `/`, the 3 root pages, `products/*.html`) |
| Cache-Control | 1 year for versioned assets, 7 days for photos, 1 hour for PDFs | only `/assets/…` and `/images/(products|gallery|certs)/` |
| HSTS | (commented out) | enable only once HTTPS works on both hosts |
| HTTPS + www→bare redirect | (commented out) | enable only if the existing file has no redirect, to avoid loops |

Procedure:

1. Keep a copy of the original file (§11).
2. Append the block at the end; never delete existing lines.
3. If the existing file already has a `DirectoryIndex` line, **don't add a second one**. Edit the
   existing line only after confirming the backend doesn't depend on its order.
4. Load the site immediately. On HTTP 500, restore the copy (likely a disallowed module or
   `<If>` unsupported) and send me the error-log line.

`privacy.html` §4 is only accurate once these headers are live (T4). If they can't be enabled,
edit that paragraph.

## 10. Pre-upload server inspection (read-only)

Before uploading anything, collect the facts this document marks UNKNOWN:

```bash
# upload deployment/MANIFEST.sha256 and deployment/inspect-server-readonly.sh to your HOME dir, then:
sh ~/inspect-server-readonly.sh          # DOCROOT=/other/path sh ... if the docroot differs
less ~/lr-server-report.txt              # review; remove anything sensitive, then share it
```

The script only lists and reads files. The single file it writes is `~/lr-server-report.txt`.
It reports: root listing; `index.*` files; every `.htaccess` (full root file plus all
`DirectoryIndex`/`Rewrite*`/`Options`/`Header` lines); `.user.ini`; which package paths already
exist (collisions); backend folders (`admin`, `ajax.php`, `modules`, `plugins`, `vendor`,
`uploads`, …); `<form>` tags; mail code (`mail()`, PHPMailer, SMTP); CAPTCHA/CSRF/honeypot; sessions
and cookies; database inserts; AJAX endpoints. Credential-looking values are redacted on a
best-effort basis, so **read the report before sharing it.**

Without SSH: send the root `.htaccess` (download only), a listing of `public_html`, the contact
page's `<form>…</form>` from the browser's View Source, and the PHP file named in its `action`
(redacted).

## 11. Backup procedure

```bash
cd ~/domains/lateralrepairs.com
tar czf ~/backup-public_html-$(date +%Y%m%d-%H%M).tar.gz public_html        # full file backup
cp public_html/.htaccess ~/htaccess-backup-$(date +%Y%m%d-%H%M) 2>/dev/null  # .htaccess copy
cd public_html                                                               # collision list
while read -r hash path; do [ -e "$path" ] && echo "$path"; done < ~/MANIFEST.sha256 > ~/lr-collisions.txt
wc -l ~/lr-collisions.txt
```

- **Database:** export it from the control panel or phpMyAdmin, even though this release doesn't
  touch it.
- **Without SSH:** use the control panel's backup for the domain, or download all of
  `public_html` with FTP. Build the collision list by comparing `MANIFEST.sha256` with the server
  listing.
- **Baseline:** write down which old URLs work today (homepage, contact handler, admin login,
  other PHP pages) for T10.
- Keep the backups until the new site has run without problems for several weeks.

## 12. Recommended: staging in a hidden subfolder

All paths are relative, so you can upload the package to `public_html/_lr-preview-<random>/`.
Then open it on desktop and phone, or run
`python3 tools/qa/browser_check.py https://lateralrepairs.com/_lr-preview-<random>/`.
This exercises the real server (MIME types, existing rewrites) but **not** the §9 headers, which
are scoped to root paths. Delete the subfolder afterwards.

## 13. Go-live steps

1. Low-traffic window. §3 gates done, §10 reviewed, §11 backups taken, §12 ideally done.
2. Upload `deployment/public_html/*` → `public_html/` (§4).
3. Append the `.htaccess` additions (§9). Load the homepage straight away.
4. Run every post-deployment test (§15).
5. Any failure you can't fix in minutes → rollback (§14).
6. Google Search Console: submit `https://lateralrepairs.com/sitemap.xml`.

## 14. Rollback procedure

**Fast (seconds):** put back the saved `.htaccess`. If the old homepage is `index.php` and the
server's own order prefers it, `/` serves the old site again.

**Full** (SSH; replace `XXXX` with the backup timestamps):

```bash
cd ~/domains/lateralrepairs.com/public_html
cp ~/htaccess-backup-XXXX .htaccess
# delete only files the new site ADDED (files that existed before are left alone)
while read -r hash path; do grep -qxF "$path" ~/lr-collisions.txt || rm -f -- "$path"; done < ~/MANIFEST.sha256
# restore the old versions of files the new site OVERWROTE
[ -s ~/lr-collisions.txt ] && tar xzf ~/backup-public_html-XXXX.tar.gz -C ~/domains/lateralrepairs.com \
    $(sed 's|^|public_html/|' ~/lr-collisions.txt)
# remove folders the new site created, only if they are now empty
for d in products assets/css assets/js assets/vendor assets/fonts assets/datasheets assets/certs \
         images/products images/gallery images/certs assets images; do rmdir "$d" 2>/dev/null; done
```

**Last resort:** restore all of `public_html` from the archive. This also reverts files the PHP
backend wrote since the backup (e.g. uploads), so check that first. **Without SSH:** re-upload the
`.htaccess` and the overwritten files from your FTP backup, then delete the added files.

## 15. Post-deployment tests

From any computer with `bash` and `curl` (macOS: `shasum -a 256` instead of `sha256sum`).

| # | Test | Command | Expected |
| --- | --- | --- | --- |
| T1 | New homepage at `/` | `curl -s https://lateralrepairs.com/ \| grep -o '<title>[^<]*'` | `<title>Lateral Repairs — CIPP Liners …` |
| T2 | Every sitemap URL | block A | 18 lines, all `200` |
| T2b | Legal pages | `curl -s -o /dev/null -w '%{http_code}\n' https://lateralrepairs.com/privacy.html` (same for `cookies.html`) | `200` |
| T3 | Upload complete and intact | block B (run inside the repo's `deployment/` folder) | no `MISMATCH` lines |
| T4 | Security headers | block C | CSP, nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy on each page |
| T5 | Caching | `curl -sI 'https://lateralrepairs.com/assets/js/main.js?v=16' \| grep -i cache-control` | `max-age=31536000, immutable`; a datasheet PDF shows `max-age=3600` |
| T6 | Compression | `curl -s -H 'Accept-Encoding: gzip' -o /dev/null -w '%{size_download}\n' 'https://lateralrepairs.com/assets/vendor/three.min.js?v=8'` | far below `669884` |
| T7 | MIME types | block D | `font/woff2`, `application/pdf`, `image/svg+xml`, `…javascript`, `text/css` |
| T8 | Host and HTTPS | `curl -sI https://lateralrepairs.com/ \| head -1`; `curl -sI http://lateralrepairs.com/ \| grep -i location`; `curl -sI https://www.lateralrepairs.com/ \| grep -i location` | `200`; both redirects → `https://lateralrepairs.com/` |
| T9 | Real 404 | `curl -s -o /dev/null -w '%{http_code}\n' https://lateralrepairs.com/qa-does-not-exist.html` | `404`. A `200` means a catch-all rewrite sends unknown URLs to the old PHP site. |
| T10 | **Backend unaffected** | open every baseline URL from §11 (admin login, AJAX-driven pages, old contact handler, uploads) | identical behaviour to before. **You must check this; it can't be tested from here.** |
| T11 | Full browser suite | `python3 tools/qa/browser_check.py https://lateralrepairs.com/` | `0 fail` |
| T12 | Real devices | iPhone Safari + Android Chrome: menu drawer, product page, open a PDF, cookie banner, video consent, contact-form notice | everything works; no sideways scrolling |
| T13 | Folder URLs | `curl -s -o /dev/null -w '%{http_code}\n' https://lateralrepairs.com/products/` | `403` or a redirect is acceptable; a directory listing is not (§8) |

```bash
# A — sitemap URLs
curl -s https://lateralrepairs.com/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' |
  while read -r u; do printf '%s %s\n' "$(curl -s -o /dev/null -w '%{http_code}' "$u")" "$u"; done
# B — integrity against the manifest
while read -r hash path; do
  got=$(curl -s "https://lateralrepairs.com/$path" | sha256sum | cut -d' ' -f1)
  [ "$got" = "$hash" ] || echo "MISMATCH $path"
done < MANIFEST.sha256; echo "integrity check done"
# C — security headers
for u in / /products/multiline-flex.html /privacy.html; do echo "== $u"
  curl -sI "https://lateralrepairs.com$u" | grep -iE '^(HTTP|content-security-policy|x-content-type-options|x-frame-options|referrer-policy|permissions-policy)'
done
# D — MIME types
for f in assets/fonts/inter-latin-400-normal.woff2 assets/datasheets/LR_MULTIline_FLEX.pdf images/logo.svg assets/js/main.js assets/css/styles.css; do
  printf '%-45s ' "$f"; curl -sI "https://lateralrepairs.com/$f" | grep -i '^content-type'
done
```

## 16. Contact form

**Current state (verified in the browser):** the form in `index.html` has no `action` and carries
`data-form-status="not-connected"`. It shows a visible "NOT CONNECTED YET" notice with the email
address and phone number. The browser requires a name and a valid email. On submit it shows
"Your message was **NOT sent**". It makes **no network request** and never claims success. No
backend exists in this repository, and none has been invented.

Needed from the existing PHP site (redact passwords; the §10 report covers most of it):

1. Handler path: the URL the current form posts to; a standalone script or a page posting to itself.
2. Method and encoding; exact field names; which are required.
3. CSRF token / honeypot / CAPTCHA, and how tokens are created. A PHP-session token **can't** be
   produced by a static page, so that would need a backend change by the PHP owner.
4. Responses: redirect / HTML / JSON on success; status codes and messages on failure.
5. Delivery: `mail()` or SMTP or library; recipient(s); SPF/DKIM for lateralrepairs.com; UTF-8.
6. Storage (database table, retention) and cookies set. Both feed the privacy and cookie policies.
7. Server-side validation and rate limiting.
8. Confirmation that the handler's path is not in `MANIFEST.sha256`.

Connecting then means:

- set `action` and `method="post"`, add the required fields, and remove the notice and
  `data-form-status`;
- adjust the CSP `form-action` if the handler is on another origin;
- update the policies if needed;
- rerun QA, then send a real enquiry and confirm it arrives in the inbox (not spam) with correct
  Lithuanian characters.

## 17. Cannot be verified without access to the Serveriai.lt server

Each item is **UNKNOWN** until §10, the hosting provider, or the PHP site's owner answers it:

| # | Unknown | How to resolve |
| --- | --- | --- |
| U1 | Exact document-root path | §10 (`pwd`), control panel |
| U2 | Effective `DirectoryIndex` order (server config + `.htaccess`) | §10 + ask Serveriai.lt support |
| U3 | Whether `index.php` / `index.html` exist at the root | §10 |
| U4 | Existing rewrite rules and whether they intercept `.html` files, `/`, `/products/` | §10 (root `.htaccess` + all others) |
| U5 | Which package paths already exist (overwrite list) | §10 / §11 collision list |
| U6 | Whether `products/`, `assets/`, `images/` exist as folders or PHP routes | §10 |
| U7 | Existence and location of `/admin/`, AJAX endpoints, `modules/`, `plugins/`, `vendor/`, `uploads/` | §10 |
| U8 | Everything about the contact handler (§16, items 1–8) | §10 + handler source |
| U9 | Whether the PHP site sets cookies on public pages | §10 + browser dev tools on the old site |
| U10 | Apache version, `<If>` support, mod_headers / mod_deflate allowed in `.htaccess` | §9 step 4 (HTTP 500 test) + support |
| U11 | Existing HTTPS/www redirect rules and certificate coverage for `www.` | §10 + T8 |
| U12 | Old public URLs that need 301 redirects | §10 + Search Console / old sitemap |
| U13 | Hosting company legal name, server location, log retention, DPA | Serveriai.lt (needed for `privacy.html`) |
| U14 | Whether outbound links (partners, app stores, socials) are still live | click-check once online |

## 18. Remaining known issues

| ID | Priority | Issue | Blocks? |
| --- | --- | --- | --- |
| C1 | CRITICAL | Contact form not connected (§16) | yes, unless the business accepts the visible notice |
| C2 | CRITICAL | Server state unknown: index precedence, rewrites, collisions (§7, §8, U1–U7) | yes, until §10 is reviewed |
| P1 | HIGH | 4 `[TO CONFIRM]` facts in `privacy.html` (§3) | yes (legal accuracy) |
| H3 | HIGH | Security headers / compression only after the `.htaccess` merge, untested on this host (U10) | no, but `privacy.html` §4 depends on it |
| H5 | HIGH | No 301 map from old PHP URLs (U12); old pages may stay reachable or 404 | no |
| M1 | MEDIUM | 3 links to `https://www.lateralrepairs.com/` (index.html: "More on lateralrepairs.com" under the video, footer globe icon, footer "lateralrepairs.com") open this same site in a new tab after go-live. **Decide:** remove them or point them elsewhere. | no |
| M5 | MEDIUM | Heavy assets: `three.min.js` 660 KB (older non-module build, logs a deprecation warning), `gallery/patch-kit.jpg` 399 KB, `liner-macro.jpg` 267 KB | no |
| L* | LOW | `/products/` folder has no index page (§8); footer heading skip h2→h5; no skip link; no custom 404 page; `backdrop-filter` without `-webkit-` on 3 rules (older Safari: no blur); `100svh` without fallback; brand pink 4.49:1 contrast on black; content items (2006 year, calibration-hose LD/MD filename, 4 resins without datasheets) | no |
