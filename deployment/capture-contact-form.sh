#!/bin/sh
# READ-ONLY capture of the existing contact/inquiry form on www.lateralrepairs.com.
#
# Makes only GET requests to public pages, exactly like a browser opening the page twice.
# It NEVER submits the form. Writes one report file in the current directory.
#
#   sh capture-contact-form.sh                          # lists candidate contact-page links
#   sh capture-contact-form.sh https://www.lateralrepairs.com/<contact-page>/
#
# Send lr-contact-form-report.txt back. It contains only public page markup; session cookie
# VALUES are masked.
set -u
SITE="https://www.lateralrepairs.com"
UA="Mozilla/5.0 (LR contact-form capture, read-only)"
OUT="lr-contact-form-report.txt"
TMP="${TMPDIR:-/tmp}/lr-capture.$$"; mkdir -p "$TMP"

if [ $# -eq 0 ]; then
  echo "Candidate contact pages linked from the homepage:"
  curl -s -A "$UA" "$SITE/" | grep -o -i 'href="[^"]*"' | grep -i -E 'kontakt|contact|uzklaus|užklaus|inquir|enquir|susisiek' | sort -u
  echo; echo "Run again with the contact page URL as the argument."
  rm -rf "$TMP"; exit 0
fi
URL=$1

forms() { awk '{l=tolower($0)} l~/<form/{f=1} f{print} l~/<\/form>/{f=0}' "$1"; }
hidden() { grep -o -i '<input[^>]*type=["'"'"']hidden["'"'"'][^>]*>' "$1" | sort; }

for i in 1 2; do  # two independent visits: no shared cookies
  curl -s -A "$UA" -D "$TMP/h$i" -o "$TMP/p$i" "$URL"
done

{
  echo "== capture of $URL"; date
  echo; echo "== HTTP status / redirects (visit 1)"; grep -i -E '^(HTTP/|location:)' "$TMP/h1"
  echo; echo "== cookies the page sets (values masked)"; grep -i '^set-cookie:' "$TMP/h1" | sed -E 's/^([Ss]et-[Cc]ookie: *[^=]+=)[^;]*/\1<masked>/'
  echo; echo "== <form> blocks (visit 1)"; forms "$TMP/p1"
  echo; echo "== hidden inputs, visit 1"; hidden "$TMP/p1"
  echo; echo "== hidden inputs, visit 2"; hidden "$TMP/p2"
  echo; echo "== do hidden values change between visits? (no output = identical = static)"
  hidden "$TMP/p1" > "$TMP/x1"; hidden "$TMP/p2" > "$TMP/x2"; diff "$TMP/x1" "$TMP/x2"
  echo; echo "== CAPTCHA / anti-spam markers"
  grep -o -i -E 'recaptcha[^"'"'"' ]*|hcaptcha[^"'"'"' ]*|turnstile[^"'"'"' ]*|captcha[^"'"'"' <]*|honeypot[^"'"'"' ]*' "$TMP/p1" | sort -u
  echo; echo "== scripts that may submit the form (AJAX)"
  grep -o -i -E '<script[^>]*src="[^"]*"|ajax\.php[^"'"'"' ]*|\$\.(ajax|post)\([^)]{0,80}|fetch\([^)]{0,80}' "$TMP/p1" | sort -u
} > "$OUT" 2>&1

rm -rf "$TMP"
echo "Report written to $OUT (no form was submitted)."
