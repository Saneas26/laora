#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · BITÁCORA, MONTADA DESDE LA MADRE

    python3 herramientas/capas_bitacora_madre.py [carpeta] [--prueba]

Óscar, 04/09/2026: «monta esto ahora en el bitácora y retira todas las
fotos pero deja las opciones del configurador […] a ver si podemos montar
el reloj por capas».

LA ENTREGA SON DOS PIEZAS, no cuatro:

  · `...madre-caja-esfera-agujas-4096.png` — la CABEZA ENTERA: caja,
    esfera y agujas en una sola pieza.
  · `...madre-brazalete-norte-sur-4096.png` — el brazalete, las dos tiras.

Las dos están cortadas de la MISMA imagen de 4.096, así que ya vienen
colocadas una respecto de otra y aquí NO SE MIDE NADA ENTRE PIEZAS. Es la
misma idea del despiece del 03/09 (ver `capas_bitacora_despiece.py`) con
una diferencia que importa: **la esfera y las agujas van dentro de la
cabeza**, así que hoy no se pueden elegir por separado. Los pasos siguen
en el configurador —Óscar los quiere ahí— pero sólo dibuja la caja.

QUÉ SE HACE, y son dos cosas del lienzo, no del reloj:

  1. llevar el eje del reloj al centro del lienzo de la casa;
  2. elegir UNA escala, la misma para las dos piezas.

EL EJE sale del BRAZALETE, no de la cabeza: el hueco entre sus dos tiras
da la fila del eje y el ancho de las tiras da la columna. La cabeza no
vale para eso porque lleva la corona a un lado y su centro geométrico
está corrido a la derecha.

LA ESCALA sale de una sola condición: que el brazalete llegue a los dos
cantos del marco. La casa enseña el reloj alejado, con el lienzo a 0,72,
así que la ventana visible son 1.200/0,72 = 1.667 filas centradas en el
eje. Manda la tira más corta. Se comprueba al final.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from tarjeta_de_capas import ESCALA as CAMARA, apila            # noqa: E402

ENTREGA = ('/Users/oscar/Documents/Codex/2026-09-04/'
           'necesito-la-imagen-definitiva-de-la/outputs/')
DESTINO = os.path.join(RAIZ, 'assets/img/bitacora-2026/capas/1200')
ANCHO = 1200
ALTO_LARGO = 1952
HOLGURA = 1.002                 # el pelo que separa la tira del filo del marco
CALIDADES = (78, 72, 64, 56, 48, 40)
PESO = 95000

# qué fichero es cada capa: se busca por un trozo del nombre, porque la
# entrega los numera y los nombra a su manera
PIEZAS = {'caja-plata':      'madre-caja-esfera-agujas',
          'brazalete-acero': 'madre-brazalete-norte-sur'}
LARGAS = ('brazalete-acero',)   # las que van en el lienzo alto


def busca(carpeta, trozo):
    for f in sorted(os.listdir(carpeta)):
        if f.lower().endswith('.png') and trozo in f.lower():
            return os.path.join(carpeta, f)
    return None


def _alfa(ruta, u=128):
    return np.asarray(Image.open(ruta).convert('RGBA'))[:, :, 3] > u


def marco(ruta_brazalete):
    """El eje del reloj y la escala, leídos del brazalete."""
    b = _alfa(ruta_brazalete)
    fil = np.where(b.any(1))[0]
    cortes = np.split(fil, np.where(np.diff(fil) > 1)[0] + 1)
    if len(cortes) != 2:
        raise SystemExit('✗ el brazalete no trae dos tiras')
    ejey = (int(cortes[0][-1]) + int(cortes[1][0])) / 2.0
    col = np.where(b.any(0))[0]
    ejex = (int(col.min()) + int(col.max())) / 2.0
    arriba, abajo = ejey - fil.min(), fil.max() - ejey
    media = (ANCHO / CAMARA) / 2.0
    return (ejex, ejey), HOLGURA * media / min(arriba, abajo), arriba, abajo


def coloca(ruta, eje, escala, lienzo):
    im = Image.open(ruta).convert('RGBA')
    n = im.resize((max(1, int(round(im.width * escala))),
                   max(1, int(round(im.height * escala)))), Image.LANCZOS)
    L = Image.new('RGBA', lienzo, (0, 0, 0, 0))
    L.alpha_composite(n, (int(round(lienzo[0] / 2.0 - eje[0] * escala)),
                          int(round(lienzo[1] / 2.0 - eje[1] * escala))))
    return L


def guarda(im, ident):
    for q in CALIDADES:
        b = _io.BytesIO()
        im.save(b, 'AVIF', quality=q)
        d = b.getvalue()
        if len(d) <= PESO or q == CALIDADES[-1]:
            break
    open(os.path.join(DESTINO, ident + '.avif'), 'wb').write(d)
    return len(d)


def main():
    prueba = '--prueba' in sys.argv
    carpeta = next((a for a in sys.argv[1:] if not a.startswith('--')), ENTREGA)
    rutas = {k: busca(carpeta, t) for k, t in PIEZAS.items()}
    faltan = [k for k, v in rutas.items() if not v]
    if faltan:
        raise SystemExit('✗ no encuentro %s en %s' % (', '.join(faltan), carpeta))
    eje, escala, arriba, abajo = marco(rutas['brazalete-acero'])
    print('EJE       %.1f, %.1f (del hueco del brazalete, no de la cabeza)' % eje)
    print('BRAZALETE %d filas por arriba del eje y %d por abajo; la ventana '
          'pide %.0f' % (arriba, abajo, (ANCHO / CAMARA) / 2.0))
    print('ESCALA    %.4f (la manda la tira más corta)' % escala)
    capas = {k: coloca(v, eje, escala,
                       (ANCHO, ALTO_LARGO) if k in LARGAS else (ANCHO, ANCHO))
             for k, v in rutas.items()}
    a = np.asarray(capas['brazalete-acero'])[:, :, 3] > 128
    f = np.where(a.any(1))[0]
    ve = ((ALTO_LARGO - ANCHO / CAMARA) / 2.0,
          (ALTO_LARGO + ANCHO / CAMARA) / 2.0)
    print('          llega al canto de arriba: %s · al de abajo: %s'
          % (f.min() <= ve[0], f.max() >= ve[1]))
    hoja = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'bitacora-madre.png')
    apila([capas['brazalete-acero'], capas['caja-plata']], ANCHO,
          (233, 233, 231), CAMARA).convert('RGB').save(hoja)
    print('hoja de control: ' + hoja)
    if prueba:
        return
    os.makedirs(DESTINO, exist_ok=True)
    print('\nPUBLICADO en %s' % os.path.relpath(DESTINO, RAIZ))
    for k in sorted(capas):
        print('  %-20s %6d B  %dx%d'
              % (k, guarda(capas[k], k), capas[k].width, capas[k].height))


if __name__ == '__main__':
    main()
