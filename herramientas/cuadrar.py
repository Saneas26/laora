#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deja la esfera cuadrada en la caja, midiendo el resultado.

Calcular el centro de la caja por su contorno no basta: las asas
sobresalen, la corona sobresale, la correa tapa el borde arriba y abajo,
y el círculo que sale del ajuste se desvía entre diez y cuarenta píxeles
según la foto. Óscar lo vio en las cuatro de ante: la esfera cargada a
la derecha.

Así que no se calcula: se prueba y se corrige. Se monta, se mide el
anillo de metal que queda a cada lado de la esfera, y se mueve la
esfera la mitad de lo que difieran. Dos o tres vueltas y la diferencia
se queda en un par de píxeles, que ya no se ve.

Las medidas se toman donde el borde está limpio: a los lados, en filas
por encima y por debajo de la corona; arriba y abajo, en la columna del
centro, que es la única donde no hay asas.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def anillos(img, centro, r):
    """El metal entre la esfera y el borde, en los cuatro lados."""
    a = np.asarray(img.convert('RGB')).astype(float)
    lum = a.mean(axis=2)
    H, W, _ = a.shape
    cx, cy = centro
    fondo = np.median(np.concatenate([a[:40].reshape(-1, 3), a[-40:].reshape(-1, 3)]), axis=0)
    noF = np.abs(a - fondo).max(axis=2) > 16
    izq, der, arr, aba = [], [], [], []
    for f in (-0.42, -0.30, 0.30, 0.42):          # filas, lejos de la corona
        y = int(cy + f * r)
        xs = np.where(noF[y])[0]
        if len(xs) < 50:
            continue
        fila = lum[y]
        for lado, arranque, paso, donde in ((xs.min(), 10, 1, izq), (xs.max(), -10, -1, der)):
            x = lado + arranque
            while 0 < x < W - 30 and abs(x - cx) > 20:
                if fila[x] < 60 and all(fila[x + paso * k] < 85 for k in range(25)):
                    donde.append(abs(x - lado)); break
                x += paso
    for f in (-0.12, 0.0, 0.12):                  # columnas, sin asas
        x = int(cx + f * r)
        col = lum[:, x]
        for arriba in (True, False):
            # DESDE EL CENTRO HACIA FUERA, que es lo único fiable: hacia
            # dentro se topa uno con la correa, que llega hasta el borde
            # de la foto y no dice nada del borde de la caja.
            paso = -1 if arriba else 1
            y = int(cy + paso * r * 0.6)
            esfera = None
            while 0 < y < H - 30:
                if col[y] > 130 and all(col[y + paso * k] > 105 for k in range(20)):
                    esfera = y; break
                y += paso
            if esfera is None:
                continue
            y = esfera
            while 0 < y < H - 30:
                if col[y] < 70 and all(col[y + paso * k] < 95 for k in range(25)):
                    (arr if arriba else aba).append(abs(y - esfera)); break
                y += paso
    med = lambda v: sum(v) / len(v) if v else None
    return {'izq': med(izq), 'der': med(der), 'arriba': med(arr), 'abajo': med(aba)}


def pegar(caja, esfera, centro_esfera, r_esfera, destino, r, tapar=None, borde=2.0):
    cx, cy = destino
    a = np.asarray(caja.convert('RGB')).astype(float)
    if tapar is not None:
        a = tapar(a, (cx, cy), r)
    fondo = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    ecx, ecy, ecr = centro_esfera[0], centro_esfera[1], r_esfera
    z = esfera.convert('RGB').crop((int(ecx - ecr), int(ecy - ecr),
                                    int(ecx + ecr), int(ecy + ecr))).resize((2 * r, 2 * r), Image.LANCZOS)
    m = Image.new('L', (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(borde))
    fondo.paste(z, (int(cx - r), int(cy - r)), m)
    return fondo


def cuadrar(caja, esfera, centro_esfera, r_esfera, destino, r, tapar=None, vueltas=6):
    """Monta, mide y corrige, hasta que el anillo es igual por los cuatro lados."""
    cx, cy = destino
    for i in range(vueltas):
        img = pegar(caja, esfera, centro_esfera, r_esfera, (cx, cy), r, tapar)
        m = anillos(img, (cx, cy), r)
        if None in m.values():
            return img, m, (cx, cy)
        dx = (m['der'] - m['izq']) / 2
        dy = (m['abajo'] - m['arriba']) / 2
        if abs(dx) < 3 and abs(dy) < 3:
            return img, m, (cx, cy)
        cx += dx; cy += dy
    img = pegar(caja, esfera, centro_esfera, r_esfera, (cx, cy), r, tapar)
    return img, anillos(img, (cx, cy), r), (cx, cy)
