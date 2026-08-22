#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte las madres de NATO y NATO + PIEL del Lunar en CORREA SOLA.

EL PORQUÉ (Óscar, 22/08: «nato beige y gris siguen mal, y en nato+piel gris
sigue mal»). Desde que la cabeza se monta entera, la foto de debajo estorba:
cada madre traía su propio reloj, con la caja un poco más pequeña que la de
la cabeza, y entre el asa de la cabeza y el tejido asomaba el asa de la FOTO
—una cuña de acero con filo recto que delata el montaje—. En la marrón no se
veía porque su tejido es el más ancho y tapaba ese hueco; en la beige, la
gris y la gris claro sí.

Además las madres no eran iguales entre sí: la beige tenía la correa 20 px
descentrada a la derecha y la gris claro es 60 px más estrecha que la marrón.

LO QUE HACE. De cada foto se queda SOLO con el tejido y lo reconstruye:
  · lo lleva a la geometría de la marrón, que es la que cuadra con las asas
    (mismo ancho y mismo eje en el encuentro con la caja);
  · lo prolonga hacia el centro por detrás del reloj, repitiendo el patrón
    con su PERIODO —medido por autocorrelación—, no reflejándolo: reflejar
    dibujaba un galón en mitad de la correa;
  · el resto del lienzo queda en el gris de estudio de esa misma foto.
Así, al montar la cabeza entera encima no hay nada que pueda asomar.

Es el mismo régimen que ya tenía la piel perforada: `soloCorrea` en el
manifiesto y la cabeza siempre entera.

Uso:
    python3 herramientas/correa_sola_lunar.py            # las once
    python3 herramientas/correa_sola_lunar.py beige      # las que casen
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

MANIFEST = 'assets/img/lunar-config/manifest.json'
ORIGENES = 'herramientas/madres-origen'
COMMIT_ORIGEN = 'c0bf6d0'
REFERENCIA = 'assets/img/lunar-config/straps/nato-espiga-marron.webp'
ARRIBA = range(5, 146, 5)      # filas donde el tejido va libre por encima
ABAJO = range(1060, 1246, 5)   # ídem por debajo
CORTE_ARRIBA, CORTE_ABAJO = 149, 1061


def origen(k):
    ruta = os.path.join(ORIGENES, k + '.webp')
    if not os.path.exists(ruta):
        os.makedirs(ORIGENES, exist_ok=True)
        open(ruta, 'wb').write(subprocess.check_output(
            ['git', 'show', '%s:assets/img/lunar-config/straps/%s.webp' % (COMMIT_ORIGEN, k)]))
    return ruta


def _obj(a):
    return ~((a.min(axis=2) > 200) & ((a.max(axis=2) - a.min(axis=2)) < 14))


def rectas(a, ys):
    """Las dos orillas del tejido, ajustadas a una recta."""
    obj = _obj(a); Y, xi, xd = [], [], []
    for y in ys:
        xs = np.where(obj[y])[0]
        if len(xs) > 5:
            Y.append(y); xi.append(xs.min()); xd.append(xs.max())
    return np.polyfit(Y, xi, 1), np.polyfit(Y, xd, 1)


def gris_de_estudio(a):
    borde = np.concatenate([a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    return borde.mean(axis=0).round().astype(np.uint8)


def periodo(src, y0, y1):
    """Cada cuántas filas se repite el tejido (autocorrelación vertical)."""
    g = np.asarray(Image.fromarray(src).convert('L')).astype(float)
    b = g[y0:y1, 520:760]; b = b - b.mean(axis=1, keepdims=True)
    mejor = (18, -1.0)
    for p in range(12, 60):
        n = (y1 - y0) - p
        x, y = b[:n], b[p:p + n]
        c = float((x * y).sum() / np.sqrt((x * x).sum() * (y * y).sum()))
        if c > mejor[1]: mejor = (p, c)
    return mejor[0]


def correa_sola(ruta, salida, ref=REFERENCIA):
    r = np.asarray(Image.open(ref).convert('RGB')).astype(int)
    ria, rda = rectas(r, ARRIBA)
    rib, rdb = rectas(r, ABAJO)
    src = np.asarray(Image.open(ruta).convert('RGB'))
    a = src.astype(int)
    sia, sda = rectas(a, ARRIBA)
    sib, sdb = rectas(a, ABAJO)
    P, Q = periodo(src, 10, 146), periodo(src, 1090, 1240)
    out = np.zeros_like(src); out[:] = gris_de_estudio(a)
    W = src.shape[1]

    def pinta(y, ys, oi, od, si, sd):
        x0, x1 = np.polyval(si, ys), np.polyval(sd, ys)
        X0, X1 = np.polyval(oi, y), np.polyval(od, y)
        anc = int(round(X1 - X0))
        if anc < 10: return
        xs = np.linspace(x0, x1, anc)
        fila = np.stack([np.interp(xs, np.arange(W), src[ys, :, c]) for c in range(3)], 1)
        ini = int(round(X0))
        out[y, max(0, ini):ini + anc] = fila[max(0, -ini):].round().astype(np.uint8)

    for y in range(0, 628):
        ys = y if y <= CORTE_ARRIBA else CORTE_ARRIBA - ((y - CORTE_ARRIBA - 1) % P) - 1
        pinta(y, ys, ria, rda, sia, sda)
    for y in range(627, 1254):
        ys = y if y >= CORTE_ABAJO else CORTE_ABAJO + ((CORTE_ABAJO - y - 1) % Q) + 1
        pinta(y, ys, rib, rdb, sib, sdb)
    Image.fromarray(out).save(salida, quality=95)
    return P, Q


if __name__ == '__main__':
    filtros = sys.argv[1:]
    m = json.load(open(MANIFEST))
    for k, st in m['straps'].items():
        if not (k.startswith('nato-espiga-') or k.startswith('nato-pasadores-')): continue
        if filtros and not any(f in k for f in filtros): continue
        destino = '.' + st['src'].split('?')[0]
        P, Q = correa_sola(origen(k), destino)
        st.pop('cabezaDeLaFoto', None)
        st.pop('cajaDeLaFoto', None)
        st.pop('mascaraFuera', None)
        st['soloCorrea'] = True
        st['correa_sola'] = ('22/08/2026: tejido solo, llevado a la geometría de nato-espiga-marron '
                             'y prolongado con periodo %d arriba y %d abajo. El reloj de la foto '
                             'se ha quitado: la cabeza va entera.' % (P, Q))
        print('%-30s hecha (periodo %d/%d)' % (k, P, Q))
    json.dump(m, open(MANIFEST, 'w'), ensure_ascii=False, indent=1)
