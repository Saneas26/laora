#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quita los bultos que sobresalen del contorno de una capa.

EL PROBLEMA (Óscar, 28/08/2026): «en la caja de acero hay algunas manchas
blancas cerca de las asas». Son cuatro parches casi blancos, uno por asa,
pegados al canto de fuera: restos del recorte, con el borde a escuadra y
sin nada de la textura cepillada del acero.

NO SE PINTA EL FONDO, SE QUITAN. Óscar proponía pintar el fondo del mismo
gris para que no se notaran. No vale: medidos, los parches van del gris
195 al blanco 253, así que no hay un solo gris que los tape, y encima la
capa dejaría de ser transparente —y estas capas se ven sobre el #e9e9e7
de la ficha y sobre el #eae8e8 de la colección—. Quitándolos desaparecen
sobre cualquier fondo.

TAMPOCO SE QUITAN POR EL COLOR. Se probó: «claro y sin textura» pilla
también los brillos pulidos del canto de la caja, que son igual de
blancos. Lo que de verdad distingue al parche es que **está fuera del
contorno**, así que se recorta por geometría y ni un píxel del reloj se
toca.

LA FIRMA DEL BULTO ES UNA PARED RECTA. El canto del asa es una curva que
se mueve medio píxel por fila; el parche, en cambio, deja el canto
CLAVADO en el mismo píxel durante cien filas seguidas —x=1125 a la
izquierda y x=2983 a la derecha, en las cuatro asas— y entra en él de
golpe, con un salto de sesenta píxeles. Así que se buscan las mesetas:
tramos largos donde el canto no se mueve.

Y NO TODA MESETA ES UN BULTO: el punto más ancho de la caja también deja
el canto quieto unas cuantas filas, y ahí no sobra nada. Se distinguen
por el salto. Para cada meseta se ajusta una recta con las filas de antes
y otra con las de después —sin tocar la meseta— y se mira dónde debería
ir el canto. Si la meseta se sale más de `margen` píxeles por fuera de esa
cuerda, es un bulto y se recorta hasta ella; si no, se deja en paz.

DOS CUIDADOS CON ESAS RECTAS, que la primera versión no tenía y por eso
se dejaba el bulto de arriba y se inventaba uno en el flanco:

  · LA MESETA SE ESTIRA ANTES DE MEDIR. El parche no empieza donde el
    canto se queda quieto: antes hay una rampa de treinta filas donde el
    canto se sale a tres píxeles por fila. Si esa rampa se queda dentro
    del apoyo, la recta sale torcida hacia el bulto y el bulto se salva.
    Se estira la meseta mientras el canto corra más de `rampa` px por
    fila.

  · Y SE VUELVE A ESTIRAR ANTES DE RECORTAR, ya con la cuerda en la mano:
    se sigue subiendo y bajando mientras el canto asome más de `margen`
    por fuera de ella. Recortar sólo la meseta deja las dos esquinas del
    parche —la rampa de entrada y la de salida—, que es justo lo que se
    veía todavía en las cuatro asas.

  · UN APOYO TORCIDO NO CUENTA. Por arriba, el apoyo cae en la punta
    redondeada del asa, que es una curva y no una recta. Se mide el error
    del ajuste y el lado que pase de `error` px se descarta; si se
    descartan los dos, la meseta se deja en paz. Con un solo lado bueno
    se PROLONGA ESA RECTA hasta los dos extremos de la meseta. Copiar el
    valor del extremo bueno en el otro extremo —que es lo que hacía la
    primera versión— deja la cuerda plana justo donde el bulto también lo
    está, y entonces el bulto no se sale de nada y se salva.

⚠️ NO VALE MIRAR SI LA FILA TIENE DOS TROZOS para saber si es de un asa.
La caja es un anillo: casi todas sus filas tienen dos trozos, uno por
flanco, y con esa regla el programa se comía el canto del cuerpo. Aquí no
se decide por filas, se decide por mesetas.

Uso:
    python3 herramientas/limpiar_bultos_capa.py caja-4096.png salida.png
