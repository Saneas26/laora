#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lleva el lume de los índices al tono del reloj de verdad. Sin IA.

El generador suele devolver los triángulos de las horas más TOSTADOS de lo
que son: mismo rojo y mismo verde que el original, pero el azul mucho más
bajo, y eso los convierte en cuero viejo en vez de amarillo pálido. Aquí se
mide el tono de la foto del proveedor y se desplaza el de la nuestra hasta
ese punto, sin tocar nada más.

QUÉ SE TOCA Y QUÉ NO:
- SÍ los índices con lume, que viven en el anillo exterior de la esfera y
  son lo único cálido que hay ahí.
- NO las agujas ni los numerales, que ya son blancos y están más adentro.
- NO el logotipo, que va en plata y por tanto sin color.
- NO la correa: el anillo se queda dentro del disco de la esfera.

El ajuste va sobre las DIFERENCIAS de canal, no sobre valores absolutos,
para que el relieve y la sombra de cada píxel se conserven: si el objetivo
pide R-B = 27 y ahora es 48, el azul sube 21 en todos por igual.

Uso:
    python3 herramientas/tono_lumen.py entrada.png salida.png \
        --centro 2046,1928 --radio 749 --rb 26.4 --gb 20.0
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

ANILLO = (0.74, 1.02)   # dónde viven los índices, en fracción del radio


def mascara(a, centro, radio):
    """Los índices con lume: anillo exterior, claros y cálidos."""
    op = a[..., 3] > 200 if a.shape[2] == 4 else np.ones(a.shape[:2], bool)
    R, B = a[..., 0], a[..., 2]
    mx = a[..., :3].max(2)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d2 = (xx - centro[0]) ** 2 + (yy - centro[1]) ** 2
    anillo = (d2 >= (ANILLO[0] * radio) ** 2) & (d2 < (ANILLO[1] * radio) ** 2)
    return op & anillo & (mx > 140) & (R > B + 12)


def ajustar(img, centro, radio, rb_obj, gb_obj):
    a = np.asarray(img.convert('RGBA')).astype(float)
    m = mascara(a, centro, radio)
    if not m.any():
        raise SystemExit('no encuentro los índices: revisa el centro y el radio')

    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    rb, gb = (R[m] - B[m]).mean(), (G[m] - B[m]).mean()
    sube_b = rb - rb_obj              # cuánto azul falta
    sube_g = gb_obj + sube_b - gb     # y el verde que lo acompaña
    print('ahora  R-B %+.1f · G-B %+.1f  (%d píxeles)' % (rb, gb, m.sum()))
    print('subo   azul %+.1f · verde %+.1f' % (sube_b, sube_g))

    # el borde se difumina medio píxel para que no se vea el recorte
    suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 255
    out = a.copy()
    out[..., 1] = np.clip(G + sube_g * suave, 0, 255)
    out[..., 2] = np.clip(B + sube_b * suave, 0, 255)
    fuera = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    b = np.asarray(fuera).astype(float)
    print('queda  R-B %+.1f · G-B %+.1f  (objetivo %+.1f / %+.1f)'
          % ((b[..., 0][m] - b[..., 2][m]).mean(),
             (b[..., 1][m] - b[..., 2][m]).mean(), rb_obj, gb_obj))
    return fuera, m


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('salida')
    p.add_argument('--centro', required=True, help='cx,cy del disco de la esfera')
    p.add_argument('--radio', type=float, required=True)
    p.add_argument('--rb', type=float, required=True, help='R menos B que se busca')
    p.add_argument('--gb', type=float, required=True, help='G menos B que se busca')
    a = p.parse_args()
    cx, cy = (float(v) for v in a.centro.split(','))
    img, _ = ajustar(Image.open(a.origen), (cx, cy), a.radio, a.rb, a.gb)
    img.save(a.salida)
    print(a.salida)
