# -*- coding: utf-8 -*-
"""
Mide el BORDE EXTERIOR DEL BISEL del Lunar: el círculo donde el negro del
taquímetro acaba y empieza el acero de la caja.

SE MIDE DE FUERA A DENTRO (22/08/2026, segunda tanda). La primera versión
iba de dentro a fuera buscando «negro y luego acero sostenido 14 px», y eso
mentía: en la cabeza la pared de la caja es de solo 9 px, así que el rayo se
comía la pared y se paraba en el FONDO; en las fotos de Óscar, con la pared
aún más fina en algunos ángulos, unas veces paraba en el bisel y otras en la
silueta. Medía dos cosas distintas según la foto — de ahí que unas correas
cuadraran y otras no.

Ahora cada rayo entra desde fuera del reloj:
  1. primer píxel que NO es fondo, con 6 px seguidos de objeto → filo de la caja;
  2. desde ahí hacia dentro, primer tramo de 8 px seguidos de negro → bisel.
Así el punto siempre significa lo mismo, haya la pared que haya.

Se usan tres arcos limpios (la izquierda entera y las dos diagonales de la
derecha) para esquivar asas, corona y pulsadores, y se ajusta un círculo por
mínimos cuadrados con recorte de atípicos.
"""
import math
import numpy as np
from PIL import Image

FONDO = (234, 232, 232)
ARCOS = [(200, 340), (20, 70), (110, 160)]
CENTRO = (627.4, 565.3)


def _es_fondo(p):
    return p.min() > 200 and (p.max() - p.min()) < 14


def _lum(a):
    return a.mean(axis=2)


def _bilineal(lum, x, y):
    H, W = lum.shape
    x0, y0 = int(x), int(y)
    if not (0 <= x0 < W - 1 and 0 <= y0 < H - 1): return 255.0
    fx, fy = x - x0, y - y0
    return float(lum[y0, x0] * (1 - fx) * (1 - fy) + lum[y0, x0 + 1] * fx * (1 - fy)
                 + lum[y0 + 1, x0] * (1 - fx) * fy + lum[y0 + 1, x0 + 1] * fx * fy)


def puntos_bisel(im, centro=CENTRO, r_fuera=460):
    """Puntos (x, y) del borde exterior del bisel, con precisión de subpíxel.

    El corte se toma donde la luz cae al PUNTO MEDIO entre el acero de la
    caja y el negro del bisel de ESE rayo. Un umbral fijo se movería con el
    desenfoque del reescalado —hasta 3 px, que era el resto que dejaba cada
    vuelta—; el punto medio no, porque el desenfoque es simétrico.
    """
    a = np.asarray(im.convert('RGB')).astype(int)
    lum = _lum(a); H, W, _ = a.shape
    cx, cy = centro
    P = []
    for lo_a, hi_a in ARCOS:
        for g in range(lo_a, hi_a + 1, 1):
            t = math.radians(g); dx, dy = math.sin(t), -math.cos(t)
            pos = lambda r: (int(round(cx + dx * r)), int(round(cy + dy * r)))
            dentro = lambda x, y: 0 <= x < W and 0 <= y < H
            caja = None
            r = r_fuera
            while r > 300:
                x, y = pos(r)
                if dentro(x, y) and not _es_fondo(a[y, x]):
                    if all(dentro(*pos(r - j)) and not _es_fondo(a[pos(r - j)[1], pos(r - j)[0]])
                           for j in range(1, 7)):
                        caja = r; break
                r -= 1
            if caja is None: continue
            v = [_bilineal(lum, cx + dx * rr, cy + dy * rr)
                 for rr in [caja + 3 - 0.25 * i for i in range(int((3 + 34) / 0.25))]]
            i = next((j for j in range(4, len(v)) if v[j] < 100), None)
            if i is None: continue
            alto = max(v[:i]); bajo = min(v[i:i + 16])
            if alto - bajo < 60: continue
            T = (alto + bajo) / 2.0
            j = i
            while j > 0 and v[j] < T: j -= 1
            if v[j] <= T: continue
            f = (v[j] - T) / (v[j] - v[j + 1])
            rr = caja + 3 - 0.25 * (j + f)
            P.append((cx + dx * rr, cy + dy * rr))
    return P


