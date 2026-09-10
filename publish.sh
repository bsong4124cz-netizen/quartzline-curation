#!/bin/bash
# 校验并发布 curation.json
# 用法：bash publish.sh
set -euo pipefail
export PATH="/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")"

echo "════════════════════════════════════════"
echo " Quartzline 精选清单 · 校验并发布"
echo "════════════════════════════════════════"
echo

# 校验不通过会直接退出，不会推送任何东西
/usr/bin/python3 validate.py

echo
if git diff --quiet -- curation.json; then
  echo "内容无变化，无需发布。"
  exit 0
fi

git add curation.json
git commit -q -m "Curation $(date +%F)"
git push -q origin main

echo "✅ 已推送，Cloudflare 约 1 分钟内自动部署"
echo
echo "线上地址："
echo "   https://quartzline-curation.pages.dev/curation.json"
