# -*- coding: utf-8 -*-
"""Pasa a NEGRO la correa profesional del Tortuga, que llegó dibujada en azul.

    python3 herramientas/correa_a_negro.py

Óscar, 01/09/2026: «la profesional es negra». El render de estudio que
mandó —la pieza 47— está dibujado en azul marino, pero las tres fotos de
la correa de verdad son negras, y la miniatura que se enseña al elegirla
sale de esas fotos: dejarla azul era enseñar dos correas distintas en la
misma pantalla.

CÓMO SE PASA A NEGRO, sin aplanarla. No vale multiplicar por gris: el
caucho se ve porque tiene brillos, y bajándolo todo por igual se queda
como un recorte de cartulina. Se hacen dos cosas por separado:

  · SE LE QUITA EL COLOR sólo al caucho. Se conoce por el tono —el azul
    del render vive entre los 170° y los 270°, y el amarillo y el blanco
    de la tabla impresa están muy lejos—, así que la tabla se queda como
    está y no hay que dibujar ninguna máscara a mano.
  · SE OSCURECE POR ABAJO, no por arriba. Las sombras y el medio tono
    bajan a 0,77 —que es lo que separa el azul de la foto negra medida
    píxel a píxel: mediana 0,255 contra 0,196— y los brillos se dejan
    intactos, con una rampa entre medias. Así el caucho sigue teniendo
    reflejo y no se convierte en una silueta.

⚠️ NO SE TOCA LA FORMA. Ni el alfa, ni un píxel de sitio: es el mismo
dibujo, del mismo tamaño y en el mismo lienzo. Lo único que cambia es el
color, para que `capas_tortuga.py` lo monte igual que montaba el azul.
"""
import os

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ENTREGA = ('/Users/oscar/Documents/Codex/2026-08-31/'
           'tortuga-eres-el-dise-ador-gr/outputs/')
DESTINO = os.path.join(ENTREGA, 'preparadas')
FUENTE = '47-correa-caucho-azul-lujo-4k-hueco-caja-44mm.png'
SALIDA = '47-correa-caucho-profesional-negra.png'

TONO = (170.0, 270.0)      # los grados de azul que lleva el caucho
COLOR_MINIMO = 0.08        # por debajo de esto el tono es ruido: no se toca
OSCURO = 0.77              # lo que bajan sombras y medios tonos
BRILLO_LIBRE = 0.90        # de aquí para arriba el brillo se queda entero
BRILLO_TOPE = 0.50         # y hasta aquí baja del todo


def a_hsv(rgb):
    mx = rgb.max(2)
    mn = rgb.min(2)
    dif = mx - mn
    s = np.where(mx > 0, dif / np.maximum(mx, 1e-6), 0)
    h = np.zeros_like(mx)
    seguro = dif > 1e-6
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    esr = seguro & (mx == r)
    esg = seguro & (mx == g) & ~esr
    esb = seguro & (mx == b) & ~esr & ~esg
    h[esr] = ((g - b)[esr] / dif[esr]) % 6
    h[esg] = ((b - r)[esg] / dif[esg]) + 2
    h[esb] = ((r - g)[esb] / dif[esb]) + 4
    return h * 60.0, s, mx


def de_hsv(h, s, v):
    c = v * s
    x = c * (1 - np.abs((h / 60.0) % 2 - 1))
    m = v - c
    z = np.zeros_like(h)
    tramo = (h / 60.0).astype(int) % 6
    r = np.select([tramo == 0, tramo == 1, tramo == 2, tramo == 3, tramo == 4, tramo == 5],
                  [c, x, z, z, x, c])
    g = np.select([tramo == 0, tramo == 1, tramo == 2, tramo == 3, tramo == 4, tramo == 5],
                  [x, c, c, x, z, z])
    b = np.select([tramo == 0, tramo == 1, tramo == 2, tramo == 3, tramo == 4, tramo == 5],
                  [z, z, x, c, c, x])
    return np.dstack([r + m, g + m, b + m])


def rampa(v):
    """1 arriba del todo (el brillo se queda), OSCURO abajo (la sombra baja)."""
    t = np.clip((v - BRILLO_TOPE) / (BRILLO_LIBRE - BRILLO_TOPE), 0, 1)
    t = t * t * (3 - 2 * t)
    return OSCURO + (1.0 - OSCURO) * t


def main():
    a = np.asarray(Image.open(ENTREGA + FUENTE).convert('RGBA')).astype(np.float32) / 255.0
    rgb, alfa = a[:, :, :3], a[:, :, 3]
    h, s, v = a_hsv(rgb)
    caucho = (s > COLOR_MINIMO) & (h >= TONO[0]) & (h <= TONO[1])
    print('el caucho azul son %d px de los %d que tienen algo de color'
          % (int(caucho.sum()), int((s > COLOR_MINIMO).sum())))
    s2 = np.where(caucho, 0.0, s)
    v2 = np.where(caucho, v * rampa(v), v)
    fuera = np.clip(de_hsv(h, s2, v2), 0, 1)
    out = (np.dstack([fuera, alfa]) * 255).round().astype('uint8')
    if not os.path.isdir(DESTINO):
        os.makedirs(DESTINO)
    Image.fromarray(out).save(os.path.join(DESTINO, SALIDA))
    vis = alfa > 0.8
    print('valor medio: %.3f -> %.3f (la foto de la correa de verdad da 0.196)'
          % (float(v[vis].mean()), float(v2[vis].mean())))
    print('color medio: %.3f -> %.3f' % (float(s[vis].mean()), float(s2[vis].mean())))
    print('alfa intacto:', bool((out[:, :, 3] == (a[:, :, 3] * 255).round()).all()))
    print('escrita en ' + os.path.join(DESTINO, SALIDA))


if __name__ == '__main__':
    main()
