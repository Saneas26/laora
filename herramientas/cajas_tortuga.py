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

⚠️ Y EL ANILLO NO ES OTRA CAJA: ES UN ARO DENTRO DE LA MISMA CAJA (Óscar,
31/08/2026: «lo que has hecho con el tortuga es montar la caja sobre otra
caja y lo que hay que hacer es sustituir la caja por otra, pero siempre
todas del mismo tamaño en el mismo punto central del eje, es decir cuando
yo cambio de elección la caja no se mueve»).

Escalar cada render y centrarlo por su ojo no bastaba: puestos uno encima
de otro, el contorno seguía bailando hasta 60 px —los once renders no se
ponen de acuerdo en dónde cae el cuerpo respecto del ojo— y al cambiar de
anillo el reloj daba un salto. Así que de los diez renders de anillo NO SE
USA LA CAJA: se les recorta SÓLO lo que hay dentro del ojo —el aro de color
y su escala— y se pega dentro de la caja del patrón. Las once cajas salen
entonces del MISMO dibujo, con el mismo contorno y el mismo bisel; lo único
que cambia de una a otra es el aro. Píxel a píxel, fuera del ojo son
idénticas: cambiar de anillo no mueve nada.

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
# ⚠️ CUARENTA Y CUATRO, NO CUARENTA Y CINCO (Óscar, 31/08/2026). El nombre
# del fichero del patrón dice «45mm» y la landing decía 45, pero la ficha
# la puso a 44 y él confirma que manda la ficha. Importa, y mucho: de esta
# cifra sale cuánto mide un milímetro en el dibujo, y de ahí los 20 mm de
# la ranura de las astas. A 45 salían 1.428 px; a 44 son 1.460.
MM_CAJA = 44.0          # la caja, de lado a lado
MM_ASTAS = 20.0         # lo que tienen que medir las astas al acabar
BANDA = 340.0           # hasta dónde llega el estirón, hacia fuera de la pared
COLA = 90               # y cuántas filas tarda en apagarse por debajo del hueco
VUELVE = 420.0          # en esas filas, lo que tarda el empujón en deshacerse
SOLIDO = 128            # el alfa a partir del cual una fila cuenta como caja

