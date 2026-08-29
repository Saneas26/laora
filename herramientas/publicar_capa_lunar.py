#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publica una capa del Lunar: del PNG de 4.096 a los tres AVIF que sirve la web.

POR QUÉ EXISTE. Cada capa nueva se venía convirtiendo a mano, y a mano se
olvida algo: el alfa, un tamaño, o la calidad, que en una capa con
transparencia no se puede apretar igual que en una foto. Esto lo hace
siempre igual.

LOS TRES TAMAÑOS son los de la norma de la casa
(laora-formato-imagen-web): 480 para el móvil, 1200 para el visor de
escritorio y 1600 para las pantallas finas. El máster de 4.096 NO se
publica.

⚠️ **SE GUARDA EN RGBA.** Las capas se apilan unas encima de otras; una sola
convertida a RGB tapa a las de abajo con un rectángulo. El programa se
niega a escribir una capa sin canal alfa.

⚠️ **NO ALINEA NI ENCAJA NADA.** Da por hecho que el PNG ya está en su
sitio: eje 2047,50 / 1924,50 y, si es correa, entrando en las asas con
1.324 px de ancho centrados en x = 2054. Para eso están
`alinear_capas_lunar.py` y `encajar_correa.py`. Aquí sólo se avisa si la
medida no cuadra.

Uso:
    python3 herramientas/publicar_capa_lunar.py capa-4096.png [otra.png ...]
    python3 herramientas/publicar_capa_lunar.py --peso 26000 capa-4096.png
"""
import argparse
import io
import os
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, 'assets/img/lunar-2026/capas')
TAMANOS = (480, 1200, 1600)
# Lo que pesan las capas que ya están publicadas, a 1.200. Se busca la
# calidad más alta que quepa; los otros dos tamaños van a escala.
PESO = {480: 7000, 1200: 26000, 1600: 36000}
CALIDADES = (72, 68, 64, 60, 56, 52, 48, 44, 40)

# El hueco entre las asas, medido en el máster de 4.096.
ASAS = (1392, 2716)


def publica(origen, pesos):
    im = Image.open(origen)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    if im.size != (4096, 4096):
        sys.exit('✗ %s no mide 4096x4096 sino %dx%d' % (origen, im.size[0], im.size[1]))
    if im.getchannel('A').getextrema()[0] == 255:
        sys.exit('✗ %s no tiene transparencia: taparía a las capas de debajo' % origen)

    nombre = os.path.basename(origen).replace('-4096.png', '')
    caja = im.getbbox()
    aviso = ''
    if 'correa' in nombre or 'brazalete' in nombre:
        if caja[0] < ASAS[0] - 2 or caja[2] > ASAS[1] + 2:
            aviso = '  ⚠️ se sale de las asas (x %d–%d)' % (caja[0], caja[2])
        elif caja[2] - caja[0] < 1300:
            aviso = '  ⚠️ se queda corta (%d px de ancho)' % (caja[2] - caja[0])

    linea = '%-52s' % nombre
    for t in TAMANOS:
        chico = im.resize((t, t), Image.LANCZOS)
        for q in CALIDADES:
            b = io.BytesIO()
            chico.save(b, 'AVIF', quality=q)
            datos = b.getvalue()
            if len(datos) <= pesos[t] or q == CALIDADES[-1]:
                break
        carpeta = os.path.join(DESTINO, str(t))
        os.makedirs(carpeta, exist_ok=True)
        open(os.path.join(carpeta, nombre + '.avif'), 'wb').write(datos)
        linea += ' %d:%2dq/%5dB' % (t, q, len(datos))
    print(linea + aviso)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('capas', nargs='+')
    ap.add_argument('--peso', type=int, default=None,
                    help='tope en bytes para el de 1.200 (los otros a escala)')
    o = ap.parse_args()
    pesos = dict(PESO)
    if o.peso:
        pesos = {480: int(o.peso * 0.27), 1200: o.peso, 1600: int(o.peso * 1.38)}
    for c in o.capas:
        publica(c, pesos)
