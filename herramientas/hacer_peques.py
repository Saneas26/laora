#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saca una copia LIGERA de cada foto de reloj, para el móvil.

Óscar, 12/08/2026: «si colocamos tantas fotos de ese tamaño la web pesa
demasiado para verlo en el móvil con 4g». Y tiene razón: una foto de
2000 px pesa unos 300 KB y en un teléfono no se aprovecha ni la mitad de
esos píxeles.

Así que de cada foto ancha se guarda una copia de 1200 px en
`completas/1200/`, y la página ofrece las dos: el navegador se lleva la
que le sirve —el móvil la pequeña, el escritorio la grande— sin que
nadie tenga que elegir nada.

Las que ya nacen pequeñas se quedan como están: hacerles una copia de
1200 no ahorraría ni ocho kilobytes.

USO
    python3 herramientas/hacer_peques.py
"""

import os
import struct
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPLETAS = os.path.join(RAIZ, 'assets/img/piezas/completas')
PEQUES = os.path.join(COMPLETAS, '1200')
ANCHO = 1200
DESDE = 1500          # por debajo de esto no compensa duplicar el archivo


def ancho_webp(ruta):
    """El ancho, leído de la cabecera del webp: sin dependencias."""
    with open(ruta, 'rb') as f:
        d = f.read(32)
    if d[:4] != b'RIFF' or d[8:12] != b'WEBP':
        return 0
    tipo = d[12:16]
    if tipo == b'VP8X':
        return 1 + int.from_bytes(d[24:27], 'little')
    if tipo == b'VP8 ':
        return struct.unpack('<H', d[26:28])[0] & 0x3fff
    if tipo == b'VP8L':
        b = int.from_bytes(d[21:25], 'little')
        return 1 + (b & 0x3fff)
    return 0


def main():
    os.makedirs(PEQUES, exist_ok=True)
    hechas = saltadas = 0
    for nom in sorted(os.listdir(COMPLETAS)):
        if not nom.endswith('.webp'):
            continue
        ent = os.path.join(COMPLETAS, nom)
        if ancho_webp(ent) < DESDE:
            saltadas += 1
            continue
        sal = os.path.join(PEQUES, nom)
        if os.path.exists(sal) and os.path.getmtime(sal) >= os.path.getmtime(ent):
            continue
        subprocess.run(['cwebp', '-quiet', '-q', '88', '-alpha_q', '100',
                        '-resize', str(ANCHO), '0', ent, '-o', sal], check=True)
        hechas += 1
    peso = sum(os.path.getsize(os.path.join(PEQUES, n)) for n in os.listdir(PEQUES))
    print(f'{hechas} copias de {ANCHO} px nuevas · {saltadas} ya eran pequeñas · '
          f'{peso/1024/1024:.1f} MB en total')


if __name__ == '__main__':
    main()
