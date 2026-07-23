#!/bin/sh
# Arma dist/ con los archivos publicables del sitio (usado por CI y deploy.sh).
set -e
cd "$(dirname "$0")/.."
rm -rf dist
mkdir -p dist
cp -r index.html 404.html en assets site.webmanifest sitemap.xml robots.txt dist/
rm -rf dist/assets/brand  # fuentes y scripts del pipeline de marca no se publican
