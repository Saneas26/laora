#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiñe la correa de una foto con el color de OTRA foto. Sin IA, sin inventar.

La foto de la correa extendida está hecha en un solo color, y el resto de la
gama existe pero solo en la foto del reloj puesto. En vez de pedir seis
sesiones más, se mide el color real en la foto grande de cada tono y se
traslada al tejido de la abierta.

CÓMO, Y POR QUÉ ASÍ:

- No es un tinte plano. La correa tiene trama, pliegues y sombra, y todo eso
  vive en la LUMINANCIA. Se normaliza la del tejido de origen —media y
  desviación— y se remapea a la media y la desviación medidas en el destino:
  el relieve se conserva y el tono acaba donde tiene que acabar.
- El color se copia del destino en el plano cromático, no se estira el del
  origen. Un beige llevado a negro por multiplicación se queda pardo.

QUÉ NO SE TIÑE:
- Los índices de lume de la esfera, que también son cálidos. Se quitan por
  TAMAÑO, con una apertura morfológica: son islas finas y la correa es una
  masa ancha. Excluirlos con un disco alrededor del reloj era peor, porque
  el disco se comía la correa que pasa por detrás de la caja.
- La hebilla y los pasadores metálicos: son grises neutros y la máscara
  exige tono cálido.
- El fondo: se exige alfa opaco.

Uso:
    python3 herramientas/recolorear_correa.py abierta.png destino.png salida.png
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

LUM = (0.2126, 0.7152, 0.0722)


def luminancia(a):
    return LUM[0] * a[..., 0] + LUM[1] * a[..., 1] + LUM[2] * a[..., 2]


def mascara_tejido(a, calibre=31):
    """El tejido, y solo el tejido.

    Se pide opaco y cálido: eso descarta el fondo, la caja de acero, la
    hebilla y las agujas, que son grises neutros. Pero deja dentro los
    índices de lume de la esfera, que también son cálidos.

    Se quitan por TAMAÑO y no por posición: una apertura —erosión seguida de
    dilatación— borra las islas más finas que el calibre y deja intacta la
    correa, que es una masa ancha y continua. Excluirlos con un disco
    alrededor del reloj era peor: el disco se comía la correa que pasa por
    detrás de la caja y dejaba un halo del color viejo.
    """
    op = a[..., 3] > 200
    R, B = a[..., 0], a[..., 2]
    m = op & (R > B + 22) & (R > 110)

    img = Image.fromarray((m * 255).astype(np.uint8))
    abierta = img.filter(ImageFilter.MinFilter(calibre)).filter(ImageFilter.MaxFilter(calibre))
    # La apertura sola devuelve una correa MORDIDA: la erosión se come el
    # contorno y en las zonas estrechas —el borde junto a las asas, el canto
    # de los agujeros— la dilatación no lo repone, y ahí quedaban motitas del
    # color viejo. Así que la apertura no se usa como máscara, sino como
    # SEMILLA: se ensancha y se corta con la máscara de color original, que sí
    # tiene el borde exacto. Los índices no se recuperan porque están lejos.
    # se ensancha al doble: con una dilatación corta, el pico de correa que se
    # mete bajo las asas quedaba fuera y se veían dos motitas del color viejo
    semilla = np.asarray(abierta.filter(ImageFilter.MaxFilter(calibre * 2 + 1))) > 127
    # Y DENTRO de esa zona, la exigencia de color se afloja. El pespunte y el
    # canto de la correa son bastante más oscuros que la trama y no llegaban
    # al umbral, así que se quedaban del color viejo y se veían: una costura
    # beige sobre la correa verde. Aquí dentro ya no hay nada más que tejido
    # —la caja y la hebilla son grises neutros y siguen fuera por el tono—,
    # así que basta con pedir que tire a cálido.
    return semilla & op & (R > B + 8)


