#!/bin/sh
# READ-ONLY inspection of the existing lateralrepairs.com hosting, run BEFORE any upload.
#
# It only lists and reads files (ls, find, grep, cat). It never creates, edits, moves or
# deletes anything inside the website. The only file it writes is the report in $HOME.
#
#   1. Upload deployment/MANIFEST.sha256 to your HOME directory (NOT public_html).
#   2. Upload this script to your HOME directory and run:  sh ~/inspect-server-readonly.sh
#   3. READ ~/lr-server-report.txt, remove anything sensitive the redaction missed,
#      then share it.
#
# Adjust DOCROOT if the document root is elsewhere.
DOCROOT="${DOCROOT:-$HOME/domains/lateralrepairs.com/public_html}"
OUT="$HOME/lr-server-report.txt"
MANIFEST="$HOME/MANIFEST.sha256"

[ -d "$DOCROOT" ] || { echo "Document root not found: $DOCROOT (set DOCROOT=...)"; exit 1; }
cd "$DOCROOT" || exit 1

section() { printf '\n==================== %s ====================\n' "$1"; }
PHPGREP="--include=*.php --include=*.phtml --include=*.inc --include=*.tpl --include=*.twig --include=*.html"

{
section "document root"; pwd; date
section "top level (ls -la)"; ls -la
section "index files at the root (which one serves / depends on DirectoryIndex)"; ls -la index.* 2>/dev/null || echo "(no index.* files)"

section "public_html/.htaccess (full)"; cat .htaccess 2>/dev/null || echo "(no .htaccess in document root)"
section "all other .htaccess files"; find . -name .htaccess ! -path ./.htaccess -print 2>/dev/null
section "DirectoryIndex / RewriteRule / RewriteCond / Options / ErrorDocument lines in every .htaccess"
find . -name .htaccess -exec grep -Hn -i -E 'DirectoryIndex|Rewrite(Rule|Cond|Base|Engine)|Options|ErrorDocument|FallbackResource|Header|Expires|Deflate' {} \; 2>/dev/null
section "PHP ini overrides"; ls -la .user.ini php.ini 2>/dev/null; cat .user.ini 2>/dev/null

section "paths the new frontend would create or overwrite (top level)"
for p in index.html privacy.html cookies.html robots.txt sitemap.xml products assets images; do
  if [ -e "$p" ]; then printf 'EXISTS  %s\n' "$p"; ls -ld "$p"; else printf 'absent  %s\n' "$p"; fi
done
section "manifest collisions (files that WOULD BE OVERWRITTEN)"
if [ -f "$MANIFEST" ]; then
  n=0; while read -r hash path; do [ -e "$path" ] && { echo "$path"; n=$((n+1)); }; done < "$MANIFEST"; echo "collisions: $n"
else
  echo "MANIFEST.sha256 not found in \$HOME - collision check skipped"
fi

section "backend folders (admin / ajax / modules / plugins / vendor / uploads / includes / config)"
for p in admin administrator ajax.php ajax modules plugins vendor uploads upload files includes inc config core app lib cache tmp; do
  [ -e "$p" ] && ls -ld "$p"
done
section "PHP files at the root"; ls -la ./*.php 2>/dev/null

section "<form> tags in PHP/templates (contact form candidates)"
grep -rIn $PHPGREP -i '<form' . 2>/dev/null | grep -v '/vendor/' | head -80
section "files mentioning contact / kontakt / enquiry / uzklaus"
grep -rIl $PHPGREP -i -E 'contact|kontakt|enquir|inquir|uzklaus|užklaus' . 2>/dev/null | grep -v '/vendor/' | head -60
section "mail sending (mail(), PHPMailer, SMTP, Swift/Symfony mailer)"
grep -rIn --include=*.php -E 'mail[[:space:]]*\(|PHPMailer|SwiftMailer|Symfony.Component.Mailer|->isSMTP|SMTPAuth' . 2>/dev/null | grep -v '/vendor/' | head -60
section "CAPTCHA / CSRF / honeypot"
grep -rIn $PHPGREP -i -E 'recaptcha|hcaptcha|turnstile|captcha|csrf|_token|honeypot' . 2>/dev/null | grep -v '/vendor/' | head -60
section "sessions / cookies"
grep -rIln --include=*.php -E 'session_start|setcookie' . 2>/dev/null | grep -v '/vendor/' | head -60
section "database inserts"
grep -rIn --include=*.php -i -E 'insert[[:space:]]+into' . 2>/dev/null | grep -v '/vendor/' | head -60
section "AJAX endpoints referenced from front-end JS"
grep -rIn --include=*.js -E '\.php|\$\.(ajax|post|get)\(|fetch\(' . 2>/dev/null | grep -v -E '/vendor/|\.min\.js' | head -60
} > "$OUT" 2>&1

# best-effort redaction of credentials (REVIEW THE REPORT ANYWAY)
sed -i -E "s/((pass(word)?|passwd|pwd|secret|api[_-]?key|smtp_?pass|db_?pass)['\"]?[[:space:]]*(=>|=|:|,)[[:space:]]*)['\"][^'\"]*['\"]/\1'<REDACTED>'/Ig" "$OUT"
echo "Read-only report written to $OUT - review it before sharing."
