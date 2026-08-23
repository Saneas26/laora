#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centra el reloj en su lienzo. No recompone nada: mueve la imagen entera.

Los generadores devuelven el reloj donde les cae, y en el visor —que es un
cuadrado con la foto a `object-fit:contain`— un reloj a 90 px del centro se
ve con más aire a un lado que al otro. Aquí se mide el eje de verdad y se
desplaza el lienzo hasta que caiga en el medio.

EL EJE SE MIDE DOS VECES, y tienen que coincidir:

1. POR LA CORREA. Es simétrica, así que el punto medio de cada fila de
   correa es el eje. Se miden muchas filas arriba y abajo y se promedia; la
   desviación típica dice si la medida es de fiar.
2. POR LA CAJA. Las columnas altas son el cuerpo de la caja. Su punto medio
   es el mismo eje.

Se centra por el CUERPO, no por el rectángulo que ocupa todo: la corona
sobresale a un lado, y centrando el rectángulo el reloj se iría al otro.

Uso:
    python3 herramientas/centrar_lienzo.py entrada.png salida.png
"""
import argparse
import numpy as np
from PIL import Image

TOLERANCIA = 25   # px de desviación típica por encima de los cuales no me fío


def ejes(mascara, alto):
    """El eje por la correa, fila a fila, arriba y abajo."""
    medidas = []
    tramos = list(range(int(alto * .02), int(alto * .13), 40)) + \
             list(range(int(alto * .87), int(alto * .99), 40))
    for y in tramos:
        if not mascara[y].any():
            continue
        z = np.where(mascara[y])[0]
        if z.max() - z.min() > alto * .35:   # eso ya es la caja, no la correa
            continue
        medidas.append((z.min() + z.max()) / 2)
    return medidas


def centrar(origen, destino):
    im = Image.open(origen)
    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
    a = np.asarray(im)
    if a.shape[2] == 4:
        m = a[..., 3] > 10
    else:                                     # sin alfa: lo que no es fondo
        m = np.abs(a[..., :3].astype(int) - a[0, 0, :3].astype(int)).sum(2) > 30

    alto, ancho = m.shape
    medidas = ejes(m, alto)
    if not medidas:
        raise SystemExit('no encuentro la correa: mide el eje a mano')
    eje_correa, disp = float(np.mean(medidas)), float(np.std(medidas))

    columnas = np.where(m.sum(axis=0) > alto * .39)[0]
    eje_caja = (columnas.min() + columnas.max()) / 2

    print('eje por la correa: %.1f  (%d filas, desviación %.1f)'
          % (eje_correa, len(medidas), disp))
    print('eje por la caja:   %.1f' % eje_caja)
    if disp > TOLERANCIA:
        raise SystemExit('la correa no da una medida estable: revísalo a mano')
    if abs(eje_correa - eje_caja) > TOLERANCIA:
        raise SystemExit('las dos medidas no coinciden (%.0f px): revísalo a mano'
                         % abs(eje_correa - eje_caja))

    eje = (eje_correa + eje_caja) / 2
    dx = int(round(ancho / 2 - eje))
    print('desplazamiento: %+d px' % dx)

    ys, xs = np.where(m)
    if xs.min() + dx < 0 or xs.max() + dx > ancho - 1:
        raise SystemExit('al mover se saldría del lienzo: hay que reencuadrar')

    fuera = Image.new(im.mode, im.size, (0, 0, 0, 0) if im.mode == 'RGBA'
                      else tuple(a[0, 0, :3]))
    fuera.paste(im, (dx, 0))
    fuera.save(destino)

    # comprobación: vuelvo a medir sobre lo guardado
    b = np.asarray(Image.open(destino).convert('RGBA'))[..., 3] > 10
    m2 = ejes(b, alto)
    print('comprobado en el fichero guardado: eje %.1f (centro %d)'
          % (float(np.mean(m2)), ancho // 2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen')
    p.add_argument('destino')
    centrar(*vars(p.parse_args()).values())
