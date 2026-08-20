#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cambia el color del nato SIN volver a generar la foto.

El proveedor hace la misma correa en varios colores (1005012621893442):
verde militar, negro, gris claro, beige y negro-gris. Tener una foto de
cada una no aporta nada: es el mismo tejido con el mismo tramado, la
misma luz y las mismas costuras. Solo cambia el tono.

Cómo se aísla la correa, y por qué NO por color: el tejido oliva está en
tono 42° y la piel de los pasadores en 30°, demasiado cerca para
separarlos sin comerse medio pasador. Se hace por GEOMETRÍA: es correa
todo lo que queda fuera del círculo de la caja, no es fondo y tiene
color —así el acero de las asas, que está desaturado, se queda fuera—.

Dentro de esa zona sí se distinguen tejido y piel por tono, porque ya no
hay nada más que pueda confundirse.

No se dibuja ni un píxel: se conserva el tramado, sus brillos y su
relieve; lo único que cambia es el tono.

Uso:
    python3 herramientas/recolorear_nato.py montaje.png salida.png --color negro
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

# tono, saturación y cuánto se sube o baja la luz. El verde militar es el
# original, así que no se toca.
COLORES = {
    'negro':      {'tejido': (0,   0.00, 0.42), 'piel': (0,   0.00, 0.45)},
    'gris-claro': {'tejido': (0,   0.00, 1.85), 'piel': (0,   0.00, 1.30)},
    'beige':      {'tejido': (42,  0.22, 1.85), 'piel': None},
    'negro-gris': {'tejido': (0,   0.00, 0.55), 'piel': (0,   0.00, 0.75)},
    # y la piel del khaki, que es la misma correa en tres tonos
    'marron-oscuro': {'tejido': None, 'piel': (24, 0.46, 0.46)},
    # los antes, que salen unos de otros como los natos
    'ante-camel':        {'tejido': None, 'piel': (31, 0.55, 1.55)},
    'ante-azulpetroleo': {'tejido': None, 'piel': (196, 0.62, 1.05)},
    'ante-negro':        {'tejido': None, 'piel': (0, 0.00, 0.45)},
}


def hsv(a):
    mx = a.max(axis=2); mn = a.min(axis=2); dif = mx - mn
    s = np.where(mx > 0, dif / np.maximum(mx, 1e-6), 0)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    h = np.zeros_like(mx); m = dif > 1e-6
    i = m & (mx == r); h[i] = ((g - b)[i] / dif[i]) % 6
    i = m & (mx == g); h[i] = ((b - r)[i] / dif[i]) + 2
    i = m & (mx == b); h[i] = ((r - g)[i] / dif[i]) + 4
    return h * 60, s, mx


def rgb(h, s, v):
    h = h / 60.0
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(v.shape + (3,))
    for k, (a1, b1, c1) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        sel = i == k
        out[sel] = np.stack([a1, b1, c1], axis=-1)[sel]
    return out


def correa(a, centro, radio_caja, margen=1.04, banda=False, vmax=None):
    """Máscara de la correa: fuera de la caja, con color y sin ser el fondo.

    Con las cajas de acero basta con salirse de un círculo: el metal está
    desaturado y se queda fuera solo. Con las de BRONCE no, que el bronce
    tiene tanto color como la correa y se teñía con ella.

    Lo que sí los separa es el BRILLO: el bronce es metal pulido y la
    correa, cuero mate. Con `vmax` se deja fuera todo lo que brille más
    que la correa, y así se salvan el bisel y las asas enteras sin tener
    que adivinar su contorno. Probado antes con una banda horizontal: el
    corte se veía a media correa y quedaba peor que el problema.
    """
    h, s, v = hsv(a)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    if banda:
        fuera = np.abs(yy - centro[1]) > radio_caja * margen
    else:
        fuera = ((xx - centro[0]) ** 2 + (yy - centro[1]) ** 2) > (radio_caja * margen) ** 2
    m = fuera & (s > 0.12) & ~((v > 0.72) & (s < 0.06))
    if vmax is not None:
        m &= v < vmax
    return m, h, s, v


def recolorear(img, color, centro, radio_caja, banda=False, vmax=None):
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    zona, h, s, v = correa(a, centro, radio_caja, banda=banda, vmax=vmax)
    receta = COLORES[color]
    out = a.copy()
    for parte, rango in (('tejido', (38, 70)), ('piel', (0, 38))):
        destino = receta[parte]
        if destino is None:
            continue
        m = zona & (h >= rango[0]) & (h < rango[1])
        if not m.any():
            continue
        th, ts, mult = destino
        nh = np.full_like(h, th)
        ns = np.where(ts == 0, 0.0, s / max(s[m].mean(), 1e-6) * ts)
        nv = np.clip(v * mult, 0, 1)
        nuevo = rgb(nh, np.clip(ns, 0, 1), nv)
        suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                           .filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 255
        out = out * (1 - suave[:, :, None]) + nuevo * suave[:, :, None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('salida')
    p.add_argument('--color', required=True, choices=sorted(COLORES))
    p.add_argument('--centro', default='1008,946')
    p.add_argument('--radio', type=int, default=430)
    p.add_argument('--vmax', type=float, default=None,
                   help='brillo máximo de la correa: deja fuera el metal de la caja')
    p.add_argument('--banda', action='store_true',
                   help='para cajas con color, como el bronce: la correa es lo de arriba y abajo')
    a = p.parse_args()
    cx, cy = (int(v) for v in a.centro.split(','))
    recolorear(Image.open(a.origen), a.color, (cx, cy), a.radio, a.banda, a.vmax).save(a.salida)
    print(a.salida, a.color)
