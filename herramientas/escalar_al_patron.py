#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pone un reloj a la MISMA escala que otro. No recompone nada: agranda o
encoge la imagen entera y la vuelve a encuadrar en su lienzo.

POR QUÉ HACE FALTA. El generador no siempre devuelve el reloj al mismo
tamaño: el 26/08/2026 la madre del Murph con numerales blancos vino con la
caja a 1.680 px y la de numerales crema a 1.330, un 21 % más pequeña. En el
visor, que ajusta la foto al alto, eso se ve como que el reloj ENCOGE al
cambiar de esfera.

POR QUÉ NO PIERDE CALIDAD. De cada máster se publican 480, 1.200 y 1.600 px
del lienzo entero (laora-formato-imagen-web). Con la caja al 41 % del ancho,
en el tamaño mayor ocupa unos 650 px. Aunque aquí se agrande de 1.330 a
1.680, lo que se publica sigue siendo una REDUCCIÓN de la fuente original,
así que el resultado no se ablanda. Si algún día el máster hiciera falta a
tamaño completo, se pide de nuevo al generador.

LA MEDIDA ES EL CUERPO DE LA CAJA, no el rectángulo que ocupa todo: la
corona sobresale a un lado y la correa se sale del lienzo, así que ni una
cosa ni la otra sirven de referencia. Se toman las columnas y las filas con
más del 30 % de píxeles opacos, que es el cuerpo.

Que la correa se salga del lienzo al agrandar es NORMAL y es lo que hace el
patrón: en la madre buena el contenido va de y=47 a y=4075, o sea, cortada
arriba y abajo. Lo que no puede salirse es la caja, y eso sí se comprueba.

Uso:
    python3 herramientas/escalar_al_patron.py entrada.png patron.png salida.png
"""
import argparse
import numpy as np
from PIL import Image


def cuerpo(a):
    """El DISCO DE LA ESFERA: radio y centro.

    La primera versión medía el cuerpo de la caja con un umbral sobre el alto
    del lienzo —columnas con más del 30 % de píxeles opacos—, y eso NO vale
    aquí: al agrandar la foto el reloj llena más lienzo, más columnas pasan el
    umbral y la misma caja se mide más ancha. Escalando con esa medida se
    pasaba de largo (1.804 px pedidos 1.680).

    La esfera no tiene ese problema: es un disco negro y su radio se encuentra
    saliendo del centro hasta que el anillo deja de ser mayoritariamente
    oscuro. Es la misma medida en cualquier escala.
    """
    op = a[..., 3] > 200
    if not op.any():
        raise SystemExit('la imagen está vacía')
    ys, xs = np.where(op)
    h, w = op.shape
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    # el centro: el punto medio de las columnas y filas más llenas, que es la caja
    col = op.sum(0); fil = op.sum(1)
    cx = float(np.average(np.arange(w), weights=(col > col.max() * .75)))
    cy = float(np.average(np.arange(h), weights=(fil > fil.max() * .75)))
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    paso = max(2, int(min(h, w) / 800))
    r = None
    for k in range(int(min(h, w) * .04), int(min(h, w) * .45), paso):
        anillo = (d >= k) & (d < k + paso) & op
        if anillo.sum() and (L[anillo] < 60).mean() < 0.5:
            r = k
            break
    if r is None:
        raise SystemExit('no encuentro el disco de la esfera')
    return float(r), cx, cy


def escalar(origen, patron, destino):
    im = Image.open(origen).convert('RGBA')
    a = np.asarray(im)
    b = np.asarray(Image.open(patron).convert('RGBA'))
    if im.size != Image.open(patron).size:
        raise SystemExit('el lienzo tiene que ser el mismo en las dos')

    anc, cx, cy = cuerpo(a)
    anc_p, cx_p, cy_p = cuerpo(b)
    k = anc_p / anc
    print('esfera de la foto: %4.0f px de radio · centro (%.0f, %.0f)' % (anc, cx, cy))
    print('esfera del patrón: %4.0f px de radio · centro (%.0f, %.0f)' % (anc_p, cx_p, cy_p))
    print('factor:            %.4f' % k)
    if abs(k - 1) < 0.01:
        print('ya está a la escala buena: no toco nada')
        im.save(destino)
        return

    w, h = im.size
    grande = im.resize((int(round(w * k)), int(round(h * k))), Image.LANCZOS)
    # el centro de la caja, donde lo tiene el patrón
    dx = int(round(cx_p - cx * k))
    dy = int(round(cy_p - cy * k))
    fuera = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    fuera.paste(grande, (dx, dy))
    fuera.save(destino)

    # comprobación sobre lo guardado: la caja tiene que caber entera
    c = np.asarray(Image.open(destino).convert('RGBA'))
    anc2, cx2, cy2 = cuerpo(c)
    op = c[..., 3] > 200
    ys, xs = np.where(op)
    print('queda:             %4.0f px de radio · centro (%.0f, %.0f)' % (anc2, cx2, cy2))
    if xs.min() <= 0 or xs.max() >= w - 1:
        raise SystemExit('la CAJA se sale por un lado: hay que pedirla de nuevo')
    print('contenido: x[%d..%d] y[%d..%d]  (la correa cortada arriba y abajo es lo normal)'
          % (xs.min(), xs.max(), ys.min(), ys.max()))
    print(destino)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('patron'); p.add_argument('salida')
    a = p.parse_args()
    escalar(a.origen, a.patron, a.salida)
