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
# ⚠️ SE MONTA A 1.600, NO A 1.200 (31/08/2026). El fichero de 1.600 —el que
# ve la lupa— se sacaba AGRANDANDO el montaje de 1.200: la esfera se
# encogía a 0,55 y luego se estiraba a 1,33, y lo que se pierde por el
# camino no vuelve. La entrega da de sobra para 1.600 (el disco viene a
# 1.160 px de diámetro y el hueco de la caja pide 842), así que se monta
# grande y se baja, que es el orden bueno.
ANCHO = 1600
ALTO_CAJA = 2222
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
    a = np.asarray(Image.open(os.path.join(CAPAS, '%d/caja-brazalete-acero.avif' % ANCHO))
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


def coloca(f, eje, radio_hueco):
    """Coloca una esfera por SU pista de minutos.

    El centro de la pista va al centro del ojo de la caja, y la esfera se
    recorta en un círculo un 2 % por fuera de la punta de los índices. Ese
    círculo se lleva a medio punto por fuera del ojo, así que queda bajo el
    bisel y los índices se ven enteros, a la misma distancia del bisel en
    toda la vuelta."""
    d = mide_la_pista(f)
    r_corte = d['r_punta'] * PUNTA
    s = radio_hueco * BAJO_BISEL / r_corte
    im = recorta_circulo(Image.open(f).convert('RGBA'), d['cx'], d['cy'], r_corte)
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - d['cx'] * s), round(eje[1] - d['cy'] * s)))
    return L, s, d


# ═══════════════════════════════════════════════════════════════════
# LA PISTA DE MINUTOS SE ENCUENTRA POR SU FRECUENCIA (31/08/2026)
# ═══════════════════════════════════════════════════════════════════
# Óscar: «las esferas del Precisa no están ajustadas perfectamente a la
# caja; revisa el tamaño de las imágenes y ajusta el centro, donde se vean
# en la misma longitud los indicadores de segundos alrededor de toda la
# esfera».
#
# LO QUE NO VALÍA, y son las dos cosas que se hacían:
#   · EL DISCO DEL RECORTE. Cada entrega trae un disco de un radio y con
#     el dibujo en un sitio distinto dentro de él. Escalando y centrando
#     por el disco, el dibujo sale de un tamaño distinto en cada esfera y
#     descentrado respecto al hueco: los índices de segundo se comen por
#     un lado y sobran por el otro.
#   · ALINEAR LAS SIETE CON LA ANTRACITA. Las deja iguales entre sí, que
#     está bien, pero hereda el error de la antracita, que también estaba
#     colocada por su disco.
#
# LO QUE SÍ: medirle a cada esfera SU PISTA DE MINUTOS. Se pasa a
# coordenadas polares y se mira, anillo a anillo, la energía del armónico
# 60 a lo largo del ángulo. Sólo la pista late sesenta veces por vuelta:
# ni el canto sucio de la entrega, ni el fondo, ni los índices grandes.
#
# Y EL CENTRO SALE DE LO MISMO. Si el centro está mal, el armónico se
# emborrona: se prueba una rejilla de centros y gana el que lo deja más
# limpio. Es una medida de la propia pista, no del recorte.
#
# LUEGO SE RECORTA A UN CÍRCULO. Con la pista medida, la esfera se corta
# en un círculo concéntrico un 2 % por fuera de la punta de los índices y
# se coloca llenando el hueco de la caja. Así se van de una vez el canto
# sucio y el recorte irregular de la entrega, y los índices quedan a la
# misma distancia del bisel en toda la vuelta, que es lo que se pidió.

PUNTA = 1.020        # el corte, un 2 % por fuera de la punta de los índices
BAJO_BISEL = 1.005   # y el corte se mete medio punto bajo el bisel


def _polar(L, cx, cy, r0, r1, NR, NA=720):
    rr = np.linspace(r0, r1, NR)[:, None]
    aa = np.linspace(0, 2 * np.pi, NA, endpoint=False)[None, :]
    x = np.clip((cx + rr * np.cos(aa)).round().astype(int), 0, L.shape[1] - 1)
    y = np.clip((cy + rr * np.sin(aa)).round().astype(int), 0, L.shape[0] - 1)
    return L[y, x], rr[:, 0]


