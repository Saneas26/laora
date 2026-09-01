# -*- coding: utf-8 -*-
"""TRINCHERA · monta las capas del configurador.

    python3 herramientas/capas_trinchera.py [--prueba]

Óscar, 30/08/2026: «no hay nada del trinchera». Y era verdad: vendía
6.624 referencias sin una sola imagen. La entrega del 29/08 estaba ahí,
en `tri/outputs/transparentes/`, y esta vez SÍ trae alfa de verdad: no
hay que recortar nada, sólo medir y colocar.

LA CAJA SE COLOCA CONTRA LA CORREA, NO AL REVÉS. Las correas del
Trinchera salen de la biblioteca compartida, que está dibujada para un
hueco de asas de 1412 a 2696 (376 px en el lienzo de 1200): la caja se
escala hasta que su hueco mide eso mismo, y se coloca con el centro del
hueco y el centro de sus dos filas de asa donde los tiene la caja del
Lunar. Así cualquier correa de la biblioteca le entra igual de bien.

LA ESFERA, POR EL OJO DE LA CAJA, y las AGUJAS por el eje del ojo y a la
escala de la esfera, que es lo aprendido en el Precisa: la esfera va
DEBAJO de la caja y el bisel le tapa el canto.

LAS AGUJAS DEPENDEN DE LA ESFERA: el Murph lleva las suyas, con los
numerales en crema o en blanco. El motor lo admite —una capa puede traer
una tabla por esfera en vez de un nombre— y así se declara en la ficha.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGA = '/Users/oscar/Documents/Codex/2026-08-29/tri/outputs/transparentes/'
DESTINO = os.path.join(RAIZ, 'assets/img/trinchera-2026/capas/1200')
ANCHO = 1200
TAMANOS = (480, 1200, 1600)
CALIDADES = (72, 64, 56, 48, 40)
PESO = 95000
FONDO = (233, 233, 231, 255)

# El contrato de la biblioteca, copiado de la caja del Lunar (1200 px).
ASAS_HUECO = 376.0
ASAS_CX = 601.5          # centro del hueco entre asas
ASAS_CY = 554.5          # centro entre la fila de arriba y la de abajo
HOLGURA_ESF = 1.02       # la esfera se mete un pelín bajo el bisel
# EL PELLIZCO DEL MURPH (Óscar, 01/09/2026). Sus numerales de minutos van
# más afuera que los índices de las demás, así que aun con todas las
# esferas del mismo tamaño se quedaban rozando el bisel. Un 1,5 % menos los
# separa lo mismo que los de las otras, y la esfera sigue metiéndose bajo
# el bisel: 1,02 x 0,985 = 1,005 del ojo.
AJUSTE = {'esfera-murph-crema': 0.985, 'esfera-murph-blanca': 0.985}
# LAS AGUJAS NO SE COLOCAN A LA ESCALA DE LA ESFERA (Óscar, 30/08/2026:
# «hay que reducir la imagen de las agujas, se salen de la esfera»). Y es
# verdad: puestas a la escala de la esfera llegaban a 404 px cuando la
# pista de minutos se acaba en 270. El dibujo de las agujas viene más
# largo de lo que le toca a esta esfera, así que se encoge hasta que la
# más larga muere justo dentro de la pista.
# Y AÚN ASÍ SE PASABAN (Óscar, 31/08/2026: «un poco más pequeña la imagen
# de las agujas, siguen siendo más largas de lo normal»). Con el 98 % el
# minutero moría en la pista de minutos, por fuera del anillo de cifras;
# con el 90 % muere en la punta de los triángulos, que es donde acaba un
# minutero de reloj de campo.
PUNTA_AGUJA = 0.90       # de la pista de minutos de la esfera

CAJAS = {'caja-acero': 'trinchera-caja-acero.png',
         'caja-negra': 'trinchera-caja-pvd-negro.png',
         'caja-bronce': 'trinchera-caja-bronce.png',
         'caja-titanio': 'trinchera-caja-titanio.png'}
ESFERAS = {'esfera-negra': 'trinchera-esfera-logo-6mm.png',
           'esfera-blanca': 'trinchera-esfera-blanca-mate.png',
           'esfera-azul': 'trinchera-esfera-azul-degradado.png',
           'esfera-murph-crema': 'trinchera-esfera-murph-negra-v2.png',
           'esfera-murph-blanca': 'trinchera-esfera-murph-blanco-plata.png'}
AGUJAS = {'agujas': 'trinchera-agujas.png',
          'agujas-murph-crema': 'trinchera-agujas-murph-crema.png',
          'agujas-murph-blancas': 'trinchera-agujas-murph-blancas.png'}


def alfa(f):
    return np.asarray(Image.open(f).convert('RGBA'))[:, :, 3] > 128


def asas(f):
    """Fila de asa de arriba y de abajo, y el hueco entre ellas."""
    a = alfa(f)
    tr = []
    for r in np.where(a.any(1))[0]:
        xs = np.where(a[r])[0]
        t = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
        if len(t) == 2:
            tr.append((int(r), int(t[0][-1]), int(t[1][0])))
    ar, ab = tr[0], tr[-1]
    hueco = ((ar[2] - ar[1] - 1) + (ab[2] - ab[1] - 1)) / 2.0
    cx = ((ar[1] + ar[2]) + (ab[1] + ab[2])) / 4.0
    cy = (ar[0] + ab[0]) / 2.0
    return hueco, cx, cy


def ojo(f):
    a = alfa(f)
    h = ndimage.binary_fill_holes(a) & ~a
    lab, n = ndimage.label(h)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = lab == 1 + int(np.argmax(t))
    ys, xs = np.where(m)
    return (float(xs.mean()), float(ys.mean())), float(np.hypot(xs - xs.mean(), ys - ys.mean()).max())


def eje_esfera(f):
    """El eje de la esfera: SU AGUJERO CENTRAL, no el centro del recorte.

    Las esferas del Trinchera traen dibujado el agujero por donde pasa el
    eje de las agujas, y ése es el punto bueno. Colocándolas por el centro
    del recorte, las agujas quedaban un pelo altas y a la derecha del
    centro del dibujo, que es de lo que se quejó Óscar en el Precisa por
    otro motivo."""
    a = alfa(f)
    h = ndimage.binary_fill_holes(a) & ~a
    lab, n = ndimage.label(h)
    if n:
        t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        ys, xs = np.where(lab == 1 + int(np.argmax(t)))
        if len(xs) > 40:
            return float(xs.mean()), float(ys.mean())
    ys, xs = np.where(a)
    return (float(xs.min()) + float(xs.max())) / 2.0, (float(ys.min()) + float(ys.max())) / 2.0


def buje(f):
    """El eje de las agujas: por donde pasan LAS TRES.

    No vale el punto más grueso a secas: en las agujas del Murph la parte
    ancha de una aguja mide más que el buje (62 px de radio contra 37) y
    el eje se iba cien píxeles de su sitio. Se prueban los puntos gordos y
    gana aquel que, quitándole un disco alrededor, deja el dibujo partido
    en más trozos: eso sólo pasa donde se cruzan las agujas."""
    m = alfa(f)
    dt = ndimage.distance_transform_edt(m)
    picos = np.argwhere((dt == ndimage.maximum_filter(dt, 25)) & (dt > dt.max() * 0.45))
    y, x = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    mejor = None
    for py, px in picos:
        r = np.hypot(x - px, y - py)
        lab, n = ndimage.label(m & (r > dt[py, px] * 2.2))
        t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)) if n else []
        brazos = sum(1 for v in t if v > 600)
        if mejor is None or brazos > mejor[0]:
            mejor = (brazos, float(px), float(py))
    return mejor[1], mejor[2]


def pon(im, s, ancla, eje):
    n = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ANCHO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(eje[0] - ancla[0] * s), round(eje[1] - ancla[1] * s)))
    return L


def guarda(im, ident):
    for t in TAMANOS:
        chica = im.resize((t, round(im.size[1] * t / float(ANCHO))), Image.LANCZOS)
        for q in CALIDADES:
            b = _io.BytesIO()
            chica.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        carpeta = os.path.join(os.path.dirname(DESTINO), str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, ident + '.avif'), 'wb').write(d)
    return len(d)


def monta():
    capas = {}
    ref = ENTREGA + CAJAS['caja-acero']
    hueco, cx, cy = asas(ref)
    s = ASAS_HUECO / hueco
    dx, dy = ASAS_CX - cx * s, ASAS_CY - cy * s
    c_ojo, r_ojo = ojo(ref)
    eje = (c_ojo[0] * s + dx, c_ojo[1] * s + dy)
    print('CAJA  hueco de asas %.0f -> %.0f · escala %.4f · eje del reloj %.2f,%.2f · ojo r=%.1f'
          % (hueco, ASAS_HUECO, s, eje[0], eje[1], r_ojo * s))
    for ident, f in sorted(CAJAS.items()):
        im = Image.open(ENTREGA + f).convert('RGBA')
        capas[ident] = pon(im, s, (-dx / s, -dy / s), (0, 0))
    # LA ESFERA, AL OJO, Y CADA UNA CON SU RADIO.
    #
    # ⚠️ NO TODAS ESTÁN DIBUJADAS DEL MISMO TAMAÑO, y eso costó los
    # numerales del Murph. Hasta el 01/09/2026 las cinco se escalaban con
    # el número que salía de la NEGRA (radio 501), y las dos del Murph
    # vienen dibujadas a 545: al montarlas quedaban un 9 % más grandes que
    # el ojo, así que su corona de minutos —que en ellas llega al 96,5 %
    # del radio, mucho más afuera que el 94 % de las demás— se metía debajo
    # del bisel y salía cortada. Óscar, 01/09/2026: «la esfera del murph
    # hay que hacerla un pelín más pequeña, sobre el mismo eje, porque los
    # numerales de los minutos quedan muy cerca del borde de la caja y
    # tienen que verse un poco más».
    #
    # Ahora cada esfera se escala con SU radio, así que todas acaban del
    # tamaño del ojo con la misma holgura bajo el bisel. Y al Murph se le
    # da además un pelín menos —`AJUSTE`— para que sus numerales queden a la
    # misma distancia del bisel que los índices de las otras: con la
    # normalización sola se quedaban al 98,4 % del ojo, o sea rozándolo.
    for ident, f in sorted(ESFERAS.items()):
        ruta = ENTREGA + f
        ce = eje_esfera(ruta)
        ys, xs = np.where(alfa(ruta))
        re = float(np.hypot(xs - ce[0], ys - ce[1]).max())
        se = r_ojo * s * HOLGURA_ESF / re * AJUSTE.get(ident, 1.0)
        print('ESFERA %-22s r=%.1f -> %.1f (escala %.4f%s)'
              % (ident, re, re * se, se,
                 ', ajustada x%.3f' % AJUSTE[ident] if ident in AJUSTE else ''))
        capas[ident] = pon(Image.open(ruta).convert('RGBA'), se, ce, eje)
    # la pista de minutos de la esfera, ya colocada: hasta ahí llegan las agujas
    pista = pista_de_la_esfera(capas['esfera-negra'], eje)
    print('PISTA de minutos a %.1f px · las agujas mueren en %.1f' % (pista, pista * PUNTA_AGUJA))
    for ident, f in sorted(AGUJAS.items()):
        b = buje(ENTREGA + f)
        im = Image.open(ENTREGA + f).convert('RGBA')
        m = np.asarray(im)[:, :, 3] > 128
        ys, xs = np.where(m)
        largo = float(np.hypot(xs - b[0], ys - b[1]).max())
        sa = pista * PUNTA_AGUJA / largo
        capas[ident] = pon(im, sa, b, eje)
        print('AGUJAS %-22s buje %.0f,%.0f · largo %.0f -> %.0f px (escala %.4f)'
              % (ident, b[0], b[1], largo, largo * sa, sa))
    return capas


def pista_de_la_esfera(capa, eje):
    """Hasta dónde llega el dibujo de la esfera: su anillo claro de fuera."""
    a = np.asarray(capa).astype(float)
    m = a[:, :, 3] > 128
    L = a[:, :, :3].mean(2)
    y, x = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(x - eje[0], y - eje[1])
    claro = m & (L > 150)
    if not claro.any():
        return float(r[m].max())
    return float(np.percentile(r[claro], 99.5))


def hoja(capas, destino):
    tiros = [('caja-acero', 'esfera-negra', 'agujas'),
             ('caja-bronce', 'esfera-blanca', 'agujas'),
             ('caja-negra', 'esfera-murph-crema', 'agujas-murph-crema'),
             ('caja-titanio', 'esfera-azul', 'agujas')]
    h = Image.new('RGB', (len(tiros) * 400, 400), FONDO[:3])
    corr = os.path.join(RAIZ, 'assets/img/componentes/correas/1200/piel-vintage-conac.avif')
    tira = Image.open(corr).convert('RGBA') if os.path.exists(corr) else None
    for i, (caja, esf, ag) in enumerate(tiros):
        L = Image.new('RGBA', (ANCHO, ANCHO), FONDO)
        if tira is not None:
            L.alpha_composite(tira.crop((0, (tira.height - ANCHO) // 2,
                                         ANCHO, (tira.height + ANCHO) // 2)))
        for k in (esf, caja, ag):
            L.alpha_composite(capas[k])
        h.paste(L.convert('RGB').resize((400, 400)), (i * 400, 0))
    h.save(destino)


if __name__ == '__main__':
    capas = monta()
    prueba = '--prueba' in sys.argv
    d = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'trinchera-capas.png') if prueba
         else os.path.join(RAIZ, 'herramientas/capturas/trinchera-capas.png'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    hoja(capas, d)
    print('\nhoja de control: ' + d)
    if prueba:
        sys.exit(0)
    print('\nPUBLICADO en assets/img/trinchera-2026/capas/')
    for ident in sorted(capas):
        print('  %-24s %6d B' % (ident, guarda(capas[ident], ident)))
