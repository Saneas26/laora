#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monta TODAS las fotos del Murph, de la caja original a los tres AVIF.

Hasta ahora cada foto se montaba a mano y los parámetros se perdían: al
cambiar la esfera madre no había forma de rehacerlas sin volver a
acertar el encuadre una por una. Aquí está escrito lo que hace falta
—qué caja va con qué clave— y con un comando se rehace la serie entera.

Uso:
    python3 herramientas/serie_murph.py            # todo
    python3 herramientas/serie_murph.py ante       # solo lo que case
"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from esfera_en_caja import montar
from foto_a_web import publicar

CAJAS = ('/Users/oscar/Documents/Codex/2026-08-19/'
         'traspaso-proyecto-laora-trinchera-carpeta-de-2/outputs')
DESTINO = 'assets/img/trinchera-2026/serie'
ESFERAS = 'assets/img/trinchera-2026/esferas'

# La esfera del Murph sale enderezada y centrada de logo_en_esfera.py:
# disco de 490 px de radio en el centro de un lienzo de 1200.
CENTRO, RESFERA = (600, 600), 490

# caja original -> cola de la clave. Delante se pone el diámetro y la
# esfera, que son los dos ejes que multiplican cada foto.
CORREAS = [
    ('trinchera-caja-maestra-correa-ante-azul-petroleo-esfera-vacia-v1-4096.png', 'ante-azulpetroleo'),
    ('trinchera-caja-maestra-correa-ante-camel-esfera-vacia-v1-4096.png',         'ante-camel'),
    ('trinchera-caja-maestra-correa-ante-marron-oscuro-esfera-vacia-v1-4096.png', 'ante-marronoscuro'),
    ('trinchera-caja-acero-cepillado-nueva-correa-ante-negro-esfera-vacia-prueba-v2-4096.png', 'ante-negro'),
    ('trinchera-h70405130-brazalete-original-esfera-vacia-prueba-v1-4096.png',    'brazalete'),
    # Estas tres llegan CON esfera puesta —otra distinta de la nuestra—,
    # y aun así el hueco se encuentra solo: el disco es oscuro y liso por
    # dentro, que es lo único que mira el relleno.
    ('trinchera-h70405730-esfera-sin-letras-fondo-eae8e8-v2-4096.png',            'negra-pblanco'),
    ('trinchera-acero-esfera-crema-sin-letras-correa-piel-marron-v1-4096.png',    'marron-ptono'),
    ('trinchera-acero-esfera-crema-sin-letras-correa-piel-verde-v1-4096.png',     'verde-ptono'),
]

# La piel negra solo se fotografió en 39: no se inventa una de 36.
SOLO_39 = {'negra-pblanco'}

ESFERA = {'crema': 'murph-crema.png', 'blanco': 'murph-blanco.png'}


def claves(cola, esf):
    medidas = ('39',) if cola in SOLO_39 else ('36', '39')
    return ['%s-acero-%s-%s' % (d, esf, cola) for d in medidas]


def main(filtro=None):
    hechas = 0
    for caja, cola in CORREAS:
        if filtro and filtro not in cola:
            continue
        origen = Image.open(os.path.join(CAJAS, caja))
        for esf, archivo in ESFERA.items():
            img, info = montar(origen, Image.open(os.path.join(ESFERAS, archivo)),
                               centro=CENTRO, resfera=RESFERA)
            tmp = '/tmp/serie-murph.png'
            img.save(tmp)
            for k in claves(cola, esf):
                publicar(tmp, DESTINO, k)
                print('  ', k)
                hechas += 1
    print(hechas, 'fotos')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
