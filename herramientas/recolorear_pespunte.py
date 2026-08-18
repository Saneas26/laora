#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cambia el color del pespunte de la correa de goma del Lunar.

El proveedor hace la MISMA correa —caucho negro con trama de cesta— con
la costura en verde (P-019), naranja (P-020) o blanca (P-025/026). Solo
tenemos foto de la verde, y no hace falta más: sobre un caucho negro, es
decir sin color, el hilo verde es lo único cromático de la imagen, así
que se puede aislar por saturación y teñir de otro color sin tocar nada
más. No se dibuja ni un píxel: se conservan la torsión del hilo, sus
brillos y su relieve; solo cambia el tono.

Ojo: esto vale para el HILO, no para la correa. El caucho es negro, y el
negro no tiene tono que girar: teñirlo sería inventarse la luz de todo
el material. Además el proveedor solo la hace en negro.

Uso: python3 recolorear_pespunte.py
"""
from PIL import Image
import numpy as np

MADRE = 'masters-2026/lunar/capas/goma-negra-costura-verde-madre-4k.png'
DESTINO = 'masters-2026/lunar/capas/'
TONO_VERDE = 120          # el del hilo original, medido en la propia foto
MARGEN = 55               # cuánto se abre la horquilla de tono, en grados


def a_hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); d = mx - mn
    h = np.zeros_like(mx); m = d > 1e-6
    i = (mx == r) & m; h[i] = ((g - b)[i] / d[i]) % 6
    i = (mx == g) & m; h[i] = ((b - r)[i] / d[i]) + 2
    i = (mx == b) & m; h[i] = ((r - g)[i] / d[i]) + 4
    return h / 6.0, np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0), mx


def a_rgb(h, s, v):
    i = np.floor(h * 6.0); f = h * 6.0 - i
    p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s)
    i = (i % 6).astype(int)
    out = np.zeros(h.shape + (3,))
    for k, tres in enumerate([(v, t, p), (q, v, p), (p, v, t),
                              (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack(tres, -1)[m]
    return out


def recolorea():
    a = np.asarray(Image.open(MADRE).convert('RGB')).astype(float) / 255.0
    h, s, v = a_hsv(a)
    hilo = (s > 0.18) & (np.abs(((h * 360) - TONO_VERDE + 180) % 360 - 180) < MARGEN)
    print('hilo aislado: %d px (%.2f%% de la foto)' % (hilo.sum(), 100 * hilo.mean()))

    for nombre, h2, s2, v2 in [
        # naranja de la casa: el tono se fija y la saturación se levanta,
        # que el verde original es más apagado que el naranja laOra
        ('goma-negra-costura-naranja', np.full_like(h, 25 / 360.0),
         np.clip(s * 1.7, 0, .95), np.clip(v * 1.12, 0, 1)),
        # blanco: se le quita el color y se le sube el brillo, porque un
        # hilo blanco luce mucho más que uno verde con la misma luz
        ('goma-negra-costura-blanca', h, np.zeros_like(s), np.clip(v ** 0.55, 0, 1)),
    ]:
        out = a.copy()
        out[hilo] = a_rgb(h2, s2, v2)[hilo]
        Image.fromarray((np.clip(out, 0, 1) * 255).astype('uint8')) \
             .save(DESTINO + nombre + '-madre-4k.png')
        print('escrita', nombre)


if __name__ == '__main__':
    recolorea()