CAJAS = [
    '19-caja-tortuga-45mm-eje-2048.png',
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
    """Los milímetros de la caja se miden en la fila del eje, como en
    `capas_tortuga.py`: es la medida con la que ya está publicado todo."""
    fila = np.where(al[al.shape[0] // 2] > SOLIDO)[0]
    return int(fila.max() - fila.min() + 1)


def ojo_de(al):
    """El centro y el radio del ojo de la caja: por ahí se ve la esfera."""
    h = ndimage.binary_fill_holes(al > SOLIDO) & ~(al > SOLIDO)
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = lab == 1 + int(np.argmax(t))
    ys, xs = np.where(m)
    cx, cy = float(xs.mean()), float(ys.mean())
    return (cx, cy), float(np.hypot(xs - cx, ys - cy).max())


def corre(a, dx, dy):
    """Mueve el dibujo entero, sin salirse del lienzo."""
    im = Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGBA')
    return np.asarray(im.transform(im.size, Image.AFFINE,
                                   (1, 0, -dx, 0, 1, -dy),
                                   resample=Image.BICUBIC)).astype(np.float32)


def dentro_del_ojo(aro, caja, centro, radio, margen=12):
    """Mete el aro DENTRO de la caja del patrón, y tira el resto.

    El aro va debajo: la caja tapa todo lo que sobresalga, así que el filo
    del ojo lo pone siempre el patrón y no hay costura que cuadrar."""
    yy, xx = np.mgrid[0:aro.shape[0], 0:aro.shape[1]]
    d = np.hypot(xx - centro[0], yy - centro[1])
    b = aro.copy()
    b[d > radio + margen] = 0
    # «encima» de verdad, con alfa recta: donde la caja es opaca no se toca
    # ni un píxel, y en el filo del ojo —que viene difuminado— se mezcla
    # como es debido. Multiplicando a lo bruto salía una orla oscura en
    # todo el contorno, y las diez cajas dejaban de ser idénticas por
    # 190.522 píxeles de nada.
    aA = caja[:, :, 3:4] / 255.0
    aB = b[:, :, 3:4] / 255.0
    salida = aA + aB * (1 - aA)
    rgb = np.where(salida > 0,
                   (caja[:, :, :3] * aA + b[:, :, :3] * aB * (1 - aA)) /
                   np.maximum(salida, 1e-6), 0)
    junta = np.dstack([rgb, salida * 255.0])
    # y donde el aro no pinta nada, la caja se copia TAL CUAL: recalcular
    # esos píxeles los redondeaba distinto y dejaba las once cajas
    # diferentes en 32.315 píxeles del contorno, que es justo lo que no
    # puede pasar.
    quieto = (b[:, :, 3] <= 0)
    junta[quieto] = caja[quieto]
    return junta


# ---------- llevar al patrón ----------

def al_patron(a, ancho_patron):
    """La lleva al tamaño del patrón SIN MOVERLE EL EJE.

    Las once vienen centradas en el ojo de la caja —(2.048, 2.048) las
    once—, así que basta con escalarlas desde el centro del lienzo y el eje
    se queda donde estaba. Encajar en cambio las siluetas por su marco daba
    tumbos: el marco incluye la corona, que sobresale por un lado, y en la
    del plata además llevaba pelusa del recorte.

    Y LA MEDIDA ES EL ANCHO EN LA FILA DEL EJE, no el del marco: es la
    misma con la que `capas_tortuga.py` calcula los milímetros, y una fila
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

    # 1 · LA CAJA, UNA SOLA VEZ: la del patrón, con las astas cerradas.
    a = np.asarray(Image.open(ENTREGA + PATRON).convert('RGBA')).astype(np.float32)
    caja, medido, dx = cierra_las_astas(a, objetivo)
    ahora, centro = hueco(caja[:, :, 3])
    ojo_c, ojo_r = ojo_de(caja[:, :, 3])
    Image.fromarray(np.clip(caja, 0, 255).astype('uint8'), 'RGBA').save(
        os.path.join(DESTINO, PATRON))
    print('%-56s astas %4d -> %4d px (%.2f mm) centradas en %.1f · ojo en '
          '%.1f,%.1f r %.0f'
          % (PATRON, int(medido), int(ahora), ahora / por_mm, centro,
             ojo_c[0], ojo_c[1], ojo_r))

    # 2 · Y LOS DIEZ AROS, cada uno metido en esa misma caja.
    for f in CAJAS[1:]:
        b = np.asarray(Image.open(ENTREGA + f).convert('RGBA')).astype(np.float32)
        aviso = ''
        if sobre_fondo_negro(b):
            b = quita_el_fondo_negro(b)
            aviso = ' · venía sobre FONDO NEGRO, recortado'
        antes_an = ancho_en_el_eje(b[:, :, 3])
        b, s = al_patron(b, ancho_patron)
        c, r = ojo_de(b[:, :, 3])
        b = corre(b, ojo_c[0] - c[0], ojo_c[1] - c[1])   # su ojo, sobre el del patrón
        junta = dentro_del_ojo(b, caja, ojo_c, ojo_r)
        Image.fromarray(np.clip(junta, 0, 255).astype('uint8'), 'RGBA').save(
            os.path.join(DESTINO, f))
        print('%-56s aro r %4.0f -> %4.0f · caja %4d -> %4d px (x%.4f) · '
              'movido %+5.1f,%+5.1f para cuadrar el ojo%s'
              % (f, r, ojo_r, antes_an, ancho_patron, s,
                 ojo_c[0] - c[0], ojo_c[1] - c[1], aviso))
    print('\nescritas en %s' % DESTINO)


if __name__ == '__main__':
    prepara('--mira' in sys.argv)