"""
import argparse

import numpy as np
from PIL import Image

MESETA = 25       # filas seguidas con el canto quieto para llamarlo meseta
MARGEN = 12       # lo que se le perdona a una meseta antes de llamarla bulto
APOYO = 130       # filas de antes y de después con las que se ajusta la recta
HUECO = 15        # filas que se dejan de colchón entre la meseta y el apoyo
RAMPA = 1.5       # px por fila: por encima de eso, el canto va de subida al bulto
ERROR = 2.0       # px de error del ajuste por encima del cual el apoyo no vale


def canto(m, lado):
    """El píxel de fuera del contorno en cada fila; NaN si la fila está vacía."""
    fuera = np.full(m.shape[0], np.nan)
    for y in range(m.shape[0]):
        i = np.where(m[y])[0]
        if len(i):
            fuera[y] = i.min() if lado < 0 else i.max()
    return fuera


def mesetas(e, largo):
    """Tramos donde el canto no se mueve más de un píxel."""
    fuera = []
    y = 0
    n = len(e)
    while y < n:
        if np.isnan(e[y]):
            y += 1
            continue
        z = y
        while z + 1 < n and not np.isnan(e[z + 1]) and abs(e[z + 1] - e[y]) <= 1:
            z += 1
        if z - y + 1 >= largo:
            fuera.append((y, z))
        y = z + 1
    return fuera


def estira(e, y0, y1, rampa):
    """Mete dentro de la meseta la rampa por la que el canto sube hasta ella."""
    while y0 - 1 >= 0 and not np.isnan(e[y0 - 1]) and abs(e[y0] - e[y0 - 1]) > rampa:
        y0 -= 1
    while y1 + 1 < len(e) and not np.isnan(e[y1 + 1]) and abs(e[y1 + 1] - e[y1]) > rampa:
        y1 += 1
    return y0, y1


def prediccion(e, y0, y1, o):
    """Dónde iría el canto en los dos extremos de la meseta."""
    def recta(desde, hasta):
        ys = np.arange(max(0, desde), min(len(e), hasta))
        ys = ys[~np.isnan(e[ys])]
        if len(ys) < 20:
            return None
        x = e[ys]
        ys = ys.astype(float)
        m, b = np.polyfit(ys, x, 1)
        if np.sqrt(np.mean((x - (m * ys + b)) ** 2)) > o.error:
            return None          # ese apoyo es una curva, no vale
        return m, b
    antes = recta(y0 - o.hueco - o.apoyo, y0 - o.hueco)
    despues = recta(y1 + o.hueco, y1 + o.hueco + o.apoyo)
    if antes is None and despues is None:
        return None
    # Cada extremo lo dice su propia recta; el que no la tenga, la del otro
    # PROLONGADA hasta él.
    ra = antes or despues
    rd = despues or antes
    return ra[0] * y0 + ra[1], rd[0] * y1 + rd[1]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('origen')
    ap.add_argument('salida')
    ap.add_argument('--meseta', type=int, default=MESETA)
    ap.add_argument('--margen', type=float, default=MARGEN)
    ap.add_argument('--apoyo', type=int, default=APOYO)
    ap.add_argument('--hueco', type=int, default=HUECO)
    ap.add_argument('--rampa', type=float, default=RAMPA)
    ap.add_argument('--error', type=float, default=ERROR)
    o = ap.parse_args()

    a = np.asarray(Image.open(o.origen).convert('RGBA')).copy()
    m = a[..., 3] > 128
    ancho = a.shape[1]

    borrados = 0
    for nombre, lado in (('izquierdo', -1), ('derecho', +1)):
        e = canto(m, lado)
        for cruda0, cruda1 in mesetas(e, o.meseta):
            y0, y1 = estira(e, cruda0, cruda1, o.rampa)
            p = prediccion(e, y0, y1, o)
            if p is None:
                print('  meseta y %4d-%4d en x %4d: sin apoyo recto, se deja'
                      % (y0, y1, e[cruda0]))
                continue
            pendiente = (p[1] - p[0]) / max(1, y1 - y0)

            def cuerda(y, _p0=p[0], _y0=y0, _m=pendiente):
                return _p0 + _m * (y - _y0)

            def asomo(y):
                return lado * (e[y] - cuerda(y))

            asoma = max(asomo(y) for y in range(y0, y1 + 1))
            if asoma <= o.margen:
                print('  meseta y %4d-%4d en x %4d: se sale %5.1f px, se deja'
                      % (y0, y1, e[cruda0], asoma))
                continue
            # Las dos esquinas del parche caen fuera de la meseta: se sigue
            # abriendo mientras el canto asome por fuera de la cuerda.
            z0, z1 = y0, y1
            while z0 - 1 >= 0 and not np.isnan(e[z0 - 1]) and asomo(z0 - 1) > o.margen:
                z0 -= 1
            while z1 + 1 < len(e) and not np.isnan(e[z1 + 1]) and asomo(z1 + 1) > o.margen:
                z1 += 1
            print('  BULTO  y %4d-%4d en x %4d: se sale %5.1f px, se recorta '
                  'de %d a %d' % (y0, y1, e[cruda0], asoma, z0, z1))
            for y in range(z0, z1 + 1):
                t = cuerda(y)
                # EL BORDE SUAVIZADO TAMBIÉN. El canto se mide con lo opaco,
                # pero por fuera queda una orla de píxeles medio
                # transparentes; si se dejan, el parche desaparece y en su
                # sitio queda su silueta dibujada a lápiz.
                borde = int(round(e[y]))
                while 0 <= borde + lado < ancho and a[y, borde + lado, 3] > 0:
                    borde += lado
                if lado < 0:
                    x0, x1 = borde, int(round(t)) - 1
                else:
                    x0, x1 = int(round(t)) + 1, borde
                if x1 >= x0:
                    a[y, x0:x1 + 1] = 0
                    borrados += x1 - x0 + 1
        print('canto %s repasado\n' % nombre)

    Image.fromarray(a).save(o.salida)
    print('borrados %d px (%.4f%% de la imagen) · escrita en %s'
          % (borrados, 100.0 * borrados / a[..., 0].size, o.salida))
