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


def correa(a, centro, radio_caja, margen=1.04):
    """Máscara de la correa: fuera de la caja, con color y sin ser el fondo."""
    h, s, v = hsv(a)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    fuera = ((xx - centro[0]) ** 2 + (yy - centro[1]) ** 2) > (radio_caja * margen) ** 2
    return fuera & (s > 0.12) & ~((v > 0.72) & (s < 0.06)), h, s, v


def recolorear(img, color, centro, radio_caja):
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    zona, h, s, v = correa(a, centro, radio_caja)
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
    a = p.parse_args()
    cx, cy = (int(v) for v in a.centro.split(','))
    recolorear(Image.open(a.origen), a.color, (cx, cy), a.radio).save(a.salida)
    print(a.salida, a.color)
