#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador por capas de laOra 2026 — método Omega, SIN dibujar nada.

La foto del brazalete se hace UNA vez. De ella se recortan los dos
tramos de brazalete (arriba y abajo), y se colocan DETRÁS de la cabeza:
el corte del tramo queda escondido bajo la caja, así que no hay unión
que pintar ni retocar. Ningún píxel es inventado: o es de la foto del
brazalete, o es de la foto de la cabeza.

Registro automático y a prueba de manchas:
  · el centro de la cabeza = punto medio del hueco entre asas, medido
    en muchas filas y con mediana (un píxel suelto ya no descoloca);
  · el brazalete se escala UNIFORME (sin deformar los eslabones) hasta
    que su ancho coincide con ese hueco.

Uso:
  python3 componer_configurador.py <base.png> <cabeza.png> <salida> [px]
"""
from PIL import Image
import sys, statistics


# ---------------------------------------------------------------- base
def mide_base(im):
    W, H = im.size
    px = im.load()
    bg = px[10, 10]

    def objeto(p):
        return abs(p[0]-bg[0]) + abs(p[1]-bg[1]) + abs(p[2]-bg[2]) > 40

    def franja(y):
        xs = [x for x in range(W) if objeto(px[x, y])]
        return (xs[0], xs[-1]) if xs else None

    f = franja(150)
    cx, correa_w = (f[0]+f[1])//2, f[1]-f[0]
    anchos = {}
    for y in range(300, H-300, 6):
        g = franja(y)
        if g:
            anchos[y] = g[1]-g[0]
    caja_w = max(anchos.values())
    filas = [y for y, a in anchos.items() if a > caja_w*0.9]
    # el borde REAL de la caja: donde deja de ser solo correa/brazalete
    caja = [y for y, a in anchos.items() if a > correa_w*1.05]
    return dict(bg=bg, cx=cx, cy=(min(filas)+max(filas))//2, caja_w=caja_w,
                correa_w=correa_w, caja_y0=min(caja), caja_y1=max(caja))


def tramos_brazalete(im, B, margen=None):
    """Los dos trozos de correa, ya recortados y con transparencia.

    Se corta BIEN LEJOS de la caja (y justo al ancho de la correa) para
    que no se cuele ni una punta de asa de la foto original.
    """
    W, H = im.size
    px = im.load()
    bg = B['bg']
    if margen is None:
        margen = int(H*0.05)

    def objeto(p):
        return abs(p[0]-bg[0]) + abs(p[1]-bg[1]) + abs(p[2]-bg[2]) > 40

    piezas = []
    for y0, y1 in ((0, B['caja_y0']-margen), (B['caja_y1']+margen, H)):
        media = int(B['correa_w']*0.49)          # sin rebabas laterales
        x0, x1 = B['cx']-media, B['cx']+media
        trozo = im.crop((x0, y0, x1, y1)).convert('RGBA')
        tp = trozo.load()
        for y in range(trozo.height):
            for x in range(trozo.width):
                if not objeto(tp[x, y][:3]):
                    tp[x, y] = (0, 0, 0, 0)
        piezas.append(trozo)
    return piezas          # [arriba, abajo]


# -------------------------------------------------------------- cabeza
def mide_cabeza(im):
    """centro = mitad del hueco entre asas (mediana de muchas filas)."""
    w, h = im.size
    px = im.load()

    def tramos(y):
        rs, ini = [], None
        for x in range(w):
            if px[x, y][3] > 100:
                if ini is None:
                    ini = x
            elif ini is not None:
                rs.append((ini, x-1)); ini = None
        if ini is not None:
            rs.append((ini, w-1))
        return [r for r in rs if r[1]-r[0] > 8]      # fuera motas

    anchos = {}
    for y in range(60, h-60, 4):
        rs = tramos(y)
        if rs:
            anchos[y] = rs[-1][1]-rs[0][0]
    caja_w = max(anchos.values())
    filas_caja = [y for y, a in anchos.items() if a > caja_w*0.9]
    cy = (min(filas_caja)+max(filas_caja))//2

    centros, huecos = [], []
    for y in range(40, min(filas_caja)-30, 3):        # zona de asas de arriba
        rs = tramos(y)
        if len(rs) < 2:
            continue
        hueco = max(((rs[i][1], rs[i+1][0]) for i in range(len(rs)-1)),
                    key=lambda p: p[1]-p[0])
        ancho = hueco[1]-hueco[0]
        if ancho > caja_w*0.25:                       # un hueco creíble
            centros.append((hueco[0]+hueco[1])/2)
            huecos.append(ancho)
    if not centros:                                   # sin asas visibles
        rs = tramos(filas_caja[len(filas_caja)//2])
        centros = [(rs[0][0]+rs[-1][1])/2]
        huecos = [caja_w*0.47]
    return dict(cx=statistics.median(centros), cy=cy,
                caja_w=caja_w, gap=statistics.median(huecos))


# ------------------------------------------------------------- compone
def compone(ruta_base, ruta_cabeza, salida, px_salida=1600, _cache={}):
    if ruta_base not in _cache:
        base = Image.open(ruta_base).convert('RGB')
        B = mide_base(base)
        _cache[ruta_base] = (base, B, tramos_brazalete(base, B))
    base, B, (arriba, abajo) = _cache[ruta_base]

    cab = Image.open(ruta_cabeza).convert('RGBA')
    C = mide_cabeza(cab)
    W, H = base.size

    s = B['caja_w']/C['caja_w']                 # cabeza al tamaño de la base
    gap = C['gap']*s                            # hueco entre asas ya escalado
    e = gap/B['correa_w']                       # el brazalete, escala UNIFORME
    CX, CY = B['cx'], B['cy']

    lienzo = Image.new('RGBA', (W, H), B['bg']+(255,))
    nc = cab.resize((round(cab.width*s), round(cab.height*s)), Image.LANCZOS)
    ox, oy = round(CX-C['cx']*s), round(CY-C['cy']*s)
    l, t, r, bb = nc.getchannel('A').getbbox()          # silueta de la cabeza
    cabeza_y0, cabeza_y1 = oy+t, oy+bb
    dentro = int((cabeza_y1-cabeza_y0)*0.12)            # cuánto se esconde

    for pieza, arriba_p in ((arriba, True), (abajo, False)):
        # el tramo se estira SOLO lo justo para ir del borde del lienzo
        # hasta debajo de la caja: ni repetición ni costuras a la vista
        largo = (cabeza_y0+dentro) if arriba_p else (H - (cabeza_y1-dentro))
        largo = max(60, largo)
        np_ = pieza.resize((max(1, round(pieza.width*e)), largo), Image.LANCZOS)
        x = round(CX - np_.width/2)
        y = 0 if arriba_p else H - largo
        lienzo.alpha_composite(np_, (x, y))

    lienzo.alpha_composite(nc, (ox, oy))

    lienzo.convert('RGB').resize((px_salida, px_salida), Image.LANCZOS)\
          .save(salida, quality=93)
    return dict(escala_cabeza=round(s, 4), escala_brazalete=round(e, 4),
                gap=round(gap))


if __name__ == '__main__':
    b, c, o = sys.argv[1], sys.argv[2], sys.argv[3]
    px = int(sys.argv[4]) if len(sys.argv) > 4 else 1600
    print(compone(b, c, o, px), '->', o)
