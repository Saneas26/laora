#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alinea las cabezas del Lunar a UNA misma geometría: la del BISEL.

Cada cabeza salió de una generación distinta y no miden lo mismo: entre la
del bisel azul y la de la esfera racing hay 12 px de diámetro de bisel (un
2%). La versión anterior de este script las cuadraba por la SILUETA DE LA
CAJA con el canal alfa, y por eso seguían bailando: la pared de caja no
guarda la misma proporción con el bisel en todas las generaciones, así que
cuadrando la caja el bisel se descuadraba.

Ahora manda el bisel, que es lo único que se ve en el modo disco: de la
cabeza solo cae dentro la esfera con su bisel, y el corte tiene que caer
exactamente donde acaba el bisel de la foto.

Las cabezas de CAJA NEGRA no se pueden medir por el bisel —el filo de la
caja y el bisel son los dos negros y el detector no los distingue—, así que
se miden por el TAQUÍMETRO impreso, que sí se ve, y se les aplica la
proporción bisel/taquímetro de la cabeza de referencia.

La referencia es cab-acero-bnegro-agujas-plateadas, que es la cabeza que
salió de la foto de la piel perforada: no se toca, y todo lo demás va a
ella.

Uso: python3 herramientas/alinear_cabezas.py
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bisel_lunar import ARCOS, CENTRO, bisel_ext, sobre_fondo

HEADS = 'assets/img/lunar-config/heads'
MANIFEST = 'assets/img/lunar-config/manifest.json'
REF = 'cab-acero-bnegro-agujas-plateadas'


def taquimetro(ruta, r_ini):
    """Círculo del taquímetro impreso: el primer blanco entrando desde fuera."""
    im = Image.open(ruta).convert('RGBA')
    lum = np.asarray(im.convert('L')).astype(int)
    al = np.asarray(im.split()[3])
    cx, cy = CENTRO; P = []
    for lo, hi in ARCOS:
        for g in range(lo, hi + 1):
            t = math.radians(g); dx, dy = math.sin(t), -math.cos(t)
            r = r_ini - 3
            while r > 300:
                x, y = int(round(cx + dx * r)), int(round(cy + dy * r))
                if al[y, x] > 200 and lum[y, x] > 140:
                    P.append((cx + dx * r, cy + dy * r)); break
                r -= 0.5
    P = np.array(P, float)
    t = np.arctan2(P[:, 0] - cx, -(P[:, 1] - cy))
    r = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
    h, b = np.histogram(r, bins=np.arange(280, 400, 1.0))
    h = np.convolve(h, np.ones(5), 'same')
    m = np.abs(r - (b[int(h.argmax())] + .5)) < 5
    t, r = t[m], r[m]
    A = np.stack([np.ones(len(t)), np.sin(t), -np.cos(t)], 1)
    for _ in range(3):
        c = np.linalg.lstsq(A, r, rcond=None)[0]
        e = np.abs(A @ c - r); m = e < max(np.percentile(e, 85), 0.5)
        A, r = A[m], r[m]
    return cx + c[1], cy + c[2], c[0]


def geometria(ruta, ref_taq=None, negra=None):
    """Centro y radio del BORDE EXTERIOR DEL BISEL de esa cabeza.

    OJO con `negra`: se pasa a mano porque en las vueltas se mide un archivo
    temporal, y si se dedujera del nombre el temporal pasaría por cabeza de
    acero y devolvería la silueta en vez del bisel (una tanda perdida).
    """
    if negra is None: negra = os.path.basename(ruta).startswith('cab-negra-')
    bx, by, bR, err, n = bisel_ext(sobre_fondo(ruta))
    tx, ty, tR = taquimetro(ruta, bR)
    if not negra:
        return bx, by, bR, 'bisel'
    # Caja negra: del taquímetro, con la proporción de la referencia.
    k, dx, dy = ref_taq
    return tx + dx * tR, ty + dy * tR, tR * k, 'taquimetro'


if __name__ == '__main__':
    ref = os.path.join(HEADS, REF + '.webp')
    rx, ry, rR, _, _ = bisel_ext(sobre_fondo(ref))
    trx, tryy, trR = taquimetro(ref, rR)
    ref_taq = (rR / trR, (rx - trx) / trR, (ry - tryy) / trR)
    print('referencia %s: bisel (%.1f,%.1f) R=%.1f · taquímetro R=%.1f · razón %.4f'
          % (REF, rx, ry, rR, trR, ref_taq[0]))

    m = json.load(open(MANIFEST))
    for ruta in sorted(glob.glob(HEADS + '/*.webp')):
        k = os.path.basename(ruta)[:-5]
        if k == REF:
            print('%-46s referencia: no se toca' % k); continue
        im0 = Image.open(ruta).convert('RGBA')
        negra = k.startswith('cab-negra-')
        cx, cy, R, via = geometria(ruta, ref_taq, negra)
        esc = rR / R
        for vuelta in range(6):
            W, H = im0.size
            g = im0.resize((round(W * esc), round(H * esc)), Image.LANCZOS)
            out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            out.alpha_composite(g, (round(rx - cx * esc), round(ry - cy * esc)))
            tmp = 'herramientas/_tmp_cabeza.webp'
            out.save(tmp, quality=95)
            ax, ay, aR, _ = geometria(tmp, ref_taq, negra)
            os.remove(tmp)
            if abs(aR - rR) < 0.25 and abs(ax - rx) < 0.25 and abs(ay - ry) < 0.25: break
            esc *= rR / aR
            cx += (ax - rx) / esc; cy += (ay - ry) / esc
        out.save(ruta, quality=95)
        v = m['heads'].get(k, '')
        base = v.split('?v=')[0] if v else '/assets/img/lunar-config/heads/%s.webp' % k
        nv = int(v.split('?v=')[1]) + 1 if '?v=' in v else 2
        m['heads'][k] = '%s?v=%d' % (base, nv)
        print('%-46s por %-10s R %.1f → %.1f (objetivo %.1f) · escala %.4f · %d vueltas · v%d'
              % (k, via, R, aR, rR, esc, vuelta + 1, nv))
    json.dump(m, open(MANIFEST, 'w'), ensure_ascii=False, indent=1)