def bisel_ext(im, centro=CENTRO):
    """centro x, centro y, radio, error medio y número de puntos del bisel.

    Ajuste EN POLARES: r(t) = R + tx·sen t − ty·cos t, que es el mismo
    círculo pero lineal en (R, tx, ty) y bien condicionado aunque los puntos
    no den la vuelta entera.
    """
    P = np.array(puntos_bisel(im, centro), float)
    cx0, cy0 = centro
    t = np.arctan2(P[:, 0] - cx0, -(P[:, 1] - cy0))
    r = np.hypot(P[:, 0] - cx0, P[:, 1] - cy0)
    # Filtro por MODA, no por mediana: casi la mitad de los rayos se comen un
    # asa, la corona o el propio tejido y devuelven radios de 380 a 460. Con
    # la mediana el corte caía entre los dos grupos y se quedaba con la
    # basura; la moda se queda con el grupo apretado, que es el bisel.
    h, bordes = np.histogram(r, bins=np.arange(300, 470, 1.0))
    h = np.convolve(h, np.ones(5), 'same')
    pico = bordes[int(h.argmax())] + 0.5
    m = np.abs(r - pico) < 6
    t, r = t[m], r[m]
    A = np.stack([np.ones(len(t)), np.sin(t), -np.cos(t)], 1)
    for _ in range(3):
        c = np.linalg.lstsq(A, r, rcond=None)[0]
        e = np.abs(A @ c - r)
        m = e < max(np.percentile(e, 85), 0.6)
        A, r = A[m], r[m]
    return cx0 + c[1], cy0 + c[2], c[0], float(e.mean()), len(A)


def _ajusta_circulo(P, centro):
    """Círculo robusto en polares a partir de una nube de puntos de borde."""
    P = np.array(P, float)
    cx0, cy0 = centro
    t = np.arctan2(P[:, 0] - cx0, -(P[:, 1] - cy0))
    r = np.hypot(P[:, 0] - cx0, P[:, 1] - cy0)
    h, bordes = np.histogram(r, bins=np.arange(280, 470, 1.0))
    h = np.convolve(h, np.ones(5), 'same')
    m = np.abs(r - (bordes[int(h.argmax())] + 0.5)) < 6
    t, r = t[m], r[m]
    A = np.stack([np.ones(len(t)), np.sin(t), -np.cos(t)], 1)
    for _ in range(3):
        c = np.linalg.lstsq(A, r, rcond=None)[0]
        e = np.abs(A @ c - r)
        m = e < max(np.percentile(e, 85), 0.6)
        A, r = A[m], r[m]
    return cx0 + c[1], cy0 + c[2], c[0], float(e.mean()), len(A)


def bisel_chaflan(im, centro=CENTRO):
    """El bisel de un reloj de CAJA NEGRA, por el chaflán pulido.

    En la foto del brazalete PVD la caja y el bisel son los dos negros, así
    que el detector normal se para en el filo de la caja. Lo que sí se ve es
    el brillo del chaflán: caja mate → destello → negro plano del bisel. Se
    toma el final de ese destello. Cae unos 4 px por dentro del borde real,
    así que quien lo use tiene que corregirlo con la proporción medida en una
    foto de caja de acero (ahí se pueden medir las dos cosas).
    """
    a = np.asarray(im.convert('RGB')).astype(int)
    lum = a.mean(axis=2); H, W, _ = a.shape
    cx, cy = centro; P = []
    for lo_a, hi_a in ARCOS:
        for g in range(lo_a, hi_a + 1):
            t = math.radians(g); dx, dy = math.sin(t), -math.cos(t)
            pos = lambda r: (int(round(cx + dx * r)), int(round(cy + dy * r)))
            r = 460; caja = None
            while r > 300:
                x, y = pos(r)
                if 0 <= x < W and 0 <= y < H and not _es_fondo(a[y, x]):
                    if all(not _es_fondo(a[pos(r - j)[1], pos(r - j)[0]]) for j in range(1, 7)):
                        caja = r; break
                r -= 1
            if caja is None: continue
            v = [lum[pos(caja - j)[1], pos(caja - j)[0]] for j in range(0, 34)]
            pico = next((j for j in range(4, 30)
                         if v[j] > 100 and v[j] >= max(v[max(0, j - 3):j + 4])), None)
            if pico is None: continue
            fin = next((j for j in range(pico + 1, 34)
                        if all(v[k] < 60 for k in range(j, min(j + 6, 34)))), None)
            if fin is None: continue
            P.append((cx + dx * (caja - fin), cy + dy * (caja - fin)))
    return _ajusta_circulo(P, centro)


def sobre_fondo(ruta, fondo=FONDO):
    """La cabeza (PNG con alfa) plantada sobre el gris de estudio."""
    im = Image.open(ruta).convert('RGBA')
    bg = Image.new('RGBA', im.size, tuple(fondo) + (255,))
    bg.alpha_composite(im)
    return bg


if __name__ == '__main__':
    import json
    ref = sobre_fondo('assets/img/lunar-config/heads/cab-acero-bnegro-agujas-plateadas.webp')
    print('CABEZA ref   bisel centro=(%.1f,%.1f) R=%.1f err=%.2f n=%d' % bisel_ext(ref))
    m = json.load(open('assets/img/lunar-config/manifest.json'))
    for k, st in m['straps'].items():
        im = Image.open('.' + st['src'].split('?')[0])
        print('%-40s centro=(%.1f,%.1f) R=%.1f err=%.2f n=%d' % ((k,) + bisel_ext(im)))
