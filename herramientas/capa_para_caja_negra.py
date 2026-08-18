#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepara las capas de correa del paquete para la CAJA NEGRA.

Las capas con alfa que manda Óscar traen pegado un trozo de la caja de
acero con la que se fotografiaron: el arco del bisel y el arranque de
las asas. Mientras la cabeza que va encima sea de acero no se nota,
porque queda tapado; con la caja negra, ese acero asoma.

Aquí NO se clona ni se dibuja nada, al contrario que limpiar_correa.py:
simplemente se BORRA lo que cae dentro de la silueta de la cabeza de
acero. Se puede hacer porque la cabeza negra es más grande que la de
acero en todo su contorno (139-1018 frente a 144-1007 en vertical, y
246-1065 frente a 248-1059 en horizontal), así que tapa de sobra el
hueco que deja el borrado.

Uso: python3 capa_para_caja_negra.py
"""
from PIL import Image, ImageFilter
import numpy as np
import os

PAQUETE = ('/Users/oscar/Documents/Codex/2026-08-15/per/outputs/'
           'Lunar2026/ENTREGA-CLAUDE/masters-4k/straps/')
HEADS = 'assets/img/lunar-config/heads/'
DESTINO = 'masters-2026/lunar/capas/'
LADO = 4096

# capa del paquete -> nombre nuestro
CAPAS = {
    'goma-negra-texturizada-costura-verde': 'goma-negra-costura-verde-capa',
    'goma-azul-texturizada-pespunte-blanco': 'goma-azul-pespunte-blanco-capa',
    'piel-cocodrilo-negra': 'piel-italiana-negra-capa',
    'piel-cocodrilo-marron': 'piel-italiana-marron-capa',
    'piel-cocodrilo-azul': 'piel-italiana-azul-capa',
}


def silueta_negra():
    """La silueta de la cabeza NEGRA, que es la que irá encima.

    Se borra justo lo que ella va a tapar, ni un píxel más: así no queda
    hueco por ningún lado y desaparece todo el metal de la foto. Con la
    silueta de la cabeza de ACERO no bastaba —las asas de la foto
    sobresalen de ella y seguían asomando— y además en la capa del
    cocodrilo marrón lo que asomaba era el oro rosa de aquella
    generación fallida.
    """
    a = np.asarray(Image.open(HEADS + 'cab-negra-bnegro-agujas-plateadas.webp')
                   .convert('RGBA'))[:, :, 3] > 40
    im = Image.fromarray((a * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3))
    return np.asarray(im.resize((LADO, LADO), Image.NEAREST)) > 128


def prepara():
    os.makedirs(DESTINO, exist_ok=True)
    caja = silueta_negra()
    for origen, salida in CAPAS.items():
        ruta = PAQUETE + origen + '.png'
        if not os.path.exists(ruta):
            print('falta', origen); continue
        im = Image.open(ruta).convert('RGBA')
        a = np.asarray(im).copy()
        antes = int((a[:, :, 3] > 128).sum())
        a[caja, 3] = 0                       # fuera el trozo de caja
        despues = int((a[:, :, 3] > 128).sum())
        Image.fromarray(a).save(DESTINO + salida + '-4k.png')
        print('%-38s borrado %6d px de caja' % (salida, antes - despues))


if __name__ == '__main__':
    prepara()
