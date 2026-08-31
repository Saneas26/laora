# -*- coding: utf-8 -*-
"""Pone en hora unas agujas que vienen ya montadas, girando cada una por su lado.

    python3 herramientas/agujas_en_hora.py [--hora 10:10:37]

Óscar, 31/08/2026: «las agujas tienen que mostrar las 10:10 y el segundero
el segundo 37». Es la hora de la casa —la misma que el Lunar, el Trinchera
y el Precisa, cuyas capas hasta se llaman `1010-segundero-37`— y las dos
entregas del Tortuga llegaban a su aire: el minutero casi en las 12, la
horaria pasadas las ocho y media y el segundero por el 21.

⚠️ ESTAS AGUJAS VIENEN ARMADAS, no sueltas. `herramientas/agujas_tortuga.py`
monta las de la primera entrega, que llegaban tumbadas una al lado de otra
y había que buscarle a cada una su pivote. Las que Óscar mandó después
—`38-` y `39-`— vienen ya montadas sobre el eje 2.048 y a la escala de la
esfera, así que no hay que armarlas: hay que RE-HORARLAS.

CÓMO SE SEPARAN LAS TRES. Se recorta un disco en el eje —el del tornillo,
que es donde las tres se pisan— y lo que queda fuera se parte solo en tres
trozos. Por debajo de 260 px de radio la horaria y el minutero siguen
pegados; a 280 salen limpios los tres.

CUÁL ES CUÁL, sin decírselo: el segundero es el de MENOS superficie —74.000
px contra 245.000— y de los otros dos, el minutero es el más largo. No hace
falta mirar ninguna en concreto.

CADA UNA GIRA SOBRE EL EJE Y SE VUELVE A APILAR en el orden del reloj de
verdad: horaria abajo, minutero encima y segundero arriba del todo. El
tornillo del centro se pega al final, sin girar: es redondo, así que da
igual, y tapa el hueco que dejan las tres al girar por separado.
"""
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGA = ('/Users/oscar/Documents/Codex/2026-08-31/'
           'tortuga-eres-el-dise-ador-gr/outputs/')
DESTINO = os.path.join(ENTREGA, 'preparadas')
LIENZO = 4096
CORTE = 280          # el disco donde las tres se pisan: ahí se separan
CUNA = 120           # y lo que se mira, hacia fuera, para saber por dónde
                     # entra cada una al centro
TAPA = 210           # el tornillo redondo, que se vuelve a pegar sin girar
MINIMA = 20000       # lo que tiene que medir un trozo para ser una aguja

AGUJAS = ['39-agujas-tortuga-acero-inoxidable-esfera-28-5mm-eje-2048.png',
          '38-agujas-tortuga-gris-oscuro-esfera-28-5mm-eje-2048.png']


def _angulo(x, y, eje):
    """El ángulo de reloj: 0 en las 12 y creciendo hacia las 3."""
    return math.degrees(math.atan2(x - eje[0], -(y - eje[1]))) % 360


def separa(a, eje, corte=CORTE):
    """Las tres agujas, de la más larga a la más corta."""
    al = a[:, :, 3] > 100
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.hypot(xx - eje[0], yy - eje[1])
    lab, n = ndimage.label(al & (d > corte))
    fuera = []
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() < MINIMA:
            continue
        ys, xs = np.where(m)
        r = np.hypot(xs - eje[0], ys - eje[1])
        i = int(np.argmax(r))
        fuera.append(dict(masc=m, area=int(m.sum()), largo=float(r.max()),
                          grados=_angulo(xs[i], ys[i], eje)))
    return sorted(fuera, key=lambda o: -o['largo'])


def reparte(tres):
    """Cuál es el segundero, cuál el minutero y cuál la horaria.

    El segundero es el de menos superficie —es un alambre— y de los otros
    dos manda el largo. Así no hay que escribir a mano qué trozo es cada
    cosa, que cambiaría con cada entrega."""
    seg = min(tres, key=lambda o: o['area'])
    resto = sorted([o for o in tres if o is not seg], key=lambda o: -o['largo'])
    return {'horaria': resto[1], 'minutero': resto[0], 'segundero': seg}


