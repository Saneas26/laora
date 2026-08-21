#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alinea las imágenes madre de las correas del Lunar a la cabeza de referencia.

Cada madre es una FOTO COMPLETA —reloj con su correa— sobre la que se
monta la cabeza elegida. Si la caja de la foto no cae donde cae la
cabeza, se pisan: asas dobles, bisel que asoma, esfera descentrada.

LA MEDIDA es el BORDE EXTERIOR DEL BISEL —donde el negro del taquímetro
acaba y empieza el metal—, buscado por rayos en tres arcos limpios
(izquierda entera y las dos diagonales de la derecha, esquivando asas y
pulsadores) y ajustado con recorte de atípicos. El taquímetro NO sirve
de referencia: la cabeza y las madres son fotos de relojes con
proporciones distintas (bisel 369 px con taquímetro 324 en la cabeza,
410 con 324 en las madres), así que igualando el taquímetro el bisel se
sale por fuera.

DOS COSAS QUE COSTARON UNA TANDA CADA UNA (22/08/2026):
1. Se parte SIEMPRE de la foto original de Óscar, no del webp ya
   alineado: encadenar reescalados emborrona y el error se acumula.
   Los originales se sacan del commit c0bf6d0 a herramientas/madres-origen/.
2. Un solo pase no basta: el remuestreo mueve el borde medido hasta 7 px.
   Se itera midiendo el resultado hasta que el radio cae a menos de
   medio píxel, y solo entonces se guarda —una única codificación—.

La piel perforada no se toca: es la foto de la que salió la cabeza.

Uso:
    python3 herramientas/alinear_madres.py            # todas
    python3 herramientas/alinear_madres.py nato       # las que casen
"""
import json, os, subprocess, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bisel_lunar import bisel_ext

MANIFEST = 'assets/img/lunar-config/manifest.json'
CABEZA_REF = 'assets/img/lunar-config/heads/cab-acero-bnegro-agujas-plateadas.webp'
ORIGENES = 'herramientas/madres-origen'      # las fotos de Óscar, sin tocar
COMMIT_ORIGEN = 'c0bf6d0'
FONDO = (234, 232, 232)
NO_TOCAR = {'piel-negra-perforada-pespunte-blanco'}


def origen(k):
    """La foto original de la correa, sacada del repo la primera vez."""
    ruta = os.path.join(ORIGENES, k + '.webp')
    if not os.path.exists(ruta):
        os.makedirs(ORIGENES, exist_ok=True)
        blob = subprocess.check_output(
            ['git', 'show', '%s:assets/img/lunar-config/straps/%s.webp' % (COMMIT_ORIGEN, k)])
        open(ruta, 'wb').write(blob)
    return Image.open(ruta)


def coloca(im, cx, cy, k, rx, ry):
    W, H = im.size
    g = im.convert('RGB').resize((round(W * k), round(H * k)), Image.LANCZOS)
    out = Image.new('RGB', (W, H), FONDO)
    out.paste(g, (round(rx - cx * k), round(ry - cy * k)))
    return out


if __name__ == '__main__':
    filtros = sys.argv[1:]
    m = json.load(open(MANIFEST))
    r = Image.open(CABEZA_REF).convert('RGBA')
    bgr = Image.new('RGBA', r.size, FONDO + (255,)); bgr.alpha_composite(r)
    rx, ry, rR, err, n = bisel_ext(bgr)
    print('cabeza de referencia: bisel centro=(%.1f,%.1f) R=%.1f (err %.1f, %d puntos)' % (rx, ry, rR, err, n))

    for k, st in m['straps'].items():
        if filtros and not any(f in k for f in filtros): continue
        if k in NO_TOCAR:
            print('%-38s es la foto de la cabeza: no se toca' % k); continue
        im0 = origen(k)
        mx, my, mR, merr, mn = bisel_ext(im0)
        if mn < 25 or merr > 8:
            print('%-38s bisel dudoso (err %.1f, %d puntos): NO se toca' % (k, merr, mn)); continue
        # Se itera sobre la ORIGINAL: cada vuelta corrige el resto que deja
        # el remuestreo, y solo se guarda la última.
        esc, cx, cy = rR / mR, mx, my
        for vuelta in range(6):
            out = coloca(im0, cx, cy, esc, rx, ry)
            ax, ay, aR, aerr, an = bisel_ext(out)
            if abs(aR - rR) < 0.5 and abs(ax - rx) < 0.5 and abs(ay - ry) < 0.5: break
            esc *= rR / aR
            cx += (ax - rx) / esc; cy += (ay - ry) / esc
        ruta = '.' + st['src'].split('?')[0]
        out.save(ruta, quality=92)
        ver = st['src'].split('?v='); v = int(ver[1]) + 1 if len(ver) > 1 else 2
        st['src'] = ver[0] + '?v=%d' % v
        st['alineada'] = ('22/08/2026: desde la foto original, por el BORDE EXTERIOR DEL BISEL. '
                          'Era (%.0f,%.0f) R=%.0f → escala %.4f; queda en (%.1f,%.1f) R=%.1f '
                          'contra la cabeza (%.0f,%.0f) R=%.0f' % (mx, my, mR, esc, ax, ay, aR, rx, ry, rR))
        print('%-38s R %.0f → %.1f (objetivo %.0f) · escala %.4f · %d vueltas · v%d'
              % (k, mR, aR, rR, esc, vuelta + 1, v))
    json.dump(m, open(MANIFEST, 'w'), ensure_ascii=False, indent=1)
