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
import numpy as np


def periodo(pieza):
    """Cada cuántos píxeles se repite el dibujo de la correa."""
    a = np.asarray(pieza.convert('L'), dtype=float)
    filas = a.mean(axis=1)
    filas = filas - filas.mean()
    mejor, punto = -2.0, None
    lo, hi = max(30, int(len(filas)*0.12)), max(40, int(len(filas)*0.62))
    for p in range(lo, hi):
        v = np.corrcoef(filas[:-p], filas[p:])[0, 1]
        if v > mejor:
            mejor, punto = v, p
    if punto is None:
        return len(filas)
    # afinado fino: el periodo bueno es el que hace INVISIBLE la junta,
    # o sea el que mejor casa las dos franjas que quedarán pegadas
    img = np.asarray(pieza.convert('RGB'), dtype=float)
    h = img.shape[0]
    franja = 24
    mejor_err, fino = None, punto
    for p in range(max(30, punto-10), min(h-franja, punto+11)):
        a1 = img[h-franja:h]
        a2 = img[h-p-franja:h-p]
        err = np.abs(a1-a2).mean()
        if mejor_err is None or err < mejor_err:
            mejor_err, fino = err, p
    return fino


def alarga(pieza, alto, por_arriba, P=None):
    """Si falta poco, se estira ese poco (invisible); si falta mucho,
    se prolonga repitiendo el periodo real de la correa."""
    """Prolonga la correa REPITIENDO su periodo — nunca estirándola.

    El extremo que se mete bajo la caja no se toca: se añade tira por
    el lado contrario, que es donde la repetición es invisible.
    """
    if pieza.height >= alto:
        caja = (0, pieza.height-alto, pieza.width, pieza.height) if por_arriba \
               else (0, 0, pieza.width, alto)
        return pieza.crop(caja)
    if alto <= pieza.height*1.12:        # un pelín: estirar no se nota
        return pieza.resize((pieza.width, alto), Image.LANCZOS)
    P = P or periodo(pieza)
    if P >= pieza.height:                # no cabe ni un periodo: estira
        return pieza.resize((pieza.width, alto), Image.LANCZOS)
    nueva = Image.new('RGBA', (pieza.width, alto), (0, 0, 0, 0))
    if por_arriba:
        y = alto - pieza.height
        nueva.paste(pieza, (0, y), pieza)
        slab = pieza.crop((0, 0, pieza.width, P))
        while y > 0:
            y -= P
            nueva.paste(slab, (0, y), slab)
    else:
        nueva.paste(pieza, (0, 0), pieza)
        y = pieza.height
        slab = pieza.crop((0, pieza.height-P, pieza.width, pieza.height))
        while y < alto:
            nueva.paste(slab, (0, y), slab)
            y += P
    return nueva


# ---------------------------------------------------------------- base
def fondo_de_fila(px, W, y, borde=0.03):
    """El fondo se mide EN CADA FILA: estas fotos llevan degradado."""
    n = max(4, int(W*borde))
    m = [px[x, y] for x in range(n)] + [px[W-1-x, y] for x in range(n)]
    return tuple(int(statistics.median([c[i] for c in m])) for i in range(3))


