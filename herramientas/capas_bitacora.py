# -*- coding: utf-8 -*-
"""BITÁCORA · monta las capas del configurador a partir de la entrega.

    python3 herramientas/capas_bitacora.py            # publica
    python3 herramientas/capas_bitacora.py --prueba   # solo la hoja de control

LO QUE LLEGA (30/08/2026) y por qué no se puede usar tal cual:

  1. NO TIENE ALFA. Las cajas, el brazalete y las agujas vienen en RGB con
     un damero DIBUJADO donde debería haber transparencia (casillas de
     25 px, gris ~254 y ~246). Apiladas así, el ojo de la caja saldría
     blanco y taparía la esfera. Aquí se les devuelve el alfa. Las esferas
     sí llegan en RGBA: esas se usan tal cual.

  2. CADA PIEZA VIENE EN SU PROPIO LIENZO. Cajas y agujas a 1254x1254, el
     brazalete a 1036x1519, las esferas a 1280x1280, y ninguna comparte ni
     escala ni centro. El motor apila todas las capas en el MISMO marco
     cuadrado, así que hay que llevarlas a un lienzo común.

EL LIENZO COMÚN se mide, no se estima:

  · El centro del reloj es el CENTRO DEL OJO DE LA CAJA (el hueco donde va
    la esfera). Se saca de cada caja por separado.
  · La esfera se ajusta al ojo por solapamiento (IoU 0,94): su centro cae
    justo en el centro del ojo, lo que confirma que ojo y esfera están
    dibujados al mismo eje.
  · LAS AGUJAS NO. Su buje está 21 px a la derecha del eje (unos 0,9 mm) y
    su tamaño es el de la ESFERA, no el de la caja, aunque compartan lienzo
    de 1254. Se colocan por el buje y a la escala de la esfera; con la de
    la caja salían del reloj.
  · EL BRAZALETE se registra contra `bitacora-caja-brazalete-v1.png`, la
    entrega antigua que trae caja y brazalete juntos: el brazalete suelto
    encaja ahí sin mover un píxel (IoU 0,94 en la mitad de abajo, que es la
    que la caja no tapa), y la caja suelta encaja a escala 0,8236 (IoU 0,96
    midiendo el ojo). De ahí sale dónde cae el eje dentro del brazalete.

SALIDA: assets/img/bitacora-2026/capas/1200/
  · cuadradas 1200x1200 — caja, esfera, agujas
  · alta 1200x1952 para el brazalete, que el motor reconoce por ser más
    alta que ancha y coloca por su centro (ver configurador-2026.css).
"""
import io as _io
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from tarjeta_de_capas import ESCALA, apila                      # noqa: E402

ENTREGA = ('/Users/oscar/Documents/Codex/2026-08-29/'
           'bitacora-eres-el-dise-ador-grafico/outputs/')
DESTINO = os.path.join(RAIZ, 'assets/img/bitacora-2026/capas/1200')
TARJETAS = os.path.join(RAIZ, 'assets/img/bitacora-2026/tarjetas')

# LAS FOTOS DE LA COLECCIÓN, armadas con las mismas capas. Las que había
# —/assets/img/piezas/completas/— se fueron el 23/08/2026 con las fotos a
# cero, y la Bitácora llevaba desde entonces con las veintiuna rotas.
# Sólo se arman las combinaciones que se pueden DIBUJAR ENTERAS: caja de
# color con su brazalete a juego y una esfera de las cuatro que hay.
# ⚠️ Y SÓLO LAS QUE LA BITÁCORA MONTA DE VERDAD: de multiplicar salen 126
# y monta 36, así que las combinaciones se leen de la ficha. Sin esto se
# armaban la de oro rosa con esfera azul y la negra con esfera azul, que no
# existen y no se pueden comprar.
FICHA = os.path.join(RAIZ, 'assets/datos/fichas/bitacora.json')
# ⚠️ LAS TRES TARJETAS SALEN CON EL MISMO BRAZALETE desde el 03/09/2026, y
# no es un descuido: sólo hay uno dibujado. Las combinaciones de oro rosa y
# negro PVD (Brz-Acero-Bit-06 y -02) siguen en la ficha, pero sin capa, así
# que su tarjeta se arma con el brazalete que hay.
FOTOS = [
    ('plata',      'C1', 'Brz-Acero-Bit-01'),
    ('oro-rosa',   'C3', 'Brz-Acero-Bit-01'),
    ('negro-pvd',  'C4', 'Brz-Acero-Bit-01'),
]
FONDO = (233, 233, 231)

LADO = 25          # casilla del damero, medida en la fila 3 de la entrega
DESFASE = 1        # la primera casilla arranca en x=1

ANCHO = 1200                    # lienzo publicado
UNIDAD = 1254.0                 # el lienzo de la caja es la regla del montaje
F = ANCHO / UNIDAD
ALTO_LARGO = 1952               # lienzo del brazalete (alto, se coloca por el centro)

# LA ESFERA, UN 5 % MÁS GRANDE que el ajuste medido (Óscar, 01/09/2026:
# «haz un poquito más grande la imagen de la esfera por debajo de la caja,
# bien cuadrada en el eje central»).
#
# ⚠️ Y NO ES UN CAPRICHO: EL OJO NO ES REDONDO Y LA ESFERA SÍ. El ojo de la
# Bitácora es un cuadrado de esquinas blandas —un cojín—: mide 282 px de
# radio por los lados y 314 por las esquinas. El ajuste por solapamiento
# iguala las ÁREAS, así que deja un círculo que se mete bajo el bisel por
# los lados y se queda corto en las esquinas: con el 2 % de antes asomaban
# 2.765 px de fondo, dos medias lunas arriba y abajo que se veían a simple
# vista sobre el gris del marco.
#
# Se probaron cuatro medidas contando los píxeles de fondo que quedan
# dentro del ojo: 1,02 deja 2.765; 1,035 deja 517; 1,05 deja CERO y 1,065
# también. Se queda en 1,05, que es el primero que tapa y el que menos
# esconde: la pista de puntos de los minutos se sigue viendo entera.
HOLGURA_ESFERA = 1.05

