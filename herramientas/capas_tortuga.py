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

⚠️ LAS ASTAS SE CIERRAN A 20 mm, y la caja mide 44 (Óscar, 31/08/2026).
El hueco venía de 22 y pico y las correas de la entrega se llaman
«20-18mm», así que se cierran las astas: lo hace
`herramientas/cajas_tortuga.py`, que hay que pasar ANTES que esto.
⚠️ Y SON 44 mm, NO 45, aunque el fichero del patrón se llame «45mm»: lo
dice la ficha y lo confirmó Óscar. De ahí salen 73,0 px por milímetro y
una ranura de 1.460 px.

LA CORREA PROFESIONAL (Óscar, 01/09/2026: «monta esta correa de caucho en
el tortuga y la nombras caucho profesional»). Es la número 47 de la
entrega y viene dibujada entera —hebilla, trabilla, tabla de tiempos sin
descompresión y su escalera de agujeros—, así que hay dos cosas que no se
pueden hacer con ella como con las otras seis: medirla por su punto más
ancho, que es la HEBILLA y no el asa, y pasarle `tapa_los_agujeros`, que
está para un defecto que ésta no tiene. De ahí `POR_LAS_PUNTAS` y
`SIN_TAPAR`. Lo que se ve en el visor son los 17 mm de correa que asoman
a cada lado de la caja; la tabla y los agujeros caen fuera del marco, y
sólo el rótulo «N.D.LIMITS» llega a asomar al alejarse.
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

# ⚠️ LAS CAJAS SE LEEN DE `preparadas/`, NO DE LA ENTREGA (Óscar,
# 31/08/2026: «Las astas se cierran a 20»). Las once llegan a tamaños
# distintos —la lisa un 7 % más pequeña que las de anillo— y con el hueco
# entre astas a 22,4 mm, que no es lo que miden las correas. Antes de
# montar nada hay que pasarlas por `herramientas/cajas_tortuga.py`, que las
# deja todas del mismo tamaño, centradas por el ojo, y con la ranura a
# 1.428 px, o sea 20 mm clavados. Si esa carpeta no existe, se ejecuta ese
# guión primero.
CAJA_PATRON = 'preparadas/19-caja-tortuga-45mm-eje-2048.png'
MM_CAJA = 44.0                   # la caja, de lado a lado (lo dice la ficha)
HOLGURA_ESF = 1.005              # la esfera se mete un pelín bajo el anillo
# LAS AGUJAS NO LLEGAN AL ÍNDICE (Óscar, 31/08/2026: «la aguja del minutero
# tiene que señalar el indicador pero el indicador no puede ser tapado, al
# igual que el segundero, y por tanto la aguja de las horas se encogerá en
# la misma proporción»). Iban a la escala de la ESFERA, así que el minutero
# se plantaba en 1.072 px con los índices empezando en 824: los cruzaba
# enteros. Ahora las tres se escalan para que la punta del minutero se pare
# un pelo antes del índice al que apunta, y las otras dos bajan con ella.
# EL TOPE DE LAS AGUJAS ES LA PISTA DE SEGUNDOS (Óscar, 01/09/2026: «el
# segundero y el minutero quedan siempre justo antes del indicador de
# segundos, dejan ver la línea del indicador —por ejemplo segundo 14— pero
# no lo tapan»). Antes el tope era el índice redondo; ahora es la pista.
HUECO_PISTA = 18.0               # lo que se paran antes de tocarla (px del 4.096)
HOLGURA_COR = 1.010              # y la correa, un pelín bajo las astas
# EL LIENZO ALTO DE LAS CORREAS (Óscar, 31/08/2026: «cuando hacemos zoom es
# precisamente para que se vea más correa, como ya funciona con las otras
# correas en trinchera y lunar»). Es la norma de la casa desde el 29/08: la
# correa se publica en un lienzo 4.096 ÷ 0,72 = 5.688 de alto y se coloca
# por su centro. En primer plano el marco cuadrado la recorta y se ve la
# franja de siempre; al alejarse al 72 % cabe entera y aparece el resto de
# la tira. Publicada cuadrada —como estaba el Tortuga— al alejarse no sale
# más correa: sale su corte flotando dentro del marco.
ALTO_COR = 5688
DESP_COR = (ALTO_COR - LIENZO) // 2   # de fila de la caja a fila de la correa
MARGEN_COR = 40                  # lo que la punta se mete bajo la caja
SOBRA_COR = 1.02                 # y lo que la correa se mete bajo las astas
DESTENSA = 180                   # las filas que tarda en volver a su ancho natural

