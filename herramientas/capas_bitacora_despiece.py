#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · BITÁCORA, MONTADA DESDE EL DESPIECE

    python3 herramientas/capas_bitacora_despiece.py [--prueba]

Óscar, 03/09/2026, después de una semana peleándose con el montaje:
«cambia el bitácora por esto a ver si podemos dar con la tecla, porque no
es posible por el momento, siempre falla algo».

Y ERA ESO. El problema nunca fue el ajuste: era que cada pieza llegaba en
un encuadre distinto —las cajas en un lienzo, las esferas en otra carpeta
y a otra escala, el brazalete registrado contra un dibujo del proveedor,
las agujas «en la misma posición» que una esfera que no publicamos—, y
había que RECONSTRUIR la relación entre ellas midiendo. Cada medida era
una oportunidad de fallar, y fallaba.

EL DESPIECE LO ARREGLA DE RAÍZ: las cuatro piezas están cortadas de la
MISMA imagen de 4.096, así que ya vienen colocadas unas respecto de otras.
Aquí no se mide NADA entre piezas. Sólo se hacen dos cosas, y las dos son
del lienzo, no del reloj:

  1. llevar el eje del reloj al centro del lienzo de la casa, y
  2. elegir UNA escala, la misma para todas.

⚠️ SI ALGÚN DÍA HAY QUE VOLVER A MEDIR ENTRE PIEZAS, ES QUE LA ENTREGA NO
ES UN DESPIECE. Parar y pedirlo bien, en vez de reconstruirlo a mano: eso
es lo que costó la semana del 27/08 al 03/09.

--------------------------------------------------------------------------
LA ESCALA, Y POR QUÉ ÉSTA

`ESCALA` sale de una sola condición: **que el brazalete llegue a los dos
cantos del marco**. La casa enseña el reloj alejado, con el lienzo a 0,72
(ver `tarjeta_de_capas.ESCALA` y `configurador-2026.css`), así que la
ventana que se ve son 1.200/0,72 = 1.667 filas centradas en el eje: 833
hacia arriba y 833 hacia abajo.

En el despiece, desde el eje hay 1.540 filas de brazalete hacia arriba y
2.312 hacia abajo. La de arriba es la que manda: 833/1.540 = 0,5409. Se
deja un pelo más para que no quede al filo del redondeo.

⚠️ NO ES UN NÚMERO A MANO: se recalcula de la entrega en cada pasada y se
comprueba al final. Si la tira norte de un despiece nuevo viene más larga,
el reloj se enseñará más alejado él solo.

--------------------------------------------------------------------------
LO QUE HACE FALTA PARA CAMBIAR EL MODELO ENTERO

El primer despiece trae UNA combinación. La Bitácora vende 67 referencias
con 4 cajas, 5 esferas y 5 brazaletes, así que hacen falta **15 piezas**,
todas cortadas del mismo sitio (el encargo se le pasó a Codex el 03/09).
Mientras falte una, NO se publica nada: Óscar decidió esperar a tenerlas
todas para no enseñar dos relojes distintos dentro del mismo modelo.

