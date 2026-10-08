# Release runbook: Lateral Repairs frontend on lateralrepairs.com (Serveriai.lt)

The new static frontend is added **next to** the existing CMS Made Simple (CMSMS) site. The
CMSMS backend, admin, database, modules, plugins, uploads and server configuration stay exactly
as they are. Only one `.htaccess` change (3 lines) makes the root URL `/` show the new homepage.

| | Status |
| --- | --- |
| Frontend package | Passes full QA, **except 3 `[TO CONFIRM]` facts in `privacy.html`** (§1) |
| Contact form | **NOT CONNECTED** — visibly marked; visitors are sent to email/phone (§11) |
| Server configuration | **NOT VERIFIED** — production `.htaccess`/layout not seen; §3 checks it before upload |

Server folder: `domains/lateralrepairs.com/public_html/` (confirm in the control panel).

---

## 1. Before release (5 minutes, in the repo)

Fill in the 3 highlighted facts in `privacy.html`. Replace each
`<span class="confirm">[TO CONFIRM: …]</span>` with plain text:

1. **Publication date** (e.g. the release date).
2. **Legal name of the hosting company behind Serveriai.lt, and the country of its servers.**
3. **Server log retention period** (from Serveriai.lt).

Then rebuild and recheck:
```bash
python3 tools/build-products.py && python3 tools/build-deploy.py && python3 tools/qa/static_check.py
```
The static check must end with **0 blocker(s)**. The contact form shows as `KNOWN`.

## 2. What gets uploaded (exact)

The **contents** of `deployment/public_html/`: 87 files, 11.2 MB, listed with SHA-256 hashes in
`deployment/MANIFEST.sha256`. The upload touches **only these 7 names** in the document root:

```
public_html/
├── index.html          new homepage (served at / by the §6 rule)
├── privacy.html
├── cookies.html
├── robots.txt          replaces an existing robots.txt, if any (back it up, §4)
├── sitemap.xml         replaces an existing sitemap.xml, if any (back it up, §4)
├── products/           17 product pages
└── lr-assets/          all CSS, JS, fonts, images, datasheet PDFs, ISO certificate
    ├── css/  js/  vendor/  fonts/  datasheets/  certs/
    └── images/  (+ products/ gallery/ certs/)
```

All frontend assets sit in **`lr-assets/`** on purpose. CMSMS 2.x already uses a top-level
`assets/` folder for templates and module overrides, so the new site never writes into it. The
package builder refuses to package any PHP file, `config.php`, `.htaccess`, SQL file, or
anything under `admin/`, `modules/`, `plugins/`, `vendor/`, `uploads/`, `lib/`, `tmp/`, `doc/`,
`install/` or `assets/`.

Upload in binary mode (FileZilla "auto" is fine) and keep filenames exactly as they are.

## 3. Pre-upload checks on the server (read-only, ~15 minutes)

FTP or the control panel's file manager is enough. Nothing is changed in this step.

| # | Check | If… |
| --- | --- | --- |
| A | Do `products/` or `lr-assets/` already exist in `public_html/`? | **either exists → STOP and send me the listing** |
| B | Does `index.html` exist in `public_html/`? | yes → download a copy (it may be what `/` serves today) |
| C | Do `robots.txt` / `sitemap.xml` / `privacy.html` / `cookies.html` exist? | yes → download copies; they will be replaced |
| D | Open `public_html/.htaccess` (download a copy). Find the line `RewriteEngine on`. | not found → note it (see §6) |
| E | In that `.htaccess`, is there a rule that sends **every** request to `index.php` *without* `RewriteCond %{REQUEST_FILENAME} !-f` before it? | yes → **STOP and send me the file**: it would hide the new pages |
| F | Is there an existing rule whose pattern matches the root (`^$`, `^/?$`, `^index\.html$`)? | yes → send me the file |
| G | Note the admin URL and one or two normal CMS page URLs (e.g. `/?page=…` or a pretty URL) for the post-release tests | — |

With SSH you can instead run the read-only `deployment/inspect-server-readonly.sh` (put it and
`MANIFEST.sha256` in your home directory, **not** in `public_html`). It writes only
`~/lr-server-report.txt`.

## 4. Backup (before uploading)

1. **Files:** download all of `public_html/` via FTP, or use the control panel's backup for the
   domain. With SSH:
   `cd ~/domains/lateralrepairs.com && tar czf ~/backup-public_html-$(date +%Y%m%d-%H%M).tar.gz public_html`
