#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El triángulo de la O, de naranja o amarillo a PLATA.

En la esfera, el logotipo de laOra va en PLATA monocroma —lo dice
`herramientas/logotipo_esfera.py` desde el 19/08— pero en varias tandas
de fotos el triangulito de dentro de la O salió de color: naranja en el
Cero Cero y amarillo en el Trinchera y el Bitácora. Óscar, 22/08/2026:
«es monocromo y tiene que ser plata».

CÓMO, para que no se note:

1. NO SE DIBUJA NADA. Se conserva el modelado que ya tiene el triángulo
   —arriba está más claro que abajo— y solo se le quita el color: el
   brillo de cada píxel se estira del rango que tenía al del plata del
   propio logotipo de esa misma foto, medido a su alrededor. Así el
   triángulo pesa lo mismo que las letras y no parece pegado.

2. LOS BORDES, CON MEZCLA SUAVE. La foto lleva antialiasing: alrededor
   del color hay una orla de píxeles a medias. Con un umbral duro
   quedaría un halo. Se calcula cuánto tiene de cálido cada píxel (0 a
   1) y se mezcla en esa proporción.

3. EL TRIÁNGULO SE BUSCA, NO SE SUPONE. Se mira la banda del logotipo
   —el centro alto de la esfera— y se queda con la mancha cálida que
   tiene forma y tamaño de triangulito: ancho de entre el 0,55 % y el
   1,35 % de la foto, casi tan alta como ancha y maciza. Ese filtro es
   el que separa el triángulo del LUME CREMA de agujas y numerales, que
   también es cálido y que NO hay que tocar: sin él, la serie Murph del
   Trinchera salía marcada de arriba abajo.

Uso:
    python3 herramientas/triangulo_a_plata.py 'assets/img/piezas/completas/LO-04-*.webp'
    python3 herramientas/triangulo_a_plata.py ... --prueba   # dice qué haría
"""
import glob, os, sys
from collections import deque

import numpy as np
from PIL import Image

UMBRAL = 35          # r − b a partir del cual un píxel se considera cálido
REL_MIN, REL_MAX = 0.0055, 0.0135     # ancho del triángulo, en tanto por uno de la foto


def _componentes(m, minimo):
    H, W = m.shape
    visto = np.zeros_like(m)
    out = []
    for y0, x0 in zip(*np.where(m)):
        if visto[y0, x0]: continue
        q = deque([(y0, x0)]); visto[y0, x0] = True; xs = []; ys = []
        while q:
            y, x = q.popleft(); xs.append(x); ys.append(y)
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not visto[yy, xx]:
                    visto[yy, xx] = True; q.append((yy, xx))
        if len(xs) >= minimo:
            out.append((len(xs), min(xs), max(xs), min(ys), max(ys)))
    return out


def busca_triangulo(a):
    """(x0, x1, y0, y1) del triangulito cálido de la O, o None."""
    H, W, _ = a.shape
    Y0, Y1 = int(H * 0.28), int(H * 0.52)
    X0, X1 = int(W * 0.36), int(W * 0.64)
    z = a[Y0:Y1, X0:X1]
    m = ((z[:, :, 0] - z[:, :, 2] > UMBRAL) & (z[:, :, 1] - z[:, :, 2] > 12)
         & (z[:, :, 0] > 100))
    cand = []
    for n, x0, x1, y0, y1 in _componentes(m, max(12, int(W * W * 2e-6))):
        w, h = x1 - x0 + 1, y1 - y0 + 1
        if not (REL_MIN <= w / W <= REL_MAX): continue
        if not (0.55 <= w / h <= 1.35): continue
        if n < 0.35 * w * h: continue                  # macizo, ni aro ni raya
        cand.append((abs((x0 + x1) / 2 + X0 - W / 2), x0 + X0, x1 + X0, y0 + Y0, y1 + Y0))
    if not cand: return None
    cand.sort()
    return cand[0][1:]


def plata_alrededor(a, caja):
    """Percentiles de brillo del plata de las letras, junto al triángulo."""
    x0, x1, y0, y1 = caja
    w, h = x1 - x0 + 1, y1 - y0 + 1
    z = a[max(0, y0 - h): y1 + h * 2, max(0, x0 - w * 5): x1 + w * 5]
    lum = z.mean(axis=2)
    neutro = (z.max(axis=2) - z.min(axis=2)) < 18
    m = (lum > 140) & neutro
    if m.sum() < 120: return None
    return np.percentile(lum[m], [5, 95])


def repinta(ruta, prueba=False):
    im = Image.open(ruta)
    formato = im.format
    a = np.asarray(im.convert('RGB')).astype(float)
    caja = busca_triangulo(a.astype(int))
    if caja is None:
        return '%-42s sin triángulo cálido' % os.path.basename(ruta)
    ref = plata_alrededor(a, caja)
    if ref is None:
        return '%-42s no encuentro el plata del logotipo' % os.path.basename(ruta)

    x0, x1, y0, y1 = caja
    w, h = x1 - x0 + 1, y1 - y0 + 1
    X0, X1 = max(0, x0 - w // 2), x1 + w // 2 + 1
    Y0, Y1 = max(0, y0 - h // 2), y1 + h // 2 + 1
    z = a[Y0:Y1, X0:X1]
    r, g, b = z[:, :, 0], z[:, :, 1], z[:, :, 2]
    alfa = np.clip((r - b - 10) / 50.0, 0, 1)
    nucleo = alfa > 0.6
    if nucleo.sum() < 20:
        return '%-42s el triángulo se queda en nada' % os.path.basename(ruta)

    L = 0.299 * r + 0.587 * g + 0.114 * b
    lo, hi = np.percentile(L[nucleo], [5, 95])
    k = (ref[1] - ref[0]) / max(hi - lo, 1e-6)
    Lp = np.clip(ref[0] + (L - lo) * k, 0, 255)
    plata = np.stack([Lp, Lp, Lp * 0.995], axis=2)
    a[Y0:Y1, X0:X1] = z * (1 - alfa[:, :, None]) + plata * alfa[:, :, None]

    if not prueba:
        salida = Image.fromarray(a.round().clip(0, 255).astype(np.uint8))
        if formato == 'WEBP': salida.save(ruta, quality=92, method=6)
        elif formato == 'AVIF': salida.save(ruta, quality=68)
        else: salida.save(ruta)
    return '%-42s %3d px · %dx%d en (%d,%d) · %.0f-%.0f → %.0f-%.0f' % (
        os.path.basename(ruta), int(nucleo.sum()), w, h, x0, y0, lo, hi, ref[0], ref[1])


if __name__ == '__main__':
    prueba = '--prueba' in sys.argv
    rutas = []
    for a in [x for x in sys.argv[1:] if not x.startswith('--')]:
        rutas += sorted(glob.glob(a))
    if not rutas: sys.exit('no hay fotos que casen')
    for r in rutas: print(repinta(r, prueba))
