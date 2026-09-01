# -*- coding: utf-8 -*-
"""Las cuatro fotos del Trinchera para la landing de la colección.

    python3 herramientas/tarjetas_trinchera.py [--prueba]

Mismas capas del configurador y el orden de su `PILA`: correa, ESFERA,
caja —el bisel le tapa el canto a la esfera, como en el reloj de verdad— y
agujas. Las correas salen de la biblioteca compartida.

⚠️ La referencia y el precio los lleva escritos `coleccion.html` y salen
del catálogo; aquí sólo se dibuja. Si cambia una capa hay que volver a
pasar esto Y subirle el `?v=` a las tarjetas en `coleccion.html`.
"""
import io as _io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from tarjeta_de_capas import ESCALA, apila                     # noqa: E402
CAPAS = os.path.join(RAIZ, 'assets/img/trinchera-2026/capas/1200')
CORREAS = os.path.join(RAIZ, 'assets/img/componentes/correas/1200')
DESTINO = os.path.join(RAIZ, 'assets/img/trinchera-2026/tarjetas')
LADO = 1200
FONDO = (233, 233, 231)
PESO = 110000
CALIDADES = (72, 64, 56, 48, 40)

# correa (biblioteca) · esfera · caja · agujas · la referencia que vende
TARJETAS = {
    'acero-negra':   ('acero-316l-cepillado', 'esfera-negra', 'caja-acero', 'agujas',
                      'LO-02-A-PL36-KNEG-A316SAT'),
    'bronce-blanca': ('piel-vintage-conac', 'esfera-blanca', 'caja-bronce', 'agujas',
                      'LO-02-A-BR39-KBLA-PVCO-plata'),
    'pvd-azul':      ('acero-316l-cepillado', 'esfera-azul', 'caja-negra', 'agujas',
                      'LO-02-A-NG39-KAZU-A316SAT'),
    # ⚠️ ERA NATO NEGRO Y YA NO PUEDE SERLO (Óscar, 01/09/2026: «el trinchera
    # murph no va a tener caucho ni nato»). La referencia de esa tarjeta dejó
    # de existir en el catálogo, así que el servidor la habría rechazado al
    # cobrar. Pasa a VAQUERA NEGRA, que es la que deja el precio donde estaba
    # —369,90— y sigue siendo una correa de diario. Las de piel suben a
    # 379,90, la vintage a 399,90 y el brazalete a 409,90.
    'titanio-murph': ('vaquera-negra', 'esfera-murph-crema', 'caja-titanio', 'agujas-murph-crema',
                      'LO-02-A-TI39-MMCR-VNEG'),
}


def pieza(nombre):
    """La correa vive en la biblioteca; el resto, en la carpeta del modelo."""
    f = os.path.join(CAPAS, nombre + '.avif')
    return f if os.path.exists(f) else os.path.join(CORREAS, nombre + '.avif')


def arma(capas, escala=ESCALA):
    """El mismo encuadre que el configurador: alejado, con la correa entera
    (Óscar, 01/09/2026). Ver `tarjeta_de_capas.apila`."""
    return apila([pieza(c) for c in capas], LADO, FONDO, escala).convert('RGB')


def main():
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
