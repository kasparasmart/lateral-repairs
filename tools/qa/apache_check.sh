#!/bin/sh
# Apache routing test for deployment/htaccess-additions.conf (development machine only).
# Needs root and an apache2 binary (apt-get install apache2).
#
# Builds a throwaway docroot from deployment/public_html, adds a FAKE CMS Made Simple layout
# (CGI stand-ins for index.php, admin/, modules/, plus assets/ and uploads/), writes a
# representative CMSMS pretty-URL .htaccess with PART A/B merged in, and serves it with
# DirectoryIndex "index.php index.html" (PHP first = worst case). The fixture is NOT the
# production .htaccess; it proves how the additions behave next to standard CMSMS rules.
set -u
REPO=$(cd "$(dirname "$0")/../.." && pwd)
T=${T:-/srv/lr-apache-test}
D=$T/public_html
M=/usr/lib/apache2/modules
command -v apache2 >/dev/null || { echo "apache2 not installed"; exit 2; }

[ -f "$T/httpd.pid" ] && apache2 -f "$T/httpd.conf" -k stop 2>/dev/null; sleep 1
rm -rf "$T"; mkdir -p "$T"; cp -r "$REPO/deployment/public_html" "$D"

mk() { mkdir -p "$(dirname "$D/$1")"
  printf '#!/bin/sh\ncat >/dev/null\nprintf "Content-Type: text/plain\\r\\n\\r\\n"\necho "SERVED-BY: %s"\necho "METHOD: $REQUEST_METHOD"\necho "QUERY: $QUERY_STRING"\n' "$2" > "$D/$1"
  chmod 755 "$D/$1"; }
mk index.php "CMSMS index.php"; mk admin/index.php "CMSMS admin/index.php"; mk modules/FormBuilder/action.php "CMSMS module file"
mkdir -p "$D/assets/templates" "$D/uploads/images"
echo "cmsms template" > "$D/assets/templates/demo.tpl"; echo "old upload" > "$D/uploads/images/old.txt"

python3 -I - "$D/.htaccess" "$REPO/deployment/htaccess-additions.conf" << 'PYEOF'
import sys
out, add = sys.argv[1], open(sys.argv[2]).read()
part_a = add[add.index("RewriteCond %{REQUEST_METHOD}"):add.index("# -----------------------------------------------------------------------------\n# PART B")]
part_b = add[add.index("AddType font/woff2"):]
open(out, "w").write(f"""# representative CMS Made Simple .htaccess (TEST FIXTURE, not production)
Options -Indexes
Options +FollowSymLinks
<IfModule mod_rewrite.c>
RewriteEngine on
RewriteBase /
{part_a}
RewriteCond %{{REQUEST_FILENAME}} !-f
RewriteCond %{{REQUEST_FILENAME}} !-d
RewriteRule ^(.+)$ index.php?page=$1 [QSA]
</IfModule>
{part_b}""")
PYEOF

cat > "$T/httpd.conf" << EOF
ServerRoot "/etc/apache2"
ServerName lr-test.local
Listen 127.0.0.1:8088
PidFile $T/httpd.pid
User www-data
Group www-data
ErrorLog $T/error.log
LoadModule mpm_event_module $M/mod_mpm_event.so
LoadModule authz_core_module $M/mod_authz_core.so
LoadModule mime_module $M/mod_mime.so
LoadModule dir_module $M/mod_dir.so
LoadModule autoindex_module $M/mod_autoindex.so
LoadModule rewrite_module $M/mod_rewrite.so
LoadModule headers_module $M/mod_headers.so
LoadModule filter_module $M/mod_filter.so
LoadModule deflate_module $M/mod_deflate.so
LoadModule cgid_module $M/mod_cgid.so
ScriptSock $T/cgisock
TypesConfig /etc/mime.types
DocumentRoot $D
DirectoryIndex index.php index.html
<Directory $D>
  AllowOverride All
  Options +ExecCGI
  AddHandler cgi-script .php
  Require all granted
</Directory>
EOF
chown -R www-data:www-data "$T"
apache2 -f "$T/httpd.conf" -k start || exit 1; sleep 1

B=http://127.0.0.1:8088; pass=0; fail=0
t() { name=$1; exp=$2; shift 2; out=$(curl -s -i "$@" 2>/dev/null | tr -d '\000'); code=$(printf '%s' "$out" | head -1 | awk '{print $2}')
  if printf '%s' "$out" | grep -q -- "$exp"; then pass=$((pass+1)); r=PASS; else fail=$((fail+1)); r=FAIL; fi
  printf '%s %-58s HTTP %s\n' "$r" "$name" "$code"; [ $r = FAIL ] && printf '%s\n' "$out" | head -8 | sed 's/^/      /'; return 0; }
