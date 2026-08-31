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


def tiras(m):
    filas = np.where(m.any(1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    return [(int(t[0]), int(t[-1])) for t in np.split(filas, cortes + 1)]


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
    L_ = L
    m = ndimage.binary_closing(m, np.ones((5, 5)))
    lab, n = ndimage.label(m)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    dos = ndimage.binary_fill_holes(
        np.isin(lab, [int(i) + 1 for i in np.argsort(t)[::-1][:2]]))
    # SE PELA LO QUE SE PUEDA, NO LO QUE SE QUIERA. En el brazalete de
    # centro oro el pelado llegó a partir una tira en dos —tres bandas
    # donde tiene que haber dos—, así que se prueba de más a menos y se
    # queda la primera que sigue dejando la correa entera.
    for tope in (60, 40, 25, 12, 0):
        m = _pela(dos, L, gris, s > sat, tope=tope) if tope else dos
        if len(tiras(m)) == 2:
            return m, a
    return dos, a


def _pela(m, L, gris, color, tope=60):
    """Le quita al canto la SOMBRA de estudio.

    La foto trae una sombra suave alrededor de la pieza: en la piel con
    costura, veintiocho píxeles de rampa que van del 117 al 253 del fondo.
    El umbral del recorte la da por pieza y se veía como una orla clara
    pegada al canto.

    La rampa se pela por dónde CAE SU GRIS: se toma el gris del corazón de
    la pieza y el del fondo, y se van quitando los píxeles del borde que
    estén más cerca del fondo que de la pieza. Un pelado por umbral fijo no
    valía —el fondo no siempre es el mismo gris, y una correa clara se
    habría comido a sí misma—; éste se adapta a cada foto.

    Con tope, por si acaso: sesenta píxeles de 4.096 son quince centésimas
    de milímetro. Si hiciera falta pelar más, es que el recorte está mal y
    hay que mirarlo, no seguir comiendo.

    ⚠️ LO QUE TIENE COLOR NO SE PELA (31/08/2026). El hilo crema de la piel
    con costura es CLARO, y en una correa negra el pelado lo daba por fondo
    y se comía la costura entera: por eso al sacarla de debajo del asa
    aparecían boquetes justo donde va el hilo. El fondo del estudio y su
    sombra son grises neutros; el hilo, no. Se pela por gris, pero solo
    donde no hay color.
    """
    nucleo = ndimage.binary_erosion(m, np.ones((21, 21)))
    if not nucleo.any():
        return m
    medio = (float(np.median(L[nucleo])) + gris) / 2.0
    claro = L > medio if gris > np.median(L[nucleo]) else L < medio
    for _ in range(tope):
        borde = m & ~ndimage.binary_erosion(m, np.ones((3, 3)))
        fuera = borde & claro & ~color
        if not fuera.any():
            break
        m = m & ~fuera
    return m


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


def prepara(origen, holgura=1.0, ancho=0, factor=1.0):
    m, rgb = sin_fondo(origen)
    mio = medidas(m)
    ref = patron()
    # EL ANCHO SE PUEDE PEDIR A PELO, y es lo que hace falta para que una
    # correa mida 20 mm de verdad: el patrón está a 23,33 y copiarlo es
    # heredar su error (Óscar, 31/08/2026: «hay que estrecharla a 20 mm,
    # ahora mismo está como en 22»). 20 mm SON LOS 1.284 px del hueco entre
    # asas: la correa entra justo entre ellas, ni las tapa ni deja rendija.
    if ancho:
        ref = dict(ref, ancho=float(ancho))
    # ⚠️ LA HOLGURA es para los brazaletes que van de 20 a 16 mm: igualando
    # el ancho máximo al del patrón, en las filas de las asas se quedaban
    # entre 8 y 14 px cortos y `auditar_correas.py` los cantaba. Lo que
    # sobra no se ve —la correa va detrás de la caja—, lo que falta sí.
    s = ref['ancho'] / mio['ancho'] * holgura * factor
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



def sella_canto(L):
    """Tapa lo que el hilo deja al cinchar la piel, junto al asa.

    Óscar, 31/08/2026: «la correa de piel con costura pierde la costura si
    no la movemos un poco más cerca del asa». Al acercarla sale la costura…
    y sale con ella lo que el hilo deja al cinchar: en la coñac, una mordida
    de setenta píxeles en el canto izquierdo y unas ranuras entre las
    hebras. Por todas se veía el FONDO DE LA PÁGINA.

    Eso es del estudio, no del producto: en la muñeca, detrás está el asa.

    CÓMO. En la zona de la costura —y SOLO ahí— la correa es una banda
    maciza: se toma el canto izquierdo y el derecho que tiene la pieza en
    esa zona y se rellena todo lo que quede en medio y esté vacío, con la
    piel de la fila limpia más cercana. El hilo, que va por encima, no se
    toca.

    LOS DOS LÍMITES DE LA ZONA, y son los que hacen que esto no estropee
    nada más:
      · por dentro, PUNTA: el corte del extremo se estrecha de verdad y se
        mete bajo la caja. No se toca.
      · por fuera, ZONA: los agujeros de la hebilla son de verdad y están a
        mil ochocientos píxeles del extremo. Ni se acercan.
    """
    a = np.asarray(L).copy()
    alfa = a[:, :, 3] > 60
    # ⚠️ NO VALE «hay alfa»: la máscara viene de una foto de 1.024 px
    # estirada a 4.096, así que cada canto es una RAMPA de cien píxeles. En
    # la mordida del hilo el alfa se quedaba entre 65 y 232 —opaco para un
    # umbral de 60— y por ahí seguía viéndose el fondo. Dentro de la correa
    # el alfa es 255 o no es nada.
    solido = a[:, :, 3] > 250
    PUNTA, ZONA = 150, 750
    for ini, fin in tiras(alfa):
        arriba = ini == 0
        borde_dentro = fin if arriba else ini
        r0, r1 = ((borde_dentro - ZONA, borde_dentro - PUNTA) if arriba
                  else (borde_dentro + PUNTA, borde_dentro + ZONA))
        r0, r1 = max(ini, r0), min(fin, r1)
        izq, der = [], []
        for r in range(r0, r1 + 1):
            idx = np.where(solido[r])[0]
            if len(idx):
                izq.append(idx[0])
                der.append(idx[-1])
        if not izq:
            continue
        x0, x1 = int(np.median(izq)), int(np.median(der)) + 1
        falta = np.zeros_like(alfa)
        falta[r0:r1 + 1, x0:x1] = ~solido[r0:r1 + 1, x0:x1]
        if not falta.any():
            continue
        _rellena(a, falta)
    return Image.fromarray(a)


def _rellena(a, falta):
    """Tapa un hueco CON LA PIEL DE AL LADO.

    No vale copiar un trozo de otra fila: se veían los recuadros del parche,
    porque el grano no casa. Cada hueco toma el color del píxel opaco más
    próximo y luego se difumina SOLO por dentro del parche, que es lo que
    hace que no se note."""
    if not falta.any():
        return
    _, idx = ndimage.distance_transform_edt(
        falta, return_distances=True, return_indices=True)
    parche = a[idx[0], idx[1]].astype(np.float32)
    for canal in range(3):
        parche[:, :, canal] = ndimage.gaussian_filter(parche[:, :, canal], 12)
    a[falta] = np.clip(parche[falta], 0, 255).astype(np.uint8)
    a[:, :, 3][falta] = 255


# LAS FILAS DONDE ESTÁN LAS ASAS, en el lienzo de 4.096. Es la única franja
# donde el ancho de la correa decide si se ve fondo o no: por encima se la
# ve entera y por debajo la tapa el cuerpo del reloj.
#
# ⚠️ NO SON SIMÉTRICAS, y ése fue el fallo. La primera vez se puso la de
# abajo como espejo de la de arriba alrededor del centro del lienzo, y el
# reloj NO está centrado en el lienzo de la correa: su eje cae 150 px por
# encima. La franja de abajo quedaba 260 px fuera de sitio y por ahí seguían
# saliendo tres píxeles de fondo por mucho que se ensanchara la correa.
#
# Salen de medir las cuatro cajas que montan estas correas —el Lunar y las
# del Trinchera— con `filas_de_asa` de `auditar_correas.py`, y de coger la
# unión con un poco de margen:
#     Lunar acero      1152–1448  ·  3975–4226
#     Trinchera acero  1185–1484  ·  3896–4193
#     titanio          1190–1489  ·  3914–4231
#     bronce           1157–1472  ·  4147–4221
ASA_FILAS = ((1145, 1495), (3888, 4240))


def _cantos_en_la_punta_del_asa(L):
    """Los dos cantos EN LA PUNTA DEL ASA, que es donde se ve el ancho.

    Ni el máximo de la pieza ni el mínimo de la franja: la correa se
    estrecha hacia la hebilla, así que su ancho depende de dónde se mida.
    El que ve el cliente es el de la fila donde la correa asoma por primera
    vez —la punta del asa—; de ahí hacia dentro es más ancha y la tapa la
    caja, y de ahí hacia fuera se estrecha como debe."""
    a = np.asarray(L)[:, :, 3] > 60
    izq, der = [], []
    for i, (r0, r1) in enumerate(ASA_FILAS):
        r = r0 if i == 0 else r1
        idx = np.where(a[min(r, a.shape[0] - 1)])[0]
        if len(idx):
            izq.append(int(idx[0]))
            der.append(int(idx[-1]))
    if not izq:
        return None
    return sum(izq) / float(len(izq)), sum(der) / float(len(der))


def banda_en_las_asas(L):
    """El ancho de la correa en la punta del asa. 1.284 px son 20 mm."""
    c = _cantos_en_la_punta_del_asa(L)
    return 0 if not c else int(round(c[1] - c[0] + 1))


def cuadra_las_asas(L, ancho):
    """Deja la correa RECTA y de `ancho` justo donde entra en las asas.

    Óscar, 31/08/2026: «hazla a 20 mm exactos y centrada sobre el eje, debe
    haber la misma distancia de hueco a izquierda y derecha de las asas».

    ⚠️ ESCALAR NO BASTA. Esto es la foto de una correa de verdad: sus cantos
    no son paralelos y bailan veinte píxeles. Con la pieza a 20 mm justos,
    una fila se metía seis píxeles dentro del asa y se veía el fondo, y el
    hueco de asa que quedaba a la vista no era el mismo a los dos lados.

    Aquí se le pone el canto que tiene la correa de verdad: una banda de
    1.284 px —los 20 mm del hueco entre asas— centrada en el eje 2.054.
    Sólo en las filas de las asas y hacia dentro, que es donde la correa es
    recta; por encima sigue estrechándose hacia la hebilla como en la foto.

    SÓLO SE RELLENA, NO SE RECORTA. Lo que sobra por los lados queda detrás
    del asa y no se ve; lo que falta sí. Recortando además se le comía a la
    correa el canto de las filas de dentro, que es lo que la sujeta."""
    a = np.asarray(L).copy()
    x0 = int(round((ASAS[0] + ASAS[1]) / 2.0 - ancho / 2.0))
    x1 = x0 + int(ancho)
    # ⚠️ Y EL CONTRATO POR ENCIMA DE TODO. El hueco entre asas va de la 1.412
    # a la 2.696 INCLUIDAS, y en la primera fila del asa —la punta, donde la
    # caja está achaflanada— es un píxel más ancho todavía. Una banda de
    # 1.284 centrada y redondeada se quedaba corta justo ahí, y
    # `auditar_correas.py` lo cantaba. Se estira lo justo para taparlo:
    # nueve píxeles de 4.096, catorce centésimas de milímetro.
    x0, x1 = min(x0, ASAS[0] - 4), max(x1, ASAS[1] + 5)
    vivo = a[:, :, 3] > 60
    falta = np.zeros(a.shape[:2], bool)
    for r0, r1 in ASA_FILAS:
        for r in range(r0, min(r1, a.shape[0] - 1) + 1):
            if not vivo[r].any():
                continue
            falta[r, x0:x1] = a[r, x0:x1, 3] <= 250
    _rellena(a, falta)
    return Image.fromarray(a)


def centra(L):
    """Vuelve a poner la pieza en el eje de las asas.

    ⚠️ NO SE CENTRA POR EL RECUADRO DE LA PIEZA. Esto es una foto de una
    correa de verdad, no un dibujo: sus cantos no son paralelos y el
    recuadro los promedia. Centrando así, con la correa a 20 mm justos, el
    canto izquierdo se quedaba seis píxeles dentro del asa y el derecho
    sobraba ocho: una rendija de fondo por la izquierda de arriba abajo.

    SE CENTRA POR DONDE APRIETA: se busca, en las filas de las asas, el
    canto izquierdo que más se mete y el derecho que menos llega, y se
    centra esa banda —la peor— en el eje del hueco. Así lo que falte, si
    falta, falta por igual a los dos lados.

    Y se llama DESPUÉS de sellar, que rellena la mordida del hilo por un
    solo canto y mueve la pieza."""
    c = _cantos_en_la_punta_del_asa(L)
    if not c:
        return L
    centro = (c[0] + c[1]) / 2.0
    dx = int(round((ASAS[0] + ASAS[1]) / 2.0 - centro))
    if not dx:
        return L
    n = Image.new('RGBA', L.size, (0, 0, 0, 0))
    n.alpha_composite(L, (dx, 0))
    return n


def acerca_al_asa(L, px=0, punta=0):
    """Separa las dos tiras: la de arriba sube, la de abajo baja.

    Sirve para sacar de debajo del asa un detalle que se estaba comiendo la
    caja —la costura de la piel con costura va en la punta—. Lo que se
    descubre por dentro no deja hueco: el extremo de la tira sigue quedando
    bajo el cuerpo de la caja, que a 4.096 tapa de la fila 1.667 hacia
    dentro.

    CON `punta` SE PIDE EL SITIO, no el empujón, y es lo que hay que usar:
    el empujón en píxeles vale para UNA escala, y en cuanto la correa se
    estrecha o se ensancha deja de valer. Diciendo dónde tiene que morir el
    extremo, la costura cae en el mismo hueco mida lo que mida la pieza."""
    a = np.asarray(L)
    m = a[:, :, 3] > 60
    t = tiras(m)
    if punta:
        px = t[0][1] - int(punta)
    n = Image.new('RGBA', L.size, (0, 0, 0, 0))
    med = (t[0][1] + t[1][0]) // 2
    n.alpha_composite(L.crop((0, 0, L.width, med)), (0, -px))
    n.alpha_composite(L.crop((0, med, L.width, L.height)), (0, med + px))
    return n


if __name__ == '__main__':
    CON_VALOR = ('--holgura', '--acerca', '--punta', '--ancho', '--asas', '--cuadra')
    args = [a for i, a in enumerate(sys.argv[1:])
            if not a.startswith('--') and not (i and sys.argv[i] in CON_VALOR)]
    if len(args) < 2:
        sys.exit(__doc__)
    origen, ident = args[0], args[1]
    holgura = float(sys.argv[sys.argv.index('--holgura') + 1]) if '--holgura' in sys.argv else 1.0
    acerca = int(sys.argv[sys.argv.index('--acerca') + 1]) if '--acerca' in sys.argv else 0
    punta = int(sys.argv[sys.argv.index('--punta') + 1]) if '--punta' in sys.argv else 0
    ancho_pedido = int(sys.argv[sys.argv.index('--ancho') + 1]) if '--ancho' in sys.argv else 0
    asas = int(sys.argv[sys.argv.index('--asas') + 1]) if '--asas' in sys.argv else 0
    cuadra = int(sys.argv[sys.argv.index('--cuadra') + 1]) if '--cuadra' in sys.argv else 0

    def monta(factor):
        capa, s, mio, ref = prepara(origen, holgura, ancho_pedido, factor)
        if '--sella' in sys.argv:
            capa = sella_canto(capa)
        if acerca or punta:
            capa = acerca_al_asa(capa, acerca, punta)
        # el centrado va el ÚLTIMO: mira las filas de las asas, y hasta que las
        # tiras no están en su sitio esas filas no enseñan lo que van a enseñar.
        capa = centra(capa)
        if cuadra:
            capa = cuadra_las_asas(capa, cuadra)
        return capa, s

    # ⚠️ EL ANCHO QUE VE ÓSCAR NO ES EL DEL DIBUJO. La correa se estrecha
    # hacia la hebilla y sus cantos no son paralelos —es una foto—, así que
    # escalar «el ancho máximo» deja la parte de las asas más estrecha de lo
    # pedido: pidiendo 20 mm salían 19,1 en las asas y una rendija de fondo.
    # Con `--asas` se pide la medida DONDE IMPORTA y se busca la escala que
    # la da, midiéndola en cada vuelta. Dos o tres vueltas y está.
    factor = 1.0
    capa, s = monta(factor)
    if asas:
        for _ in range(6):
            b = banda_en_las_asas(capa)
            if not b or abs(b - asas) <= 1:
                break
            factor *= asas / float(b)
            capa, s = monta(factor)
        print('   banda en las asas: %d px = %.2f mm' % (
            banda_en_las_asas(capa), banda_en_las_asas(capa) / 1284.0 * 20))
    a = np.asarray(capa)[:, :, 3] > 128
    ys, xs = np.where(a)
    ancho = xs.max() - xs.min() + 1
    hueco = ASAS[1] - ASAS[0]
    print('%-38s escala %.4f · ancho %d px = %.2f mm para un hueco de %d %s · '
          'centro en x=%.0f (toca 2054) · punta en la fila %d' % (
        ident, s, ancho, ancho / float(hueco) * 20, hueco,
        'OK' if ancho >= hueco else '✗ SE QUEDA CORTA',
        (xs.min() + xs.max()) / 2.0, tiras(a)[0][1]))
    salida = os.path.join(os.environ.get('TMPDIR', '/tmp'), ident + '.png')
    capa.save(salida)
    print('   ' + salida)
