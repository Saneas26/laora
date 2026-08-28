#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cuadra el eje central de las capas del configurador del Lunar.

EL ENCARGO (Óscar, 28/08/2026): «un montaje por capas a ver si funciona
de una vez por todas. Debemos conseguir que coincidan el eje central de
la caja, bisel, esfera y agujas».

CADA CAPA SE MIDE COMO TOCA, que es lo que hace que esto funcione. El
centro del recuadro que ocupa la capa NO sirve casi nunca:

  · BISEL y ESFERA son un anillo y un disco centrados: ahí el recuadro
    SÍ vale, y de hecho las cuatro caen clavadas en el mismo punto.
  · La CAJA lleva corona y pulsadores a la derecha, que le tiran del
    recuadro. Su eje es el del AGUJERO donde va la esfera: se inunda
    desde el centro y se toma el punto medio de cada fila y de cada
    columna de la franja central. Sale con menos de un píxel de
    desviación.
  · Las AGUJAS no son simétricas —dos brazos arriba y un segundero con
    contrapeso abajo—, así que ni el recuadro ni el centroide valen. Su
    eje es el del HUB, la tapa redonda del centro. Se lanzan rayos, se
    coge el borde del hub allí donde no lo tapa ningún brazo y se ajusta
    un círculo, tirando los puntos que se salen. Quedan ochocientos y
    pico puntos con medio píxel de error.

LO QUE SALIÓ. Con la esfera y el bisel como referencia (2047,5 / 1924,5):

    caja ............ 5,0 px a la izquierda
    agujas plata .... 4,1 px abajo
    agujas azules ... 6,9 px abajo

Las dos capas de agujas NO son la misma imagen pintada de otro color:
se solapan al 87 % y uno está 3 px por debajo del otro. Por eso cada una
lleva su corrección.

SE MUEVE EN PÍXELES ENTEROS, sin remuestrear: medio píxel a 4096 es
0,15 px en la foto de 1.200 que se publica, y remuestrear ablandaría el
filo de las agujas por corregir algo que nadie puede ver.

Uso:
    python3 herramientas/alinear_capas_lunar.py <carpeta> [<salida>]