def mascara_piel(a, _=None):
    """La piel: opaca, OSCURA y CONECTADA con los extremos de la foto.

    Una correa de piel negra no se distingue por el tono, como el nato, sino
    por lo oscura que es. Eso deja fuera la caja de acero, la hebilla y el
    pespunte, que son claros —y el pespunte tiene que quedarse claro, que es
    blanco en todos los colores—. Lo que queda dentro y no debería es la
    ESFERA, tan negra como la correa.

    Con un disco alrededor del reloj no hay manera: pequeño deja un halo
    teñido en el bisel, y grande se come el trozo de correa que entra bajo
    las asas y lo deja del color viejo. Lo que sí distingue a una de otra es
    la FORMA: la correa entra por arriba y sale por abajo, y la esfera es una
    mancha aislada en medio. Así que se siembra en la primera y la última
    fila y se deja crecer por dentro de lo oscuro; lo que no alcanza el
    crecimiento es la esfera.

    La inundación se hace a un cuarto de tamaño, que va de sobra para separar
    dos manchas tan grandes y es mucho más rápida.
    """
    op = a[..., 3] > 200
    mx = a[..., :3].max(2)
    m = op & (mx < 120)

    ch, cw = m.shape[0] // 4, m.shape[1] // 4
    peq = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                     .resize((cw, ch), Image.NEAREST)) > 127
    # LA SEMILLA: todo lo oscuro que cae FUERA de las filas de la cabeza.
    # Sembrar solo en las filas extremas no valía: arriba lo primero que
    # aparece es la correa doblada bajo la hebilla, y los pasadores la
    # separan del resto, así que la inundación se quedaba encerrada ahí y
    # medio brazalete se quedaba sin teñir.
    anchos = np.array([(a[..., 3] > 200)[y].sum() for y in range(a.shape[0])])
    correa_ancho = np.median(anchos[anchos > 0][:400])
    cabeza = np.where(anchos > correa_ancho * 1.5)[0]
    if len(cabeza):
        ymax = int(np.argmax(anchos))
        y0 = y1 = ymax
        while y0 > 0 and anchos[y0 - 1] > correa_ancho * 1.5:
            y0 -= 1
        while y1 < len(anchos) - 1 and anchos[y1 + 1] > correa_ancho * 1.5:
            y1 += 1
    else:
        y0 = y1 = a.shape[0] // 2
    crece = peq.copy()
    crece[max(0, y0 // 4):min(peq.shape[0], y1 // 4 + 1)] = False
    for _ in range(400):
        antes = crece.sum()
        d = np.asarray(Image.fromarray((crece * 255).astype(np.uint8))
                       .filter(ImageFilter.MaxFilter(9))) > 127
        crece = d & peq
        if crece.sum() == antes:
            break

    grande = np.asarray(Image.fromarray((crece * 255).astype(np.uint8))
                        .resize((m.shape[1], m.shape[0]), Image.BILINEAR)) > 100
    return m & grande


def color_destino(img, franja=(0.08, 0.22), piel=False):
    """El color de la correa en la foto del reloj puesto: la franja de
    arriba, que es correa limpia y no tiene dentro ni la cabeza ni la
    hebilla. Con `piel`, se descarta el pespunte, que es claro y no debe
    entrar en la media."""
    a = np.asarray(img.convert('RGBA')).astype(float)
    h, w = a.shape[:2]
    z = a[int(h * franja[0]):int(h * franja[1]), int(w * .36):int(w * .64)]
    o = z[..., 3] > 200
    if piel:
        # el pespunte es lo más claro de la franja: fuera el quinto de arriba
        lz = luminancia(z)
        o = o & (lz <= np.percentile(lz[o], 80))
    if o.sum() < 500:
        raise SystemExit('no encuentro la correa en la foto de destino')
    lum = luminancia(z)[o]
    return z[..., 0][o].mean(), z[..., 1][o].mean(), z[..., 2][o].mean(), lum.mean(), lum.std()


def recolorear(abierta, destino, calibre=31, esfera=None):
    a = np.asarray(abierta.convert('RGBA')).astype(float)
    m = mascara_piel(a, esfera) if esfera else mascara_tejido(a, calibre)
    if not m.any():
        raise SystemExit('no encuentro la correa en la foto abierta')

    dr, dg, db, dlum, dstd = color_destino(destino, piel=bool(esfera))
    lum = luminancia(a)
    olum, ostd = lum[m].mean(), lum[m].std()

    # el relieve del tejido, en unidades de desviación, trasladado al destino
    z = (lum - olum) / max(ostd, 1e-6)
    nueva = np.clip(dlum + z * dstd, 4, 250)
    factor = nueva / np.maximum(lum, 1e-6)

    # el color base del destino, modulado por ese relieve
    base = np.stack([np.full(a.shape[:2], dr), np.full(a.shape[:2], dg),
                     np.full(a.shape[:2], db)], axis=2)
    tenido = np.clip(base * (nueva / max(dlum, 1e-6))[..., None], 0, 255)

    suave = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255
    out = a.copy()
    out[..., :3] = a[..., :3] * (1 - suave[..., None]) + tenido * suave[..., None]
    fuera = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    b = np.asarray(fuera).astype(float)
    print('destino  R %3.0f G %3.0f B %3.0f · luz %5.1f' % (dr, dg, db, dlum))
    print('queda    R %3.0f G %3.0f B %3.0f · luz %5.1f  (%d px teñidos)'
          % (b[..., 0][m].mean(), b[..., 1][m].mean(), b[..., 2][m].mean(),
             luminancia(b)[m].mean(), m.sum()))
    return fuera


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('abierta'); p.add_argument('destino'); p.add_argument('salida')
    p.add_argument('--calibre', type=int, default=31,
                   help='islas más finas que esto se descartan (los índices de lume)')
    p.add_argument('--esfera', help='cx,cy,radio: activa el modo PIEL, que busca '
                                    'lo oscuro en vez de lo cálido')
    a = p.parse_args()
    esf = tuple(int(v) for v in a.esfera.split(',')) if a.esfera else None
    recolorear(Image.open(a.abierta), Image.open(a.destino), a.calibre, esf).save(a.salida)
    print(a.salida)
