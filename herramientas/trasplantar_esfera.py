#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lleva la esfera de una cabeza del Lunar a otra, sin generar más fotos.

Todas las cabezas están alineadas a la misma geometría (ver
alinear_cabezas.py), así que la esfera de una encaja en el hueco de otra
al píxel. Sirve para montar combinaciones que el paquete no trae: por
ejemplo la esfera racing sobre la caja negra PVD.

Lo único delicado es dónde cortar. El anillo del taquímetro NO se puede
cruzar: los números de las dos cabezas no caen exactamente en el mismo
sitio y salen duplicados. Por eso el corte va por dentro de la esfera
(r=315 en lienzo 1254), antes del aro y del bisel, con una transición
suave de 18 px para que no quede un canto.

Del donante sale solo la esfera —con sus agujas, sus índices y su
fecha—; la caja, el bisel y el alfa son los de la base. Ni un píxel
dibujado: los dos trozos son fotos.

Uso: python3 trasplantar_esfera.py <base> <donante> <salida>
     (nombres sin ruta ni extensión, de assets/img/lunar-config/heads/)
"""
from PIL import Image
import numpy as np
import sys

HEADS = 'assets/img/lunar-config/heads/'
CENTRO = (630.4, 565.3)     # el eje de la esfera en el lienzo alineado
RADIO = 315                 # por dentro del aro: el taquímetro no se toca
TRANSICION = 18


def trasplanta(base, donante, salida):
    b = np.asarray(Image.open(HEADS + base + '.webp').convert('RGBA')).astype(float) / 255.0
    o = np.asarray(Image.open(HEADS + donante + '.webp').convert('RGBA')).astype(float) / 255.0
    if b.shape != o.shape:
        raise SystemExit('las dos cabezas tienen que venir del mismo lienzo')

    yy, xx = np.mgrid[0:b.shape[0], 0:b.shape[1]]
    d = np.hypot(xx - CENTRO[0], yy - CENTRO[1])
    peso = np.clip((RADIO - d) / TRANSICION, 0, 1)[..., None]

    out = b.copy()
    out[..., :3] = b[..., :3] * (1 - peso) + o[..., :3] * peso   # el alfa, el de la base
    Image.fromarray((np.clip(out, 0, 1) * 255).astype('uint8')).save(HEADS + salida + '.webp',
                                                                     quality=92, method=6)
    print('%s = caja de %s + esfera de %s' % (salida, base, donante))


if __name__ == '__main__':
    if len(sys.argv) == 4:
        trasplanta(*sys.argv[1:])
    else:
        # Las tres que le faltaban a la caja negra para llevar las
        # mismas esferas que la de acero (Óscar, 18/08).
        for don, sal in [
            ('cab-acero-bnegro-esf44-racing-naranja', 'cab-negra-bnegro-esf44-racing-naranja'),
            ('cab-acero-bnegro-esf26-negra-dorada',   'cab-negra-bnegro-esf26-negra-dorada'),
            ('cab-acero-bnegro-esf27-verde',          'cab-negra-bnegro-esf27-verde'),
        ]:
            trasplanta('cab-negra-bnegro-agujas-plateadas', don, sal)
