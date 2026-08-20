#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mete la esfera terminada dentro de la caja.

La caja con su correa la genera ChatGPT con el hueco de la esfera vacío
—un disco negro liso—; la esfera sale de la foto del proveedor con el
logotipo ya compuesto (logo_en_esfera.py). Aquí se unen, y no a ojo:

- EL HUECO se localiza rellenando desde el centro la mancha oscura, así
  que da igual lo que haya alrededor.
- LA PERSPECTIVA de la foto del proveedor se corrige: casi nunca sale
  redonda del todo, y una esfera ovalada dentro de una caja redonda
  canta a la legua.
- EL GIRO se endereza con el eje 12-6 que se midió al poner el logo.
- EL BORDE se recorta con antialiasing y se le deja la sombra que
  proyecta el bisel, o la esfera parece pegada encima.

Uso:
    python3 herramientas/esfera_en_caja.py caja.png esfera.png salida.png --giro 16
"""
import argparse
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def hueco(caja, umbral=70, muestra=512):
    """Centro y radio del disco vacío, por relleno desde el centro."""
    a = np.asarray(caja.convert('RGB').resize((muestra, muestra), Image.LANCZOS)).astype(float).mean(axis=2)
    m = a < umbral
    vis = np.zeros_like(m)
    q = deque([(muestra // 2, muestra // 2)])
    vis[muestra // 2, muestra // 2] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < muestra and 0 <= nx < muestra and m[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True
                q.append((ny, nx))
    ys, xs = np.where(vis)
    k = caja.width / muestra
    return ((xs.min() + xs.max()) / 2 * k, (ys.min() + ys.max()) / 2 * k,
            (xs.max() - xs.min()) / 2 * k)


def disco(esfera, umbral=90):
    """El disco de la esfera en la foto del proveedor: centro y semiejes."""
    a = np.asarray(esfera.convert('RGB')).astype(float).mean(axis=2)
    ys, xs = np.where(a < umbral)
    return ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2,
            (xs.max() - xs.min()) / 2, (ys.max() - ys.min()) / 2)


def montar(caja, esfera, giro=0.0, lado=2048, sombra=0.55, dx=0, dy=0, cristal=0.06, holgura=1.0):
    caja = caja.convert('RGB').resize((lado, lado), Image.LANCZOS)
    hx, hy, hr = hueco(caja)

    cx, cy, rx, ry = disco(esfera)
    lo = int(max(rx, ry) * 2.2)
    e = esfera.convert('RGB').crop((int(cx - lo / 2), int(cy - lo / 2),
                                   int(cx + lo / 2), int(cy + lo / 2)))
    if ry != rx:
        e = e.resize((e.width, int(e.height * rx / ry)), Image.LANCZOS)
    e = e.rotate(giro, resample=Image.BICUBIC)

    # HOLGURA: las esferas del proveedor suelen venir con el borde comido
    # por algún lado —muescas de la pieza o del recorte—. Un pelo de más
    # deja ese defecto fuera del círculo que se ve.
    escala = (hr * 2) / (rx * 2) * holgura
    e = e.resize((max(1, int(e.width * escala)), max(1, int(e.height * escala))), Image.LANCZOS)

    m = Image.new('L', e.size, 0)
    ex, ey = e.width / 2, e.height / 2
    ImageDraw.Draw(m).ellipse((ex - hr, ey - hr, ex + hr, ey + hr), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.6))

    s = Image.new('L', e.size, 0)
    ImageDraw.Draw(s).ellipse((ex - hr, ey - hr, ex + hr, ey + hr), fill=255)
    dentro = s.filter(ImageFilter.GaussianBlur(hr * 0.055))
    anillo = np.clip(255 - np.asarray(dentro).astype(float), 0, 255) / 255 * sombra
    ea = np.asarray(e).astype(float) * (1 - anillo[:, :, None])
    e = Image.fromarray(ea.astype(np.uint8))

    # EL REFLEJO DEL CRISTAL. La caja lleva su luz y la esfera viene de
    # una foto plana de estudio: sin esto, el cristal no existe y la
    # esfera parece un adhesivo mate dentro de un aro que sí brilla.
    if cristal:
        gy, gx = np.mgrid[0:e.height, 0:e.width]
        diag = ((gx / e.width) * -1 + (1 - gy / e.height)) / 2      # claro arriba-izquierda
        luz = 1 + (diag - 0.25) * cristal * 2
        ea = np.clip(np.asarray(e).astype(float) * luz[:, :, None], 0, 255)
        e = Image.fromarray(ea.astype(np.uint8))

    out = caja.copy()
    # dx/dy: el centro del disco se saca del contorno, y si la esfera del
    # proveedor viene con una muesca o un trozo comido, ese contorno miente.
    # El eje 12-6 del resultado dice la verdad y con esto se compensa.
    out.paste(e, (int(hx - ex) + dx, int(hy - ey) + dy), m)
    return out, {'hueco': (round(hx), round(hy), round(hr)), 'escala': round(escala, 3),
                 'ajuste': (dx, dy)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('caja'); p.add_argument('esfera'); p.add_argument('salida')
    p.add_argument('--giro', type=float, default=0.0)
    p.add_argument('--lado', type=int, default=2048)
    p.add_argument('--sombra', type=float, default=0.55)
    p.add_argument('--dx', type=int, default=0)
    p.add_argument('--dy', type=int, default=0)
    p.add_argument('--cristal', type=float, default=0.06)
    p.add_argument('--holgura', type=float, default=1.0)
    a = p.parse_args()
    img, info = montar(Image.open(a.caja), Image.open(a.esfera), a.giro, a.lado, a.sombra, a.dx, a.dy, a.cristal, a.holgura)
    img.save(a.salida)
    print(a.salida, info)
