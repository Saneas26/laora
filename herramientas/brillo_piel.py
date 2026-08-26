#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baja el brillo reventado de una correa de piel sin quitarle el charol.

EL PROBLEMA (Óscar, 26/08/2026): «lo que no me gusta es el brillo
exagerado de la piel, sobre todo en el marrón y el verde cerca de las
cajas».

Y es medible. En las tres pieles del Murph el reflejo son LOS MISMOS
35.471 píxeles, con la misma claridad y la misma saturación —0,09, o
sea, casi blanco—: el motor pinta el brillo igual y luego cambia el
color del cuero debajo. Sobre la piel negra eso pasa por charol; sobre
la marrón y la verde es una mancha blanca encima de un color saturado.
Empieza a 1.118 px del centro, que es justo donde acaba la caja: de ahí
lo de «cerca de las cajas».

QUÉ SE HACE. Dos cosas, y ninguna borra el reflejo:

  - SE RECOGE LA LUZ por encima de una rodilla. Por debajo no se toca
    nada; por encima, lo que sobra se multiplica por (1 - fuerza). El
    cuero sigue brillando, pero deja de quemarse a blanco puro.
  - SE LE DEVUELVE EL COLOR DEL CUERO. Un reflejo de verdad sobre piel
    de color no es blanco del todo: arrastra el tono de debajo. Se mezcla
    hacia el color medio de esa correa, escalado a la luz que le queda.

EL PESPUNTE SE QUEDA FUERA. El hilo blanco es igual de claro que el
reflejo y por la luz no se distinguen; se aísla con `hilo_claro` de
pespunte.py —lo claro Y cálido, crecido— y se protege. Si no, bajar el
brillo apaga la costura, que es lo único de la foto que tiene que
seguir siendo blanco.

Uso:
    python3 herramientas/brillo_piel.py foto.png salida.png \\
        --caja-por-par madre-acero.png madre-titanio.png \\
        --centro 2048,1960 --radio 800 --fuerza 0.55 --color 0.45
"""
import argparse
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pespunte import correa, hilo_claro
from titanio_del_par import donde_cambia


def color_del_cuero(a, zona, rodilla):
    """El color medio del cuero, medido donde NO está reventado."""
    cuerpo = zona & (a.mean(2) < rodilla) & (a.mean(2) > 8)
    if cuerpo.sum() < 5000:
        return None
    c = a[cuerpo].mean(axis=0)
    return c / max(c.mean(), 1e-6)


def recoger(a, zona, rodilla=150.0, fuerza=0.55, color=0.45, borde=1.2):
    L = a.mean(2)
    tono = color_del_cuero(a, zona, rodilla)
    exceso = np.clip(L - rodilla, 0, None)
    nueva = L - exceso * fuerza
    # la luz nueva, con el color que tenía el píxel
    escala = np.where(L > 1, nueva / np.maximum(L, 1e-6), 1)
    out = a * escala[:, :, None]
    if tono is not None and color > 0:
        # y mezclado hacia el color del cuero, sólo en lo que estaba alto
        cuanto = np.clip(exceso / max(255.0 - rodilla, 1), 0, 1) * color
        tinte = tono[None, None, :] * nueva[:, :, None]
        out = out * (1 - cuanto[:, :, None]) + tinte * cuanto[:, :, None]
    s = np.asarray(Image.fromarray((zona * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(borde))).astype(float) / 255
    return a * (1 - s[:, :, None]) + np.clip(out, 0, 255) * s[:, :, None]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('foto'); p.add_argument('salida')
    p.add_argument('--caja-por-par', nargs=2, metavar=('ACERO', 'TITANIO'))
    p.add_argument('--centro', default='2048,1960')
    p.add_argument('--radio', type=float, default=800)
    p.add_argument('--rodilla', type=float, default=150)
    p.add_argument('--fuerza', type=float, default=0.55)
    p.add_argument('--color', type=float, default=0.45)
    o = p.parse_args()

    im = Image.open(o.foto)
    hay_alfa = 'A' in im.getbands()
    alfa = np.asarray(im.convert('RGBA')).astype(float)[..., 3] if hay_alfa else None
    a = np.asarray(im.convert('RGB')).astype(float)
    cx, cy = (float(v) for v in o.centro.split(','))
    sin = None
    if o.caja_por_par:
        ac = np.asarray(Image.open(o.caja_por_par[0]).convert('RGB')).astype(float)
        ti = np.asarray(Image.open(o.caja_por_par[1]).convert('RGB')).astype(float)
        sin = donde_cambia(ac, ti)
    zona = correa(a, (cx, cy), o.radio, alfa=alfa, sin=sin)
    hilo = hilo_claro(a, zona)
    zona = zona & ~np.asarray(Image.fromarray((hilo * 255).astype(np.uint8))
                              .filter(ImageFilter.MaxFilter(5))).astype(bool)

    L = a.mean(2)
    antes = (zona & (L > 200)).sum()
    out = recoger(a, zona, o.rodilla, o.fuerza, o.color)
    despues = (zona & (out.mean(2) > 200)).sum()
    print('%s . correa %d px (hilo protegido %d) . quemado %d -> %d px . L max %.0f -> %.0f'
          % (o.salida, zona.sum(), hilo.sum(), antes, despues,
             L[zona].max(), out.mean(2)[zona].max()))
    out = np.clip(out, 0, 255)
    if hay_alfa:
        Image.fromarray(np.dstack([out, alfa]).astype(np.uint8), 'RGBA').save(o.salida)
    else:
        Image.fromarray(out.astype(np.uint8)).save(o.salida)