no() { name=$1; pat=$2; shift 2; if curl -s -i "$@" | grep -qi -- "$pat"; then fail=$((fail+1)); echo "FAIL $name"; else pass=$((pass+1)); echo "PASS $name"; fi; }

echo "== routing (DirectoryIndex index.php index.html = PHP first)"
t "GET /                    -> new index.html"            "<title>Lateral Repairs — CIPP" $B/
t "HEAD /                   -> new index.html"            "Content-Type: text/html" -I $B/
t "GET /?page=about         -> CMSMS index.php"           "QUERY: page=about" "$B/?page=about"
t "GET /?mact=FormBuilder.. -> CMSMS index.php"           "QUERY: mact=FormBuilder" "$B/?mact=FormBuilder,m1,default,1"
t "POST /                   -> CMSMS index.php"           "METHOD: POST" -X POST -d a=1 $B/
t "GET /index.php           -> CMSMS index.php"           "SERVED-BY: CMSMS index.php" $B/index.php
t "GET /about-us (pretty)   -> CMSMS index.php?page="     "QUERY: page=about-us" $B/about-us
t "GET /admin/              -> CMSMS admin/index.php"     "SERVED-BY: CMSMS admin/index.php" $B/admin/
t "POST /admin/             -> CMSMS admin (POST intact)" "METHOD: POST" -X POST -d u=x $B/admin/
t "GET /modules/.../x.php   -> module PHP"                "SERVED-BY: CMSMS module file" $B/modules/FormBuilder/action.php
t "GET /assets/... (CMSMS)  -> untouched"                 "cmsms template" $B/assets/templates/demo.tpl
t "GET /uploads/...         -> untouched"                 "old upload" $B/uploads/images/old.txt
t "GET /unknown-url         -> CMSMS (as before)"         "QUERY: page=unknown-url" $B/unknown-url
t "GET /privacy.html        -> static"                    "<title>Privacy Policy" $B/privacy.html
t "GET /products/x.html     -> static"                    "<title>MULTIline FLEX" $B/products/multiline-flex.html
t "GET /products/           -> 403, no listing"           "HTTP/1.1 403" $B/products/
t "GET /lr-assets/js/main.js-> static JS"                 "Content-Type: text/javascript" "$B/lr-assets/js/main.js?v=16"
t "GET datasheet PDF        -> application/pdf"           "Content-Type: application/pdf" $B/lr-assets/datasheets/LR_MULTIline_FLEX.pdf
echo "== PART B headers (scoped)"
t "CSP on /"                                              "Content-Security-Policy: default-src" $B/
t "CSP on product page"                                   "Content-Security-Policy:" $B/products/lr-uv-resin.html
no "no CSP on CMSMS page /?page=about"                    "content-security-policy" "$B/?page=about"
no "no CSP/X-Frame on /admin/"                            "content-security-policy\|x-frame-options" $B/admin/
t "1y immutable cache on lr-assets JS"                    "max-age=31536000, immutable" "$B/lr-assets/js/main.js?v=16"
t "1h cache on PDFs"                                      "max-age=3600" $B/lr-assets/datasheets/LR_MULTIline_FLEX.pdf
t "7d cache on photos"                                    "max-age=604800" $B/lr-assets/images/products/flex.jpg
t "woff2 MIME"                                            "Content-Type: font/woff2" $B/lr-assets/fonts/inter-latin-400-normal.woff2
t "gzip three.min.js"                                     "Content-Encoding: gzip" -H "Accept-Encoding: gzip" "$B/lr-assets/vendor/three.min.js?v=8"
t "gzip index.html"                                       "Content-Encoding: gzip" -H "Accept-Encoding: gzip" $B/
echo "      three.min.js gzipped: $(curl -s -H 'Accept-Encoding: gzip' -o /dev/null -w '%{size_download}' "$B/lr-assets/vendor/three.min.js?v=8") bytes (raw 669884)"
errs=$(grep -c -E '\[(core|rewrite|headers):(error|alert)\]' "$T/error.log" 2>/dev/null); echo "      apache error-log entries: ${errs:-0}"

apache2 -f "$T/httpd.conf" -k stop; sleep 1
echo "== $pass pass, $fail fail"
[ "$fail" -eq 0 ]
