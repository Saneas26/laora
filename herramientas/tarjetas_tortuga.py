# -*- coding: utf-8 -*-
"""Las cuatro fotos del Tortuga para la landing de la colección.

    python3 herramientas/tarjetas_tortuga.py [--escala 0.72] [--prueba]

Se arman con las MISMAS capas del configurador, en el orden de la `PILA`
del modelo —correa, esfera, caja (el anillo SUSTITUYE a la caja lisa, así
que va sólo el anillo) y agujas—, para que la foto de la landing sea
exactamente el reloj que se mete en el carrito.

⚠️ LA REFERENCIA Y EL PRECIO NO SE ESCRIBEN AQUÍ: los lleva escritos
`coleccion.html` y salen del catálogo. Aquí sólo se dibuja. Si cambia una
capa de estas combinaciones hay que volver a pasar esto Y subirle el `?v=`
a las tarjetas en `coleccion.html`, o Cloudflare seguirá sirviendo la
foto de antes.

LA CÁMARA, ALEJADA. Por la mañana Óscar las pidió «con zoom ampliado» y
salieron a 1,12 —un recorte del 12 % por los cuatro lados—. Por la tarde,
al verlas: «el reloj debe presentarse SIEMPRE más alejado con más correa o
brazalete; lo no habitual es hacer zoom». Así que el recorte se va y entra
la escala de la casa, 0,72, la misma de `assets/css/configurador-2026.css`:
la tarjeta enseña el mismo encuadre que el configurador, con la correa de
punta a punta.
"""
import io as _io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from tarjeta_de_capas import ESCALA, apila                     # noqa: E402
CAPAS = os.path.join(RAIZ, 'assets/img/tortuga-2026/capas/1200')
DESTINO = os.path.join(RAIZ, 'assets/img/tortuga-2026/tarjetas')
LADO = 1200
FONDO = (233, 233, 231)
PESO = 110000
CALIDADES = (72, 64, 56, 48, 40)

# Las cuatro que vende la colección, con la referencia que lleva escrita
# `coleccion.html` al lado para poder cotejarlas de un vistazo.
# LAS CUATRO SON LAS DEL CARRITO DE ÓSCAR (01/09/2026: «las 4 promociones
# del tortuga que quiero en la colección son las que tengo en el carrito»).
# Ojo: NO son las cuatro de siempre —tres llevan cuarzo y una mineral, así
# que hay dos a 199,90 y la landing ya no abre por los 339,90 de antes—.
TARJETAS = {
    'naranja':  ('caucho-profesional', 'esfera-negra', 'caja-anillo-naranja-grueso', 'agujas-acero',
                 'LO-06-44-AC-NRG-NEG-ACE-MIN-Q-CAUCHO-KPRO-NEG-plata'),
    'turquesa': ('caucho-profesional', 'esfera-turquesa-sunburst', 'caja-anillo-negro', 'agujas-acero',
                 'LO-06-44-AC-NEG-TUS-ACE-ZAF-A-CAUCHO-KPRO-NEG-plata'),
    'champan':  ('caucho-naranja', 'esfera-turquesa-champagne', 'caja-anillo-turquesa', 'agujas-acero',
                 'LO-06-44-AC-TUR-TUC-ACE-ZAF-Q-CAUCHO-KNAR-plata'),
    'acero':    ('brazalete-cepillado', 'esfera-negra', 'caja-anillo-negro', 'agujas-acero',
                 'LO-06-44-AC-NEG-NEG-ACE-ZAF-Q-A316-A316SAT-plata'),
}


def arma(capas, escala=ESCALA):
    """El reloj sobre el crema del papel, como lo pinta el navegador."""
    return apila([os.path.join(CAPAS, c + '.avif') for c in capas],
                 LADO, FONDO, escala).convert('RGB')


def main():
    escala = (float(sys.argv[sys.argv.index('--escala') + 1])
              if '--escala' in sys.argv else ESCALA)
    prueba = '--prueba' in sys.argv
    print('ESCALA %.2f%s' % (escala, '  (prueba: no se escribe nada)' if prueba else ''))
    for nombre, datos in sorted(TARJETAS.items()):
        capas, ref = datos[:-1], datos[-1]
        im = arma(capas, escala)
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
