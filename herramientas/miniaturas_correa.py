# -*- coding: utf-8 -*-
"""Recorta las fotos de la correa profesional y las publica como miniatura.

    python3 herramientas/miniaturas_correa.py [--prueba]

Óscar, 01/09/2026: «cuando pulsa el cliente caucho profesional colocamos
esta miniatura en la parte derecha inferior de la imagen grande, en
vertical sin fondo», y «esta correa puede elegirse con pasadores plata o
pasadores negros».

Son fotos de la correa de verdad, no dibujos: por eso van de miniatura y
no de capa. La capa es el reloj montado; esto es el detalle que el reloj
no puede enseñar, porque el pasador cae a diez centímetros de la caja y
en el visor no se ve ni uno.

CÓMO SE LES QUITA EL FONDO. Las dos vienen sobre blanco de estudio, así
que el alfa sale del propio blanco: 250 arriba es fondo, 200 abajo es
correa, y en medio una rampa que da el borde suavizado. Dos cuidados:

  · SE LIMPIA POR TROZOS, no por umbral suelto. Con el umbral a secas se
    colaba el marco de la foto —la compresión oscurece la última fila— y
    la sombra del suelo. Se quedan sólo los trozos grandes, que son la
    correa y su rabo.
  · Y SE LE QUITA EL VELO BLANCO. El borde llega mezclado con el fondo;
    publicándolo tal cual, sobre el crema de la ficha se ve un halo claro
    alrededor de la correa. Se deshace la mezcla: color = (lo que hay −
    blanco × (1 − alfa)) ÷ alfa.

VAN EN VERTICAL, que es como las pidió, y NO con un cuarto de vuelta
fijo: la de los pasadores negros llega tumbada y la de los plata llega en
diagonal, así que girando las dos noventa grados una quedaba de pie y la
otra se tumbaba. Se le mide a la correa su eje largo y se gira lo que haga
falta para ponerlo vertical. Y para decidir de qué lado queda arriba, la
HEBILLA VA ABAJO: es lo más brillante de la foto, así que se encuentra
sola y no hay que escribir «ésta al revés».

⚠️ LA DE LOS PASADORES DE PLATA ES DE 220 px, la única que hay: al lado
de la de los negros —679 px— se nota que son dos fotos distintas, en otra
pose y con el rabo curvado. Óscar lo sabe y la quiso así, sin retocar.
"""
import io as _io
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = '/Users/oscar/Documents/Codex/2026-09-01/tortuga-correa-profesional/'
DESTINO = os.path.join(RAIZ, 'assets/img/tortuga-2026/miniaturas')
ALTO = 900               # lo que se publica; en la ficha se ve a un cuarto
PESO = 40000
CALIDADES = (80, 72, 64, 56, 48)

FONDO_LIMPIO = 250.0     # de aquí para arriba es fondo de estudio
CORREA = 200.0           # de aquí para abajo es correa segura
TROZO = 1500             # lo que tiene que medir un trozo para no ser basura

MINIS = {
    'pasadores-negros': '01-correa-profesional-pasadores-negros.jpg',
    'pasadores-plata':  '02-correa-profesional-pasadores-plata.png',
}


def sin_fondo(f):
    a = np.asarray(Image.open(FOTOS + f).convert('RGB')).astype(np.float32)
    gris = a.mean(2)
    nucleo = ndimage.binary_fill_holes(
        ndimage.binary_closing(gris < CORREA, np.ones((5, 5))))
    lab, n = ndimage.label(nucleo)
    t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    nucleo = np.isin(lab, [1 + i for i, v in enumerate(t) if v > TROZO])
    cerca = ndimage.binary_dilation(nucleo, iterations=6)

    alfa = np.clip((FONDO_LIMPIO - gris) / (FONDO_LIMPIO - CORREA), 0, 1)
    alfa[~cerca] = 0
    alfa[nucleo] = 1.0

    # ⚠️ Y SE LE COME UN PÍXEL AL BORDE. Deshacer la mezcla con el blanco
    # es una división por el alfa, y donde el alfa es casi cero cualquier
    # ruido de compresión sale disparado: la de 220 px quedaba con un
    # festón claro alrededor, que sobre el crema de la ficha se ve como un
    # halo. Un mínimo de 3×3 tira esa fila de borde y deja el filo limpio.
    alfa = ndimage.minimum_filter(alfa, size=3)
    con = alfa[:, :, None]
    rgb = np.clip(np.where(con > 0.15, (a - 255.0 * (1 - con)) / np.maximum(con, 1e-3), a),
                  0, 255)
    im = Image.fromarray(np.dstack([rgb, alfa * 255]).astype('uint8'), 'RGBA')
    ys, xs = np.where(alfa > 0.05)
    im = de_pie(im)
    return im.resize((max(1, round(im.width * ALTO / im.height)), ALTO), Image.LANCZOS)


