# -*- coding: utf-8 -*-
"""Monta la foto de una tarjeta de la colección apilando las capas del
configurador, para que la foto que se enseña en la landing sea EXACTAMENTE
el reloj que se mete en el carrito.

El navegador pinta las capas dentro de un cuadrado: las que son más altas
que anchas —las correas, 1200x1666— van a ancho completo y centradas en
vertical, así que sobresalen por arriba y por abajo y se recortan. Esto
hace lo mismo con Pillow, y se comprobó contra las cuatro del Trinchera ya
publicadas: la diferencia media es de 1,25 sobre 255, que es el ruido del
AVIF.

⚠️ EL ORDEN DE LAS CAPAS ES EL DE LA `PILA` DE CADA MODELO, y no es el
mismo en todos: en el Lunar va correa, caja, bisel, esfera y agujas; en el
Trinchera la esfera va DEBAJO de la caja, porque el bisel le tapa el canto
como en el reloj de verdad.

    python3 herramientas/tarjeta_de_capas.py salida.avif capa1.avif capa2.avif ...
"""
import sys
from PIL import Image

FONDO = (233, 233, 231)   # el mismo crema del papel de la colección
LADO = 1200


def monta(capas, salida, fondo=FONDO, lado=LADO):
    base = Image.new('RGBA', (lado, lado), fondo + (255,))
    for f in capas:
        im = Image.open(f).convert('RGBA')
        w, h = im.size
        if w != lado:
            im = im.resize((lado, round(h * lado / w)), Image.LANCZOS)
            w, h = im.size
        base.alpha_composite(im, (0, (lado - h) // 2))
    base.convert('RGB').save(salida, quality=82)
    return salida


if __name__ == '__main__':
    print(monta(sys.argv[2:], sys.argv[1]))
