# -*- coding: utf-8 -*-
"""Deja listas las esferas nuevas de la Bitácora para el montaje.

    python3 herramientas/esferas_bitacora.py [--prueba]

Óscar, 01/09/2026: «cambia las esferas del bitacora por estas». La entrega
del 01/09 —`Codex/2026-09-01/esferas-bitacora-simplemente-a-esta-esfera/
outputs/4k-transparent/`— trae cinco esferas mucho mejores que las de
agosto: índices aplicados con relieve, doble batón a las 12, pista de
minutos punteada, marco de fecha en relieve y el rótulo AUTOMATIC.

Pero NO se pueden montar tal cual, por tres cosas que se miden:

  1. **NI EL MISMO TAMAÑO NI EL MISMO CENTRO.** Los radios van de 1.860 a
     1.928 px (un 3,7 % de diferencia) y el eje baila hasta 80 px de una a
     otra. Apiladas así, al cambiar de color el reloj daba un salto: es lo
     mismo que pasó con las once cajas del Tortuga.

  2. **LA BLANCA NO ES UN CÍRCULO, ES UN POLÍGONO.** Su borde ondula un
     16,7 % —de 1.826 a 2.152 px de radio— y encima trae en una esquina un
     trozo del damero de transparencia sin quitar. Las otras cuatro son
     círculos limpios (0,3 % de ondulación).

  3. **EL EJE VIENE AGUJEREADO.** Donde va el cañón de las agujas hay un
     hueco transparente de unos 270 px. Hoy lo tapa el buje de las agujas
     —que llega a 32 px de un radio de 302 en la capa publicada, y el
     agujero se queda en 22—, pero es un agujero esperando a que alguien
     cambie las agujas.

QUÉ SE HACE, y por qué así:

  · **EL EJE SE SACA DEL AGUJERO DEL CAÑÓN, no del contorno.** El contorno
    no vale: el disco está dibujado descentrado respecto del dibujo, y de
    una esfera a otra el desfase entre los dos cambia de 15 a 81 px. El
    agujero del cañón, en cambio, ES el eje del reloj por definición.
  · **EL BORDE SE REHACE REDONDO**, con el radio mediano de esa esfera.
    Lo que sobra se recorta —ahí se va el damero de la blanca— y donde
    falta se estira el color del borde hacia fuera. Es una franja lisa que
    además acaba debajo del bisel, así que no se inventa dibujo: se
    prolonga el mismo color un par de píxeles.
  · **EL AGUJERO SE TAPA** con el color de alrededor. No se ve nunca —el
    buje se le pone encima— pero deja de ser una trampa.
  · Y las cinco salen a **1.280 px con el radio en 570 y el eje en el
    centro**, que es exactamente como venían las de agosto: así
    `capas_bitacora.py` las monta sin cambiar una línea.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTREGA = ('/Users/oscar/Documents/Codex/2026-09-01/'
           'esferas-bitacora-simplemente-a-esta-esfera/outputs/4k-transparent/')
DESTINO = os.path.join(ENTREGA, 'preparadas')

LIENZO = 1280          # el de las esferas de agosto
RADIO = 570.0          # y su radio, para que el montaje no se entere del cambio
SECTORES = 720

ESFERAS = {
    'bitacora-esfera-turquesa-26.png': 'esfera-bitacora-turquesa-26-4k.png',
    'bitacora-esfera-blanca-26.png':   'esfera-bitacora-blanca-26-4k.png',
    'bitacora-esfera-negra-26.png':    'esfera-bitacora-negra-26-4k.png',
    'bitacora-esfera-azul-26.png':     'esfera-bitacora-azul-26-4k.png',
    'bitacora-esfera-cobre-26.png':    'esfera-bitacora-cobre-26-4k.png',
}


def el_eje(al):
    """El centro del agujero del cañón: el eje del reloj.

    ⚠️ NO SIRVE EL CENTRO DEL CONTORNO. El disco viene dibujado descentrado
    respecto del dibujo, y además cada esfera lo trae descentrado de una
    manera: de 15 a 81 px. Alineando por el contorno, los índices y la
    ventana de la fecha bailaban al cambiar de color."""
    hueco = ndimage.binary_fill_holes(al) & ~al
    lab, n = ndimage.label(hueco)
    if not n:
        raise SystemExit('esta esfera no trae el agujero del cañón')
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    m = lab == 1 + int(np.argmax(t))
    ys, xs = np.where(m)
    return (float(xs.mean()), float(ys.mean())), m


def el_radio(al, eje):
    """El radio mediano del borde, mirado por sectores.

    Por la MEDIANA y no por el máximo ni el mínimo: la blanca ondula de
    1.826 a 2.152 y cualquiera de los dos extremos la dejaría de otro
    tamaño que las demás."""
    borde = al & ~ndimage.binary_erosion(al)
    ys, xs = np.where(borde)
    ang = np.arctan2(ys - eje[1], xs - eje[0])
    rad = np.hypot(xs - eje[0], ys - eje[1])
    k = np.clip(((ang + np.pi) / (2 * np.pi) * SECTORES).astype(int), 0, SECTORES - 1)
    r = np.full(SECTORES, np.nan)
    for i in range(SECTORES):
        s = k == i
        if s.any():
            r[i] = rad[s].max()
    r = r[~np.isnan(r)]
    return float(np.median(r)), float(r.min()), float(r.max())


def redonda(a, eje, radio, hueco):
    """Borde redondo de verdad, agujero tapado y nada fuera del disco."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx - eje[0], yy - eje[1])
    dentro = d <= radio
    # el color: lo que ya es opaco y no es el agujero
    bueno = (a[:, :, 3] > 200) & ~hueco
    rgb = a[:, :, :3].copy()

    # EL FILO CORTO se estira hacia fuera: se copia del píxel bueno más
    # cercano, que en una franja de dos píxeles es el de justo dentro.
    corto = dentro & ~bueno & ~hueco
    if corto.any():
        cerca = ndimage.distance_transform_edt(~bueno, return_distances=False,
                                               return_indices=True)
        rgb[corto] = a[:, :, :3][cerca[0], cerca[1]][corto]

    # ⚠️ EL AGUJERO DEL CAÑÓN SE TAPA SIGUIENDO LAS RAYAS, fila por fila.
    # Y AHORA SE VE: hasta el 01/09 lo tapaba el buje de las agujas, pero
    # Óscar las quitó («quita las agujas»), así que el centro de la esfera
    # queda a la vista y el parche tiene que ser invisible.
    # Los otros dos rellenos que se probaron NO valen: por vecino más
    # cercano sale un borrón con forma de cometa, y copiando lo que hay en
    # el mismo ángulo justo fuera salen RAYOS, porque lo que rodea al cañón
    # es su propia sombra circular y proyectarla hacia dentro la convierte
    # en un abanico. La esfera de la Bitácora está rayada EN HORIZONTAL, así
    # que cruzando cada fila de un lado al otro del agujero las rayas
    # siguen su camino y el parche desaparece.
    if hueco.any():
        # ⚠️ Y SE COSE UN POCO MÁS ANCHO QUE EL AGUJERO. Alrededor del
        # cañón, el dibujo lleva su sombra; cosiendo sólo lo transparente,
        # esa sombra se quedaba dando la vuelta al parche y lo que se veía
        # era un anillo oscuro con una cúpula clara dentro. Cuarenta
        # píxeles se la llevan por delante.
        rgb = _cose_las_rayas(rgb, ndimage.binary_dilation(hueco, iterations=40))
    # alfa: disco con el filo suavizado un píxel
    alfa = np.clip(radio + 0.5 - d, 0, 1) * 255.0
    return np.dstack([rgb, alfa]).astype(np.uint8)


