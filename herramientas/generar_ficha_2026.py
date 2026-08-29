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

import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'herramientas'))
from cabecera_laora import RECURSOS, SCRIPT, marcado          # noqa: E402

V_CSS_PRODUCTO = 42
V_CSS_COLECCION = 44
V_CSS_CONFIG = 1
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
INTOCABLES = ('lunar', 'trinchera')

# Precisa y Bitácora salieron de aquí el 29/08/2026, cuando sus costes
# pasaron a su JSON y el generador supo hacerles el precio. Se hizo con una
# copia delante y comprobando que sus referencias salían idénticas.

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


PLANTILLA = os.path.join(RAIZ, 'assets/datos/ficha-2026.tpl.html')


def js(v):
    """Un valor de Python escrito como JavaScript legible."""
    return json.dumps(v, ensure_ascii=False)


def tabla(opciones):
    """De la lista de opciones del JSON a la tabla que espera el motor:
    `{ID: {nombre, expl}}`. El motor no sabe de listas."""
    t = {}
    for o in opciones:
        fila = {'nombre': o['nombre']}
        if o.get('expl'):
            fila['expl'] = o['expl']
        if o.get('color'):
            fila['color'] = o['color']
        # ⚠️ EL COSTE VIAJA TAL CUAL, y la diferencia entre 0 y ausente es
        # deliberada: `0` es «esta pieza no añade coste» y ausente es «no se
        # sabe». Sin coste no hay precio y no se vende.
        if 'coste' in o:
            fila['coste'] = o['coste']
        # Cualquier otro dato de la opción viaja tal cual: lo usan las
        # plantillas de referencia, como la tapa de la Precisa.
        for k in o:
            if k not in ('id', 'nombre', 'expl', 'color', 'coste', 'familia', 'nota'):
                fila[k] = o[k]
        t[o['id']] = fila
    return t


def modelo_js(d, dentro):
    """El bloque `window.LAORA_MODELO` de una ficha generada.

    Aquí NO hay reglas: solo las piezas. Un modelo con dependencias entre
    pasos —el Lunar— escribe las suyas a mano en su ficha; los demás se
    pintan y se reparan solos, que es lo que permite que los diez tengan
    configurador desde el primer día aunque no tengan ni una foto ni un
    coste (Óscar, 29/08/2026: «quiero todos ya aunque no estén las
    imágenes»)."""
    opciones, estado = {}, {}
    for paso, ops in dentro:
        opciones[paso['id']] = tabla(ops)
        estado[paso['id']] = ops[0]['id']

    # Las familias de correa, si las hay: de qué familia es cada color.
    correa_mat = {}
    for o in d.get('correa', {}).get('colores', []):
        if o.get('familia'):
            correa_mat[o['id']] = o['familia']

    codigo = d.get('codigo') or d['slug'][:6].upper()
    orden = [p['id'] for p, _ in dentro]

    return """<script>
/* ============================================================
   LAS PIEZAS DEL %(NOMBRE)s
   ============================================================
   GENERADO por herramientas/generar_ficha_2026.py desde
   `assets/datos/fichas/%(slug)s.json`. No se edita a mano: se edita el
   JSON y se vuelve a generar.

   Aquí solo hay PIEZAS. Cómo funciona el configurador es de la casa y
   vive en `/assets/js/configurador-2026.js`, que se carga debajo.
   ============================================================ */
  var OPCIONES = %(opciones)s;

  /* Lo que viene puesto al abrir: la primera opción de cada paso. */
  var e = %(estado)s;

  /* ---------- LA REFERENCIA ----------
     Es la que viaja al carrito y la que el servidor comprueba, así que NO
     se puede cambiar de forma a la ligera: una referencia emitida ayer
     tiene que seguir resolviéndose hoy.

     Por eso el modelo puede traer su plantilla en el JSON. `{esf}` es lo
     elegido en ese paso y `{mov.tapa}` un dato de la opción elegida. El
     que no traiga ninguna, se arma con el código y todos los pasos en el
     orden del contrato. */
  var ORDEN = %(orden)s;
  var PLANTILLA_REF = %(plantillaref)s;
  function referencia(e) {
    if (!PLANTILLA_REF) {
      return '%(codigo)s-' + ORDEN.map(function (k) { return e[k]; }).join('-');
    }
    return PLANTILLA_REF.replace(/\{([a-z]+)(?:\.([a-z]+))?\}/g, function (_, paso, campo) {
      var v = e[paso];
      if (!campo) return v;
      var o = OPCIONES[paso] && OPCIONES[paso][v];
      return (o && o[campo]) || '';
    });
  }
  function nombreDe(k) {
    var t = OPCIONES[k], o = t && t[e[k]];
    return o ? o.nombre : '';
  }
  function descripcion(e) {
    return 'laOra %(nombre)s, ' + ORDEN.map(nombreDe).filter(Boolean)
      .join(', ').toLowerCase() + '.';
  }
  function dichoCompleto(e) { return descripcion(e); }
  function detalle(e) {
    return ORDEN.map(nombreDe).filter(Boolean).join(' · ');
  }
  function agua(e) { return %(agua)s; }

  /* La ficha técnica, con lo elegido en cada paso. Mientras no haya textos
     técnicos de verdad, dice lo que el cliente lleva puesto, que es más de
     lo que decía antes: nada. */
  function tecnica(e) {
    return { caja: detalle(e) + '.', mov: nombreDe('mov'),
             esf: nombreDe('esf'), agua: agua(e) };
  }

  window.LAORA_MODELO = {
    slug: %(slugjs)s, nombre: %(nombrejs)s,
    OPCIONES: OPCIONES, e: e,
    CORREAS: OPCIONES.correa || {}, CORREA_MAT: %(correamat)s,
    MATERIALES: OPCIONES.correamat || {}, CIERRES: OPCIONES.cierre || {},
    /* SIN PIEZAS DIBUJADAS TODAVÍA: sin capas no se arma el reloj, y sin
       paquetes no hay coste, así que la ficha dice «Precio por definir» y
       no deja comprar. Es lo honrado hasta que lleguen las dos cosas. */
    CAPA: {}, PILA: [],
    /* LAS COMBINACIONES QUE EXISTEN DE VERDAD. De multiplicar los pasos
       salen muchas más de las que se montan: la Bitácora da 126 y monta
       36. Con esta lista, cada paso enseña sólo lo que sigue teniendo
       salida con lo ya elegido. Vacía quiere decir «todas valen». */
    PAQUETES: %(combis)s,
    /* EL COSTE, SUMANDO LO ELEGIDO. Cada opción trae el suyo y el modelo
       añade lo que no depende de ningún paso —el logo—. Si a una le falta,
       no hay coste: se dibuja, pero no se pone precio ni se vende. */
    COSTES_PUESTOS: %(listo)s, EXTRA: %(extra)s,
    CADENA: %(cadena)s,
    referencia: referencia, descripcion: descripcion,
    dichoCompleto: dichoCompleto, detalle: detalle, agua: agua,
    tecnica: tecnica
  };
</script>
<!-- El motor de precio y el configurador, los mismos para los diez. -->
<script src="/assets/js/precio-2026.js?v=1"></script>
<script src="/assets/js/configurador-2026.js?v=1"></script>""" % {
        'NOMBRE': d['nombre'].upper(), 'slug': d['slug'],
        'nombre': d['nombre'], 'nombrejs': js(d['nombre']), 'slugjs': js(d['slug']),
        'codigo': codigo, 'orden': js(orden),
        'opciones': json.dumps(opciones, ensure_ascii=False, indent=2).replace('\n', '\n  '),
        'estado': js(estado),
        'correamat': js(correa_mat),
        'agua': js(d.get('agua', '')),
        'plantillaref': js(d.get('referencia')) if d.get('referencia') else 'null',
        'listo': 'true' if d.get('listo') else 'false',
        'extra': js(d.get('extra', 0)),
        'combis': json.dumps(d.get('combinaciones', []), ensure_ascii=False),
        'cadena': js(d.get('cadena')) if d.get('cadena') else 'ORDEN',
    }


