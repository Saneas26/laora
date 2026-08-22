#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El triángulo de la O, de naranja a PLATA.

En las fotos del Cero Cero el logotipo de la esfera está en plata —con
su relieve y su luz— pero el triangulito de dentro de la O salió
NARANJA, y esa esfera es monocroma (Óscar, 22/08/2026). Aquí se repinta.

CÓMO, para que no se note:

1. NO SE DIBUJA NADA. Se conserva el modelado que ya tiene el triángulo
   —arriba está más claro que abajo— y solo se le quita el color: el
   brillo de cada píxel se estira del rango que tenía al del plata del
   propio logotipo de esa misma foto, medido al lado. Así el triángulo
   pesa lo mismo que las letras y no parece pegado.

2. LOS BORDES, CON MEZCLA SUAVE. La foto lleva antialiasing: alrededor
   del naranja hay una orla de píxeles medio naranjas. Con un umbral
   duro quedaría un halo de color. Se calcula cuánto tiene de naranja
   cada píxel (0 a 1) y se mezcla en esa proporción.

3. SOLO EN SU VENTANA. Se trabaja en un recuadro alrededor del
   triángulo, que en estas fotos cae siempre en el mismo sitio. Fuera
   de ahí hay agujas doradas e índices color crema que NO se tocan.

Uso:
    python3 herramientas/triangulo_a_plata.py 'assets/img/piezas/completas/LO-05-*.webp'
    python3 herramientas/triangulo_a_plata.py ... --prueba   # no escribe
"""
import glob, os, sys
import numpy as np
from PIL import Image

VENTANA = (928, 976, 724, 790)      # x0, x1, y0, y1 en la foto de 2000 px
                                    # (el triángulo cae entre 939-963 y 733-770 en las
                                    #  24 fotos; el margen sobra y no toca nada más)
LOGO = (820, 1120, 700, 830)        # de dónde se mide el plata de las letras


def plata_del_logo(a):
    """Percentiles de brillo del plata de las letras, en esta misma foto."""
    x0, x1, y0, y1 = LOGO
    z = a[y0:y1, x0:x1]
    lum = z.mean(axis=2)
    neutro = (z.max(axis=2) - z.min(axis=2)) < 18
    m = (lum > 140) & neutro
    if m.sum() < 200: return None
    return np.percentile(lum[m], [5, 95])


def repinta(ruta, prueba=False):
    im = Image.open(ruta).convert('RGB')
    if im.size != (2000, 2000):
        return '%s: no mide 2000 px (%dx%d), me lo salto' % (os.path.basename(ruta),) + im.size
    a = np.asarray(im).astype(float)
    ref = plata_del_logo(a)
    if ref is None:
        return '%s: no encuentro el plata del logotipo' % os.path.basename(ruta)

    x0, x1, y0, y1 = VENTANA
    z = a[y0:y1, x0:x1]
    r, g, b = z[:, :, 0], z[:, :, 1], z[:, :, 2]
    alfa = np.clip((r - b - 10) / 50.0, 0, 1)
    nucleo = alfa > 0.6
    if nucleo.sum() < 60:
        return '%s: no hay triángulo naranja' % os.path.basename(ruta)

    L = 0.299 * r + 0.587 * g + 0.114 * b
    lo, hi = np.percentile(L[nucleo], [5, 95])
    # el brillo del triángulo, estirado al del plata de las letras
    k = (ref[1] - ref[0]) / max(hi - lo, 1e-6)
    Lp = np.clip(ref[0] + (L - lo) * k, 0, 255)
    # el plata de la casa es neutro con una pizca de frío
    plata = np.stack([Lp, Lp, Lp * 0.995], axis=2)
    z2 = z * (1 - alfa[:, :, None]) + plata * alfa[:, :, None]
    a[y0:y1, x0:x1] = z2

    if not prueba:
        Image.fromarray(a.round().clip(0, 255).astype(np.uint8)).save(ruta, quality=92, method=6)
    return '%s: %d px repintados (naranja %.0f-%.0f → plata %.0f-%.0f)' % (
        os.path.basename(ruta), int(nucleo.sum()), lo, hi, ref[0], ref[1])


if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    prueba = '--prueba' in sys.argv
    rutas = []
    for a in args: rutas += sorted(glob.glob(a))
    if not rutas: sys.exit('no hay fotos que casen con ' + ' '.join(args))
    for r in rutas: print(repinta(r, prueba))