def mide_base(im):
    W, H = im.size
    px = im.load()
    bg = fondo_de_fila(px, W, 10)

    def franja(y):
        f = fondo_de_fila(px, W, y)
        xs = [x for x in range(W)
              if abs(px[x, y][0]-f[0]) + abs(px[x, y][1]-f[1])
               + abs(px[x, y][2]-f[2]) > 40]
        return (xs[0], xs[-1]) if xs else None

    # TODO en proporción al tamaño de la foto: hay bases de 4096 y de
    # 1254, y medir con números fijos se comía media caja (17/08/2026)
    paso = max(1, H//700)
    anchos = {y: (franja(y)[1]-franja(y)[0]) for y in range(0, H, paso)
              if franja(y)}
    filas = sorted(anchos)
    y_caja = max(anchos, key=anchos.get)          # la fila más ancha = caja
    caja_w = anchos[y_caja]

    def bordes_caja(ancho_correa):
        """de la fila más ancha hacia fuera, mientras siga siendo caja."""
        lim = ancho_correa*1.05
        y0 = y1 = y_caja
        for y in [y for y in filas if y < y_caja][::-1]:
            if anchos[y] <= lim:
                break
            y0 = y
        for y in [y for y in filas if y > y_caja]:
            if anchos[y] <= lim:
                break
            y1 = y
        return y0, y1

    provisional = statistics.median([anchos[y] for y in filas[:max(3, len(filas)//12)]])
    y0, y1 = bordes_caja(provisional)
    # la correa se mide JUNTO a la caja, que es donde debe casar con las
    # asas — no en el borde del lienzo, donde puede ir más estrecha
    cerca = [y for y in filas if y0-H*0.10 < y < y0-H*0.01] or filas[:6]
    correa_w = int(statistics.median([anchos[y] for y in cerca]))
    y0, y1 = bordes_caja(correa_w)
    f = franja(cerca[len(cerca)//2])
    return dict(bg=bg, cx=(f[0]+f[1])//2, cy=(y0+y1)//2, caja_w=caja_w,
                correa_w=correa_w, caja_y0=y0, caja_y1=y1)


def tramos_brazalete(im, B, margen=None):
    """Los dos trozos de correa, ya recortados y con transparencia.

    Se corta BIEN LEJOS de la caja (y justo al ancho de la correa) para
    que no se cuele ni una punta de asa de la foto original.
    """
    W, H = im.size
    px = im.load()
    if margen is None:
        margen = int(H*0.015)

    piezas = []
    for y0, y1 in ((0, B['caja_y0']-margen), (B['caja_y1']+margen, H)):
        media = int(B['correa_w']*0.49)          # sin rebabas laterales
        x0, x1 = B['cx']-media, B['cx']+media
        trozo = im.crop((x0, y0, x1, y1)).convert('RGBA')
        tp = trozo.load()
        for y in range(trozo.height):
            f = fondo_de_fila(px, W, min(H-1, y0+y))
            for x in range(trozo.width):
                p = tp[x, y]
                if abs(p[0]-f[0])+abs(p[1]-f[1])+abs(p[2]-f[2]) <= 40:
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
        tr = tramos_brazalete(base, B)
        # el periodo se mide en el tramo MÁS LARGO y vale para los dos
        _cache[ruta_base] = (base, B, tr, periodo(max(tr, key=lambda t: t.height)))
    base, B, (arriba, abajo), P = _cache[ruta_base]

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
    # la correa tiene que morir DENTRO DEL CUERPO de la caja, no entre
    # las asas: se busca dónde la silueta pasa de asas a caja
    alfa = nc.getchannel('A')
    an = np.asarray(alfa) > 100
    filas_con = [(y, np.flatnonzero(an[y])) for y in range(0, an.shape[0], 2)
                 if an[y].any()]
    # el cuerpo de la caja = filas de UNA sola pieza; las asas son dos
    def de_una_pieza(xs):
        return len(xs) > 0 and (np.diff(xs).max(initial=1) <= 3)
    cuerpo = [y for y, xs in filas_con if de_una_pieza(xs)]
    cabeza_y0 = oy + (min(cuerpo) if cuerpo else filas_con[0][0])
    cabeza_y1 = oy + (max(cuerpo) if cuerpo else filas_con[-1][0])
    dentro = int((cabeza_y1-cabeza_y0)*0.06)            # cuánto se esconde

    for pieza, arriba_p in ((arriba, True), (abajo, False)):
        # largo necesario: del borde del lienzo hasta DEBAJO de la caja
        largo = max(60, (cabeza_y0+dentro) if arriba_p
                        else (H - (cabeza_y1-dentro)))
        # se prolonga repitiendo su periodo y se escala SIN deformar
        pieza = alarga(pieza, int(round(largo/e))+2, arriba_p, P)
        np_ = pieza.resize((max(1, round(pieza.width*e)),
                            max(1, round(pieza.height*e))), Image.LANCZOS)
        x = round(CX - np_.width/2)
        y = (largo - np_.height) if arriba_p else H - largo
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