# --- lo que se publica y de qué fichero sale -------------------------------
# ⚠️ LAS CAJAS SON LAS «-transparente-v2» (Óscar, 01/09/2026: «sustituye
# las imágenes de las cajas»). Llegan con ALFA DE VERDAD, así que ya no hay
# que adivinarles el recorte quitándoles el damero pintado: eso era lo que
# les comía un pelo del ojo —el hueco de la esfera salía 3.800 px más
# pequeño de lo que es— y lo que obligaba a inventarse una silueta.
CAJAS = {
    'caja-plata':     'bitacora-caja-40mm-acero-plata-transparente-v2.png',
    'caja-oro-rosa':  'bitacora-caja-40mm-oro-rosa-transparente-v2.png',
    'caja-negro-pvd': 'bitacora-caja-40mm-negro-pvd-transparente-v2.png',
    # LA BRONCE, para la esfera cobre (Óscar, 01/09/2026). Su capa se
    # publica; que se pueda COMPRAR depende de dos datos que son suyos: lo
    # que cuesta la caja y con qué brazalete o correa la sirve el
    # proveedor. Brazalete de bronce no hay dibujado: los tres que existen
    # son acero plata, acero oro rosa y acero negro.
    'caja-bronce':    'bitacora-caja-40mm-bronce-transparente-v2.png',
}
# ⚠️ LAS ESFERAS SON LAS DEL 01/09/2026 Y VIVEN EN OTRA CARPETA (Óscar:
# «cambia las esferas del bitacora por estas»). Traen índices con relieve,
# doble batón a las 12, pista de minutos punteada y el rótulo AUTOMATIC, y
# llegan a 4.096 con alfa de verdad. Se leen de `preparadas/`, que las deja
# todas del mismo tamaño, con el mismo eje y con el borde redondo: pasar
# antes `herramientas/esferas_bitacora.py` NO ES OPCIONAL —tal cual vienen,
# los radios se llevan un 3,7 %, el eje baila 80 px y la blanca es un
# polígono con un trozo de damero en una esquina—.
ENTREGA_ESF = ('/Users/oscar/Documents/Codex/2026-09-01/'
               'esferas-bitacora-simplemente-a-esta-esfera/outputs/'
               '4k-transparent/preparadas/')
ESFERAS = {
    'esfera-turquesa': ENTREGA_ESF + 'bitacora-esfera-turquesa-26.png',
    'esfera-blanca':   ENTREGA_ESF + 'bitacora-esfera-blanca-26.png',
    'esfera-negra':    ENTREGA_ESF + 'bitacora-esfera-negra-26.png',
    'esfera-azul':     ENTREGA_ESF + 'bitacora-esfera-azul-26.png',
    # LA COBRE SE MONTA (Óscar, 01/09/2026: «monta también el cobre»). La
    # capa se publica; que se pueda COMPRAR es otra cosa y depende de que
    # Óscar diga con qué cajas y con qué correas la sirve el proveedor: la
    # ficha vende por lista de combinaciones, no por multiplicación.
    'esfera-cobre':    ENTREGA_ESF + 'bitacora-esfera-cobre-26.png',
}

# ⚠️ LOS BRAZALETES SON LOS «-frontal-hueco-caja» (Óscar, 01/09/2026:
# «coloca estos brazaletes al bitácora y sustituyes los anteriores»). Los de
# agosto eran una tira corta; éstos traen LAS DOS RAMAS con el hueco de la
# caja en medio, que es lo que el montaje por capas necesita, y llegan a
# 1024x1536.
BRAZALETES = {
    # ⚠️ UNO SOLO, Y ES EL «INTEGRADO DE CORTE EXACTO» (Óscar, 03/09/2026:
    # «elimina el brazalete del bitácora, todos los brazaletes, y coloca
    # este»). Los tres de antes —el de lujo, el oro rosa y el negro PVD—
    # están BORRADOS a propósito; si vuelven a hacer falta, sus nombres
    # están en el git, no aquí.
    'brazalete-acero':
        'bitacora-brazalete-integrado-acero-corte-exacto-transparente-4k-v1.png',
}
# ⛔ `PASO_4K`, `SESGO_4K`, `SILUETA_BRAZALETE`, `CON_FILETE` y `COMBINADO`
# SE FUERON CON ELLOS. El brazalete integrado no se registra contra el
# dibujo de caja+brazalete del proveedor: se registra contra LA CAJA QUE
# PUBLICAMOS, y con una regla que se puede comprobar mirando la foto. Ver
# `_registra_el_integrado`.

# ---------------------------------------------------------------- la piel
# LA BITÁCORA SÓLO LLEVA CORREAS SUYAS (Óscar, 01/09/2026: «estas correas
# son exclusivamente del bitácora […] el resto de correas y brazaletes al
# bitácora no le sirven, el bitácora sólo tiene correas y brazaletes
# exclusivos»). Y es de cajón: la caja es integrada, la correa entra por un
# hueco con la forma del asa y ninguna de las 45 de la biblioteca —todas de
# asas rectas de 20 mm— encaja ahí. Por eso la Bitácora nunca ha tirado de
# `assets/img/componentes/correas/`, y por eso no debe empezar.
ENTREGA_COR = '/Users/oscar/Documents/Codex/2026-08-29/correas-x20/outputs/'
PIELES = {
    'piel-azul-marino':
        'laora-correa-bitacora-piel-especial-25mm-azul-marino.png',
    'piel-marron-burdeos':
        'laora-correa-bitacora-piel-especial-25mm-marron-burdeos-oro-rosa.png',
    # ⚠️ LA NEGRA VIENE MARCADA «prueba-01». Se monta porque es la que falta
    # para tener las tres, pero es un ensayo: antes de venderla, que Óscar
    # confirme que ésa es la buena.
    'piel-negra':
        'laora-correa-bitacora-piel-especial-25mm-negra-prueba-01.png',
}

