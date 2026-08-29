#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · ¿ENTRA LA CORREA EN LAS ASAS?

EL PROBLEMA (Óscar, 29/08/2026): «en el lunar ya tenemos todos los
brazaletes pero los de acero no cuadran con las asas».

La correa va DETRÁS de la caja, así que lo que se pasa del hueco queda
tapado por las asas y no se ve; lo que se queda CORTO sí se ve, y se ve
como una rendija de fondo entre el asa y el brazalete. Por eso no se mide
«el ancho de la correa»: se mide, FILA A FILA de las asas, si la correa
llega de canto a canto.

CÓMO SE MIDE
  1. De la caja se sacan las filas de asa: las que tienen DOS tramos de
     material con un hueco en medio. Ese hueco es lo que hay que tapar.
  2. De la correa se mira, en esas mismas filas, hasta dónde llega por la
     izquierda y por la derecha.
  3. Se apunta lo que FALTA por cada lado. Cero es que entra.

Se mide sobre el AVIF publicado de 1.600 px, que es el que ve el cliente.

Uso:
    python3 herramientas/auditar_correas.py
    python3 herramientas/auditar_correas.py --caja 22-caja-pvd-negra
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(RAIZ, 'assets/img/lunar-2026/capas/1600')
CORREAS = os.path.join(RAIZ, 'assets/img/componentes/correas/1600')
ALFA = 24          # a partir de aquí se considera que hay material


def mascara(ruta):
    im = Image.open(ruta).convert('RGBA')
    return np.array(im)[:, :, 3] > ALFA


def filas_de_asa(caja):
    """Para cada fila de ASA: (fila, izq, der), los cantos INTERIORES.

    ⚠️ NO VALE con «dos tramos y un hueco en medio». Entre las dos asas, la
    caja es un aro: sus filas centrales tienen también dos tramos —el canto
    izquierdo y el derecho— con la ESFERA en medio, y la esfera no la tapa la
    correa, la tapa la esfera. Contando aquellas salían 956 filas de asa y un
    «hueco» de 878 px, que es el diámetro del cristal.

    Las asas son las que tienen el hueco DONDE Y COMO TOCA: 1.324 px
    centrados en x = 2054 del lienzo de 4.096, que a 1.600 son 517 px de
    543,7 a 1.060,9. Es el contrato con el que se publican las piezas
    (`herramientas/publicar_componente.py`), no una medida a ojo."""
    escala = caja.shape[1] / 4096.0
    # ⚠️ LA CAJA ENCOGIÓ UN 3 %% EL 29/08/2026 (Óscar: la correa de 20 mm
    # manda y es la misma para todos los relojes; lo que se ajusta es la
    # caja). Las asas de 1392–2716 pasaron a 1412–2696, encogidas
    # alrededor del eje 2047,5. El hueco queda en 1284 px.
    IZQ, DER = 1411.7 * escala, 2696.0 * escala
    HOLGURA = 10
    out = []
    for y in range(caja.shape[0]):
        idx = np.where(caja[y])[0]
        if len(idx) < 2:
            continue
        cortes = np.where(np.diff(idx) > 1)[0]
        tramos = np.split(idx, cortes + 1)
        if len(tramos) != 2:
            continue
        izq, der = int(tramos[0][-1]), int(tramos[1][0])
        if abs(izq - IZQ) > HOLGURA or abs(der - DER) > HOLGURA:
            continue
        out.append((y, izq, der))

    # ⚠️ Y NI ASÍ VALEN TODAS. En mitad de la caja hay filas sueltas que dan
    # la misma medida por casualidad —el perfil del cuerpo, la corona— y
    # ninguna correa las tapa porque ahí no hay asa que tapar: son 21 filas
    # que hacían que las 39 correas salieran suspendidas incluso después de
    # encajarlas. Las asas son las de los DOS EXTREMOS: se corta en el primer
    # salto grande contando desde arriba y desde abajo.
    if not out:
        return out
    ys = [y for y, _i, _d in out]
    SALTO = max(40, caja.shape[0] // 40)
    fin_arriba = ys[0]
    for a, b in zip(ys, ys[1:]):
        if b - a > SALTO:
            break
        fin_arriba = b
    ini_abajo = ys[-1]
    for a, b in zip(reversed(ys[:-1]), reversed(ys)):
        if b - a > SALTO:
            break
        ini_abajo = a
    return [(y, i, d) for y, i, d in out if y <= fin_arriba or y >= ini_abajo]


def falta(correa, asas, alto_caja):
    """Cuánto se queda corta la correa por cada lado, en píxeles.

    UNA CORREA PUEDE VENIR EN LIENZO ALTO (4096x5688, ver
    publicar_componente.py): entonces sus filas no son las de la caja.
    El eje comparte descentrado en los dos lienzos, así que la fila
    equivalente es la de la caja más la mitad de la diferencia de altos."""
    desfase = (correa.shape[0] - alto_caja) // 2
    izq_max = der_max = 0
    filas_vacias = 0
    for y, izq, der in asas:
        idx = np.where(correa[y + desfase])[0]
        if not len(idx):
            filas_vacias += 1
            continue
        izq_max = max(izq_max, int(idx[0]) - izq)      # >0: no llega al asa
        der_max = max(der_max, der - int(idx[-1]))
    return izq_max, der_max, filas_vacias


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--caja', default='01-caja-acero')
    ap.add_argument('--solo', default='')
    o = ap.parse_args()

    caja = mascara(os.path.join(CAPAS, o.caja + '.avif'))
    asas = filas_de_asa(caja)
    if not asas:
        sys.exit('no encuentro las asas en ' + o.caja)
    arriba = [a for a in asas if a[0] < caja.shape[0] / 2]
    abajo = [a for a in asas if a[0] >= caja.shape[0] / 2]
    hueco = max(d - i for _y, i, d in asas)
    print('caja %s · %d filas de asa (%d arriba, %d abajo) · hueco máximo %d px'
          % (o.caja, len(asas), len(arriba), len(abajo), hueco))
    print()

    nombres = sorted(f[:-5] for f in os.listdir(CORREAS) if f.endswith('.avif'))
    if o.solo:
        nombres = [n for n in nombres if o.solo in n]

    malas = []
    print('%-46s %7s %7s %7s  %s' % ('pieza', 'izq', 'der', 'vacías', ''))
    print('-' * 82)
    for n in nombres:
        c = mascara(os.path.join(CORREAS, n + '.avif'))
        i, d, v = falta(c, asas, caja.shape[0])
        peor = max(i, d)
        marca = 'entra' if peor <= 0 and not v else ('SE VE EL FONDO: %d px' % peor)
        if v:
            marca += ' · %d filas de asa SIN CORREA' % v
        if peor > 0 or v:
            malas.append((n, i, d, v))
        print('%-46s %7d %7d %7d  %s' % (n, max(i, 0), max(d, 0), v, marca))
    print()
    print('%d de %d no tapan el hueco.' % (len(malas), len(nombres)))


if __name__ == '__main__':
    main()
