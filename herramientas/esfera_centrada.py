#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mete la esfera aprobada en una caja cuyo hueco viene descentrado.

Las cuatro cajas de ante llegaron con el hueco de la esfera 69 píxeles
más arriba de donde toca: el bisel medía 132 px por arriba y 267 por
abajo, el doble. Óscar lo vio a simple vista el 20/08/2026. Con la
esfera puesta en el hueco, el reloj sale con la esfera alta.

Se compensa así: la esfera se pone donde tiene que estar —centrada en
la CAJA, no en el hueco— y se agranda lo justo para que siga tapando el
hueco entero, que está corrido. El bisel queda uniforme. El precio es
que la esfera sale algo más grande que en las fotos cuyo hueco venía
bien; Óscar lo dio por bueno antes que dejar el bisel torcido.

EL DESCENTRADO NO SE PONE A MANO: se mide el anillo de metal que queda
entre la esfera y el borde de la caja en cuatro diagonales —las que no
tienen asa ni corona— y la mitad de la diferencia entre arriba y abajo
es lo que hay que bajar.

Uso:
    python3 herramientas/esfera_centrada.py caja.png esfera.png salida.png
"""
import argparse, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from logo_en_caja import disco
from caja_a_titanio import silueta

DIAGONALES = {'arriba-dcha': 60, 'abajo-dcha': 120, 'abajo-izq': 240, 'arriba-izq': 300}


def anillos(img, hueco):
    """Cuánto metal hay entre la esfera y el borde, en cada diagonal."""
    hx, hy, hr = hueco
    sil = silueta(np.asarray(img.convert('RGB')).astype(float))
    H, W = sil.shape
    fuera = {}
    for nombre, g in DIAGONALES.items():
        t = math.radians(g)
        dx, dy = math.sin(t), -math.cos(t)
        r = hr; ult = hr
        while r < hr * 2.0:
            x, y = int(hx + dx * r), int(hy + dy * r)
            if not (0 <= x < W and 0 <= y < H):
                break
            if sil[y, x]:
                ult = r
            elif r > ult + 15:
                break
            r += 1.0
        fuera[nombre] = ult - hr
    return fuera


def descentrado(a):
    """Cuánto hay que mover la esfera para que el bisel quede parejo.

    De las dos diagonales de abajo se toma la MAYOR, no la media: si un
    rayo se corta antes —una sombra, el arranque de la correa— mide de
    menos, nunca de más. En las cuatro cajas de ante, abajo-izquierda
    daba 197 donde abajo-derecha daba 270, y promediarlas se comía la
    mitad de la corrección.

    Y el desvío lateral sale solo de las dos de arriba, que son las
    limpias: abajo entra la correa.
    """
    arriba = min(a['arriba-dcha'], a['arriba-izq'])
    abajo = max(a['abajo-dcha'], a['abajo-izq'])
    return (a['arriba-izq'] - a['arriba-dcha']) / 2, (abajo - arriba) / 2


def poner(caja, esfera, centro_esfera, r_esfera, margen=6, borde=2.0):
    hx, hy, hr = disco(caja)
    a = anillos(caja, (hx, hy, hr))
    dx, dy = descentrado(a)
    # la esfera crece lo que se ha movido, para no dejar el hueco al aire
    r = int(hr + math.hypot(dx, dy) + margen)
    cx, cy, cr = centro_esfera[0], centro_esfera[1], r_esfera
    z = esfera.convert('RGB').crop((int(cx - cr), int(cy - cr), int(cx + cr), int(cy + cr)))
    z = z.resize((2 * r, 2 * r), Image.LANCZOS)
    m = Image.new('L', (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(borde))
    out = caja.convert('RGB').copy()
    out.paste(z, (int(hx + dx - r), int(hy + dy - r)), m)
    return out, {'hueco': (round(hx), round(hy), round(hr)), 'anillos': {k: round(v) for k, v in a.items()},
                 'mover': (round(dx), round(dy)), 'r': r}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('caja'); p.add_argument('esfera'); p.add_argument('salida')
    p.add_argument('--centro', default='1936,1984', help='centro del disco en la foto de la esfera')
    p.add_argument('--resfera', type=float, default=812)
    a_ = p.parse_args()
    cx, cy = (float(v) for v in a_.centro.split(','))
    img, info = poner(Image.open(a_.caja), Image.open(a_.esfera), (cx, cy), a_.resfera)
    img.save(a_.salida)
    print(a_.salida, info)