# ⛔ LAS AGUJAS SE FUERON el 01/09/2026, por orden de Óscar: «quita las
# agujas». Eran las de la entrega de agosto y no acompañaban a las esferas
# nuevas: el segundero se salía de la esfera y cruzaba el bisel, y el
# minutero tapaba el rótulo BITÁCORA. El fichero sigue en la entrega y aquí
# queda su nombre, para que volver a ponerlas sea deshacer esto y no
# reconstruirlo.
AGUJAS = 'bitacora-agujas-con-sombras-misma-posicion-transparente-4k-v2.png'
CON_AGUJAS = True
# ⚠️ LAS NUEVAS NO VAN CON LAS ESFERAS QUE PUBLICAMOS, Y POR ESO NO SE
# COLOCAN COMO LAS VIEJAS. Vienen «en la misma posición» que la esfera
# turquesa de SU entrega —la de 4K del 02/09—, que no es la que se publica
# (las publicadas son las del 01/09, otra carpeta y otro encuadre). Así que
# no se les busca el buje: se mide la transformación que lleva el disco de
# la esfera 4K sobre el disco de la esfera publicada y se les aplica ESA,
# entera. Ver `capa_de_agujas`.
ESFERA_DE_LAS_AGUJAS = ('bitacora-esfera-turquesa-con-agujas-extraida-'
                        'transparente-4k-v1.png')

# LA SILUETA DE LA CAJA SALE DE LAS DE COLOR, Y VALE PARA LAS CINCO.
# La caja plateada es acero pulido y neutro: su propio brillo pasa por
# damero —mismo gris, misma alternancia de cuatro niveles— y el recorte se
# comía media caja (IoU 0,75 contra las demás, que entre ellas dan 0,98).
# Las cinco son el MISMO objeto con distinto acabado y caen en el mismo
# sitio con dos píxeles de margen, así que se recortan todas con la silueta
# que votan las de color. De paso, el eje del reloj deja de bailar medio
# píxel de un color a otro.
# ⚠️ Y LA SILUETA LA SIGUEN VOTANDO CUATRO, aunque ahora traigan alfa.
# La de acero plateado NO cae donde las otras: su recorte es un 0,8 % más
# gordo de cuerpo y un 1 % más chico de ojo (IoU 0,95 contra ellas, que
# entre sí dan 0,99). Publicándolas cada una con su alfa, el reloj cambia
# de tamaño al cambiar de color. Con la silueta votada, las tres salen del
# mismo contorno y el eje no se mueve ni medio píxel.
# La de oro entra de votante y no de capa: su fichero v2 está roto —llega
# casi sin alfa, en pedazos—, pero para votar no se usa, así que se queda
# fuera también de aquí. Votan las cuatro buenas.
CAJAS_LIMPIAS = ('bitacora-caja-40mm-acero-plata-transparente-v2.png',
                 'bitacora-caja-40mm-bronce-transparente-v2.png',
                 'bitacora-caja-40mm-negro-pvd-transparente-v2.png',
                 'bitacora-caja-40mm-oro-rosa-transparente-v2.png')

CALIDADES = (72, 64, 56, 48, 40)
PESO = 90000


# ---------------------------------------------------------------- el damero
def mascara_damero(im, minimo=2.0, maximo=9.0):
    """Fondo = donde el gris ALTERNA con la fuerza del damero.

    NO SE MODELA LA REJILLA. Se intentó, y no vale: cada fichero de la
    entrega trae su casilla —25 px las cajas, 23,2 las agujas— y con un
    periodo que no es entero la fase se desplaza medio cuadro de un lado al
    otro del lienzo, así que la plantilla se anulaba consigo misma
    (amplitud 0,13 en vez de 4) y la máscara se quedaba en el 23 %.

    Lo que sí es igual en todos es CUÁNTO alterna: unos cuatro niveles
    arriba y abajo del gris de base. El gris de base se saca con una media
    de 50x50, PERO contando sólo píxeles que ya parecen fondo. Sin ese
    «sólo», junto a la pieza la ventana se comía el contorno negro de la
    caja, la base se hundía treinta niveles y una corona de 22 px de damero
    quedaba fichada como pieza: ese era el halo blanco que salía alrededor
    de todo, y no una sombra de la entrega.

    Un brillo plano de acero se separa cero de su base y no pasa el mínimo;
    el contorno negro no llega a 235; el acero cepillado se pasa del
    máximo. Recortar por color no valdría: el acero pulido tiene brillos de
    255, tan blancos como el damero. Lo que la prueba deja fuera es la
    costura entre casilla y casilla, donde la diferencia pasa por cero: de
    coserla se encarga `_trozos`.
    """
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    h, w, _ = a.shape
    L = a.mean(2)
    neutro = (a.max(2) - a.min(2)) <= 8
    burdo = (neutro & (L >= 238) & (L <= 258)).astype(np.float32)
    k = 2 * LADO
    den = ndimage.uniform_filter(burdo, k, mode='nearest')
    num = ndimage.uniform_filter(L * burdo, k, mode='nearest')
    base = np.where(den > 0.05, num / np.maximum(den, 1e-6), L)
    d = np.abs(L - base)
    return neutro & (d >= minimo) & (d <= maximo) & (L >= 235)


