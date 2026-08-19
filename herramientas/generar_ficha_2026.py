#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LAS FICHAS DE 2026, CON EL FORMATO DEL LUNAR
============================================================
Óscar, 19/08/2026: «el formato que manda es el del Lunar para el
configurador, vete montando todos los demás porque vamos a necesitar».

Esto escribe una ficha completa a partir de un archivo de datos en
`assets/datos/fichas/<modelo>.json`: los pasos numerados, el visor, el
pie de compra con el precio, «Disponible», el botón, Klarna y la
confianza. El mismo esqueleto que el Lunar.

POR QUÉ UN GENERADOR Y NO CUATRO FICHAS A MANO
    Porque el catálogo está cambiando toda la semana. Con los datos
    fuera, cuando lleguen los costes y las fotos solo hay que rellenar
    el JSON y volver a pasar esto: no se rehace ninguna ficha.

MIENTRAS NO HAYA PRECIO, NO SE VENDE
    El motor de la casa calcula el PVP a partir del COSTE de cada
    pieza. Si el JSON todavía no los tiene (`"listo": false`), la ficha
    sale con el precio sin poner y el botón apagado, y lo dice. Es
    preferible a inventar un precio o a dejar un botón que llevaría a
    un carrito que el servidor va a rechazar.

USO
    python3 herramientas/generar_ficha_2026.py tortuga coctel diver
    python3 herramientas/generar_ficha_2026.py            (todas)
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from cabecera_laora import RECURSOS, SCRIPT, marcado          # noqa: E402

V_CSS_PRODUCTO = 37
V_CSS_COLECCION = 17
V_JS_CARRITO = 11


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def paso_html(paso):
    """Un paso del configurador: su número, su rótulo y sus botones."""
    fija = paso.get('fija')
    botones = []
    for o in paso['opciones']:
        punto = ('<i class="pv-punto" style="background:%s"></i>' % o['color']) if o.get('color') else ''
        botones.append(
            '            <button type="button" data-v="%s"%s>%s%s</button>'
            % (esc(o['id']), ' aria-pressed="true"' if o is paso['opciones'][0] else '',
               punto, esc(o['nombre'])))

    # `pv-nota` es la etiqueta que flota SOBRE la foto; la de un paso va
    # debajo de sus botones y necesita su propia clase.
    nota = ''
    for o in paso['opciones']:
        if o.get('nota'):
            nota = '\n            <p class="pv-nota-paso">%s</p>' % esc(o['nota'])
            break

    return """          <div class="pv-grupo">
            <p class="pv-rotulo">%s%s</p>
            <div class="pv-opciones" data-pv="%s">
%s
            </div>%s
          </div>""" % (esc(paso['rotulo']),
                       ' <b>uno solo</b>' if fija else '',
                       esc(paso['id']), '\n'.join(botones), nota)


def ficha(d):
    listo = bool(d.get('listo'))
    pasos = '\n\n'.join(paso_html(p) for p in d['pasos'])

    combinaciones = 1
    for p in d['pasos']:
        combinaciones *= len(p['opciones'])

    # Sin costes no hay precio: se dice y no se vende.
    if listo:
        precio = '<p class="pv-precio" data-pv-precio>—</p>'
        boton = ('<button class="cv2-comprar pv-comprar" type="button" '
                 'data-pv-comprar>Añadir al carrito</button>')
        klarna = """
        <p class="pv-klarna">
          <span>3 plazos sin intereses (0&nbsp;% TAE) de <b data-pv-klarna>—</b> con</span>
          <img src="/assets/img/pago/klarna.svg?v=2" alt="Klarna" width="48" height="20" loading="lazy">
          <a href="https://www.klarna.com/es/a-plazos/" target="_blank" rel="noopener">Más información</a>
        </p>"""
        aviso = ''
    else:
        precio = '<p class="pv-precio pv-precio-pendiente">Precio por cerrar</p>'
        boton = ('<button class="cv2-comprar pv-comprar" type="button" disabled>'
                 'Todavía no está a la venta</button>')
        klarna = ''
        aviso = ('\n        <p class="pv-aviso-pendiente">Este modelo está en el taller: '
                 'las piezas están elegidas y el precio, por cerrar. '
                 'En cuanto esté, se podrá comprar desde aquí.</p>')

    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="%(nombre)s de laOra: %(combinaciones)d combinaciones, al precio honesto.">
