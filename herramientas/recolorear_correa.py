#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiñe la correa de una foto con el color de OTRA foto. Sin IA, sin inventar.

La foto de la correa extendida está hecha en un solo color, y el resto de la
gama existe pero solo en la foto del reloj puesto. En vez de pedir seis
sesiones más, se mide el color real en la foto grande de cada tono y se
traslada al tejido de la abierta.

CÓMO, Y POR QUÉ ASÍ:

- No es un tinte plano. La correa tiene trama, pliegues y sombra, y todo eso
  vive en la LUMINANCIA. Se normaliza la del tejido de origen —media y
  desviación— y se remapea a la media y la desviación medidas en el destino:
  el relieve se conserva y el tono acaba donde tiene que acabar.
- El color se copia del destino en el plano cromático, no se estira el del
  origen. Un beige llevado a negro por multiplicación se queda pardo.

QUÉ NO SE TIÑE:
- Los índices de lume de la esfera, que también son cálidos. Se quitan por
  TAMAÑO, con una apertura morfológica: son islas finas y la correa es una
  masa ancha. Excluirlos con un disco alrededor del reloj era peor, porque
  el disco se comía la correa que pasa por detrás de la caja.
- La hebilla y los pasadores metálicos: son grises neutros y la máscara
  exige tono cálido.
- El fondo: se exige alfa opaco.

Uso:
    python3 herramientas/recolorear_correa.py abierta.png destino.png salida.png
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

LUM = (0.2126, 0.7152, 0.0722)


def luminancia(a):
    return LUM[0] * a[..., 0] + LUM[1] * a[..., 1] + LUM[2] * a[..., 2]


def mascara_tejido(a, calibre=31):
    """El tejido, y solo el tejido.

    Se pide opaco y cálido: eso descarta el fondo, la caja de acero, la
    hebilla y las agujas, que son grises neutros. Pero deja dentro los
    índices de lume de la esfera, que también son cálidos.

    Se quitan por TAMAÑO y no por posición: una apertura —erosión seguida de
    dilatación— borra las islas más finas que el calibre y deja intacta la
    correa, que es una masa ancha y continua. Excluirlos con un disco
    alrededor del reloj era peor: el disco se comía la correa que pasa por
    detrás de la caja y dejaba un halo del color viejo.
    """
    op = a[..., 3] > 200
    R, B = a[..., 0], a[..., 2]
    m = op & (R > B + 22) & (R > 110)

    img = Image.fromarray((m * 255).astype(np.uint8))
    abierta = img.filter(ImageFilter.MinFilter(calibre)).filter(ImageFilter.MaxFilter(calibre))
    # La apertura sola devuelve una correa MORDIDA: la erosión se come el
    # contorno y en las zonas estrechas —el borde junto a las asas, el canto
    # de los agujeros— la dilatación no lo repone, y ahí quedaban motitas del
    # color viejo. Así que la apertura no se usa como máscara, sino como
    # SEMILLA: se ensancha y se corta con la máscara de color original, que sí
    # tiene el borde exacto. Los índices no se recuperan porque están lejos.
    # se ensancha al doble: con una dilatación corta, el pico de correa que se
    # mete bajo las asas quedaba fuera y se veían dos motitas del color viejo
    semilla = np.asarray(abierta.filter(ImageFilter.MaxFilter(calibre * 2 + 1))) > 127
    # Y DENTRO de esa zona, la exigencia de color se afloja. El pespunte y el
    # canto de la correa son bastante más oscuros que la trama y no llegaban
    # al umbral, así que se quedaban del color viejo y se veían: una costura
    # beige sobre la correa verde. Aquí dentro ya no hay nada más que tejido
    # —la caja y la hebilla son grises neutros y siguen fuera por el tono—,
    # así que basta con pedir que tire a cálido.
    return semilla & op & (R > B + 8)


def color_destino(img, franja=(0.08, 0.22)):
    """La correa en la foto del reloj puesto: la franja de arriba, que es
    tejido limpio y sin la cabeza ni la hebilla dentro."""
    a = np.asarray(img.convert('RGBA')).astype(float)
    h, w = a.shape[:2]
    z = a[int(h * franja[0]):int(h * franja[1]), int(w * .36):int(w * .64)]
    o = z[..., 3] > 200
    if o.sum() < 500:
        raise SystemExit('no encuentro la correa en la foto de destino')
    lum = luminancia(z)[o]
    return z[..., 0][o].mean(), z[..., 1][o].mean(), z[..., 2][o].mean(), lum.mean(), lum.std()


def recolorear(abierta, destino, calibre=31):
    a = np.asarray(abierta.convert('RGBA')).astype(float)
    m = mascara_tejido(a, calibre)
    if not m.any():
        raise SystemExit('no encuentro el tejido en la foto abierta')

    dr, dg, db, dlum, dstd = color_destino(destino)
    lum = luminancia(a)
    olum, ostd = lum[m].mean(), lum[m].std()

    # el relieve del tejido, en unidades de desviación, trasladado al destino
    z = (lum - olum) / max(ostd, 1e-6)
    nueva = np.clip(dlum + z * dstd, 4, 250)
    factor = nueva / np.maximum(lum, 1e-6)

    # el color base del destino, modulado por ese relieve
    base = np.stack([np.full(a.shape[:2], dr), np.full(a.shape[:2], dg),
                     np.full(a.shape[:2], db)], axis=2)
    tenido = np.clip(base * (nueva / max(dlum, 1e-6))[..., None], 0, 255)

    suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255
    out = a.copy()
    out[..., :3] = a[..., :3] * (1 - suave[..., None]) + tenido * suave[..., None]
    fuera = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    b = np.asarray(fuera).astype(float)
    print('destino  R %3.0f G %3.0f B %3.0f · luz %5.1f' % (dr, dg, db, dlum))
    print('queda    R %3.0f G %3.0f B %3.0f · luz %5.1f  (%d px teñidos)'
          % (b[..., 0][m].mean(), b[..., 1][m].mean(), b[..., 2][m].mean(),
             luminancia(b)[m].mean(), m.sum()))
    return fuera


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('abierta'); p.add_argument('destino'); p.add_argument('salida')
    p.add_argument('--calibre', type=int, default=31,
                   help='islas más finas que esto se descartan (los índices de lume)')
    a = p.parse_args()
    recolorear(Image.open(a.abierta), Image.open(a.destino), a.calibre).save(a.salida)
    print(a.salida)
