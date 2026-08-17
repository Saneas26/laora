#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alinea las cabezas del Lunar a UNA misma geometría.

Cada cabeza salió de una generación distinta, así que la caja no cae en
el mismo sitio ni mide lo mismo (hasta 13 px de desvío y 6,6% de
tamaño). Eso hace que unas encajen con la correa y otras bailen.

Esto NO retoca el dibujo: solo mueve y escala la imagen entera hasta
que la caja coincide con la de la cabeza de referencia — la misma que
se fotografió con la correa. Los originales no se tocan: el resultado
va a una carpeta nueva.

Medidas usadas (a prueba de corona y de motas):
  · centro X = punto medio del hueco entre asas (mediana de las filas
    de arriba donde la silueta son dos piezas);
  · centro Y y diámetro = extremos de la caja en la columna central,
    que no pasa por la corona ni los pulsadores.

Uso: python3 alinear_cabezas.py <carpeta_heads> <carpeta_salida> [referencia.png]
"""
from PIL import Image
import numpy as np
import sys, os, glob


def geometria(ruta):
    a = np.asarray(Image.open(ruta).convert('RGBA').getchannel('A')) > 100
    H, W = a.shape
    centros = []
    for y in range(20, H//3):
        f = np.flatnonzero(a[y])
        if len(f) < 2:
            continue
        saltos = np.diff(f)
        if saltos.max(initial=1) > 20:
            i = saltos.argmax()
            centros.append((f[i]+f[i+1])/2)
    cx = float(np.median(centros)) if centros else W/2
    col = np.flatnonzero(a[:, int(round(cx))])
    y0, y1 = col.min(), col.max()
    return cx, (y0+y1)/2.0, float(y1-y0)


def alinea(ruta, destino, ref):
    rx, ry, rd = ref
    cx, cy, d = geometria(ruta)
    k = rd/d
    im = Image.open(ruta).convert('RGBA')
    W, H = im.size
    grande = im.resize((round(W*k), round(H*k)), Image.LANCZOS)
    lienzo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lienzo.alpha_composite(grande, (round(rx - cx*k), round(ry - cy*k)))
    lienzo.save(destino)
    return dict(dx=round(rx-cx, 1), dy=round(ry-cy, 1), escala=round(k, 4))


if __name__ == '__main__':
    origen, salida = sys.argv[1], sys.argv[2]
    referencia = sys.argv[3] if len(sys.argv) > 3 else \
        'cab-acero-bnegro-agujas-plateadas.png'
    os.makedirs(salida, exist_ok=True)
    ref = geometria(os.path.join(origen, referencia))
    print(f'referencia {referencia}: centro ({ref[0]}, {ref[1]}) Ø {ref[2]}')
    for r in sorted(glob.glob(os.path.join(origen, '*.png'))):
        info = alinea(r, os.path.join(salida, os.path.basename(r)), ref)
        print(f'  {os.path.basename(r):46} {info}')
    # comprobación: todas deben quedar idénticas a la referencia
    print('\nverificación tras alinear:')
    for r in sorted(glob.glob(os.path.join(salida, '*.png'))):
        g = geometria(r)
        ok = abs(g[0]-ref[0]) <= 1 and abs(g[1]-ref[1]) <= 1 and abs(g[2]-ref[2]) <= 2
        print(f'  {"OK " if ok else "MAL"} {os.path.basename(r):46} '
              f'centro ({g[0]:.1f}, {g[1]:.1f}) Ø {g[2]:.0f}')
