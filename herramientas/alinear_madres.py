#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alinea las imágenes madre de las correas del Lunar a la cabeza de referencia.

Cada madre es una FOTO COMPLETA —reloj con su correa— y de la cabeza solo
cae dentro el DISCO (esfera + bisel). Para que el disco no se note, el borde
exterior del bisel de la foto tiene que caer exactamente donde cae el de la
cabeza.

LA MEDIDA (`herramientas/_bisel_lunar.py`) va de FUERA A DENTRO: filo de la
caja contra el fondo y, desde ahí, el primer negro sostenido. La primera
versión iba al revés y medía cosas distintas según la foto —en unas el
bisel, en otras la silueta—, que es justo por lo que unas correas cuadraban
y otras no (Óscar, 22/08: «en nato solo está bien la marrón»).

DOS COSAS QUE COSTARON UNA TANDA CADA UNA:
1. Se parte SIEMPRE de la foto original de Óscar, no del webp ya alineado:
   encadenar reescalados emborrona y el error se acumula. Los originales se
   sacan del commit c0bf6d0 a herramientas/madres-origen/.
2. Un solo pase no basta: el remuestreo mueve el borde medido. Se itera
   midiendo el resultado hasta que el radio cae a menos de medio píxel, y
   solo entonces se guarda —una única codificación—.

El relleno que pueda quedar al recolocar lleva el gris del propio estudio de
esa foto, no un gris fijo: con #EAE8E8 sobre fotos de fondo 215 salía un
marco más claro alrededor del cuadro.

La piel perforada no se toca: es la foto de la que salió la cabeza. El
brazalete negro PVD es de caja negra —el detector normal se para en el filo
de la caja, que también es negro—, así que ese se mide por el chaflán
pulido y se corrige con la proporción medida en una foto de acero.

Uso:
    python3 herramientas/alinear_madres.py            # todas
    python3 herramientas/alinear_madres.py nato       # las que casen
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bisel_lunar import bisel_ext, bisel_chaflan, sobre_fondo

MANIFEST = 'assets/img/lunar-config/manifest.json'
CABEZA_REF = 'assets/img/lunar-config/heads/cab-acero-bnegro-agujas-plateadas.webp'
ORIGENES = 'herramientas/madres-origen'      # las fotos de Óscar, sin tocar
COMMIT_ORIGEN = 'c0bf6d0'
NO_TOCAR = {'piel-negra-perforada-pespunte-blanco'}   # es la foto de la que salió la cabeza
POR_CHAFLAN = {'brazalete-negro-pvd'}                # caja negra: se mide por el chaflán
REF_CHAFLAN = 'nato-espiga-gris'                     # foto de acero donde se miden las dos cosas


def origen(k):
    """La foto original de la correa, sacada del repo la primera vez."""
    ruta = os.path.join(ORIGENES, k + '.webp')
    if not os.path.exists(ruta):
        os.makedirs(ORIGENES, exist_ok=True)
        blob = subprocess.check_output(
            ['git', 'show', '%s:assets/img/lunar-config/straps/%s.webp' % (COMMIT_ORIGEN, k)])
        open(ruta, 'wb').write(blob)
    return Image.open(ruta)


def gris_de_estudio(im):
    """El gris del fondo de ESA foto, del marco de 6 px de fuera."""
    a = np.asarray(im.convert('RGB')).astype(int)
    # Solo los costados: la correa cruza la foto de arriba abajo y sale por
    # el borde superior e inferior, así que arriba y abajo NO son fondo.
    borde = np.concatenate([a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    return tuple(int(round(v)) for v in borde.mean(axis=0))


def coloca(im, cx, cy, k, rx, ry, fondo):
    W, H = im.size
    g = im.convert('RGB').resize((round(W * k), round(H * k)), Image.LANCZOS)
    out = Image.new('RGB', (W, H), fondo)
    out.paste(g, (round(rx - cx * k), round(ry - cy * k)))
    return out


if __name__ == '__main__':
    filtros = sys.argv[1:]
    m = json.load(open(MANIFEST))
    rx, ry, rR, err, n = bisel_ext(sobre_fondo(CABEZA_REF))
    ref = origen(REF_CHAFLAN)
    k_chaflan = bisel_ext(ref)[2] / bisel_chaflan(ref)[2]
    print('cabeza de referencia: bisel centro=(%.1f,%.1f) R=%.1f (err %.2f, %d puntos)' % (rx, ry, rR, err, n))
    print('chaflán → bisel: ×%.4f (medido en %s)' % (k_chaflan, REF_CHAFLAN))

    def mide(im, chaflan):
        if not chaflan: return bisel_ext(im)
        x, y, R, e, n = bisel_chaflan(im)
        return x, y, R * k_chaflan, e, n

    for k, st in m['straps'].items():
        if filtros and not any(f in k for f in filtros): continue
        if k in NO_TOCAR:
            print('%-38s no se toca' % k); continue
        im0 = origen(k)
        fondo = gris_de_estudio(im0)
        chaflan = k in POR_CHAFLAN
        mx, my, mR, merr, mn = mide(im0, chaflan)
        if mn < 18 or merr > 3:
            print('%-38s bisel dudoso (err %.2f, %d puntos): NO se toca' % (k, merr, mn)); continue
        # Se itera sobre la ORIGINAL: cada vuelta corrige el resto que deja
        # el remuestreo, y solo se guarda la última.
        esc, cx, cy = rR / mR, mx, my
        for vuelta in range(6):
            out = coloca(im0, cx, cy, esc, rx, ry, fondo)
            ax, ay, aR, aerr, an = mide(out, chaflan)
            if abs(aR - rR) < 0.25 and abs(ax - rx) < 0.25 and abs(ay - ry) < 0.25: break
            esc *= rR / aR
            cx += (ax - rx) / esc; cy += (ay - ry) / esc
        ruta = '.' + st['src'].split('?')[0]
        out.save(ruta, quality=92)
        ver = st['src'].split('?v='); v = int(ver[1]) + 1 if len(ver) > 1 else 2
        st['src'] = ver[0] + '?v=%d' % v
        st['alineada'] = ('22/08/2026 (2.ª tanda): desde la foto original, midiendo el bisel de FUERA A DENTRO. '
                          'Era (%.0f,%.0f) R=%.1f → escala %.4f; queda en (%.1f,%.1f) R=%.1f '
                          'contra la cabeza (%.1f,%.1f) R=%.1f' % (mx, my, mR, esc, ax, ay, aR, rx, ry, rR))
        print('%-38s R %.1f → %.1f (objetivo %.1f) · escala %.4f · %d vueltas · v%d · fondo %s'
              % (k, mR, aR, rR, esc, vuelta + 1, v, fondo))
    json.dump(m, open(MANIFEST, 'w'), ensure_ascii=False, indent=1)
