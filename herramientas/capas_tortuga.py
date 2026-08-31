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
# LAS AGUJAS VIENEN YA MONTADAS (Óscar, 31/08/2026). Las primeras llegaron
# sueltas —las tres tumbadas una al lado de otra, sin eje— y habría habido
# que buscarle a cada una su pivote y girarla. Éstas vienen armadas sobre el
# eje 2.048 y DIBUJADAS PARA LA ESFERA DE 28,5 mm, que es la misma a la que
# están dibujadas las esferas: por eso van a la escala de la esfera, no a
# una suya. Si se les midiera el largo y se escalaran aparte, la hora que
# marcan seguiría siendo la misma pero las puntas dejarían de caer donde el
# dibujante las puso.
AGUJAS = {
    'agujas-acero':       '39-agujas-tortuga-acero-inoxidable-esfera-28-5mm-eje-2048.png',
    'agujas-gris-oscuro': '38-agujas-tortuga-gris-oscuro-esfera-28-5mm-eje-2048.png',
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


def tiras_de(f):
    """Las dos tiras de una correa, en las filas del fichero de la entrega."""
    a = alfa(f)
    filas = np.where(a.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    return [(int(x[0]), int(x[-1])) for x in np.split(filas, cortes + 1)]


def pon_correa(f, s, cx, centro, baja=0, sube=0):
    """Escala una correa y pega cada tira con su propio desplazamiento.

    ⚠️ EL DESPLAZAMIENTO VA ANTES DE RECORTAR AL LIENZO, y esto costó una
    pasada. Moviendo las tiras DESPUÉS de pegarlas, lo que se había salido
    del lienzo al escalar ya estaba perdido: al meter la tira de abajo
    hacia el reloj, su otro extremo se despegaba del canto de la foto y la
    correa se acababa 109 px antes de tiempo. Escalando y pegando con el
    desplazamiento puesto, el sobrante sigue estando y sólo se recorta lo
    que sobra."""
    im = Image.open(ENTREGA + f).convert('RGBA')
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    a = np.asarray(n)[:, :, 3] > 128
    filas = np.where(a.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    t = [(int(x[0]), int(x[-1])) for x in np.split(filas, cortes + 1)]
    med = (t[0][1] + t[1][0]) // 2 if len(t) == 2 else n.height // 2
    dx = round(centro - cx * s)
    dy = round(LIENZO / 2.0 - (LIENZO / 2.0) * s)
    L = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    L.alpha_composite(n.crop((0, 0, n.width, med)), (dx, dy + baja))
    L.alpha_composite(n.crop((0, med, n.width, n.height)), (dx, dy + med - sube))
    return L


def cubierto_por_la_caja(caja, cols):
    """De qué fila a qué fila tapa la caja TODO el ancho de la correa."""
    a = alfa(caja)
    c0, c1 = cols
    filas = [r for r in range(a.shape[0]) if a[r, c0:c1 + 1].all()]
    return (filas[0], filas[-1]) if filas else (0, a.shape[0] - 1)


def pega_a_la_caja(L, arriba, abajo, margen=40):
    """Mete cada tira hasta que su punta queda DEBAJO de la caja.

    Óscar, 31/08/2026: «extrae la correa hasta la caja». Y no llegaba: la
    correa de caucho viene dibujada a menos de la mitad de tamaño, y al
    escalarla x2,22 DESDE EL CENTRO las dos puntas se van hacia fuera —el
    hueco entre ellas pasa de 876 px a 1.945—. Por abajo se quedaba 94 px
    corta y por ahí se veía el fondo entre la correa y la caja.

    Cada tira se mueve por su cuenta y SÓLO HACIA DENTRO: sacarla hacia
    fuera dejaría un hueco en el canto del lienzo, que es por donde la
    correa se sale de la foto. El brazalete, que ya llega, casi no se
    mueve."""
    a = np.asarray(L)[:, :, 3] > 128
    filas = np.where(a.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    t = [(int(x[0]), int(x[-1])) for x in np.split(filas, cortes + 1)]
    if len(t) != 2:
        return L, 0, 0
    med = (t[0][1] + t[1][0]) // 2
    baja = max(0, (arriba + margen) - t[0][1])
    sube = max(0, t[1][0] - (abajo - margen))
    if not baja and not sube:
        return L, 0, 0
    n = Image.new('RGBA', L.size, (0, 0, 0, 0))
    n.alpha_composite(L.crop((0, 0, L.width, med)), (0, baja))
    n.alpha_composite(L.crop((0, med, L.width, L.height)), (0, med - sube))
    return n, baja, sube


def pon(f, s, eje_origen, eje_destino, sin_bajar=False):
    """Escala una pieza y le pone su eje donde toca."""
    im = Image.open(ENTREGA + f).convert('RGBA')
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje_destino[0] - eje_origen[0] * s),
                          round(eje_destino[1] - eje_origen[1] * s)))
    return L if sin_bajar else L.resize((ANCHO, ANCHO), Image.LANCZOS)


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

    # las agujas, a la MISMA escala que la esfera: están dibujadas para ella
    for ident, f in sorted(AGUJAS.items()):
        b = alfa(f)
        yy, xx = np.where(b)
        largo = float(np.hypot(xx - LIENZO / 2.0, yy - LIENZO / 2.0).max())
        capas[ident] = pon(f, se, (LIENZO / 2.0, LIENZO / 2.0), eje)
        print('AGUJAS %-20s largo %.0f -> %.0f px, de un ojo de %.0f (%.0f %% del radio)'
              % (ident, largo, largo * se, r_ojo, 100 * largo * se / r_ojo))

    # las correas, a llenar el hueco entre astas Y a llegar hasta la caja
    a_caja = alfa(CAJA_PATRON)
    for ident, f in sorted(CORREAS.items()):
        an, cx = ancho_maximo(f)
        s = astas * HOLGURA_COR / an
        capa = pon_correa(f, s, cx, centro_astas)
        b = np.asarray(capa)[:, :, 3] > 128
        cols = np.where(b.any(0))[0]
        arr, aba = cubierto_por_la_caja(CAJA_PATRON, (cols.min(), cols.max()))
        _, baja, sube = pega_a_la_caja(capa, arr, aba)
        # ⚠️ Y NO SE PUEDE METER MÁS DE LO QUE SOBRA POR EL OTRO EXTREMO. La
        # correa de caucho se sale del lienzo por arriba y por abajo, así que
        # tiene de dónde; el brazalete es una pieza corta que llega justa al
        # canto, y metiéndolo se despegaba de él. Se mete lo que se puede.
        ta = tiras_de(f)
        dy = LIENZO / 2.0 - (LIENZO / 2.0) * s
        baja = int(min(baja, max(0.0, -(dy + ta[0][0] * s))))
        sube = int(min(sube, max(0.0, dy + ta[1][1] * s - (LIENZO - 1))))
        if baja or sube:                       # y se vuelve a montar, ya con el sitio
            capa = pon_correa(f, s, cx, centro_astas, baja, sube)
        capas[ident] = capa.resize((ANCHO, ANCHO), Image.LANCZOS)
        print('CORREA %-20s ancho %4d -> %4d (escala %.4f) · la caja tapa de la '
              '%d a la %d · tira de arriba %+d, la de abajo %+d'
              % (ident, an, round(an * s), s, arr, aba, baja, -sube))
    return capas


def hoja(capas, destino):
    tiros = [('caja-acero', 'esfera-negra', 'caucho-negra', 'agujas-acero'),
             ('caja-anillo-naranja', 'esfera-negra-marfil', 'caucho-naranja', 'agujas-acero'),
             ('caja-anillo-azul', 'esfera-azul-sunburst', 'brazalete-acero', 'agujas-acero'),
             ('caja-anillo-turquesa', 'esfera-turquesa-champagne', 'caucho-gris', 'agujas-gris-oscuro'),
             ('caja-anillo-burdeos', 'esfera-frambuesa-fume', 'caucho-roja', 'agujas-gris-oscuro'),
             ('caja-anillo-oliva', 'esfera-roja-fume', 'caucho-verde', 'agujas-gris-oscuro')]
    cols = 3
    filas = (len(tiros) + cols - 1) // cols
    h = Image.new('RGB', (cols * 420, filas * 420), FONDO[:3])
    for i, (caja, esf, cor, ag) in enumerate(tiros):
        L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
        for k in (cor, esf, caja, ag):
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
