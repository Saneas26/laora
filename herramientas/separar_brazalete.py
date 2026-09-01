#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · SACAR EL BRAZALETE DE DEBAJO DE LA CAJA

Óscar, 01/09/2026, mirando el Murph del Trinchera: «el brazalete de acero
hay que separarlo bastante más y ajustarlo a la caja del reloj, ahora
mismo hay mucho brazalete debajo de la caja».

QUÉ PASABA, medido en el lienzo de 4.096 de la biblioteca. Las cuarenta y
cinco correas de piel, tela y caucho mueren en la fila ~1.731 y vuelven a
empezar en la ~3.815: entran bajo el asa, cruzan un poco y ya. Los seis
BRAZALETES DE ACERO mueren en la ~2.620 y empiezan en la ~2.925, o sea que
sus dos tiras casi se tocan por debajo del cuerpo del reloj: novecientos
píxeles de eslabones escondidos donde no los ve nadie, y en el Trinchera
—cuya caja es más estrecha que la del Lunar— asomando por los lados del
asa. El nato tiene el mismo defecto (muere en la 2.572); no se toca aquí
porque Óscar habló del brazalete.

Y ADEMÁS IBAN ANCHOS: 20,9 a 21,9 mm en las filas del asa, contra los 20,5
de todo lo demás. Ésa es la parte de «ajustarlo a la caja».

LA MEDIDA NO SE INVENTA: se lee de la familia. El objetivo es la MEDIANA de
las correas que ya están bien, así que el día que la familia cambie, esto
cambia con ella y no hay ningún número a mano que se quede viejo.

POR QUÉ SE TRABAJA SOBRE LA PIEZA PUBLICADA Y NO SOBRE EL ORIGINAL. Cuatro
de los seis se reproducen desde su PNG de la entrega —comprobado: IoU
0,987-0,994 y menos de 8 sobre 255 de color—, pero DOS NO: el «centro oro
amarillo pulido» y el «oro rosa» no salen de ninguna de las seis fuentes
(lo más parecido se queda en 17 y 32 sobre 255), así que en algún momento
se recolorearon y ese paso no está escrito en ningún sitio. Rehacerlos
desde la fuente les cambiaría el acabado, que es lo único que no se puede
tocar. Se les hace a los seis la MISMA operación —geométrica, sin tocar un
color— sobre lo que está publicado. Cuesta un reencodeado; equivocarse de
acabado cuesta más.

Uso:
    python3 herramientas/separar_brazalete.py                 (los seis)
    python3 herramientas/separar_brazalete.py acero-316l-cepillado
    python3 herramientas/separar_brazalete.py --prueba        (no publica)
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from preparar_correa_x20 import (ANCHO, ALTO, ASAS, acerca_al_asa,   # noqa: E402
                                 banda_en_las_asas, centra, tiras)
import auditar_correas as AUD                                      # noqa: E402

BIBLIO = os.path.join(RAIZ, 'assets/img/componentes/correas')
BRAZALETES = ('acero-316l-cepillado',
              'acero-316l-centro-pulido',
              'acero-316l-oro-rosa',
              'acero-316l-centro-oro-rosa-pulido',
              'acero-316l-centro-oro-amarillo-pulido',
              'acero-316l-pvd-negro-centro-pulido')