<title>%(nombre)s · laOra</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/manifest.json">
<!-- GENERADO por herramientas/generar_ficha_2026.py — no editar a mano.
     Los datos viven en assets/datos/fichas/%(slug)s.json -->
%(recursos)s
<link rel="stylesheet" href="/assets/css/laora.css?v=51">
<link rel="stylesheet" href="/assets/css/coleccion-v2.css?v=%(vcol)d">
<link rel="stylesheet" href="/assets/css/producto-2026.css?v=%(vprod)d">
</head>
<body>%(cabecera)s

<main class="cv2">
  <div class="pv-cuerpo">
    <div class="pv-galeria">
      <div class="pv-hero pv-hero-vacio" data-pv-hero>
        <p class="pv-foto-pendiente">Foto por hacer</p>
      </div>
    </div>

    <aside class="pv-info">
      <!-- Este <div> no es decorativo: es el que lleva el contador que
           numera los pasos (`.pv-info>div{counter-reset:paso}`). -->
      <div>
        <div class="pv-chips"><span class="cv2-chip">%(clase)s</span></div>
        <h1>%(nombre)s</h1>
        <p class="pv-desc">%(desc)s</p>

%(pasos)s
      </div>

      <!-- El pie de compra: fijo bajo las elecciones, con el precio, el
           botón y Klarna juntos, como en el Lunar. -->
      <div class="pv-pie" data-pv-pie>
        <div class="pv-precio-fila">
          %(precio)s
          <p class="pv-stock"><span>%(stock)s</span><i aria-hidden="true"></i></p>
        </div>
        <p class="pv-imp">Impuestos incluidos.</p>
        %(boton)s%(klarna)s%(aviso)s
        <div class="pv-confianza">
          <span>Envío gratis · devolución 30 días</span>
          <span>Garantía 3 años*</span>
        </div>
        <p class="pv-nota-garantia">* La ley da 3 años. Los 5 son para los socios del <a href="/club.html">Club laOra</a>, que va incluido con tu reloj.</p>
      </div>
    </aside>
  </div>
</main>

<footer class="aviso-marcas">
  <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
</footer>

%(script)s
<script src="/assets/js/carrito.js?v=%(vjs)d"></script>
<script src="/assets/js/telemetria.js" defer></script>
</body>
</html>
""" % {
        'nombre': esc(d['nombre']), 'slug': d['slug'], 'clase': esc(d.get('clase', '')),
        'desc': esc(d.get('desc') or 'Ficha en construcción.'),
        'combinaciones': combinaciones,
        'recursos': RECURSOS, 'cabecera': marcado('relojes'), 'script': SCRIPT,
        'vcol': V_CSS_COLECCION, 'vprod': V_CSS_PRODUCTO, 'vjs': V_JS_CARRITO,
        'pasos': pasos, 'precio': precio, 'boton': boton, 'klarna': klarna, 'aviso': aviso,
        'stock': 'Disponible' if listo else 'En el taller',
    }


def main():
    carpeta = os.path.join(RAIZ, 'assets/datos/fichas')
    quiere = sys.argv[1:] or sorted(
        f[:-5] for f in os.listdir(carpeta) if f.endswith('.json'))

    for slug in quiere:
        with open(os.path.join(carpeta, slug + '.json'), encoding='utf-8') as f:
            d = json.load(f)
        with open(os.path.join(RAIZ, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(ficha(d))
        n = 1
        for p in d['pasos']:
            n *= len(p['opciones'])
        print('%-10s %d pasos · %d combinaciones · %s'
              % (slug, len(d['pasos']), n,
                 'a la venta' if d.get('listo') else 'sin precio, no se vende'))


if __name__ == '__main__':
    main()
