# -*- coding: utf-8 -*-
"""PRECISA · coloca un juego de agujas en las capas del configurador.

    python3 herramientas/agujas_precisa.py <fichero.png> <plata|oro-rosa|negras>
    python3 herramientas/agujas_precisa.py <fichero.png> plata --prueba
    ... --minutero 0.95 --segundero 1.05   (estirar o acortar una aguja suelta)
    ... --segundero igual                  (el segundero, tan largo como el minutero)
    ... --sin-tono                          (no igualar el tono a los índices)
    ... --tono oro-rosa                     (igualar al oro rosa, no al acero)

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
# ⚠️ SE MONTA A 1.600 (31/08/2026), como las esferas: el fichero grande —el
# que ve la lupa— se sacaba agrandando el de 1.200 y lo que se pierde por el
# camino no vuelve. La entrega de agujas viene a 1.536 px, así que a 1.600
# el montaje ya no inventa nada.
ANCHO = 1600                     # el lienzo en el que se mide todo
ALTO_CAJA = 2222                 # la caja va en lienzo alto
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 60000
MINUTERO_R = 400.0               # dónde cae la punta del minutero, en px de 1600
                                 # (los 300 de 1.200 de siempre, a la nueva escala)
# ⛔ AQUÍ SE IMPORTABA `BAJADA`, los 11,5 px que la esfera bajaba respecto
# al hueco de la caja. Se fue el 31/08/2026 con ella: ahora la esfera se
# coloca por SU pista de minutos, centrada en el ojo de la caja, así que el
# eje del movimiento es el del ojo y no hay nada que corregir.
FONDO = (233, 233, 231, 255)
ESFERA_PATRON = 'esfera-antracita.avif'   # la negra: sus barras se recortan solas


def _alfa(f):
    return np.asarray(Image.open(f).convert('RGBA'))[:, :, 3]


def eje_del_reloj():
    """El centro del reloj: donde coinciden el hueco de la caja y la esfera."""
    c = _alfa(os.path.join(CAPAS, '%d/caja-brazalete-acero.avif' % ANCHO)) > 128
    h = ndimage.binary_fill_holes(c) & ~c
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    oy, ox = np.where(lab == 1 + int(np.argmax(t)))
    # el lienzo de la caja es alto: se pasa a las coordenadas del cuadrado
    caja = (float(ox.mean()), float(oy.mean()) - (ALTO_CAJA - ANCHO) / 2.0)
    radio = (ox.max() - ox.min() + 1) / 2.0

    e = _alfa(os.path.join(CAPAS, '%d/esfera-turquesa.avif' % ANCHO)) > 128
    ys, xs = np.where(e)
    esf = ((float(xs.min()) + float(xs.max())) / 2.0,
           (float(ys.min()) + float(ys.max())) / 2.0)
    # ⚠️ EL EJE ES EL DEL OJO DE LA CAJA, a secas. Antes se promediaba con el
    # centro del RECORTE de la esfera, y ese recorte es irregular: su centro
    # no es el del dibujo y arrastraba el buje unos píxeles. Desde que la
    # esfera se coloca por su pista de minutos, centrada en el ojo, el eje
    # del movimiento es el del ojo y promediar sólo puede estropearlo.
    return caja, radio, caja, esf


def pista_de_minutos():
    """Hasta dónde llegan los índices aplicados de la esfera."""
    a = np.asarray(Image.open(os.path.join(CAPAS, '%d/esfera-turquesa.avif' % ANCHO))
                   .convert('RGBA'))
    rgb = a[:, :, :3].astype(int)
    eje, _, _, _ = eje_del_reloj()
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(x - eje[0], y - eje[1])
    ind = ((a[:, :, 3] > 200) & (rgb.mean(2) > 190)
           & (rgb.max(2) - rgb.min(2) < 45)
           & (r > 200 * ANCHO / 1200.0) & (r < 330 * ANCHO / 1200.0))
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
        trozos.append({'largo': float(r[s].max()), 'area': int(s.sum()), 'mask': s})
    trozos.sort(key=lambda d: -d['area'])
    minutero = max(trozos[:2], key=lambda d: d['largo'])   # de los dos anchos, el largo
    horaria = min(trozos[:2], key=lambda d: d['largo'])
    finos = [d for d in trozos[2:]]
    segundero = max(finos, key=lambda d: d['largo']) if finos else None
    return eje, minutero, horaria, segundero


def estira(im, hub, arm_mask, f):
    """Alarga o acorta UNA aguja por su eje, dejando quieto el arranque.

    Escalar el dibujo entero no vale: mueve las tres a la vez. Y escalar la
    aguja alrededor del buje la engorda igual que la alarga, y despega su
    arranque del buje. Aquí se trabaja en el eje de la propia aguja: se
    estira a lo largo y no a lo ancho, y el punto de arranque se queda
    donde estaba, así que no aparece ninguna costura."""
    if abs(f - 1.0) < 1e-6:
        return im
    a = np.asarray(im).astype(np.float32)
    ys, xs = np.where(arm_mask)
    d = np.stack([xs - hub[0], ys - hub[1]], 1)
    r = np.hypot(d[:, 0], d[:, 1])
    punta = d[int(np.argmax(r))]
    u = punta / np.hypot(*punta)                       # eje de la aguja
    r0, R = float(r.min()), float(r.max())
    g = (R * f - r0) / (R - r0)
    # el mapa inverso, en coordenadas (fila, columna)
    U = np.array([[u[1], -u[0]], [u[0], u[1]]])        # columnas: eje y perpendicular
    Sinv = np.diag([1.0 / g, 1.0])
    Minv = U.dot(Sinv).dot(U.T)
    hubrc = np.array([hub[1], hub[0]])
    corr = U.dot(np.array([r0 - r0 / g, 0.0]))
    off = hubrc - Minv.dot(hubrc) + corr
    salida = np.zeros_like(a)
    for c in range(4):
        salida[:, :, c] = ndimage.affine_transform(
            a[:, :, c] * arm_mask, Minv, offset=off, order=1, mode='constant')
    base = a.copy()
    base[arm_mask] = 0                                  # se quita la aguja de su sitio
    dentro = salida[:, :, 3:4] / 255.0
    mezcla = base * (1 - dentro) + salida * dentro
    return Image.fromarray(np.clip(mezcla, 0, 255).astype(np.uint8))


def tono_de_los_indices():
    """La escalera de grises de las barras aplicadas de la esfera.

    Se leen en la esfera ANTRACITA porque ahí el fondo es casi negro y las
    barras se recortan solas; en la blanca la máscara se come la esfera."""
    a = np.asarray(Image.open(os.path.join(CAPAS, '1200', ESFERA_PATRON))
                   .convert('RGBA'))
    L = a[:, :, :3].astype(float).mean(2)
    eje, _, _, _ = eje_del_reloj()
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(x - eje[0], y - eje[1])
    m = (a[:, :, 3] > 250) & (L > 80) & (r > 215) & (r < 320)
    lab, n = ndimage.label(m)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = ndimage.binary_fill_holes(
        np.isin(lab, [i + 1 for i in range(n) if t[i] > 250]))
    return L[m]


def indices_oro_rosa():
    """Los índices de la esfera BLANCA Y ORO ROSA, píxel a píxel (RGB).

    Se cogen por el color, no por el brillo: sobre una esfera blanca lo
    único que distingue una barra de oro rosa es que es CÁLIDA (R−B por
    encima de 18). Filtrando por brillo, como se hace en la antracita, la
    máscara se comía la esfera entera."""
    a = np.asarray(Image.open(os.path.join(CAPAS, '%d/esfera-blanca-oro-rosa.avif' % ANCHO))
                   .convert('RGBA')).astype(float)
    rgb = a[:, :, :3]
    eje, _, _, _ = eje_del_reloj()
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(x - eje[0], y - eje[1])
    m = (a[:, :, 3] > 250) & ((rgb[:, :, 0] - rgb[:, :, 2]) > 18) & (r > 200) & (r < 330)
    lab, n = ndimage.label(m)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = np.isin(lab, [i + 1 for i in range(n) if t[i] > 150])
    return rgb[m]


def lumen(im):
    """El canal de lumen de las agujas de plata.

    El acero es neutro y el lumen es cálido, así que el canal se separa
    solo con R−B ≥ 3. Salen DOS trozos grandes —el del minutero y el de la
    horaria— y ninguno más: si salieran otros, la regla no valdría."""
    a = np.asarray(im).astype(float)
    op = a[:, :, 3] > 250
    cand = op & ((a[:, :, 0] - a[:, :, 2]) >= 3)
    lab, n = ndimage.label(cand)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i in range(n) if t[i] > 800])


def _lut(origen, destino):
    """La tabla que lleva una escalera de grises encima de la otra."""
    bins = np.arange(0, 257)
    co = np.cumsum(np.histogram(origen, bins)[0]).astype(float)
    cd = np.cumsum(np.histogram(destino, bins)[0]).astype(float)
    if co[-1] == 0 or cd[-1] == 0:
        return np.arange(256, dtype=float)
    return np.interp(co / co[-1], cd / cd[-1], np.arange(256))


def _aplica(a, zona, lut):
    """Pinta la zona con la tabla, arrastrando el color con el brillo."""
    L = a[:, :, :3].mean(2)
    Ln = np.interp(L, np.arange(256), lut)
    k = np.where(L > 1, Ln / np.maximum(L, 1e-6), 1.0)
    for c in range(3):
        canal = a[:, :, c]
        canal[zona] = np.clip(canal[zona] * k[zona], 0, 255)
    return a


def iguala_el_tono(im, patron='acero'):
    """Le pone a las agujas el color, el brillo y el tono de los índices.

    Óscar, 30/08/2026: «el color de las agujas, el brillo y el tono tiene
    que ser igual al de los indicadores de la esfera y ahora es más
    blanco». Y con la foto del homenaje delante: «mira cómo son las agujas
    cuando llevan negro».

    ACERO, POR ZONAS. Una barra de la esfera son dos cosas: un marco
    pulido y un CANAL oscuro por dentro (mediana 150). La aguja tiene lo
    mismo —marco y canal de lumen—, pero su canal estaba en 218 y su marco
    en 244, casi plano: de ahí que pareciera plástico blanco al lado de una
    barra de acero. Se emparejan las dos zonas por separado, cada una con
    la suya. Emparejar la aguja entera de una vez no vale: el canal ocupa
    el 16 % de la aguja y el 35 % de la barra, y la cuenta acumulada lo
    dejaba casi tan claro como estaba.

    ORO ROSA, entero. Ahí el marco también es cálido y la regla del R−B no
    separa nada, pero tampoco hace falta: el dibujo de oro rosa ya trae el
    reparto de luces y sombras de las barras (cuartiles 130/191/217 contra
    119/187/231). Se empareja canal por canal —R, G y B por separado—, que
    además de la escalera iguala el tinte."""
    a = np.asarray(im).astype(np.float32).copy()
    op = a[:, :, 3] > 250
    if patron == 'oro-rosa':
        ref = indices_oro_rosa()
        for c in range(3):
            lut = _lut(a[:, :, c][op], ref[:, c])
            canal = a[:, :, c]
            canal[op] = np.interp(canal[op], np.arange(256), lut)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    ref = tono_de_los_indices()
    corte = np.percentile(ref, 35)
    lum = lumen(im) & op
    marco = op & ~lum
    L = a[:, :, :3].mean(2)
    a = _aplica(a, lum,   _lut(L[lum],   ref[ref <= corte]))
    a = _aplica(a, marco, _lut(L[marco], ref[ref > corte]))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def guarda(im, ident):
    for t in TAMANOS:
        chica = (im if t == ANCHO
                 else im.resize((t, round(im.size[1] * t / float(ANCHO))), Image.LANCZOS))
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


def coloca(origen, f_min=1.0, f_seg=1.0, tono='acero'):
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
    # las agujas se estiran ANTES de escalar: así el 5 % es del dibujo, no
    # del encaje, y la escala global sigue siendo la del minutero original.
    if abs(f_min - 1.0) > 1e-6:
        im = estira(im, anc, minutero['mask'], f_min)
        print('  minutero x%.3f -> %5.1f px' % (f_min, minutero['largo'] * s * f_min))
    if segundero and f_seg == 'igual':
        # Óscar, 30/08/2026: «el segundero debe ser igual de largo que el
        # minutero». Se calcula aquí para que no dependa de una cuenta a
        # mano que se queda vieja en cuanto cambie el dibujo.
        f_seg = (minutero['largo'] * f_min) / segundero['largo']
    if segundero and abs(f_seg - 1.0) > 1e-6:
        im = estira(im, anc, segundero['mask'], f_seg)
        print('  segundero x%.3f -> %5.1f px%s' % (
            f_seg, segundero['largo'] * s * f_seg,
            '   ⚠️ sigue sin llegar a los índices'
            if segundero['largo'] * s * f_seg < dentro else '   ✓ ya llega a los índices'))
    if tono:
        n_lum = int((lumen(im) & (np.asarray(im)[:, :, 3] > 250)).sum())
        im = iguala_el_tono(im, tono)
        print('  tono igualado a los índices %s%s' % (
            'de acero' if tono == 'acero' else 'de oro rosa',
            ' (canal de lumen: %d px)' % n_lum if tono == 'acero' else ''))
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                  Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - anc[0] * s),
                          round(eje[1] - anc[1] * s)))
    return L


def hoja(capa, destino):
    L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
    L.alpha_composite(Image.open(os.path.join(CAPAS, '%d/esfera-turquesa.avif' % ANCHO))
                      .convert('RGBA'))
    c = Image.open(os.path.join(CAPAS, '%d/caja-brazalete-acero.avif' % ANCHO)).convert('RGBA')
    L.alpha_composite(c.crop((0, (ALTO_CAJA - ANCHO) // 2,
                              ANCHO, (ALTO_CAJA + ANCHO) // 2)))
    L.alpha_composite(capa)
    L.convert('RGB').save(destino)


if __name__ == '__main__':
    argv = sys.argv[1:]
    def opt(nombre, por_defecto):
        if nombre not in argv:
            return por_defecto
        v = argv[argv.index(nombre) + 1]
        return v if v == 'igual' else float(v)
    f_min = opt('--minutero', 1.0)
    f_seg = opt('--segundero', 1.0)
    args = [a for i, a in enumerate(argv)
            if not a.startswith('--')
            and not (i and argv[i - 1] in ('--minutero', '--segundero', '--tono'))]
    if len(args) < 2:
        sys.exit(__doc__)
    origen, color = args[0], args[1]
    patron = argv[argv.index('--tono') + 1] if '--tono' in argv else 'acero'
    capa = coloca(origen, f_min, f_seg, False if '--sin-tono' in argv else patron)
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
