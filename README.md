# Byteploy · sitio web comercial

Sitio de **[Byteploy](https://byteploy.com)**, agencia chilena de desarrollo de
software a medida. Español en `/` e inglés en `/en/`.

**Stack: HTML + CSS + JS estático, cero dependencias, cero build.** Elegido a
propósito: Lighthouse 100/100/100/100 en ambas páginas, CLS 0, fuentes
self-hosted (sin CDN) y nada que mantener. La única pieza dinámica es el
formulario de contacto: una Cloudflare Pages Function (`functions/api/contact.js`)
que valida Cloudflare Turnstile en el servidor y envía el correo vía API de Brevo.

## Estructura

```
├── index.html            # Página principal (es)
├── en/index.html         # Versión en inglés (en)
├── 404.html              # Error autocontenido
├── robots.txt            # Indexación + sitemap
├── sitemap.xml           # Ambos idiomas con alternates hreflang
├── site.webmanifest
├── functions/api/contact.js   # Endpoint del formulario (Turnstile + Brevo)
├── scripts/
│   ├── build.sh          # Arma dist/ (lo publicable, sin fuentes de marca)
│   └── deploy.sh         # Deploy manual de respaldo (wrangler)
├── .github/workflows/deploy.yml  # CI: push a main = deploy a Cloudflare Pages
├── .claude/skills/verify/        # Suite de verificación (16 chequeos CDP)
└── assets/
    ├── styles.css        # Tokens de marca al inicio (papel/tinta/amarillo)
    ├── script.js         # Typewriter, terminal animado, reveal, menú, formulario
    ├── fonts/            # Manrope variable + IBM Plex Mono (woff2, subset latin)
    ├── wordmark*.png, favicons, og.png, founder.jpg, makundal-demo.gif
    └── brand/            # Fuentes de marca + pipeline (no se publica en dist/)
```

> **Marca:** papel `#F6F4EF` · tinta `#111114` · amarillo `#FFD21F` · oro
> `#C99E00`, con motivo de terminal/deploy. **Tipografía:** Manrope
> (display 800 / cuerpo 500) + IBM Plex Mono (labels, terminal), self-hosted.

## Desarrollo local

```bash
python3 -m http.server 8000
# → http://localhost:8000        (español)
# → http://localhost:8000/en/    (inglés)
```

El formulario en local muestra "en configuración" (no hay endpoint ni captcha
fuera de Cloudflare); es el comportamiento esperado.

## Verificación

```bash
# Suite interactiva (16 chequeos en Chromium headless via CDP):
SITE_BASE=http://localhost:8000 CDP_PORT=9251 python3 .claude/skills/verify/cdp_verify.py

# Lighthouse:
npx lighthouse@12 http://localhost:8000 --preset=desktop \
  --chrome-flags="--headless=new --user-data-dir=$(mktemp -d)"
```

Regla del repo: todo cambio se verifica antes de commitear (suite completa +
Lighthouse 100 + FAQ visible idéntica al JSON-LD).

## Deploy

`git push` a `main` publica automáticamente en Cloudflare Pages
(`.github/workflows/deploy.yml`; secrets del repo: `CLOUDFLARE_API_TOKEN` con
permiso Pages:Edit y `CLOUDFLARE_ACCOUNT_ID`). Fallback manual:
`CLOUDFLARE_API_TOKEN=... ./scripts/deploy.sh`.

Configuración del formulario en Pages (Settings → Variables and Secrets):
`TURNSTILE_SECRET_KEY`, `BREVO_API_KEY` y opcionales `CONTACT_TO` /
`CONTACT_FROM_EMAIL` / `CONTACT_FROM_NAME`. La Site Key de Turnstile vive en el
atributo `data-sitekey` de ambos HTML (es pública).

## Regenerar assets de marca

```bash
python3 assets/brand/process.py        # logos, wordmarks, favicons, íconos
python3 assets/brand/make_founder.py   # foto del fundador (recorte + gradación)

# og.png (1200×630) desde su fuente:
chromium --headless=new --hide-scrollbars --window-size=1200,630 \
  --default-background-color=00000000 --screenshot=assets/og.png assets/og-source.html

# GIF de la demo de Makundal (staging local; credenciales por entorno):
DEMO_BASE_URL=... DEMO_EMAIL=... DEMO_PASSWORD=... \
  python3 assets/brand/capture-makundal-demo.py
```

## SEO pendiente post-lanzamiento

1. Google Search Console: verificar propiedad + enviar `sitemap.xml`.
2. Bing Webmaster Tools (importa desde Search Console).
3. Google Business Profile (búsquedas "desarrollo de software + ciudad").
4. Considerar `byteploy.cl` con redirect 301 al `.com`.

Incluido de fábrica: canonical + hreflang es/en/x-default, OG/Twitter Cards,
JSON-LD (`Organization` + `ProfessionalService` + `FAQPage` sincronizada con el
texto visible), sitemap, robots y HTML semántico accesible.
