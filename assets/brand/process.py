#!/usr/bin/env python3
"""
Genera los assets web de Byteploy a partir de los PNG originales (2000x2000,
fondo blanco, sin alpha). Produce versiones transparentes, recortadas y en
tinta blanca (para fondos oscuros), más favicons e íconos.

Reglas de recolor por píxel (fondo blanco):
  - saturado (max-min > SAT)  -> es AMARILLO de marca: opaco, color intacto
  - gris/negro                -> es TINTA: alpha = 255-luma; color = negro o blanco
  - blanco                    -> fondo: transparente
"""
from PIL import Image
import os

SRC = os.path.dirname(__file__)
OUT = os.path.dirname(SRC)  # assets/
SAT = 45                 # umbral de saturación para detectar amarillo
GOLD = (255, 210, 31)    # amarillo v2 (#FFD21F) al que se remapea el amarillo del logo
REF_LUMA = 214.0         # luma del amarillo puro del logo (255,219,45), referencia de escala

def load_rgb(name):
    return Image.open(os.path.join(SRC, name)).convert("RGB")

def recolor(im, ink):
    """Devuelve RGBA: fondo blanco -> transparente; tinta -> `ink`; amarillo intacto."""
    im = im.convert("RGB")
    W, H = im.size
    src = im.load()
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dst = out.load()
    for y in range(H):
        for x in range(W):
            r, g, b = src[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            if mx - mn > SAT:                       # amarillo -> oro de paleta (#EBC547)
                luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
                k = max(0.4, min(1.12, luma / REF_LUMA))   # preserva el AA (bordes más oscuros/claros)
                dst[x, y] = (min(255, int(GOLD[0] * k)),
                             min(255, int(GOLD[1] * k)),
                             min(255, int(GOLD[2] * k)), 255)
            else:                                    # gris/negro/blanco
                a = 255 - mn                         # blanco->0, negro->255
                if a <= 4:
                    continue
                dst[x, y] = (ink[0], ink[1], ink[2], a)
    return out

def content_bbox(rgba):
    return rgba.split()[3].getbbox()

def crop_pad(rgba, pad_frac=0.04, square=False):
    bb = content_bbox(rgba)
    c = rgba.crop(bb)
    w, h = c.size
    pad = int(round(max(w, h) * pad_frac))
    if square:
        side = max(w, h) + pad * 2
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(c, ((side - w) // 2, (side - h) // 2), c)
        return canvas
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    canvas.paste(c, (pad, pad), c)
    return canvas

def fit_h(rgba, h):
    w = round(rgba.width * h / rgba.height)
    return rgba.resize((w, h), Image.LANCZOS)

def fit_w(rgba, w):
    h = round(rgba.height * w / rgba.width)
    return rgba.resize((w, h), Image.LANCZOS)

def rounded_tile(bg, size, radius_frac=0.22):
    """Cuadrado de color `bg` con esquinas redondeadas, RGBA."""
    from PIL import ImageDraw
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    rad = int(size * radius_frac)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=rad, fill=bg + (255,))
    return tile

def compose_icon_on_tile(icon_light, tile_bg, size, inset_frac=0.20):
    tile = rounded_tile(tile_bg, size)
    inner = size - int(size * inset_frac * 2)
    ic = fit_h(icon_light, inner) if icon_light.height >= icon_light.width else fit_w(icon_light, inner)
    if ic.width > inner:
        ic = fit_w(icon_light, inner)
    tile.paste(ic, ((size - ic.width) // 2, (size - ic.height) // 2), ic)
    return tile

# ---------- ICON ----------
icon_rgb = load_rgb("icon-source.png")
icon_black = crop_pad(recolor(icon_rgb, (0, 0, 0)), pad_frac=0.05, square=True)
icon_white = crop_pad(recolor(icon_rgb, (255, 255, 255)), pad_frac=0.05, square=True)

fit_h(icon_black, 512).save(os.path.join(OUT, "logo-icon.png"))
fit_h(icon_white, 512).save(os.path.join(OUT, "logo-icon-light.png"))

# ---------- WORDMARK (capitalizado "Byteploy" con B = principal) ----------
word_rgb = load_rgb("wordmark-upper-source.png")
word_black = crop_pad(recolor(word_rgb, (0, 0, 0)), pad_frac=0.02)
word_white = crop_pad(recolor(word_rgb, (255, 255, 255)), pad_frac=0.02)
fit_h(word_black, 220).save(os.path.join(OUT, "wordmark.png"))
fit_h(word_white, 220).save(os.path.join(OUT, "wordmark-light.png"))

# ---------- FAVICONS / TILES (tile negro, tinta blanca + amarillo) ----------
# tile negro con B blanca+amarilla, esquinas redondeadas
for size, fname in [(512, "icon-512.png"), (180, "apple-touch-icon.png"),
                    (48, "favicon-48.png"), (32, "favicon-32.png"), (16, "favicon-16.png")]:
    compose_icon_on_tile(icon_white, (10, 10, 11), size, inset_frac=0.17).save(os.path.join(OUT, fname))

# .ico multi-tamaño
ico = compose_icon_on_tile(icon_white, (10, 10, 11), 48, inset_frac=0.17)
ico.save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# maskable (mismo tile, con más zona segura ya incluida por el inset)
compose_icon_on_tile(icon_white, (10, 10, 11), 512, inset_frac=0.22).save(os.path.join(OUT, "maskable-512.png"))

print("OK")
for f in ["logo-icon.png","logo-icon-light.png","wordmark.png","wordmark-light.png",
          "icon-512.png","apple-touch-icon.png","favicon-32.png","favicon-16.png","favicon.ico","maskable-512.png"]:
    im = Image.open(os.path.join(OUT, f))
    print(f"  {f}: {im.size} {im.mode}")
