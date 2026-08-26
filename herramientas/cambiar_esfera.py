#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cambia la esfera de una foto del Trinchera por otra, sin rehacer la foto.

LA IDEA ES DE ÓSCAR (26/08/2026): «utilizar los modelos que ya tenemos con la
posibilidad de elegir esferas solo para el khaki (…) en lugar de volver a hacer
todas las fotos, tan solo colocar minuciosamente la esfera cuadrando eje de la
esfera con la caja en el mismo tamaño adaptándolo para que encaje perfecta».

Y encaja porque las fotos son FRONTALES: la esfera es un círculo, no una
elipse, así que basta con el centro y el radio. Nada de perspectiva.

CÓMO ENCUENTRA EL HUECO. No se le dicen las coordenadas: se buscan. Se prueban
centros alrededor del centro de la caja y se mide, para cada uno, cómo cae la
proporción de píxeles oscuros al salir del centro. El centro BUENO es el que
hace esa caída más brusca: si está desviado, unos rayos cruzan el borde antes
que otros y la transición se emborrona. El radio es donde el anillo deja de ser
mayoritariamente oscuro.

  · Medido a mano sobre la foto del acero con nato verde: centro (2053, 1927),
    radio 736, y el círculo cae clavado en el canto de la esfera con la cruz
    justo en el eje de las agujas.
  · El centro de la ESFERA no es el de la CAJA: en esa foto va 40 px más
    arriba, porque el cuerpo de la caja incluye las asas.

LA BÚSQUEDA VA SOBRE UN RECORTE REDUCIDO. A tamaño completo son 441 mapas de
distancias de 4096×4096 y no termina; en un recorte de 550 px tarda segundos y
la precisión sobra, porque luego se reescala.

LA SOMBRA DEL CANTO. Una esfera pegada en plano se nota: en las fotos de verdad
el bisel oscurece el borde del disco. Se imita con una caída suave —smoothstep—
en el 10 % exterior. NO se copia el perfil de luz de la foto vieja: se intentó,
y como allí la esfera es negra, el perfil medido llevaba el borde al 12 % de
luz, que sobre una esfera clara es un vignette brutal, y encima salía a
anillos por el ruido del perfil.

QUÉ NO HACE: no transfiere el reflejo del cristal ni las sombras de las agujas.
La esfera que se le pase tiene que traer sus propias agujas, en la MISMA hora
que la foto —las nuestras van a las 10:09— o el reloj cambiará de hora al
cambiar de esfera.

Uso:
    python3 herramientas/cambiar_esfera.py foto.png esfera.png salida.png
    python3 herramientas/cambiar_esfera.py foto.png esfera.png salida.png --sombra 0.82
