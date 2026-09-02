#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LA CORREA DE ARRIBA SE METÍA MÁS QUE LA DE ABAJO

Óscar, 02/09/2026: «por defecto las correas de arriba de la caja, digamos
la correa norte, siempre queda más debajo de la caja que la correa sur».

TENÍA RAZÓN, Y ERA SIEMPRE EL MISMO NÚMERO. Medido sobre el lienzo de
1.600: el hueco entre las dos tiras de la correa está centrado en la fila
771,5 —mediana de las 38 correas altas de la biblioteca, de 770 a 776,5—,
y el centro geométrico de la caja está en la 740,5 —mediana de las seis
cajas que montan estas correas: las dos del Lunar y las cuatro del
Trinchera, que van de 739,3 a 748,7—. O sea que la correa entera cae
**31 px por debajo de la caja**, y por eso la tira de arriba se esconde
62 px más que la de abajo: 226 contra 164 en la piel vintage, 226 contra
157 en el brazalete de acero, 223 contra 164 en la perforada… todas.

DE DÓNDE VENÍA. `preparar_correa_x20.py` coloca cada correa haciendo
coincidir el centro de su hueco con el del PATRÓN, y el patrón heredó ese
descentrado. Como todas se miden contra él, todas lo arrastran igual.

⚠️ NO SE MUEVE LA CORREA ENTERA, Y ÉSTE FUE EL PRIMER INTENTO FALLIDO.
Subir el dibujo completo 31 px hace dos destrozos: deja 31 filas vacías
abajo —las 38 correas llegan EXACTAS a las dos filas del lienzo, así que al
alejarse se vería el corte flotando— y, sobre todo, lleva a las FILAS DEL
ASA un trozo distinto de correa. Como la correa se estrecha hacia la
hebilla, ese trozo es más fino: seis correas se quedaron cortas y
`auditar_correas.py` las cantó, la de costura lateral por quince píxeles.

LO QUE SE MUEVE SON LOS DOS EXTREMOS DE DENTRO, que es lo único que Óscar
está viendo. A la tira de arriba se le quitan 31 filas por su punta —la que
se mete bajo la caja— y a la de abajo se le añaden 31 por la suya. La
diferencia entre lo que se esconde una y otra pasa de 62 a 0, y NINGÚN
píxel que se vea por fuera de la caja se mueve: las filas del asa siguen
enseñando exactamente lo mismo, los cantos siguen llegando al lienzo y el
auditor sigue diciendo 0.

Las 31 filas que se le añaden a la de abajo se dibujan espejando las suyas
propias. Da igual lo que se pinte ahí: quedan a 195 px por dentro del borde
de la caja, o sea tapadas.

Uso:
    python3 herramientas/subir_correas.py [--prueba] [pieza ...]
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLIO = os.path.join(RAIZ, 'assets/img/componentes/correas')
GRANDE = 1600
LIENZO = 4096                # el lienzo de la casa, el que pide el publicador
CAJAS = (
    'assets/img/lunar-2026/capas/1600/01-caja-acero.avif',
    'assets/img/lunar-2026/capas/1600/22-caja-pvd-negra.avif',
    'assets/img/trinchera-2026/capas/1200/caja-acero.avif',
    'assets/img/trinchera-2026/capas/1200/caja-negra.avif',
    'assets/img/trinchera-2026/capas/1200/caja-bronce.avif',
    'assets/img/trinchera-2026/capas/1200/caja-titanio.avif',
)


def _alfa(ruta, u=60):
    return np.asarray(Image.open(ruta).convert('RGBA'))[:, :, 3] > u


def _tiras(m):
    filas = np.where(m.any(1))[0]
    if not len(filas):
        return []
    cortes = np.where(np.diff(filas) > 1)[0]
    return [(int(t[0]), int(t[-1])) for t in np.split(filas, cortes + 1)]


