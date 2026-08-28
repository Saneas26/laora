#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rescata una esfera que llega sin transparencia y con otro tamaño.

EL CASO (Óscar, 28/08/2026, la esfera Rally). El fichero venía en RGB de
1.254 px, sin canal alfa, y con el DAMERO DE LA TRANSPARENCIA PINTADO
ENCIMA: los cuadraditos grises que enseña el editor estaban dentro de los
píxeles, no eran transparencia de verdad. Puesto tal cual como capa, el
reloj saldría con un tablero de ajedrez alrededor de la esfera.

QUÉ HACE. La esfera es un disco oscuro y el damero es claro, así que se
separan solos. Se ajusta un círculo al borde del disco —fila a fila, el
primer y el último píxel oscuro, tirando lo que se sale—, se recorta por
ahí y se pega en el lienzo de 4.096 con el diámetro y el eje de las demás
esferas.

SE RECORTA UN PELO POR DENTRO (`--dentro`) porque el borde del disco trae
mezclado el gris del damero: dejando esos dos píxeles fuera no queda orla
clara alrededor de la esfera.

EL BORDE SALE SUAVE. La máscara se dibuja a cuatro veces el tamaño y se
reduce, que un círculo recortado a píxel entero se ve dentado.

⚠️ ESTO NO INVENTA RESOLUCIÓN. Si la esfera viene a 1.177 px y hay que
llevarla a 2.236, se agranda al doble y se nota: sale más blanda que las
que llegan ya a tamaño. El programa dice cuánto ha tenido que agrandar.

Uso:
    python3 herramientas/recortar_disco.py rally.png salida-4096.png
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw

LIENZO = 4096
DIAMETRO = 2236        # el de las demás esferas del Lunar, medido
EJE = (2047.5, 1924.5)
OSCURO = 170           # por debajo de esta luz, es esfera; por encima, damero
DENTRO = 2             # px que se recortan por dentro del borde


def circulo(p):
    x, y = p[:, 0].astype(float), p[:, 1].astype(float)
    M = np.c_[2 * x, 2 * y, np.ones(len(p))]
    s, _, _, _ = np.linalg.lstsq(M, x * x + y * y, rcond=None)
    return s[0], s[1], np.sqrt(s[2] + s[0] ** 2 + s[1] ** 2)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('origen')
    ap.add_argument('salida')
    ap.add_argument('--oscuro', type=float, default=OSCURO)
    ap.add_argument('--dentro', type=float, default=DENTRO)
    ap.add_argument('--diametro', type=float, default=DIAMETRO)
    o = ap.parse_args()

    im = Image.open(o.origen).convert('RGB')
    a = np.asarray(im).astype(int)
    osc = a.mean(axis=2) < o.oscuro

    # el borde del disco: el primer y el último píxel oscuro de cada fila y
    # de cada columna, que entre las dos direcciones cubren todo el contorno
    p = []
    for y in range(osc.shape[0]):
        i = np.where(osc[y])[0]
        if len(i) > 20:
            p += [(i[0], y), (i[-1], y)]
    for x in range(osc.shape[1]):
        i = np.where(osc[:, x])[0]
        if len(i) > 20:
            p += [(x, i[0]), (x, i[-1])]
    p = np.array(p, float)
    err = 0.0
    for _ in range(4):
        X, Y, R = circulo(p)
        d = np.abs(np.hypot(p[:, 0] - X, p[:, 1] - Y) - R)
        err = d.mean()
        p = p[d < max(1.5, 2.2 * d.std())]
    print('disco: centro %.2f,%.2f  radio %.2f  (%d puntos, error %.2f px)'
          % (X, Y, R, len(p), err))

    # la máscara redonda, dibujada a 4× para que el borde no salga dentado
    k = 4
    mas = Image.new('L', (im.width * k, im.height * k), 0)
    r = (R - o.dentro) * k
    ImageDraw.Draw(mas).ellipse(
        [X * k - r, Y * k - r, X * k + r, Y * k + r], fill=255)
    mas = mas.resize(im.size, Image.LANCZOS)

    recorte = Image.merge('RGBA', (*im.split(), mas))
    # se recorta al cuadrado justo del disco antes de escalar, que escalar
    # el lienzo entero arrastra el damero y su peso para nada
    caja = (int(X - R) - 2, int(Y - R) - 2, int(X + R) + 3, int(Y + R) + 3)
    recorte = recorte.crop(caja)

    escala = o.diametro / (2 * R)
    lado = int(round(recorte.width * escala))
    print('se agranda %.2f veces (de %.0f px de diámetro a %.0f)'
          % (escala, 2 * R, o.diametro))
    if escala > 1.05:
        print('⚠️  se está inventando tamaño: la esfera saldrá más blanda '
              'que las que llegan ya a 4.096')
    recorte = recorte.resize((lado, lado), Image.LANCZOS)

    fuera = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    # el centro del disco dentro del recorte, ya escalado
    cx = (X - caja[0]) * escala
    cy = (Y - caja[1]) * escala
    fuera.alpha_composite(recorte, (int(round(EJE[0] - cx)), int(round(EJE[1] - cy))))
    fuera.save(o.salida)

    m = np.asarray(fuera)[..., 3] > 128
    ys, xs = np.where(m)
    print('en el lienzo: bbox x %d-%d y %d-%d  centro %.1f,%.1f  diámetro %d'
          % (xs.min(), xs.max(), ys.min(), ys.max(),
             (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2,
             xs.max() - xs.min() + 1))
    print('escrita en ' + o.salida)
