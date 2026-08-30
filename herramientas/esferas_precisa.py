# -*- coding: utf-8 -*-
"""PRECISA · rehace las capas de esfera desde la entrega.

    python3 herramientas/esferas_precisa.py            # publica las ocho
    python3 herramientas/esferas_precisa.py --prueba   # solo la hoja de control

POR QUÉ. Óscar, 30/08/2026: «hay píxeles en blanco sobre la esfera
antracita, manchas, en la unión con la caja irregularidades, y tan solo
debe ser una capa inferior a la caja, que se superpone sin tener que
descolorear o pintar nada».

QUÉ PASABA, MEDIDO. La entrega trae un borde sucio: en la antracita, un
gajo BLANCO pegado al canto que ocupa desde el 96 % del radio hacia
fuera; en la azul hielo y la turquesa, lo mismo pero más fino. Y la capa
publicada se escalaba de forma que el borde del hueco de la caja caía en
el 97 % del radio de la esfera: el gajo quedaba FUERA del bisel y se veía
como una mancha blanca justo en la unión.

CÓMO SE ARREGLA. Sin tocar un píxel del dibujo: se agranda un pelo la
esfera para que el borde del hueco caiga en el **96 % de su radio**. Todo
lo que hay del 96 % hacia fuera —el gajo incluido— pasa a estar debajo
del bisel, que es donde tiene que estar. Y no se pierde nada del dibujo:
en las esferas limpias el contenido (la pista de minutos) se acaba justo
en ese 96 %, medido en el histograma radial de las ocho.

Las ocho salen al MISMO tamaño visible aunque la entrega las traiga con
radios distintos (578 a 597 px), porque la escala se calcula de cada una.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGA = '/Users/oscar/Documents/Codex/2026-08-29/prec/outputs/'
CAPAS = os.path.join(RAIZ, 'assets/img/precisa-2026/capas')
ANCHO = 1200
ALTO_CAJA = 1666
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 95000
FONDO = (233, 233, 231, 255)

# Dónde cae el borde del hueco de la caja sobre el radio de la esfera.
# 0,96 es donde se acaba el dibujo en las esferas limpias y donde empieza
# el gajo sucio en las manchadas: el único punto que salva las dos cosas.
CORTE = 0.96

# LA ESFERA VA UN POCO MÁS ABAJO QUE EL EJE DEL HUECO (Óscar, 30/08/2026:
# «todas las esferas deben bajar 2 grados hacia el sur»). Dos grados de
# arco sobre el radio de la esfera son 11,5 px en el lienzo de 1200.
# Y al bajarla hay que AGRANDARLA lo mismo, o por arriba asomaría el
# fondo: la condición es que el 96 % del radio siga tapando el hueco por
# el lado alto, o sea Rd = (radio del hueco + bajada) / 0,96.
# Lo que se paga: por abajo la pista de minutos se mete bajo el bisel.
# Preguntado y confirmado por Óscar antes de hacerlo.
BAJADA = 11.5

ESFERAS = {
    'esfera-antracita':      'laora-precisa-esfera-antracita.png',
    'esfera-azul-hielo':     'laora-precisa-esfera-azul-hielo.png',
    'esfera-azul-marino':    'laora-precisa-esfera-azul-marino.png',
    'esfera-blanca':         'laora-precisa-esfera-blanca.png',
    'esfera-blanca-oro-rosa': 'laora-precisa-esfera-blanca-indices-oro-rosa.png',
    'esfera-naranja':        'laora-precisa-esfera-naranja.png',
    'esfera-turquesa':       'laora-precisa-esfera-turquesa.png',
    'esfera-verde':          'laora-precisa-esfera-verde.png',
}
# ⚠️ LOS NOMBRES DE LA ENTREGA VAN CRUZADOS entre turquesa y azul hielo, y
# el cruce se deshace en la ficha del modelo (`montaje.capas.esf`), no
# aquí: aquí cada fichero conserva su nombre. Ver `_esferas_cruzadas` en
# assets/datos/fichas/precisa.json.


def hueco_de_la_caja():
    """Centro y radio máximo del ojo de la caja, en el lienzo cuadrado."""
    a = np.asarray(Image.open(os.path.join(CAPAS, '1200/caja-brazalete-acero.avif'))
                   .convert('RGBA'))[:, :, 3] > 128
    h = ndimage.binary_fill_holes(a) & ~a
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = lab == 1 + int(np.argmax(t))
    ys, xs = np.where(m)
    cx = float(xs.mean())
    cy = float(ys.mean()) - (ALTO_CAJA - ANCHO) / 2.0
    r = float(np.hypot(xs - xs.mean(), ys - ys.mean()).max())
    return (cx, cy), r


def disco(f):
    """Centro y radio de la esfera entregada."""
    a = np.asarray(Image.open(f).convert('RGBA'))[:, :, 3] > 200
    ys, xs = np.where(a)
    cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    r = float(np.hypot(xs - cx, ys - cy).max())
    return (cx, cy), r


def coloca(f, eje, radio_hueco):
    im = Image.open(f).convert('RGBA')
    c, r = disco(f)
    s = (radio_hueco + BAJADA) / (CORTE * r)
    eje = (eje[0], eje[1] + BAJADA)
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - c[0] * s), round(eje[1] - c[1] * s)))
    return L, s, r


def guarda(im, ident):
    for t in TAMANOS:
        chica = im.resize((t, round(im.size[1] * t / float(ANCHO))), Image.LANCZOS)
        for q in CALIDADES:
            b = _io.BytesIO()
            chica.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        carpeta = os.path.join(CAPAS, str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, ident + '.avif'), 'wb').write(d)
    return len(d)


def hoja(capas, destino):
    caja = Image.open(os.path.join(CAPAS, '1200/caja-brazalete-acero.avif')).convert('RGBA')
    caja = caja.crop((0, (ALTO_CAJA - ANCHO) // 2, ANCHO, (ALTO_CAJA + ANCHO) // 2))
    agujas = Image.open(os.path.join(CAPAS, '1200/agujas-plata.avif')).convert('RGBA')
    nombres = sorted(capas)
    cols, filas = 4, (len(nombres) + 3) // 4
    hoja = Image.new('RGB', (cols * 400, filas * 400), FONDO[:3])
    for i, k in enumerate(nombres):
        L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
        L.alpha_composite(capas[k])
        L.alpha_composite(caja)
        L.alpha_composite(agujas)
        hoja.paste(L.convert('RGB').resize((400, 400)), ((i % cols) * 400, (i // cols) * 400))
    hoja.save(destino)


if __name__ == '__main__':
    eje, rh = hueco_de_la_caja()
    print('OJO DE LA CAJA: centro %.2f, %.2f · radio %.1f px' % (eje[0], eje[1], rh))
    print('El borde del hueco cae en el %.0f %% del radio de cada esfera.' % (CORTE * 100))
    print('La esfera baja %.1f px (2 grados de arco) y crece lo mismo para taparlo.' % BAJADA)
    capas = {}
    for ident, f in sorted(ESFERAS.items()):
        capas[ident], s, r = coloca(ENTREGA + f, eje, rh)
        print('  %-24s entregada r=%5.1f  escala %.4f  -> r=%5.1f' % (ident, r, s, r * s))
    prueba = '--prueba' in sys.argv
    d = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'precisa-esferas.png') if prueba
         else os.path.join(RAIZ, 'herramientas/capturas/precisa-esferas.png'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    hoja(capas, d)
    print('\nhoja de control: ' + d)
    if prueba:
        sys.exit(0)
    print('\nPUBLICADO en assets/img/precisa-2026/capas/{480,1200,1600}/')
    for ident in sorted(capas):
        print('  %-24s %6d B' % (ident, guarda(capas[ident], ident)))
