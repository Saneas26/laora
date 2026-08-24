#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pasa a blanco los numerales crema de una esfera, y sus agujas con ellos.

El proveedor hace la esfera del Murph con los numerales en crema o en
blanco (1005005589112497, «dial A» y «dial B»). Es la misma esfera: lo
único que cambia es el tono del lume. Su foto de la variante blanca
viene tan inclinada, y con otra esfera metida en el encuadre, que
enderezarla no da nada aprovechable — así que la blanca se DERIVA de la
crema, igual que los colores del nato.

Qué se tiñe y qué no, que es lo delicado:
- SÍ los numerales y las agujas, que son lo único crema de la esfera.
- NO el logotipo, que va en plata y por tanto sin color.
- NO los índices de los minutos, que ya son blancos.
Basta con exigir color —saturación— y quedarse dentro del disco.

Uso:
    python3 herramientas/numerales_a_blanco.py crema.png blanca.png --centro 600,600 --radio 490
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter


def a_blanco(img, centro, radio, sat_min=0.18, luz=1.12, fuerza=1.0):
    """`fuerza` mezcla entre el crema original (0) y el blanco (1), para
    poder dejarlo «un poco más blanco» en vez de blanco del todo."""
    # EL ALFA SE CONSERVA (24/08/2026). Con convert('RGB') a secas, un máster
    # de fondo transparente sale recortado sobre negro y hay que rehacerlo
    # entero. Es la misma trampa que tenía foto_a_web.py.
    alfa = img.getchannel('A') if 'A' in img.getbands() else None
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    crema = (sat > sat_min) & (r >= b) & (g >= b) & (mx > 0.20)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    crema &= ((xx - centro[0]) ** 2 + (yy - centro[1]) ** 2) < radio ** 2

    suave = np.asarray(Image.fromarray((crema * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.6))).astype(float) / 255
    # a blanco conservando la luz de cada píxel: el relieve del lume se queda
    gris = np.clip(mx * luz, 0, 1)[:, :, None]
    m = (suave * fuerza)[:, :, None]
    out = a * (1 - m) + np.repeat(gris, 3, axis=2) * m
    fuera = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    if alfa is not None:
        fuera = fuera.convert('RGBA')
        fuera.putalpha(alfa)
    return fuera, int(crema.sum())


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('salida')
    p.add_argument('--centro', required=True); p.add_argument('--radio', type=float, required=True)
    p.add_argument('--sat', type=float, default=0.18)
    p.add_argument('--luz', type=float, default=1.12)
    p.add_argument('--fuerza', type=float, default=1.0,
                   help='0 = como está, 1 = blanco del todo')
    a = p.parse_args()
    cx, cy = (float(v) for v in a.centro.split(','))
    img, n = a_blanco(Image.open(a.origen), (cx, cy), a.radio, a.sat, a.luz, a.fuerza)
    img.save(a.salida)
    print(a.salida, '· píxeles pasados a blanco:', n)
