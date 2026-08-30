# -*- coding: utf-8 -*-
"""PRECISA · coloca un juego de agujas en las capas del configurador.

    python3 herramientas/agujas_precisa.py <fichero.png> <plata|oro-rosa|negras>
    python3 herramientas/agujas_precisa.py <fichero.png> plata --prueba

POR QUÉ EXISTE. Las agujas del Precisa se colocaron a mano el 30/08/2026
y salieron largas: «el minutero y el segundero se salen de la esfera»
(Óscar). El minutero llegaba a 307 px de un radio visible de 312, o sea
que tocaba el bisel. Ponerlas a ojo otra vez sería repetir el fallo, así
que aquí se colocan MIDIENDO.

CÓMO SE COLOCA, con tres medidas y ninguna estimación:

  · EL EJE es donde coinciden dos cosas que ya están publicadas: el
    centro del hueco de la caja y el centro de la esfera. Salen a menos
    de un píxel y medio uno de otro.
  · EL TAMAÑO lo manda EL MINUTERO, que es la aguja larga y ancha: su
    punta tiene que caer en la pista de minutos de la esfera, no en el
    bisel. La pista se mide en la propia esfera —los índices aplicados
    van de 230 a 313 px de radio, con el anillo de la pista entre 295 y
    313— y se apunta a 300.
  · LA HORARIA Y EL SEGUNDERO van de propina: su largo es el que traiga
    el dibujo. Si el segundero se queda corto, es el dibujo el que hay
    que rehacer, no la escala: subirla devolvería el minutero al bisel.

El fichero de agujas llega con alfa de verdad (a diferencia de la
entrega de la Bitácora, ver [[laora-entrega-damero-sin-alfa]]), así que
aquí no hay que recortar nada.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(RAIZ, 'assets/img/precisa-2026/capas')
ANCHO = 1200                     # el lienzo en el que se mide todo
ALTO_CAJA = 1666                 # la caja va en lienzo alto
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 60000
MINUTERO_R = 300.0               # dónde cae la punta del minutero, en px de 1200
FONDO = (233, 233, 231, 255)


def _alfa(f):
    return np.asarray(Image.open(f).convert('RGBA'))[:, :, 3]


def eje_del_reloj():
    """El centro del reloj: donde coinciden el hueco de la caja y la esfera."""
    c = _alfa(os.path.join(CAPAS, '1200/caja-brazalete-acero.avif')) > 128
    h = ndimage.binary_fill_holes(c) & ~c
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    oy, ox = np.where(lab == 1 + int(np.argmax(t)))
    # el lienzo de la caja es alto: se pasa a las coordenadas del cuadrado
    caja = (float(ox.mean()), float(oy.mean()) - (ALTO_CAJA - ANCHO) / 2.0)
    radio = (ox.max() - ox.min() + 1) / 2.0

    e = _alfa(os.path.join(CAPAS, '1200/esfera-turquesa.avif')) > 128
    ys, xs = np.where(e)
    esf = ((float(xs.min()) + float(xs.max())) / 2.0,
           (float(ys.min()) + float(ys.max())) / 2.0)
    return ((caja[0] + esf[0]) / 2.0, (caja[1] + esf[1]) / 2.0), radio, caja, esf


def pista_de_minutos():
    """Hasta dónde llegan los índices aplicados de la esfera."""
    a = np.asarray(Image.open(os.path.join(CAPAS, '1200/esfera-turquesa.avif'))
                   .convert('RGBA'))
    rgb = a[:, :, :3].astype(int)
    eje, _, _, _ = eje_del_reloj()
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(x - eje[0], y - eje[1])
    ind = ((a[:, :, 3] > 200) & (rgb.mean(2) > 190)
           & (rgb.max(2) - rgb.min(2) < 45) & (r > 200) & (r < 330))
    rr = r[ind]
    # p10 y no p2: por debajo hay flecos del logo y del waffle brillante, y el
    # borde interior de las barras está en 230, no en 208.
    return float(np.percentile(rr, 10)), float(np.percentile(rr, 98))


def brazos(im):
    """El eje del juego y el largo de cada aguja, en píxeles del fichero.

    El buje es el punto más grueso del dibujo; quitándolo, lo que queda
    suelto son las agujas. El MINUTERO es el brazo largo Y ancho: el
    segundero llega lejos pero es una aguja, y ordenar solo por largo
    los confunde en cuanto el dibujo cambia."""
    m = _alfa(im) > 128 if isinstance(im, str) else (
        np.asarray(im.convert('RGBA'))[:, :, 3] > 128)
    dt = ndimage.distance_transform_edt(m)
    i = np.unravel_index(np.argmax(dt), dt.shape)
    nucleo = dt > dt[i] * 0.7
    lab, n = ndimage.label(nucleo)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    by, bx = np.where(lab == 1 + int(np.argmax(t)))
    eje = (float(bx.mean()), float(by.mean()))
    y, x = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    r = np.hypot(x - eje[0], y - eje[1])
    lab2, k = ndimage.label(m & (r > dt[i] * 1.6))
    trozos = []
    for q in range(1, k + 1):
        s = lab2 == q
        if s.sum() < 400:
            continue
        trozos.append({'largo': float(r[s].max()), 'area': int(s.sum())})
    trozos.sort(key=lambda d: -d['area'])
    minutero = max(trozos[:2], key=lambda d: d['largo'])   # de los dos anchos, el largo
    horaria = min(trozos[:2], key=lambda d: d['largo'])
    finos = [d for d in trozos[2:]]
    segundero = max(finos, key=lambda d: d['largo']) if finos else None
    return eje, minutero, horaria, segundero


def guarda(im, ident):
    for t in TAMANOS:
        alto = round(im.size[1] * t / float(ANCHO))
        chica = im.resize((t, alto), Image.LANCZOS)
        for q in CALIDADES:
            b = _io.BytesIO()
            chica.save(b, 'AVIF', quality=q)
            datos = b.getvalue()
            if len(datos) <= PESO or q == CALIDADES[-1]:
                break
        carpeta = os.path.join(CAPAS, str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, ident + '.avif'), 'wb').write(datos)
        print('  %-5d %6d B' % (t, len(datos)))


def coloca(origen):
    im = Image.open(origen).convert('RGBA')
    eje, radio, caja, esf = eje_del_reloj()
    dentro, fuera = pista_de_minutos()
    anc, minutero, horaria, segundero = brazos(im)
    s = MINUTERO_R / minutero['largo']
    print('EJE DEL RELOJ %.2f, %.2f   (hueco de la caja %.2f,%.2f · esfera %.2f,%.2f)'
          % (eje[0], eje[1], caja[0], caja[1], esf[0], esf[1]))
    print('RADIO VISIBLE %.1f px · índices de %.0f a %.0f · minutero a %.0f'
          % (radio, dentro, fuera, MINUTERO_R))
    print('ESCALA %.4f' % s)
    print('  minutero  %6.1f -> %5.1f px' % (minutero['largo'], minutero['largo'] * s))
    print('  horaria   %6.1f -> %5.1f px' % (horaria['largo'], horaria['largo'] * s))
    if segundero:
        print('  segundero %6.1f -> %5.1f px%s'
              % (segundero['largo'], segundero['largo'] * s,
                 '   ⚠️ no llega a los índices' if segundero['largo'] * s < dentro else ''))
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - anc[0] * s), round(eje[1] - anc[1] * s)))
    return L


def hoja(capa, destino):
    L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
    L.alpha_composite(Image.open(os.path.join(CAPAS, '1200/esfera-turquesa.avif'))
                      .convert('RGBA'))
    c = Image.open(os.path.join(CAPAS, '1200/caja-brazalete-acero.avif')).convert('RGBA')
    L.alpha_composite(c.crop((0, (ALTO_CAJA - ANCHO) // 2,
                              ANCHO, (ALTO_CAJA + ANCHO) // 2)))
    L.alpha_composite(capa)
    L.convert('RGB').save(destino)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) < 2:
        sys.exit(__doc__)
    origen, color = args[0], args[1]
    capa = coloca(origen)
    prueba = '--prueba' in sys.argv
    salida = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'precisa-agujas.png')
              if prueba else os.path.join(RAIZ, 'herramientas/capturas/precisa-agujas.png'))
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    hoja(capa, salida)
    print('\nhoja de control: ' + salida)
    if prueba:
        sys.exit(0)
    print('\nPUBLICADO agujas-%s' % color)
    guarda(capa, 'agujas-' + color)
