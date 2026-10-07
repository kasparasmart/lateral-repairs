# Deploying the Lateral Repairs frontend to Serveriai.lt

Target: `https://lateralrepairs.com/` → server folder `domains/lateralrepairs.com/public_html/`
(relative to the hosting account's home directory).

> **Current status: NOT READY.** `tools/qa/static_check.py` reports two blockers:
> the contact form is **not connected** (§11) and `privacy.html` contains **4 unresolved
> `[TO CONFIRM …]` markers** (§1). The browser suite passes (73/73) against this package.
> Anything about the existing PHP backend is **NOT VERIFIED**: it is not in this repository
> and was not reachable during QA.

This package only **adds/overwrites** the files listed in `MANIFEST.sha256`. It does not
delete, replace or modify any PHP file, database, upload folder or server setting.

---

## 1. Gates — all must be true before go-live

- [ ] `sh tools/qa/run-all.sh` ends with **ALL CHECKS PASSED** (static check exits 0).
- [ ] Contact form decision made (§11): either connected to the verified PHP handler and tested
      end-to-end, **or** the business explicitly accepts going live with the visible
      "NOT CONNECTED" notice (visitors are pointed to email/phone; nothing is lost silently).
      In the second case, the static check stays red for this one known item.
- [ ] `privacy.html` markers resolved (replace each `<span class="confirm">[TO CONFIRM …]</span>`
      with confirmed text and remove the span):
  1. Publication date of the policy.
  2. Legal name of the hosting company behind Serveriai.lt and the country of the servers.
  3. Server log retention period (ask Serveriai.lt).
  4. Whether contact-form submissions are stored anywhere besides email (depends on §11).
- [ ] A data processing agreement (GDPR Art. 28) with the hosting provider exists (usually part
      of the hosting terms — confirm, do not assume).
- [ ] If the PHP form handler sets cookies (e.g. `PHPSESSID` for CSRF), `cookies.html` is updated
      to list them — it currently states that only `lr-consent-v1` (local storage) is used.
- [ ] Canonical host confirmed: `https://lateralrepairs.com/` (no `www`) must answer **200**, and
      `www` must redirect **to** it. All canonical tags and the sitemap use the bare domain.
- [ ] Old-URL redirect map prepared (§12, item H5) — needs the list of old PHP page URLs.

## 2. Exact upload files

Upload the **contents** of `deployment/public_html/` (not the folder itself) into
`domains/lateralrepairs.com/public_html/`. 87 files, ~11.2 MB. The authoritative list with
SHA-256 hashes is `deployment/MANIFEST.sha256`.

```
public_html/
├── index.html
├── privacy.html
├── cookies.html
├── robots.txt                 (replaces the existing one — back it up, §6)
├── sitemap.xml                (replaces the existing one — back it up, §6)
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

Use SFTP/FTP in **binary** mode (FileZilla's default "auto" is fine) so PDFs, fonts and
images are not corrupted. Filenames are case-sensitive on the server; upload them as-is.

## 3. Files that must NOT be uploaded

| File / folder | Why |
| --- | --- |
| the repository root (`index.html` etc. at repo level) | upload only `deployment/public_html/*`, which is checked and hash-listed |
| `.git/`, `.gitignore`, `.vercelignore`, `vercel.json` | version control / Vercel preview config, meaningless on Apache |
| `README.md`, `tools/` (Python build + QA scripts) | development only |
| `deployment/DEPLOY.md`, `deployment/MANIFEST.sha256` | documentation; the manifest may go to your **home directory** (not `public_html`) for the checks in §6/§10 |
| `deployment/htaccess-additions.conf` | **never upload as a file** — merge its contents into the existing `.htaccess` (§5) |
| `images/logo.png`, `assets/certs/README.md` (repo only) | unused / internal notes; already excluded from the package |

## 4. Files that must remain on the existing server

Do **not** delete, rename or overwrite anything that is not in `MANIFEST.sha256`. In particular:

- all `*.php` files, PHP admin folders, includes/config files (e.g. `config.php`, `.env`) and the
  **contact-form handler** of the old site;
- upload folders written by the PHP backend; the database (untouched by this release);
- the existing **`.htaccess`** (only appended to, §5), `.user.ini` / `php.ini`, `.well-known/`
  (SSL certificate validation), `cgi-bin/`, search-engine verification files
  (`google*.html`, `BingSiteAuth.xml`, …), `favicon.ico`, custom error pages;
- anything belonging to other domains or subdomains in the hosting account.

Files from the old site that share a path with the new one (found in §6.4) **will be overwritten**.
Everything else stays reachable at its old URL until redirects are added (§12, H5).

## 5. `.htaccess` changes

1. Download and keep a copy of the current `public_html/.htaccess` (§6.3).
2. Open it and **append** the contents of `deployment/htaccess-additions.conf` at the end.
   Do not delete existing lines.
3. Read the comments in that file:
   - `DirectoryIndex index.html index.php` makes `/` serve the new homepage. Folders that only
     contain `index.php` keep working. If a folder holds **both** files, the `.html` now wins —
     check with `ls` first.
   - Security headers and caching are scoped by URL path (`<If>`) to the new frontend's files,
     so existing PHP pages/admin keep their current behaviour.
   - **HSTS** stays commented until HTTPS works on both `lateralrepairs.com` and `www.`.
   - The **HTTPS/www redirect** block stays commented unless the existing file has none. Two
     competing redirect blocks can loop.
4. Save and immediately load `https://lateralrepairs.com/`. On **HTTP 500**, restore the copy from
   step 1. The most likely cause is a module the host does not allow in `.htaccess`. Tell me the
   error-log line and I'll adjust the snippet.

`privacy.html` §4 claims a Content Security Policy and HSTS. It is only accurate once these
headers are active (§10, T4). If they can't be enabled, edit that paragraph before go-live.

## 6. Backup procedure (before any upload)

With SSH access (paths relative to the hosting home directory):

```bash
# 6.1 full file backup of the current site
cd ~/domains/lateralrepairs.com
tar czf ~/backup-public_html-$(date +%Y%m%d-%H%M).tar.gz public_html
# 6.3 separate copy of .htaccess
cp public_html/.htaccess ~/htaccess-backup-$(date +%Y%m%d-%H%M) 2>/dev/null
# 6.4 which files of the new site already exist on the server (= will be overwritten)
#     first upload deployment/MANIFEST.sha256 to your HOME directory (not public_html)
cd ~/domains/lateralrepairs.com/public_html
while read -r hash path; do [ -e "$path" ] && echo "$path"; done < ~/MANIFEST.sha256 > ~/lr-collisions.txt
wc -l ~/lr-collisions.txt; cat ~/lr-collisions.txt
ls -la index.* .htaccess
```

Without SSH: use the control panel's backup function for the domain, or download all of
`public_html` with FTP (keep the copy until the new site has been stable for several weeks), and
compare the manifest paths with the server listing by hand to build `lr-collisions.txt`.

- **6.2 Database:** export it from the control panel or phpMyAdmin. This release does not touch
  the database, but the PHP backend depends on it, so keep a snapshot from the same moment.
- **6.5 Baseline:** note which old URLs work today (homepage, contact handler, admin login, any
  other PHP pages) so you can confirm afterwards that they still behave the same.

**Review `lr-collisions.txt` before uploading.** If it lists `index.html`, `robots.txt`,
`sitemap.xml` or files under `images/`/`assets/` that the old PHP site uses, those files get
replaced. Make sure the old pages that still need to work don't depend on them.

## 7. Recommended: test in a hidden subfolder first

All paths in the package are relative, so the site works from a subfolder:

1. Upload the package contents to `public_html/_lr-preview-<random>/`.
2. Open `https://lateralrepairs.com/_lr-preview-<random>/` on desktop and phone, or run
   `python3 tools/qa/browser_check.py https://lateralrepairs.com/_lr-preview-<random>/`.
3. This tests the real server (MIME types, existing `.htaccess` rewrites). It does **not** test
   the §5 headers, because they are scoped to root paths.
4. Delete the subfolder afterwards.

## 8. Go-live steps

1. Choose a low-traffic window. Complete §1 gates, §6 backups and, ideally, §7.
2. Upload `deployment/public_html/*` to `public_html/` (§2).
3. Append the `.htaccess` additions (§5) and check that the homepage loads.
4. Run all post-deployment tests (§10).
5. Any failure you can't fix in minutes → roll back (§9).
6. In Google Search Console: submit `https://lateralrepairs.com/sitemap.xml` and inspect the
   homepage URL.

## 9. Rollback procedure

**Fast (seconds):** restore the saved `.htaccess` copy. If the old homepage is `index.php`, `/`
serves the old homepage again, because the `DirectoryIndex` line is gone. The new files remain
on disk but are no longer the entry point.

**Full** (SSH; replace `XXXX` with your backup timestamps):

```bash
cd ~/domains/lateralrepairs.com/public_html
cp ~/htaccess-backup-XXXX .htaccess
# delete only files the new site ADDED (files that existed before are left alone)
while read -r hash path; do grep -qxF "$path" ~/lr-collisions.txt || rm -f -- "$path"; done < ~/MANIFEST.sha256
# put back the old versions of files the new site OVERWROTE
[ -s ~/lr-collisions.txt ] && tar xzf ~/backup-public_html-XXXX.tar.gz -C ~/domains/lateralrepairs.com \
    $(sed 's|^|public_html/|' ~/lr-collisions.txt)
# remove folders the new site created, only if they are now empty
for d in products assets/css assets/js assets/vendor assets/fonts assets/datasheets assets/certs \
         images/products images/gallery images/certs assets images; do rmdir "$d" 2>/dev/null; done
```

**Last resort:** restore the whole `public_html` from `backup-public_html-XXXX.tar.gz`. This also
reverts any files the PHP backend wrote since the backup (e.g. uploads), so check that first.

Without SSH: re-upload `.htaccess` and the overwritten files from your FTP backup, then delete
the added files listed in `MANIFEST.sha256` that are not in your collision list.

## 10. Post-deployment tests

Run from any computer with `bash` and `curl` (macOS: replace `sha256sum` with `shasum -a 256`).

| # | Test | Command | Expected |
| --- | --- | --- | --- |
| T1 | New homepage is served | `curl -s https://lateralrepairs.com/ \| grep -o '<title>[^<]*'` | `<title>Lateral Repairs — CIPP Liners …` |
| T2 | Every sitemap URL works | see block A | 20 lines, all `200` |
| T3 | Upload is complete and intact | see block B | no `MISMATCH` lines |
| T4 | Security headers | see block C | CSP, nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy on each page |
| T5 | Caching | `curl -sI 'https://lateralrepairs.com/assets/js/main.js?v=16' \| grep -i cache-control` | `max-age=31536000, immutable`; a datasheet PDF shows `max-age=3600` |
| T6 | Compression | `curl -s -H 'Accept-Encoding: gzip' -o /dev/null -w '%{size_download}\n' 'https://lateralrepairs.com/assets/vendor/three.min.js?v=8'` | far below `669884` (≈170–200 KB) |
| T7 | MIME types | see block D | `font/woff2`, `application/pdf`, `image/svg+xml`, `…javascript`, `text/css` |
| T8 | Canonical host & HTTPS | `curl -sI https://lateralrepairs.com/ \| head -1`; `curl -sI http://lateralrepairs.com/ \| grep -i location`; `curl -sI https://www.lateralrepairs.com/ \| grep -i location` | `200`; both redirects point to `https://lateralrepairs.com/` |
| T9 | Real 404 (no catch-all) | `curl -s -o /dev/null -w '%{http_code}\n' https://lateralrepairs.com/qa-does-not-exist.html` | `404`. If `200`, an old rewrite rule serves the old site for unknown URLs. |
| T10 | Old PHP backend unaffected | open the admin login, the old contact handler and any PHP pages from §6.5 | same behaviour as before — **NOT VERIFIED by this QA; owner must check** |
| T11 | Full browser suite | `python3 tools/qa/browser_check.py https://lateralrepairs.com/` | `73 pass, 0 fail` |
| T12 | Real devices | iPhone Safari + Android Chrome: menu drawer, product page, open a PDF, cookie banner, video consent, contact form notice | everything works; no horizontal scrolling |

```bash
# A — sitemap URLs
curl -s https://lateralrepairs.com/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' |
  while read -r u; do printf '%s %s\n' "$(curl -s -o /dev/null -w '%{http_code}' "$u")" "$u"; done

# B — integrity against the manifest (run inside the repo's deployment/ folder)
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

## 11. Contact form — what is needed to connect it

**Current state (verified):** the form in `index.html` has no `action`. It shows a visible
"NOT CONNECTED YET" notice with the email address and phone number. Browser validation enforces
name and a valid email. On submit it shows "Your message was **NOT sent**". It makes no network
request and never claims success. This repository contains **no** backend endpoint. Nothing is
invented here.

To connect it safely, I need the following from the old production PHP site (**redact all
passwords/SMTP credentials before sharing**):

1. **Handler path**: the URL the current contact form posts to, and whether it is a standalone
   script or a page that posts to itself and renders HTML.
2. **Request contract**: HTTP method, encoding (`application/x-www-form-urlencoded` or
   `multipart/form-data`), and the exact field names and which are required (name, email,
   message, phone, company, GDPR checkbox, …).
3. **CSRF / anti-spam**: token fields and how tokens are created. A session token rendered by PHP
   into the page **cannot** be produced by a static HTML page, so that would need a small backend
   change by whoever owns the PHP code. Also: honeypot field names, CAPTCHA (reCAPTCHA/hCaptcha
   keys and domains, which require CSP changes), rate limiting, `Referer`/`Origin` checks.
4. **Response**: redirect to a thank-you page, HTML, or JSON? Status codes and messages for
   validation errors and failures?
5. **Delivery**: recipient address(es); `mail()` or SMTP; whether SPF/DKIM are set up for
   lateralrepairs.com (otherwise mail lands in spam); UTF-8 handling (Lithuanian characters).
6. **Storage & cookies**: whether submissions are saved to a database (which table, retention),
   and whether the handler sets cookies. Both feed the privacy and cookie policies (§1).
7. **Server-side validation**: whether email/length/content are validated on the server
   (client-side checks alone are not a defence).
8. **Path safety**: confirm the handler's path does not appear in `MANIFEST.sha256`. It
   doesn't by name, but check if it lives under `products/`, `assets/` or `images/`.

The most useful single input is the PHP source of the handler plus the HTML `<form>` markup of
the current contact page ("view source"). Once the contract is known, connecting means:

- set `action` and `method="post"` on the form, add the required (hidden) fields, and remove
  the notice and `data-form-status`;
- adjust `form-action` in the CSP if the handler is on another origin;
- update privacy/cookie text if needed, then rerun QA;
- send a real test enquiry and confirm it arrives in the inbox (not spam) with correct
  characters.

## 12. Remaining known issues

| ID | Priority | Issue | Blocks? |
| --- | --- | --- | --- |
| C1 | CRITICAL | Contact form not connected (§11) | yes, unless the business accepts the visible notice |
| C2 | CRITICAL | Upload into the live `public_html` not yet checked on the server: collisions, `DirectoryIndex`, existing rewrites (§6.4, §5) — **NOT VERIFIED** | yes, until §6 is done |
| P1 | HIGH | 4 `[TO CONFIRM]` facts in `privacy.html` (§1) | yes (legal accuracy) |
| H3 | HIGH | Security headers/compression only active after the `.htaccess` merge (§5, T4/T6) — **NOT VERIFIED** on Serveriai.lt | no, but `privacy.html` §4 depends on it |
| H5 | HIGH | No redirect map from old PHP URLs; old pages stay reachable (duplicate/stale content) — **NOT VERIFIED** | no |
| M5 | MEDIUM | Heavy assets: `three.min.js` 660 KB (old non-module build, logs a deprecation warning), `gallery/patch-kit.jpg` 399 KB, `liner-macro.jpg` 267 KB | no |
| L* | LOW | footer heading skip (h2→h5); no skip link; no custom 404 page; `backdrop-filter` without `-webkit-` on 3 rules; `100svh` without fallback; minor idle animations; brand pink contrast 4.49:1 on black; footer links to lateralrepairs.com open the site itself in a new tab; content items (2006 year, calibration-hose LD/MD file name, missing resin datasheets) | no |
