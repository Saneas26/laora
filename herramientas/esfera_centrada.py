#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mete la esfera aprobada en una caja cuyo hueco viene descentrado.

Las cuatro cajas de ante llegaron con el hueco de la esfera corrido 38
píxeles a la derecha y 113 hacia abajo respecto al centro de la caja.
Puesta la esfera en el hueco, el reloj sale con la esfera alta y a un
lado. Óscar lo vio a simple vista el 20/08/2026.

La esfera va donde tiene que ir —EN EL CENTRO DE LA CAJA— y del tamaño
que tiene que tener. Eso deja al aire una media luna del hueco, de hasta
134 píxeles, que se rellena con el propio bisel: se refleja hacia dentro
el metal que hay justo fuera del hueco, en cada dirección. El bisel es
un anillo liso con su degradado, así que el injerto no se ve.

DÓNDE ESTÁ EL CENTRO DE LA CAJA. Ni el recuadro de la silueta ni el
contorno entero sirven: las asas sobresalen, la corona sobresale y la
correa entra por arriba y por abajo tapando el borde. Se ajusta un
círculo SOLO con los cuatro arcos limpios —los flancos, entre las asas y
sin la corona—. Comprobado contra la caja que sí venía bien: da 2 y 10
píxeles de desvío, o sea nada.

Uso:
    python3 herramientas/esfera_centrada.py caja.png esfera.png salida.png
"""
import argparse, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from logo_en_caja import disco
from caja_a_titanio import silueta

# los cuatro arcos donde el borde de la caja se ve limpio, en grados
# desde las 12 y en sentido horario
ARCOS = [(48, 82), (98, 132), (228, 262), (278, 312)]
# lo que mide la esfera comparada con la caja. La foto aprobada da 0,780
# y Óscar la pidió «un pelín más grande» (20/08/2026).
PROPORCION = 0.80


def caja_redonda(img, hueco):
    """Centro y radio de la caja, por sus flancos."""
    hx, hy, hr = hueco
    sil = silueta(np.asarray(img.convert('RGB')).astype(float))
    H, W = sil.shape
    pts = []
    for lo, hi in ARCOS:
        for g in range(lo, hi + 1):
            t = math.radians(g)
            dx, dy = math.sin(t), -math.cos(t)
            r = hr; ult = None
            while r < hr * 1.9:
                x, y = int(hx + dx * r), int(hy + dy * r)
                if not (0 <= x < W and 0 <= y < H):
                    break
                if sil[y, x]:
                    ult = r
                elif ult is not None and r > ult + 10:
                    break
                r += 1.0
            if ult:
                pts.append((hx + dx * ult, hy + dy * ult))
    P = np.array(pts, float)
    A = np.stack([P[:, 0], P[:, 1], np.ones(len(P))], 1)
    c = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0]
    cx, cy = c[0] / 2, c[1] / 2
    return cx, cy, math.sqrt(c[2] + cx * cx + cy * cy)


def tapar_luna(a, hueco, caja, r_esf, borde=1.5):
    """Rellena con bisel el trozo de hueco que la esfera deja al aire."""
    hx, hy, hr = hueco
    cx, cy, _ = caja
    H, W, _ = a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    vx, vy = xx - cx, yy - cy
    d = np.hypot(vx, vy)
    ang = np.arctan2(vy, vx)
    # hasta dónde llega el hueco en cada dirección, visto desde el centro
    # de la caja: es un círculo mirado desde un punto que no es el suyo
    ex, ey = hx - cx, hy - cy
    e = math.hypot(ex, ey)
    al = ang - math.atan2(ey, ex)
    disc = hr * hr - (e * np.sin(al)) ** 2
    b = np.where(disc > 0, e * np.cos(al) + np.sqrt(np.maximum(disc, 0)), 0)
    luna = (d >= r_esf) & (d < b)
    if not luna.any():
        return a
    # el metal de fuera, reflejado hacia dentro
    d2 = np.clip(2 * b - d, 0, None)
    sx = np.clip(cx + np.cos(ang) * d2, 0, W - 1).astype(int)
    sy = np.clip(cy + np.sin(ang) * d2, 0, H - 1).astype(int)
    m = np.asarray(Image.fromarray((luna * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(borde))).astype(float) / 255
    return a * (1 - m[:, :, None]) + a[sy, sx] * m[:, :, None]


def poner(caja_img, esfera, centro_esfera, r_esfera, proporcion=PROPORCION, borde=2.0):
    hx, hy, hr = disco(caja_img)
    cx, cy, R = caja_redonda(caja_img, (hx, hy, hr))
    r = int(proporcion * R)
    a = tapar_luna(np.asarray(caja_img.convert('RGB')).astype(float),
                   (hx, hy, hr), (cx, cy, R), r)
    fondo = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    ecx, ecy, ecr = centro_esfera[0], centro_esfera[1], r_esfera
    z = esfera.convert('RGB').crop((int(ecx - ecr), int(ecy - ecr),
                                    int(ecx + ecr), int(ecy + ecr))).resize((2 * r, 2 * r), Image.LANCZOS)
    m = Image.new('L', (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(borde))
    fondo.paste(z, (int(cx - r), int(cy - r)), m)
    return fondo, {'hueco': (round(hx), round(hy), round(hr)),
                   'caja': (round(cx), round(cy), round(R)),
                   'desvío': (round(hx - cx), round(hy - cy)), 'r': r}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('caja'); p.add_argument('esfera'); p.add_argument('salida')
    p.add_argument('--centro', default='1936,1984')
    p.add_argument('--resfera', type=float, default=812)
    p.add_argument('--proporcion', type=float, default=PROPORCION)
    a_ = p.parse_args()
    cx, cy = (float(v) for v in a_.centro.split(','))
    img, info = poner(Image.open(a_.caja), Image.open(a_.esfera), (cx, cy), a_.resfera, a_.proporcion)
    img.save(a_.salida)
    print(a_.salida, info)
