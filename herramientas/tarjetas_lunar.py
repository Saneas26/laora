# -*- coding: utf-8 -*-
"""Las cuatro fotos del Lunar para la landing de la colección.

    python3 herramientas/tarjetas_lunar.py [--cotejo] [--prueba]

Mismas capas del configurador y el orden de su `PILA`: correa, caja,
bisel, esfera y agujas. Las correas salen de la biblioteca compartida; el
resto, de la carpeta del modelo.

⚠️ La referencia y el precio los lleva escritos `coleccion.html` y salen
del catálogo; aquí sólo se dibuja. Si cambia una capa hay que volver a
pasar esto Y subirle el `?v=` a las tarjetas en `coleccion.html`, o
Cloudflare seguirá sirviendo la foto de antes.

POR QUÉ NACE ESTE FICHERO (01/09/2026). Las cuatro fotos del Lunar
estaban publicadas pero no había con qué rehacerlas: cuando Óscar pidió
que todas las imágenes se presentaran alejadas no existía la tabla que
dice qué capas lleva cada tarjeta. Se reconstruyó y se comprobó contra las
cuatro publicadas —diferencia media de 0,46 a 0,58 sobre 255, que es el
ruido del AVIF—, y esa comprobación se queda dentro: `--cotejo` la repite.

EL ENCUADRE lo pone `tarjeta_de_capas.ESCALA`, el mismo 0,72 del
configurador. Ver ahí por qué es ese número y no otro.
"""
import io as _io
import os
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from tarjeta_de_capas import ESCALA, apila                     # noqa: E402

CAPAS = os.path.join(RAIZ, 'assets/img/lunar-2026/capas/1200')
CORREAS = os.path.join(RAIZ, 'assets/img/componentes/correas/1200')
DESTINO = os.path.join(RAIZ, 'assets/img/lunar-2026/tarjetas')
LADO = 1200
FONDO = (233, 233, 231)
PESO = 110000
CALIDADES = (72, 64, 56, 48, 40)

# correa (biblioteca) · caja · bisel · esfera · agujas · la referencia que vende
TARJETAS = {
    'acero-negra':  ('acero-316l-centro-pulido', '01-caja-acero',
                     '02-bisel-negro-taquimetro', '04-esfera-negra-sin-agujas',
                     '06-agujas-plata-para-negra',
                     'LO-03-MQ-PLMIN-NEG-NEG-BLA-A316P'),
    'acero-panda':  ('piel-perforada-negra', '01-caja-acero',
                     '08-bisel-blanco-taquimetro', '10-esfera-panda-sin-agujas',
                     '06-agujas-plata-para-panda',
                     'LO-03-MQ-PLMIN-PAN-BLA-BLA-PNEG'),
    'acero-blanca': ('acero-316l-centro-pulido', '01-caja-acero',
                     '03-bisel-azul-taquimetro',
                     '05-esfera-blanca-subesferas-azules-sin-agujas',
                     '07-agujas-azules-para-blanca',
                     'LO-03-MQ-PLMIN-BLA-AZU-AZU-A316P'),
    'pvd-rally':    ('caucho-curvada-negro-naranja-oro', '22-caja-pvd-negra',
                     '02-bisel-negro-taquimetro', '15-esfera-rally-sin-agujas',
                     '06-agujas-plata-para-rally',
                     'LO-03-MQ-NGMIN-NAR-NEG-BLA-KNNO'),
}


def pieza(nombre):
    """La correa vive en la biblioteca; el resto, en la carpeta del modelo."""
    f = os.path.join(CAPAS, nombre + '.avif')
    return f if os.path.exists(f) else os.path.join(CORREAS, nombre + '.avif')


def arma(capas, escala=ESCALA):
    return apila([pieza(c) for c in capas], LADO, FONDO, escala).convert('RGB')


def cotejo():
    """¿Sigue siendo ésta la tabla de capas de las fotos publicadas?

    Se arma cada tarjeta al encuadre VIEJO —escala 1— y se compara con la
    que está publicada. Por debajo de 3 sobre 255 es el ruido del AVIF; por
    encima, alguien cambió una capa o la tabla dejó de ser verdad.
    """
    import numpy as np
    mal = 0
    for nombre, datos in sorted(TARJETAS.items()):
        pub = os.path.join(DESTINO, nombre + '.avif')
        if not os.path.exists(pub):
            print('  %-14s NO PUBLICADA' % nombre)
            mal += 1
            continue
        a = np.asarray(arma(datos[:-1], 1.0), dtype=np.float32)
        b = np.asarray(Image.open(pub).convert('RGB'), dtype=np.float32)
        d = float(np.abs(a - b).mean())
        print('  %-14s diferencia media %.2f/255 %s'
              % (nombre, d, 'OK' if d < 3 else '⚠️ NO CUADRA'))
        mal += d >= 3
    return mal


def main():
    if '--cotejo' in sys.argv:
        sys.exit(1 if cotejo() else 0)
    prueba = '--prueba' in sys.argv
    for nombre, datos in sorted(TARJETAS.items()):
        capas, ref = datos[:-1], datos[-1]
        im = arma(capas)
        for q in CALIDADES:
            b = _io.BytesIO()
            im.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        if not prueba:
            os.makedirs(DESTINO, exist_ok=True)
            open(os.path.join(DESTINO, nombre + '.avif'), 'wb').write(d)
        print('  %-14s %6d B  %s' % (nombre, len(d), ref))


if __name__ == '__main__':
    main()
