#!/bin/sh
# Deploy manual a Cloudflare Pages (fallback; el camino normal es git push
# a main, que dispara .github/workflows/deploy.yml).
# Requiere CLOUDFLARE_API_TOKEN en el entorno.
set -e
cd "$(dirname "$0")/.."
./scripts/build.sh
npx --yes wrangler pages deploy dist --project-name byteploy
