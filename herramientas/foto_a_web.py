#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deja una foto lista para la web: AVIF en 480, 1200 y 1600.

La norma de la casa (laora-formato-imagen-web): el máster no se publica
nunca, y de cada foto se sirven tres tamaños con srcset para que el
móvil no se baje una imagen de escritorio. AVIF porque pesa la mitad
que el WEBP a la misma calidad.

Uso:
    python3 herramientas/foto_a_web.py montaje.png \
        assets/img/trinchera-2026/serie 39-acero-blanca-nato-verde
"""
import argparse, os
from PIL import Image

TAMANOS = (480, 1200, 1600)
CALIDAD = {480: 62, 1200: 66, 1600: 68}


def publicar(origen, carpeta, nombre):
    # EL ALFA SE CONSERVA (23/08/2026). Antes esto hacía convert('RGB') a
    # secas, y en un máster con fondo transparente los píxeles de fuera son
    # (0,0,0,0): al tirar el canal alfa el reloj salía recortado sobre NEGRO.
    # AVIF guarda transparencia, así que la foto se adapta al fondo de cada
    # sitio —#e9e9e7 en la ficha, #eae8e8 en colección— en vez de traerse
    # un cuadrado gris que no casa con ninguno de los dos.
    im = Image.open(origen)
    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
    hechos = []
    for t in TAMANOS:
        d = os.path.join(carpeta, str(t))
        os.makedirs(d, exist_ok=True)
        z = im.resize((t, int(im.height * t / im.width)), Image.LANCZOS)
        f = os.path.join(d, nombre + '.avif')
        z.save(f, quality=CALIDAD[t])
        hechos.append((f, os.path.getsize(f)))
    return hechos


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('origen'); p.add_argument('carpeta'); p.add_argument('nombre')
    a = p.parse_args()
    for f, n in publicar(a.origen, a.carpeta, a.nombre):
        print('%7.1f KB  %s' % (n / 1024, f))