def a_lienzo(ident):
    """La pieza publicada de 1.600, llevada al lienzo de trabajo de 4.096."""
    im = Image.open(os.path.join(BIBLIO, '1600', ident + '.avif')).convert('RGBA')
    k = ANCHO / float(im.width)
    n = im.resize((ANCHO, int(round(im.height * k))), Image.LANCZOS)
    L = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
    L.alpha_composite(n, (0, (ALTO - n.height) // 2))
    return L


def medida(L):
    """(fila donde muere la tira de arriba, ancho en las filas del asa)."""
    a = np.asarray(L)[:, :, 3] > 60
    t = tiras(a)
    return (t[0][1] if t else 0), banda_en_las_asas(L)


def familia():
    """Lo que hacen las correas que YA están bien: la mediana de las que no
    son brazalete de acero ni nato."""
    puntas, anchos = [], []
    for f in sorted(os.listdir(os.path.join(BIBLIO, '1600'))):
        if not f.endswith('.avif'):
            continue
        ident = f[:-5]
        if ident in BRAZALETES or ident.startswith('nato-'):
            continue
        im = Image.open(os.path.join(BIBLIO, '1600', f)).convert('RGBA')
        if im.height <= im.width:          # las cuadradas viejas no cuentan
            continue
        p, an = medida(a_lienzo(ident))
        if p and an:
            puntas.append(p)
            anchos.append(an)
    return int(np.median(puntas)), int(np.median(anchos))


_ASAS_CAJA = None


def _cuanto_falta(M):
    """Los píxeles que le faltan a la correa para tapar el hueco del asa.

    Se mide con el mismo `falta()` de `auditar_correas.py` y contra la misma
    caja que él —la del Lunar, que es la de referencia—, para que aquí no
    haya una segunda opinión sobre lo que está bien."""
    global _ASAS_CAJA
    if _ASAS_CAJA is None:
        caja = AUD.mascara(os.path.join(AUD.CAPAS, '01-caja-acero.avif'))
        _ASAS_CAJA = (AUD.filas_de_asa(caja), caja.shape[0], caja.shape[1])
    asas, alto, ancho_caja = _ASAS_CAJA
    k = ancho_caja / float(M.width)
    n = M.resize((ancho_caja, int(round(M.height * k))), Image.LANCZOS)
    izq, der, _ = AUD.falta(np.asarray(n)[:, :, 3] > AUD.ALFA, asas, alto)
    # el que falte se mide en el lienzo de la caja; se devuelve en el de trabajo
    return max(izq, der) / k


def _monta(L, factor, punta):
    """La pieza a escala, separada y centrada. Siempre desde el original: si
    se escalara sobre lo ya escalado, cada vuelta del bucle añadiría un
    remuestreo."""
    n = L.resize((int(round(ANCHO * factor)), int(round(ALTO * factor))),
                 Image.LANCZOS)
    M = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
    M.alpha_composite(n, (int(round((ANCHO - n.width) / 2.0)),
                          int(round((ALTO - n.height) / 2.0))))
    # las dos tiras, separadas hasta que la de arriba muera donde la familia
    M = acerca_al_asa(M, punta=punta)
    # y el centrado el ÚLTIMO, que mira las filas del asa
    return centra(M)


def arregla(ident, punta, ancho, prueba=False):
    """
    ⚠️ EL ANCHO HAY QUE BUSCARLO, NO CALCULARLO, y ésta fue la primera
    pasada fallida: se escaló por la regla de tres —ancho que quiero entre
    ancho que tengo— y los seis salieron MÁS ANCHOS que antes, de 20,9 a
    22,6 mm. El brazalete va de 20 a 16 mm, así que su ancho depende de POR
    DÓNDE se mida; al separar las tiras novecientos píxeles, lo que queda a
    la altura del asa ya no es el mismo trozo de brazalete, sino uno más
    cercano a la caja y por tanto más ancho. Se mide después de separar, y
    se vuelve a intentar.
    """
    L = a_lienzo(ident)
    p0, an0 = medida(L)
    factor = 1.0
    M = _monta(L, factor, punta)
    for _ in range(8):
        an = banda_en_las_asas(M)
        if not an or abs(an - ancho) <= 2:
            break
        factor *= ancho / float(an)
        M = _monta(L, factor, punta)
    # ⚠️ Y AHORA SE LE PREGUNTA AL AUDITOR, que es quien manda.
    # Poniéndolos en la mediana de la familia, los seis se quedaron 1 o 2 px
    # cortos por la derecha y `auditar_correas.py` los cantó: el brazalete se
    # estrecha hacia la hebilla y en las filas MÁS EXTREMAS del asa —que no
    # son las que mide `banda_en_las_asas`— llega un pelo justo. Se ensancha
    # hasta que no falta nada, y ni un píxel más: lo que sobra lo tapa la
    # caja, lo que falta se ve como una rendija de fondo.
    for _ in range(6):
        f = _cuanto_falta(M)
        if f <= 0:
            break
        factor *= 1.0 + (f + 1) / float(ancho)
        M = _monta(L, factor, punta)
    p1, an1 = medida(M)
    print('%-40s punta %4d -> %4d · asas %4d -> %4d px (%.2f -> %.2f mm)'
          % (ident, p0, p1, an0, an1, an0 / 1284.0 * 20, an1 / 1284.0 * 20))
    salida = os.path.join(os.environ.get('TMPDIR', '/tmp'), ident + '.png')
    M.save(salida)
    if not prueba:
        subprocess.run([sys.executable,
                        os.path.join(RAIZ, 'herramientas/publicar_componente.py'),
                        'correas', ident, salida], check=True,
                       stdout=subprocess.DEVNULL)
    return salida


def main():
    prueba = '--prueba' in sys.argv
    quiere = [a for a in sys.argv[1:] if not a.startswith('--')] or list(BRAZALETES)
    punta, ancho = familia()
    print('LA FAMILIA manda: mueren en la fila %d y miden %d px en las asas '
          '(%.2f mm)\n' % (punta, ancho, ancho / 1284.0 * 20))
    for ident in quiere:
        arregla(ident, punta, ancho, prueba)
    print('\n⚠️  después de esto, `python3 herramientas/auditar_correas.py` '
          'tiene que seguir diciendo 0.')


if __name__ == '__main__':
    main()
