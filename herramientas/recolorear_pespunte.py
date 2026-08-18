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


def hilo_blanco_a_azul():
    """El pespunte de la goma AZUL: de blanco a azul.

    Aquí el reparto es al revés que en la negra —la correa tiene color y
    el hilo no—, así que el hilo se aísla por lo contrario: dentro de la
    zona de la correa, lo poco saturado y muy luminoso. La zona de la
    correa se acota quitando el fondo del estudio y la caja (el alfa de
    la cabeza, con holgura).

    Teñir un hilo BLANCO sí sale bien, al revés que teñir uno negro: el
    blanco lleva toda la luz encima —torsión, brillos y sombras—, y el
    tinte solo le pone color, como el teñido de verdad. Un hilo negro no
    tiene esa luz y no hay nada que teñir.
    """
    from PIL import ImageFilter
    MADRE_AZUL = 'masters-2026/lunar/capas/goma-azul-pespunte-blanco-madre-4k.png'
    a = np.asarray(Image.open(MADRE_AZUL).convert('RGB')).astype(float) / 255.0
    _, s_, v = a_hsv(a)

    fondo = np.abs(a - a[8, 8]).max(axis=2) < 0.055
    cab = np.asarray(Image.open('assets/img/lunar-config/heads/'
                                'cab-acero-bazul-esfblanca-agujas-plateadas.webp')
                     .convert('RGBA'))[:, :, 3] > 40
    cab = np.asarray(Image.fromarray((cab * 255).astype('uint8'))
                     .filter(ImageFilter.MaxFilter(21))
                     .resize(a.shape[1::-1], Image.NEAREST)) > 128
    correa = (~fondo) & (~cab)
    hilo = correa & (s_ < 0.22) & (v > np.percentile(v[correa], 88))
    print('hilo blanco aislado: %d px' % hilo.sum())

    # el borde se difumina, o el tinte deja un halo blanco alrededor
    peso = np.asarray(Image.fromarray((hilo * 255).astype('uint8'))
                      .filter(ImageFilter.MaxFilter(5))
                      .filter(ImageFilter.GaussianBlur(1.6))).astype(float) / 255.0
    peso = np.clip(peso, 0, 1)[..., None]

    # azul claro: se lee sobre el azul marino y rima con el reborde de
    # la propia correa. Un azul más oscuro se confundiría con el fondo.
    tinte = a_rgb(np.full_like(v, 205 / 360.0), np.full_like(v, 0.42), np.clip(v * 0.97, 0, 1))
    out = a * (1 - peso) + tinte * peso
    Image.fromarray((np.clip(out, 0, 1) * 255).astype('uint8')) \
         .save('masters-2026/lunar/capas/goma-azul-pespunte-azul-madre-4k.png')
    print('escrita goma-azul-pespunte-azul')


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
    hilo_blanco_a_azul()
