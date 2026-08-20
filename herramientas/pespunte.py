#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cambia el color del pespunte de una correa de piel.

El proveedor cose la misma correa con hilo claro o con hilo del tono de
la piel. Fotografiar las dos versiones de cada color son el doble de
fotos, y no hace falta: el hilo se aísla y se tiñe, conservando su
trenza, sus brillos y su relieve. No se dibuja ni un punto.

CÓMO SE ENCUENTRA EL HILO. En una correa negra con hilo claro es
sencillo, pero no tanto como parece: el núcleo del hilo es casi blanco
puro y ahí se pierde la calidez que lo distingue del brillo del cuero.
Por eso se hace en dos tiempos —lo que ya usamos con las agujas—:
primero la semilla, lo claro Y cálido, que es hilo seguro; después se
crece esa semilla hacia todo lo que esté claro y pegado a ella. Así el
núcleo entra y los reflejos sueltos del cuero, no.

EL TEÑIDO conserva la luz de cada píxel: se le cambia el tono y se le
deja su claro y su oscuro, que es lo que hace que siga pareciendo hilo
y no una raya pintada.

Uso:
    python3 herramientas/pespunte.py foto.png salida.png --a tono
    python3 herramientas/pespunte.py foto.png salida.png --a blanco
"""
import argparse
from collections import deque
import numpy as np
from PIL import Image, ImageFilter


def correa(a, centro, radio, cierre=9):
    """Lo que hay fuera del reloj y no es fondo: la correa.

    Con el cuidado de TAPAR LOS AGUJEROS. El fondo del estudio es gris
    claro y el hilo crema también, así que los puntos más luminosos de la
    costura se colaban como si fueran fondo: quedaban fuera de la correa,
    fuera de la máscara y sin teñir, y la costura acababa con chispas
    blancas por encima del color nuevo. Un cierre morfológico los recupera
    sin ensanchar la correa por fuera.
    """
    H, W, _ = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    fuera = ((xx - centro[0]) ** 2 + (yy - centro[1]) ** 2) > radio ** 2
    fondo = np.median(np.concatenate([a[:60].reshape(-1, 3), a[-60:].reshape(-1, 3)]), axis=0)
    esFondo = np.abs(a - fondo).max(axis=2) <= 18
    # el fondo DE VERDAD es el que se toca desde el borde de la foto; lo
    # que parece fondo y está encerrado dentro de la correa es hilo
    im = Image.fromarray((esFondo * 255).astype(np.uint8))
    im = im.filter(ImageFilter.MinFilter(3))          # despegar por los cantos
    libre = np.asarray(im).astype(bool)
    alcanzado = np.zeros_like(libre)
    q = deque()
    H2, W2 = libre.shape
    for x in range(W2):
        for y in (0, H2 - 1):
            if libre[y, x] and not alcanzado[y, x]:
                alcanzado[y, x] = True; q.append((y, x))
    for y in range(H2):
        for x in (0, W2 - 1):
            if libre[y, x] and not alcanzado[y, x]:
                alcanzado[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H2 and 0 <= nx < W2 and libre[ny, nx] and not alcanzado[ny, nx]:
                alcanzado[ny, nx] = True; q.append((ny, nx))
    im = Image.fromarray(((~alcanzado) * 255).astype(np.uint8))
    im = im.filter(ImageFilter.MaxFilter(cierre)).filter(ImageFilter.MinFilter(cierre))
    return fuera & np.asarray(im).astype(bool)


def crecer(semilla, permitido, vueltas=26):
    """Extiende la semilla por lo permitido, un píxel cada vuelta."""
    m = semilla.copy()
    for _ in range(vueltas):
        d = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.MaxFilter(3))).astype(bool)
        n = d & permitido
        if n.sum() == m.sum():
            break
        m = n
    return m


def hilo_claro(a, zona, luz=125, calor=8, suelo=70):
    """El pespunte claro sobre una correa oscura."""
    lum = a.mean(axis=2)
    semilla = zona & (lum > luz) & (a[:, :, 0] > a[:, :, 2] + calor)
    return crecer(semilla, zona & (lum > suelo))


def tenir(a, m, color, mezcla=0.96, contraste=0.55):
    """Le cambia el tono al hilo dejándole su luz.

    La luz se COMPRIME, no se copia tal cual: un hilo claro tiene puntos
    casi blancos, y si se conserva ese rango entero al pasarlo a negro
    quedan chispas blancas por toda la costura. Se guarda el relieve
    —dónde hay más luz y dónde menos— pero en la horquilla del color
    nuevo.
    """
    lum = a.mean(axis=2)
    ref = np.percentile(lum[m], 70) if m.any() else 1
    rel = np.clip(lum / max(ref, 1), 0, 1.6)
    rel = (1 - contraste) + contraste * rel
    base = np.array(color, dtype=float)
    tinte = np.clip(base[None, None, :] * rel[:, :, None], 0, 255)
    suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 255 * mezcla
    return a * (1 - suave[:, :, None]) + tinte * suave[:, :, None]


def tono_de_la_piel(a, zona, m):
    """El color medio de la piel de al lado, para el hilo «a tono»."""
    cerca = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.MaxFilter(21))).astype(bool) & zona & ~m
    return a[cerca].mean(axis=0) if cerca.any() else np.array([30., 30., 30.])


def injertar(a, b, m, desvanecido=1.0):
    """Trae el hilo de otra foto de la MISMA correa.

    Sobre una piel marrón o verde el hilo a tono no se puede aislar: es
    del mismo color que la piel y del mismo brillo, y todo lo que se
    intente coge medio cuero por el camino. Pero la costura clara de la
    correa negra está en el mismo sitio —las dos fotos encajan sin mover
    un píxel, comprobado por correlación— y es opaca, así que se trae
    entera y tapa la que había debajo.
    """
    s = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(desvanecido))).astype(float) / 255
    return a * (1 - s[:, :, None]) + b * s[:, :, None]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('foto'); p.add_argument('salida')
    p.add_argument('--a', choices=['tono', 'blanco'], required=True)
    p.add_argument('--de', help='foto de la que traer el hilo claro (para --a blanco)')
    p.add_argument('--centro', default='1936,1984'); p.add_argument('--radio', type=float, default=1150)
    p.add_argument('--luz', type=float, default=125)
    p.add_argument('--suelo', type=float, default=70)
    p.add_argument('--contraste', type=float, default=0.55)
    a_ = p.parse_args()
    img = Image.open(a_.foto).convert('RGB')
    a = np.asarray(img).astype(float)
    cx, cy = (float(v) for v in a_.centro.split(','))
    zona = correa(a, (cx, cy), a_.radio)
    if a_.a == 'blanco' and a_.de:
        b = np.asarray(Image.open(a_.de).convert('RGB')).astype(float)
        m = hilo_claro(b, correa(b, (cx, cy), a_.radio), a_.luz, suelo=a_.suelo)
        out = injertar(a, b, m)
        print(a_.salida, '· hilo injertado de %s: %d px' % (a_.de.split('/')[-1], m.sum()))
    else:
        m = hilo_claro(a, zona, a_.luz, suelo=a_.suelo)
        color = tono_de_la_piel(a, zona, m) if a_.a == 'tono' else np.array([236., 232., 222.])
        out = tenir(a, m, color, contraste=a_.contraste)
        print(a_.salida, '· hilo: %d px · color %s' % (m.sum(), np.round(color).astype(int)))
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a_.salida)
