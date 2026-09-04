# -*- coding: utf-8 -*-
"""Mascara de los eslabones centrales (capsulas pulidas) del brazalete.

No mide nada nuevo: recorre cada capsula fila a fila y se para en el surco
oscuro que la rodea. La caja solo acota la busqueda."""
import numpy as np
from PIL import Image
from scipy import ndimage

CAJAS = [(1855,2258,118,230),(1843,2258,246,395),(1825,2272,448,613),
         (1797,2279,2862,3068),(1809,2267,3174,3348),(1819,2256,3449,3609),
         (1827,2247,3669,3794),(1835,2237,3826,3918),(1832,2230,3926,3985)]
UMBRAL = 150

def construir(ruta='despiece/despiece-bitacora/01-brazalete-norte-sur.png', avisar=True):
    a = np.array(Image.open(ruta).convert('RGBA')).astype(np.float32)
    L = a[:,:,:3].mean(2); al = a[:,:,3]
    borde = (L < UMBRAL) | (al < 120)
    m = np.zeros(L.shape, bool)
    for k,(x0,x1,y0,y1) in enumerate(CAJAS):
        cx0 = (x0+x1)//2
        XA, XB = x0-12, x1+12
        YA, YB = y0-8, y1+8
        trozo = np.zeros((YB-YA+1, XB-XA+1), bool)
        for y in range(YA, YB+1):
            cx = None                       # columna de arranque de la fila
            for d in range(0, 60):
                for c in (cx0-d, cx0+d):
                    if not borde[y,c]: cx = c; break
                if cx is not None: break
            if cx is None: continue
            xl = cx
            while xl > XA and not borde[y,xl-1]: xl -= 1
            if xl <= XA: continue           # se escapa: la fila no es capsula
            xr = cx
            while xr < XB and not borde[y,xr+1]: xr += 1
            if xr >= XB: continue
            trozo[y-YA, xl-XA:xr+1-XA] = True
        lab,n = ndimage.label(trozo)
        if not n:
            print(f'  AVISO: capsula {k} vacia'); continue
        ancho_min = 0.5*(x1-x0)
        vale = np.zeros_like(trozo)
        for i,sl in enumerate(ndimage.find_objects(lab), 1):
            if sl is None: continue
            if (sl[1].stop-sl[1].start) >= ancho_min and (lab[sl]==i).sum() > 150:
                vale |= (lab==i)
        trozo = rellena_convexo(vale)
        m[YA:YB+1, XA:XB+1] |= trozo
        ys,xs = np.where(trozo)
        if avisar:
            print(f'  capsula {k}: {int(trozo.sum())} px  x {xs.min()+XA}-{xs.max()+XA}'
                  f'  y {ys.min()+YA}-{ys.max()+YA}')
    m = ndimage.binary_closing(m, np.ones((5,5)))
    m = ndimage.binary_dilation(m, np.ones((7,7)))   # muerde el filo del surco
    return m

def rellena_convexo(t):
    """Cierra las grietas: en cada columna y en cada fila, rellena entre extremos."""
    out = t.copy()
    for eje in (0,1):
        acc = np.maximum.accumulate(out, axis=eje)
        acc2 = np.flip(np.maximum.accumulate(np.flip(out, eje), axis=eje), eje)
        out = acc & acc2
    return out

if __name__ == '__main__':
    m = construir()
    np.save('mask_centros.npy', m)
    im = Image.open('despiece/despiece-bitacora/01-brazalete-norte-sur.png').convert('RGBA')
    f = Image.new('RGBA', im.size, (120,120,120,255)); f.alpha_composite(im)
    v = np.array(f.convert('RGB'))
    v[m] = (v[m]*0.42 + np.array([255,80,0])*0.58).astype(np.uint8)
    Image.fromarray(v).crop((1400,110,2700,740)).resize((1040,504)).save('vista/mask-norte.png')
    Image.fromarray(v).crop((1350,2660,2760,4020)).resize((760,733)).save('vista/mask-sur.png')
    print('total', m.sum())