"""
import argparse
import numpy as np
from PIL import Image

LUM = (0.2126, 0.7152, 0.0722)
BUSCA = 550          # lado del recorte reducido donde se busca el centro


def luminancia(a):
    return LUM[0] * a[..., 0] + LUM[1] * a[..., 1] + LUM[2] * a[..., 2]


def centro_caja(a):
    """El cuerpo de la caja, que solo sirve como punto de partida."""
    op = a[..., 3] > 200
    alto = op.shape[0]
    col = np.where(op.sum(0) > alto * .30)[0]
    fil = np.where(op.sum(1) > alto * .30)[0]
    if not len(col) or not len(fil):
        raise SystemExit('no encuentro la caja en la foto')
    return (col.min() + col.max()) / 2, (fil.min() + fil.max()) / 2


def hueco(foto, margen=1100):
    """El disco de la esfera: centro y radio, buscados y no supuestos."""
    a = np.asarray(foto).astype(float)
    cx0, cy0 = centro_caja(a)
    caja = (int(cx0 - margen), int(cy0 - margen), int(cx0 + margen), int(cy0 + margen))
    z = np.asarray(foto.crop(caja).resize((BUSCA, BUSCA), Image.LANCZOS)).astype(float)
    op = z[..., 3] > 200
    osc = op & (luminancia(z) < 70)
    yy, xx = np.mgrid[0:BUSCA, 0:BUSCA]

    mejor = None
    for dx in np.arange(-10, 10.5, 1.0):
        for dy in np.arange(-10, 10.5, 1.0):
            cx, cy = BUSCA / 2 + dx, BUSCA / 2 + dy
            d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            rs = np.arange(BUSCA * .11, BUSCA * .44, 1.0)
            fr = []
            for r in rs:
                an = (d >= r) & (d < r + 1)
                fr.append(osc[an].mean() if an.sum() > 20 else np.nan)
            fr = np.array(fr)
            i = np.where(fr < 0.5)[0]
            if not len(i):
                continue
            j = i[0]
            salto = np.nanmax(fr[max(0, j - 4):j + 1]) - np.nanmin(fr[j:j + 5])
            if mejor is None or salto > mejor[0]:
                mejor = (salto, cx, cy, rs[j])
    if mejor is None:
        raise SystemExit('no encuentro el disco de la esfera')
    salto, cx, cy, r = mejor
    k = 2 * margen / BUSCA
    return caja[0] + cx * k, caja[1] + cy * k, r * k, salto


def radio_esfera(esf):
    """La esfera suelta: su radio, comprobando que de verdad es un círculo."""
    a = np.asarray(esf)
    op = a[..., 3] > 128
    ys, xs = np.where(op)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    anc, alt = xs.max() - xs.min(), ys.max() - ys.min()
    if abs(anc - alt) > max(anc, alt) * 0.01:
        raise SystemExit('la esfera no es circular (%d x %d): no se puede encajar' % (anc, alt))
    return cx, cy, (anc + alt) / 4


def suave(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def cambiar(foto, esf, sombra=0.82, desde=0.90):
    b = np.asarray(foto).astype(float)
    H = b.shape[0]
    CX, CY, R, salto = hueco(foto)
    ex, ey, ER = radio_esfera(esf)
    print('hueco en la foto:  centro (%.0f, %.0f) · radio %.0f · nitidez del borde %.2f'
          % (CX, CY, R, salto))
    print('esfera suelta:     centro (%.0f, %.0f) · radio %.0f' % (ex, ey, ER))
    k = R / ER
    print('escala:            %.4f' % k)

    w, _ = esf.size
    peq = esf.resize((int(round(w * k)),) * 2, Image.LANCZOS)
    capa = Image.new('RGBA', foto.size, (0, 0, 0, 0))
    capa.paste(peq, (int(round(CX - ex * k)), int(round(CY - ey * k))))
    a = np.asarray(capa).astype(float)

    yy, xx = np.mgrid[0:H, 0:H]
    d = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
    # el recorte, con medio píxel de suavizado para que no quede canto duro
    dentro = np.clip((R - 1.5 - d) / 2.0, 0, 1)
    alfa = (a[..., 3] / 255.0) * dentro

    z = a[..., :3]
    if sombra < 1:
        f = 1 - (1 - sombra) * suave((d / R - desde) / (1 - desde))
        z = z * np.clip(f, 0, 1)[..., None]

    out = b.copy()
    out[..., :3] = b[..., :3] * (1 - alfa[..., None]) + np.clip(z, 0, 255) * alfa[..., None]
    fuera = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    # comprobación: el contraste de lo que queda dentro
    c = np.asarray(fuera).astype(float)
    L = luminancia(c)
    en = (c[..., 3] > 200) & (d < R * 0.95)
    hist, bins = np.histogram(L[en], bins=64, range=(0, 256))
    fondo = (bins[hist.argmax()] + bins[hist.argmax() + 1]) / 2
    lume = en & (c[..., 0] > c[..., 2] + 28) & (L > 140)
    num = en & ((L < 90) if fondo > 128 else ((L > 170) & (c[..., :3].max(2) - c[..., :3].min(2) < 40)))

    def contraste(x, y):
        x, y = max(x, y) / 255, min(x, y) / 255
        return (x + 0.05) / (y + 0.05)
    print('queda: fondo %.0f · numerales %.0f (%.1f:1) · lume %.0f (%.1f:1)'
          % (fondo, L[num].mean(), contraste(fondo, L[num].mean()),
             L[lume].mean(), contraste(fondo, L[lume].mean())))
    if lume.sum() and contraste(fondo, L[lume].mean()) < 2.5:
        print('   ⚠️  el lume de las horas casi no se ve sobre este fondo')
    return fuera


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('foto'); p.add_argument('esfera'); p.add_argument('salida')
    p.add_argument('--sombra', type=float, default=0.82,
                   help='cuánto se oscurece el canto del disco: 1 = nada, 0,82 por defecto')
    a = p.parse_args()
    im = cambiar(Image.open(a.foto).convert('RGBA'), Image.open(a.esfera).convert('RGBA'), a.sombra)
    im.save(a.salida)
    print(a.salida)
