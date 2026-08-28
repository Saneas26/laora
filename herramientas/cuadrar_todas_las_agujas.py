#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cuadra CADA juego de agujas con CADA esfera del Lunar.

EL ENCARGO (Óscar, 28/08/2026): «con la esfera blanca y bisel azul, sólo
encajan las agujas azules, el resto en las agujas pequeñas no encajan
(…). Si hay que hacerlas de nuevo y definir exactamente las coordenadas
de cada eje, se hace, tiene que quedar un trabajo profesional».

POR QUÉ PASABA. Las tres agujas pequeñas de los contadores van DENTRO de
la capa de agujas, y cada esfera tiene los contadores en un punto
distinto —son imágenes generadas una a una—. Todas las capas de agujas
se dibujaron con los contadores de la esfera NEGRA, así que encajan en
las esferas que se le parecen y bailan en las demás. Cada capa cuadrada
se había hecho a mano, de una en una; esto las hace todas.

LO QUE HACE. Para cada pareja (acabado de agujas × esfera) llama a
cuadrar_agujas_pequenas.py, que mide el resalte del centro de cada
contador y el hub de cada aguja pequeña y la mueve hasta él.

Y NO ESCRIBE LAS QUE NO HACEN FALTA. Si a las tres agujas les toca
moverse menos de `--minimo` píxeles, la pareja se queda con la capa de
siempre: seis píxeles a 4.096 son menos de dos en la foto de 1.200 que se
publica, y una capa de más son 14 KB que el navegador se baja para nada.
El programa dice pareja por pareja cuánto se ha movido, así que la
decisión queda a la vista y se puede bajar el umbral a cero.

SALE UNA TABLA PARA `CAPA.agujas` de lunar.html, ya escrita, para pegar.

Uso:
    python3 herramientas/cuadrar_todas_las_agujas.py <capas-alineadas> <salida>
"""
import argparse
import os
import re
import subprocess
import sys

AGUJAS = [
    ('BLA', '06-agujas-plata-1010-segundero-37'),
    ('AZU', '07-agujas-azules-1010-segundero-37'),
    ('ORO', '09-agujas-oro-rosa-1010-segundero-37'),
    ('NAR', '12-agujas-rally-naranjas-1010-segundero-37'),
    ('DOR', '16-agujas-doradas-1010-segundero-37'),
]
ESFERAS = [
    ('NEG', '04-esfera-negra-sin-agujas', 'negra'),
    ('BLA', '05-esfera-blanca-subesferas-azules-sin-agujas', 'blanca'),
    ('PAN', '10-esfera-panda-sin-agujas', 'panda'),
    ('ORO', '11-esfera-blanca-oro-rosa-sin-agujas', 'ororosa'),
    ('DOR', '13-esfera-dorada-sin-agujas', 'dorada'),
    ('NAR', '15-esfera-rally-sin-agujas', 'rally'),
]
MOVIDA = re.compile(r'mueve\s+([+-]?\d+),([+-]?\d+)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('capas')
    ap.add_argument('salida')
    ap.add_argument('--minimo', type=float, default=6.0,
                    help='px por debajo de los cuales no se hace copia')
    o = ap.parse_args()
    os.makedirs(o.salida, exist_ok=True)
    aqui = os.path.dirname(os.path.abspath(__file__))

    print('%-8s %-8s %-30s %s' % ('AGUJAS', 'ESFERA', 'lo que se mueve', 'copia'))
    print('-' * 78)
    tabla = {}
    for ak, af in AGUJAS:
        tabla[ak] = {}
        for ek, ef, mote in ESFERAS:
            nombre = af.split('-1010')[0] + '-para-' + mote
            destino = os.path.join(o.salida, nombre + '-4096.png')
            r = subprocess.run(
                [sys.executable, os.path.join(aqui, 'cuadrar_agujas_pequenas.py'),
                 os.path.join(o.capas, af + '-4096.png'),
                 os.path.join(o.capas, ef + '-4096.png'), destino],
                capture_output=True, text=True)
            if r.returncode:
                print('%-8s %-8s  ✗ %s' % (ak, ek, r.stdout.strip().splitlines()[-1]))
                continue
            m = MOVIDA.findall(r.stdout)
            tope = max(max(abs(int(a)), abs(int(b))) for a, b in m) if m else 0
            if tope < o.minimo:
                if os.path.exists(destino):
                    os.remove(destino)
                print('%-8s %-8s %-30s la de siempre' % (ak, ek, 'nada, %d px' % tope))
                continue
            tabla[ak][ek] = nombre
            print('%-8s %-8s %-30s %s' % (
                ak, ek, ' · '.join('%s,%s' % p for p in m), nombre))

    print('\n\n    /* pegar en CAPA.agujas de lunar.html */')
    print('    agujas: {')
    for ak, af in AGUJAS:
        if not tabla[ak]:
            print("      %s: '%s'," % (ak, af))
            continue
        print("      %s: { '*': '%s'," % (ak, af))
        cl = list(tabla[ak].items())
        for i, (ek, nom) in enumerate(cl):
            coma = ' },' if i == len(cl) - 1 else ','
            print("             %s: '%s'%s" % (ek, nom, coma))
    print('    },')
