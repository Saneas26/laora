#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pinta de rojo el segundero de una foto ya aprobada.

El proveedor hace la misma esfera khaki con el segundero blanco o rojo
(1005005292610859). Es el mismo reloj: no hace falta volver a
fotografiar ni a montar nada, basta con teñir esa aguja en la foto que
ya está dada por buena. Así las dos versiones son idénticas en todo lo
demás —misma luz, misma caja, mismo encuadre—, que es lo que se espera
de un catálogo.

CÓMO SE AÍSLA, y por qué no vale lo obvio: coger la mancha clara pegada
al eje y quitarle lo grueso parece lo natural, pero la mancha se escapa
por el antialiasing hasta los numerales y acaba pintando de rojo el 10 y
el 8. Aquí se usa la forma de la aguja:

1. El segundero es LA QUE MÁS LEJOS LLEGA. Se barren los 360° desde el
   eje y se mide hasta dónde sigue habiendo claro; el ángulo que gana es
   el suyo, y da igual la hora que marque el reloj.
2. Se trabaja dentro de un CORREDOR estrecho a lo largo de esa recta, en
   los dos sentidos: así entra la aguja entera —punta, cola y el
   contrapeso redondo del extremo, que va pasado el eje— y no entra nada
   que quede fuera del corredor, por muy claro que sea.
3. Dentro del corredor se descarta lo GRUESO. Hace falta: a las 10:10 la
   aguja de minutos cae casi en la misma recta que la cola del segundero,
   y sin esto se teñía entera. Una apertura —erosionar y dilatar— deja
   fuera lo ancho y conserva lo fino.
4. Se crece desde el eje solo por vecinos claros.

El tono se aplica conservando la luminancia: los brillos y el lume de la
aguja siguen ahí, no es una silueta pintada de plano.

Uso:
    python3 herramientas/segundero_rojo.py foto.png salida.png --centro 1012,950
