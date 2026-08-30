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

# Dónde cae el borde del hueco sobre el radio del recorte DEL PATRÓN.
CORTE = 0.96
PATRON_ESF = 'esfera-antracita'    # la que Óscar dio por buena (30/08/2026)

# ⚠️ LAS DEMÁS NO SE MIDEN POR SU DISCO, SE ALINEAN CON EL PATRÓN.
# Óscar, 30/08/2026: «la única esfera que veo bien colocada es la de
# antracita, revisa por qué es la única». Y era esto: el disco recortado
# de cada entrega tiene un radio distinto —de 578 a 597 px— y encima el
# DIBUJO ocupa una fracción distinta de ese disco, del 0,919 al 0,964.
# Escalando por el disco, como se hacía, cada esfera salía con el dibujo
# de un tamaño: hasta un 4,7 % de diferencia entre la blanca y la azul
# hielo. Sólo una podía estar bien, y era la antracita.
#
# Medirle a cada una su pista de minutos tampoco salía: el borde sucio de
# la entrega —el gajo blanco del canto de la antracita— da más energía que
# la propia pista y se llevaba la medida veinte píxeles hacia fuera.
#
# Lo que sí sale es COMPARAR cada dibujo con el de la antracita por
# correlación de bordes: son el mismo dibujo en otro color y se solapan
# casi perfecto.
#
# La antracita se queda EXACTAMENTE donde está —por su disco, como hasta
# ahora— y las otras siete se alinean con ella.

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
    """Centro y radio del recorte. Ya sólo sirve para acotar la búsqueda."""
    a = np.asarray(Image.open(f).convert('RGBA'))[:, :, 3] > 200
    ys, xs = np.where(a)
    cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    r = float(np.hypot(xs - cx, ys - cy).max())
    return (cx, cy), r


def _bordes(f, lado=320):
    """Mapa de bordes normalizado, chico, para comparar dibujos."""
    a = np.asarray(Image.open(f).convert('RGBA')).astype(np.float32)
    m = a[:, :, 3] > 200
    L = a[:, :, :3].mean(2) * m
    g = np.hypot(ndimage.sobel(L, 1), ndimage.sobel(L, 0)) * m
    k = lado / float(max(g.shape))
    g = ndimage.zoom(g, k, order=1)
    g = g - g.mean()
    n = np.linalg.norm(g)
    return (g / n if n else g), k


def alinea_con_patron(f, ref, kref):
    """Qué escala y qué desplazamiento llevan el dibujo de `f` sobre el patrón.

    Óscar, 30/08/2026: «la única esfera que veo bien colocada es la de
    antracita... para que todas las demás hagan lo mismo». Pues eso: en vez
    de medirle a cada una su pista —que el borde sucio de la entrega
    despista—, se COMPARA cada dibujo con el de la antracita. Son el mismo
    dibujo en otro color, así que el mapa de bordes se solapa casi perfecto
    y la escala sale sin discutir.

    La correlación va por FFT. Hacerla a lo bruto con `ndimage.correlate`
    y un núcleo del tamaño de la imagen se come la memoria y el proceso
    muere (exit 137): son 320^4 cuentas por cada escala que se prueba."""
    g, k = _bordes(f)
    H, W = ref.shape
    F = np.fft.fft2(ref)
    mejor = None
    for esc in np.arange(0.90, 1.1001, 0.005):
        z = ndimage.zoom(g, esc, order=1)
        h = np.zeros_like(ref)
        oy, ox = (H - z.shape[0]) // 2, (W - z.shape[1]) // 2
        sy = slice(max(oy, 0), max(oy, 0) + min(z.shape[0], H))
        sx = slice(max(ox, 0), max(ox, 0) + min(z.shape[1], W))
        zy = slice(max(-oy, 0), max(-oy, 0) + (sy.stop - sy.start))
        zx = slice(max(-ox, 0), max(-ox, 0) + (sx.stop - sx.start))
        h[sy, sx] = z[zy, zx]
        c = np.real(np.fft.ifft2(np.fft.fft2(h) * np.conj(F)))
        i = np.unravel_index(np.argmax(c), c.shape)
        dy = i[0] - (H if i[0] > H // 2 else 0)
        dx = i[1] - (W if i[1] > W // 2 else 0)
        v = float(c[i])
        if mejor is None or v > mejor[0]:
            mejor = (v, float(esc), dx, dy)
    _, esc, dx, dy = mejor
    return esc, -dx / k, -dy / k, mejor[0]


def coloca(f, eje, radio_hueco, patron=None):
    """Coloca una esfera. El patrón va por su disco; las demás, por él."""
    im = Image.open(f).convert('RGBA')
    c, r = disco(f)
    eje = (eje[0], eje[1] + BAJADA)
    if patron is None:
        s = (radio_hueco + BAJADA) / (CORTE * r)
        cx, cy = c
    else:
        ref, kref, cpat, spat = patron
        esc, dx, dy, _ = alinea_con_patron(f, ref, kref)
        # el dibujo de esta esfera es `esc` veces el del patrón y está
        # corrido (dx, dy) respecto de él: se deshace lo uno y lo otro.
        s = spat / esc
        cx, cy = cpat[0] - dx, cpat[1] - dy
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - cx * s), round(eje[1] - cy * s)))
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
    print('La antracita manda; las otras siete se alinean con su dibujo.')
    print('La esfera baja %.1f px (2 grados de arco) y crece lo mismo para taparlo.' % BAJADA)
    capas = {}
    # el patrón primero, y por su cuenta: es el que Óscar dio por bueno
    fp = ENTREGA + ESFERAS[PATRON_ESF]
    capas[PATRON_ESF], sp, rp = coloca(fp, eje, rh)
    cpat, _ = disco(fp)
    ref, kref = _bordes(fp)
    print('  %-24s PATRÓN · recorte r=%5.1f  escala %.4f' % (PATRON_ESF, rp, sp))
    for ident, f in sorted(ESFERAS.items()):
        if ident == PATRON_ESF:
            continue
        capas[ident], s, r = coloca(ENTREGA + f, eje, rh, (ref, kref, cpat, sp))
        print('  %-24s dibujo x%.4f del patrón  ->  escala %.4f' % (ident, sp / s, s))
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
