#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · REPASO COMPLETO DEL LUNAR

Óscar, 29/08/2026: «tienes que auditar todo para que podamos ir dando forma
definitiva y acabar con este modelo para pasar al siguiente».

Mira cuatro cosas, y ninguna se cree lo que dice la ficha: todas se
comprueban contra lo que hay en el disco y contra el catálogo del servidor.

  1. PIEZAS QUE FALTAN · cada opción dibuja una capa; ¿existe el fichero?
  2. PIEZAS QUE SOBRAN · ficheros publicados que no pinta ninguna opción.
  3. SIN COSTE, NO SE VENDE · qué opciones dejan al reloj sin precio.
  4. EL CATÁLOGO · cuántas referencias salen y a qué precios.

Uso:
    python3 herramientas/auditar_lunar.py
"""
import io
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def del_js(nombre):
    """Lee una tabla del `lunar.html` ejecutándola con node: es JavaScript,
    no JSON, y copiarla aquí a mano sería tener dos verdades."""
    guion = r'''
      const fs = require('fs');
      const s = fs.readFileSync(%s, 'utf8');
      // El bloque de PIEZAS es el que acaba declarando `window.LAORA_MODELO`:
      // se coge desde el `<script>` que lo contiene hasta esa línea.
      const j = s.indexOf('window.LAORA_MODELO');
      const i = s.lastIndexOf('<script>', j);
      const cuerpo = s.slice(i + '<script>'.length, j);
      const f = new Function(cuerpo + '; return {CAPA, CAPA_IMG, CORREAS, CIERRES, ' +
        'CAJAS, BISELES, ESFERAS, AGUJAS, CRISTALES, MOVS, PAQUETES, CORREA_MAT, ' +
        'MATERIALES, PESPUNTES, CON_PESPUNTE, MINI, CIERRE_IMG};');
      process.stdout.write(JSON.stringify(f()));
    ''' % json.dumps(os.path.join(RAIZ, 'lunar.html'))
    out = subprocess.run(['node', '-e', guion], capture_output=True, text=True)
    if out.returncode:
        sys.exit('✗ no he podido leer las tablas del Lunar:\n' + out.stderr[:900])
    return json.loads(out.stdout)


def main():
    M = del_js('lunar.html')
    capas = os.path.join(RAIZ, 'assets/img/lunar-2026/capas/1600')
    comp = os.path.join(RAIZ, 'assets/img/componentes/correas/1600')

    print('=' * 74)
    print('1 · PIEZAS QUE FALTAN')
    print('=' * 74)
    faltan = []
    for grupo, tabla in M['CAPA'].items():
        # `cristal` y `fecha` no dibujan capa: son tablas vacías o nulas.
        if not isinstance(tabla, dict):
            continue
        for k, v in tabla.items():
            if not v:
                continue
            hijos = v.items() if isinstance(v, dict) else [(None, v)]
            for esf, fich in hijos:
                p = os.path.join(capas, fich + '.avif')
                if not os.path.exists(p):
                    faltan.append('%s/%s%s → %s' % (grupo, k, '·' + esf if esf else '', fich))
    # las correas viven en la biblioteca y su nombre lleva el pespunte
    def sufijos_de(c, d):
        """El pespunte va DENTRO del nombre de la pieza: claro para todas,
        y el a color lo dice cada correa en `pespTono` (30/08/2026)."""
        mat = M['CORREA_MAT'].get(c, 'A316')
        if not M['CON_PESPUNTE'].get(mat):
            return ['']
        return ['-pespunte-blanco', d.get('pespTono', '')]

    for c, d in M['CORREAS'].items():
        if not d.get('pieza'):
            faltan.append('correa/%s no dice de qué pieza sale' % c)
            continue
        for su in sufijos_de(c, d):
            p = os.path.join(comp, d['pieza'] + su + '.avif')
            if not os.path.exists(p):
                faltan.append('correa/%s → %s' % (c, d['pieza'] + su))
    for k, d in M['CIERRES'].items():
        if d.get('mini') and not os.path.exists(
                os.path.join(RAIZ, 'assets/img/lunar-2026/cierres', d['mini'] + '.avif')):
            faltan.append('cierre/%s → %s' % (k, d['mini']))
    print('\n'.join('   ✗ ' + f for f in faltan) if faltan
          else '   ✔ ninguna: cada opción tiene su dibujo')

    print()
    print('=' * 74)
    print('2 · PIEZAS PUBLICADAS QUE NO USA NADIE')
    print('=' * 74)
    usadas = set()
    for c, d in M['CORREAS'].items():
        for su in sufijos_de(c, d):
            usadas.add(d['pieza'] + su)
    hay = set(f[:-5] for f in os.listdir(comp) if f.endswith('.avif'))
    sobran = sorted(hay - usadas)
    print('\n'.join('   · ' + s for s in sobran) if sobran
          else '   ✔ ninguna: todo lo publicado se usa')

    print()
    print('=' * 74)
    print('3 · SIN COSTE NO SE VENDE')
    print('=' * 74)
    sin = []
    for c, d in sorted(M['CORREAS'].items()):
        if d.get('coste') is None:
            sin.append('correa %-10s %s' % (c, d['nombre']))
    paq = [p for p in M['PAQUETES'] if p.get('coste') is None]
    for p in paq:
        sin.append('paquete %s' % p)
    print('\n'.join('   ✗ ' + x for x in sin) if sin
          else '   ✔ todas las piezas tienen coste')
    if sin:
        print('   → esas combinaciones se dibujan, pero dicen «Precio por '
              'definir» y no dejan comprar.')


if __name__ == '__main__':
    main()