def _cose_las_rayas(rgb, hueco):
    """Cruza cada fila del agujero del color que tiene a los dos lados.

    Fila a fila: se coge el último píxel bueno de la izquierda y el primero
    de la derecha y se pasa de uno a otro. Es una interpolación de nada,
    pero como la esfera está rayada en horizontal cada raya se reengancha
    con la suya y no hay manera de ver por dónde iba el agujero."""
    ys = np.where(hueco.any(1))[0]
    fuera = rgb.astype(np.float32)
    for y in ys:
        xs = np.where(hueco[y])[0]
        i, j = int(xs.min()), int(xs.max())
        if i == 0 or j >= rgb.shape[1] - 1:
            continue
        izq = fuera[y, i - 1]
        der = fuera[y, j + 1]
        t = np.linspace(0.0, 1.0, j - i + 3)[1:-1][:, None]
        fuera[y, i:j + 1] = izq * (1 - t) + der * t
    return np.clip(fuera, 0, 255).astype(rgb.dtype)


def prepara(f):
    a = np.asarray(Image.open(ENTREGA + f).convert('RGBA'))
    al = a[:, :, 3] > 128
    eje, hueco = el_eje(al)
    r, rmin, rmax = el_radio(al, eje)
    limpia = Image.fromarray(redonda(a, eje, r, hueco), 'RGBA')
    # a 1.280 con el radio en 570 y el eje en el centro
    s = RADIO / r
    n = limpia.resize((max(1, round(limpia.width * s)), max(1, round(limpia.height * s))),
                      Image.LANCZOS)
    L = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    L.alpha_composite(n, (round(LIENZO / 2.0 - 0.5 - eje[0] * s),
                          round(LIENZO / 2.0 - 0.5 - eje[1] * s)))
    return L, eje, r, rmin, rmax, int(hueco.sum())


def main():
    prueba = '--prueba' in sys.argv
    if not prueba:
        os.makedirs(DESTINO, exist_ok=True)
    hoja = Image.new('RGB', (len(ESFERAS) * 300 + 20, 320), (233, 233, 231))
    for i, (salida, f) in enumerate(sorted(ESFERAS.items())):
        im, eje, r, rmin, rmax, ag = prepara(f)
        if not prueba:
            im.save(os.path.join(DESTINO, salida))
        L = Image.new('RGBA', im.size, (233, 233, 231, 255))
        L.alpha_composite(im)
        hoja.paste(L.convert('RGB').resize((290, 290), Image.LANCZOS), (10 + i * 300, 15))
        print('%-34s eje %7.1f,%7.1f · radio %.0f (de %.0f a %.0f, ondula %.1f %%) · '
              'cañón %d px' % (salida, eje[0], eje[1], r, rmin, rmax,
                               100 * (rmax - rmin) / r, ag))
    d = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'bitacora-esferas.png') if prueba
         else os.path.join(RAIZ, 'herramientas/capturas/bitacora-esferas.png'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    hoja.save(d)
    print('\nhoja de control: ' + d)
    if not prueba:
        print('escritas en ' + DESTINO)


if __name__ == '__main__':
    main()
