# -*- coding: utf-8 -*-
"""PRECISA · coloca una caja con brazalete integrado en el lienzo del modelo.

    python3 herramientas/caja_precisa.py <fichero.png> <ident> [--prueba]

La caja del Precisa no es una pieza suelta: es caja Y brazalete, y va en
lienzo alto (1200x1666) porque al alejarse la cámara tiene que salir más
brazalete. Una caja nueva se coloca CONTRA LA QUE YA ESTÁ: se le iguala
el ojo —el hueco donde va la esfera— al de la caja de acero, en centro y
en radio. Así la esfera y las agujas, que se colocan contra ese ojo, no
se enteran de que ha cambiado la caja.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(RAIZ, 'assets/img/precisa-2026/capas')
PATRON = 'caja-brazalete-acero.avif'
ANCHO, ALTO = 1200, 1666
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 95000


def ojo(a):
    h = ndimage.binary_fill_holes(a) & ~a
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = ndimage.binary_closing(lab == 1 + int(np.argmax(t)), np.ones((41, 41)))
    ys, xs = np.where(m)
    cx, cy = float(xs.mean()), float(ys.mean())
    return (cx, cy), float(np.hypot(xs - cx, ys - cy).max()), float(m.sum())


def coloca(origen):
    ref = np.asarray(Image.open(os.path.join(CAPAS, '1200', PATRON))
                     .convert('RGBA'))[:, :, 3] > 128
    cr, rr, ar = ojo(ref)
    im = Image.open(origen).convert('RGBA')
    a = np.asarray(im)[:, :, 3] > 128
    cn, rn, an = ojo(a)
    s = (ar / an) ** 0.5          # por área: menos sensible al ruido del canto
    n = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(cr[0] - cn[0] * s), round(cr[1] - cn[1] * s)))
    return L, s, (cn, rn), (cr, rr)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) < 2:
        sys.exit(__doc__)
    capa, s, mio, ref = coloca(args[0])
    c2, r2, _ = ojo(np.asarray(capa)[:, :, 3] > 128)
    print('%-24s escala %.4f · ojo %.2f,%.2f r=%.1f  (el patrón: %.2f,%.2f r=%.1f)'
          % (args[1], s, c2[0], c2[1], r2, ref[0][0], ref[0][1], ref[1]))
    if '--prueba' in sys.argv:
        capa.save(os.path.join(os.environ.get('TMPDIR', '/tmp'), args[1] + '.png'))
        sys.exit(0)
    for t in TAMANOS:
        chica = capa.resize((t, round(ALTO * t / float(ANCHO))), Image.LANCZOS)
        for q in CALIDADES:
            b = _io.BytesIO()
            chica.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        open(os.path.join(CAPAS, str(t), args[1] + '.avif'), 'wb').write(d)
        print('  %-5d %6d B' % (t, len(d)))
