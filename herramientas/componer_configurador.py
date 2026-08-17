#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador por capas de laOra 2026: monta CUALQUIER cabeza-máster
sobre UNA foto base de reloj completo (la del brazalete), sin generar
ni una imagen nueva con IA.

Idea (la de Omega): la foto de la correa/brazalete se hace UNA vez; la
cabeza se sustituye por encima. Aquí todo el registro es automático:

1. Mide la base: centro (por el eje del brazalete), tamaño de caja y
   ancho del brazalete.
2. Mide la cabeza: centro real = punto medio del hueco entre asas,
   tamaño de caja y ancho entre asas.
3. Escala la cabeza para que su caja mida lo mismo que la de la base.
4. Ensancha el brazalete al ancho de asas de esa cabeza.
5. Borra la cabeza vieja, pega la nueva y estira el metal hasta el
   borde de la caja para que la unión no deje aire.

Uso:
  python3 componer_configurador.py <base.png> <cabeza.png> <salida> [px]
"""
from PIL import Image
import sys, math


def mide_base(im):
    """centro x por el eje del brazalete, centro y y tamaño de caja."""
    W, H = im.size
    px = im.load()
    bg = px[10, 10]

    def objeto(p):
        return abs(p[0]-bg[0]) + abs(p[1]-bg[1]) + abs(p[2]-bg[2]) > 40

    def franja(y):
        xs = [x for x in range(W) if objeto(px[x, y])]
        return (xs[0], xs[-1]) if xs else None

    f = franja(150)                       # brazalete limpio, arriba
    cx = (f[0] + f[1]) // 2
    ancho_correa = f[1] - f[0]
    anchos = {}
    for y in range(400, H-400, 8):
        g = franja(y)
        if g:
            anchos[y] = g[1] - g[0]
    caja_w = max(anchos.values())
    filas = [y for y, a in anchos.items() if a > caja_w*0.9]
    cy = (min(filas) + max(filas)) // 2
    return dict(bg=bg, cx=cx, cy=cy, caja_w=caja_w, correa_w=ancho_correa)


def mide_cabeza(im):
    """centro x = mitad del hueco entre asas; centro y y caja."""
    w, h = im.size
    px = im.load()

    def tramos(y):
        rs, ini = [], None
        for x in range(w):
            if px[x, y][3] > 0:
                if ini is None:
                    ini = x
            elif ini is not None:
                rs.append((ini, x-1)); ini = None
        if ini is not None:
            rs.append((ini, w-1))
        return rs

    hueco = None
    for y in range(40, h//3):                    # entre las asas de arriba
        rs = tramos(y)
        if len(rs) >= 2:
            hueco = (rs[0][1], rs[1][0])
            break
    anchos = {}
    for y in range(100, h-100, 4):
        rs = tramos(y)
        if rs:
            anchos[y] = rs[-1][1] - rs[0][0]
    caja_w = max(anchos.values())
    filas = [y for y, a in anchos.items() if a > caja_w*0.9]
    cy = (min(filas) + max(filas)) // 2
    cx = (hueco[0] + hueco[1]) / 2 if hueco else w/2
    gap = (hueco[1] - hueco[0]) if hueco else caja_w*0.45
    return dict(cx=cx, cy=cy, caja_w=caja_w, gap=gap)


def compone(ruta_base, ruta_cabeza, salida, px_salida=1600):
    base = Image.open(ruta_base).convert('RGB')
    cab = Image.open(ruta_cabeza).convert('RGBA')
    B = mide_base(base)
    C = mide_cabeza(cab)
    W, H = base.size
    bg = B['bg']
    s = B['caja_w'] / C['caja_w']              # cabeza a tamaño de la base
    gap = C['gap'] * s                          # ancho de asas ya escalado
    CX, CY = B['cx'], B['cy']
    R = B['caja_w'] // 2

    # 1) brazalete al ancho de asas de esta cabeza (bloques limpios)
    med_old, med_new = B['correa_w']//2, int(gap//2)
    for y0, y1 in ((0, CY-R-8), (CY+R+8, H)):
        if y1 <= y0:
            continue
        banda = base.crop((CX-med_old, y0, CX+med_old, y1))
        banda = banda.resize((med_new*2, y1-y0), Image.LANCZOS)
        base.paste(banda, (CX-med_new, y0))

    # 2) fuera la cabeza vieja (y la corona, que sobresale del círculo)
    d = Image.new('RGB', base.size, bg)
    mascara = Image.new('L', base.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mascara).ellipse((CX-R-14, CY-R-14, CX+R+14, CY+R+14), fill=255)
    ImageDraw.Draw(mascara).rectangle((CX+R-40, CY-700, min(W, CX+R+520), CY+700), fill=255)
    base.paste(d, (0, 0), mascara)

    # 3) la cabeza nueva, registrada por el hueco entre asas
    nc = cab.resize((round(cab.width*s), round(cab.height*s)), Image.LANCZOS)
    ox, oy = round(CX - C['cx']*s), round(CY - C['cy']*s)
    compo = base.convert('RGBA')
    compo.alpha_composite(nc, (ox, oy))

    # 4) el brazalete sube/baja hasta morder la caja (sin aire)
    plano = compo.convert('RGB')
    p = plano.load()
    a = nc.load()

    def alfa(x, y):
        xm, ym = x-ox, y-oy
        return a[xm, ym][3] if 0 <= xm < nc.width and 0 <= ym < nc.height else 0

    def es_bg(q):
        return abs(q[0]-bg[0]) + abs(q[1]-bg[1]) + abs(q[2]-bg[2]) < 30

    for dx in range(-med_new, med_new+1):
        x = CX + dx
        for sentido in (1, -1):
            borde = None
            rango = range(CY, H) if sentido > 0 else range(CY, 0, -1)
            for y in rango:
                if alfa(x, y) > 128:
                    borde = y
            if borde is None:
                continue
            y = borde + sentido
            while 0 < y < H and es_bg(p[x, y]):
                y += sentido
            hueco_px = abs(y - borde) - 1
            if not (3 < hueco_px < 400) or not (0 < y < H):
                continue
            alto = 260
            origen = [p[x, min(H-1, max(0, y + sentido*k))] for k in range(alto)]
            total = hueco_px + alto
            for k in range(total):
                yy = borde + sentido*k
                if 0 <= yy < H:
                    p[x, yy] = origen[min(alto-1, int(k*alto/total))]

    plano.resize((px_salida, px_salida), Image.LANCZOS).save(salida, quality=93)
    return dict(escala=round(s, 4), gap=round(gap), centro=(CX, CY))


if __name__ == '__main__':
    b, c, o = sys.argv[1], sys.argv[2], sys.argv[3]
    px = int(sys.argv[4]) if len(sys.argv) > 4 else 1600
    print(compone(b, c, o, px), '->', o)
