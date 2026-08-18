#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iguala las tres tapas traseras del Lunar.

Vienen de generaciones distintas y el disco no mide lo mismo en las
tres (hasta un 2% de diferencia) ni cae en el mismo punto. Como en la
web se ven una detrás de otra en el MISMO visor, ese salto se nota al
cambiar de opción.

Aquí se corrige igual que con las cabezas: se mide el disco de cada
una, se mueve y se escala la IMAGEN ENTERA hasta la geometría de la
tapa lisa, que es la de referencia, y se asienta sobre el gris de la
casa. El dibujo no se toca.

Uso: python3 alinear_tapas.py
"""
from PIL import Image
import numpy as np
import os

ORIGEN = ('/Users/oscar/Documents/Codex/2026-08-15/per/outputs/'
          'Lunar2026/ENTREGA-CLAUDE/masters-4k/casebacks/')
DESTINO = 'masters-2026/lunar/tapas/'
GRIS = (234, 232, 232)
LADO = 4096
REFERENCIA = 'tapa-solida-acero-4k.png'
TAPAS = [REFERENCIA, 'tapa-lunar-color-4k.png', 'tapa-huella-astronauta-4k.png']


def disco(f):
    """Centro y diámetro del disco, medidos por su ancho.

    Se mide fila a fila en la mitad central y se toma la fila más
    ancha: la sombra alarga la silueta por abajo y engañaría a un
    bounding box, pero no ensancha el disco."""
    a = np.asarray(Image.open(ORIGEN + f).convert('RGB')).astype(int)
    alto, ancho = a.shape[:2]
    fondo = np.abs(a - a[8, 8]).max(axis=2) < 12
    obj = ~fondo
    anchos, centros = [], []
    for y in range(int(alto * .30), int(alto * .70)):
        xs = np.flatnonzero(obj[y])
        if len(xs) < 10:
            anchos.append(0); centros.append(0); continue
        anchos.append(xs.max() - xs.min())
        centros.append((xs.max() + xs.min()) / 2)
    i = int(np.argmax(anchos))
    d = anchos[i]
    # El centro vertical se saca del TECHO, nunca del suelo: la sombra
    # cuelga por debajo y falsearía cualquier medida de abajo. La fila
    # donde el disco alcanza la mitad de su ancho está, por geometría
    # del círculo, a 0,866 radios por encima del centro.
    techo = None
    for y in range(alto):
        xs = np.flatnonzero(obj[y])
        if len(xs) > 10 and (xs.max() - xs.min()) >= d / 2:
            techo = y
            break
    return centros[i], techo + 0.8660 * (d / 2), d


def alinea():
    os.makedirs(DESTINO, exist_ok=True)
    cx0, cy0, d0 = disco(REFERENCIA)
    print('referencia %s: centro %.1f,%.1f  Ø %d' % (REFERENCIA, cx0, cy0, d0))
    for f in TAPAS:
        cx, cy, d = disco(f)
        k = d0 / d
        im = Image.open(ORIGEN + f).convert('RGB')
        nueva = im.resize((round(LADO * k), round(LADO * k)), Image.LANCZOS)
        lienzo = Image.new('RGB', (LADO, LADO), GRIS)
        lienzo.paste(nueva, (round(cx0 - cx * k), round(cy0 - cy * k)))
        lienzo.save(DESTINO + f)
        print('%-30s Ø %d -> %d  (x%.4f), movida %+d,%+d'
              % (f, d, round(d * k), k, round(cx0 - cx * k), round(cy0 - cy * k)))


if __name__ == '__main__':
    alinea()
