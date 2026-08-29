#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LOS CONFIGURADORES DE 2026, TODOS CON LOS MISMOS PASOS
============================================================
Óscar, 19/08/2026: «el formato que manda es el del Lunar para el
configurador, vete montando todos los demás porque vamos a necesitar».
Y el 29/08/2026, el orden de pasos para los diez modelos.

EL ORDEN DE PASOS NO ESTÁ AQUÍ: está en `assets/datos/pasos-2026.json`,
que es el contrato. Aquí solo se obedece. Si mañana cambia el orden se
toca ese fichero y se vuelven a generar las diez fichas.

LAS DOS REGLAS DE ÓSCAR, y son las que hacen que esto valga para diez
modelos distintos sin escribir diez ficheros a mano:

    · UN PASO CON UNA SOLA OPCIÓN sale ya señalado y explicado. No se
      esconde. El cliente tiene que saber que su reloj lleva zafiro
      aunque no haya podido elegir otra cosa.

    · UN PASO SIN OPCIONES NO APARECE. Ni rótulo vacío, ni «pendiente»,
      ni un botón solo que no lleva a ningún sitio. Con caja integrada
      —Precisa, Bitácora— eso deja la ficha sin bisel, y así tiene que
      ser.

POR QUÉ UN GENERADOR Y NO DIEZ FICHAS A MANO
    Porque el catálogo cambia todas las semanas. Con los datos fuera,
    cuando lleguen los costes y las fotos solo hay que rellenar el JSON
    y volver a pasar esto: no se rehace ninguna ficha.

MIENTRAS NO HAYA PRECIO, NO SE VENDE
    El motor de la casa calcula el PVP a partir del COSTE de cada pieza.
    Si el JSON todavía no los tiene (`"listo": false`), la ficha sale con
    el precio sin poner y el botón apagado, y lo dice. Es preferible a
    inventar un precio o a dejar un botón que llevaría a un carrito que
    el servidor va a rechazar.

⚠️ NO GENERA `lunar.html` NI `trinchera.html`. Los dos están vendiendo y
   llevan dentro cosas que este generador todavía no sabe hacer —el
   montaje por capas, la criba, el motor de precios—. Se niega a
   escribirlos aunque se le pida por nombre.

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

V_CSS_PRODUCTO = 42
V_CSS_COLECCION = 44
V_JS_CARRITO = 11
MARCA = 'GENERADO por herramientas/generar_ficha_2026.py'

# ⚠️ LOS QUE ESTÁN VENDIENDO. NO SE TOCAN.
#
# Llevan dentro cosas que este generador todavía no sabe hacer —el montaje
# por capas, la criba, el motor de precios que saca el PVP del coste— y
# sobrescribirlos sería tirarlos de la tienda.
#
# ESTO NO ES UNA PRECAUCIÓN TEÓRICA: el 29/08/2026, la primera vez que se
# pasó el generador con los diez modelos, se llevó por delante `precisa.html`
# y `bitacora.html`, que estaban vendiendo, y las dejó con «Todavía no está a
# la venta». Se recuperaron de una copia hecha un minuto antes. De ahí esta
# lista y de ahí que se compruebe ANTES de escribir nada.
INTOCABLES = ('lunar', 'trinchera', 'precisa', 'bitacora', 'cero-cero')

# ⚠️ Y LA COMPROBACIÓN DE VERDAD: este generador SOLO reescribe páginas que
# él mismo escribió. Lo dicen ellas en su propia cabecera. `cero-cero.html`
# no lleva esa marca —viene del configurador viejo, el de las clases `cf-`—
# y por eso está arriba en la lista: no es suyo, no lo toca.


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


ORDEN = os.path.join(RAIZ, 'assets/datos/pasos-2026.json')


def bolsa(d, ruta):
    """Saca `caja.materiales` de los datos del modelo. Lo que no está,
    vuelve como lista vacía: es lo que hace que el paso no aparezca."""
    sitio = d
    for tramo in ruta.split('.'):
        if not isinstance(sitio, dict):
            return []
        sitio = sitio.get(tramo)
        if sitio is None:
            return []
    return sitio if isinstance(sitio, list) else []


