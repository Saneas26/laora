#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera TODAS las imágenes del configurador del Lunar.

REGLA DE LA CASA: lo que Óscar ha dado por bueno NO se vuelve a
generar. Los nombres listados en `demo-configurador/CONGELADAS.txt`
se saltan siempre; para rehacer una hay que quitarla de esa lista a
mano (o pasar --forzar, que avisa de lo que pisa).

Uso:
  python3 generar_configurador.py            # respeta lo congelado
  python3 generar_configurador.py --forzar   # rehace todo (avisa)
"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from componer_configurador import compone

RAIZ = os.path.join(os.path.dirname(__file__), '..')
MASTERS = os.path.join(RAIZ, 'masters-2026', 'lunar')
DESTINO = os.path.join(RAIZ, 'demo-configurador', 'img')
CONGELADAS = os.path.join(RAIZ, 'demo-configurador', 'CONGELADAS.txt')

# base de correa -> (prefijo, cabezas que NO la llevan)
CORREAS = {
    'full-acero-bnegro-plateadas-brazacero.png': ('braz-', ()),
    # la piel perforada no se ofrece con el bisel azul (orden de Óscar)
    'full-acero-bnegro-plateadas-pielperf.png':  ('piel-', ('bazul',)),
}


def congeladas():
    if not os.path.exists(CONGELADAS):
        return set()
    with open(CONGELADAS) as f:
        return {l.strip() for l in f if l.strip() and not l.startswith('#')}


def main(forzar=False):
    quietas = congeladas()
    hechas = saltadas = 0
    for base, (prefijo, veta) in CORREAS.items():
        for ruta in sorted(glob.glob(os.path.join(MASTERS, 'cab-*.png'))):
            nombre = os.path.basename(ruta)[4:-4]
            if any(v in nombre for v in veta):
                continue
            archivo = f'{prefijo}{nombre}.jpg'
            if archivo in quietas and not forzar:
                saltadas += 1
                continue
            if archivo in quietas:
                print(f'  ¡OJO! rehaciendo una CONGELADA: {archivo}')
            compone(os.path.join(MASTERS, base), ruta,
                    os.path.join(DESTINO, archivo), 1400)
            hechas += 1
    print(f'{hechas} imágenes generadas, {saltadas} respetadas por congeladas')


if __name__ == '__main__':
    main('--forzar' in sys.argv)
