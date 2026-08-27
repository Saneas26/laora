#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pinta de azul la horaria y el minutero de una foto del Lunar.

EL PROBLEMA. Las agujas no se pueden aislar por color: son del mismo
acero pulido que los indices, y su cuerpo mide LO MISMO que la esfera
(a 700 px del centro la esfera da 223-226 y la aguja 170-225). No hay
umbral que las separe.

LO QUE SI SE PUEDE. Son batones rectos que salen del centro. Se gira la
foto hasta poner la aguja horizontal y entonces sus dos biseles
brillantes -lo unico que pasa de 238- forman dos rectas. Se ajusta una
recta a cada riel, se rellena entre ellas y se gira la mascara de
vuelta. La mascara sale con el borde suave del propio giro, que es
justo el difuminado que hace falta.

EL COLOR sale de la foto, no de la imaginacion: el azul del bisel y de
los contadores mide RGB(27, 47, 78). Se toma esa direccion de color y
se le monta encima la luz que tenia la aguja, comprimida con una
rodilla para que el pulido siga brillando. Es el mismo metodo que
titanio_del_par.py: una curva luz -> color aprendida de la propia foto.

Uso:
    python3 herramientas/agujas_azules.py entrada.png salida.png
"""
import argparse
import numpy as np
from PIL import Image

# los dos batones del Lunar en la foto de esfera blanca y bisel azul:
# angulo en grados, primera y ultima columna utiles, y donde acaba la punta
AGUJAS = [
    dict(nombre='minutero', ang=39.6, col0=280, col1=780, punta=828, hub=100, hombro=True),
    dict(nombre='horaria',  ang=146.0, col0=180, col1=540, punta=592, hub=100, hombro=True),
]
CENTRO = (2040, 1870)
FONDO = 247.0


def gira(im, ang, centro):
    return im.rotate(-ang, center=centro, resample=Image.BICUBIC)


def rieles(L, cx, cy, col0, col1, alto=60, bajo=30, umbral=238):
    """Las dos rectas que dibujan los biseles brillantes del baton.

    Dos vueltas: la primera con la ventana ancha, la segunda ya pegada a
    la recta que salio. Sin eso se cuelan el otro baton, el hub y los
    indices, y el ajuste se va treinta pixeles.
    """
    cols, arr, aba = [], [], []
    for col in range(col0, col1 + 1, 4):
        x = cx - 60 + col
        ys = np.where(L[cy - alto:cy + bajo, x] > umbral)[0]
        if len(ys) < 2:
            continue
        cols.append(col); arr.append(ys.min() - alto); aba.append(ys.max() - alto)
    cols = np.array(cols, float)
    arr = np.array(arr, float); aba = np.array(aba, float)

    def limpia(cols, ys):
        p = np.polyfit(cols, ys, 1)
        for _ in range(6):
            d = np.abs(np.polyval(p, cols) - ys)
            ok = d <= max(4.0, np.median(d) * 3)
            if ok.sum() < 8 or ok.all():
                break
            cols, ys = cols[ok], ys[ok]
            p = np.polyfit(cols, ys, 1)
        return p, np.abs(np.polyval(p, cols) - ys).max(), len(cols)

    pa, ra, na = limpia(cols, arr)
    pb, rb, nb = limpia(cols, aba)
    return pa, pb, ra, rb, min(na, nb)


def hombro(L, cx, cy, pa, hub, col0, margen=40, umbral=238):
    """Cerca del eje el baton se ensancha: se lee su borde de verdad.

    Las rectas se ajustan lejos del centro, donde el baton tiene los
    lados paralelos. En los ultimos 150 px antes del eje sube una faceta
    que las rectas se dejan fuera, y queda una tira de acero encima del
    azul. Se busca el brillo mas alto dentro de una franja pegada a la
    recta -no mas de `margen`, para que no entre la otra aguja- y se
    toma lo que este mas arriba de los dos.
    """
    extra = {}
    for col in range(hub, col0 + 1):
        x = cx - 60 + col
        base = int(round(np.polyval(pa, col)))
        y0 = cy + base - margen; y1 = cy + base + 10
        ys = np.where(L[y0:y1, x] > umbral)[0]
        extra[col] = (y0 - cy + ys.min()) if len(ys) else base
    # se suaviza para que el borde no vaya a saltos
    cols = sorted(extra)
    vals = np.array([extra[c] for c in cols], float)
    k = 15
    sua = np.convolve(np.pad(vals, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'same')[k:-k]
    return {c: v for c, v in zip(cols, sua)}


def mascara(forma, cx, cy, pa, pb, hub, punta, col1, extra=None):
    """Relleno entre las dos rectas, con la punta en pico."""
    m = np.zeros(forma, np.float32)
    for col in range(hub, punta + 1):
        x = cx - 60 + col
        a = np.polyval(pa, col); b = np.polyval(pb, col)
        if extra is not None and col in extra:
            a = min(a, extra[col])
        if col > col1:                       # la punta se cierra en pico
            k = (col - col1) / float(punta - col1)
            med = (a + b) / 2.0
            a = med + (a - med) * (1 - k); b = med + (b - med) * (1 - k)
        y0 = int(round(cy + a)); y1 = int(round(cy + b))
        if y1 > y0:
            m[y0:y1 + 1, x] = 1.0
    return m


def azulea(rgb, peso, tono, rodilla=120.0, techo=115.0, brillo=243.0, dureza=3.0):
    """La luz de la aguja, montada sobre el azul medido en la foto."""
    L = rgb.mean(2)
    t = np.clip((L - rodilla) / (255.0 - rodilla), 0, 1)
    Lt = 40.0 + (t ** dureza) * (techo - 40.0)
    nueva = tono[None, None, :] * Lt[:, :, None]
    # el destello del pulido no se tiñe del todo, como no lo hace el azul real
    d = np.clip((L - brillo) / (255.0 - brillo), 0, 1)[:, :, None]
    nueva = nueva * (1 - d * 0.70) + np.minimum(rgb, 255) * (d * 0.70)
    p = peso[:, :, None]
    return rgb * (1 - p) + np.clip(nueva, 0, 255) * p


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('entrada'); ap.add_argument('salida')
    ap.add_argument('--solo-mascara', action='store_true')
    o = ap.parse_args()

    im = Image.open(o.entrada).convert('RGBA')
    a = np.asarray(im).astype(float)
    alfa = a[..., 3]
    al = alfa[:, :, None] / 255.0
    rgb = a[..., :3] * al + FONDO * (1 - al)
    cx, cy = CENTRO

    # el azul de la propia foto: bisel y contadores
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    az = (b - r > 30) & (b > 60)
    medio = rgb[az].mean(axis=0)
    tono = medio / medio.mean()
    print('azul medido en la foto: RGB(%.0f, %.0f, %.0f)  -> tono %.2f/%.2f/%.2f'
          % (*medio, *tono))

    peso = np.zeros(rgb.shape[:2], np.float32)
    for h in AGUJAS:
        L = np.asarray(gira(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)),
                            h['ang'], (cx, cy))).astype(float).mean(2)
        pa, pb, ra, rb, n = rieles(L, cx, cy, h['col0'], h['col1'])
        print('%-9s %d columnas . riel alto y=%+.5fx%+.2f (resto %.1f) . '
              'riel bajo y=%+.5fx%+.2f (resto %.1f)'
              % (h['nombre'], n, pa[0], pa[1], ra, pb[0], pb[1], rb))
        ex = hombro(L, cx, cy, pa, h['hub'], h['col0']) if h.get('hombro') else None
        m = mascara(L.shape, cx, cy, pa, pb, h['hub'], h['punta'], h['col1'], ex)
        m = np.asarray(gira(Image.fromarray((m * 255).astype(np.uint8)),
                            -h['ang'], (cx, cy))).astype(np.float32) / 255.0
        peso = np.maximum(peso, m)
        print('%-9s %d px de mascara' % ('', (m > 0.5).sum()))

    if o.solo_mascara:
        Image.fromarray((peso * 255).astype(np.uint8)).save(o.salida)
        raise SystemExit(0)

    # SOLO se tocan los pixeles de las agujas: el resto de la foto sale
    # byte a byte como entro, transparencia y bordes incluidos.
    tinta = azulea(rgb, np.ones_like(peso), tono)
    p3 = peso[:, :, None]
    out = a[..., :3] * (1 - p3) + np.clip(tinta, 0, 255) * p3
    Image.fromarray(np.dstack([out, alfa]).astype(np.uint8)).save(o.salida)
    print('escrito %s . %d px teñidos' % (o.salida, (peso > 0.5).sum()))