2. **`.htaccess`:** keep a separate copy (you'll edit it in §6).
3. **Database:** export it from the control panel / phpMyAdmin. It's untouched by this release,
   but CMSMS depends on it.
4. Keep the copies from §3 B/C.

## 5. Files that must NOT be uploaded

Everything outside `deployment/public_html/`, in particular:

- `.git/`, `.gitignore`, `.vercelignore`, `vercel.json` (Vercel preview config);
- `README.md`, `tools/`;
- `deployment/DEPLOY.md`, `deployment/MANIFEST.sha256`, `deployment/inspect-server-readonly.sh`;
- `deployment/htaccess-additions.conf` (copy its lines into `.htaccess`; never upload the file).

## 6. Index handling (`index.html` vs the CMSMS `index.php`)

**Do not change `DirectoryIndex`.** CMSMS needs `index.php` as its front controller for every
CMS page, pretty URL, module action and the admin. Changing `DirectoryIndex` site-wide would
also affect any subdirectory that holds both an `index.html` and an `index.php`.

Instead, add **PART A** of `deployment/htaccess-additions.conf` (3 lines). In the existing
`public_html/.htaccess`, insert them **directly after** `RewriteEngine on` (and after
`RewriteBase /` if present), **before** the CMSMS rewrite rules:

```apache
RewriteCond %{REQUEST_METHOD} ^(GET|HEAD)$
RewriteCond %{QUERY_STRING} ^$
RewriteRule ^$ index.html [L]
```

The rule fires only for a plain `GET`/`HEAD` of exactly `/` with no query string. It changes
nothing else:

| Request | Served by |
| --- | --- |
| `GET /` | **new `index.html`** |
| `/?page=…`, `/?mact=…` (CMSMS pages and module actions), any `POST /` | CMSMS `index.php`, as today |
| `/index.php`, CMS pretty URLs, unknown URLs | CMSMS `index.php`, as today |
| `/admin/` (GET and POST), `modules/`, `plugins/`, CMSMS `assets/`, `uploads/` | unchanged |
| `/privacy.html`, `/products/*.html`, `/lr-assets/…` | the new static files |

**Tested:** `tools/qa/apache_check.sh` runs this rule on Apache 2.4.58 next to a representative
CMSMS pretty-URL `.htaccess`, with the worst-case `DirectoryIndex index.php index.html`.
Result: **28/28 pass**, covering every row above plus `/products/` → 403 (no listing).
The **production** `.htaccess` itself is NOT VERIFIED, which is why §3 D–F and the §9 tests exist.

- If the file has **no** `RewriteEngine on`, add `RewriteEngine on` above the three lines.
- If `mod_rewrite` is not allowed at all (HTTP 500 after saving), remove the lines and tell me.
  The fallback is `DirectoryIndex index.html index.php`, but that is a site-wide change, so first
  confirm that no backend folder contains both `index.html` and `index.php`.

## 7. `.htaccess` PART B (optional; not needed for launch)

PART B of `deployment/htaccess-additions.conf` adds security headers to the new pages,
long-term caching for `lr-assets/`, gzip (three.min.js: 669,884 → 167,196 bytes) and the
`woff2` font type. Every rule is scoped by path to the new frontend only; in the test, CMS pages
and `/admin/` got no new headers. **Append it at the end** of the existing file. If the site
returns HTTP 500 afterwards, remove PART B again (keep PART A).

`privacy.html` §4 mentions a Content Security Policy and HSTS. If PART B is not active, ask me to
reword that paragraph. HSTS stays commented out until HTTPS works on both `lateralrepairs.com`
and `www.lateralrepairs.com`.

## 8. Release steps

1. §1 done (static check: 0 blockers). §3 checks passed. §4 backups taken.
2. Upload the contents of `deployment/public_html/` to `public_html/`.
3. Edit `.htaccess`: add PART A (§6). Save, then open `https://lateralrepairs.com/` straight away.
4. Optional: append PART B (§7), then reload.
5. Run the §9 tests. If any **must-pass** test fails and can't be fixed in minutes → §10.

## 9. Post-deployment tests

With the usual CMSMS rewrite rules, a request for a **missing** file is handed to CMSMS, which
answers it with its own page. Whether that comes with a 404 or a 200 status on this site is NOT
VERIFIED, so a status code alone doesn't prove a file was uploaded. Test 3 (hash check) is the
reliable proof that the upload is complete.

| # | Must pass | Test | Expected |
| --- | --- | --- | --- |
| 1 | yes | `curl -s https://lateralrepairs.com/ \| grep -o '<title>[^<]*'` | `<title>Lateral Repairs — CIPP Liners …` |
| 2 | yes | open the admin URL from §3 G and log in; open a CMS page from §3 G | works exactly as before |
| 3 | yes | **integrity:** block A, run in the repo's `deployment/` folder | `integrity check done`, no `MISMATCH` |
| 4 | yes | **pages:** block B | 18 × `OK` |
| 5 | yes | `curl -s -o /dev/null -w '%{http_code}\n' 'https://lateralrepairs.com/?page=<alias from §3 G>'` | same status as before the release (normally 200) |
| 6 | yes | phone (iPhone Safari + Android Chrome): menu drawer, a product page, open a datasheet PDF, cookie banner, contact section shows "NOT CONNECTED YET" | all work, no sideways scrolling |
| 7 | no | `curl -sI https://lateralrepairs.com/products/multiline-flex.html \| grep -i content-security-policy` | present if PART B is active |
| 8 | no | `curl -s -H 'Accept-Encoding: gzip' -o /dev/null -w '%{size_download}\n' 'https://lateralrepairs.com/lr-assets/vendor/three.min.js?v=8'` | ≈170 KB if PART B is active, 669,884 if not |
| 9 | no | `curl -sI http://lateralrepairs.com/ \| grep -i location`; `curl -sI https://www.lateralrepairs.com/ \| grep -i location` | both → `https://lateralrepairs.com/` (if not, report it; it doesn't block the release) |
| 10 | no | `python3 tools/qa/browser_check.py https://lateralrepairs.com/` (needs Playwright) | 0 fail |

```bash
# A — every uploaded file is present and identical (macOS: use 'shasum -a 256')
while read -r hash path; do
  got=$(curl -s "https://lateralrepairs.com/$path" | sha256sum | cut -d' ' -f1)
  [ "$got" = "$hash" ] || echo "MISMATCH $path"
done < MANIFEST.sha256; echo "integrity check done"

# B — each sitemap URL serves the new page (canonical must equal the URL)
curl -s https://lateralrepairs.com/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' | while read -r u; do
  c=$(curl -s "$u" | grep -o '<link rel="canonical" href="[^"]*"' | sed 's/.*href="//; s/"$//')
  [ "$c" = "$u" ] && echo "OK    $u" || echo "WRONG $u (canonical: ${c:-none})"
done
```

## 10. Rollback

**Fast, seconds:** in `.htaccess`, delete the 3 PART A lines (and PART B if added) or restore the
`.htaccess` copy from §4. `/` immediately serves the CMSMS homepage again. The new files can stay
on disk; nothing links to them from the CMS.

**Full removal:** delete exactly what the release added:

- `products/` and `lr-assets/` (both new; §3 A confirmed they didn't exist);
- `index.html`, `privacy.html`, `cookies.html`, `robots.txt`, `sitemap.xml`;
- then put back any of those 5 files you saved in §3 B/C.

Never delete anything else.

## 11. Contact form: NOT CONNECTED

The form in `index.html` has no `action` and carries `data-form-status="not-connected"`.
Visitors see "NOT CONNECTED YET — please email info@lateralrepairs.com or call +370 698 76581".
Browser validation requires a name and a valid email. On submit it shows "Your message was **NOT
sent**", sends no request and never claims success. No backend was invented, and the privacy
policy states that enquiries currently arrive by email/phone only.

To connect it after the release I need:

1. The URL of the current CMSMS contact page.
2. Its `<form>` HTML: View Source, copy `<form …>…</form>`.
3. Which CMSMS module renders it, from the admin's module list.

A CMSMS module form usually posts to `index.php` with hidden fields that CMSMS generates per
request. Whether those can be reproduced from a static page is **NOT VERIFIED** until I see 1–3.
Options then: link to the existing CMS contact page, add a small handler (by whoever maintains the
PHP site), or keep the current state.

## 12. Not verified (needs the server)

- Production `.htaccess` content, the effective `DirectoryIndex`, `mod_rewrite` / `<If>` /
  `mod_headers` / `mod_deflate` availability. §3 D–F, §6, §7 and test 1 cover these.
- Whether `products/`, `lr-assets/`, `index.html`, `robots.txt`, `sitemap.xml` already exist (§3 A–C).
- The CMSMS contact-form module and its handler (§11).
- HTTPS/`www` redirects and certificate coverage (test 9).
- Hosting legal entity, server country, log retention (§1).
- Old CMS URLs still indexed by search engines. They keep working via CMSMS; a redirect plan can
  follow after the release.
