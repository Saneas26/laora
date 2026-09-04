# -*- coding: utf-8 -*-
"""Comprobacion de la entrega. Si esto no sale limpio, el reloj pega un salto
al cambiar de color y el despiece no sirve.

Todo se mide sobre el canal alfa con umbral 128 (cobertura mayor de media).
"""
import sys, os, glob
import numpy as np
from PIL import Image
from scipy import ndimage

UMBRAL = 128

def alfa(p):
    return np.array(Image.open(p).convert('RGBA'))[:,:,3]

def caja(m):
    ys, xs = np.where(m)
    return xs.min(), xs.max(), ys.min(), ys.max()

def disco(a):
    x0,x1,y0,y1 = caja(a >= UMBRAL)
    return x1-x0+1, y1-y0+1, (x0+x1)/2, (y0+y1)/2

def hueco(a):
    fondo = a < UMBRAL
    lab, n = ndimage.label(fondo)
    fuera = set(lab[0,:]) | set(lab[-1,:]) | set(lab[:,0]) | set(lab[:,-1])
    mejor, tam = None, 0
    for i in range(1, n+1):
        if i in fuera: continue
        s = int((lab == i).sum())
        if s > tam: mejor, tam = i, s
    x0,x1,y0,y1 = caja(lab == mejor)
    return x1-x0+1, y1-y0+1, (x0+x1)/2, (y0+y1)/2

def tramos(a):
    filas = np.where((a >= UMBRAL).any(axis=1))[0]
    cortes = np.where(np.diff(filas) > 1)[0]
    tr, ini = [], filas[0]
    for c in cortes:
        tr.append((int(ini), int(filas[c]))); ini = filas[c+1]
    tr.append((int(ini), int(filas[-1])))
    return tr

def filete(p):
    """Cuanto se aclara el canto respecto al pixel opaco vecino."""
    a = np.array(Image.open(p).convert('RGBA')).astype(np.float32)
    L = a[:,:,:3].mean(2); al = a[:,:,3]
    op = al >= 250; canto = (al > 10) & ~op
    if not canto.any() or not op.any(): return 0.0
    idx = ndimage.distance_transform_edt(~op, return_indices=True, return_distances=False)
    d = (L - L[idx[0], idx[1]])[canto]
    return float(d.mean())

def revisa(carpeta, originales):
    fallos = []
    ref = {os.path.basename(f)[:2]: alfa(f) for f in glob.glob(f'{originales}/*.png')}
    for f in sorted(glob.glob(f'{carpeta}/*.png')):
        b = os.path.basename(f)
        im = Image.open(f)
        a = alfa(f)
        linea, mal = [], False
        if im.size != (4096,4096) or im.mode != 'RGBA':
            linea.append(f'!! {im.size} {im.mode}'); mal = True
        if not np.array_equal(a, ref[b[:2]]):
            linea.append('!! el alfa NO es el del original'); mal = True
        else:
            linea.append('alfa identico al original')
        if b.startswith('03'):
            w,h,cx,cy = disco(a)
            ok = (w,h,cx,cy) == (1418,1418,2047.5,1667.5)
            linea.append(f'disco {w}x{h} centro ({cx},{cy})'); mal |= not ok
        elif b.startswith('02'):
            w,h,cx,cy = hueco(a)
            ok = (w,h,cx,cy) == (1419,1419,2048.0,1668.0)
            linea.append(f'hueco {w}x{h} centro ({cx},{cy})'); mal |= not ok
        elif b.startswith('01'):
            t = tramos(a)
            ok = len(t) == 2 and t[0][1] == 719 and t[1][0] == 2675
            linea.append(f'tira norte acaba en {t[0][1]}, sur empieza en {t[1][0]}'); mal |= not ok
        fl = filete(f)
        linea.append(f'canto {fl:+.1f}')
        if fl > 12: mal = True
        print(('MAL ' if mal else 'OK  ') + b.ljust(48) + ' | ' + ' | '.join(linea))
        if mal: fallos.append(b)
    print()
    if fallos:
        print('HAY FALLOS en:', ', '.join(fallos)); return 1
    print('TODO CORRECTO: las %d piezas caen en la misma posicion del lienzo.' %
          len(glob.glob(f'{carpeta}/*.png')))
    return 0

if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv)>1 else 'salida/despiece-bitacora-2026'
    o = sys.argv[2] if len(sys.argv)>2 else 'despiece/despiece-bitacora'
    sys.exit(revisa(c, o))
