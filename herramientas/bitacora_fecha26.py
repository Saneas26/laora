# -*- coding: utf-8 -*-
"""Cambia el dia de la esfera: un digito (8) -> dos digitos (26).
Solo toca RGB dentro de la ventana; el alfa no se roza."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = 'despiece/despiece-bitacora/03-esfera-sin-agujas.png'
DST = 'base/03-esfera-base26.png'

# --- geometria de la ventana (medida sobre el original) ---
PLACA = dict(x0=2484, x1=2603, y0=1606, y1=1717)   # interior liso de la placa
DIG   = dict(x0=2506, x1=2583, y0=1621, y1=1708)   # el "8"
BORRA = dict(x0=2497, x1=2592, y0=1612, y1=1716)   # digito + su halo
CENTRO = ((DIG['x0']+DIG['x1'])/2, (DIG['y0']+DIG['y1'])/2)
ALTO_DIGITO = DIG['y1']-DIG['y0']+1                # 88 px de altura de cifra

def fondo_placa(rgb):
    """Reconstruye la placa: ajuste lineal en x fila a fila, con las columnas
    limpias de los dos lados del digito. La placa es un degradado suave."""
    ys = np.arange(PLACA['y0'], PLACA['y1']+1)
    colsL = np.arange(PLACA['x0'], DIG['x0']-8)
    colsR = np.arange(DIG['x1']+9, PLACA['x1']+1)
    cols = np.concatenate([colsL, colsR])
    xs_all = np.arange(PLACA['x0'], PLACA['x1']+1)
    fondo = np.zeros((len(ys), len(xs_all), 3), np.float32)
    for c in range(3):
        M = rgb[PLACA['y0']:PLACA['y1']+1, cols, c]          # (nfilas, ncols)
        A = np.vstack([cols.astype(np.float64), np.ones_like(cols, float)]).T
        coef, *_ = np.linalg.lstsq(A, M.T, rcond=None)        # (2, nfilas)
        # suavizado vertical de los coeficientes
        for k in range(2):
            v = coef[k]
            ker = np.ones(9)/9.0
            coef[k] = np.convolve(np.pad(v, 4, mode='edge'), ker, 'valid')
        fondo[:,:,c] = np.outer(np.ones(len(ys)), np.ones(len(xs_all)))*0
        fondo[:,:,c] = coef[0][:,None]*xs_all[None,:] + coef[1][:,None]
    return np.clip(fondo, 0, 255)

def mascara_digitos(texto='26'):
    """Dibuja el texto a 4x y lo devuelve como mascara float 0..1 del tamano
    del lienzo completo, centrada en el hueco del digito viejo."""
    S = 4
    fuente = '/System/Library/Fonts/Helvetica.ttc'
    # tamano tal que la altura de cifra sea ALTO_DIGITO
    px = 10
    for _ in range(60):
        f = ImageFont.truetype(fuente, px*S, index=1)   # index 1 = Bold
        bb = f.getbbox(texto)
        h = bb[3]-bb[1]
        if abs(h - ALTO_DIGITO*S) < 2: break
        px = px * (ALTO_DIGITO*S) / max(h,1)
        px = max(4, px)
    f = ImageFont.truetype(fuente, int(round(px*S)), index=1)
    bb = f.getbbox(texto)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    lienzo = Image.new('L', (w+40*S, h+40*S), 0)
    d = ImageDraw.Draw(lienzo)
    d.text((20*S-bb[0], 20*S-bb[1]), texto, fill=255, font=f)
    # ancho maximo permitido dentro de la placa
    max_w = (PLACA['x1']-PLACA['x0']+1) - 16
    esc_x = min(1.0, max_w*S / w)
    dest_w = int(round(lienzo.width*esc_x/S)); dest_h = int(round(lienzo.height/S))
    peq = lienzo.resize((dest_w, dest_h), Image.LANCZOS)
    m = np.array(peq).astype(np.float32)/255.0
    # posicion: centro del texto sobre el centro del 8
    tx = 20 - 0  # margen en px finales
    cx_local = (20*esc_x + w*esc_x/S/2)
    cy_local = (20 + h/S/2)
    ox = int(round(CENTRO[0] - cx_local))
    oy = int(round(CENTRO[1] - cy_local))
    full = np.zeros((4096,4096), np.float32)
    full[oy:oy+m.shape[0], ox:ox+m.shape[1]] = m
    return full

def main():
    im = Image.open(SRC).convert('RGBA')
    arr = np.array(im).astype(np.float32)
    rgb, alfa = arr[:,:,:3].copy(), arr[:,:,3].copy()

    # 1) borrar el 8 -> reponer la placa
    fondo = fondo_placa(rgb)
    y0,y1,x0,x1 = BORRA['y0'],BORRA['y1'],BORRA['x0'],BORRA['x1']
    peso = np.zeros((PLACA['y1']-PLACA['y0']+1, PLACA['x1']-PLACA['x0']+1), np.float32)
    peso[y0-PLACA['y0']:y1-PLACA['y0']+1, x0-PLACA['x0']:x1-PLACA['x0']+1] = 1.0
    peso = np.array(Image.fromarray((peso*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)/255.0
    sl = (slice(PLACA['y0'],PLACA['y1']+1), slice(PLACA['x0'],PLACA['x1']+1))
    rgb[sl] = rgb[sl]*(1-peso[...,None]) + fondo*peso[...,None]

    # 2) pintar "26"
    m = mascara_digitos('26')
    m = np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32)/255.0
    # sombra suave abajo-derecha
    som = np.roll(np.roll(m, 4, axis=0), 3, axis=1)
    som = np.array(Image.fromarray((som*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.5)), np.float32)/255.0
    tinta = np.array([22,21,23], np.float32)
    rgb = rgb*(1-0.28*som[...,None]) + (tinta*0.28*som[...,None])
    rgb = rgb*(1-m[...,None]) + tinta*m[...,None]

    out = np.concatenate([np.clip(rgb,0,255), alfa[...,None]], axis=2).astype(np.uint8)
    import os; os.makedirs('base', exist_ok=True)
    Image.fromarray(out, 'RGBA').save(DST)
    print('escrito', DST)

main()
