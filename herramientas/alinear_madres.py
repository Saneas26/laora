#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alinea las imágenes madre de las correas del Lunar a la cabeza de referencia.

Cada madre es una foto completa —reloj con su correa— sobre la que se
monta la cabeza elegida. Si la caja de la foto no cae donde cae la
cabeza, se pisan: asas dobles, bisel que asoma, esfera descentrada.
Óscar lo vio en los natos el 21/08/2026; medido, las madres venían hasta
un 10 % más pequeñas y 10-30 px corridas respecto a la cabeza.

LA MEDIDA es el anillo de cifras del taquímetro, por VOTACIÓN de círculo:
se toman los píxeles claros rodeados de negro (las cifras; la caja de
acero es clara rodeada de claro y queda fuera) y se busca el centro y
radio que más de ellos tienen a la misma distancia. Un borde o un
ajuste por mínimos cuadrados se dejaban engañar por la correa y los
brillos; la votación no. La madre se escala y se mueve para que su
anillo caiga sobre el de la cabeza. El dibujo no se toca.

La piel perforada no se toca: es la foto de la que salió la cabeza.

Uso:
    python3 herramientas/alinear_madres.py            # todas
    python3 herramientas/alinear_madres.py nato       # las que casen
"""
import json, sys
import numpy as np
from PIL import Image, ImageFilter

MANIFEST = 'assets/img/lunar-config/manifest.json'
CABEZA_REF = 'assets/img/lunar-config/heads/cab-acero-bnegro-agujas-plateadas.webp'
FONDO = (234, 232, 232)
NO_TOCAR = {'piel-negra-perforada-pespunte-blanco'}
VOTOS_MIN = 800


def cifras(im, c0=(627, 561), R0=262, R1=340):
    a = np.asarray(im.convert('RGB')).astype(float); lum = a.mean(axis=2); H, W = lum.shape
    osc = Image.fromarray(((lum < 85) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(7))
    vec = np.asarray(osc).astype(float) / 255
    yy, xx = np.mgrid[0:H, 0:W]; r0 = np.hypot(xx - c0[0], yy - c0[1])
    return np.where((lum > 185) & (vec > 0.45) & (r0 > R0 - 50) & (r0 < R1 + 50))


def voto(im, R0=262, R1=340, c0=(627, 561), rango=60, paso=2):
    ys, xs = cifras(im, c0, R0, R1); xs = xs.astype(float); ys = ys.astype(float)
    def mejor_en(cxs, cys, m):
        for cy in cys:
            for cx in cxs:
                d = np.hypot(xs - cx, ys - cy)
                h, _ = np.histogram(d, bins=np.arange(R0 - 0.5, R1 + 1.5, 1.0)); h3 = h[:-2] + h[1:-1] + h[2:]
                i = h3.argmax()
                if m is None or h3[i] > m[0]: m = (int(h3[i]), cx, cy, R0 + i + 1)
        return m
    m = mejor_en(range(c0[0] - rango, c0[0] + rango + 1, paso), range(c0[1] - rango, c0[1] + rango + 1, paso), None)
    m = mejor_en(range(m[1] - 2, m[1] + 3), range(m[2] - 2, m[2] + 3), m)
    return m  # votos, cx, cy, R


def referencia():
    ref = Image.open(CABEZA_REF).convert('RGBA')
    bg = Image.new('RGBA', ref.size, FONDO + (255,)); bg.alpha_composite(ref)
    return voto(bg)


def alinear(im, med, ref, k_extra=1.0):
    _, cx, cy, R = med; _, rx, ry, rR = ref
    k = rR / R * k_extra; W, H = im.size
    g = im.convert('RGB').resize((round(W * k), round(H * k)), Image.LANCZOS)
    out = Image.new('RGB', (W, H), FONDO); out.paste(g, (round(rx - cx * k), round(ry - cy * k)))
    return out, k


_REF_L = None
def acuerdo(out, ref):
    """Cuánto coincide la madre alineada con la cabeza en la corona del
    taquímetro: correlación de luminancia entre r=290 y r=350 de la
    cabeza. Una madre bien alineada da 0,6 o más; si la votación pilló
    otro anillo —los índices de la esfera, por ejemplo— baja de 0,3."""
    global _REF_L
    if _REF_L is None:
        ref_im = Image.open(CABEZA_REF).convert('RGBA')
        bg = Image.new('RGBA', ref_im.size, FONDO + (255,)); bg.alpha_composite(ref_im)
        _REF_L = np.asarray(bg.convert('L')).astype(float)
    H, W = _REF_L.shape; yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - ref[1], yy - ref[2]); m = (r > 290) & (r < 350)
    a = _REF_L[m] - _REF_L[m].mean(); b = np.asarray(out.convert('L')).astype(float)[m]; b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-9))


if __name__ == '__main__':
    filtros = sys.argv[1:]
    m = json.load(open(MANIFEST)); ref = referencia()
    print('cabeza de referencia: centro=(%d,%d) R=%d (%d votos)' % (ref[1], ref[2], ref[3], ref[0]))
    for k, st in m['straps'].items():
        if filtros and not any(f in k for f in filtros): continue
        if k in NO_TOCAR: print('%-36s es la foto de la cabeza: no se toca' % k); continue
        ruta = '.' + st['src'].split('?')[0]
        im = Image.open(ruta); med = voto(im)
        if med[0] < VOTOS_MIN:
            print('%-36s medida dudosa (%d votos): NO se toca, revisar a ojo' % (k, med[0])); continue
        out, esc = alinear(im, med, ref); ac = acuerdo(out, ref)
        if ac < 0.45:
            # la votación pudo coger otro anillo: se busca más lejos y más grande
            med_b = voto(im, R0=240, R1=420, rango=110, paso=3)
            out_b, esc_b = alinear(im, med_b, ref); ac_b = acuerdo(out_b, ref)
            print('   %s: acuerdo %.2f con el anillo corto; con rango amplio %.2f' % (k, ac, ac_b))
            if ac_b > ac: out, esc, med, ac = out_b, esc_b, med_b, ac_b
        if ac < 0.45:
            print('%-36s NO SE TOCA: no hay acuerdo con la cabeza (%.2f), revisar a mano' % (k, ac)); continue
        out.save(ruta, quality=90)
        med2 = voto(Image.open(ruta))
        ver = st['src'].split('?v='); v = int(ver[1]) + 1 if len(ver) > 1 else 2
        st['src'] = ver[0] + '?v=%d' % v
        print('%-36s escala %.3f · ahora (%d,%d) R=%d · acuerdo %.2f · v%d'
              % (k, esc, med2[1], med2[2], med2[3], ac, v))
    json.dump(m, open(MANIFEST, 'w'), ensure_ascii=False, indent=1)
