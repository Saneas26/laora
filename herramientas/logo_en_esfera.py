#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pone el logotipo de laOra en la esfera de un proveedor. Sin IA.

El logotipo NO se dibuja ni se genera: se recorta de una foto YA
APROBADA —donde está en plata, con su relieve y su luz— y se compone
sobre la esfera nueva. Por eso no puede salir mal: es el mismo logo,
píxel a píxel, solo escalado y girado.

Tres cosas que hay que hacer bien y que aquí están resueltas:

1. EL GIRO. La esfera del proveedor casi nunca sale recta en la foto.
   Se mide con el eje 12-6 (los dos numerales grandes de lume) y el
   logotipo se gira lo mismo, para que no quede torcido respecto a la
   esfera.
2. LA ESCALA. Se toma del mismo eje 12-6: la proporción entre el ancho
   del logotipo y esa distancia es la misma en las dos fotos.
3. LA MÁSCARA. El logotipo va IMPRESO en la esfera, así que tiene que
   quedar DEBAJO de las agujas y de los numerales. Donde el fondo de la
   foto es claro no se pinta nada, y la aguja pasa por encima como en
   el reloj de verdad.

Uso:
    python3 herramientas/logo_en_esfera.py esfera.png salida.png \
        --doce 565,216 --seis 408,763
"""
import argparse, math
import numpy as np
from PIL import Image, ImageFilter

# El logotipo se CONSTRUYE con logotipo_esfera.py a partir del wordmark
# oficial de la marca. Antes se recortaba de una foto aprobada, pero
# aquellas fotos traían el triángulo de la O desproporcionado (Óscar,
# 19/08/2026): es un detalle pequeño a las 12, no medio interior de la O.
LOGO = 'assets/img/marca/logo-esfera-{modelo}.png'
ANCHO_FUENTE = 151                      # px que medía el logo en la foto aprobada
EJE_FUENTE = 545                         # px que medía ahí el eje 12-6
ALTURA = 0.34                            # a qué fracción del radio va, sobre el centro


def logotipo(modelo='trinchera'):
    """El logotipo en plata del modelo, ya montado con su nombre debajo."""
    return Image.open(LOGO.format(modelo=modelo)).convert('RGBA')


def poner(esfera, doce, seis, escala=1.12, altura=ALTURA, modelo='trinchera'):
    E = np.asarray(esfera.convert('RGB')).astype(float)
    (x12, y12), (x6, y6) = doce, seis
    cx, cy = (x12 + x6) / 2, (y12 + y6) / 2
    ang = math.degrees(math.atan2(x12 - x6, y6 - y12))
    eje = math.hypot(x12 - x6, y12 - y6)

    L = logotipo(modelo)
    ancho = int(ANCHO_FUENTE * (eje / EJE_FUENTE) * escala)
    alto = int(L.height * ancho / L.width)
    # PREMULTIPLICAR ANTES DE REDUCIR. Si no, el color de las zonas
    # transparentes se mezcla en el borde y el logotipo sale con un halo
    # plateado alrededor, como despegado de la esfera.
    n = np.asarray(L).astype(float)
    n[:, :, :3] *= (n[:, :, 3:4] / 255.0)
    pm = Image.fromarray(n.astype(np.uint8)).resize((ancho, alto), Image.LANCZOS)
    pm = pm.rotate(-ang, resample=Image.BICUBIC, expand=True)
    q = np.asarray(pm).astype(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        q[:, :, :3] = np.where(q[:, :, 3:4] > 0, q[:, :, :3] * 255.0 / q[:, :, 3:4], 0)
    capa = Image.fromarray(np.clip(q, 0, 255).astype(np.uint8))

    r = eje / 2 * altura
    rad = math.radians(ang)
    ox = int(cx + r * math.sin(rad) - capa.width / 2)
    oy = int(cy - r * math.cos(rad) - capa.height / 2)

    fondo = E[oy:oy + capa.height, ox:ox + capa.width].mean(axis=2)
    tapa = np.clip((fondo - 45) / 55, 0, 1)
    tapa = np.asarray(Image.fromarray((tapa * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(1.2))).astype(float) / 255
    c = np.asarray(capa).astype(float)
    c[:, :, 3] *= (1 - tapa)

    out = esfera.convert('RGBA')
    out.alpha_composite(Image.fromarray(c.astype(np.uint8)), (ox, oy))
    return out.convert('RGB'), {'giro': round(ang, 1), 'eje': round(eje), 'logo': capa.size}


def par(s):
    x, y = s.split(',')
    return float(x), float(y)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('esfera'); p.add_argument('salida')
    p.add_argument('--doce', type=par, required=True, help='centro del numeral 12, x,y')
    p.add_argument('--seis', type=par, required=True, help='centro del numeral 6, x,y')
    p.add_argument('--escala', type=float, default=1.12)
    p.add_argument('--altura', type=float, default=ALTURA)
    p.add_argument('--modelo', default='trinchera')
    a = p.parse_args()
    img, info = poner(Image.open(a.esfera), a.doce, a.seis, a.escala, a.altura, a.modelo)
    img.save(a.salida)
    print(a.salida, info)