`COLORES` dice qué fichero es cada capa. Con el despiece de una sola
combinación se publica una capa de cada, que es lo que hay hoy.
"""
import io as _io
import os
import re
import sys

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from tarjeta_de_capas import ESCALA as CAMARA, apila            # noqa: E402

DESPIECE = os.environ.get('DESPIECE_BITACORA', '')
DESTINO = os.path.join(RAIZ, 'assets/img/bitacora-2026/capas/1200')
ANCHO = 1200                    # lienzo cuadrado publicado
ALTO_LARGO = 1952               # lienzo del brazalete, que es más alto
CALIDADES = (72, 64, 56, 48, 40)
PESO = 90000
HOLGURA = 1.002                 # el pelo que separa la tira del filo del marco

# Qué pieza del despiece es cada capa publicada. Las claves son los nombres
# que ya usan la ficha y `montaje.capas`; los valores, el trozo de nombre de
# fichero que hay que buscar en la carpeta del despiece.
COLORES = {
    'caja':      {'caja-plata': 'plata', 'caja-bronce': 'bronce',
                  'caja-oro-rosa': 'oro-rosa', 'caja-negro-pvd': 'negro-pvd'},
    'esfera':    {'esfera-turquesa': 'turquesa', 'esfera-blanca': 'blanca',
                  'esfera-negra': 'negra', 'esfera-azul': 'azul',
                  'esfera-cobre': 'cobre'},
    'brazalete': {'brazalete-acero': 'acero',
                  'brazalete-acero-centros-oro-rosa': 'centros-oro-rosa',
                  'brazalete-acero-centros-dorados': 'centros-oro-amarillo',
                  'brazalete-oro-rosa': 'oro-rosa-entero',
                  'brazalete-negro-pvd': 'negro-pvd'},
}
# el trozo de nombre que identifica cada FAMILIA de pieza dentro del despiece
FAMILIA = {'caja': 'cabeza', 'esfera': 'esfera', 'brazalete': 'brazalete',
           'agujas': 'agujas'}


def _alfa(ruta, u=128):
    return np.asarray(Image.open(ruta).convert('RGBA'))[:, :, 3] > u


def piezas(carpeta):
    """{familia: {color o None: ruta}} a partir de los ficheros de la carpeta.

    Se busca por trozos de nombre y no por una lista cerrada, porque el
    despiece llega numerado (`01-`, `02-`…) y los colores todavía no tienen
    un nombre acordado con Codex. Lo que NO se hace es adivinar: si un color
    de `COLORES` no aparece, se dice y no se publica.
    """
    encontrado = {f: {} for f in FAMILIA}
    for f in sorted(os.listdir(carpeta)):
        if not f.lower().endswith('.png'):
            continue
        n = f.lower()
        for fam, marca in FAMILIA.items():
            if marca not in n:
                continue
            color = None
            for capa, trozo in COLORES.get(fam, {}).items():
                if re.search(r'(^|[-_])' + re.escape(trozo) + r'([-_.]|$)', n):
                    color = capa
                    break
            encontrado[fam][color] = os.path.join(carpeta, f)
            break
    return encontrado


def marco(ruta_esfera, ruta_brazalete):
    """El eje del reloj y la escala, leídos de la propia entrega.

    EL EJE ES EL CENTRO DEL DISCO DE LA ESFERA, que es el único punto del
    reloj que está definido sin discusión. La caja no vale: lleva la corona
    a un lado y su centro geométrico está corrido.
    """
    a = _alfa(ruta_esfera)
    ys, xs = np.where(a)
    eje = ((xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0)
    b = _alfa(ruta_brazalete)
    fil = np.where(b.any(1))[0]
    arriba = eje[1] - fil.min()
    abajo = fil.max() - eje[1]
    media = (ANCHO / CAMARA) / 2.0          # media ventana visible, en filas
    escala = HOLGURA * media / min(arriba, abajo)
    return eje, float(escala), int(arriba), int(abajo), media


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
    carpeta = DESPIECE or next((a for a in sys.argv[1:]
                                if not a.startswith('--')), '')
    if not carpeta or not os.path.isdir(carpeta):
        raise SystemExit('✗ dime la carpeta del despiece (o DESPIECE_BITACORA)')
    hay = piezas(carpeta)
    for fam in ('esfera', 'brazalete', 'caja', 'agujas'):
        if not hay[fam]:
            raise SystemExit('✗ en el despiece no hay ninguna pieza de «%s»' % fam)
    eje, escala, arriba, abajo, media = marco(next(iter(hay['esfera'].values())),
                                              next(iter(hay['brazalete'].values())))
    print('EJE del reloj (centro del disco de la esfera): %.1f, %.1f' % eje)
    print('BRAZALETE  %d filas por arriba del eje y %d por abajo; la ventana '
          'pide %.0f' % (arriba, abajo, media))
    print('ESCALA     %.4f (la manda la tira más corta, para que llegue al canto)'
          % escala)

    capas, faltan = {}, []
    for fam, tabla in COLORES.items():
        lienzo = (ANCHO, ALTO_LARGO) if fam == 'brazalete' else (ANCHO, ANCHO)
        for capa in tabla:
            ruta = hay[fam].get(capa)
            if ruta is None:
                faltan.append(capa)
                continue
            capas[capa] = coloca(ruta, eje, escala, lienzo)
    if None in hay['agujas']:
        capas['agujas'] = coloca(hay['agujas'][None], eje, escala, (ANCHO, ANCHO))
    elif hay['agujas']:
        capas['agujas'] = coloca(next(iter(hay['agujas'].values())), eje,
                                 escala, (ANCHO, ANCHO))

    # con un despiece de una sola combinación, las piezas llegan sin color en
    # el nombre: sirven de muestra, pero no se publican con nombre de color
    sueltas = {f: hay[f].get(None) for f in ('caja', 'esfera', 'brazalete')}
    if faltan:
        print('\n⚠️  FALTAN %d capas y por eso NO SE PUBLICA NADA:' % len(faltan))
        for c in faltan:
            print('     %s' % c)
        if any(sueltas.values()):
            print('   (el despiece trae la combinación suelta, sin color en el '
                  'nombre: sirve para mirarla, no para publicar)')

    # la hoja de control: el reloj como lo pinta el navegador
    orden = [k for k in ('brazalete', 'esfera', 'caja', 'agujas')]
    muestra = []
    for fam in orden:
        if fam == 'agujas':
            if 'agujas' in capas:
                muestra.append(capas['agujas'])
            continue
        c = next((capas[k] for k in COLORES[fam] if k in capas), None)
        if c is None and sueltas.get(fam):
            lienzo = (ANCHO, ALTO_LARGO) if fam == 'brazalete' else (ANCHO, ANCHO)
            c = coloca(sueltas[fam], eje, escala, lienzo)
        if c is not None:
            muestra.append(c)
    hoja = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'bitacora-despiece.png')
    apila(muestra, ANCHO, (233, 233, 231), CAMARA).convert('RGB').save(hoja)

    # ⚠️ LA COMPROBACIÓN QUE NO SE SALTA: el brazalete tiene que llegar a los
    # dos cantos. Si no llega, la tira norte del dibujo es más corta que la sur
    # y hace falta un render más largo, no un apaño.
    brz = next((capas[k] for k in COLORES['brazalete'] if k in capas), None)
    if brz is None and sueltas.get('brazalete'):
        brz = coloca(sueltas['brazalete'], eje, escala, (ANCHO, ALTO_LARGO))
    if brz is not None:
        a = np.asarray(brz)[:, :, 3] > 128
        f = np.where(a.any(1))[0]
        ve = ((ALTO_LARGO - ANCHO / CAMARA) / 2.0,
              (ALTO_LARGO + ANCHO / CAMARA) / 2.0)
        print('\nEL BRAZALETE llega al canto de arriba: %s · al de abajo: %s'
              % (f.min() <= ve[0], f.max() >= ve[1]))
    print('hoja de control: ' + hoja)

    if prueba or faltan:
        return
    os.makedirs(DESTINO, exist_ok=True)
    print('\nPUBLICADO en %s' % os.path.relpath(DESTINO, RAIZ))
    for ident in sorted(capas):
        print('  %-34s %6d B  %dx%d'
              % (ident, guarda(capas[ident], ident),
                 capas[ident].width, capas[ident].height))


if __name__ == '__main__':
    main()
