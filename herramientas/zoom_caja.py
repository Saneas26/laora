"""Acerca la foto hasta que la CAJA mida lo mismo que en las demás.
Óscar, 11/08/2026: en las pieles antiguas el reloj salía pequeño y se
veía la hebilla. Se escala alrededor del centro de la caja y se recorta
al lienzo de 2000×2000: lo que sobra de correa —y la hebilla— se va."""
from PIL import Image
import subprocess, sys, os

LIENZO, OBJETIVO = 2000, 1080

def caja_de(im):
    a = im.split()[-1]
    filas = []
    for y in range(im.height):
        f = a.crop((0, y, im.width, y + 1)).getbbox()
        filas.append((f[2] - f[0], y) if f else (0, y))
    ancho = max(f[0] for f in filas)
    ys = [y for w, y in filas if w > ancho * 0.80]
    xs = a.getbbox()
    return ancho, (ys[0] + ys[-1]) // 2, (xs[0] + xs[2]) // 2

def zoom(ruta):
    subprocess.run(['dwebp', ruta, '-o', '/tmp/_z.png'], capture_output=True)
    im = Image.open('/tmp/_z.png').convert('RGBA')
    ancho, cy, cx = caja_de(im)
    if ancho >= OBJETIVO * 0.95:
        return None
    k = OBJETIVO / ancho
    im2 = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    cx2, cy2 = int(cx * k), int(cy * k)
    lienzo = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    lienzo.paste(im2, (LIENZO // 2 - cx2, LIENZO // 2 - cy2))
    salida = '/tmp/_zoom.png'
    lienzo.save(salida)
    return ancho, k, salida

if __name__ == '__main__':
    D = '/Users/oscar/Sites/laora/assets/img/piezas/completas/'
    for f in sys.argv[1:]:
        r = zoom(D + f)
        if not r:
            print(f'{f}: ya está bien'); continue
        antes, k, png = r
        subprocess.run(['cwebp', '-q', '88', '-alpha_q', '100', png, '-o', D + f], capture_output=True)
        print(f'{f}: caja {antes} → {OBJETIVO} px  (×{k:.2f})')
