#!/bin/sh
# Full QA: regenerate, verify generation is deterministic, rebuild the package, run all checks.
#   sh tools/qa/run-all.sh                 # local package
#   sh tools/qa/run-all.sh https://lateralrepairs.com/   # browser checks against production
set -u
cd "$(dirname "$0")/../.." || exit 1
status=0

snap() { cat index.html privacy.html cookies.html sitemap-lr.xml products/*.html | sha256sum; }

echo "== 1. generator: regenerate twice, output must be identical"
python3 tools/build-products.py >/dev/null && a=$(snap)
python3 tools/build-products.py >/dev/null && b=$(snap)
[ "$a" = "$b" ] && echo "PASS generator output is deterministic" || { echo "FAIL generator output changes between runs"; status=1; }

echo "== 2. JavaScript syntax"
if command -v node >/dev/null 2>&1; then
  node --check lr-assets/js/main.js && echo "PASS lr-assets/js/main.js parses" || status=1
else
  echo "SKIP node not installed"
fi

echo "== 3. build deployment package"
python3 tools/build-deploy.py || status=1

echo "== 4. static checks (deployment/public_html)"
python3 tools/qa/static_check.py || status=1

echo "== 5. browser checks"
python3 tools/qa/browser_check.py "$@" || status=1

[ $status -eq 0 ] && printf '\nALL CHECKS PASSED\n' || printf '\nCHECKS FAILED OR BLOCKERS REMAIN (see above)\n'
exit $status
