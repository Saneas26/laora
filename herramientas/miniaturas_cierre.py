# -*- coding: utf-8 -*-
"""TRINCHERA · las miniaturas del cierre de la piel italiana.

    python3 herramientas/miniaturas_cierre.py [--prueba]

Óscar, 01/09/2026: «cuando se selecciona piel italiana, hebilla mariposa
es esta imagen que hay que colocar en la fotografía grande, abajo a la
derecha», y otras cuatro para las hebillas clásicas dorada, plateada, oro
rosa y negra.

SON CINCO FOTOS DEL FABRICANTE, la correa entera con su cierre puesto. No
son las del Lunar: aquéllas —`assets/img/lunar-2026/cierres/`— son la
hebilla SOLA en primer plano, y éstas enseñan la correa con la hebilla
montada, que es lo que hace falta cuando la miniatura acompaña a la foto
grande del reloj.

⚠️ CADA UNA VIENE CON LA CORREA DE UN COLOR —la de la mariposa y las de
oro, oro rosa y plata sobre azul marino o negro, la negra sobre marrón—.
Es el catálogo del proveedor, no una serie: la miniatura enseña EL CIERRE,
y por eso el `alt` habla del cierre y no del color de la correa.

CÓMO SE PREPARAN. Llegan como capturas de pantalla: RGB sobre blanco puro,
sin alfa, con márgenes de sobra. Aquí se les quita el blanco —es blanco de
verdad, 255 en las cuatro esquinas—, se quedan las piezas grandes, se
recorta al contenido con un poco de aire y se publica en vertical. Van
`suelta`, o sea sin tarjeta ni fondo, así que el recorte tiene que estar
limpio o se ve el rectángulo blanco sobre el gris del marco.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCRITORIO = '/Users/oscar/Desktop/'
DESTINO = os.path.join(RAIZ, 'assets/img/trinchera-2026/miniaturas')
ALTO = 900                    # el mismo que las del Tortuga
AIRE = 12                     # píxeles de respiro alrededor del recorte
PESO = 45000
CALIDADES = (72, 64, 56, 48, 40)

# id del cierre en la ficha  ->  captura que mandó Óscar
FOTOS = {
    'mariposa': 'Captura de pantalla 2026-08-16 a las 12.37.26.png',
    'oro':      'Captura de pantalla 2026-08-17 a las 18.25.21.png',
    'plata':    'Captura de pantalla 2026-08-17 a las 18.23.08.png',
    'oro-rosa': 'Captura de pantalla 2026-08-17 a las 18.25.02.png',
    'negra':    'Captura de pantalla 2026-08-17 a las 18.24.44.png',
}
NOMBRE = {
    'mariposa': 'cierre-mariposa',
    'oro':      'cierre-clasica-oro',
    'plata':    'cierre-clasica-plata',
    'oro-rosa': 'cierre-clasica-oro-rosa',
    'negra':    'cierre-clasica-negra',
}
ALT = {
    'cierre-mariposa':        'Cierre de mariposa de acero, foto del fabricante',
    'cierre-clasica-oro':     'Hebilla clásica dorada, foto del fabricante',
    'cierre-clasica-plata':   'Hebilla clásica plateada, foto del fabricante',
    'cierre-clasica-oro-rosa': 'Hebilla clásica en oro rosa, foto del fabricante',
    'cierre-clasica-negra':   'Hebilla clásica negra, foto del fabricante',
}


def recorta(ruta):
    """Fuera el blanco, fuera las motas y fuera el margen que sobra."""
    im = Image.open(ruta).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    fondo = (a.min(2) >= 245) & ((a.max(2) - a.min(2)) <= 6)
    lab, n = ndimage.label(~fondo)
    tam = ndimage.sum(~fondo, lab, range(1, n + 1))
    # SE QUEDAN LAS PIEZAS GRANDES: el resto son píxeles sueltos del
    # antialias de la captura, y sin quitarlos salen como puntos negros
    # flotando alrededor de la correa, que va sin tarjeta.
    grandes = [i + 1 for i, t in enumerate(tam) if t > 1500]
    m = ndimage.binary_fill_holes(np.isin(lab, grandes))
    ys, xs = np.where(m)
    caja = (max(0, xs.min() - AIRE), max(0, ys.min() - AIRE),
            min(a.shape[1], xs.max() + 1 + AIRE),
            min(a.shape[0], ys.max() + 1 + AIRE))
    r = im.convert('RGBA')
    r.putalpha(Image.fromarray((m * 255).astype(np.uint8)))
    return r.crop(caja), int(n), len(grandes)


def main():
    prueba = '--prueba' in sys.argv
    if not prueba:
        os.makedirs(DESTINO, exist_ok=True)
    for cierre, captura in sorted(FOTOS.items()):
        origen = ESCRITORIO + captura
        if not os.path.exists(origen):
            print('  %-10s ✗ no está: %s' % (cierre, origen))
            continue
        im, trozos, grandes = recorta(origen)
        s = ALTO / float(im.height)
        im = im.resize((max(1, round(im.width * s)), ALTO), Image.LANCZOS)
        for q in CALIDADES:
            b = _io.BytesIO()
            im.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        ident = NOMBRE[cierre]
        if not prueba:
            open(os.path.join(DESTINO, ident + '.avif'), 'wb').write(d)
        print('  %-10s -> %-24s %dx%d  %6d B  (trozos %d, se quedan %d)'
              % (cierre, ident, im.width, im.height, len(d), trozos, grandes))


if __name__ == '__main__':
    main()