def ficha(d):
    listo = bool(d.get('listo'))
    dentro, _fuera = pasos_del_modelo(d)
    # UNA FICHA SIN NINGÚN PASO NO SE INDEXA. Medusa y Barlovento existen
    # como página para poder empezar a llenarlas, pero hoy no tienen ni una
    # pieza decidida: dejar que Google las liste sería anunciar un reloj que
    # no existe. En cuanto tengan un paso, el noindex se cae solo.
    noindex = '' if dentro else '<meta name="robots" content="noindex">\n'

    combinaciones = 1
    for _p, ops in dentro:
        combinaciones *= len(ops)

    cuerpo = io.open(PLANTILLA, encoding='utf-8').read() % {
        'nombre': esc(d['nombre']),
        'codigo': esc((d.get('codigo') or '') + (' · ' if d.get('codigo') else '') + d.get('clase', '')),
        'nuevo': '<span class="cv2-chip pv-chip-oro">Nuevo</span>' if not listo else '',
        # SIN FOTO DE PRESENTACIÓN NO SE PONE NADA. El visor se queda con el
        # montaje por capas, que sin capas no dibuja: un marco vacío dice la
        # verdad mejor que una foto de otro reloj.
        'presentacion': '',
        'decerca': '',
    }

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
<!-- EL ESTILO DEL CONFIGURADOR, el del Lunar, que desde el 29/08/2026 es el
     de la casa. VA DESPUÉS de producto-2026.css: buena parte de sus reglas
     están para ganarle a esa hoja, y cargándolo antes pierde. -->
<link rel="stylesheet" href="/assets/css/configurador-2026.css?v=%(vconf)d">
</head>
<body>%(cabecera)s

%(cuerpo)s

<footer class="aviso-marcas">
  <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
</footer>

%(script)s
<script src="/assets/js/carrito.js?v=%(vjs)d"></script>
<script src="/assets/js/telemetria.js" defer></script>
%(modelo)s
</body>
</html>
""" % {
        'nombre': esc(d['nombre']), 'slug': d['slug'],
        'combinaciones': combinaciones, 'noindex': noindex,
        'recursos': RECURSOS, 'cabecera': marcado('relojes'), 'script': SCRIPT,
        'vcol': V_CSS_COLECCION, 'vprod': V_CSS_PRODUCTO, 'vjs': V_JS_CARRITO,
        'vconf': V_CSS_CONFIG,
        'cuerpo': cuerpo,
        'modelo': modelo_js(d, dentro),
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
