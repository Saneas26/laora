# -*- coding: utf-8 -*-
"""TORTUGA · monta las capas del configurador desde la entrega del 31/08.

    python3 herramientas/capas_tortuga.py [--prueba]

Óscar, 31/08/2026: «ves montando el tortuga». La entrega —
`Codex/2026-08-31/tortuga-eres-el-dise-ador-gr/outputs/` — llega MUCHO
mejor que las anteriores: de la pieza 11 en adelante viene en lienzo de
4.096 con alfa de verdad y con el eje en la 2.048, que es la norma de la
casa. No hay que recortar nada; sólo medir y escalar.

MANDA LA CAJA, y en este reloj más que en ninguno: el bisel de buceo y el
anillo de minutos van DIBUJADOS DENTRO de ella, así que la esfera no se
mide contra el hueco «a ojo» sino que se lleva a llenarlo. Cada anillo de
color es una caja entera: no es una capa aparte.

LAS DOS COSAS QUE NO ESTÁN A ESCALA, y por eso hay que escalarlas:
  · LA ESFERA viene a radio 1.800 y el hueco de la caja mide 1.140. Es un
    dibujo de esfera suelto, no está a la escala del reloj.
  · LA CORREA viene a 745 px de ancho y el hueco entre las astas mide
    1.637. Está dibujada a menos de la mitad.
El BRAZALETE, en cambio, sí llega a escala (1.635 px para un hueco de
1.637): sólo hay que centrarlo, que viene 28 px a la izquierda.

⚠️ EL HUECO ENTRE LAS ASTAS SON 22,4 mm, NO 20. La caja mide 45 mm de
lado a lado (3.212 px en la fila del centro, o sea 71,4 px por milímetro)
y el hueco entre las astas es de 1.637 px. Las correas de la entrega se
llaman «20-18mm». O la correa sube a 22 —que es lo que lleva el reloj al
que homenajea— o las astas se cierran 2,4 mm. Mientras tanto se llena el
hueco, que es lo único que no deja ver el fondo, y queda dicho.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGA = ('/Users/oscar/Documents/Codex/2026-08-31/'
           'tortuga-eres-el-dise-ador-gr/outputs/')
DESTINO = os.path.join(RAIZ, 'assets/img/tortuga-2026/capas')
LIENZO = 4096                    # el de la entrega
ANCHO = 1600                     # el que se publica grande; los otros se bajan
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 95000
FONDO = (233, 233, 231, 255)

CAJA_PATRON = '19-caja-tortuga-45mm-eje-2048.png'
HOLGURA_ESF = 1.005              # la esfera se mete un pelín bajo el anillo
HOLGURA_COR = 1.010              # y la correa, un pelín bajo las astas

CAJAS = {
    'caja-acero':            '19-caja-tortuga-45mm-eje-2048.png',
    'caja-anillo-naranja':   '21-caja-tortuga-anillo-naranja-eje-2048.png',
    'caja-anillo-naranja-grueso': '22-caja-tortuga-anillo-naranja-grueso-escala-negra.png',
    'caja-anillo-plata':     '23-caja-tortuga-anillo-plata-escala-negra.png',
    'caja-anillo-azul':      '24-caja-tortuga-anillo-azul-escala-negra.png',
    'caja-anillo-verde':     '25-caja-tortuga-anillo-verde-escala-negra.png',
    'caja-anillo-negro':     '26-caja-tortuga-anillo-negro-escala-clara.png',
    'caja-anillo-oliva':     '27-caja-tortuga-anillo-oliva-escala-negra.png',
    'caja-anillo-burdeos':   '28-caja-tortuga-anillo-burdeos-escala-negra.png',
    'caja-anillo-turquesa':  '29-caja-tortuga-anillo-turquesa-escala-negra.png',
    'caja-anillo-acero':     '30-caja-tortuga-anillo-acero-liso.png',
}
ESFERAS = {
    'esfera-negra':            '11-esfera-negra-28-5mm-4096.png',
    'esfera-azul-texturizada': '12-esfera-azul-texturizada-28-5mm-4096.png',
    'esfera-azul-sunburst':    '13-esfera-azul-sunburst-28-5mm-4096.png',
    'esfera-turquesa-sunburst': '14-esfera-turquesa-sunburst-28-5mm-4096.png',
    'esfera-turquesa-champagne': '15-esfera-turquesa-champagne-28-5mm-4096.png',
    'esfera-roja-fume':        '16-esfera-roja-fume-28-5mm-4096.png',
    'esfera-negra-marfil':     '17-esfera-negra-marfil-28-5mm-4096.png',
    'esfera-frambuesa-fume':   '18-esfera-frambuesa-fume-28-5mm-4096.png',
}
CORREAS = {
    'caucho-negra':      '32-correa-caucho-negra-buzo-20-18mm-eje-2048.png',
    'caucho-azul-marino': '33-correa-caucho-azul-marino-buzo-20-18mm-eje-2048.png',
    'caucho-gris':       '34-correa-caucho-gris-buzo-20-18mm-eje-2048.png',
    'caucho-verde':      '35-correa-caucho-verde-buzo-20-18mm-eje-2048.png',
    'caucho-roja':       '36-correa-caucho-roja-buzo-20-18mm-eje-2048.png',
    'caucho-naranja':    '37-correa-caucho-naranja-buzo-20-18mm-eje-2048.png',
    'brazalete-acero':   '20-brazalete-tortuga-eje-2048.png',
}


def alfa(f, u=128):
    return np.asarray(Image.open(ENTREGA + f).convert('RGBA'))[:, :, 3] > u


def hueco_de_la_caja(f):
    """Centro y radio del ojo de la caja: por ahí se ve la esfera."""
    from scipy import ndimage
    a = alfa(f)
    h = ndimage.binary_fill_holes(a) & ~a
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    ys, xs = np.where(lab == 1 + int(np.argmax(t)))
    cx, cy = float(xs.mean()), float(ys.mean())
    return (cx, cy), float(np.hypot(xs - cx, ys - cy).max())


def hueco_entre_astas(f):
    """El hueco por el que entra la correa, y hasta qué fila se ve.

    Las astas de la Tortuga son cuatro cuernos cortos: no hay «filas de
    asa» como en un reloj de correa recta. Se buscan las filas de arriba
    que tienen DOS tramos de caja con un hueco en medio; el hueco más ancho
    de todas es el que la correa tiene que tapar."""
    a = alfa(f)
    peor, ultima, centro = 0, 0, 2048.0
    visto = False
    for r in range(a.shape[0] // 2):
        idx = np.where(a[r])[0]
        if not len(idx):
            continue
        seg = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        if len(seg) < 2 or int(seg[-1][0]) - int(seg[0][-1]) < 400:
            # ⚠️ AQUÍ SE PARA, y no en la mitad del lienzo. El cuerpo de la
            # caja es macizo justo debajo de las astas, y más abajo vuelve a
            # abrirse —el ojo del bisel—: siguiendo se cogía un «hueco» de
            # 2.282 px que es el cristal, no las astas.
            if visto:
                break
            continue
        visto = True
        izq, der = int(seg[0][-1]), int(seg[-1][0])
        ultima = r
        if der - izq > peor:
            peor, centro = der - izq, (izq + der) / 2.0
    return peor, centro, ultima


def ancho_maximo(f):
    a = alfa(f)
    xs = np.where(a.any(0))[0]
    return int(xs.max() - xs.min() + 1), float((xs.min() + xs.max()) / 2.0)


def pon(f, s, eje_origen, eje_destino):
    """Escala una pieza y le pone su eje donde toca."""
    im = Image.open(ENTREGA + f).convert('RGBA')
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje_destino[0] - eje_origen[0] * s),
                          round(eje_destino[1] - eje_origen[1] * s)))
    return L.resize((ANCHO, ANCHO), Image.LANCZOS)


def guarda(im, ident):
    for t in TAMANOS:
        chica = (im if t == ANCHO
                 else im.resize((t, round(im.size[1] * t / float(ANCHO))), Image.LANCZOS))
        for q in CALIDADES:
            b = _io.BytesIO()
            chica.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        carpeta = os.path.join(DESTINO, str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, ident + '.avif'), 'wb').write(d)
    return len(d)


def monta():
    eje, r_ojo = hueco_de_la_caja(CAJA_PATRON)
    astas, centro_astas, hasta = hueco_entre_astas(CAJA_PATRON)
    # LA ESCALA DEL RELOJ: 45 mm de lado a lado, medidos en la fila del eje.
    ancho_caja = int(np.ptp(np.where(alfa(CAJA_PATRON)[LIENZO // 2])[0])) + 1
    por_mm = ancho_caja / 45.0
    print('CAJA · ojo en %.1f,%.1f r %.0f · hueco entre astas %d px centrado en '
          '%.1f, visible hasta la fila %d' % (eje[0], eje[1], r_ojo, astas,
                                              centro_astas, hasta))
    print('        45 mm son %d px: %.1f px por milímetro' % (ancho_caja, por_mm))
    print('        ⚠️ el hueco entre astas mide %.2f mm, y las correas de la '
          'entrega se llaman «20-18mm»' % (astas / por_mm))

    capas = {}
    for ident, f in sorted(CAJAS.items()):
        capas[ident] = pon(f, 1.0, (0, 0), (0, 0))

    # la esfera, a llenar el ojo
    a = alfa(ESFERAS['esfera-negra'])
    ys, xs = np.where(a)
    ce = ((xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0)
    re = float(np.hypot(xs - ce[0], ys - ce[1]).max())
    se = r_ojo * HOLGURA_ESF / re
    print('ESFERA · r %.0f -> %.0f (escala %.4f)' % (re, re * se, se))
    for ident, f in sorted(ESFERAS.items()):
        b = alfa(f)
        yy, xx = np.where(b)
        c = ((xx.min() + xx.max()) / 2.0, (yy.min() + yy.max()) / 2.0)
        capas[ident] = pon(f, se, c, eje)

    # las correas, a llenar el hueco entre astas
    for ident, f in sorted(CORREAS.items()):
        an, cx = ancho_maximo(f)
        s = astas * HOLGURA_COR / an
        capas[ident] = pon(f, s, (cx, LIENZO / 2.0), (centro_astas, LIENZO / 2.0))
        print('CORREA %-20s ancho %4d -> %4d (escala %.4f) · centro %.1f -> %.1f'
              % (ident, an, round(an * s), s, cx, centro_astas))
    return capas


def hoja(capas, destino):
    tiros = [('caja-acero', 'esfera-negra', 'caucho-negra'),
             ('caja-anillo-naranja', 'esfera-negra-marfil', 'caucho-naranja'),
             ('caja-anillo-azul', 'esfera-azul-sunburst', 'brazalete-acero'),
             ('caja-anillo-turquesa', 'esfera-turquesa-champagne', 'caucho-gris'),
             ('caja-anillo-burdeos', 'esfera-frambuesa-fume', 'caucho-roja'),
             ('caja-anillo-oliva', 'esfera-roja-fume', 'caucho-verde')]
    cols = 3
    filas = (len(tiros) + cols - 1) // cols
    h = Image.new('RGB', (cols * 420, filas * 420), FONDO[:3])
    for i, (caja, esf, cor) in enumerate(tiros):
        L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
        for k in (cor, esf, caja):
            L.alpha_composite(capas[k])
        h.paste(L.convert('RGB').resize((420, 420)),
                ((i % cols) * 420, (i // cols) * 420))
    h.save(destino)


if __name__ == '__main__':
    capas = monta()
    prueba = '--prueba' in sys.argv
    d = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'tortuga-capas.png') if prueba
         else os.path.join(RAIZ, 'herramientas/capturas/tortuga-capas.png'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    hoja(capas, d)
    print('\nhoja de control: ' + d)
    if prueba:
        sys.exit(0)
    print('\nPUBLICADO en assets/img/tortuga-2026/capas/')
    for ident in sorted(capas):
        print('  %-30s %6d B' % (ident, guarda(capas[ident], ident)))
