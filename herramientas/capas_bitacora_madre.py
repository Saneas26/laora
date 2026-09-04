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
from scipy import ndimage

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
# ⚠️ LA TANDA BUENA ES LA DEL «MEDIO ESLABÓN» (04/09/2026, 20:24). La
# carpeta guarda también las anteriores —las «madre» de las 19:42 y los dos
# brazaletes sueltos de las 20:05—, y como aquí se busca por un trozo del
# nombre, el trozo tiene que ser LO BASTANTE LARGO para no pescarlas: sin
# el `-con-medio-eslabon`, `brazalete-negro-pvd` cogía el de las 20:05, que
# va antes por orden alfabético.
# ⚠️ LA CABEZA ES CAJA+ESFERA+AGUJAS EN UN DIBUJO, así que hay una por cada
# pareja caja/esfera: dos cajas por cinco esferas, diez cabezas. La turquesa
# viene de la entrega de las 20:24 (`-hueco-medio-eslabon`) y las otras
# cuatro de la de las 22:06.
PIEZAS = {
    'caja-plata-E1':     'caja-acero-hueco-medio-eslabon',
    'caja-plata-E2':     'caja-acero-esfera-blanca',
    'caja-plata-E3':     'caja-acero-esfera-negra',
    'caja-plata-E4':     'caja-acero-esfera-azul',
    'caja-plata-E6':     'caja-acero-esfera-marron',
    'caja-negro-pvd-E1': 'caja-negro-pvd-hueco-medio-eslabon',
    'caja-negro-pvd-E2': 'caja-negro-pvd-esfera-blanca',
    'caja-negro-pvd-E3': 'caja-negro-pvd-esfera-negra',
    'caja-negro-pvd-E4': 'caja-negro-pvd-esfera-azul',
    'caja-negro-pvd-E6': 'caja-negro-pvd-esfera-marron',
    'brazalete-acero': 'brazalete-acero-con-medio-eslabon',
    'brazalete-acero-centros-oro-rosa': 'brazalete-acero-oro-rosa-con-medio-eslabon',
    'brazalete-negro-pvd': 'brazalete-negro-pvd-con-medio-eslabon',
    # ⚠️ LAS PIELES YA VIENEN CON SU HERRAJE (entrega de las 21:58). Eso
    # resuelve lo del 04/09 —«hay que recortar más el eslabón del medio en
    # piel para que encaje con la caja»—: el hueco del medio eslabón ya no lo
    # tapa el cuero, lo tapa una pieza de metal dibujada. Por eso hay DOS de
    # cada color, una por acabado de caja, y ya NO se recortan por la silueta.
    'piel-negra-C1':         'correa-piel-negra-herraje-acero',
    'piel-negra-C4':         'correa-piel-negra-herraje-negro-pvd',
    'piel-azul-marino-C1':   'correa-piel-azul-marino-herraje-acero',
    'piel-azul-marino-C4':   'correa-piel-azul-marino-herraje-negro-pvd',
    'piel-marron-burdeos-C1': 'correa-piel-marron-herraje-acero',
    'piel-marron-burdeos-C4': 'correa-piel-marron-herraje-negro-pvd',
}
LARGAS = tuple(k for k in PIEZAS if k.startswith(('brazalete', 'piel')))
# las pieles también van en el lienzo alto; se añaden aparte porque no salen
# de esta entrega sino de la de correas del 29/08 (ver `capas_de_piel`)
# ⚠️ LOS ACABADOS DE UNA MISMA PIEZA TIENEN QUE SER EL MISMO DIBUJO. Se
# comprueba antes de publicar, cabezas y brazaletes por separado: si la
# silueta de uno no es la del primero de su familia, el reloj pegaría un
# salto al cambiar de acabado y esto para en vez de publicarlo.


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
    for k in faltan:
        del rutas[k]
    if 'caja-plata-E1' not in rutas or 'brazalete-acero' not in rutas:
        raise SystemExit('✗ faltan las dos piezas madre en %s' % carpeta)
    if faltan:
        print('todavía sin dibujo: %s' % ', '.join(sorted(faltan)))
    eje, escala, arriba, abajo = marco(rutas['brazalete-acero'])
    print('EJE       %.1f, %.1f (del hueco del brazalete, no de la cabeza)' % eje)
    print('BRAZALETE %d filas por arriba del eje y %d por abajo; la ventana '
          'pide %.0f' % (arriba, abajo, (ANCHO / CAMARA) / 2.0))
    print('ESCALA    %.4f (la manda la tira más corta)' % escala)
    for patron, cabeza in (('brazalete-acero',
                            [k for k in LARGAS if k.startswith('brazalete')]),
                           ('piel-negra-C1',
                            [k for k in LARGAS if k.startswith('piel')]),
                           ('caja-plata-E1', [k for k in rutas
                                              if k.startswith('caja')])):
        if patron not in rutas:
            continue
        ref = _alfa(rutas[patron])
        for k in cabeza:
            if k == patron or k not in rutas:
                continue
            otro = _alfa(rutas[k])
            u = (ref | otro).sum()
            iou = (ref & otro).sum() / float(u) if u else 0.0
            if iou < 0.999:
                raise SystemExit('✗ %s no tiene la silueta de %s (IoU %.5f)'
                                 % (k, patron, iou))
            print('          %-34s IoU %.5f con %s' % (k, iou, patron))
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
    apila([capas['brazalete-acero'], capas['caja-plata-E1']], ANCHO,
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