def _trozos(cand):
    """El damero se parte en islas de 25x25: entre casilla y casilla la
    diferencia pasa por cero y no llega al umbral, y queda una costura de
    uno o dos píxeles. Se cierra 7x7 para coserlas ANTES de contar, pero el
    cierre sólo sirve para saber QUÉ trozo es cuál: el borde bueno se
    recupera después cruzando con la máscara sin cerrar (ver `alfa`). Si se
    publica el cierre tal cual, el canto sale con dientes de 12 px y en el
    ojo de la caja eso se ve desde la otra punta de la pantalla.

    El marco se rellena antes de cerrar porque cerrar sin margen se come el
    borde del lienzo, y entonces NADA toca el borde y el fondo entero pasaba
    por hueco."""
    p = 8
    c = np.pad(cand, p, constant_values=True)
    c = ndimage.binary_closing(c, np.ones((7, 7)))
    cerrada = c[p:-p, p:-p]
    lab, n = ndimage.label(cerrada)
    borde = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    borde.discard(0)
    tam = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)) if n else []
    return lab, n, borde, tam


def _afina(gordo, cand):
    """Devuelve el trozo con su canto de verdad.

    El cierre de `_trozos` deja el borde con dientes de doce píxeles, y en
    el ojo de la caja eso se ve desde la otra punta de la pantalla. Aquí se
    repasa SOLO LA ORILLA —una banda de doce píxeles por dentro del borde—
    con la máscara sin cerrar, y se vuelve a cerrar 5x5, lo justo para
    coser la costura de uno o dos píxeles que queda entre casilla y
    casilla. El interior no se toca: repasarlo entero lo dejaba hecho una
    criba de casillas sueltas y la pieza se comía el lienzo."""
    if not gordo.any():
        return gordo
    dentro = ndimage.binary_erosion(gordo, np.ones((25, 25)))
    orilla = gordo & ~dentro
    fino = gordo.copy()
    fino[orilla] = cand[orilla]
    # ⚠️ EL MARCO SE RELLENA ANTES DE CERRAR. `binary_closing` erosiona
    # contra el borde del array: sin esto el fondo perdía su anillo de dos
    # píxeles, ese anillo pasaba a ser «pieza», rodeaba el lienzo entero y
    # `binary_fill_holes` rellenaba TODO. La pieza medía el 100 %.
    p = 4
    c = np.pad(fino, p, constant_values=True)
    c = ndimage.binary_closing(c, np.ones((5, 5)))
    return c[p:-p, p:-p] | dentro


def desfleca(im, umbral=250):
    """Quita el fleco blanco del canto.

    Todas las piezas llegan recortadas contra un fondo casi blanco, y el
    borde suave se queda con ese blanco dentro del color. Al apilar, la
    esfera salía con una orla blanca dentada entre el dibujo y el bisel.
    Se le da a cada píxel medio transparente el COLOR del píxel opaco más
    cercano; el alfa no se toca, así que el canto sigue igual de suave."""
    a = np.asarray(im).copy()
    solido = a[:, :, 3] >= umbral
    if solido.all() or not solido.any():
        return im
    _, idx = ndimage.distance_transform_edt(~solido, return_indices=True)
    for c in range(3):
        canal = a[:, :, c]
        canal[~solido] = canal[idx[0], idx[1]][~solido]
    return Image.fromarray(a)


def alfa(im, min_hueco=20000, min_trozo=4000, cuerpos=None):
    """Alfa de una pieza entregada con damero pintado.

    `cuerpos` es cuántos trozos tiene la pieza de verdad —la caja uno, el
    brazalete dos—: quedándose con los mayores se van las motas que deja el
    damero por el lienzo, que si no salían como pecas blancas encima de la
    esfera."""
    cand = mascara_damero(im)
    lab, n, borde, tam = _trozos(cand)
    fuera = _afina(np.isin(lab, list(borde)), cand)
    dentro = [i + 1 for i in range(n) if (i + 1) not in borde and tam[i] > min_hueco]
    hueco = (ndimage.binary_fill_holes(_afina(np.isin(lab, dentro), cand))
             if dentro else np.zeros_like(fuera))
    pieza = ndimage.binary_fill_holes(~fuera) & ~hueco
    lab2, n2 = ndimage.label(pieza)
    if n2:
        t2 = ndimage.sum(np.ones_like(lab2), lab2, range(1, n2 + 1))
        if cuerpos:
            vale = [int(i) + 1 for i in np.argsort(t2)[::-1][:cuerpos]]
        else:
            vale = [i + 1 for i in range(n2) if t2[i] >= min_trozo]
        pieza = np.isin(lab2, vale)
    a = ndimage.gaussian_filter((pieza * 255).astype(np.float32), 0.8)
    return np.clip(a, 0, 255).astype(np.uint8)


_CONSENSO = {}


def silueta_caja():
    """La silueta que votan las cajas de color (mayoría de cuatro)."""
    if 'm' not in _CONSENSO:
        votos = None
        for f in CAJAS_LIMPIAS:
            im = abre(f)
            m = ((np.asarray(im.convert('RGBA'))[:, :, 3] > 128) if im.mode == 'RGBA'
                 else (alfa(im, cuerpos=1) > 128)).astype(np.int8)
            votos = m if votos is None else votos + m
        _CONSENSO['m'] = votos >= 3
    return _CONSENSO['m']


def abre(nombre):
    """Las piezas ya no están todas en la misma carpeta: las esferas son de
    la entrega del 01/09 y las demás de la del 29/08."""
    return Image.open(nombre if os.path.isabs(nombre) else ENTREGA + nombre)


