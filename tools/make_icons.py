#!/usr/bin/env python3
"""Genera el ícono de la app (mancuerna naranja sobre fondo oscuro) y la pantalla de carga."""
import pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / 'android' / 'app' / 'src' / 'main' / 'res'
BG = (23, 24, 27, 255)        # --text del tema claro / fondo oscuro
ACCENT = (255, 106, 61, 255)  # --accent oscuro
SS = 4                        # supersampling

def dumbbell(size, scale=1.0, color=ACCENT):
    """Mancuerna centrada en un lienzo transparente de `size` px. `scale` = fracción del ancho que ocupa."""
    S = size * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = S * scale
    cx = cy = S / 2
    u = w / 100.0  # unidad: la mancuerna mide 100u de ancho
    r = lambda x0, y0, x1, y1, rad: d.rounded_rectangle([cx + x0*u, cy + y0*u, cx + x1*u, cy + y1*u], radius=rad*u, fill=color)
    r(-26, -5, 26, 5, 3)          # barra
    for sgn in (-1, 1):
        a, b = sorted((sgn*27, sgn*37)); r(a, -30, b, 30, 5)   # disco grande
        a, b = sorted((sgn*39, sgn*47)); r(a, -20, b, 20, 4)   # disco chico
        a, b = sorted((sgn*48, sgn*50)); r(a, -6, b, 6, 1)     # tope
    return im.resize((size, size), Image.LANCZOS)

def square_icon(size, round_=False):
    S = size * SS
    base = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    if round_:
        d.ellipse([0, 0, S - 1, S - 1], fill=BG)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=S * 0.22, fill=BG)
    base = base.resize((size, size), Image.LANCZOS)
    base.alpha_composite(dumbbell(size, 0.72 if not round_ else 0.66))
    return base

dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for name, k in dens.items():
    d = RES / f'mipmap-{name}'
    d.mkdir(parents=True, exist_ok=True)
    legacy = round(48 * k); fg = round(108 * k)
    square_icon(legacy).save(d / 'ic_launcher.png')
    square_icon(legacy, round_=True).save(d / 'ic_launcher_round.png')
    dumbbell(fg, 0.56).save(d / 'ic_launcher_foreground.png')

(RES / 'values' / 'ic_launcher_background.xml').write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#17181B</color>\n</resources>\n')

# Pantallas de carga: reemplaza cada splash.png conservando su tamaño
for p in RES.glob('drawable*/splash.png'):
    w, h = Image.open(p).size
    im = Image.new('RGBA', (w, h), (17, 18, 20, 255))
    m = round(min(w, h) * 0.32)
    im.alpha_composite(dumbbell(m, 0.9), ((w - m) // 2, (h - m) // 2))
    im.convert('RGB').save(p)

# Ícono para la tienda / README
square_icon(512).save(ROOT / 'icon.png')
print('Íconos generados')