def _energia60(P):
    Q = np.nan_to_num(P - np.nanmean(P, axis=1, keepdims=True))
    return np.abs(np.fft.rfft(Q, axis=1)[:, 60])


def mide_la_pista(f, busca=14.0):
    """Centro de la pista de minutos y radio de la punta de sus índices."""
    a = np.asarray(Image.open(f).convert('RGBA')).astype(np.float32)
    m = a[:, :, 3] > 200
    L = np.where(m, a[:, :, :3].mean(2), np.nan)
    ys, xs = np.where(m)
    cx0, cy0 = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    rd = float(np.hypot(xs - cx0, ys - cy0).max())
    r0, r1 = 0.70 * rd, 1.00 * rd
    NR = int(r1 - r0)
    mejor = None
    for paso, radio in ((2.0, busca), (0.5, 2.5), (0.125, 0.6)):
        base = (mejor[1], mejor[2]) if mejor else (cx0, cy0)
        n = int(radio / paso)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                cx, cy = base[0] + i * paso, base[1] + j * paso
                e = _energia60(_polar(L, cx, cy, r0, r1, NR)[0])
                v = float(e.max())
                if mejor is None or v > mejor[0]:
                    mejor = (v, cx, cy, e)
    _, cx, cy, e = mejor
    rs = np.linspace(r0, r1, NR)
    pico = int(np.argmax(e))
    k = pico
    while k + 1 < len(e) and e[k + 1] > 0.5 * e[pico]:
        k += 1
    return dict(cx=cx, cy=cy, rd=rd, r_pico=float(rs[pico]), r_punta=float(rs[k]))


def recorta_circulo(im, cx, cy, r):
    """Deja la esfera en un círculo limpio de radio `r`, sin agujeros.

    El recorte de la entrega es irregular y trae el canto sucio: cortando
    un círculo por dentro de la porquería se acaban las dos cosas. Lo que
    quede transparente dentro del círculo —algún mordisco del recorte— se
    rellena con el píxel opaco más cercano, que a esa distancia del centro
    va a quedar debajo del bisel de todas formas."""
    a = np.asarray(im).copy()
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.hypot(x - cx, y - cy)
    dentro = d <= r
    falta = dentro & (a[:, :, 3] <= 200)
    if falta.any():
        _, idx = ndimage.distance_transform_edt(falta, return_distances=True,
                                                return_indices=True)
        a[falta] = a[idx[0], idx[1]][falta]
    borde = np.clip(r + 0.5 - d, 0.0, 1.0)      # un píxel de suavizado
    a[:, :, 3] = (a[:, :, 3] * borde).astype(np.uint8)
    return Image.fromarray(a)


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
        carpeta = os.path.join(CAPAS, str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, ident + '.avif'), 'wb').write(d)
    return len(d)


def hoja(capas, destino):
    caja = Image.open(os.path.join(CAPAS, '%d/caja-brazalete-acero.avif' % ANCHO)).convert('RGBA')
    caja = caja.crop((0, (ALTO_CAJA - ANCHO) // 2, ANCHO, (ALTO_CAJA + ANCHO) // 2))
    agujas = Image.open(os.path.join(CAPAS, '%d/agujas-plata.avif' % ANCHO)).convert('RGBA')
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
    print('Cada esfera se mide por SU pista de minutos y se recorta en círculo.')
    print()
    print('  %-24s %8s %8s %9s %9s %8s' % (
        'esfera', 'centro x', 'centro y', 'r punta', 'r disco', 'escala'))
    capas, medidas = {}, {}
    for ident, f in sorted(ESFERAS.items()):
        capas[ident], s, d = coloca(ENTREGA + f, eje, rh)
        medidas[ident] = d
        print('  %-24s %8.2f %8.2f %9.1f %9.1f %8.4f' % (
            ident, d['cx'], d['cy'], d['r_punta'], d['rd'], s))
    tocan = [d['r_punta'] * PUNTA * (rh * BAJO_BISEL / (d['r_punta'] * PUNTA)) / rh
             for d in medidas.values()]
    print()
    print('  la punta de los índices queda al %.1f %% del radio del hueco '
          'en las ocho' % (100.0 / PUNTA * BAJO_BISEL))
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