def con_alfa(nombre, cuerpos=1, mascara=None):
    im = abre(nombre)
    # ⚠️ SI SE LE DA MÁSCARA, MANDA LA MÁSCARA, traiga alfa o no. Las cajas
    # v2 vienen con su alfa, pero cada una recortada a su manera, y lo que
    # se publica tiene que ser el mismo contorno para las tres.
    if im.mode == 'RGBA' and mascara is None:
        return desfleca(im.copy())
    r = im.convert('RGB').copy()
    m = mascara if mascara is not None else alfa(im, cuerpos=cuerpos)
    r.putalpha(m if isinstance(m, Image.Image) else Image.fromarray(m))
    return desfleca(r)


# ---------------------------------------------------------------- medir
def _silueta_de(im, cuerpos=1):
    """La silueta de una pieza: su alfa si lo trae de verdad, y si no, el
    damero.

    ⚠️ «TRAE ALFA» NO ES «ES RGBA». Los brazaletes nuevos llegan en RGBA con
    el canal entero opaco y el damero pintado dentro: preguntando sólo por
    el modo, la silueta sería el rectángulo del lienzo."""
    if im.mode == 'RGBA':
        a = np.asarray(im)[:, :, 3]
        if a.min() < 250:
            return a > 128
    return alfa(im, cuerpos=cuerpos) > 128


def ojo(im, m=None):
    """El ojo de la caja: lo que la pieza encierra."""
    a = m if m is not None else _silueta_de(im)
    h = ndimage.binary_fill_holes(a) & ~a
    lab, n = ndimage.label(h)
    if not n:
        return h
    tam = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(tam)))


def centro(m):
    ys, xs = np.where(m)
    return float(xs.mean()), float(ys.mean())


def _iou_escalando(fuente, destino, s0, pasos, rango):
    """Busca la escala y el desplazamiento que mejor solapan dos siluetas."""
    dy_, dx_ = np.where(destino)
    dcx, dcy = dx_.mean(), dy_.mean()
    H, W = destino.shape
    mejor = None
    for s in np.arange(s0 - pasos, s0 + pasos + 1e-9, pasos / 5.0):
        k = Image.fromarray((fuente * 255).astype('uint8')).resize(
            (int(round(fuente.shape[1] * s)), int(round(fuente.shape[0] * s))),
            Image.LANCZOS)
        ka = np.asarray(k) > 128
        if not ka.any():
            continue
        ys, xs = np.where(ka)
        for dy in range(-rango, rango + 1, 2):
            for dx in range(-rango, rango + 1, 2):
                ox = int(round(dcx - xs.mean())) + dx
                oy = int(round(dcy - ys.mean())) + dy
                L = Image.new('L', (W, H), 0)
                L.paste(k, (ox, oy))
                m = np.asarray(L) > 128
                u = (m | destino).sum()
                iou = (m & destino).sum() / u if u else 0
                if mejor is None or iou > mejor[0]:
                    mejor = (iou, float(s), ox, oy)
    return mejor


def medidas():
    """Todo lo que hace falta para colocar cada pieza, medido de la entrega."""
    m = {}
    silueta = silueta_caja()
    o = ojo(None, silueta)
    m['eje'] = centro(o)                       # el mismo para las cinco cajas
    # la esfera se ajusta al ojo por solapamiento
    esf = np.asarray(abre(ESFERAS['esfera-turquesa']).convert('RGBA'))[:, :, 3] > 128
    s0 = (o.sum() / esf.sum()) ** 0.5
    iou, s, ox, oy = _iou_escalando(esf, o, s0, 0.03, 24)
    m['esfera'] = {'escala': s, 'iou': iou, 'ancla': (639.5, 639.5),
                   'cae': (639.5 * s + ox, 639.5 * s + oy)}
    # ⛔ EL BRAZALETE YA NO SE REGISTRA AQUÍ. El integrado se coloca contra
    # la caja publicada, midiendo, y eso vive en `_registra_el_integrado`.
    return m


# ---------------------------------------------------------------- publicar
def coloca(im, escala, ancla, lienzo, eje):
    """Pega `im`, escalada, con su punto `ancla` sobre `eje` del lienzo."""
    s = escala * F
    n = im.resize((max(1, int(round(im.width * s))),
                   max(1, int(round(im.height * s)))), Image.LANCZOS)
    L = Image.new('RGBA', lienzo, (0, 0, 0, 0))
    L.alpha_composite(n, (int(round(eje[0] - ancla[0] * s)),
                          int(round(eje[1] - ancla[1] * s))))
    return L


def guarda(im, ident):
    for q in CALIDADES:
        b = _io.BytesIO()
        im.save(b, 'AVIF', quality=q)
        datos = b.getvalue()
        if len(datos) <= PESO or q == CALIDADES[-1]:
            break
    os.makedirs(DESTINO, exist_ok=True)
    open(os.path.join(DESTINO, ident + '.avif'), 'wb').write(datos)
    return len(datos)


def _dos_ramas(m, minimo=3000):
    """Las dos tiras de una correa o un brazalete, sin las motas del fondo."""
    lab, n = ndimage.label(m)
    tam = ndimage.sum(m, lab, range(1, n + 1))
    gr = sorted([i + 1 for i, t in enumerate(tam) if t >= minimo],
                key=lambda i: -tam[i - 1])[:2]
    return lab, gr


def hueco_de_asas(mascara):
    """Dónde y con qué ancho se mete una correa bajo la caja.

    Devuelve (ancho del asa, fin de la rama de arriba, principio de la de
    abajo, centro en x). El ancho se mide en el lado de DENTRO de la rama
    de arriba —el que toca la caja—, saltándose las últimas cuatro filas,
    que son la muesca y el suavizado del filo."""
    lab, gr = _dos_ramas(mascara)
    tapas = sorted((int(np.where(lab == i)[0].min()), i) for i in gr)
    (_, arriba), (_, abajo) = tapas
    fin = int(np.where(lab == arriba)[0].max())
    ini = int(np.where(lab == abajo)[0].min())
    ancho = 0
    for y in range(max(0, fin - 60), max(1, fin - 4)):
        xs = np.where(lab[y] == arriba)[0]
        if len(xs):
            ancho = max(ancho, int(xs.max() - xs.min() + 1))
    return ancho, fin, ini, float(np.where(mascara)[1].mean())


