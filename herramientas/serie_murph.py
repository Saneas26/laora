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
import logo_en_caja as lec
from PIL import Image as _Image


def logo_en_caja(ruta, blancos=False, modelo='trinchera'):
    """El logotipo sobre la esfera que la caja ya trae, sin cambiarla."""
    import math
    img = _Image.open(ruta)
    m = lec.medir(img)
    cx, cy, r = m['disco']
    if blancos:
        img, _ = lec.a_blanco(img, (cx, cy), r * 0.98, 0.12)
    L = lec.logotipo(modelo)
    eje = math.hypot(m['doce'][0] - m['seis'][0], m['doce'][1] - m['seis'][1])
    ancho = lec.PROPORCION * r
    alto = L.height * ancho / L.width
    ejeY = (m['doce'][1] + m['seis'][1]) / 2
    altura = (ejeY - (m['linea'] + alto / 2)) / (eje / 2)
    return lec.poner(img, m['doce'], m['seis'],
                     escala=ancho * 545 / (151 * eje), altura=altura, modelo=modelo)[0]

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
]

# ESTAS TRES NO CAMBIAN DE ESFERA. Llegan con una esfera del Murph que ya
# es buena —negra de verdad, nítida y centrada— y sustituirla por la
# madre solo empeoraba: se perdía nitidez, el negro se volvía morado y el
# logotipo acababa veintiún píxeles a la izquierda del 12. Se les pone el
# logotipo encima y ya está, con `logo_en_caja.py`. Aprobadas por Óscar
# el 20/08/2026.
#
# OJO con la piel negra: las suyas se montaron a mano antes de que
# existiera la herramienta y son las que Óscar dio por buenas. La
# herramienta las reproduce casi igual —el logotipo cae en la misma
# línea— pero no píxel a píxel, así que si se rehacen, mirarlas.
CON_ESFERA = [
    ('trinchera-h70405730-esfera-sin-letras-fondo-eae8e8-v2-4096.png',            'negra-pblanco'),
    ('trinchera-acero-esfera-crema-sin-letras-correa-piel-marron-v1-4096.png',    'marron-ptono'),
    ('trinchera-acero-esfera-crema-sin-letras-correa-piel-verde-v1-4096.png',     'verde-ptono'),
]

# Todas valen para las dos medidas (Óscar, 20/08/2026): «caja de acero y
# titanio sirve para 36 y 39 mm». Es la misma caja fotografiada de frente
# y las correas son todas de 20 mm.
SOLO_39 = set()

ESFERA = {'crema': 'murph-crema.png', 'blanco': 'murph-blanco.png'}


def claves(cola, esf):
    medidas = ('39',) if cola in SOLO_39 else ('36', '39')
    return ['%s-acero-%s-%s' % (d, esf, cola) for d in medidas]


def main(filtro=None):
    hechas = 0
    for caja, cola in CON_ESFERA:
        if filtro and filtro not in cola:
            continue
        origen = os.path.join(CAJAS, caja)
        for esf in ESFERA:
            img = logo_en_caja(origen, blancos=(esf == 'blanco'))
            tmp = '/tmp/serie-murph.png'
            img.save(tmp)
            for k in claves(cola, esf):
                publicar(tmp, DESTINO, k)
                print('  ', k)
                hechas += 1

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
