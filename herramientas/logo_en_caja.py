#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pone el logotipo sobre la esfera QUE YA TRAE la caja, sin sustituirla.

Es la forma que Óscar aprobó el 20/08/2026. Antes, a una caja que
llegaba con su esfera se le pegaba encima la esfera madre: se perdía
nitidez, el negro se volvía morado y el logotipo acababa veintiún
píxeles a la izquierda del 12. Si la esfera de la foto es buena, lo
único que le falta es el logotipo.

Aquí no se mide nada a ojo. De la propia foto se sacan:

- EL DISCO, rellenando desde el centro la mancha oscura.
- EL EJE 12-6, que da el giro y la escala del logotipo.
- LA LÍNEA DEL 10 Y DEL 2, que es donde va el borde de arriba del
  logotipo. Los numerales se distinguen de las agujas por su ÁNGULO y
  su RADIO: las dos son del mismo crema, pero un numeral vive pegado al
  borde y una aguja sale del centro.

Uso:
    python3 herramientas/logo_en_caja.py caja.png salida.png
    python3 herramientas/logo_en_caja.py caja.png salida.png --blancos
"""
import argparse, math, os, sys
from collections import deque
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from logo_en_esfera import poner, logotipo
from numerales_a_blanco import a_blanco


# Lo que mide el logotipo comparado con el radio de la esfera, tomado de
# la foto aprobada: 396 px de ancho sobre un disco de 812 de radio.
PROPORCION = 396 / 812


def disco(img, umbral=70, k=4):
    """Centro y radio de la esfera, por relleno desde el centro."""
    s = img.convert('RGB').resize((img.width // k, img.height // k), Image.LANCZOS)
    a = np.asarray(s).astype(float).mean(axis=2)
    L = a.shape[0]
    m = a < umbral
    vis = np.zeros_like(m)
    q = deque([(L // 2, L // 2)]); vis[L // 2, L // 2] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < L and 0 <= nx < L and m[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True; q.append((ny, nx))
    ys, xs = np.where(vis)
    return ((xs.min() + xs.max()) / 2 * k, (ys.min() + ys.max()) / 2 * k,
            ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 4 * k)


def numerales(img, centro, radio, k=4, minimo=60):
    """Las manchas de lume, con su ángulo y su radio. Sin las agujas."""
    s = img.convert('RGB').resize((img.width // k, img.height // k), Image.LANCZOS)
    a = np.asarray(s).astype(float)
    R, B = a[:, :, 0], a[:, :, 2]
    m = (a.mean(axis=2) > 140) & (R > B + 20)
    H, W = m.shape
    cx, cy = centro[0] / k, centro[1] / k
    visto = np.zeros_like(m); fuera = []
    for y in range(H):
        for x in range(W):
            if m[y, x] and not visto[y, x]:
                q = deque([(y, x)]); visto[y, x] = True; pix = []
                while q:
                    py, px = q.popleft(); pix.append((py, px))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = py + dy, px + dx
                            if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not visto[ny, nx]:
                                visto[ny, nx] = True; q.append((ny, nx))
                if len(pix) < minimo:
                    continue
                p = np.array(pix)
                mx, my = p[:, 1].mean(), p[:, 0].mean()
                r = math.hypot(mx - cx, my - cy) * k
                # un numeral vive pegado al borde; una aguja sale del centro
                if not (radio * 0.65 < r < radio * 0.92):
                    continue
                ang = (math.degrees(math.atan2(mx - cx, cy - my)) + 360) % 360
                fuera.append({'ang': ang, 'r': r,
                              'x0': p[:, 1].min() * k, 'x1': p[:, 1].max() * k,
                              'y0': p[:, 0].min() * k, 'y1': p[:, 0].max() * k})
    return fuera


def cerca(ns, grados, tol=14):
    return [n for n in ns if min(abs(n['ang'] - grados), 360 - abs(n['ang'] - grados)) < tol]


def medir(img):
    cx, cy, r = disco(img)
    ns = numerales(img, (cx, cy), r)
    def centroDe(g):
        """El centro del numeral por su RECUADRO, no por su centroide: el 12
        son dos cifras y la de la izquierda pesa menos que la otra, así que
        el centroide se corre y el eje sale torcido casi un grado y medio."""
        p = cerca(ns, g)
        if not p: raise SystemExit('no encuentro el numeral de %d°' % g)
        x0 = min(q['x0'] for q in p); x1 = max(q['x1'] for q in p)
        y0 = min(q['y0'] for q in p); y1 = max(q['y1'] for q in p)
        return (x0 + x1) / 2, (y0 + y1) / 2, y0
    x12, y12, _ = centroDe(0)
    x6,  y6,  _ = centroDe(180)
    _, _, t10 = centroDe(300)
    _, _, t2  = centroDe(60)
    return {'disco': (cx, cy, r), 'doce': (x12, y12), 'seis': (x6, y6),
            'linea': (t10 + t2) / 2}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('caja'); p.add_argument('salida')
    p.add_argument('--modelo', default='trinchera')
    p.add_argument('--blancos', action='store_true', help='pasar el lume a blanco antes')
    p.add_argument('--sat', type=float, default=0.12)
    a = p.parse_args()

    img = Image.open(a.caja)
    m = medir(img)
    cx, cy, r = m['disco']
    if a.blancos:
        img, _ = a_blanco(img, (cx, cy), r * 0.98, a.sat)

    # EL TAMAÑO DEL LOGOTIPO SE SACA DEL DISCO, no del eje 12-6. El eje
    # depende de dónde acabe exactamente cada cifra y baila un 3 % entre
    # fotos; el disco se mide igual siempre. La proporción, 0,4877 del
    # radio, es la de la foto que Óscar aprobó el 20/08/2026, y así todas
    # las de la serie llevan el logotipo del mismo tamaño.
    L = logotipo(a.modelo)
    eje = math.hypot(m['doce'][0] - m['seis'][0], m['doce'][1] - m['seis'][1])
    ancho = PROPORCION * r
    escala = ancho * 545 / (151 * eje)
    alto = L.height * ancho / L.width
    # y el borde de arriba, a la línea del 10 y del 2
    ejeY = (m['doce'][1] + m['seis'][1]) / 2
    altura = (ejeY - (m['linea'] + alto / 2)) / (eje / 2)

    out, info = poner(img, m['doce'], m['seis'], escala=escala, altura=altura, modelo=a.modelo)
    out.save(a.salida)
    print(a.salida, info, 'altura=%.3f · línea=%.0f' % (altura, m['linea']))
