#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sienta las agujas pequeñas de una capa sobre los contadores de su esfera.

EL PROBLEMA (Óscar, 28/08/2026): «las agujas pequeñas azules no cuadran
con la esfera». Y no cuadran: sobre la esfera blanca, las tres agujas de
los contadores se quedan unos 30 px por encima de su sitio, y por debajo
del hub asoma el resalte claro que la esfera lleva pintado en el centro
de cada contador.

DE DÓNDE VIENE. La capa de agujas trae DENTRO las tres agujas pequeñas,
así que da por hecho que todas las esferas tienen los contadores en el
mismo sitio. No lo tienen: son imágenes generadas una a una y cada una
se desvía por su cuenta. Medido, el contador de la izquierda está en

    esfera negra ....... 1488, 1885   (y ahí las agujas caen clavadas)
    esfera blanca ...... 1467, 1904   (20 px a la izquierda y 20 abajo)

Por eso el par negro+plata se ve bien y el blanco+azules se ve torcido:
las agujas se dibujaron para la negra.

LO QUE HACE ESTE PROGRAMA. Mide las dos cosas y mueve cada aguja pequeña
por separado —son tres trozos sueltos de la imagen, no se tocan entre
ellas ni tocan a las agujas grandes—:

  · LA DIANA es el resalte del centro del contador, y se busca de DOS
    MANERAS porque ninguna vale para todas las esferas:

      1) POR INUNDACIÓN desde una semilla, mientras el color se parezca.
         Va bien cuando el resalte destaca sobre su contador —el blanco
         sobre el azul de la esfera blanca—: sale un disco de unos 80 px
         que no se mueve aunque se cambie la tolerancia.
      2) POR DIFERENCIA CON EL COLOR DE ALREDEDOR, cuando la inundación
         se escapa. En la esfera de oro rosa el contador es del mismo
         blanco que la esfera, así que la inundación se lleva el dial
         entero; ahí se coge la mancha pequeña más cercana al centro que
         se salga de la mediana de su alrededor.

    Y la comprobación es la misma para las dos: los contadores de los
    lados tienen que salir simétricos respecto al eje. Si no, el programa
    se planta en vez de mover nada.

  · EL HUB de la aguja es la tapa redonda de su base. Se ajusta un
    círculo al borde de DEBAJO de la fila más ancha: por arriba la aguja
    se le pega al hub y ensucia el ajuste, por debajo el borde está
    limpio. Salen ochenta y pico puntos con 0,3 px de error.

SE MUEVE EN PÍXELES ENTEROS y sólo el trozo de cada aguja pequeña; las
agujas grandes y su hub central no se tocan, que ésos ya están cuadrados
con el eje por alinear_capas_lunar.py.

⚠️ EL TROZO SE COGE POR ALFA > 8, NO > 128. La primera versión cogía sólo
lo opaco y dejaba clavados en el sitio viejo los píxeles del borde
suavizado: quedaba el fantasma de la aguja anterior y un escalón donde se
había cortado. El hub sí se mide sobre lo opaco, que ahí el borde blando
sólo ablandaría el ajuste.

⚠️ EL ARREGLO ES POR PAREJA. La capa que sale de aquí vale para LA
ESFERA CON LA QUE SE CUADRÓ y para ninguna otra. Hoy da igual, porque
las agujas azules sólo salen con la esfera blanca, pero en cuanto un
juego de agujas sirva a dos esferas con los contadores en sitios
distintos habrá que pedir las esferas con los contadores en su sitio.

Uso:
    python3 herramientas/cuadrar_agujas_pequenas.py \
        capas/07-agujas-azules-...-4096.png \
        capas/05-esfera-blanca-...-4096.png \
        salida/07-agujas-azules-...-4096.png