def paso_html(paso, opciones):
    """Un paso del configurador: su número, su rótulo y sus botones.

    ⚠️ CON UNA SOLA OPCIÓN NO SE ESCONDE EL PASO. Sale señalada y con su
    explicación a la vista, que es la regla de Óscar: el cliente tiene que
    saber que su reloj lleva zafiro aunque no haya podido elegir otra cosa.
    ⚠️ Y NO SE MARCA `disabled`. Se probó y quedaba justo al revés de lo que
    él pide: la hoja compartida pinta los botones deshabilitados TACHADOS y
    al 35 % de opacidad, que es como dice «esto no lo puedes llevar». La
    única opción que hay tiene que verse como lo que es —lo que lleva el
    reloj—, no como algo agotado. Se queda señalada, entera y pulsable; la
    marca de que no hay más es el «uno solo» del rótulo."""
    sola = len(opciones) == 1
    botones = []
    for o in opciones:
        punto = ('<i class="pv-punto" style="background:%s"></i>' % o['color']) if o.get('color') else ''
        botones.append(
            '            <button type="button" data-v="%s"%s%s>%s%s</button>'
            % (esc(o['id']),
               ' aria-pressed="true"' if o is opciones[0] else '',
               '',
               punto, esc(o['nombre'])))

    # `pv-nota` es la etiqueta que flota SOBRE la foto; la de un paso va
    # debajo de sus botones y necesita su propia clase.
    #
    # CON UNA SOLA OPCIÓN, SU EXPLICACIÓN SALE SIEMPRE. Con varias, solo si
    # alguna la trae: ahí la explicación la da el propio rótulo al pulsar.
    nota = ''
    if sola and (opciones[0].get('expl') or opciones[0].get('nota')):
        nota = '\n            <p class="pv-nota-paso">%s</p>' % esc(
            opciones[0].get('expl') or opciones[0]['nota'])
    else:
        for o in opciones:
            if o.get('nota'):
                nota = '\n            <p class="pv-nota-paso">%s</p>' % esc(o['nota'])
                break

    return """          <div class="pv-grupo">
            <p class="pv-rotulo">%s%s</p>
            <div class="pv-opciones" data-pv="%s">
%s
            </div>%s
          </div>""" % (esc(paso['rotulo']),
                       ' <b>uno solo</b>' if sola else '',
                       esc(paso['id']), '\n'.join(botones), nota)


def pasos_del_modelo(d):
    """Los pasos que le tocan a este modelo, en el orden de la casa.

    Aquí viven las dos reglas: un paso sin opciones no sale, y un paso que
    depende de algo que este modelo no tiene —el bisel de una caja
    integrada— tampoco."""
    with open(ORDEN, encoding='utf-8') as f:
        orden = json.load(f)['pasos']
    fuera, dentro = [], []
    for paso in orden:
        salta = paso.get('salta_si')
        if salta and bolsa_bool(d, salta):
            fuera.append((paso['id'], 'caja integrada'))
            continue
        ops = bolsa(d, paso['de'])
        if not ops:
            fuera.append((paso['id'], 'sin opciones'))
            continue
        dentro.append((paso, ops))
    return dentro, fuera


def bolsa_bool(d, ruta):
    sitio = d
    for tramo in ruta.split('.'):
        if not isinstance(sitio, dict):
            return False
        sitio = sitio.get(tramo)
    return bool(sitio)


def ficha(d):
    listo = bool(d.get('listo'))
    dentro, _fuera = pasos_del_modelo(d)
    # UNA FICHA SIN NINGÚN PASO NO SE INDEXA. Medusa y Barlovento existen
    # como página para poder empezar a llenarlas, pero hoy no tienen ni una
    # pieza decidida: dejar que Google las liste sería anunciar un reloj que
    # no existe. En cuanto tengan un paso, el noindex se cae solo.
    noindex = '' if dentro else '<meta name="robots" content="noindex">\n'
    pasos = '\n\n'.join(paso_html(p, ops) for p, ops in dentro)

    combinaciones = 1
    for _p, ops in dentro:
        combinaciones *= len(ops)

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
%(noindex)s<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/manifest.json">
<!-- GENERADO por herramientas/generar_ficha_2026.py — no editar a mano.
     Los datos viven en assets/datos/fichas/%(slug)s.json -->
%(recursos)s
<link rel="stylesheet" href="/assets/css/laora.css?v=52">
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
        'noindex': noindex,
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
        destino = os.path.join(RAIZ, slug + '.html')
        if slug in INTOCABLES:
            print('%-10s ⛔ no se toca: no es de este generador' % slug)
            continue
        if os.path.exists(destino):
            with open(destino, encoding='utf-8') as f:
                if MARCA not in f.read(4096):
                    print('%-10s ⛔ existe y NO lleva la marca de este '
                          'generador: no se pisa' % slug)
                    continue
        with open(os.path.join(carpeta, slug + '.json'), encoding='utf-8') as f:
            d = json.load(f)
        with open(os.path.join(RAIZ, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(ficha(d))
        dentro, fuera = pasos_del_modelo(d)
        n = 1
        for _p, ops in dentro:
            n *= len(ops)
        print('%-11s %2d pasos · %5d combinaciones · %s'
              % (slug, len(dentro), n,
                 'a la venta' if d.get('listo') else 'sin precio, NO se vende'))
        if fuera:
            print('%-11s    sin salir: %s' % ('',
                  ', '.join('%s (%s)' % f for f in fuera)))


if __name__ == '__main__':
    main()