def centro_de_las_cajas():
    """El centro geométrico de las cajas que montan estas correas, en filas
    del lienzo de 1.600. Es la mediana: cada caja tiene su asimetría y no se
    trata de contentar a una, sino de no favorecer a ninguna."""
    cs = []
    for f in CAJAS:
        r = os.path.join(RAIZ, f)
        if not os.path.exists(r):
            continue
        a = _alfa(r)
        k = GRANDE / float(a.shape[0])
        ys = np.where(a.any(1))[0]
        cs.append((ys.min() + ys.max()) / 2.0 * k)
    return float(np.median(cs)), len(cs)


def altas():
    d = os.path.join(BIBLIO, str(GRANDE))
    fuera = []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.avif'):
            continue
        im = Image.open(os.path.join(d, f))
        if im.height > im.width:
            fuera.append(f[:-5])
    return fuera


def centro_del_hueco(ident):
    """La fila, en coordenadas de la CAJA, donde está el centro del hueco.

    ⚠️ NO TODAS LAS CORREAS SON DOS TIRAS LIMPIAS: la vaquera y las de
    cocodrilo traen algún trozo suelto —una hebilla que no toca la tira, un
    pespunte despegado— y salen tres o cuatro. El hueco es el ESPACIO MÁS
    GRANDE entre trozos, no «el que hay entre el primero y el segundo».
    Devolver `None` y saltárselas no vale: se moverían las 36 y no ellas, y
    quedarían descolocadas respecto de todas las demás."""
    a = _alfa(os.path.join(BIBLIO, str(GRANDE), ident + '.avif'))
    t = _tiras(a)
    if len(t) < 2:
        return None
    huecos = [(t[i + 1][0] - t[i][1], (t[i][1] + t[i + 1][0]) / 2.0)
              for i in range(len(t) - 1)]
    return max(huecos)[1] - (a.shape[0] - GRANDE) / 2.0


def sube(ident, px, prueba=False):
    """Recorta la punta de la tira de arriba y alarga la de abajo.

    ⚠️ SE TRABAJA EN EL LIENZO DE 4.096, que es el que pide
    `publicar_componente.py`. La pieza publicada es de 1.600, así que sube y
    baja una vez."""
    ruta = os.path.join(BIBLIO, str(GRANDE), ident + '.avif')
    im = Image.open(ruta).convert('RGBA')
    k = LIENZO / float(im.width)
    im = im.resize((LIENZO, int(round(im.height * k))), Image.LANCZOS)
    px = int(round(px * k))
    a = np.asarray(im).copy()
    t = _tiras(np.asarray(im)[:, :, 3] > 60)
    if len(t) < 2:
        raise SystemExit('✗ %s: no le encuentro dos tiras' % ident)
    # el hueco es el ESPACIO MÁS GRANDE entre trozos (ver centro_del_hueco)
    i = max(range(len(t) - 1), key=lambda j: t[j + 1][0] - t[j][1])
    fin, ini = t[i][1], t[i + 1][0]
    if ini - fin <= px:
        raise SystemExit('✗ %s: el hueco son %d filas y hay que mover %d'
                         % (ident, ini - fin, px))
    a[fin - px + 1:fin + 1] = 0                     # la de arriba, más corta
    a[ini - px:ini] = a[ini:ini + px][::-1]         # la de abajo, más larga
    salida = os.path.join(os.environ.get('TMPDIR', '/tmp'), ident + '.png')
    Image.fromarray(a).save(salida)
    if not prueba:
        subprocess.run([sys.executable,
                        os.path.join(RAIZ, 'herramientas/publicar_componente.py'),
                        'correas', ident, salida], check=True,
                       stdout=subprocess.DEVNULL)
    return salida