CAJAS = {
    'caja-acero':            'preparadas/19-caja-tortuga-45mm-eje-2048.png',
    'caja-anillo-naranja-grueso': 'preparadas/22-caja-tortuga-anillo-naranja-grueso-escala-negra.png',
    'caja-anillo-plata':     'preparadas/23-caja-tortuga-anillo-plata-escala-negra.png',
    'caja-anillo-azul':      'preparadas/24-caja-tortuga-anillo-azul-escala-negra.png',
    'caja-anillo-verde':     'preparadas/25-caja-tortuga-anillo-verde-escala-negra.png',
    'caja-anillo-negro':     'preparadas/26-caja-tortuga-anillo-negro-escala-clara.png',
    'caja-anillo-oliva':     'preparadas/27-caja-tortuga-anillo-oliva-escala-negra.png',
    'caja-anillo-burdeos':   'preparadas/28-caja-tortuga-anillo-burdeos-escala-negra.png',
    'caja-anillo-turquesa':  'preparadas/29-caja-tortuga-anillo-turquesa-escala-negra.png',
    'caja-anillo-acero':     'preparadas/30-caja-tortuga-anillo-acero-liso.png',
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
# LAS AGUJAS VUELVEN A SER LAS DEL DIBUJANTE (Óscar, 01/09/2026: «en el
# Tortuga vuelve a colocar las agujas originales»). Las mandó ya dibujadas
# a las 10:10 con el segundero en el 37, así que aquí NO se gira nada: la
# `agujas_en_hora.py` que las ponía en hora a base de girarlas ya no hace
# falta para este modelo, y con ella se va el sombreado girado.
AGUJAS = {
    'agujas-acero':       '41-agujas-tortuga-acero-inoxidable-10-10-37-esfera-28-5mm-eje-2048.png',
    'agujas-gris-oscuro': '40-agujas-tortuga-gris-muy-oscuro-10-10-37-esfera-28-5mm-eje-2048.png',
}
CORREAS = {
    'caucho-negra':      '32-correa-caucho-negra-buzo-20-18mm-eje-2048.png',
    'caucho-azul-marino': '33-correa-caucho-azul-marino-buzo-20-18mm-eje-2048.png',
    'caucho-gris':       '34-correa-caucho-gris-buzo-20-18mm-eje-2048.png',
    'caucho-verde':      '35-correa-caucho-verde-buzo-20-18mm-eje-2048.png',
    'caucho-roja':       '36-correa-caucho-roja-buzo-20-18mm-eje-2048.png',
    'caucho-naranja':    '37-correa-caucho-naranja-buzo-20-18mm-eje-2048.png',
    # LA PROFESIONAL LLEGA CON LA HEBILLA DENTRO DEL CUADRO (Óscar,
    # 01/09/2026: «monta esta correa de caucho en el tortuga y la nombras
    # caucho profesional»). Es la única de la entrega que se dibuja entera
    # —hebilla, trabilla, tabla de tiempos sin descompresión y la escalera
    # de agujeros—, y la hebilla es MÁS ANCHA que la correa: 373 px contra
    # 359 en el asa. Por eso ésta se mide por las puntas y no por el máximo.
    'caucho-profesional': '47-correa-caucho-azul-lujo-4k-hueco-caja-44mm.png',
    'brazalete-acero':   '20-brazalete-tortuga-eje-2048.png',
}
# ⚠️ SE MIDE EN LAS PUNTAS, NO EN EL MÁXIMO, y sólo en las que hace falta.
# Lo que tiene que llenar la ranura es el ancho DEL ASA, que es donde la
# correa entra: en las seis de caucho y en el brazalete el sitio más ancho
# del dibujo es justo ése, así que el número no cambia y no se toca nada de
# lo publicado. En la profesional el sitio más ancho es la hebilla, y
# midiendo por el máximo la correa entraba un 4 % estrecha en el asa.
POR_LAS_PUNTAS = ('caucho-profesional',)
# Y NO SE LE TAPAN LOS AGUJEROS. `tapa_los_agujeros` está para el defecto de
# las seis de caucho, que traen cinco agujeros pegados a la caja donde sólo
# hay uno; ésta trae su escalera de agujeros bien dibujada y a su distancia.
SIN_TAPAR = ('caucho-profesional',)


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


def borde_del_aro(f):
    """El borde interior del aro de minutos de esa caja: por ahí se ve la esfera."""
    from scipy import ndimage
    al = alfa(f)
    h = ndimage.binary_fill_holes(al) & ~al
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    ys, xs = np.where(lab == 1 + int(np.argmax(t)))
    return float(np.hypot(xs - xs.mean(), ys - ys.mean()).max())


def punta_del_indice(fondo=120.0):
    """Hasta dónde llega el índice más largo de las ocho esferas, hacia fuera.

    ⚠️ HAY QUE DESCARTAR EL CANTO DE LA ESFERA. La de turquesa champán tiene
    el borde claro y cálido, así que pasa por lumen igual que un índice y
    daba una «punta» de 1.800: el radio entero de la esfera. Un índice tiene
    FONDO —del orden de 400 px del centro a la punta—; el canto es una tira
    de veinte. Con eso se distinguen sin mirar ninguno en concreto."""
    from scipy import ndimage
    lejos = 0.0
    for f in sorted(ESFERAS.values()):
        a = np.asarray(Image.open(ENTREGA + f).convert('RGBA'))
        al = a[:, :, 3] > 128
        rgb = a[:, :, :3].astype(int)
        lume = (al & (rgb[:, :, 0] > 150) & (rgb[:, :, 1] > 150) &
                (rgb[:, :, 2] < rgb[:, :, 1] - 8))
        lab, n = ndimage.label(lume)
        c = LIENZO / 2.0 - 0.5
        for k in range(1, n + 1):
            m = lab == k
            if m.sum() < 8000:
                continue
            ys, xs = np.where(m)
            d = np.hypot(xs - c, ys - c)
            if d.max() - d.min() < fondo:
                continue
            lejos = max(lejos, float(d.max()))
    return lejos


def borde_de_la_pista(paso=4):
    """Dónde empieza, hacia dentro, la pista de segundos de la esfera.

    SE CONOCE POR EL ARMÓNICO 60, que es el mismo truco de la Precisa: la
    pista es lo ÚNICO del dibujo que se repite sesenta veces por vuelta. Se
    remuestrea la esfera en círculos, se mira la fuerza de ese armónico en
    cada radio y se coge el pico; desde el pico se camina hacia dentro
    mientras siga valiendo más de la mitad, y ahí está el borde.

    Se miden LAS OCHO esferas y manda la que trae la pista más adentro: la
    capa de agujas es una sola y no puede taparla en ninguna."""
    c = LIENZO / 2.0 - 0.5
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    dentro = []
    for f in sorted(ESFERAS.values()):
        a = np.asarray(Image.open(ENTREGA + f).convert('RGBA'))
        g = np.where(a[:, :, 3] > 128, a[:, :, :3].mean(2), 0).astype(np.float32)
        rr, vv = [], []
        for r in range(1300, 1790, paso):
            xs = np.round(c + r * np.sin(th)).astype(int).clip(0, LIENZO - 1)
            ys = np.round(c - r * np.cos(th)).astype(int).clip(0, LIENZO - 1)
            v = g[ys, xs]
            rr.append(r)
            vv.append(abs(np.fft.rfft(v - v.mean())[60]))
        vv = np.asarray(vv)
        i = int(np.argmax(vv))
        j = i
        while j > 0 and vv[j - 1] >= vv[i] * 0.55:
            j -= 1
        dentro.append(rr[j])
    return float(min(dentro))


def ancho_maximo(f):
    a = alfa(f)
    xs = np.where(a.any(0))[0]
    return int(xs.max() - xs.min() + 1), float((xs.min() + xs.max()) / 2.0)


def ancho_en_las_puntas(f):
    """Lo que mide la correa en el asa: las puntas que miran a la caja.

    Se toma la mediana de doce filas de cada punta —la primera llega
    difuminada y miente— y manda la más ancha de las dos, que es la que
    tiene que caber."""
    al = alfa(f)
    filas = np.where(al.any(1))[0]
    t = [(int(x[0]), int(x[-1]))
         for x in np.split(filas, np.where(np.diff(filas) > 1)[0] + 1)]
    if len(t) != 2:
        return ancho_maximo(f)
    anchos, centros = [], []
    for ys in (range(t[0][1] - 11, t[0][1] + 1), range(t[1][0], t[1][0] + 12)):
        w = [np.where(al[y])[0] for y in ys if al[y].any()]
        anchos.append(np.median([int(np.ptp(i)) + 1 for i in w]))
        centros.append(np.median([(int(i.min()) + int(i.max())) / 2.0 for i in w]))
    return int(max(anchos)), float(np.mean(centros))


def tiras_de(f):
    """Las dos tiras de una correa, en las filas del fichero de la entrega."""
    a = alfa(f)
    filas = np.where(a.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    return [(int(x[0]), int(x[-1])) for x in np.split(filas, cortes + 1)]


def pon_correa(f, s, cx, centro, baja=0, sube=0):
    """Escala una correa y pega cada tira con su propio desplazamiento.

    Va sobre el LIENZO ALTO: el eje del reloj cae en el centro del lienzo
    alto, que es donde el navegador centra la imagen, así que una fila `r`
    de la caja es la fila `r + DESP_COR` de la correa.

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
    dy = round(LIENZO / 2.0 - (LIENZO / 2.0) * s) + DESP_COR
    L = Image.new('RGBA', (LIENZO, ALTO_COR), (0, 0, 0, 0))
    L.alpha_composite(n.crop((0, 0, n.width, med)), (dx, dy + baja))
    L.alpha_composite(n.crop((0, med, n.width, n.height)), (dx, dy + med - sube))
    return L


def _tramo_recto(a, y0, y1, desde_arriba):
    """Cuántas filas seguidas del extremo de FUERA van rectas.

    ⚠️ SE ESPEJA SÓLO EL TRAMO RECTO, no la tira entera. Espejando entera,
    lo que se repetía era el eslabón de la caja —el que lleva el corte
    curvo para abrazarla—, y el brazalete salía con unos ojales en forma de
    lente cada dos eslabones. Recto es donde la fila es un solo trozo y
    mide casi lo que la tira más ancha."""
    al = a[y0:y1 + 1, :, 3] > 128
    anchos = al.sum(1)
    tope = anchos.max()
    n = 0
    for i in (range(len(al)) if desde_arriba else range(len(al) - 1, -1, -1)):
        idx = np.where(al[i])[0]
        if not len(idx) or anchos[i] < tope * 0.93:
            break
        if len(np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)) > 1:
            break
        n += 1
    return max(n, 2)


def tapa_los_agujeros(L, dejar=1):
    """Deja en cada tira sólo el agujero de más afuera y tapa los demás.

    Óscar, 31/08/2026: «al trozo de la correa de abajo le has hecho más
    agujeros de los que realmente tiene; haciendo zoom sólo se debería de
    ver uno, el que está más abajo del todo; los cuatro más próximos a la
    caja no existen, así que tápalos».

    Vienen así en la entrega: la cola del caucho llega con cinco agujeros
    seguidos. Se buscan los huecos cerrados de cada tira, se ordenan por lo
    lejos que están del eje del reloj y se tapa todo menos el último.

    El relleno sale del color que tiene al lado —el más cercano que sea
    opaco— y se suaviza un poco: copiando un cuadrado de goma se veía el
    parche, porque el caucho lleva un degradado de luz a lo largo."""
    from scipy import ndimage
    a = np.asarray(L).astype(np.float32).copy()
    al = a[:, :, 3] > 128
    filas = np.where(al.any(1))[0]
    if not len(filas):
        return L
    tiras = np.split(filas, np.where(np.diff(filas) > 1)[0] + 1)
    eje = a.shape[0] / 2.0
    tapar = np.zeros(al.shape, bool)
    for t in tiras:
        y0, y1 = int(t[0]), int(t[-1])
        trozo = al[y0:y1 + 1]
        hueco = ndimage.binary_fill_holes(trozo) & ~trozo
        lab, n = ndimage.label(hueco)
        cand = []
        for k in range(1, n + 1):
            m = lab == k
            if m.sum() < 200:            # una mota no es un agujero
                continue
            ys, xs = np.where(m)
            cand.append((abs((ys.mean() + y0) - eje), m))
        if len(cand) <= dejar:
            continue
        cand.sort(key=lambda c: -c[0])   # el más lejos del reloj, primero
        for _, m in cand[dejar:]:
            tapar[y0:y1 + 1][m] = True
    if not tapar.any():
        return L
    # ⚠️ Y SE TAPA UN POCO MÁS ANCHO QUE EL AGUJERO. El dibujo lleva
    # alrededor de cada agujero una sombra de avellanado, y rellenando sólo
    # lo transparente quedaba el anillo oscuro flotando: cinco aros donde
    # antes había cinco agujeros. Se ensancha catorce píxeles, que es lo que
    # mide esa sombra, y desaparece con él.
    tapar = ndimage.binary_dilation(tapar, iterations=14)
    lejos = ndimage.distance_transform_edt(tapar | ~al, return_distances=False,
                                           return_indices=True)
    relleno = a[lejos[0], lejos[1]]
    suave = np.dstack([ndimage.gaussian_filter(relleno[:, :, c], 8) for c in range(4)])
    a[tapar] = suave[tapar]
    a[:, :, 3][tapar] = 255
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGBA')


def alarga_las_tiras(L):
    """Alarga cada tira, espejándola, hasta el canto del lienzo alto.

    ⚠️ SÓLO HACE FALTA PARA EL BRAZALETE. Las de caucho vienen dibujadas
    largas y de sobra llegan; el brazalete de la entrega son dos muñones de
    unos 700 px —el eslabón de la caja y poco más—, así que sacándolo hacia
    fuera se quedaba a 900 px del canto y en el visor se le veía el corte
    flotando. Se refleja sobre sí mismo: como los eslabones son iguales, el
    empalme cae en pixel continuo y no se nota la costura.

    Se refleja SÓLO por el lado de fuera; el de dentro es la punta que va
    bajo la caja y no se toca."""
    a = np.asarray(L).copy()
    al = a[:, :, 3] > 128
    filas = np.where(al.any(1))[0]
    if not len(filas):
        return L
    t = [(int(x[0]), int(x[-1]))
         for x in np.split(filas, np.where(np.diff(filas) > 1)[0] + 1)]
    if len(t) != 2:
        return L
    (y0, y1), (y2, y3) = t
    alto = a.shape[0]
    if y0 > 0:
        n = _tramo_recto(a, y0, y1, True)
        bloque = a[y0:y0 + n]
        a[0:y0] = np.pad(bloque, ((y0, 0), (0, 0), (0, 0)), mode='reflect')[0:y0]
    if y3 < alto - 1:
        falta = alto - 1 - y3
        n = _tramo_recto(a, y2, y3, False)
        bloque = a[y3 + 1 - n:y3 + 1]
        a[y3 + 1:] = np.pad(bloque, ((0, falta), (0, 0), (0, 0)),
                            mode='reflect')[-falta:]
    return Image.fromarray(a)


def rellena_las_astas(L, caja, centro):
    """Ensancha la correa, fila a fila, hasta llenar la ranura de las astas.

    Óscar, 31/08/2026: «la correa de abajo tiene que salir más de debajo de
    la caja, tiene que unir su extremo a la caja, y el de arriba igual».

    Y no era sacarla más: sacada un pelo más ya asoma su propio corte. Lo
    que pasa es que LA CORREA VIENE DIBUJADA EN PERSPECTIVA, cayendo hacia
    la muñeca, así que se estrecha desde la misma punta: mide sus 20 mm
    justo en el asa y un 10 % menos cinco milímetros más allá. La ranura,
    en cambio, es un carril recto de 20 mm. Resultado: un hilo de fondo a
    los dos lados, entre la correa y el asta, justo donde tienen que
    juntarse.

    Aquí se le devuelve el ancho SÓLO EN LAS FILAS DE LA RANURA: cada fila
    se estira en horizontal hasta que la correa mide lo que la ranura —un
    2 % más, para que se meta bajo el asta— y hacia fuera se vuelve a su
    ancho natural en 180 filas, que es lo que hace una correa de verdad:
    llena el asa y empieza a estrechar en cuanto la pasa."""
    a = np.asarray(L).astype(np.float32).copy()
    al = alfa(caja)
    filas = []
    ys = np.where(al.any(1))[0]
    for arriba in (True, False):
        rango = range(ys.min(), LIENZO // 2) if arriba else range(ys.max(), LIENZO // 2, -1)
        visto, malas = False, 0
        for r in rango:
            idx = np.where(al[r])[0]
            # ⚠️ UNA MOTA NO ES EL FINAL DE LA RANURA. Cerrar las astas deja
            # algún píxel suelto en la punta, y con «si esta fila no vale, se
            # acabó» el barrido de abajo se paraba a las SEIS filas: la tira
            # de abajo se quedó sin ensanchar y sólo se arregló la de arriba.
            # Se salta lo que no llegue a cuarenta píxeles de caja y se
            # aguantan cuatro filas malas seguidas antes de dar por cerrada
            # la ranura.
            if len(idx) < 40:
                continue
            seg = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
            if len(seg) < 2 or int(seg[-1][0]) - int(seg[0][-1]) < 400:
                if visto:
                    malas += 1
                    if malas > 4:
                        break
                continue
            malas = 0
            visto = True
            filas.append((r, int(seg[0][-1]), int(seg[-1][0]), 1 if arriba else -1))
    if not filas:
        return L
    # y las de fuera, para que el ensanche se apague sin dar un escalón
    borde = {1: min(r for r, _, _, d in filas if d == 1),
             -1: max(r for r, _, _, d in filas if d == -1)}
    ancho_ranura = {}
    for r, i, d, s_ in filas:
        ancho_ranura[r] = (d - i) * SOBRA_COR
    for lado in (1, -1):
        r0 = borde[lado]
        base = ancho_ranura.get(r0, 0)
        for k in range(1, DESTENSA + 1):
            r = r0 - k * lado
            if 0 <= r < LIENZO:
                ancho_ranura[r] = base * _suave(k / float(DESTENSA))
    for r, objetivo in ancho_ranura.items():
        fila = a[r + DESP_COR]
        xs = np.where(fila[:, 3] > 128)[0]
        if len(xs) < 10:
            continue
        actual = float(xs.max() - xs.min() + 1)
        k = max(1.0, objetivo / actual) if objetivo else 1.0
        if k <= 1.001:
            continue
        x = np.arange(LIENZO, dtype=np.float64)
        origen = np.clip(centro + (x - centro) / k, 0, LIENZO - 2)
        i0 = np.floor(origen).astype(int)
        w = (origen - i0)[:, None]
        a[r + DESP_COR] = fila[i0] * (1 - w) + fila[i0 + 1] * w
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGBA')


def _suave(t):
    t = float(np.clip(t, 0.0, 1.0))
    return 1.0 - (3 * t * t - 2 * t * t * t)


def cubierto_por_la_caja(caja, cols):
    """De qué fila a qué fila tapa la caja TODO el ancho de la correa."""
    a = alfa(caja)
    c0, c1 = cols
    filas = [r for r in range(a.shape[0]) if a[r, c0:c1 + 1].all()]
    return (filas[0], filas[-1]) if filas else (0, a.shape[0] - 1)


def cuanto_mover(L, arriba, abajo, margen=MARGEN_COR):
    """Cuánto hay que mover cada tira para que su punta quede JUSTO bajo la caja.

    Óscar, 31/08/2026: «la correa tienes que sacarla más hacia fuera, el
    reloj monta mucho encima de la correa (…) la máscara de la caja monta
    mucho trozo de la correa».

    Y tenía razón con números: la punta del caucho —que es su parte ANCHA,
    los 20 mm de las asas— se quedaba mil píxeles por debajo del borde de
    la caja. Lo que asomaba entre las astas ya era la parte estrecha de la
    tira, y por eso se veía fondo a los lados: 48 px por banda.

    Así que la punta se lleva a `margen` píxeles dentro de la primera fila
    en que la caja tapa la correa de lado a lado: lo justo para que el
    corte no se vea, y ni un píxel más. Y AHORA SE MUEVE EN LOS DOS
    SENTIDOS, no sólo hacia dentro: con el lienzo alto ya no hay canto que
    despegar, hay tira de sobra."""
    a = np.asarray(L)[:, :, 3] > 128
    filas = np.where(a.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    t = [(int(x[0]), int(x[-1])) for x in np.split(filas, cortes + 1)]
    if len(t) != 2:
        return 0, 0
    return (arriba + margen) - t[0][1], t[1][0] - (abajo - margen)


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
    # LA ESCALA DEL RELOJ: los milímetros de lado a lado, en la fila del eje.
    ancho_caja = int(np.ptp(np.where(alfa(CAJA_PATRON)[LIENZO // 2])[0])) + 1
    por_mm = ancho_caja / MM_CAJA
    print('CAJA · ojo en %.1f,%.1f r %.0f · hueco entre astas %d px centrado en '
          '%.1f, visible hasta la fila %d' % (eje[0], eje[1], r_ojo, astas,
                                              centro_astas, hasta))
    print('        %g mm son %d px: %.1f px por milímetro'
          % (MM_CAJA, ancho_caja, por_mm))
    print('        ⚠️ el hueco entre astas mide %.2f mm, y las correas de la '
          'entrega se llaman «20-18mm»' % (astas / por_mm))

    capas = {}
    for ident, f in sorted(CAJAS.items()):
        capas[ident] = pon(f, 1.0, (0, 0), (0, 0))

    # LA ESFERA, A CABER DENTRO DEL ARO (Óscar, 31/08/2026: «la esfera tiene
    # que reducirse para encajar dentro de la caja y el anillo»).
    #
    # Iba a llenar el OJO DE LA CAJA —1.140 px— y el aro empieza mucho antes,
    # entre 900 y 944 según el color, así que el aro le comía el borde de los
    # índices: los redondos salían con un lado cortado.
    #
    # La escala sale de dos topes que se miden solos:
    #   · POR ARRIBA, el aro más cerrado. Ningún índice puede pasar de su
    #     borde interior, o ese anillo se lo come.
    #   · POR ABAJO, el aro más abierto. La esfera tiene que llegar más allá
    #     de él, o entre esfera y aro se vería el fondo.
    # Se coge el punto medio de los dos, que deja aire por los dos lados.
    a = alfa(ESFERAS['esfera-negra'])
    ys, xs = np.where(a)
    ce = ((xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0)
    re = float(np.hypot(xs - ce[0], ys - ce[1]).max())
    aros = [borde_del_aro(f) for k, f in sorted(CAJAS.items()) if k != 'caja-acero']
    r_marca = punta_del_indice()
    tope = min(aros) / r_marca
    piso = max(aros) / re
    se = (tope + piso) / 2.0
    print('ESFERA · aros de %.0f a %.0f px · el índice más largo llega a %.0f de '
          'esfera' % (min(aros), max(aros), r_marca))
    print('         no puede pasar de x%.4f (se lo comería el aro más cerrado) ni '
          'bajar de x%.4f (se vería el fondo con el más abierto): x%.4f'
          % (tope, piso, se))
    print('ESFERA · r %.0f -> %.0f (escala %.4f) · los índices se paran en %.0f, '
          'el aro más cerrado empieza en %.0f'
          % (re, re * se, se, r_marca * se, min(aros)))
    for ident, f in sorted(ESFERAS.items()):
        b = alfa(f)
        yy, xx = np.where(b)
        c = ((xx.min() + xx.max()) / 2.0, (yy.min() + yy.max()) / 2.0)
        capas[ident] = pon(f, se, c, eje)

    # LAS AGUJAS, A SU PROPIA ESCALA: la que deja el minutero justo antes
    # del índice. Vienen dibujadas para la esfera —por eso iban con `se`—,
    # pero a esa escala la cruzan entera.
    r_pista = borde_de_la_pista()
    tope = r_pista * se - HUECO_PISTA           # hasta dónde puede llegar la punta
    largos = {}
    for ident, f in sorted(AGUJAS.items()):
        yy, xx = np.where(alfa(f))
        largos[ident] = float(np.hypot(xx - LIENZO / 2.0, yy - LIENZO / 2.0).max())
    # ⚠️ MANDA LA AGUJA MÁS LARGA DE LAS DOS ENTREGAS, no cada una por su
    # cuenta: son dos capas del mismo reloj y tienen que verse del mismo
    # tamaño. Y la más larga no es siempre el minutero —en la de acero lo es
    # el segundero—, así que se mira el largo, no el nombre.
    sa = tope / max(largos.values())
    print('PISTA · el indicador de segundos empieza en %.0f de esfera = %.0f px; '
          'las agujas se paran en %.0f' % (r_pista, r_pista * se, tope))
    print('AGUJAS · escala %.4f en vez de la de la esfera (%.4f): un %.0f %% más chicas'
          % (sa, se, 100 * (1 - sa / se)))
    for ident, f in sorted(AGUJAS.items()):
        capas[ident] = pon(f, sa, (LIENZO / 2.0, LIENZO / 2.0), eje)
        print('AGUJAS %-20s largo %.0f -> %.0f px, de un ojo de %.0f (%.0f %% del radio)'
              % (ident, largos[ident], largos[ident] * sa, r_ojo,
                 100 * largos[ident] * sa / r_ojo))

    # las correas: a llenar el hueco entre astas, con la punta justo bajo la
    # caja y en el lienzo alto, para que el alejarse enseñe más tira
    alto_pub = round(ANCHO * ALTO_COR / float(LIENZO))
    for ident, f in sorted(CORREAS.items()):
        an, cx = (ancho_en_las_puntas(f) if ident in POR_LAS_PUNTAS
                  else ancho_maximo(f))
        s = astas * HOLGURA_COR / an
        capa = pon_correa(f, s, cx, centro_astas)
        b = np.asarray(capa)[:, :, 3] > 128
        cols = np.where(b.any(0))[0]
        arr, aba = cubierto_por_la_caja(CAJA_PATRON, (cols.min(), cols.max()))
        baja, sube = cuanto_mover(capa, arr + DESP_COR, aba + DESP_COR)
        if baja or sube:                       # y se vuelve a montar, ya con el sitio
            capa = pon_correa(f, s, cx, centro_astas, baja, sube)
        capa = rellena_las_astas(capa, CAJA_PATRON, centro_astas)
        capa = alarga_las_tiras(capa)
        if ident not in SIN_TAPAR:
            capa = tapa_los_agujeros(capa)
        capas[ident] = capa.resize((ANCHO, alto_pub), Image.LANCZOS)
        vis = np.asarray(capas[ident])[:, :, 3] > 128
        fil = np.where(vis.any(1))[0]
        tir = [(int(x[0]), int(x[-1]))
               for x in np.split(fil, np.where(np.diff(fil) > 1)[0] + 1)]
        print('CORREA %-20s ancho %4d -> %4d (escala %.4f) · la caja tapa de la '
              '%d a la %d · tira de arriba %+d, la de abajo %+d · publicada '
              'en %dx%d, tiras %s'
              % (ident, an, round(an * s), s, arr, aba, baja, -sube,
                 ANCHO, alto_pub, tir))
    return capas


def en_el_marco(capa):
    """Lo que se ve de una capa en el visor cuadrado, en primer plano.

    La correa se publica más alta que ancha y el navegador la centra en
    vertical y le recorta lo que sobra; esto hace lo mismo, para que la
    hoja de control enseñe lo que verá el cliente y no la capa entera."""
    if capa.size[1] == ANCHO:
        return capa
    y = (capa.size[1] - ANCHO) // 2
    return capa.crop((0, y, ANCHO, y + ANCHO))


def hoja(capas, destino):
    # ⚠️ LA HOJA ENSEÑA CAJAS CON ANILLO, NO LA LISA. Desde que el anillo
    # SUSTITUYE a la caja, la lisa no llega a verse nunca en la ficha: el
    # paso del anillo siempre tiene valor. Y suelta se ve mal a propósito
    # —su ojo es de 1.140 y la esfera se para en 978, así que asoma el
    # fondo—, que es justo lo que el anillo viene a tapar.
    tiros = [('caja-anillo-negro', 'esfera-negra', 'caucho-negra', 'agujas-acero'),
             ('caja-anillo-naranja-grueso', 'esfera-negra-marfil', 'caucho-naranja', 'agujas-acero'),
             ('caja-anillo-azul', 'esfera-azul-sunburst', 'brazalete-acero', 'agujas-acero'),
             ('caja-anillo-turquesa', 'esfera-turquesa-champagne', 'caucho-gris', 'agujas-gris-oscuro'),
             ('caja-anillo-burdeos', 'esfera-frambuesa-fume', 'caucho-roja', 'agujas-gris-oscuro'),
             ('caja-anillo-oliva', 'esfera-roja-fume', 'caucho-verde', 'agujas-gris-oscuro'),
             ('caja-anillo-azul', 'esfera-azul-texturizada', 'caucho-profesional', 'agujas-acero')]
    cols = 3
    filas = (len(tiros) + cols - 1) // cols
    h = Image.new('RGB', (cols * 420, filas * 420), FONDO[:3])
    for i, (caja, esf, cor, ag) in enumerate(tiros):
        L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
        for k in (cor, esf, caja, ag):
            L.alpha_composite(en_el_marco(capas[k]))
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
