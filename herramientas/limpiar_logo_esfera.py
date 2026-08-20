#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quita el logotipo ya impreso de una esfera, para poder ponerlo en otra
altura. No hace falta la foto original sin logotipo.

Tres pasos:

1. ENCONTRARLO. El logotipo no se busca a ojo: se toma el archivo con el
   que se imprimió y se prueba a todas las escalas y posiciones, quedándose
   con la que más coincide con lo claro de la esfera. Sale clavado porque
   es literalmente la misma imagen.

2. SALVAR LAS AGUJAS, que pasan por encima y no se pueden borrar con él.
   No sirve distinguirlas por brillo —el logotipo es tan claro como el
   lume— ni por conectividad —se tocan—. Se separan por FORMA: una aguja
   es una recta larga y una letra no. Se erosiona con un segmento de
   setenta píxeles en dieciocho orientaciones; lo único que sobrevive a
   eso es la aguja.

3. RELLENAR. El hueco se cierra por difusión, promediando con lo que lo
   rodea vuelta tras vuelta hasta que el color entra desde los bordes. En
   esa banda la esfera es lisa, así que no hay nada que inventar; después
   se le devuelve el grano que tiene el resto.

Uso:
    python3 herramientas/limpiar_logo_esfera.py esfera.png limpia.png
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

LOGO = 'assets/img/marca/logo-esfera-{modelo}.png'


def buscar(esfera, modelo='trinchera', anchos=range(150, 280, 2), zona=None):
    """Dónde y de qué tamaño está el logotipo. Devuelve (x, y, ancho, alto)."""
    L = Image.open(LOGO.format(modelo=modelo)).convert('RGBA')
    A = np.asarray(esfera.convert('RGB')).astype(float).mean(axis=2)
    H, W = A.shape
    Y0, Y1, X0, X1 = zona or (int(H * .25), int(H * .50), int(W * .35), int(W * .65))
    claro = np.clip((A[Y0:Y1, X0:X1] - 60) / 120, 0, 1)
    mejor = None
    for anch in anchos:
        alto = int(L.height * anch / L.width)
        if alto >= Y1 - Y0 or anch >= X1 - X0:
            continue
        a = np.asarray(L.resize((anch, alto), Image.LANCZOS))[:, :, 3].astype(float) / 255
        peso = a.sum()
        for oy in range(Y1 - Y0 - alto):
            for ox in range(X1 - X0 - anch):
                s = (claro[oy:oy + alto, ox:ox + anch] * a).sum() / peso
                if mejor is None or s > mejor[0]:
                    mejor = (s, ox + X0, oy + Y0, anch, alto)
    return mejor


def alfa_logo(caja, modelo='trinchera'):
    x, y, w, h = caja
    L = Image.open(LOGO.format(modelo=modelo)).convert('RGBA').resize((w, h), Image.LANCZOS)
    return np.asarray(L)[:, :, 3].astype(float) / 255


def rectas(claro, largo=70, orientaciones=18, grosor=6):
    """Lo que sobrevive a erosionar con un segmento largo: las agujas."""
    salida = np.zeros_like(claro)
    for i in range(orientaciones):
        t = np.pi * i / orientaciones
        dx, dy = np.cos(t), np.sin(t)
        e = claro.copy()
        for k in range(-largo // 2, largo // 2 + 1):
            e = np.minimum(e, np.roll(np.roll(claro, int(round(k * dy)), 0), int(round(k * dx)), 1))
        salida = np.maximum(salida, e)
    m = Image.fromarray((salida * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * grosor + 1))
    return (np.asarray(m).astype(float) / 255) * claro


def difundir(canal, hueco, vueltas=800):
    lleno = canal.copy()
    h = hueco > 0.5
    lleno[h] = float(canal[~h].mean())
    for _ in range(vueltas):
        v = np.empty_like(lleno)
        v[1:-1, 1:-1] = (lleno[:-2, 1:-1] + lleno[2:, 1:-1] +
                         lleno[1:-1, :-2] + lleno[1:-1, 2:]) / 4
        v[0], v[-1], v[:, 0], v[:, -1] = lleno[0], lleno[-1], lleno[:, 0], lleno[:, -1]
        lleno[h] = v[h]
    return lleno


def limpiar(img, caja, modelo='trinchera', margen=40, umbral=150,
            largo=70, grano=1.0, vueltas=800, engorde=3):
    A = np.asarray(img.convert('RGB')).astype(float)
    H, W, _ = A.shape
    x, y, w, h = caja
    X0, Y0 = max(0, x - margen), max(0, y - margen)
    X1, Y1 = min(W, x + w + margen), min(H, y + h + margen)
    rec = A[Y0:Y1, X0:X1]
    lum = rec.mean(axis=2)

    a = np.zeros(lum.shape)
    # el logotipo se pegó con alfa suave: los bordes casi transparentes
    # también dejaron color, y si no entran en el hueco quedan de fantasma.
    a[y - Y0:y - Y0 + h, x - X0:x - X0 + w] = (alfa_logo(caja, modelo) > 0.02)
    if engorde:
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8))
                       .filter(ImageFilter.MaxFilter(2 * engorde + 1))).astype(float) / 255

    agujas = rectas((lum > umbral).astype(float), largo)
    agujas = np.asarray(Image.fromarray((agujas * 255).astype(np.uint8))
                        .filter(ImageFilter.GaussianBlur(1.0))).astype(float) / 255
    hueco = np.clip(a - agujas, 0, 1)

    # el grano se mide SOLO en fondo de verdad: si se mide en todo el
    # recorte, las agujas y los numerales disparan la desviación y el
    # relleno sale con una silueta de ruido donde estaban las letras.
    fondo = lum[(a < 0.02) & (agujas < 0.02) & (lum < np.percentile(lum, 55))]
    ruido = float(fondo.std()) if len(fondo) > 100 else 0.0
    salida = rec.copy()
    for c in range(3):
        salida[:, :, c] = difundir(rec[:, :, c], hueco, vueltas)
    if grano and ruido:
        salida += (np.random.default_rng(7).normal(0, ruido, hueco.shape) * hueco)[:, :, None]

    m = np.asarray(Image.fromarray((hueco * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(1.0))).astype(float) / 255
    A[Y0:Y1, X0:X1] = rec * (1 - m[:, :, None]) + salida * m[:, :, None]
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('esfera'); p.add_argument('salida')
    p.add_argument('--modelo', default='trinchera')
    p.add_argument('--caja', help='x,y,ancho,alto si ya se sabe; si no, se busca')
    p.add_argument('--largo', type=int, default=70, help='px que debe medir algo para ser aguja')
    p.add_argument('--umbral', type=float, default=150)
    p.add_argument('--grano', type=float, default=1.0)
    p.add_argument('--vueltas', type=int, default=800)
    a = p.parse_args()
    img = Image.open(a.esfera)
    if a.caja:
        caja = tuple(int(v) for v in a.caja.split(','))
    else:
        s, *caja = buscar(img, a.modelo)
        print('logotipo encontrado en', caja, 'coincidencia %.3f' % s)
    limpiar(img, tuple(caja), a.modelo, umbral=a.umbral, largo=a.largo,
            grano=a.grano, vueltas=a.vueltas).save(a.salida)
    print(a.salida)
