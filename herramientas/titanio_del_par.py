#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pasa a titanio una caja fotografiada en acero, COPIANDO EL CAMBIO de un par
acero/titanio que ya existe.

POR QUÉ ESTE Y NO `caja_a_titanio.py`. Aquel se inventaba la curva a ojo
—bajar la claridad, recoger los reflejos y darle «un punto de calor»— y el
punto de calor estaba AL REVÉS. Medido sobre el par del Khaki, que lo generó
el mismo motor y sólo cambia el metal, el titanio sale FRÍO: a claridad 220
el acero da R-B = +0,3 y el titanio R-B = -3,6. Por eso la caja de titanio
del Murph tiraba a gris marrón (Óscar, 26/08/2026: «se puede colorear mejor»).

CÓMO APRENDE. El par del Khaki es la misma foto dos veces: la esfera y la
correa son idénticas al píxel y sólo cambia la caja. Eso da dos cosas
gratis y exactas:

  - DÓNDE está la caja: los píxeles que cambian.
  - QUÉ le pasa al metal: para cada nivel de claridad del acero, el color
    medio que le corresponde en titanio. Sale una curva de una sola rama,
    monótona: 100 -> 91, 150 -> 121, 200 -> 146, 250 -> 175.

Se aplica esa tabla a la foto de acero y ya está. No se inventa textura: el
dibujo del metal —cepillado, pulido, reflejos— es el mismo, sólo cambia el
tono, que es justo lo que distingue un metal del otro.

DÓNDE se aplica, en la foto de destino. La máscara del par dice dónde está
la caja EN LA MADRE. Si la foto de destino es la misma madre con otra
correa, la correa asoma por el hueco de las asas y cae dentro de esa
máscara; pintarla de titanio la ensuciaría. Se resuelve al revés: dentro de
la máscara, es caja lo que sigue siendo IDÉNTICO a la madre de acero. Lo que
ha cambiado es correa. Al recorte se le quitan dos píxeles de borde para que
el filo antialiado entre como metal y no quede una raya brillante.

Uso:
    python3 herramientas/titanio_del_par.py \
        --patron-acero  khaki-acero.png  --patron-titanio khaki-titanio.png \
        --madre-acero   murph-acero.png  --madre-titanio  murph-titanio.png \
        foto-acero.png  salida-titanio.png
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

CANALES = ('R', 'G', 'B')


def abrir(f):
    im = Image.open(f)
    a = np.asarray(im.convert('RGBA')).astype(float)
    return a[..., :3], a[..., 3]


def donde_cambia(a, b, umbral=3.0):
    if a.shape != b.shape:
        raise SystemExit('las dos fotos del par tienen que ser del mismo tamaño')
    return np.abs(a - b).mean(2) > umbral


def tabla(ac, ti, m, suavizado=5):
    """Para cada claridad del acero, el color medio en titanio."""
    L = ac[m].mean(1)
    dest = ti[m]
    lut = np.zeros((256, 3))
    n = np.zeros(256)
    idx = np.clip(L.round().astype(int), 0, 255)
    for c in range(3):
        lut[:, c] = np.bincount(idx, weights=dest[:, c], minlength=256)
    n = np.bincount(idx, minlength=256).astype(float)
    hay = n >= 200
    if hay.sum() < 20:
        raise SystemExit('el par no tiene metal suficiente para aprender la curva')
    lut[hay] /= n[hay, None]
    # los niveles sin muestras se rellenan estirando la curva por los extremos
    xs = np.where(hay)[0]
    for c in range(3):
        lut[:, c] = np.interp(np.arange(256), xs, lut[xs, c])
    # un alisado corto quita el ruido de los niveles con pocas muestras sin
    # aplanar la curva, que es suave de por sí
    k = np.ones(suavizado) / suavizado
    for c in range(3):
        lut[:, c] = np.convolve(np.pad(lut[:, c], (suavizado, suavizado), 'edge'), k,
                                'same')[suavizado:-suavizado]
    return lut, xs.min(), xs.max()


def aplicar(foto, lut, m, borde=1.5):
    L = foto.mean(2)
    idx = np.clip(L, 0, 255)
    lo = np.floor(idx).astype(int); hi = np.minimum(lo + 1, 255); t = (idx - lo)[:, :, None]
    base = lut[lo] * (1 - t) + lut[hi] * t          # el tono nuevo
    fuera = base + (foto - L[:, :, None])           # se le devuelve su propio color
    s = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(borde))).astype(float) / 255
    return foto * (1 - s[:, :, None]) + np.clip(fuera, 0, 255) * s[:, :, None]


def caja_de_esta_foto(m_madre, foto, madre_acero, umbral=3.0, despegue=5):
    """Dentro de la máscara, es caja lo que no ha cambiado respecto a la madre."""
    cambiado = np.abs(foto - madre_acero).mean(2) > umbral
    cambiado = np.asarray(Image.fromarray((cambiado * 255).astype(np.uint8))
                          .filter(ImageFilter.MinFilter(despegue))).astype(bool)
    return m_madre & ~cambiado


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--patron-acero', required=True)
    p.add_argument('--patron-titanio', required=True)
    p.add_argument('--madre-acero')
    p.add_argument('--madre-titanio')
    p.add_argument('foto'); p.add_argument('salida')
    o = p.parse_args()

    pa, _ = abrir(o.patron_acero); pt, _ = abrir(o.patron_titanio)
    mp = donde_cambia(pa, pt)
    lut, lo, hi = tabla(pa, pt, mp)
    print('curva aprendida en %s: %d px de metal, niveles %d..%d'
          % (o.patron_acero.split('/')[-1], mp.sum(), lo, hi))
    for v in (100, 150, 200, 250):
        print('   acero %3d  ->  titanio %5.1f   (R-B %+.1f)'
              % (v, lut[v].mean(), lut[v][0] - lut[v][2]))

    foto, alfa = abrir(o.foto)
    if o.madre_acero and o.madre_titanio:
        ma, _ = abrir(o.madre_acero); mt, _ = abrir(o.madre_titanio)
        m_madre = donde_cambia(ma, mt)
        m = caja_de_esta_foto(m_madre, foto, ma)
        print('caja de la madre: %d px · en esta foto: %d px (%d son correa)'
              % (m_madre.sum(), m.sum(), m_madre.sum() - m.sum()))
    else:
        m = mp
        print('caja: la del propio patrón, %d px' % m.sum())
    if m.sum() < 10000:
        raise SystemExit('la máscara ha salido vacía: ¿es esta foto de la misma madre?')

    out = aplicar(foto, lut, m)
    r = np.dstack([np.clip(out, 0, 255), alfa]).astype(np.uint8)
    Image.fromarray(r, 'RGBA').save(o.salida)
    px = out[m]
    print('%s · caja: L50 %.1f  L99 %.1f  R-B %+.1f'
          % (o.salida, np.percentile(px.mean(1), 50), np.percentile(px.mean(1), 99),
             px[:, 0].mean() - px[:, 2].mean()))
