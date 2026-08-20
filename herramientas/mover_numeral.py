#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Acerca o aleja un numeral del centro de la esfera, en su propia diagonal.

Las esferas del proveedor no siempre reparten bien la numeración de 13 a
24: en la khaki, el 16 queda más suelto respecto al 4 de lo que quedan
el 15 con el 3 o el 17 con el 5. Esto lo mueve por su radio, que es la
única dirección en la que se puede mover un numeral de reloj sin que
deje de marcar su hora.

No se redibuja nada: se recorta el numeral tal cual, se pega desplazado
y el hueco que deja se tapa con el propio fondo de la esfera —la mediana
de lo oscuro de alrededor—, que ahí es negro mate y uniforme.

Uso:
    python3 herramientas/mover_numeral.py esfera.png salida.png \
        --hora 4 --radio 253 --centro 600,600 --acercar 35
"""
import argparse, math
import numpy as np
from PIL import Image, ImageFilter


def mover(img, centro, hora, radio, acercar, ventana=52, umbral=150):
    a = np.asarray(img.convert('RGB')).astype(float)
    cx, cy = centro
    th = math.radians(hora * 30)
    x, y = cx + radio * math.sin(th), cy - radio * math.cos(th)
    x0, y0 = int(x - ventana), int(y - ventana)
    x1, y1 = int(x + ventana), int(y + ventana)

    trozo = a[y0:y1, x0:x1].copy()
    claro = trozo.mean(axis=2) > umbral
    if not claro.any():
        raise SystemExit('no encuentro el numeral en esa ventana')

    # el fondo con el que se tapa el hueco: la mediana de lo oscuro de al lado
    fondo = np.median(a[y0:y1, x0:x1][~claro], axis=0)

    # borrar el numeral de su sitio, con el borde difuminado para que no
    # se note el parche
    m = np.asarray(Image.fromarray((claro * 255).astype(np.uint8))
                   .filter(ImageFilter.MaxFilter(5))
                   .filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 255
    a[y0:y1, x0:x1] = trozo * (1 - m[:, :, None]) + fondo[None, None, :] * m[:, :, None]

    # y pegarlo desplazado hacia AFUERA por su radio (acercándolo al
    # numeral grande, que está más lejos del centro)
    dx = int(round(acercar * math.sin(th)))
    dy = int(round(-acercar * math.cos(th)))
    m2 = np.asarray(Image.fromarray((claro * 255).astype(np.uint8))
                    .filter(ImageFilter.GaussianBlur(0.6))).astype(float) / 255
    destino = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    a[y0 + dy:y1 + dy, x0 + dx:x1 + dx] = destino * (1 - m2[:, :, None]) + trozo * m2[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('salida')
    p.add_argument('--hora', type=float, required=True)
    p.add_argument('--radio', type=float, required=True)
    p.add_argument('--centro', required=True)
    p.add_argument('--acercar', type=float, required=True, help='px hacia afuera')
    p.add_argument('--ventana', type=int, default=52)
    a = p.parse_args()
    cx, cy = (float(v) for v in a.centro.split(','))
    mover(Image.open(a.origen), (cx, cy), a.hora, a.radio, a.acercar, a.ventana).save(a.salida)
    print(a.salida)