"""
import argparse
import os
import sys
from collections import deque

import numpy as np
from PIL import Image


def mascara(ruta, umbral=128):
    return np.asarray(Image.open(ruta).convert('RGBA'))[..., 3] > umbral


def eje_bbox(m):
    """Para un anillo o un disco centrados: el centro del recuadro."""
    ys, xs = np.where(m)
    return (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0


def eje_agujero(m, semilla):
    """Para la caja: el centro del agujero donde va la esfera.

    La corona y los pulsadores le tiran del recuadro a la caja, así que su
    recuadro miente. El agujero, en cambio, es redondo y limpio.
    """
    hueco = ~m
    h, w = hueco.shape
    vis = np.zeros_like(hueco, bool)
    q = deque([semilla])
    vis[semilla] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and hueco[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True
                q.append((ny, nx))
    ys, xs = np.where(vis)
    cy = (ys.min() + ys.max()) // 2
    cx = (xs.min() + xs.max()) // 2
    # el punto medio de cada fila y de cada columna de la franja central
    mx = [np.where(vis[y])[0] for y in range(cy - 500, cy + 501, 10)]
    my = [np.where(vis[:, x])[0] for x in range(cx - 500, cx + 501, 10)]
    px = [(v.min() + v.max()) / 2.0 for v in mx if len(v)]
    py = [(v.min() + v.max()) / 2.0 for v in my if len(v)]
    return float(np.median(px)), float(np.median(py))


def _circulo(p):
    x, y = p[:, 0], p[:, 1]
    a = np.c_[2 * x, 2 * y, np.ones(len(x))]
    s, *_ = np.linalg.lstsq(a, x ** 2 + y ** 2, rcond=None)
    cx, cy = s[0], s[1]
    return cx, cy, np.sqrt(s[2] + cx * cx + cy * cy)


def eje_hub(m, c0, rmin=55, rmax=130):
    """Para las agujas: el centro de la tapa redonda del eje.

    Se lanzan rayos desde un centro aproximado y se apunta dónde acaba la
    capa. Donde hay brazo, el rayo sale lejos y el punto se descarta por el
    rango; donde no lo hay, el rayo topa con el borde del hub. Con esos
    puntos se ajusta un círculo y se repite tirando los que se salen.
    """
    pts = []
    for i in range(1440):
        t = np.deg2rad(i / 4.0)
        for q in np.arange(20, rmax + 10, 0.5):
            x = int(round(c0[0] + q * np.cos(t)))
            y = int(round(c0[1] - q * np.sin(t)))
            if not m[y, x]:
                if rmin < q < rmax:
                    pts.append((c0[0] + q * np.cos(t), c0[1] - q * np.sin(t)))
                break
    p = np.array(pts)
    for _ in range(6):
        cx, cy, r = _circulo(p)
        d = np.abs(np.hypot(p[:, 0] - cx, p[:, 1] - cy) - r)
        deja = d < max(3.0, np.percentile(d, 80))
        if deja.sum() < 80 or deja.all():
            break
        p = p[deja]
    cx, cy, r = _circulo(p)
    d = np.abs(np.hypot(p[:, 0] - cx, p[:, 1] - cy) - r)
    return cx, cy, r, len(p), float(d.mean())


COMO = {'caja': 'agujero', 'bisel': 'bbox', 'esfera': 'bbox', 'agujas': 'hub'}


def tipo(nombre):
    n = nombre.lower()
    for k in COMO:
        if k in n:
            return k
    return 'bbox'


def mide(ruta, aprox):
    m = mascara(ruta)
    t = tipo(os.path.basename(ruta))
    if COMO[t] == 'agujero':
        cx, cy = eje_agujero(m, (int(aprox[1]), int(aprox[0])))
        return t, cx, cy, ''
    if COMO[t] == 'hub':
        cx, cy, r, n, err = eje_hub(m, aprox)
        return t, cx, cy, 'hub de %.0f px con %d puntos, error medio %.2f px' % (r, n, err)
    cx, cy = eje_bbox(m)
    return t, cx, cy, ''


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta')
    ap.add_argument('salida', nargs='?')
    ap.add_argument('--eje', default=None, help='eje de destino, «x,y»')
    o = ap.parse_args()
    salida = o.salida or os.path.join(os.path.dirname(o.carpeta.rstrip('/')), 'capas-alineadas')
    os.makedirs(salida, exist_ok=True)

    fich = sorted(f for f in os.listdir(o.carpeta) if f.endswith('4096.png'))
    if not fich:
        sys.exit('no hay capas de 4096 en ' + o.carpeta)

    # La referencia sale del bisel: es un anillo perfecto y no tiene nada que
    # le tire del recuadro. Si no hay bisel, se usa el centro del lienzo.
    ref = None
    if o.eje:
        ref = tuple(float(v) for v in o.eje.split(','))
    else:
        for f in fich:
            if 'bisel' in f.lower():
                ref = eje_bbox(mascara(os.path.join(o.carpeta, f)))
                break
    if ref is None:
        ref = (2047.5, 2047.5)
    print('EJE DE DESTINO: %.2f, %.2f\n' % ref)

    for f in fich:
        ruta = os.path.join(o.carpeta, f)
        t, cx, cy, extra = mide(ruta, ref)
        dx, dy = int(round(ref[0] - cx)), int(round(ref[1] - cy))
        a = np.asarray(Image.open(ruta).convert('RGBA'))
        if dx or dy:
            b = np.roll(np.roll(a, dy, axis=0), dx, axis=1)
            # que no se cuele nada por el borde contrario
            if dx > 0: b[:, :dx] = 0
            elif dx < 0: b[:, dx:] = 0
            if dy > 0: b[:dy, :] = 0
            elif dy < 0: b[dy:, :] = 0
        else:
            b = a
        Image.fromarray(b).save(os.path.join(salida, f))
        print('%-54s %-7s eje %8.2f,%8.2f   mueve %+3d,%+3d  %s'
              % (f, t, cx, cy, dx, dy, extra))
    print('\nescritas en ' + salida)
