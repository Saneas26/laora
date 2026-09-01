# -*- coding: utf-8 -*-
"""Monta la foto de una tarjeta de la colección apilando las capas del
configurador, para que la foto que se enseña en la landing sea EXACTAMENTE
el reloj que se mete en el carrito.

El navegador pinta las capas dentro de un cuadrado y AL 72 % (Óscar,
01/09/2026: «el reloj debe presentarse siempre más alejado con más correa
o brazalete»). Esto hace lo mismo con Pillow, así que la foto de la
landing y la del configurador son el mismo encuadre.

POR QUÉ 0,72 Y NO OTRO NÚMERO: la correa se publica en un lienzo de
1.200 x 1.666, que es 1.200 ÷ 0,72. Al 72 % del ancho del marco la correa
mide 864 x 1.200 y llega JUSTA a los bordes de arriba y de abajo: se ve
entera. Alejarse más dejaría su corte flotando dentro del cuadro.

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
# LA CÁMARA DE LA CASA. El mismo 0,72 que `.pv-capas img` en
# `assets/css/configurador-2026.css`: si un día se toca, se tocan los dos.
ESCALA = 0.72


def apila(capas, lado=LADO, fondo=FONDO, escala=ESCALA):
    """Las capas una encima de otra, centradas y a la escala de la casa.

    Todas se llevan al MISMO ancho —el del marco por la escala— y se
    centran en los dos ejes: es lo que hace el navegador, que las escala
    alrededor del centro del marco. Así ninguna se desalinea de otra,
    y la correa, que es más alta, sobresale o cabe justa según la escala.
    """
    base = Image.new('RGBA', (lado, lado), fondo + (255,))
    ancho = max(1, int(round(lado * escala)))
    for f in capas:
        # Vale una ruta o una imagen ya abierta: la Bitácora arma sus capas
        # en memoria y no quiere volver a leerlas del disco.
        im = (f if hasattr(f, 'convert') else Image.open(f)).convert('RGBA')
        w, h = im.size
        alto = int(round(h * ancho / float(w)))
        if (w, h) != (ancho, alto):
            im = im.resize((ancho, alto), Image.LANCZOS)
        base.alpha_composite(im, ((lado - ancho) // 2, (lado - alto) // 2))
    return base


def monta(capas, salida, fondo=FONDO, lado=LADO, escala=ESCALA):
    apila(capas, lado, fondo, escala).convert('RGB').save(salida, quality=82)
    return salida


if __name__ == '__main__':
    print(monta(sys.argv[2:], sys.argv[1]))
