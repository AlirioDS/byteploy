#!/bin/sh
# Despliega el sitio a Cloudflare Pages por subida directa (sin git remoto).
# Requiere: npx wrangler login (una vez) y el proyecto Pages "byteploy" creado
# (la primera ejecución lo crea si no existe).
set -e
cd "$(dirname "$0")/.."

rm -rf dist
mkdir -p dist
cp -r index.html 404.html en assets site.webmanifest sitemap.xml robots.txt dist/
rm -rf dist/assets/brand  # fuentes y scripts del pipeline de marca no se publican

# wrangler toma functions/ desde la raíz del proyecto (endpoint /api/contact)
npx --yes wrangler pages deploy dist --project-name byteploy