def alfa_de_piel(im):
    """La correa de piel, recortada del papel Y DE SU SOMBRA.

    La entrega de correas no viene contra damero sino contra papel blanco
    con una sombra suave a la derecha. La sombra es lo que hay que quitar:
    con el umbral de siempre —«más claro que 232 es fondo»— se colaban diez
    píxeles de gris por todo el canto derecho, que en la capa publicada son
    veintiocho y se ven como una mancha.

    LA REGLA: el papel y su sombra son GRISES y CLAROS; la piel tiene color
    (azul, burdeos) o es oscura (negra). Así que fuera todo lo que sea gris
    —menos de 12 de diferencia entre canales— y claro —de 120 para arriba—.

    ⚠️ ESTO SE COME LAS HEBILLAS DE ACERO, que son grises y claras. No
    importa para lo que se publica: la correa se coloca escalada casi tres
    veces y la hebilla cae MUY por encima del lienzo, así que no entra en
    cuadro ni con el zoom más alejado. Si algún día hace falta la correa
    entera —una miniatura como la del Lunar—, hay que recortarla de otra
    manera. Se probó a rescatar la hebilla pidiendo que el fondo fuera
    además LISO, y no vale: la sombra es una rampa, y una rampa tampoco es
    lisa, así que volvía a colarse entera."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    gris = (a.max(2) - a.min(2)) <= 12
    claro = a.mean(2) >= 120
    lab, gr = _dos_ramas(~(gris & claro))
    return ndimage.binary_fill_holes(np.isin(lab, gr))




def _perfil(m, alto):
    """Ancho de una silueta fila a fila, en un lienzo de `alto` filas."""
    an = np.zeros(alto, int)
    for y in np.where(m.any(1))[0]:
        xs = np.where(m[y])[0]
        an[y] = xs.max() - xs.min() + 1
    return an


def _dos_tiras(a):
    fil = np.where(a.any(1))[0]
    return [(int(x[0]), int(x[-1]))
            for x in np.split(fil, np.where(np.diff(fil) > 1)[0] + 1)]


def capas_de_piel(brazalete):
    """Las correas de piel, colocadas por el hueco de las asas.

    NO HAY DIBUJO DE CAJA+CORREA con el que registrarlas, que es como se
    registra el brazalete. Pero no hace falta: la correa y el brazalete
    entran POR EL MISMO SITIO, así que valen dos reglas y las dos se miden:
      · el ancho del asa de la correa tiene que ser el del brazalete —495 px
        en la capa publicada—, que es el hueco de la caja;
      · el hueco entre sus dos ramas se centra en el eje del reloj.
    El resto —que la correa sobresalga por arriba y por abajo del marco— sale
    solo, porque es mucho más larga que el lienzo.

    ⚠️ LA CORREA SE CENTRA EN EL EJE, no en el brazalete. El brazalete cae
    3,5 px a la derecha del eje porque así viene dibujado; copiar ese sesgo
    en la correa sería copiar el error de otro dibujo."""
    ancho_b, _, _, _ = hueco_de_asas(np.asarray(brazalete)[:, :, 3] > 128)
    largo = (ANCHO, ALTO_LARGO)
    salida = {}
    for ident, f in sorted(PIELES.items()):
        im = Image.open(ENTREGA_COR + f).convert('RGB')
        mask = alfa_de_piel(im)
        ancho_p, fin, ini, cx = hueco_de_asas(mask)
        s = float(ancho_b) / ancho_p
        cy = (fin + ini) / 2.0
        r = im.convert('RGBA')
        r.putalpha(Image.fromarray((mask * 255).astype(np.uint8)))
        r = desfleca(r)
        n = r.resize((max(1, int(round(r.width * s))),
                      max(1, int(round(r.height * s)))), Image.LANCZOS)
        L = Image.new('RGBA', largo, (0, 0, 0, 0))
        L.alpha_composite(n, (int(round(ANCHO / 2.0 - cx * s)),
                              int(round(ALTO_LARGO / 2.0 - cy * s))))
        salida[ident] = L
    return salida


def capa_de_agujas(esfera_publicada):
    """Las agujas nuevas, puestas donde tienen que ir.

    Óscar, 03/09/2026: «coloca las agujas nuevas a ver cómo quedan». Son las
    «con sombras, misma posición», que sustituyen a las de agosto —aquéllas
    salían el 01/09 porque el segundero se iba al bisel y el minutero tapaba
    el rótulo BITÁCORA—.

    ⚠️ «MISMA POSICIÓN» ES RESPECTO DE SU PROPIA ESFERA, no de la nuestra.
    Vienen en el lienzo de la esfera turquesa 4K de su entrega, y las
    esferas que se publican son las del 01/09, que es otra carpeta, otro
    encuadre y otro tamaño de disco. Buscarles el buje y clavarlo en el eje
    del reloj sería colocarlas a ojo: lo que se hace es medir el disco de
    las dos esferas —la suya y la publicada— y aplicarles la MISMA
    transformación que lleva una sobre la otra. Si un día cambian las
    esferas, esto se recalcula solo.
    """
    def disco(a):
        m = a[:, :, 3] > 128
        ys, xs = np.where(m)
        return (np.array([(xs.min() + xs.max()) / 2.0,
                          (ys.min() + ys.max()) / 2.0]),
                ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 4.0)
    cA, rA = disco(np.asarray(abre(ESFERA_DE_LAS_AGUJAS).convert('RGBA')))
    cB, rB = disco(np.asarray(esfera_publicada))
    k = rB / rA
    ag = abre(AGUJAS).convert('RGBA')
    n = ag.resize((max(1, int(round(ag.width * k))),
                   max(1, int(round(ag.height * k)))), Image.LANCZOS)
    off = cB - cA * k
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (int(round(off[0])), int(round(off[1]))))
    print('AGUJAS    disco de su esfera %.0f px -> disco de la nuestra %.0f px '
          '(escala %.4f)' % (rA, rB, k))
    return L


def _registra_el_integrado(caja, largo):
    """El brazalete integrado, cuadrado con la caja AL PÍXEL.

    Óscar, 03/09/2026: «la base de la caja es una caja que acaba totalmente
    recta en sus extremos, y el brazalete es igual de ancho que la caja en su
    unión, tienen que coincidir a la perfección; este reloj se llama Precisa,
    así que vamos a hacer honor a su nombre».

    LA REGLA, Y ES UNA SOLA: cada tira del brazalete acaba en un corte recto,
    y ese corte tiene que caer justo en la fila donde la caja mide EXACTAMENTE
    lo mismo que el corte. No se fuerza el ancho ni se recorta nada: se busca
    la escala y la altura que cumplen las dos cosas a la vez, arriba y abajo.

    ⚠️ NO HAY MÁS DE UNA SOLUCIÓN, y por eso esto no es un apaño. Al agrandar
    el brazalete, su corte pide una fila donde la caja sea más ancha —o sea
    más adentro, más cerca del centro— y las dos filas se ACERCAN; pero el
    hueco entre las dos tiras del dibujo se AGRANDA. Las dos curvas se cruzan
    una vez. La búsqueda encuentra ese cruce y clava los dos cortes con menos
    de un píxel de error.

    ⚠️ EL BRAZALETE VA POR ENCIMA DE LA CAJA (ver `arma` y el `encima_si` de
    la ficha), y es lo que remata la unión: las puntas de las asas —que son
    más anchas que el brazalete y antes asomaban por los lados, 21 px por la
    izquierda y 8 por la derecha— quedan tapadas. Era «la mancha blanca del
    lado izquierdo» del 03/09.
    """
    im = abre(BRAZALETES['brazalete-acero']).convert('RGBA')
    B = np.asarray(im)[:, :, 3] > 128
    anB = _perfil(B, im.height)
    fil = np.where(B.any(1))[0]
    cortes = np.split(fil, np.where(np.diff(fil) > 1)[0] + 1)
    if len(cortes) != 2:
        raise SystemExit('✗ el brazalete integrado no trae dos tiras')
    Rn, Rs = int(cortes[0][-1]), int(cortes[1][0])      # los dos cortes rectos
    Wn, Ws = float(anB[Rn]), float(anB[Rs])
    # la caja, en el lienzo alto
    C = np.zeros((largo[1], largo[0]), bool)
    desf = (largo[1] - ANCHO) // 2
    C[desf:desf + ANCHO] = np.asarray(caja)[:, :, 3] > 128
    anC = _perfil(C, largo[1])
    mejor = None
    for s in np.arange(0.30, 0.60, 0.0002):
        for dy in np.arange(-300, 700, 1.0):
            yN, yS = int(round(Rn * s + dy)), int(round(Rs * s + dy))
            if not (0 <= yN < largo[1] and 0 <= yS < largo[1]):
                continue
            cn, cs = anC[yN], anC[yS]
            if cn <= 0 or cs <= 0:
                continue
            err = abs(Wn * s - cn) + abs(Ws * s - cs)
            if mejor is None or err < mejor[0]:
                mejor = (err, float(s), float(dy), yN, yS, cn, cs)
    err, s, dy, yN, yS, cn, cs = mejor
    n = im.resize((max(1, int(round(im.width * s))),
                   max(1, int(round(im.height * s)))), Image.LANCZOS)
    # y centrado: el eje del corte sobre el eje de la caja
    def eje(m, y):
        xs = np.where(m[int(round(y))])[0]
        return (xs.min() + xs.max()) / 2.0
    Bn = np.asarray(n)[:, :, 3] > 128
    cb = (eje(Bn, Rn * s - 3) + eje(Bn, Rs * s + 3)) / 2.0
    cc = (eje(C, yN) + eje(C, yS)) / 2.0
    L = Image.new('RGBA', largo, (0, 0, 0, 0))
    L.alpha_composite(n, (int(round(cc - cb)), int(round(dy))))
    a = np.asarray(L)[:, :, 3] > 128
    ve = ((largo[1] - ANCHO / ESCALA) / 2.0, (largo[1] + ANCHO / ESCALA) / 2.0)
    f = np.where(a.any(1))[0]
    print('BRAZALETE escala %.4f · corte norte fila %d: %.0f px de brazalete '
          'contra %.0f de caja · corte sur fila %d: %.0f contra %.0f · error '
          '%.1f px' % (s, yN, Wn * s, cn, yS, Ws * s, cs, err))
    print('          llega al canto de arriba: %s · al de abajo: %s'
          % (f.min() <= ve[0], f.max() >= ve[1]))
    return L


def capas(m):
    """Devuelve {ident: imagen ya colocada en el lienzo común}."""
    salida = {}
    cuad = (ANCHO, ANCHO)
    eje_c = (ANCHO / 2.0, ANCHO / 2.0)
    silueta = Image.fromarray(
        np.clip(ndimage.gaussian_filter((silueta_caja() * 255).astype(np.float32), 0.8),
                0, 255).astype(np.uint8))
    for ident, f in CAJAS.items():
        salida[ident] = coloca(con_alfa(f, mascara=silueta), 1.0, m['eje'], cuad, eje_c)
    for ident, f in ESFERAS.items():
        salida[ident] = coloca(con_alfa(f), m['esfera']['escala'] * HOLGURA_ESFERA,
                               m['esfera']['ancla'], cuad, eje_c)
    if CON_AGUJAS:
        salida['agujas'] = capa_de_agujas(salida['esfera-turquesa'])
    largo = (ANCHO, ALTO_LARGO)
    for ident in BRAZALETES:
        salida[ident] = _registra_el_integrado(salida['caja-plata'], largo)
    salida.update(capas_de_piel(salida['brazalete-acero']))
    return salida


def arma(cs, caja, esfera, brazalete):
    """El reloj entero sobre el gris del marco, como lo pinta el navegador.

    ALEJADO, como todo en la casa desde el 01/09/2026 («el reloj debe
    presentarse siempre más alejado con más correa o brazalete»): el mismo
    0,72 de `tarjeta_de_capas.ESCALA` y de `configurador-2026.css`. Antes se
    recortaba el brazalete por el centro; ahora se encoge todo alrededor del
    centro del marco, que es lo que hace el navegador.

    ⚠️ EL BRAZALETE DE LA BITÁCORA ES MÁS ALTO QUE 1/0,72 —1.952 sobre
    1.200, o sea 1,63 contra 1,39—, así que al 72 % sigue saliéndose del
    marco por arriba y por abajo. No es un fallo: se ve más tira que antes
    y sigue llegando a los bordes, que es lo que se buscaba.
    """
    # ⚠️ EL BRAZALETE, EL ÚLTIMO: VA POR ENCIMA DE LA CAJA (Óscar,
    # 02/09/2026). Es integrado y su primer eslabón monta sobre ella.
    # ⚠️ PERO SÓLO EL BRAZALETE. Las correas de piel de este mismo reloj
    # entran POR DEBAJO, como en todos los demás relojes: subiendo la correa
    # entera, la piel se dibuja encima de la esfera y tapa el reloj. Se
    # probó y se vio. Esto tiene que decir lo mismo que el `encima_si` de la
    # ficha, o la foto de la colección enseñará un reloj distinto del que
    # arma el configurador.
    encima = brazalete in BRAZALETES
    orden = ([] if encima else [brazalete]) + [esfera, caja] \
        + (['agujas'] if CON_AGUJAS else []) + ([brazalete] if encima else [])
    return apila([cs[c] for c in orden], ANCHO, FONDO, ESCALA).convert('RGB')


def combinaciones():
    import json
    d = json.load(_io.open(FICHA, encoding='utf-8'))
    return d['combinaciones'], d['montaje']['capas']


def fotos_de_tarjeta(cs):
    os.makedirs(TARJETAS, exist_ok=True)
    combis, capas_de = combinaciones()
    hechas = []
    for mote, cid, brz in FOTOS:
        caja = capas_de['caja'].get(cid)
        brazalete = capas_de['correa'].get(brz)
        esferas = sorted({c['esf'] for c in combis if c['caja'] == cid})
        for eid in esferas:
            esf = capas_de['esf'].get(eid)
            if not esf or esf not in cs or not caja or caja not in cs:
                continue
            ident = '%s-%s' % (mote, esf.replace('esfera-', ''))
            im = arma(cs, caja, esf, brazalete)
            for q in CALIDADES:
                b = _io.BytesIO()
                im.save(b, 'AVIF', quality=q)
                datos = b.getvalue()
                if len(datos) <= 110000 or q == CALIDADES[-1]:
                    break
            open(os.path.join(TARJETAS, ident + '.avif'), 'wb').write(datos)
            hechas.append((ident, len(datos)))
    return hechas


def hoja_de_control(cs, destino):
    """Una tira con los tres montajes completos, para mirarlos antes de nada."""
    # UN SOLO BRAZALETE desde el 03/09/2026, así que la tira enseña las
    # tres cajas con él puesto y no tres brazaletes distintos.
    tiros = [('caja-plata', 'esfera-turquesa', 'brazalete-acero'),
             ('caja-oro-rosa', 'esfera-blanca', 'brazalete-acero'),
             ('caja-negro-pvd', 'esfera-negra', 'brazalete-acero')]
    hoja = Image.new('RGB', (ANCHO * len(tiros), ANCHO), (233, 233, 231))
    for i, (caja, esf, brz) in enumerate(tiros):
        # el mismo encuadre alejado de la tarjeta: se mira lo que se publica
        hoja.paste(arma(cs, caja, esf, brz), (i * ANCHO, 0))
    hoja.resize((hoja.width // 3, hoja.height // 3)).save(destino)


if __name__ == '__main__':
    m = medidas()
    print('EJE DEL RELOJ (centro del ojo de la silueta común, lienzo de 1254): '
          '%.2f, %.2f' % m['eje'])
    print('ESFERA    escala %.4f (IoU %.4f contra el ojo); su centro cae en '
          '%.1f,%.1f' % (m['esfera']['escala'], m['esfera']['iou'],
                         m['esfera']['cae'][0], m['esfera']['cae'][1]))
    cs = capas(m)
    prueba = '--prueba' in sys.argv
    hoja = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'bitacora-control.png')
            if prueba else os.path.join(RAIZ, 'herramientas/capturas/bitacora-capas.png'))
    os.makedirs(os.path.dirname(hoja), exist_ok=True)
    hoja_de_control(cs, hoja)
    print('\nhoja de control: ' + hoja)
    if prueba:
        sys.exit(0)
    print('\nPUBLICADO en assets/img/bitacora-2026/capas/1200/')
    for ident in sorted(cs):
        n = guarda(cs[ident], ident)
        print('  %-22s %5d B  %dx%d' % (ident, n, cs[ident].width, cs[ident].height))
    print('\nFOTOS DE LA COLECCIÓN en assets/img/bitacora-2026/tarjetas/')
    for ident, n in fotos_de_tarjeta(cs):
        print('  %-26s %6d B' % (ident, n))
