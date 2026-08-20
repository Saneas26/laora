#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El logotipo que va IMPRESO en la esfera: «laOra» y debajo el modelo.

Se construye desde el wordmark oficial de la marca —el mismo PNG que
usa la cabecera de la web—, así que las letras son las de verdad y no
una imitación. Dos cosas cambian respecto al de la web:

1. EL TRIÁNGULO DE LA O. El wordmark lo lleva dorado y grande; en la
   esfera es «un pequeño detalle a las 12» (Óscar, 19/08/2026). Se
   borra el original —dilatando la máscara, o quedan los bordes suaves
   como un fantasma— y se dibuja el pequeño en su sitio.
2. EL COLOR. En la esfera todo va en PLATA monocroma, con un degradado
   vertical muy leve para que no parezca un gris plano pintado.

Uso:
    python3 herramientas/logotipo_esfera.py TRINCHERA
    python3 herramientas/logotipo_esfera.py LUNAR --salida assets/img/marca/
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WORDMARK = 'assets/img/lunar-v2/laora-wordmark-dark.png'
FUENTE = '/System/Library/Fonts/HelveticaNeue.ttc'
CX, CY, RI = 557, 185, 150          # la O del wordmark: centro y radio interior
TRIANGULO = (68, 86)                 # ancho y alto elegidos por Óscar el 19/08/2026
SEPARACION = 14                      # del borde de dentro de la O
PLATA = (232, 196)                   # degradado de arriba abajo


def sin_triangulo():
    a = np.asarray(Image.open(WORDMARK).convert('RGBA')).astype(int)
    r, b, al = a[:, :, 0], a[:, :, 2], a[:, :, 3]
    oro = ((r - b) > 25) & (al > 20)
    oro = np.asarray(Image.fromarray((oro * 255).astype(np.uint8))
                     .filter(ImageFilter.MaxFilter(7))) > 0
    a[oro] = [0, 0, 0, 0]
    return Image.fromarray(a.astype(np.uint8))


def logotipo(modelo, tam=TRIANGULO, tracking=26, cuerpo=118, sep_nombre=40):
    im = sin_triangulo()
    ancho, alto = tam
    top = CY - RI + SEPARACION
    ImageDraw.Draw(im).polygon(
        [(CX - ancho / 2, top), (CX + ancho / 2, top), (CX, top + alto)], fill=(0, 0, 0, 255))

    A = np.asarray(im).astype(float)
    h = A.shape[0]
    grad = np.repeat(np.linspace(PLATA[0], PLATA[1], h).reshape(h, 1), A.shape[1], axis=1)
    marca = Image.fromarray(np.dstack([grad, grad, grad, A[:, :, 3]]).astype(np.uint8))

    f = ImageFont.truetype(FUENTE, cuerpo, index=0)
    tmp = Image.new('RGBA', (2200, 260), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    letras = [(c, td.textlength(c, font=f)) for c in modelo]
    total = sum(w for _, w in letras) + tracking * (len(modelo) - 1)
    x = (2200 - total) / 2
    for c, w in letras:
        td.text((x, 40), c, font=f, fill=(214, 214, 214, 255))
        x += w + tracking
    nombre = tmp.crop(tmp.getbbox())

    W = max(marca.width, nombre.width)
    out = Image.new('RGBA', (W, marca.height + sep_nombre + nombre.height), (0, 0, 0, 0))
    out.alpha_composite(marca, ((W - marca.width) // 2, 0))
    out.alpha_composite(nombre, ((W - nombre.width) // 2, marca.height + sep_nombre))
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('modelo', help='TRINCHERA, LUNAR, PRECISA…')
    p.add_argument('--salida', default='assets/img/marca/')
    a = p.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    f = os.path.join(a.salida, 'logo-esfera-%s.png' % a.modelo.lower())
    logotipo(a.modelo).save(f)
    print(f)
