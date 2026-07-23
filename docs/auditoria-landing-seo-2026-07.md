# Auditoría de la landing Byteploy · deep-research 2026-07-23

Método: 5 ángulos de búsqueda (AI-search/GEO, conversión para agencias, E-E-A-T y SEO técnico, SEO local LATAM/nearshore, chequeo escéptico de anti-patrones), 20 fuentes leídas, 99 claims extraídos, los 25 principales verificados con 3 votos adversariales cada uno: 13 confirmados, 12 refutados. 102 agentes.

## Veredicto general

La landing tiene el SEO on-page al máximo (Lighthouse 100, hreflang/canonical correctos, JSON-LD completo, FAQ = texto visible). Los levers de mayor impacto que quedan son **off-page y de prueba social**, no técnicos. Los gaps del backlog (testimonios, precios, caso con métricas) son exactamente lo que la evidencia verificada señala como lo más rentable.

## Hallazgos confirmados (por impacto)

### 1. La visibilidad en motores de IA se gana FUERA del sitio (confianza alta)
Estudio Ahrefs Q1-2026 sobre 75.000 marcas: menciones en YouTube = correlación más fuerte con visibilidad en respuestas de IA (Spearman ~0,737, consistente en ChatGPT/AI Mode/AI Overviews); menciones de marca en la web 0,66-0,71. Domain Rating (0,27-0,33), backlinks (~0,2-0,3) y cantidad de páginas (~0,19) son débiles. La mitad inferior en menciones web = prácticamente invisible para la IA.
**Para Byteploy**: PR digital, apariciones en terceros (podcasts, charlas, posts ajenos) y presencia en video mencionando la marca rinden más que crear páginas o conseguir links. Correlacional, no causal; efecto más fuerte en superficies de Google.

### 2. El schema NO mueve citas de IA; su rol es verificación de entidad (confianza alta)
Ahrefs siguió 1.885 páginas que agregaron JSON-LD vs ~4.000 de control: sin uplift de citas en ninguna plataforma. Corroborado por experimento searchVIU (5 sistemas de IA leyeron el HTML visible e ignoraron el JSON-LD).
**Para Byteploy**: el JSON-LD sigue valiendo por rich results y desambiguación, no como lever de IA. La única mejora que vale: enriquecer Organization con **vatID/taxID (RUT) y dirección física**, que la doc oficial de Google llama señales de confianza verificables en registros públicos. PENDIENTE: requiere el RUT y una comuna/ciudad del usuario.

### 3. Prueba social con nombre > logos anónimos (confianza media)
A/B sobre ~2.000 páginas: claims con clientes nombrados +22% vs +9% con conteos anónimos y +8% con tiras de logos sin contexto. comScore +69% y DocSend +260% en tests citados con feedback real de clientes.
**Para Byteploy**: Masa Masters ya está nombrado en Casos (bien). Falta: una métrica concreta del caso y subir la mención cerca del hero. NO agregar tira de logos anónimos.

### 4. Barra de calidad para testimonios cuando existan (confianza media)
Nombre completo + cargo + empresa + foto, con datos concretos (no elogios genéricos), narrativa frustración→resolución, y enlazado a un case study completo (41% de compradores B2B los rankean como contenido más influyente; 83% confía más en pares que en el vendor). Matiz NN/g: los usuarios desconfían de testimonios on-site, lo que SUBE la barra de atribución verificable.
**Para Byteploy**: pedir a Masa Masters un testimonio con esa estructura y expandir Makundal a case study enlazado con métricas.

### 5. Precios indicativos: cambia volumen por calidad de lead (confianza media)
86% de compradores B2B considera crítica la transparencia de precios (LinkedIn/Ipsos n=508). A/B de primera mano: publicar precios subió lead→oportunidad +21,4% con -8,7% de volumen (pipeline neto plano). El claim "ocultar precios hace asumir que es caro" fue REFUTADO: el argumento es pre-calificación, no miedo.
**Para Byteploy**: formato "desde US$X" o bandas por modelo de engagement (no tabla SaaS). Requiere números del usuario. Pregunta abierta: el formato óptimo para custom dev no está resuelto por la evidencia.

### 6. Disciplina de CTA: un objetivo primario repetido (confianza media)
Un solo objetivo de conversión (el form) repetido hero/medio/final, con canales alternativos visualmente subordinados. OJO: el claim de que el mix actual form+email+WhatsApp ya viola esto fue REFUTADO 0-3; email/WhatsApp ya están estilizados como secundarios. Solo mantener la jerarquía.

## Refutados (NO invertir en esto)

- "Clutch se rankea solo con reviews verificadas / los top publican tarifas" (1-2 y 0-3): el impacto del perfil Clutch queda SIN estimación verificada.
- "Refrescar contenido cada 3 meses o pierdes citas de IA" (0-3).
- "Listas/citas/estadísticas dan +30-40% de visibilidad en IA" (0-3).
- "Los crawlers de IA no leen accordions/FAQ colapsadas" (0-3): las FAQ en `<details>` están bien.
- "Badges de confianza dan +20-40% de conversión" (0-3).
- "knowsAbout es señal de expertise para IA" (0-3): no agregarlo al schema por eso.
- "Structured data aumenta citas en IA (BrightEdge)" (0-3).

## Preguntas sin respuesta verificada

1. ¿Los directorios B2B (Clutch/GoodFirms/G2) siguen moviendo discovery para agencias chicas en 2026? Sin evidencia que sobreviviera.
2. SEO local Chile/LATAM + nearshore: NINGÚN claim sobrevivió; el ángulo quedó sin cubrir (Google Business Profile, es-CL vs es-419, citations por país).
3. Formato óptimo de precio indicativo para custom dev.
4. ¿Producir YouTube propio mueve visibilidad de IA para una micro-marca, o solo correlaciona con marcas ya populares?

## Plan de acción priorizado

| # | Acción | Dueño | Estado |
| --- | --- | --- | --- |
| 1 | Lanzar el sitio (Cloudflare Pages, DEPLOY.md) | Usuario | Bloqueante de todo |
| 2 | Search Console + sitemap al lanzar | Usuario (guiado) | Pendiente |
| 3 | vatID/taxID (RUT) + address en Organization schema | Claude (falta RUT/ciudad) | Pendiente dato |
| 4 | Testimonio Masa Masters con atribución completa + métrica en Casos | Usuario consigue, Claude implementa | Pendiente |
| 5 | Case study Makundal enlazado (página propia con métricas) | Ambos | Pendiente |
| 6 | Precios indicativos (bandas "desde US$X") | Usuario define números | Pendiente |
| 7 | Menciones off-site: PR digital, podcasts/charlas, video con la marca | Usuario (estrategia continua) | Pendiente |
| 8 | Clutch: hacerlo barato (perfil básico) pero sin esperar impacto verificado | Usuario | Opcional |

Fuentes principales: Ahrefs AI Search Benchmark Q1-2026 (primaria), Ahrefs schema study, Google Organization docs, LinkedIn/Ipsos Deep Sales Playbook, Genesys Growth, SaaSHero, Landingi, Leadfeeder, Bay Leaf Digital (blogs CRO, corroborados parcialmente). Caveat global: los datos de IA-search son Q1-Q2 2026 y ese paisaje cambia trimestre a trimestre.
