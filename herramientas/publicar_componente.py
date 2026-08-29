#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LA BIBLIOTECA DE COMPONENTES

Óscar, 29/08/2026: «vamos a hacer imágenes de componentes, y las mismas
correas para el Lunar me servirán para el Trinchera, para el Cero Cero,
etc. Así será mucho menos material, e intercambiables. Ahora será piel
vaca italiana negra, y no un solo modelo con toda la referencia para
colocar una foto. Se monta la caja, el bisel, la esfera, las agujas por
separado, la correa… etc.»

QUÉ CAMBIA. Una imagen deja de pertenecer a un modelo y pasa a ser una
PIEZA con nombre propio. La correa de piel italiana negra se publica una
vez, en `assets/img/componentes/correas/`, y la usan todos los modelos que
la monten. Antes cada modelo llevaba su carpeta y sus fotos: la misma
correa se guardaba tantas veces como relojes la llevaran.

CÓMO SE LLAMAN. Por lo que SON, no por dónde van:

    correas/piel-italiana-negra-pespunte-blanco
    correas/caucho-azul
    correas/acero-316l-centro-pulido
    cajas/acero-40
    biseles/negro-taquimetro
    esferas/negra
    agujas/plata

Sin número de orden y sin nombre de modelo. Un número de orden ata la
pieza al día en que llegó, y el nombre de un modelo ata una pieza
compartida a uno solo de los que la usan.

LOS GRUPOS son los del montaje, de atrás hacia delante:
`correas · cajas · biseles · esferas · agujas`.

⚠️ SE GUARDA EN RGBA y se niega a publicar una capa sin transparencia: las
piezas se apilan unas sobre otras y una sola en RGB taparía a las de
debajo con un rectángulo.

⚠️ NO ALINEA NI ENCAJA NADA. Da por hecho que el PNG ya viene en su sitio:
lienzo de 4.096, eje 2047,50 / 1924,50 y, si es correa, entrando en las
asas con 1.324 px de ancho centrados en x = 2054. Aquí solo se avisa si la
medida no cuadra.

Uso:
    python3 herramientas/publicar_componente.py correas piel-italiana-negra fuente.png
    python3 herramientas/publicar_componente.py --lista mapa.tsv
"""
import argparse
import io as _io
import os
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLIOTECA = os.path.join(RAIZ, 'assets/img/componentes')
GRUPOS = ('correas', 'cajas', 'biseles', 'esferas', 'agujas')
TAMANOS = (480, 1200, 1600)
PESO = {480: 9000, 1200: 34000, 1600: 46000}
CALIDADES = (72, 68, 64, 60, 56, 52, 48, 44, 40)
# ⚠️ Desde el 29/08/2026 la caja del Lunar va encogida un 3 %% y sus asas
# están en 1412–2696 (hueco 1284): LA CORREA DE 20 MM MANDA y la caja se
# ajustó a ella, no al revés. Una correa nueva se dibuja a 20 mm
# (1 mm = 65,4 px del original) y con eso SOBRA para el hueco.
ASAS = (1412, 2696)


def publica(grupo, ident, origen):
    if grupo not in GRUPOS:
        sys.exit('✗ grupo desconocido: %s (son %s)' % (grupo, ', '.join(GRUPOS)))
    im = Image.open(origen)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    if im.size != (4096, 4096):
        sys.exit('✗ %s no mide 4096x4096 sino %dx%d' % (origen, im.size[0], im.size[1]))
    if im.getchannel('A').getextrema()[0] == 255:
        sys.exit('✗ %s no tiene transparencia: taparía a las piezas de debajo' % origen)

    caja = im.getbbox()
    aviso = ''
    if grupo == 'correas':
        # ⚠️ PASARSE ESTÁ BIEN; QUEDARSE CORTA, NO. La correa va DETRÁS de la
        # caja: lo que sobresale del hueco lo tapan las asas y no se ve. Lo
        # que se ve —y canta— es el fondo asomando entre el asa y la correa.
        # Por eso aquí solo se avisa de lo segundo.
        ancho = caja[2] - caja[0]
        hueco = ASAS[1] - ASAS[0]
        if ancho < hueco - 8:
            aviso = ('  ⚠️ se queda corta: %d px para un hueco de %d. '
                     'Pásala por encajar_correa.py' % (ancho, hueco))

    linea = '%-10s %-42s' % (grupo, ident)
    for t in TAMANOS:
        chica = im.resize((t, t), Image.LANCZOS)
        for q in CALIDADES:
            b = _io.BytesIO()
            chica.save(b, 'AVIF', quality=q)
            datos = b.getvalue()
            if len(datos) <= PESO[t] or q == CALIDADES[-1]:
                break
        carpeta = os.path.join(BIBLIOTECA, grupo, str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, ident + '.avif'), 'wb').write(datos)
        linea += ' %d:%5dB' % (t, len(datos))
    print(linea + aviso)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('grupo', nargs='?')
    ap.add_argument('ident', nargs='?')
    ap.add_argument('origen', nargs='?')
    ap.add_argument('--lista', help='fichero con «grupo<TAB>id<TAB>ruta» por línea')
    o = ap.parse_args()
    if o.lista:
        with open(o.lista, encoding='utf-8') as f:
            for n, linea in enumerate(f, 1):
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue
                trozos = linea.split('\t')
                if len(trozos) != 3:
                    sys.exit('✗ línea %d: hacen falta tres columnas' % n)
                publica(*trozos)
    else:
        if not (o.grupo and o.ident and o.origen):
            sys.exit('✗ hacen falta grupo, id y fichero, o --lista')
        publica(o.grupo, o.ident, o.origen)
