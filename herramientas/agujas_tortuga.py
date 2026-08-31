# -*- coding: utf-8 -*-
"""TORTUGA · arma las tres agujas y las pone sobre el eje del reloj.

    python3 herramientas/agujas_tortuga.py [--prueba] [--hora 10:10]

Óscar, 31/08/2026: «monta las agujas», a las 10:10 «como el resto».

LA ENTREGA LAS TRAE SUELTAS. `01-agujas-tortuga.png` es un bodegón: las
tres agujas tumbadas una al lado de otra, apuntando hacia arriba, sobre
un damero. No es una capa de agujas montada como la del Precisa o la del
Trinchera: hay que armarla.

CÓMO SE ENCUENTRA EL EJE DE CADA AGUJA. Por el AGUJERO DEL PIVOTE, que es
el único agujero REDONDO de cada pieza. Las tres tienen agujeros de sobra
—los huecos que deja la flecha, el canal del lumen, las sombras— pero
ninguno es redondo: midiendo `área / (π·r²)` el pivote sale a 0,98 y el
siguiente no pasa de 0,55. No hay que decirle a mano dónde está ninguno.

    horaria    pivote en 383,4 / 935,1 · radio 36
    minutero   pivote en 655,6 / 952,3 · radio 39
    segundero  pivote en 894,0 / 906,7 · radio  8

LA ESCALA SALE DE LA ESFERA, no de un número: el minutero muere en la
pista de minutos, que se mide con el armónico 60 igual que en el Precisa.

LA HORA, LA DE LA CASA: 10:10 y el segundero abajo, como el Lunar, el
Trinchera y el Precisa. Se pasa con `--hora` por si algún día cambia.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capas_tortuga import (ENTREGA, DESTINO, LIENZO, ANCHO, TAMANOS, CALIDADES,
                           PESO, FONDO, CAJA_PATRON, ESFERAS, HOLGURA_ESF,
                           alfa, hueco_de_la_caja, guarda)
from esferas_precisa import mide_la_pista

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGUJAS = '01-agujas-tortuga.png'
ESFERA_PATRON = '11-esfera-negra-28-5mm-4096.png'
# Dónde muere el minutero, en tanto por uno de la pista de minutos de la
# esfera. 0,99 la deja tocando la pista, que es lo que hace un reloj.
PUNTA = 0.99


def piezas():
    """Las tres agujas del bodegón, cada una con su pivote y su punta.

    El fondo es un damero claro; la aguja, o es oscura o tiene color. Las
    dos cosas juntas la separan sin tocar un umbral a ojo: el lumen crema
    es claro pero tiene 35 de saturación, y el damero no tiene ninguna."""
    a = np.asarray(Image.open(ENTREGA + AGUJAS).convert('RGB')).astype(float)
    L = a.mean(2)
    sat = a.max(2) - a.min(2)
    m = ndimage.binary_closing((L < 215) | (sat > 25), np.ones((5, 5)))
    lab, n = ndimage.label(m)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    out = []
    for i in np.argsort(t)[::-1][:3]:
        p = lab == i + 1
        piv = _pivote(p)
        ys, xs = np.where(p)
        d = np.hypot(xs - piv[0], ys - piv[1])
        k = int(np.argmax(d))
        out.append(dict(mask=p, pivote=piv, punta=(float(xs[k]), float(ys[k])),
                        largo=float(d.max()), area=int(t[i])))
    # el más largo es el segundero; de los otros dos, el largo es el minutero
    out.sort(key=lambda h: -h['largo'])
    seg = max(out, key=lambda h: h['largo'] / max(1.0, np.sqrt(h['area'])))
    resto = [h for h in out if h is not seg]
    resto.sort(key=lambda h: -h['largo'])
    return {'minutero': resto[0], 'horaria': resto[1], 'segundero': seg}, a


def _pivote(p):
    """El agujero REDONDO de la pieza: por ahí pasa el eje del movimiento."""
    h = ndimage.binary_fill_holes(p) & ~p
    lab, n = ndimage.label(h)
    mejor = None
    for k in range(1, n + 1):
        ys, xs = np.where(lab == k)
        if len(ys) < 40:
            continue
        cx, cy = xs.mean(), ys.mean()
        r = float(np.hypot(xs - cx, ys - cy).max())
        redondez = len(ys) / (np.pi * r * r)
        if mejor is None or redondez > mejor[0]:
            mejor = (redondez, float(cx), float(cy), r)
    return (mejor[1], mejor[2]) if mejor else (0.0, 0.0)


def capa(h, rgb, s, grados, eje):
    """Una aguja escalada, girada sobre su pivote y puesta en el eje."""
    a = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    a[:, :, :3] = rgb.astype(np.uint8)
    borde = np.clip(ndimage.gaussian_filter(h['mask'].astype(np.float32), 0.6),
                    0, 1)
    a[:, :, 3] = (borde * 255).astype(np.uint8)
    im = Image.fromarray(a)
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - h['pivote'][0] * s),
                          round(eje[1] - h['pivote'][1] * s)))
    # PIL gira al revés de las agujas del reloj, así que el ángulo va con
    # el signo cambiado: aquí se cuenta desde las 12 y hacia la derecha.
    return L.rotate(-grados, resample=Image.BICUBIC, center=eje)


def monta(hora):
    hs, rgb = piezas()
    eje, r_ojo = hueco_de_la_caja(CAJA_PATRON)
    d = mide_la_pista(ENTREGA + ESFERA_PATRON)
    ys, xs = np.where(alfa(ESFERA_PATRON))
    re = float(np.hypot(xs - (xs.min() + xs.max()) / 2.0,
                        ys - (ys.min() + ys.max()) / 2.0).max())
    s_esf = r_ojo * HOLGURA_ESF / re
    pista = d['r_punta'] * s_esf
    s = pista * PUNTA / hs['minutero']['largo']
    print('OJO DE LA CAJA %.1f,%.1f r %.0f · pista de minutos a %.0f px'
          % (eje[0], eje[1], r_ojo, pista))
    print('ESCALA %.4f (el minutero muere en el %.0f %% de la pista)'
          % (s, PUNTA * 100))
    hh, mm = [int(x) for x in hora.split(':')]
    grados = {'horaria': (hh % 12) * 30.0 + mm * 0.5,
              'minutero': mm * 6.0,
              'segundero': 180.0}
    L = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    for k in ('horaria', 'minutero', 'segundero'):
        h = hs[k]
        print('  %-10s pivote %.1f,%.1f · largo %4.0f -> %4.0f px · %5.1f grados'
              % (k, h['pivote'][0], h['pivote'][1], h['largo'], h['largo'] * s,
                 grados[k]))
        L.alpha_composite(capa(h, rgb, s, grados[k], eje))
    return L.resize((ANCHO, ANCHO), Image.LANCZOS)


def hoja(agujas, destino):
    B = os.path.join(DESTINO, str(ANCHO))
    tiros = [('caja-acero', 'esfera-negra', 'caucho-negra'),
             ('caja-anillo-naranja', 'esfera-negra-marfil', 'caucho-naranja'),
             ('caja-anillo-azul', 'esfera-azul-sunburst', 'brazalete-acero')]
    h = Image.new('RGB', (len(tiros) * 460, 460), FONDO[:3])
    for i, (caja, esf, cor) in enumerate(tiros):
        L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
        for k in (cor, esf, caja):
            L.alpha_composite(Image.open(os.path.join(B, k + '.avif')).convert('RGBA'))
        L.alpha_composite(agujas)
        h.paste(L.convert('RGB').resize((460, 460)), (i * 460, 0))
    h.save(destino)


if __name__ == '__main__':
    hora = (sys.argv[sys.argv.index('--hora') + 1]
            if '--hora' in sys.argv else '10:10')
    agujas = monta(hora)
    prueba = '--prueba' in sys.argv
    d = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'tortuga-agujas.png') if prueba
         else os.path.join(RAIZ, 'herramientas/capturas/tortuga-agujas.png'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    hoja(agujas, d)
    print('\nhoja de control: ' + d)
    if prueba:
        sys.exit(0)
    print('\nPUBLICADO agujas  %d B' % guarda(agujas, 'agujas'))
