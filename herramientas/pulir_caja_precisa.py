# -*- coding: utf-8 -*-
"""PRECISA · quita los restos de máscara del ojo de la caja.

    python3 herramientas/pulir_caja_precisa.py [--prueba]

Óscar, 30/08/2026: «cerca del 3 todas tienen una mancha blanca, revisa y
pule los pequeños detalles que no queden restos de otras máscaras».

Y no era de las esferas: la mancha está en la CAJA. Su dibujo llegó en
RGB con el damero pintado —igual que la entrega de la Bitácora— y al
recortarlo quedaron trozos de acero colgando DENTRO del hueco. El mayor
mide 14x24 px y cae justo debajo de la barra de las 3; hay siete más
pequeños repartidos, y 700 px en total de mordidas en el borde del ojo.
Como la esfera va por debajo, esos restos se ven encima de ella.

CÓMO SE QUITA, sin pintar nada: el ojo de la caja es una forma suave, sin
entrantes. Se cierra morfológicamente —el resultado es el mismo con un
elemento de 21 o de 51 px, o sea que la forma buena no tiene ningún
entrante de ese tamaño— y todo píxel de caja que caiga dentro del ojo
cerrado es un resto: se le pone el alfa a cero. No se toca ni un color.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(RAIZ, 'assets/img/precisa-2026/capas')
PIEZA = 'caja-brazalete-acero.avif'
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 95000
CIERRE = 41          # da igual 21 que 51: el ojo no tiene entrantes propios


def restos(im):
    """Los píxeles de caja que se han metido dentro del ojo."""
    a = np.asarray(im.convert('RGBA'))
    al = a[:, :, 3] > 128
    h = ndimage.binary_fill_holes(al) & ~al
    lab, n = ndimage.label(h)
    if not n:
        return np.zeros_like(al), None
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    ojo = lab == 1 + int(np.argmax(t))
    cerrado = ndimage.binary_closing(ojo, np.ones((CIERRE, CIERRE)))
    return cerrado & ~ojo, ojo


def pule(im):
    fuera, _ = restos(im)
    if not fuera.any():
        return im, 0
    a = np.asarray(im.convert('RGBA')).copy()
    a[:, :, 3][fuera] = 0
    return Image.fromarray(a), int(fuera.sum())


if __name__ == '__main__':
    prueba = '--prueba' in sys.argv
    for t in TAMANOS:
        f = os.path.join(CAPAS, str(t), PIEZA)
        if not os.path.exists(f):
            continue
        im = Image.open(f)
        limpia, n = pule(im)
        print('  %-5d %6d px de resto quitados' % (t, n))
        if prueba or not n:
            continue
        for q in CALIDADES:
            b = _io.BytesIO()
            limpia.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        open(f, 'wb').write(d)
    print('hecho' if not prueba else '(prueba: no se ha escrito nada)')