def de_pie(im):
    """Pone la correa vertical, con la hebilla abajo.

    ⚠️ NO SE DEDUCE EL ÁNGULO, SE BUSCA. Sacarlo de la matriz de
    covarianza parecía lo elegante y da un número que hay que interpretar
    —el eje no tiene sentido, así que sobran ciento ochenta grados y el
    signo depende de que la `y` de una imagen crece hacia abajo—; dos
    intentos salieron tumbados. Aquí se prueban los ciento ochenta grados
    sobre las COORDENADAS —no sobre la imagen, que sería lento— y se
    escoge el que deja la correa más estrecha, que es exactamente lo que
    quiere decir «de pie».

    ⚠️ Y SE MIDE EL TROZO MÁS GRANDE, no la mancha entera. La foto de los
    pasadores negros trae la correa partida en dos tiras, una más arriba
    que la otra: midiendo las dos juntas, lo más estrecho es ponerlas en
    columna, y cada tira se queda atravesada.

    De qué lado queda arriba lo decide la HEBILLA, que va abajo: es lo más
    claro de una foto que por lo demás es caucho negro, así que se
    encuentra sola y no hay que escribir «ésta al revés»."""
    a = np.asarray(im)
    m = a[:, :, 3] > 128
    lab, n = ndimage.label(m)
    if n > 1:
        t = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        m = lab == 1 + int(np.argmax(t))
    # SE GIRA DE VERDAD Y SE MIDE. Con las coordenadas a mano hay que
    # acertar con el signo —la `y` de una imagen crece hacia abajo, así que
    # el giro de la pantalla es el contrario del de la trigonometría— y ya
    # se falló dos veces. Girar la máscara de verdad no deja lugar a duda,
    # y una máscara de trescientos mil píxeles se gira en un suspiro.
    solo = Image.fromarray((m * 255).astype('uint8'))
    def estrecha(t):
        r = np.asarray(solo.rotate(t, expand=True)) > 128
        c = np.where(r.any(0))[0]
        return int(c.max() - c.min() + 1)
    grueso = min(range(0, 180, 2), key=estrecha)
    giro = float(min(np.arange(grueso - 2, grueso + 2, 0.25), key=estrecha))
    im = im.rotate(giro, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))

    # ⚠️ QUÉ EXTREMO VA ARRIBA LO DICE EL AMARILLO DE LA TABLA, no el
    # brillo. Con «lo más claro abajo» la hebilla competía con el rótulo
    # blanco impreso —que también es claro y está en el otro extremo—, y
    # bastaba tocar el borde un píxel para que la miniatura saliera del
    # revés. El amarillo de la columna «ND TIME» no lo tiene nada más en
    # toda la foto: donde está el amarillo está la tabla, y la tabla va
    # arriba.
    a = np.asarray(im).astype(int)
    m = a[:, :, 3] > 128
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    amarillo = m & (r > 110) & (g > 80) & (b < g * 0.75)
    if amarillo.sum() > 30 and np.where(amarillo)[0].mean() > np.where(m)[0].mean():
        im = im.rotate(180, expand=True)      # la tabla había quedado abajo
    a = np.asarray(im)
    ys, xs = np.where(a[:, :, 3] > 8)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def guarda(im, ident):
    os.makedirs(DESTINO, exist_ok=True)
    for q in CALIDADES:
        b = _io.BytesIO()
        im.save(b, 'AVIF', quality=q)
        d = b.getvalue()
        if len(d) <= PESO or q == CALIDADES[-1]:
            break
    open(os.path.join(DESTINO, ident + '.avif'), 'wb').write(d)
    return len(d)


def main():
    prueba = '--prueba' in sys.argv
    hoja = Image.new('RGB', (len(MINIS) * 320, 460), (233, 233, 231))
    for i, (ident, f) in enumerate(sorted(MINIS.items())):
        im = sin_fondo(f)
        L = Image.new('RGBA', im.size, (233, 233, 231, 255))
        L.alpha_composite(im)
        hoja.paste(L.convert('RGB').resize((round(im.width * 440.0 / ALTO), 440)),
                   (i * 320 + 20, 10))
        print('%-20s %-52s %4dx%d' % (ident, f, im.width, im.height), end='')
        print('' if prueba else '  %6d B' % guarda(im, ident))
    d = (os.path.join(os.environ.get('TMPDIR', '/tmp'), 'tortuga-miniaturas.png') if prueba
         else os.path.join(RAIZ, 'herramientas/capturas/tortuga-miniaturas.png'))
    os.makedirs(os.path.dirname(d), exist_ok=True)
    hoja.save(d)
    print('hoja de control: ' + d)


if __name__ == '__main__':
    main()