def hasta_el_centro(masc, eje, forma):
    """Alarga la aguja hasta el eje por la cuña por la que entra.

    ⚠️ SIN ESTO LAS AGUJAS SALEN FLOTANDO. El corte que las separa deja
    fuera todo lo que hay a menos de 280 px del eje, así que cada aguja se
    queda sin su arranque; al girarlas, entre el tornillo y la aguja
    aparecía un hueco, y encima el tornillo seguía llevando pegados los
    tres arranques VIEJOS, apuntando a donde estaban antes.

    Se mira por qué sector entra cada aguja —los ángulos que ocupa justo
    fuera del corte— y se le devuelve esa cuña entera hasta el centro. Las
    tres entran por sitios muy distintos, así que las cuñas no se pisan; y
    lo poco que se pisen queda debajo del tornillo."""
    ys, xs = np.where(masc)
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
    d = np.hypot(xx - eje[0], yy - eje[1])
    cerca = masc & (d < CORTE + CUNA)
    cy, cx = np.where(cerca)
    if not len(cx):
        return masc
    ang = np.degrees(np.arctan2(cx - eje[0], -(cy - eje[1])))     # -180..180
    # centrado en la media, para que no rompa al cruzar las 12
    m = math.degrees(math.atan2(np.mean(np.sin(np.radians(ang))),
                                np.mean(np.cos(np.radians(ang)))))
    rel = (ang - m + 180) % 360 - 180
    tod = np.degrees(np.arctan2(xx - eje[0], -(yy - eje[1])))
    relt = (tod - m + 180) % 360 - 180
    cuna = (d <= CORTE + CUNA) & (relt >= rel.min() - 2) & (relt <= rel.max() + 2)
    return masc | cuna


def gira(a, masc, grados, eje):
    """Gira SÓLO esa aguja, sobre el eje del reloj."""
    solo = a.copy()
    solo[~masc] = 0
    im = Image.fromarray(solo)
    # PIL gira al revés que el reloj, así que el ángulo va en negativo
    return np.asarray(im.rotate(-grados, resample=Image.BICUBIC,
                                center=eje, fillcolor=(0, 0, 0, 0)))


def en_hora(f, h, m, s):
    a = np.asarray(Image.open(ENTREGA + f).convert('RGBA')).copy()
    eje = (a.shape[1] / 2.0, a.shape[0] / 2.0)
    tres = separa(a, eje)
    if len(tres) != 3:
        raise SystemExit('%s: han salido %d agujas, no tres' % (f, len(tres)))
    q = reparte(tres)
    quiere = {'horaria': ((h % 12) + m / 60.0) * 30.0,
              'minutero': m * 6.0,
              'segundero': s * 6.0}

    L = np.zeros_like(a)
    orden = ['horaria', 'minutero', 'segundero']      # el de verdad, de abajo arriba
    dicho = []
    for nombre in orden:
        o = q[nombre]
        d = (quiere[nombre] - o['grados']) % 360.0
        giro = gira(a, hasta_el_centro(o['masc'], eje, a.shape[:2]), d, eje)
        alfa = giro[:, :, 3:4].astype(np.float32) / 255.0
        L[:] = (giro.astype(np.float32) * alfa +
                L.astype(np.float32) * (1 - alfa)).astype(np.uint8)
        dicho.append('%s %.1f° -> %.1f° (gira %+.1f°)'
                     % (nombre, o['grados'], quiere[nombre], d if d <= 180 else d - 360))

    # y el tornillo, tal cual venía: es redondo y tapa el centro
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    tapa = np.hypot(xx - eje[0], yy - eje[1]) <= TAPA
    L[tapa] = a[tapa]
    return Image.fromarray(L), dicho


def main():
    hora = '10:10:37'
    if '--hora' in sys.argv:
        hora = sys.argv[sys.argv.index('--hora') + 1]
    h, m, s = [int(x) for x in hora.split(':')]
    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)
    print('LAS AGUJAS, A LAS %s' % hora)
    for f in AGUJAS:
        im, dicho = en_hora(f, h, m, s)
        im.save(os.path.join(DESTINO, f))
        print('  %s' % f)
        for d in dicho:
            print('     %s' % d)
    print('\nescritas en %s' % DESTINO)


if __name__ == '__main__':
    main()
