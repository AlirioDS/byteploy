#!/usr/bin/env python3
"""Genera assets/founder.jpg desde founder-business-source.png.

Encuadre cuadrado centrado en el sujeto + gradación a la paleta del sitio:
sombras hacia tinta (#111114) y luces hacia papel (#F6F4EF), saturación
levemente contenida. 920px = 2x del tamaño mostrado (460px) para retina.
"""
from PIL import Image, ImageEnhance
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "founder-business-source.png")
OUT = os.path.join(HERE, "..", "founder.jpg")

INK = (17, 17, 20)
PAPER = (246, 244, 239)
SIZE = 920

im = Image.open(SRC).convert("RGB")
w, h = im.size  # 1536x1024, sujeto centrado en x~770
left = 770 - h // 2
im = im.crop((left, 0, left + h, h)).resize((SIZE, SIZE), Image.LANCZOS)

im = ImageEnhance.Color(im).enhance(0.90)

gray = im.convert("L")
hi_mask = gray.point(lambda v: 0 if v <= 150 else min(255, int((v - 150) / 105 * 140)))
lo_mask = gray.point(lambda v: 0 if v >= 110 else min(255, int((110 - v) / 110 * 120)))
im = Image.composite(Image.new("RGB", im.size, PAPER), im, hi_mask)
im = Image.composite(Image.new("RGB", im.size, INK), im, lo_mask)
im = ImageEnhance.Contrast(im).enhance(1.03)

im.save(OUT, "JPEG", quality=84, optimize=True, progressive=True)
print(OUT, os.path.getsize(OUT), "bytes")
