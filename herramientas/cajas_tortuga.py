# -*- coding: utf-8 -*-
"""TORTUGA · deja las once cajas a la misma medida y les cierra las astas a 20 mm.

    python3 herramientas/cajas_tortuga.py [--mira]

Óscar, 31/08/2026: «Las astas se cierran a 20». Las correas de la entrega
se llaman «20-18mm» y el hueco entre las astas medía 22,4 mm, así que o
subían las correas o bajaba el hueco. Bajó el hueco.

PERO ANTES HAY QUE PONERLAS TODAS DEL MISMO TAMAÑO, y ésa es la sorpresa
de la entrega: las once cajas NO son un mismo dibujo recoloreado, son once
renders distintos. La lisa mide 3.345 px de ancho y las diez de anillo
rondan las 3.600: un 7 % más grande. Como el anillo se pinta ENCIMA de la
caja lisa y la tapa entera, al elegir anillo el reloj daba un salto y se
hacía más grande. Y el centro se movía hasta 86 px de una a otra.

Superpuestas y llevadas al mismo ancho, las siluetas coinciden: es el mismo
reloj a otra escala. Así que se escalan al ancho de la lisa y se centran
por su caja, y a partir de ahí las once son intercambiables.

⚠️ LA DEL ANILLO PLATA VENÍA SOBRE FONDO NEGRO, con el alfa a 255 en casi
todo el lienzo. Publicada tal cual era un cuadro negro. Se le recorta el
fondo por el negro que toca el borde —el negro del bisel no lo toca, así
que se queda— y se le quita al filo el negro que se le había pegado.

CÓMO SE CIERRAN LAS ASTAS. El asta es una pala cuya pared de dentro es una
recta casi vertical. Se empuja esa pared hacia dentro los píxeles que hagan
falta con un desplazamiento que vale `dx` en la pared misma y se apaga
suavemente 340 px hacia fuera: la pared y su bisel viajan enteros, el
metal cepillado de en medio se estira, y la silueta de fuera —que a media
altura es ya el costado del cojín— no se entera. Sólo en las filas de la
punta, donde el asta es estrecha, se mueve también el filo de fuera: eso es
justo lo que se ve cuando unas astas se cierran, que las puntas se inclinan
hacia dentro.

El desplazamiento nunca pisa el bisel: si la pared llegara a tocarlo, se
para un pelo antes, que es donde el asta se junta con la caja de verdad.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGA = ('/Users/oscar/Documents/Codex/2026-08-31/'
           'tortuga-eres-el-dise-ador-gr/outputs/')
DESTINO = os.path.join(ENTREGA, 'preparadas')

PATRON = '19-caja-tortuga-45mm-eje-2048.png'
MM_CAJA = 45.0          # la caja, de lado a lado
MM_ASTAS = 20.0         # lo que tienen que medir las astas al acabar
BANDA = 340.0           # hasta dónde llega el estirón, hacia fuera de la pared
COLA = 90               # y cuántas filas tarda en apagarse por debajo del hueco
VUELVE = 420.0          # en esas filas, lo que tarda el empujón en deshacerse
SOLIDO = 128            # el alfa a partir del cual una fila cuenta como caja

CAJAS = [
    '19-caja-tortuga-45mm-eje-2048.png',
    '21-caja-tortuga-anillo-naranja-eje-2048.png',
    '22-caja-tortuga-anillo-naranja-grueso-escala-negra.png',
    '23-caja-tortuga-anillo-plata-escala-negra.png',
    '24-caja-tortuga-anillo-azul-escala-negra.png',
    '25-caja-tortuga-anillo-verde-escala-negra.png',
    '26-caja-tortuga-anillo-negro-escala-clara.png',
    '27-caja-tortuga-anillo-oliva-escala-negra.png',
    '28-caja-tortuga-anillo-burdeos-escala-negra.png',
    '29-caja-tortuga-anillo-turquesa-escala-negra.png',
    '30-caja-tortuga-anillo-acero-liso.png',
]


# ---------- el fondo negro ----------

def sobre_fondo_negro(a):
    """¿Viene el dibujo pegado sobre un fondo, en vez de recortado?

    ⚠️ NO POR LAS ESQUINAS. La del anillo plata las tiene transparentes y
    aun así trae el fondo: su alfa es un pegote que llega hasta los cuatro
    bordes del lienzo pero se queda corto en los picos. Se mira cuánto del
    borde entero viene opaco; en las diez buenas es cero."""
    al = a[:, :, 3]
    borde = np.concatenate([al[0], al[-1], al[:, 0], al[:, -1]])
    return bool((borde > 200).mean() > 0.02)


def quita_el_fondo_negro(a, umbral=8):
    """Recorta por el negro que TOCA EL BORDE. El negro del bisel es un
    agujero cerrado y no lo toca, así que se queda donde está."""
    lum = a[:, :, :3].max(2).astype(np.float32)
    lab, _ = ndimage.label(lum <= umbral)
    fuera = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    # Y EL OJO DE LA CAJA, que también es fondo aunque no toque el borde:
    # por ahí se ve la esfera. Se coge por el trozo negro que hay JUSTO EN
    # EL CENTRO del lienzo, que es donde está el eje del reloj en las once
    # entregas. Sin esto la caja salía con un disco negro tapando la esfera
    # y las agujas flotando encima.
    ojo = int(lab[lab.shape[0] // 2, lab.shape[1] // 2])
    if ojo:
        fuera.add(ojo)
    fuera.discard(0)
    fondo = np.isin(lab, sorted(fuera))

    # EL FILO. Los píxeles de la orilla vienen mezclados con el negro del
    # fondo, así que se les mide cuánta caja llevan —por lo claros que son
    # comparados con el metal de al lado— y se les devuelve el color sin la
    # parte negra. Sin esto queda una raya oscura alrededor de toda la caja.
    orilla = ndimage.binary_dilation(fondo, iterations=3) & ~fondo
    dentro = ndimage.binary_erosion(~fondo, iterations=4)
    ref = float(np.median(lum[dentro & ndimage.binary_dilation(orilla, iterations=6)]))
    al = np.where(fondo, 0.0, 255.0)
    if ref > 1:
        cob = np.clip(lum[orilla] / ref, 0.0, 1.0)
        al[orilla] = cob * 255.0
        rgb = a[:, :, :3][orilla]
        a[:, :, :3][orilla] = np.clip(rgb / np.maximum(cob, .05)[:, None], 0, 255)
    b = a.copy()
    b[:, :, 3] = al
    return b


# ---------- medir ----------

def caja_de(al):
    ys, xs = np.where(al > SOLIDO)
    return int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())


def filas_del_hueco(al, arriba=True):
    """Las filas donde se ven las dos astas con el hueco en medio.

    Se recorren desde la punta hacia el centro y se para en cuanto la caja
    se vuelve maciza: más adentro el dibujo se abre otra vez —el ojo del
    bisel— y ahí no hay astas que valgan."""
    m = al > SOLIDO
    filas = np.where(m.any(1))[0]
    orden = range(filas.min(), al.shape[0] // 2) if arriba else \
        range(filas.max(), al.shape[0] // 2, -1)
    out, visto = [], False
    for r in orden:
        idx = np.where(m[r])[0]
        if not len(idx):
            continue
        seg = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        if len(seg) < 2 or int(seg[-1][0]) - int(seg[0][-1]) < 400:
            if visto:
                break
            continue
        visto = True
        medio = int(seg[1][0]) if len(seg) > 2 else None
        out.append((r, int(seg[0][-1]), int(seg[-1][0]), medio))
    return out


def hueco(al):
    """Cuánto mide la ranura de las astas, y dónde está centrada.

    ⚠️ POR LA MEDIANA, NO POR LA MÁS ANCHA. La ranura es un carril de
    paredes paralelas —1.604 px en el patrón, fila tras fila— con dos
    excepciones que no son la ranura: la PRIMERA fila de la punta, donde el
    filo llega difuminado y el hueco parece 40 px más ancho, y las últimas,
    donde el asta ya está doblando para juntarse con el bisel. Midiendo por
    la más ancha se cerraba de más y las paredes salían torcidas."""
    anchos, centros = [], []
    for arriba in (True, False):
        for _, izq, der, _ in filas_del_hueco(al, arriba):
            anchos.append(der - izq)
            centros.append((izq + der) / 2.0)
    if not anchos:
        return 0.0, al.shape[1] / 2.0
    return float(np.median(anchos)), float(np.median(centros))


def ancho_en_el_eje(al):
    """Los 45 mm de la caja se miden en la fila del eje, como en
    `capas_tortuga.py`: es la medida con la que ya está publicado todo."""
    fila = np.where(al[al.shape[0] // 2] > SOLIDO)[0]
    return int(fila.max() - fila.min() + 1)


# ---------- llevar al patrón ----------

def al_patron(a, ancho_patron):
    """La lleva al tamaño del patrón SIN MOVERLE EL EJE.

    Las once vienen centradas en el ojo de la caja —(2.048, 2.048) las
    once—, así que basta con escalarlas desde el centro del lienzo y el eje
    se queda donde estaba. Encajar en cambio las siluetas por su marco daba
    tumbos: el marco incluye la corona, que sobresale por un lado, y en la
    del plata además llevaba pelusa del recorte.

    Y LA MEDIDA ES EL ANCHO EN LA FILA DEL EJE, no el del marco: es la
    misma con la que `capas_tortuga.py` calcula los 45 mm, y una fila
    limpia no la ensucia ni una mota suelta."""
    s = ancho_patron / float(ancho_en_el_eje(a[:, :, 3]))
    lado = a.shape[0]
    im = Image.fromarray(a.astype('uint8'), 'RGBA')
    n = int(round(lado * s))
    im = im.resize((n, n), Image.LANCZOS)
    b = np.asarray(im).astype(np.float32)
    fuera = np.zeros((lado, lado, 4), np.float32)
    o = (lado - n) // 2                      # centrado: el eje no se mueve
    if o >= 0:
        fuera[o:o + n, o:o + n] = b
    else:
        fuera[:] = b[-o:-o + lado, -o:-o + lado]
    return fuera, s


# ---------- cerrar las astas ----------

def _suave(t):
    """1 en la pared, 0 a `BANDA` de distancia, y sin esquinas."""
    t = np.clip(t, 0.0, 1.0)
    return 1.0 - (3 * t * t - 2 * t * t * t)


def _empuja(fila, pared, dx, derecha, vuelve=0.0):
    """Estira la fila para que la pared del asta se meta `dx` hacia dentro.

    `derecha` dice si el asta es la de la derecha, que empuja al revés.

    `vuelve` es lo que tarda el empujón en deshacerse POR DENTRO de la
    pared. Vale 0 en las filas del hueco, que es donde queremos que se abra
    de verdad: al otro lado no hay nada que estropear, sólo fondo. Y vale
    unos cientos de píxeles en la cola, donde al otro lado ya hay bisel: si
    ahí se abriera hueco quedaría una costura diagonal cruzando el moleteado,
    porque el dibujo saltaría de golpe. Devolviéndolo, el moleteado se
    aprieta un poco y no se parte."""
    n = fila.shape[0]
    if derecha:
        vol = _empuja(fila[::-1].copy(), n - 1 - pared, dx, False, vuelve)
        return vol[::-1]
    ini = int(max(0, pared - BANDA - 2))
    fin = int(min(n - 1, pared + dx + vuelve + 2))
    if fin <= ini:
        return fila
    src = np.arange(ini, fin + 1, dtype=np.float64)
    izq = src <= pared
    alto = np.where(izq, _suave((pared - src) / BANDA),
                    _suave((src - pared) / vuelve) if vuelve > 0 else 0.0)
    dst = src + dx * alto
    destino = np.arange(ini, fin + 1, dtype=np.float64)
    origen = np.interp(destino, dst, src)
    out = fila.copy()
    i0 = np.clip(np.floor(origen).astype(int), 0, n - 2)
    w = (origen - i0)[:, None]
    out[ini:fin + 1] = fila[i0] * (1 - w) + fila[i0 + 1] * w
    return out


def cierra_las_astas(a, objetivo):
    """Mete las cuatro astas hacia dentro hasta que el hueco mida `objetivo`."""
    b = a.copy()
    medido, _ = hueco(a[:, :, 3])
    dx = (medido - objetivo) / 2.0
    if dx <= 0:
        return b, medido, 0.0
    for arriba in (True, False):
        filas = filas_del_hueco(a[:, :, 3], arriba)
        if not filas:
            continue
        # ⚠️ SIN TOPE CONTRA EL BISEL. Al principio la pared se paraba un
        # pelo antes de tocarlo y en las últimas filas —donde el asta ya
        # está doblando para juntarse con la caja— el remate salía cortado a
        # escuadra. Dejándola pasar, el asta se apoya en el bisel un poco
        # más adelante, que es lo que hace un asta más cerrada.
        for r, izq, der, _ in filas:
            b[r] = _empuja(_empuja(b[r], izq, dx, False), der, dx, True)
        # Y LA COLA, que es lo que quitó el escalón. Debajo de la última fila
        # del hueco la caja ya es maciza: la pared no existe, pero su bisel
        # sí se ve dibujado sobre el metal. Si el empujón se cortaba en seco
        # ahí, la raya del bisel se quedaba colgada en mitad de la pieza. Se
        # sigue empujando NOVENTA FILAS más adentro, con el empujón
        # apagándose poco a poco, y el bisel se mete en la caja como venía.
        r0, izq0, der0, _ = filas[-1]
        paso = 1 if arriba else -1
        for k in range(1, COLA + 1):
            r = r0 + k * paso
            if not 0 <= r < a.shape[0]:
                break
            d = dx * _suave(k / float(COLA))
            b[r] = _empuja(_empuja(b[r], izq0, d, False, VUELVE),
                           der0, d, True, VUELVE)
    return b, medido, dx


# ---------- el trabajo ----------

def prepara(mira=False):
    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)
    pa = np.asarray(Image.open(ENTREGA + PATRON).convert('RGBA')).astype(np.float32)
    ancho_patron = ancho_en_el_eje(pa[:, :, 3])
    por_mm = ancho_patron / MM_CAJA
    objetivo = MM_ASTAS * por_mm
    print('PATRÓN %s' % PATRON)
    print('  caja %d px en la fila del eje · %.2f px por mm · las astas se '
          'cierran a %.0f px (%.0f mm)' % (ancho_patron, por_mm, objetivo, MM_ASTAS))

    for f in CAJAS:
        a = np.asarray(Image.open(ENTREGA + f).convert('RGBA')).astype(np.float32)
        aviso = ''
        if sobre_fondo_negro(a):
            a = quita_el_fondo_negro(a)
            aviso = ' · venía sobre FONDO NEGRO, recortado'
        antes_an = ancho_en_el_eje(a[:, :, 3])
        a, s = al_patron(a, ancho_patron)
        a, medido, dx = cierra_las_astas(a, objetivo)
        ahora, centro = hueco(a[:, :, 3])
        Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGBA').save(
            os.path.join(DESTINO, f))
        print('%-56s caja %4d -> %4d px (x%.4f) · astas %4d -> %4d px '
              '(%.2f mm) centradas en %.1f%s'
              % (f, antes_an, ancho_en_el_eje(a[:, :, 3]), s,
                 int(medido), int(ahora), ahora / por_mm, centro, aviso))
    print('\nescritas en %s' % DESTINO)


if __name__ == '__main__':
    prepara('--mira' in sys.argv)
