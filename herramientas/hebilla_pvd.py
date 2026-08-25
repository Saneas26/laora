#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiñe de PVD negro la hebilla de una correa fotografiada extendida.

La miniatura de la correa abierta se hizo con la hebilla plateada, que es
la de serie. Quien elige la «Clásica negra» tiene que verla negra: si no,
la miniatura enseña una hebilla que no es la que va a comprar.

QUÉ SE TIÑE: el metal de la hebilla y su lengüeta —claro y neutro— y solo
en la franja de arriba, que es donde vive. El pespunte también es claro y
neutro, así que se descarta por TAMAÑO con una apertura: la hebilla es una
masa ancha y el pespunte son puntadas sueltas.

QUÉ NO: la correa, el reloj y el pespunte del resto de la foto.

El color no se inventa: se mide en la caja de PVD de las fotos grandes y se
traslada conservando el relieve, igual que con las correas. Un metal pintado
de gris plano deja de parecer metal.

Uso:
    python3 herramientas/hebilla_pvd.py abierta.png caja-pvd.png salida.png
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

LUM = (0.2126, 0.7152, 0.0722)


def luminancia(a):
    return LUM[0] * a[..., 0] + LUM[1] * a[..., 1] + LUM[2] * a[..., 2]


def mascara_hebilla(a, franja=0.123, calibre=7):
    op = a[..., 3] > 200
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    mx = a[..., :3].max(2)
    m = op & (mx > 130) & (abs(R - B) < 28) & (abs(R - G) < 20)
    m[int(a.shape[0] * franja):] = False
    # El pespunte también es claro y neutro, así que la franja se corta donde
    # ACABA la hebilla y no antes: midiendo el metal claro por filas, cae en
    # seco a partir del 12 % de la altura, y lo que sigue son ya las puntadas.
    # Con el corte bien puesto no hace falta descartar por grosor —eso dejaba
    # sin teñir la lengüeta y el canto de la hebilla, que son finos—; basta
    # una limpieza suave para las motas sueltas.
    img = Image.fromarray((m * 255).astype(np.uint8))
    limpia = img.filter(ImageFilter.MinFilter(calibre)).filter(ImageFilter.MaxFilter(calibre))
    semilla = np.asarray(limpia.filter(ImageFilter.MaxFilter(calibre * 3))) > 127
    return m & semilla


def tenir(abierta, pvd):
    a = np.asarray(abierta.convert('RGBA')).astype(float)
    m = mascara_hebilla(a)
    if not m.any():
        raise SystemExit('no encuentro la hebilla')

    b = np.asarray(pvd.convert('RGBA')).astype(float)
    z = b[1900:2200, 1150:1300]
    o = z[..., 3] > 200
    dr, dg, db = z[..., 0][o].mean(), z[..., 1][o].mean(), z[..., 2][o].mean()
    dlum = luminancia(z)[o].mean()
    dstd = luminancia(z)[o].std()

    lum = luminancia(a)
    olum, ostd = lum[m].mean(), lum[m].std()
    nueva = np.clip(dlum + (lum - olum) / max(ostd, 1e-6) * dstd, 2, 235)
    base = np.stack([np.full(a.shape[:2], dr), np.full(a.shape[:2], dg),
                     np.full(a.shape[:2], db)], axis=2)
    tenido = np.clip(base * (nueva / max(dlum, 1e-6))[..., None], 0, 255)

    suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255
    out = a.copy()
    out[..., :3] = a[..., :3] * (1 - suave[..., None]) + tenido * suave[..., None]
    fuera = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    c = np.asarray(fuera).astype(float)
    print('PVD de la caja  R %3.0f G %3.0f B %3.0f' % (dr, dg, db))
    print('la hebilla queda R %3.0f G %3.0f B %3.0f  (%d px)'
          % (c[..., 0][m].mean(), c[..., 1][m].mean(), c[..., 2][m].mean(), m.sum()))
    return fuera


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('abierta'); p.add_argument('pvd'); p.add_argument('salida')
    a = p.parse_args()
    tenir(Image.open(a.abierta), Image.open(a.pvd)).save(a.salida)
    print(a.salida)