"""
import argparse
import sys
from collections import deque

import numpy as np
from PIL import Image

# El eje del montaje, el que fija el bisel. Sirve para comprobar que los
# contadores de los lados salen simétricos.
EJE_X = 2047.5
# Dónde buscar cada contador. No hace falta afinar: la inundación encuentra
# el resalte desde cualquier punto de dentro.
SEMILLAS = {'izquierdo': (1470, 1900), 'derecho': (2630, 1900),
            'inferior': (2050, 2425)}


def trozos(m, minimo, maximo):
    """Los trozos sueltos de la máscara, del tamaño que se pida."""
    h, w = m.shape
    visto = np.zeros_like(m, bool)
    fuera = []
    for y0, x0 in zip(*np.where(m)):
        if visto[y0, x0]:
            continue
        cola = deque([(y0, x0)])
        visto[y0, x0] = True
        pts = []
        while cola:
            y, x = cola.popleft()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not visto[ny, nx]:
                    visto[ny, nx] = True
                    cola.append((ny, nx))
        if minimo <= len(pts) <= maximo:
            fuera.append(np.array(pts))
    return fuera


def _circulo(p):
    x, y = p[:, 0].astype(float), p[:, 1].astype(float)
    M = np.c_[2 * x, 2 * y, np.ones(len(p))]
    s, _, _, _ = np.linalg.lstsq(M, x * x + y * y, rcond=None)
    return s[0], s[1], np.sqrt(s[2] + s[0] ** 2 + s[1] ** 2)


def hub(trozo):
    """El centro de la tapa redonda, por el borde de debajo de la fila más ancha."""
    ys, xs = trozo[:, 0], trozo[:, 1]
    filas = {}
    for y in range(ys.min(), ys.max() + 1):
        v = xs[ys == y]
        if len(v):
            filas[y] = (v.min(), v.max())
    ancha = max(filas, key=lambda y: filas[y][1] - filas[y][0])
    p = []
    for y in range(ancha, ys.max() + 1):
        a = filas.get(y)
        if a and a[1] - a[0] > 3:
            p += [(a[0], y), (a[1], y)]
    p = np.array(p, float)
    err = 0.0
    for _ in range(3):
        X, Y, R = _circulo(p)
        d = np.abs(np.hypot(p[:, 0] - X, p[:, 1] - Y) - R)
        err = d.mean()
        p = p[d < max(1.5, 2.2 * d.std())]
    return X, Y, R, err


def por_diferencia(rgb, semilla, radio=170, dif=28):
    """La mancha pequeña del centro que se sale del color de alrededor."""
    cx, cy = int(semilla[0]), int(semilla[1])
    x0, y0 = cx - radio, cy - radio
    sub = rgb[y0:y0 + 2 * radio, x0:x0 + 2 * radio].astype(int)
    m = np.abs(sub - np.median(sub.reshape(-1, 3), axis=0)).max(axis=2) > dif
    h, w = m.shape
    visto = np.zeros_like(m, bool)
    mejor, cerca = None, 1e9
    for yy, xx in zip(*np.where(m)):
        if visto[yy, xx]:
            continue
        cola = deque([(yy, xx)])
        visto[yy, xx] = True
        pts = []
        while cola:
            y, x = cola.popleft()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not visto[ny, nx]:
                    visto[ny, nx] = True
                    cola.append((ny, nx))
        p = np.array(pts)
        ys, xs = p[:, 0], p[:, 1]
        ancho = max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
        if not 40 <= ancho <= 160:
            continue
        c = ((xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0)
        d = (c[0] - radio) ** 2 + (c[1] - radio) ** 2
        if d < cerca:
            cerca, mejor = d, (c[0] + x0, c[1] + y0, ancho)
    return mejor


def diana(rgb, alfa, semilla, tol=60, radio=460):
    """El resalte claro del centro del contador: se inunda por color."""
    cx, cy = int(semilla[0]), int(semilla[1])
    y0, x0 = cy - radio, cx - radio
    sub = rgb[y0:cy + radio, x0:cx + radio].astype(int)
    a = alfa[y0:cy + radio, x0:cx + radio]
    ref = sub[radio - 20:radio + 20, radio - 20:radio + 20].reshape(-1, 3).mean(axis=0)
    m = (np.abs(sub - ref).max(axis=2) < tol) & a
    if not m[radio, radio]:
        return None
    h, w = m.shape
    visto = np.zeros_like(m, bool)
    cola = deque([(radio, radio)])
    visto[radio, radio] = True
    while cola:
        y, x = cola.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not visto[ny, nx]:
                visto[ny, nx] = True
                cola.append((ny, nx))
    ys, xs = np.where(visto)
    ancho = xs.max() - xs.min() + 1
    # Si la inundación se ha ido por la esfera entera, esto no es un resalte.
    if not 40 <= ancho <= 200:
        return None
    return (xs.min() + xs.max()) / 2.0 + x0, (ys.min() + ys.max()) / 2.0 + y0, ancho


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('agujas')
    ap.add_argument('esfera')
    ap.add_argument('salida')
    # CUÁNTO SE LE PERDONA AL CONTROL DE SIMETRÍA. Los contadores de los
    # lados deberían caer simétricos respecto al eje; si no, la medida suele
    # estar mal —cuando la inundación se escapa, se va cientos de píxeles—.
    # Pero la esfera panda los tiene DE VERDAD 8 px descentrados, así que con
    # 6 el programa se plantaba en una esfera buena. A 10 sigue cazando los
    # errores gordos, que son de otro orden.
    ap.add_argument('--simetria', type=float, default=10.0)
    o = ap.parse_args()

    e = np.asarray(Image.open(o.esfera).convert('RGBA'))
    dianas = {}
    for nom, s in SEMILLAS.items():
        d = diana(e[..., :3], e[..., 3] > 128, s)
        como = 'inundando'
        if d is None:
            d = por_diferencia(e[..., :3], s)
            como = 'por diferencia'
        if d is None:
            sys.exit('no encuentro el resalte del contador %s en %s' % (nom, o.esfera))
        dianas[nom] = (d[0], d[1])
        print('contador %-10s %8.2f,%8.2f  (resalte de %d px, %s)'
              % (nom, d[0], d[1], d[2], como))

    # LA COMPROBACIÓN: los dos contadores de los lados tienen que salir
    # simétricos respecto al eje. Si no, la medida está mal y no se mueve nada.
    medio = (dianas['izquierdo'][0] + dianas['derecho'][0]) / 2.0
    print('punto medio de los dos laterales: %.2f  (el eje está en %.1f, %.2f de diferencia)'
          % (medio, EJE_X, abs(medio - EJE_X)))
    if abs(medio - EJE_X) > o.simetria:
        sys.exit('los contadores no salen simétricos: la medida no es de fiar')

    a = np.asarray(Image.open(o.agujas).convert('RGBA'))
    alfa = a[..., 3]
    fuera = a.copy()
    movidas = 0
    for t in trozos(alfa > 8, 300, 30000):
        opaco = t[alfa[t[:, 0], t[:, 1]] > 128]
        if len(opaco) < 200:
            continue
        X, Y, R, err = hub(opaco)
        nom = min(dianas, key=lambda k: (dianas[k][0] - X) ** 2 + (dianas[k][1] - Y) ** 2)
        dx = int(round(dianas[nom][0] - X))
        dy = int(round(dianas[nom][1] - Y))
        print('aguja %-10s hub %8.2f,%8.2f (R %.1f, error %.2f px)  mueve %+3d,%+3d'
              % (nom, X, Y, R, err, dx, dy))
        if not (dx or dy):
            continue
        ys, xs = t[:, 0], t[:, 1]
        trozo = a[ys, xs].copy()
        fuera[ys, xs] = 0                      # se borra de donde estaba
        fuera[ys + dy, xs + dx] = trozo        # y se pega donde toca
        movidas += 1

    Image.fromarray(fuera).save(o.salida)
    print('\n%d agujas pequeñas movidas · escrita en %s' % (movidas, o.salida))