def cuadra_el_sur(ident, caja, prueba=False):
    """Sube (o baja) SÓLO la punta de dentro de la tira de abajo.

    Óscar, 02/09/2026, mirando el Trinchera: «el brazalete acero sur, tiene
    que subir un pelín». Y es verdad: la pasada general subió las 45 correas
    lo mismo —31 px, la mediana—, y a los seis brazaletes de acero les
    faltaban entre 7 y 10 para quedar simétricos, porque su hueco no estaba
    donde el de la mediana.

    SÓLO SE TOCA EL SUR. Moviendo las dos puntas se movería también lo que
    se ve por fuera; moviendo la de abajo, el hueco se centra y en el visor
    no cambia ni un píxel de lo que asoma.

    Lo que hay que mover es el DOBLE del desvío: el centro del hueco es el
    punto medio de las dos puntas, así que moviendo una sola punta X, el
    centro se mueve X/2."""
    a = _alfa(os.path.join(BIBLIO, str(GRANDE), ident + '.avif'))
    t = _tiras(a)
    i = max(range(len(t) - 1), key=lambda j: t[j + 1][0] - t[j][1])
    desvio = ((t[i][1] + t[i + 1][0]) / 2.0 - (a.shape[0] - GRANDE) / 2.0) - caja
    px = int(round(2 * desvio))
    if not px:
        return 0
    ruta = os.path.join(BIBLIO, str(GRANDE), ident + '.avif')
    im = Image.open(ruta).convert('RGBA')
    k = LIENZO / float(im.width)
    im = im.resize((LIENZO, int(round(im.height * k))), Image.LANCZOS)
    n = int(round(abs(px) * k))
    b = np.asarray(im).copy()
    t2 = _tiras(np.asarray(im)[:, :, 3] > 60)
    j = max(range(len(t2) - 1), key=lambda q: t2[q + 1][0] - t2[q][1])
    ini = t2[j + 1][0]
    if px > 0:                                   # el sur SUBE: se alarga
        b[ini - n:ini] = b[ini:ini + n][::-1]
    else:                                        # el sur BAJA: se recorta
        b[ini:ini + n] = 0
    salida = os.path.join(os.environ.get('TMPDIR', '/tmp'), ident + '.png')
    Image.fromarray(b).save(salida)
    if not prueba:
        subprocess.run([sys.executable,
                        os.path.join(RAIZ, 'herramientas/publicar_componente.py'),
                        'correas', ident, salida], check=True,
                       stdout=subprocess.DEVNULL)
    return px


def main():
    prueba = '--prueba' in sys.argv
    solo_sur = '--sur' in sys.argv
    quiere = [a for a in sys.argv[1:] if not a.startswith('--')] or altas()
    caja, cuantas = centro_de_las_cajas()
    if solo_sur:
        print('EL CENTRO DE LA CAJA está en la fila %.1f (mediana de %d cajas)\n'
              % (caja, cuantas))
        for ident in quiere:
            antes = centro_del_hueco(ident)
            px = cuadra_el_sur(ident, caja, prueba)
            print('  %-46s hueco %.1f -> %.1f · el sur %s %d px'
                  % (ident, antes, centro_del_hueco(ident) if prueba else antes - px / 2.0,
                     'sube' if px > 0 else 'baja', abs(px)))
        print('\n⚠️  y `python3 herramientas/auditar_correas.py` tiene que seguir '
              'diciendo 0.')
        return
    huecos = [centro_del_hueco(i) for i in altas()]
    huecos = [h for h in huecos if h is not None]
    correa = float(np.median(huecos))
    px = int(round(correa - caja))
    print('EL CENTRO DE LA CAJA está en la fila %.1f (mediana de %d cajas)' % (caja, cuantas))
    print('EL HUECO DE LA CORREA, en la %.1f (mediana de %d correas, de %.1f a %.1f)'
          % (correa, len(huecos), min(huecos), max(huecos)))
    print('=> hay que SUBIR las correas %d px del lienzo de %d\n' % (px, GRANDE))
    if px <= 0:
        print('nada que hacer.')
        return
    for ident in quiere:
        antes = centro_del_hueco(ident)
        sube(ident, px, prueba)
        print('  %-46s hueco %.1f -> %.1f' % (ident, antes, antes - px))
    print('\n⚠️  ahora `python3 herramientas/auditar_correas.py` tiene que '
          'seguir diciendo 0.')


if __name__ == '__main__':
    main()
