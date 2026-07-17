---
name: verify
description: Cómo verificar este sitio estático (Byteploy) de punta a punta en un navegador real.
---

# Verificar el sitio Byteploy

Sitio 100% estático (sin build). La superficie es el navegador.

## Levantar

```bash
python3 -m http.server 8137   # desde la raíz del repo
# → http://localhost:8137/  (ES)  y  http://localhost:8137/en/  (EN)
```

## Suite interactiva automatizada

`cdp_verify.py` (en esta carpeta) levanta un Chromium headless propio y verifica
16 flujos por CDP puro (stdlib): typewriter, overflow, FAQ, anclas, toggle ES↔EN,
menú móvil con ARIA, Escape y consola limpia en ambos idiomas/viewports.

```bash
python3 .claude/skills/verify/cdp_verify.py   # con el server en :8137
```

## Flujos que valen la pena revisar

1. **Hero + typewriter**: el titular rota palabras (proyecto → idea → MVP…).
   Sin abrir DevTools se puede probar con tiempo virtual:
   ```bash
   chromium --headless=new --no-sandbox --hide-scrollbars --window-size=1440,900 \
     --virtual-time-budget=4500 --screenshot=/tmp/tw.png http://localhost:8137/
   # el titular debe mostrar una palabra distinta de "proyecto"
   ```
2. **Móvil (390px)**: nada debe desbordar horizontalmente. El `<pre>` del terminal
   es el sospechoso histórico (se arregló con `.hero-grid > * { min-width: 0 }`).
3. **Menú móvil**, **acordeón FAQ** (`<details>`), **toggle ES↔EN** (`/en/` ↔ `/`),
   y consola sin errores.
4. **SEO estático**: JSON-LD parsea (ambas páginas), preguntas del FAQPage idénticas
   al texto visible, `canonical`/`hreflang` presentes, sitemap.xml bien formado.

## Gotchas del entorno

- En este contenedor fontconfig resuelve `sans-serif` → Liberation Mono: TODO se ve
  monoespaciado en screenshots. No es un bug del sitio; en dispositivos reales
  `system-ui` resuelve a la sans del sistema.
- `python3 -m http.server` no sirve `404.html` para rutas inexistentes (eso lo hace
  el hosting). Probar la página directo: `/404.html`.
- Las imágenes OG/íconos se regeneran con chromium headless (comandos en README.md).
