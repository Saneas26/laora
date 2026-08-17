#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpia la máscara de una correa/brazalete del configurador.

El brazalete que venía en el paquete traía pegado un trozo de la caja
con la que se fotografió (el arco negro del bisel con «TACHYMÈTRE»).
Mientras la cabeza sea la misma no se nota, porque queda tapado; pero
con una caja más pequeña ese negro asoma.

Aquí se quita: se detecta el trozo de caja y se sustituye por más
brazalete, clonado con su periodo real, y el borde inferior del tramo
de arriba pasa a ser recto, para que entre bajo cualquier caja sin
dejar hueco. Ni un píxel inventado: todo sale del propio brazalete.

Uso: python3 limpiar_correa.py <capa.png> <salida.png>
"""
from PIL import Image
import numpy as np
import sys


def periodo(banda, minimo, maximo):
    """Cada cuántas filas se repite el dibujo del brazalete.

    El rango se acota al tamaño creíble de un eslabón (entre el 5% y el
    22% del alto de la imagen): si se deja libre, la correlación se
    engancha al rayado fino del cepillado y sale un periodo absurdo."""
    filas = banda.mean(axis=(1, 2))
    filas = filas - filas.mean()
    mejor, punto = -2.0, None
    for p in range(minimo, min(maximo, len(filas)//2)):
        v = np.corrcoef(filas[:-p], filas[p:])[0, 1]
        if v > mejor:
            mejor, punto = v, p
    return punto


def limpia(entrada, salida):
    im = Image.open(entrada).convert('RGBA')
    a = np.asarray(im).astype(int).copy()
    alto, ancho = a.shape[:2]
    alfa, lum = a[:, :, 3] > 128, a[:, :, :3].mean(axis=2)

    # el trozo de caja: filas con MUCHO negro seguido (el bisel), no las
    # sombras finas entre eslabones
    cols_all = np.flatnonzero(alfa.any(axis=0))
    xa, xb = int(cols_all.min()), int(cols_all.max())+1
    # el bisel es una banda negra que cruza casi todo el ancho; las
    # sombras entre eslabones son finas y no llegan ni a la mitad
    frac = ((alfa & (lum < 90))[:, xa:xb]).mean(axis=1)
    sucias = np.flatnonzero(frac > 0.6)
    sucias = sucias[sucias < alto//2]          # solo el tramo de arriba
    if not len(sucias):
        print('sin restos de caja'); return
    y0, y1 = int(sucias.min()), int(sucias.max())

    # ancho del brazalete (donde de verdad hay metal)
    cols = np.flatnonzero(alfa[:y0-40].any(axis=0))
    x0, x1 = int(cols.min()), int(cols.max())+1

    limpio_hasta = y0 - int(alto*0.02)         # última fila de fiar
    P = periodo(a[max(0, limpio_hasta-int(alto*0.35)):limpio_hasta, x0:x1, :3].astype(float),
                int(alto*0.05), int(alto*0.22))
    hasta = min(alto//2, y1 + int(alto*0.10))  # se prolonga bien bajo la caja

    for y in range(limpio_hasta, hasta):
        origen = y
        while origen >= limpio_hasta:
            origen -= P
        a[y, x0:x1, :3] = a[origen, x0:x1, :3]
        a[y, x0:x1, 3] = 255
        a[y, :x0, 3] = 0
        a[y, x1:, 3] = 0

    Image.fromarray(a.astype('uint8'), 'RGBA').save(salida)
    print(f'{entrada.split("/")[-1]}: quitado el trozo de caja (filas {y0}–{y1}), '
          f'brazalete prolongado hasta {hasta} con periodo {P}')


if __name__ == '__main__':
    limpia(sys.argv[1], sys.argv[2])
