#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camino 1 del configurador laOra 2026: variantes de color de agujas SIN
volver a generar con IA. Una máscara angular por aguja (pivote + ángulo,
contornos suavizados por mediana) y recolor por luminancia con las
llaves de color MEDIDAS en la foto del artículo del proveedor.
La tira de lume (banda central) se conserva; la punta fina del segundero
se pinta aparte. Probado el 16/08/2026 sobre la cabeza aprobada del
Lunar (demo en masters-2026/lunar/demo-agujas-naranjas.png).

Geometría medida de lunar-cab-negra-plata.png (máster 1254×1254):
  pivote central (628,587) · hora 214,6° r40-302 lume 115-235
  minuto 316,8° r40-412 lume 150-335 · segundero 139,4° blanco r30-300
  + punta naranja r300-414 · subesferas: (395,590) 338,4° / (852,585)
  53,2° / (622,800) 219,2°, r10-84
Naranja del NO.40 (muestreado): sombra (170,96,31) · medio (239,133,48)
  · brillo (255,139,74)

Uso: python3 recolorear_agujas.py <entrada.png> <salida.png>
(las llaves de color y la geometría se ajustan en el propio script)
"""
from PIL import Image
import math, statistics, sys

def lum(p): return 0.299*p[0]+0.587*p[1]+0.114*p[2]

LLAVES_NARANJA = [(0,(60,30,8)),(90,(170,96,31)),(170,(239,133,48)),(245,(255,139,74)),(255,(255,150,90))]

def mapa(L, llaves):
    for (l0,c0),(l1,c1) in zip(llaves,llaves[1:]):
        if L <= l1:
            t=(L-l0)/(l1-l0) if l1>l0 else 0
            return tuple(int(c0[i]+(c1[i]-c0[i])*t) for i in range(3))
    return llaves[-1][1]

def blanco(L):
    v=min(255,int(L*1.18)+10); return (v,v,min(255,v+2))

def pinta(px, w, h, cx, cy, ang, r0, r1, modo, llaves, lume=None, omax=17, tramos=None):
    rad=math.radians(ang); ux,uy=math.cos(rad),math.sin(rad); nx,ny=-uy,ux
    bs0={}
    for r in range(r0,r1):
        cxp,cyp=cx+ux*r,cy+uy*r
        s=None
        for o in (0,1,-1,2,-2,3,-3,4,-4):
            x,y=int(round(cxp+nx*o)),int(round(cyp+ny*o))
            if 0<=x<w and 0<=y<h and lum(px[x,y])>65: s=o;break
        if s is None: continue
        izq=s
        while izq>-omax:
            x,y=int(round(cxp+nx*(izq-1))),int(round(cyp+ny*(izq-1)))
            if 0<=x<w and 0<=y<h and lum(px[x,y])>50: izq-=1
            else: break
        der=s
        while der<omax:
            x,y=int(round(cxp+nx*(der+1))),int(round(cyp+ny*(der+1)))
            if 0<=x<w and 0<=y<h and lum(px[x,y])>50: der+=1
            else: break
        if der-izq+1<=omax*2: bs0[r]=(izq,der)
    n=0
    for r in range(r0,r1):
        vec=[bs0[k] for k in range(r-5,r+6) if k in bs0]
        if len(vec)<3: continue
        izq=round(statistics.median(v[0] for v in vec)); der=round(statistics.median(v[1] for v in vec))
        cxp,cyp=cx+ux*r,cy+uy*r
        centro=(izq+der)/2; ancho=der-izq+1
        m=modo
        if tramos:
            for (t0,t1,mm) in tramos:
                if t0<=r<t1: m=mm; break
        for o in range(izq,der+1):
            x,y=int(round(cxp+nx*o)),int(round(cyp+ny*o))
            if not(0<=x<w and 0<=y<h): continue
            p=px[x,y]; L=lum(p)
            if lume and lume[0]<=r<=lume[1] and abs(o-centro)<=ancho*0.30: continue
            c=mapa(L,llaves) if m=='color' else blanco(L)
            px[x,y]=(c[0],c[1],c[2],p[3]); n+=1
    return n

if __name__ == '__main__':
    entrada, salida = sys.argv[1], sys.argv[2]
    im = Image.open(entrada).convert('RGBA')
    px = im.load(); w,h = im.size
    K = LLAVES_NARANJA
    total  = pinta(px,w,h, 628,587, 214.6, 40, 302, 'color', K, lume=(115,235))
    total += pinta(px,w,h, 628,587, 316.8, 40, 412, 'color', K, lume=(150,335))
    total += pinta(px,w,h, 628,587, 139.4, 30, 414, 'blanco', K, omax=16, tramos=[(30,300,'blanco'),(300,414,'color')])
    total += pinta(px,w,h, 395,590, 338.4, 10, 84, 'color', K, omax=8)
    total += pinta(px,w,h, 852,585, 53.2, 10, 84, 'color', K, omax=8)
    total += pinta(px,w,h, 622,800, 219.2, 10, 84, 'color', K, omax=8)
    im.save(salida)
    print(f'{total} pixeles recoloreados -> {salida}')