"""
import argparse
import math
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

ROJO = (0.80, 0.06, 0.06)
PLATA = (0.92, 0.93, 0.94)


def mascara_por_color(img, centro=None, radio=None):
    """El segundero cuando YA es rojo: dentro de la esfera es lo único rojo.

    Más fiable que buscarlo por su forma, así que cuando la madre es la de
    segundero rojo se usa esto y no el barrido de ángulos. Con dos
    cuidados, que costaron un intento: hay que exigir ROJO DE VERDAD —que
    el rojo gane a los otros dos canales por un margen, no que sea el
    mayor— y hay que ceñirse a la esfera, porque un nato marrón o un
    pasador de piel también tienen el rojo por delante y se teñía la
    correa entera.
    """
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    rojizo = (r > 0.30) & ((r - np.maximum(g, b)) > 0.13) & (np.abs(g - b) < 0.20)
    if centro and radio:
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        rojizo &= ((xx - centro[0]) ** 2 + (yy - centro[1]) ** 2) < radio ** 2
    return rojizo


def angulo_del_segundero(claro, cx, cy, r_max):
    """El ángulo donde el claro llega más lejos desde el eje."""
    mejor, ang = 0, 0
    for k in range(720):
        th = math.radians(k / 2)
        s, c = math.sin(th), -math.cos(th)
        alcance, huecos = 0, 0
        for r in range(int(r_max * 0.12), int(r_max)):
            x, y = int(cx + r * s), int(cy + r * c)
            if not (0 <= y < claro.shape[0] and 0 <= x < claro.shape[1]):
                break
            if claro[y, x]:
                alcance, huecos = r, 0
            else:
                huecos += 1
                if huecos > r_max * 0.035:
                    break
        if alcance > mejor:
            mejor, ang = alcance, math.radians(k / 2)
    return ang, mejor


def mascara(img, centro, umbral=150, ancho=22, r_max=None, grueso=9):
    a = np.asarray(img.convert('RGB')).astype(float)
    claro = a.mean(axis=2) > umbral
    cx, cy = centro
    h, w = claro.shape
    if r_max is None:
        r_max = min(cx, cy, w - cx, h - cy) * 0.92

    th, alcance = angulo_del_segundero(claro, cx, cy, r_max)
    s, c = math.sin(th), -math.cos(th)

    # corredor: distancia perpendicular a la recta del segundero. La recta
    # se toma ENTERA, no media: la cola y su contrapeso están al otro lado.
    yy, xx = np.mgrid[0:h, 0:w]
    dx, dy = xx - cx, yy - cy
    perp = np.abs(dx * c - dy * s)
    largo = np.abs(dx * s + dy * c)
    corredor = (perp < ancho) & (largo < r_max)

    zona = claro & corredor
    # crecer desde el eje, solo por vecinos inmediatos
    vis = np.zeros_like(zona)
    q = deque()
    for rr in range(0, 30):
        for k in range(0, 360, 15):
            x = int(cx + rr * math.sin(math.radians(k)))
            y = int(cy - rr * math.cos(math.radians(k)))
            if 0 <= y < h and 0 <= x < w and zona[y, x] and not vis[y, x]:
                vis[y, x] = True
                q.append((y, x))
        if q:
            break
    while q:
        y, x = q.popleft()
        for dy2, dx2 in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            ny, nx = y + dy2, x + dx2
            if 0 <= ny < h and 0 <= nx < w and zona[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True
                q.append((ny, nx))

    # AHORA se quita lo grueso, no antes: si se filtra primero, la aguja
    # queda cortada en el eje —donde se solapan las tres— y el crecimiento
    # no pasa de ahí. Creciendo primero se recorre entera y luego se
    # descarta la de minutos, que a las 10:10 cae en esta misma recta.
    # antes de medir el grosor se CIERRA: la banda de lume que llevan
    # dentro las agujas grandes está separada del cuerpo por un filo más
    # oscuro, y sin cerrarla contaría como pieza fina — salían motas rojas
    # dentro de la aguja de minutos.
    m = Image.fromarray((claro * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    abierta = m.filter(ImageFilter.MinFilter(grueso * 2 + 1)).filter(ImageFilter.MaxFilter(grueso * 2 + 1))
    gruesas = np.asarray(abierta) > 128
    return vis & ~gruesas, math.degrees(th), alcance


def pintar(img, centro, color=ROJO, umbral=150, ancho=22, capuchon=0, grueso=9, radio=None,
           por_color=False):
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    if por_color:
        m, th, alcance = mascara_por_color(img, centro, radio), 0.0, 0
    else:
        m, th, alcance = mascara(img, centro, umbral, ancho, radio, grueso)
    if capuchon:
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        m = m | (((xx - centro[0]) ** 2 + (yy - centro[1]) ** 2) < capuchon ** 2)
    suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255
    lum = a.mean(axis=2)[:, :, None]
    if max(color) > 0.85 and min(color) > 0.6:
        # a plata: el rojo es oscuro, así que hay que LEVANTAR la luz o
        # sale una aguja gris sucia en vez de una plateada
        tenido = np.clip(np.array(color)[None, None, :] * (0.55 + 1.35 * lum), 0, 1)
    else:
        tenido = np.clip(np.array(color)[None, None, :] * (0.45 + 0.9 * lum), 0, 1)
    out = a * (1 - suave[:, :, None]) + tenido * suave[:, :, None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)), int(m.sum()), th, alcance


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('salida')
    p.add_argument('--centro', default='0,0', help='eje de las agujas, x,y')
    p.add_argument('--umbral', type=int, default=150)
    p.add_argument('--ancho', type=int, default=22, help='medio ancho del corredor')
    p.add_argument('--capuchon', type=int, default=0)
    p.add_argument('--a', default='rojo', choices=('rojo', 'plata'), help='color de destino')
    p.add_argument('--por-color', action='store_true',
                   help='la aguja ya es roja: se aísla por color, que es más fiable')
    p.add_argument('--grueso', type=int, default=9, help='lo más ancho que puede ser el segundero')
    p.add_argument('--radio', type=float, default=None,
                   help='radio de la esfera. SIN esto, en una correa clara —el nato de '
                        'franjas grises— el buscador se va a la correa y no encuentra la aguja')
    a = p.parse_args()
    cx, cy = (float(v) for v in a.centro.split(','))
    img, n, th, alc = pintar(Image.open(a.origen), (cx, cy),
                             color=(ROJO if a.a == 'rojo' else PLATA), umbral=a.umbral,
                             ancho=a.ancho, capuchon=a.capuchon, grueso=a.grueso, radio=a.radio,
                             por_color=a.por_color)
    img.save(a.salida)
    print('%s · %d px teñidos · segundero a %.1f° · llega a %d px' % (a.salida, n, th, alc))
