# -*- coding: utf-8 -*-
"""BIBLIOTECA · prepara las correas y brazaletes de la entrega «correas-x20».

    python3 herramientas/preparar_correa_x20.py <fichero.png> <ident> [--prueba]

LA ENTREGA NO VIENE COMO PIDE LA NORMA. Llega a 1024x1536 en RGB, con
fondo de estudio (gris ~235) y sombra, cuando la biblioteca quiere PNG
con alfa, sin sombra y a 4096x5688. Aquí se le quita el fondo y se lleva
al lienzo de la casa.

EL FONDO SE VA SOLO, que para eso es liso: se mide el gris del marco del
lienzo —siempre fondo— y es fondo todo lo que se le parezca y encima sea
neutro. No hace falta el lío del damero de otras entregas. La sombra se
va con el mismo umbral porque es suave y se queda a menos de doce
niveles del fondo; lo que la delata es que no tiene canto.

EL TAMAÑO NO SE INVENTA: se copia de la pieza que ya está publicada. Se
mide el ancho de la correa VIEJA justo en el borde de las asas y se
escala la nueva hasta dar el mismo, y se le hace coincidir el extremo de
dentro —el que se mete bajo la caja—. Así la pieza nueva entra en el
hueco exactamente igual que la que sustituye, y `auditar_correas.py`
sigue diciendo 0.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLIO = os.path.join(RAIZ, 'assets/img/componentes/correas')
ANCHO, ALTO = 4096, 5688
ASAS = (1412, 2696)
PATRON = 'piel-vintage-negra'      # la referencia: ya está en lienzo alto y pasa la auditoría


def sin_fondo(f, tol=12, sat=18):
    """Alfa de una foto de estudio con fondo liso."""
    a = np.asarray(Image.open(f).convert('RGB')).astype(float)
    L = a.mean(2)
    s = a.max(2) - a.min(2)
    marco = np.zeros(L.shape, bool)
    marco[:40, :] = marco[-40:, :] = True
    marco[:, :40] = marco[:, -40:] = True
    gris = float(np.median(L[marco]))
    m = (np.abs(L - gris) > tol) | (s > sat)
    m = ndimage.binary_closing(m, np.ones((5, 5)))
    lab, n = ndimage.label(m)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    dos = np.isin(lab, [int(i) + 1 for i in np.argsort(t)[::-1][:2]])
    return ndimage.binary_fill_holes(dos), a


def tiras(m):
    filas = np.where(m.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    return [(int(t[0]), int(t[-1])) for t in np.split(filas, cortes + 1)]


def medidas(m):
    """Ancho en el extremo de dentro de cada tira, y dónde está ese extremo."""
    t = tiras(m)
    if len(t) != 2:
        sys.exit('✗ esperaba dos tiras y hay %d' % len(t))
    arriba, abajo = t
    return {'fin_arriba': arriba[1], 'ini_abajo': abajo[0],
            # EL ANCHO QUE MANDA ES EL MÁXIMO, no el del extremo de dentro:
            # estos brazaletes van de 20 a 16 mm, y midiendo el extremo la
            # escala salía corta y en las filas de las asas se quedaba en
            # 830 px para un hueco de 1.284.
            'ancho': int(max(m[r].sum() for r in range(m.shape[0])))}


def patron():
    f = os.path.join(BIBLIO, '1600', PATRON + '.avif')
    a = np.asarray(Image.open(f).convert('RGBA'))[:, :, 3] > 128
    k = ANCHO / float(a.shape[1])
    m = medidas(a)
    return {kk: vv * k for kk, vv in m.items()}


def prepara(origen, holgura=1.0):
    m, rgb = sin_fondo(origen)
    mio = medidas(m)
    ref = patron()
    # ⚠️ LA HOLGURA es para los brazaletes que van de 20 a 16 mm: igualando
    # el ancho máximo al del patrón, en las filas de las asas se quedaban
    # entre 8 y 14 px cortos y `auditar_correas.py` los cantaba. Lo que
    # sobra no se ve —la correa va detrás de la caja—, lo que falta sí.
    s = ref['ancho'] / mio['ancho'] * holgura
    im = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA')
    im.putalpha(Image.fromarray(
        np.clip(ndimage.gaussian_filter((m * 255).astype(np.float32), 0.8), 0, 255).astype(np.uint8)))
    n = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    # el centro del hueco entre las dos tiras cae donde lo tiene el patrón
    mio_centro = (mio['fin_arriba'] + mio['ini_abajo']) / 2.0 * s
    ref_centro = (ref['fin_arriba'] + ref['ini_abajo']) / 2.0
    ys, xs = np.where(np.asarray(n)[:, :, 3] > 128)
    # OJO: ASAS son COLUMNAS, no filas. El hueco entre las asas va de la
    # 1412 a la 2696, o sea centrado en la 2054 y no en la 2048 del lienzo.
    dx = (ASAS[0] + ASAS[1]) / 2.0 - (xs.min() + xs.max()) / 2.0
    dy = ref_centro - mio_centro
    L = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(dx), round(dy)))
    return L, s, mio, ref


if __name__ == '__main__':
    args = [a for i, a in enumerate(sys.argv[1:])
            if not a.startswith('--') and not (i and sys.argv[i] == '--holgura')]
    if len(args) < 2:
        sys.exit(__doc__)
    origen, ident = args[0], args[1]
    holgura = float(sys.argv[sys.argv.index('--holgura') + 1]) if '--holgura' in sys.argv else 1.0
    capa, s, mio, ref = prepara(origen, holgura)
    a = np.asarray(capa)[:, :, 3] > 128
    ys, xs = np.where(a)
    ancho = xs.max() - xs.min() + 1
    hueco = ASAS[1] - ASAS[0]
    print('%-38s escala %.4f · ancho %d para un hueco de %d %s · centro en x=%.0f (toca 2054)' % (
        ident, s, ancho, hueco, 'OK' if ancho >= hueco else '✗ SE QUEDA CORTA',
        (xs.min() + xs.max()) / 2.0))
    salida = os.path.join(os.environ.get('TMPDIR', '/tmp'), ident + '.png')
    capa.save(salida)
    print('   ' + salida)
