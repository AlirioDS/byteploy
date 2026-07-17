# Byteploy — sitio web comercial

Sitio web de **Byteploy**, agencia chilena de desarrollo de software a medida.
Español en `/` (mercado principal: Chile) e inglés en `/en/` (clientes internacionales).

**Stack:** HTML + CSS + JavaScript estático, cero dependencias y cero paso de build.
Elegido a propósito: carga instantánea (Core Web Vitals al máximo, factor de ranking en Google),
hosting gratuito en cualquier plataforma y nada que mantener ni actualizar.

## Estructura

```
├── index.html          # Página principal en español (es)
├── en/index.html       # Versión en inglés (en)
├── 404.html            # Página de error (autocontenida)
├── robots.txt          # Permite indexación + apunta al sitemap
├── sitemap.xml         # Ambos idiomas con alternates hreflang
├── site.webmanifest    # Nombre, colores e íconos
└── assets/
    ├── styles.css       # Estilos (tokens de marca al inicio: negro #0A0A0B + amarillo #FFD21E)
    ├── script.js        # Typewriter del titular, menú móvil, animaciones
    ├── logo-icon.png     # Ícono B (tinta negra) — header sobre claro
    ├── logo-icon-light.png # Ícono B (tinta blanca) — sobre fondos oscuros
    ├── wordmark.png      # "byteploy" negro — header sobre claro
    ├── wordmark-light.png# "byteploy" blanco — footer/contacto (oscuro)
    ├── cursor.svg        # Cursor "deploy" (caret, viñetas, terminal)
    ├── circuit.svg       # Trazado de circuito (decoración de secciones)
    ├── check.svg         # Check amarillo del terminal
    ├── favicon.ico / favicon-16.png / favicon-32.png   # Favicons (tile negro, B blanca)
    ├── apple-touch-icon.png / icon-512.png / maskable-512.png
    ├── og.png            # Imagen para compartir (1200×630)
    ├── og-source.html    # Fuente para regenerar og.png
    └── brand/            # PNG originales del logo + process.py (pipeline de assets)
```

> **Marca:** negro `#0A0A0B` + amarillo dorado `#FFD21E`, con el motivo de circuito
> y el cursor de "deploy". Los assets web se generan desde los PNG originales del
> logo (`assets/brand/*-source.png`) con `assets/brand/process.py`.

## Ver el sitio en local

```bash
python3 -m http.server 8000
# → http://localhost:8000        (español)
# → http://localhost:8000/en/    (inglés)
```

## Checklist antes de publicar

- [ ] **Dominio**: todo el sitio usa `https://byteploy.com` como marcador de posición.
      Cuando tengas el dominio real, reemplázalo en un solo comando:
      ```bash
      grep -rl 'byteploy.com' index.html en/index.html sitemap.xml robots.txt \
        | xargs sed -i 's|byteploy\.com|TU-DOMINIO|g'
      ```
- [ ] **Correo de contacto**: hoy apunta a `info@byteploy.com`.
      Cuando tengas correo con dominio propio (ej. `hola@byteploy.com`), búscalo y reemplázalo
      en `index.html` y `en/index.html` (aparece en los `mailto:` y en el JSON-LD).
- [ ] **WhatsApp**: hay un botón comentado en la sección de contacto de ambas páginas —
      descomenta y pon tu número en formato internacional (`56 9 XXXX XXXX` sin espacios).
- [ ] **Redes sociales**: cuando existan, agrega `"sameAs": ["https://..."]` al bloque
      JSON-LD `Organization` de ambas páginas (ayuda al SEO de marca).
- [ ] Revisa la lista de tecnologías y los textos de servicios por si quieres ajustar el alcance.

## Publicar (deploy)

Cualquiera de estas opciones sirve tal cual, sin build:

- **Cloudflare Pages** (recomendado: CDN global gratis + dominio + SSL):
  conecta el repo, framework "None", build command vacío, output `/`.
- **GitHub Pages**: push del repo → Settings → Pages → branch `main` → root.
  Con dominio propio: agrega el dominio en Pages y crea el registro DNS que te indica.
- **Netlify / Vercel**: importa el repo, sin comando de build, directorio de salida `/`.

> Importante: el sitio asume que vive en la **raíz de un dominio** (ej. `byteploy.com`),
> no en una subruta como `usuario.github.io/byteploy`. Usa dominio propio al publicar.

## Subir el repo a GitHub (cuando quieras)

```bash
gh repo create byteploy --private --source=. --push
# o manual:
git remote add origin git@github.com:TU-USUARIO/byteploy.git
git push -u origin main
```

## SEO después de publicar

1. **Google Search Console**: verifica la propiedad y envía `sitemap.xml`.
2. **Bing Webmaster Tools**: importa desde Search Console (2 clics).
3. **Perfil de Empresa en Google** (Google Business Profile): clave para aparecer en
   búsquedas tipo "desarrollo de software + ciudad" en Chile.
4. Considera comprar también **byteploy.cl** y redirigirlo 301 al dominio principal
   (o usar `.cl` como principal si el foco comercial es Chile).
5. Contenido: cuando quieras sumar blog/casos de éxito (muy bueno para SEO),
   el camino natural es migrar este sitio a **Astro** manteniendo el mismo diseño.

Lo que ya viene incluido: metaetiquetas completas (title/description/canonical),
Open Graph + Twitter Cards, `hreflang` es/en/x-default, datos estructurados JSON-LD
(`Organization` + `ProfessionalService` + `FAQPage`), sitemap, robots.txt,
HTML semántico accesible y rendimiento máximo (sin librerías externas).

## Regenerar imágenes de marca

**Logos, favicons e íconos** — desde los PNG originales en `assets/brand/`:

```bash
python3 assets/brand/process.py
```

Esto produce los recortes transparentes (`logo-icon*.png`, `wordmark*.png`) y todos
los favicons/íconos (tile negro con la B blanca). Si reemplazas los originales,
usa los mismos nombres: `assets/brand/icon-source.png` y `wordmark-lower-source.png`.

**Imagen para compartir** (`og.png`, 1200×630) — desde su HTML fuente con Chromium:

```bash
chromium --headless=new --hide-scrollbars --window-size=1200,630 \
  --default-background-color=00000000 --screenshot=assets/og.png assets/og-source.html
```
