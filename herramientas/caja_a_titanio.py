#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pasa a titanio una caja fotografiada en acero.

Es el mismo reloj y la misma foto: lo que cambia es el metal. El acero
inoxidable es un gris claro con reflejos muy vivos —el cepillado brilla
casi a blanco— y el titanio es más apagado, más oscuro y ligeramente
más cálido, con las luces mucho menos disparadas. Eso se puede hacer
sobre la foto sin inventarse nada: se baja la claridad, se COMPRIMEN
LOS REFLEJOS —que es lo que de verdad distingue un metal del otro— y se
le da el punto de calor.

Lo delicado es no tocar nada más. La caja se separa así:

- LA SILUETA, rellenando el fondo desde el borde de la foto. El fondo
  del estudio es gris claro y sin color, exactamente como el metal, así
  que por color no hay manera.
- FUERA DE LA ESFERA, que va aparte y no cambia.
- SIN COLOR Y CLARO, que deja fuera la correa: la de piel de color por
  el tono y la negra por lo oscura.

Uso:
    python3 herramientas/caja_a_titanio.py acero.png titanio.png
"""
import argparse
from collections import deque
import numpy as np
from PIL import Image, ImageFilter


def silueta(a, umbral=18, despegue=3, k=4):
    """Todo lo que no es fondo, con los huecos interiores dentro.

    El relleno se hace a un cuarto de tamaño: la silueta de un reloj es
    una forma grande y no pierde nada, y en cambio recorrer dieciséis
    millones de píxeles en Python cuesta más de medio minuto por foto.
    """
    fondo = np.median(np.concatenate([a[:60].reshape(-1, 3), a[-60:].reshape(-1, 3)]), axis=0)
    libre = np.abs(a - fondo).max(axis=2) <= umbral
    grande = libre.shape
    # el despegue va ANTES de reducir: a un cuarto de tamaño, un filtro de
    # tres píxeles se come doce del original, y la caja se quedaba con una
    # franja del canto fuera de la silueta, brillando a acero.
    libre = np.asarray(Image.fromarray((libre * 255).astype(np.uint8))
                       .filter(ImageFilter.MinFilter(despegue))
                       .resize((grande[1] // k, grande[0] // k), Image.NEAREST)).astype(bool)
    H, W = libre.shape
    visto = np.zeros_like(libre); q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if libre[y, x] and not visto[y, x]:
                visto[y, x] = True; q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if libre[y, x] and not visto[y, x]:
                visto[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and libre[ny, nx] and not visto[ny, nx]:
                visto[ny, nx] = True; q.append((ny, nx))
    # de vuelta al tamaño real por interpolación, no a saltos: con NEAREST
    # el canto de la caja sale dentado a escalones de cuatro píxeles y se
    # ve a simple vista en el perfil.
    vuelta = np.asarray(Image.fromarray((visto * 255).astype(np.uint8))
                        .resize((grande[1], grande[0]), Image.BILINEAR)).astype(float)
    return vuelta < 128


def metal(a, centro, resfera, holgura=1.03, sat_max=0.16, luz_min=95):
    H, W, _ = a.shape
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    lum = a.mean(axis=2)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - centro[0], yy - centro[1])
    sil = silueta(a)
    m = sil & (r > resfera * holgura) & (sat < sat_max) & (lum > luz_min)

    # SOLO LA CAJA, NO LA CORREA. «Metal» por color no basta: el pespunte
    # claro y los brillos del cuero son igual de claros y de grises, y se
    # pintaban de titanio con ella (Óscar, 20/08/2026). La caja es lo que
    # está PEGADO al bisel: se siembra en el anillo que rodea la esfera y
    # se crece por lo metálico. El pespunte es una isla dentro del cuero y
    # no llega, porque para llegar tendría que cruzar el hueco oscuro por
    # donde entra la correa.
    m = pegado_al_bisel(m, centro, resfera, r)

    # EL FILO DE LA CAJA es un reflejo casi blanco de dos o tres píxeles,
    # y si se queda fuera el perfil sigue brillando a acero por el canto.
    # Se engorda la máscara y se recorta con la silueta, para no salirse
    # al fondo, que también es gris claro y se mancharía.
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                   .filter(ImageFilter.MaxFilter(7))).astype(bool) & sil
    return m


def pegado_al_bisel(m, centro, resfera, r, k=4, semilla=1.12):
    """De todo lo metálico, lo que forma un cuerpo con el bisel."""
    grande = m.shape
    ch = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                    .resize((grande[1] // k, grande[0] // k), Image.NEAREST)).astype(bool)
    rr = np.asarray(Image.fromarray(np.clip(r / 16, 0, 255).astype(np.uint8))
                    .resize((grande[1] // k, grande[0] // k), Image.NEAREST)).astype(float) * 16
    H, W = ch.shape
    visto = np.zeros_like(ch); q = deque()
    arranque = ch & (rr < resfera * semilla)
    for y, x in zip(*np.where(arranque)):
        visto[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and ch[ny, nx] and not visto[ny, nx]:
                visto[ny, nx] = True; q.append((ny, nx))
    vuelta = np.asarray(Image.fromarray((visto * 255).astype(np.uint8))
                        .resize((grande[1], grande[0]), Image.BILINEAR)).astype(float)
    return m & (vuelta > 96)


def a_titanio(a, m, oscuro=0.80, reflejos=0.62, calor=0.030, borde=2.4):
    """Menos claro, con los reflejos recogidos y un punto de calor."""
    lum = a.mean(axis=2)
    # la curva: por debajo del gris medio baja poco, y cuanto más brilla
    # más se recoge. Es lo que hace que el metal deje de parecer espejo.
    v = lum / 255.0
    nueva = oscuro * v - (oscuro - reflejos) * v ** 3
    factor = np.where(lum > 1, nueva * 255 / np.maximum(lum, 1), 1)
    out = a * factor[:, :, None]
    # el titanio tira a cálido: se le sube el rojo y se le baja el azul
    gris = out.mean(axis=2)
    out[:, :, 0] += gris * calor
    out[:, :, 2] -= gris * calor
    s = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(borde))).astype(float) / 255
    return a * (1 - s[:, :, None]) + np.clip(out, 0, 255) * s[:, :, None]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('foto'); p.add_argument('salida')
    p.add_argument('--centro', default='1936,1984')
    p.add_argument('--resfera', type=float, default=812)
    p.add_argument('--oscuro', type=float, default=0.80)
    p.add_argument('--reflejos', type=float, default=0.62)
    p.add_argument('--calor', type=float, default=0.030)
    a_ = p.parse_args()
    a = np.asarray(Image.open(a_.foto).convert('RGB')).astype(float)
    cx, cy = (float(v) for v in a_.centro.split(','))
    m = metal(a, (cx, cy), a_.resfera)
    out = a_titanio(a, m, a_.oscuro, a_.reflejos, a_.calor)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a_.salida)
    print(a_.salida, '· metal: %d px' % m.sum())
