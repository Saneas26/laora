#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mete el contrato de pasos dentro del motor del configurador.

EL CONTRATO ES `assets/datos/pasos-2026.json` y lo dictó Óscar el
29/08/2026: el orden de pasos que llevan los diez modelos, con sus dos
reglas —una sola opción sale señalada y explicada; sin opciones, el paso
no aparece—.

POR QUÉ NO SE LEE CON `fetch`. El motor tiene que pintar los pasos en la
primera pasada, antes de que el cliente vea nada, y además se ejecuta
FUERA del navegador cuando el volcador calcula las tres mil referencias
del catálogo. Un `fetch` obligaría a esperar en el navegador y a
inventarse un sustituto en el volcador. Así que el contrato viaja dentro
del motor, y este guión es el que lo copia.

UNA SOLA FUENTE, IGUAL. El JSON manda; el motor lleva una copia
literal entre dos marcas. Pasar esto deja las dos iguales, y
`--comprobar` dice si se han separado sin tocar nada —que es lo que hace
el gancho de pre-commit—.

Uso:
    python3 herramientas/sincronizar_pasos.py
    python3 herramientas/sincronizar_pasos.py --comprobar
"""
import argparse
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRATO = os.path.join(RAIZ, 'assets/datos/pasos-2026.json')
MOTOR = os.path.join(RAIZ, 'assets/js/configurador-2026.js')
ABRE = '  /* >>> pasos-2026.json · lo copia herramientas/sincronizar_pasos.py */'
CIERRA = '  /* <<< fin del contrato de pasos */'


def bloque():
    d = json.load(io.open(CONTRATO, encoding='utf-8'))
    # Al motor solo le hacen falta el orden y las reglas de cada paso, no
    # los comentarios del contrato: el porqué se lee en el JSON.
    pasos = [{k: v for k, v in p.items() if k != 'porque'} for p in d['pasos']]
    tarjetas = [{k: v for k, v in t.items() if k != 'porque'} for t in d['tarjetas']]
    return (ABRE + '\n  var PASOS = ' + json.dumps(pasos, ensure_ascii=False, indent=2)
            .replace('\n', '\n  ') + ';\n'
            + '  var TARJETAS = ' + json.dumps(tarjetas, ensure_ascii=False, indent=2)
            .replace('\n', '\n  ') + ';\n' + CIERRA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--comprobar', action='store_true')
    o = ap.parse_args()

    s = io.open(MOTOR, encoding='utf-8').read()
    i, j = s.find(ABRE), s.find(CIERRA)
    if i < 0 or j < 0:
        sys.exit('✗ no encuentro las marcas del contrato dentro del motor')
    viejo = s[i:j + len(CIERRA)]
    nuevo = bloque()
    if viejo == nuevo:
        print('los pasos del motor ya son los del contrato')
        return
    if o.comprobar:
        sys.exit('✗ el motor lleva unos pasos y `pasos-2026.json` dice otros.\n'
                 '  Pasa: python3 herramientas/sincronizar_pasos.py')
    io.open(MOTOR, 'w', encoding='utf-8').write(s[:i] + nuevo + s[j + len(CIERRA):])
    print('pasos copiados al motor')


if __name__ == '__main__':
    main()
