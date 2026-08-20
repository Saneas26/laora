#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pone frontal la foto de una esfera, por muy de lado que esté hecha.

Las fotos de los proveedores nunca son frontales. Estirar la elipse a
círculo —lo que hacíamos— corrige el achatamiento pero no la
perspectiva: con la cámara inclinada, el centro del dibujo se va del
centro de la elipse (en la khaki de segundero rojo, 60 px sobre un radio
de 435) y la numeración interior sale girada respecto a la exterior.

Aquí se corrige de verdad, con una HOMOGRAFÍA de cuatro puntos: se le
dan los centros del 12, el 3, el 6 y el 9 —que en el reloj están en
cruz, a la misma distancia del eje— y se calcula la transformación que
los lleva exactamente ahí. Sale la esfera frontal, centrada en el eje de
las agujas y con el 12 arriba, todo de una vez.

Uso:
    python3 herramientas/enderezar_esfera.py esfera.png salida.png \
        --p12 616,221 --p3 772,608 --p6 349,738 --p9 220,357
"""
import argparse
import numpy as np
from PIL import Image

LADO = 1200
R_NUM = 378        # radio al que quedan los numerales grandes


def coeficientes(destino, origen):
    """Los 8 coeficientes que PIL pide para Image.transform PERSPECTIVE."""
    A, B = [], []
    for (dx, dy), (ox, oy) in zip(destino, origen):
        A.append([dx, dy, 1, 0, 0, 0, -ox * dx, -ox * dy])
        A.append([0, 0, 0, dx, dy, 1, -oy * dx, -oy * dy])
        B += [ox, oy]
    return np.linalg.solve(np.array(A, dtype=float), np.array(B, dtype=float))


def enderezar(img, p12, p3, p6, p9, lado=LADO, r=R_NUM):
    c = lado / 2
    destino = [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
    co = coeficientes(destino, [p12, p3, p6, p9])
    return img.convert('RGB').transform((lado, lado), Image.PERSPECTIVE, co, Image.BICUBIC)


def par(s):
    x, y = s.split(',')
    return float(x), float(y)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('salida')
    for n in ('12', '3', '6', '9'):
        p.add_argument('--p' + n, type=par, required=True,
                       help='centro del numeral %s, x,y' % n)
    p.add_argument('--lado', type=int, default=LADO)
    p.add_argument('--radio', type=int, default=R_NUM)
    a = p.parse_args()
    enderezar(Image.open(a.origen), a.p12, a.p3, a.p6, a.p9, a.lado, a.radio).save(a.salida)
    print(a.salida)
