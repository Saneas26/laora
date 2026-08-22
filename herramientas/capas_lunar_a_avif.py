#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Las capas del Lunar, en AVIF y en tres tamaños.

POR QUÉ. La norma de la casa (laora-formato-imagen-web, y el propio
foto_a_web.py) dice AVIF y tres tamaños con srcset. El Trinchera la
cumple; el Lunar se había quedado en webp de 1254 px a pelo, así que la
ficha entraba con 513 KB y cada toque en el configurador costaba otros
160 KB. Medido el 21/08/2026.

QUÉ HACE. Lee el manifiesto, y de cada capa —cabezas, correas, tapas y
hebillas— escribe tres AVIF en subcarpetas 480/800/1254 junto al
original. **No borra ni toca los webp**: siguen siendo el máster del que
se parte, y este guión se puede volver a pasar cuantas veces haga falta.

Los tamaños salen de dónde se ve cada cosa: el visor ocupa 46vw en
escritorio y toda la pantalla en el móvil (375 x 2 = 750), y las
miniaturas de tapa y hebilla, 140 px.

CUIDADO CON LA TRANSPARENCIA: las cabezas son RGBA y se montan encima de
la correa. foto_a_web.py hace .convert('RGB') y se las cargaría, por eso
este guión es aparte.

Uso:
    python3 herramientas/capas_lunar_a_avif.py            # todas
    python3 herramientas/capas_lunar_a_avif.py --solo heads
"""
import argparse, json, os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, 'assets/img/lunar-config')
MANIFIESTO = os.path.join(BASE, 'manifest.json')

TAMANOS = (480, 800, 1254)
CALIDAD = {480: 62, 800: 65, 1254: 68}
GRUPOS = ('heads', 'straps', 'tapas', 'hebillas')


def rutas_del_manifiesto():
    m = json.load(open(MANIFIESTO, encoding='utf-8'))
    out = []
    for grupo in GRUPOS:
        for clave, v in (m.get(grupo) or {}).items():
            src = v if isinstance(v, str) else v.get('src')
            if src:
                out.append((grupo, clave, src.split('?')[0].lstrip('/')))
    return out


def convertir(rel, hechos, saltados):
    origen = os.path.join(RAIZ, rel)
    if not os.path.exists(origen):
        print(f'   NO ESTÁ {rel}')
        return
    im = Image.open(origen)
    # RGBA solo si de verdad lleva transparencia: si no, el alfa engorda sin dar nada
    im = im.convert('RGBA') if (im.mode in ('RGBA', 'LA') or 'transparency' in im.info) else im.convert('RGB')
    carpeta, fichero = os.path.split(origen)
    nombre = os.path.splitext(fichero)[0] + '.avif'
    for t in TAMANOS:
        d = os.path.join(carpeta, str(t))
        os.makedirs(d, exist_ok=True)
        destino = os.path.join(d, nombre)
        # solo se rehace si el máster es más nuevo: así se puede repasar
        # cada vez que la otra mesa regenere un webp, sin recalcular todo
        if os.path.exists(destino) and os.path.getmtime(destino) >= os.path.getmtime(origen):
            saltados.append(destino)
            continue
        z = im if t == im.width else im.resize((t, round(im.height * t / im.width)), Image.LANCZOS)
        z.save(destino, quality=CALIDAD[t])
        hechos.append((destino, os.path.getsize(destino)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--solo', choices=GRUPOS, help='un solo grupo')
    a = ap.parse_args()
    rutas = [r for r in rutas_del_manifiesto() if not a.solo or r[0] == a.solo]
    hechos, saltados = [], []
    antes = 0
    for grupo, clave, rel in rutas:
        antes += os.path.getsize(os.path.join(RAIZ, rel)) if os.path.exists(os.path.join(RAIZ, rel)) else 0
        convertir(rel, hechos, saltados)
    despues = sum(t for _, t in hechos)
    print(f'capas leídas: {len(rutas)}  ·  escritas: {len(hechos)}  ·  ya estaban: {len(saltados)}')
    if hechos:
        print(f'los webp de origen suman {antes/1024/1024:.1f} MB')
        print(f'los AVIF nuevos suman     {despues/1024/1024:.1f} MB  (los tres tamaños juntos)')
        de1254 = sum(t for f, t in hechos if '/1254/' in f)
        de480 = sum(t for f, t in hechos if '/480/' in f)
        print(f'   solo los de 1254: {de1254/1024/1024:.1f} MB   ·   solo los de 480: {de480/1024:.0f} KB')


if __name__ == '__main__':
    main()
