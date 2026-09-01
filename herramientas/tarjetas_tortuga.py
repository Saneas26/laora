# -*- coding: utf-8 -*-
"""Las cuatro fotos del Tortuga para la landing de la colección.

    python3 herramientas/tarjetas_tortuga.py [--zoom 1.12] [--prueba]

Se arman con las MISMAS capas del configurador, en el orden de la `PILA`
del modelo —correa, esfera, caja (el anillo SUSTITUYE a la caja lisa, así
que va sólo el anillo) y agujas—, para que la foto de la landing sea
exactamente el reloj que se mete en el carrito.

⚠️ LA REFERENCIA Y EL PRECIO NO SE ESCRIBEN AQUÍ: los lleva escritos
`coleccion.html` y salen del catálogo. Aquí sólo se dibuja. Si cambia una
capa de estas combinaciones hay que volver a pasar esto Y subirle el `?v=`
a las tarjetas en `coleccion.html`, o Cloudflare seguirá sirviendo la
foto de antes.

EL ZOOM (Óscar, 01/09/2026: «las quiero con zoom ampliado»). Las capas
llenan el cuadrado de 1.200 y el reloj se come el 82 % del ancho, así que
ampliar es recortar por los cuatro lados y volver a estirar. A 1,12 la
caja todavía cabe entera —corona incluida— y se gana un 12 %; de 1,25 en
adelante el recorte empieza a comerse el canto de la caja y la corona.
"""
import io as _io
import os
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPAS = os.path.join(RAIZ, 'assets/img/tortuga-2026/capas/1200')
DESTINO = os.path.join(RAIZ, 'assets/img/tortuga-2026/tarjetas')
LADO = 1200
FONDO = (233, 233, 231)
PESO = 110000
CALIDADES = (72, 64, 56, 48, 40)
ZOOM = 1.12

# Las cuatro que vende la colección, con la referencia que lleva escrita
# `coleccion.html` al lado para poder cotejarlas de un vistazo.
TARJETAS = {
    'negra':    ('caucho-profesional', 'esfera-negra', 'caja-anillo-negro', 'agujas-acero',
                 'LO-06-44-AC-NEG-NEG-ACE-ZAF-A-CAUCHO-KPRO-NEG-plata'),
    'turquesa': ('caucho-gris', 'esfera-turquesa-champagne', 'caja-anillo-turquesa', 'agujas-acero',
                 'LO-06-44-AC-TUR-TUC-ACE-ZAF-A-CAUCHO-KGRI-plata'),
    'azul':     ('brazalete-cepillado', 'esfera-azul-sunburst', 'caja-anillo-azul', 'agujas-acero',
                 'LO-06-44-AC-AZU-AZS-ACE-ZAF-A-A316-A316SAT-plata'),
    'naranja':  ('caucho-naranja', 'esfera-negra', 'caja-anillo-naranja-grueso', 'agujas-acero',
                 'LO-06-44-AC-NRG-NEG-ACE-ZAF-A-CAUCHO-KNAR-plata'),
}


def arma(capas, zoom=ZOOM):
    """El reloj sobre el crema del papel, como lo pinta el navegador."""
    L = Image.new('RGBA', (LADO, LADO), FONDO + (255,))
    for c in capas:
        im = Image.open(os.path.join(CAPAS, c + '.avif')).convert('RGBA')
        w, h = im.size
        if w != LADO:                      # la correa es más alta: va a ancho
            im = im.resize((LADO, round(h * LADO / w)), Image.LANCZOS)
            w, h = im.size                 # completo y centrada en vertical
        L.alpha_composite(im, (0, (LADO - h) // 2))
    if zoom and abs(zoom - 1.0) > 1e-6:
        lado = round(LADO / zoom)
        o = (LADO - lado) // 2
        L = L.crop((o, o, o + lado, o + lado)).resize((LADO, LADO), Image.LANCZOS)
    return L.convert('RGB')


def main():
    zoom = float(sys.argv[sys.argv.index('--zoom') + 1]) if '--zoom' in sys.argv else ZOOM
    prueba = '--prueba' in sys.argv
    print('ZOOM x%.2f%s' % (zoom, '  (prueba: no se escribe nada)' if prueba else ''))
    for nombre, datos in sorted(TARJETAS.items()):
        capas, ref = datos[:-1], datos[-1]
        im = arma(capas, zoom)
        for q in CALIDADES:
            b = _io.BytesIO()
            im.save(b, 'AVIF', quality=q)
            d = b.getvalue()
            if len(d) <= PESO or q == CALIDADES[-1]:
                break
        if not prueba:
            os.makedirs(DESTINO, exist_ok=True)
            open(os.path.join(DESTINO, nombre + '.avif'), 'wb').write(d)
        print('  %-10s %6d B  %s' % (nombre, len(d), ref))


if __name__ == '__main__':
    main()
