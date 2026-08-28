#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encaja una correa o un brazalete en el hueco entre las asas de la caja.

EL PROBLEMA. La correa se dibuja por su cuenta, sin la caja delante, así
que llega con su propio tamaño. Medido, el brazalete de acero entra en
las asas con 1.008 px de ancho cuando el hueco mide 1.324, y además
cargado hacia la izquierda: por los dos lados asomaba el fondo entre el
asa y el brazalete, y eso no parece un reloj, parece un recorte mal
pegado.

LO QUE SOBRA NO SE VE, LO QUE FALTA SÍ. La correa va DETRÁS de la caja,
así que todo lo que se pase del hueco queda tapado por las asas. Por eso
no hay que cuadrarla al milímetro: basta con agrandarla hasta que en
ninguna fila de las asas se quede corta, y dejar que el resto se esconda.

CÓMO SE BUSCA EL TAMAÑO. Se prueban escalas de menos a más y se coge LA
PRIMERA que tapa el hueco en todas las filas de las asas con un margen;
así se deforma lo mínimo. Para cada escala se prueban también los
desplazamientos laterales, porque agrandar sin mover no arregla el que
venga descentrado.

SE AGRANDA POR IGUAL A LO ANCHO Y A LO ALTO, que estirar sólo a lo ancho
dejaría los eslabones más gordos que largos y eso se nota. Y cada tira
—la de arriba y la de abajo— se agranda desde SU EXTREMO DE DENTRO, el
que se mete debajo de la caja: así ese extremo se queda donde está y la
tira crece hacia fuera, hasta salirse del lienzo, que es justo lo que
tiene que hacer.

⚠️ ESTO NO ARREGLA UNA CORREA MAL DIBUJADA, la estira. Si hace falta
agrandarla mucho, sus eslabones acaban más grandes de lo que les tocaría
al lado de una caja de 40 mm. El programa dice cuánto ha tenido que
agrandar para que se pueda decidir si compensa pedirla bien.

Uso:
    python3 herramientas/encajar_correa.py brazalete.png caja.png salida.png
"""
import argparse
import sys

import numpy as np
from PIL import Image

MARGEN = 6        # px que se le exige meter por debajo de cada asa
PASO = 0.01       # de cuánto en cuánto se prueban las escalas
TOPE = 1.60       # no se agranda más que esto sin protestar


def tiras(m):
    """Los tramos de filas con contenido: la de arriba y la de abajo."""
    filas = np.where(m.any(axis=1))[0]
    if not len(filas):
        return []
    cortes = np.where(np.diff(filas) > 1)[0]
    return [(int(t[0]), int(t[-1])) for t in np.split(filas, cortes + 1)]


def hueco_asas(caja):
    """Para cada fila, el canto interior de las dos asas; None si no hay dos."""
    fuera = {}
    for y in range(caja.shape[0]):
        i = np.where(caja[y])[0]
        if not len(i):
            continue
        c = np.where(np.diff(i) > 1)[0]
        bl = [b for b in np.split(i, c + 1) if len(b) > 6]
        if len(bl) == 2:
            fuera[y] = (int(bl[0][-1]), int(bl[-1][0]))
    return fuera


def bordes(m, y0, y1):
    """El canto izquierdo y el derecho de la tira, fila a fila."""
    fuera = {}
    for y in range(y0, y1 + 1):
        i = np.where(m[y])[0]
        if len(i):
            fuera[y] = (int(i.min()), int(i.max()))
    return fuera


def tapa(bord, huecos, filas, s, dx, ancla_x, ancla_y, margen):
    """¿Con esta escala y este desplazamiento se tapa el hueco en todas las filas?"""
    for y in filas:
        hi, hd = huecos[y]
        # de dónde sale esta fila de la pantalla en la imagen original
        oy = int(round(ancla_y + (y - ancla_y) / s))
        b = bord.get(oy)
        if b is None:
            return False
        izq = ancla_x + (b[0] - ancla_x) * s + dx
        der = ancla_x + (b[1] - ancla_x) * s + dx
        if izq > hi - margen or der < hd + margen:
            return False
    return True


def mueve(im, s, dx, ancla_x, ancla_y):
    """Agranda `s` veces alrededor del ancla y desplaza `dx` a lo ancho."""
    a = 1.0 / s
    c = ancla_x - (ancla_x + dx) / s
    f = ancla_y - ancla_y / s
    return im.transform(im.size, Image.AFFINE, (a, 0, c, 0, a, f), Image.BICUBIC)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('correa')
    ap.add_argument('caja')
    ap.add_argument('salida')
    ap.add_argument('--margen', type=float, default=MARGEN)
    o = ap.parse_args()

    co = Image.open(o.correa).convert('RGBA')
    m = np.asarray(co)[..., 3] > 128
    caja = np.asarray(Image.open(o.caja).convert('RGBA'))[..., 3] > 128
    huecos = hueco_asas(caja)

    fuera = Image.new('RGBA', co.size, (0, 0, 0, 0))
    for y0, y1 in tiras(m):
        arriba = y0 < co.size[1] / 2
        # las filas de asa que le tocan a esta tira: las que la tira tiene que tapar
        filas = [y for y in huecos if (y < y1 if arriba else y > y0)]
        # sólo las del tramo de asa, no las del cuerpo de la caja: se cortan
        # donde el hueco deja de existir seguido
        filas = sorted(filas)
        if not filas:
            continue
        seg = [filas[0]]
        for y in filas[1:]:
            if y - seg[-1] > 1:
                if arriba:
                    break            # el primer tramo es el de las asas de arriba
                seg = [y]            # abajo interesa el último
            seg.append(y)
        filas = seg
        # el extremo de DENTRO de la tira, el que se mete bajo la caja
        ancla_y = y1 if arriba else y0
        ancla_x = sum(huecos[filas[0]]) / 2.0
        bord = bordes(m, y0, y1)

        elegido = None
        s = 1.0
        while s <= TOPE + 1e-9 and elegido is None:
            for dx in range(-160, 161, 2):
                if tapa(bord, huecos, filas, s, dx, ancla_x, ancla_y, o.margen):
                    elegido = (s, dx)
                    break
            s += PASO
        if elegido is None:
            sys.exit('la tira y %d-%d no tapa el hueco ni agrandándola %.0f %%'
                     % (y0, y1, (TOPE - 1) * 100))
        s, dx = elegido
        print('tira %s (y %4d-%4d): agrandar %.0f %% y mover %+d px  '
              '[asas de la fila %d a la %d, ancla %.0f,%d]'
              % ('de arriba' if arriba else 'de abajo', y0, y1,
                 (s - 1) * 100, dx, filas[0], filas[-1], ancla_x, ancla_y))

        sola = np.asarray(co).copy()
        sola[:y0] = 0
        sola[y1 + 1:] = 0
        fuera.alpha_composite(mueve(Image.fromarray(sola), s, dx, ancla_x, ancla_y))

    fuera.save(o.salida)
    print('escrita en ' + o.salida)
