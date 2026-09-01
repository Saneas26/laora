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
V_CSS_COLECCION = 51
V_CSS_CONFIG = 5
# EL MOTOR DEL CONFIGURADOR. Cloudflare lo guarda 4 h por su nombre, así que
# cambiarlo SIN subir este número no le llega a nadie: la ficha nueva sigue
# funcionando con el motor de anteayer. Se sube cada vez que se toca
# `assets/js/configurador-2026.js`, y hay que subirlo también a mano en
# `lunar.html`, que no sale de aquí.
V_JS_CONFIG = 19
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
INTOCABLES = ('lunar',)

# EL TRINCHERA SALIÓ DE ESTA LISTA el 29/08/2026, por orden de Óscar: «quita
# todo lo que tengas en el configurador del trinchera, que vamos a empezar de
# cero». Su configurador propio —2.498 líneas, 93 fotos de serie, 31
# combinaciones vetadas y un recorte por caja para cada foto que faltaba— se
# fue entero, y ahora se genera desde `assets/datos/fichas/trinchera.json`
# como los otros ocho. El Lunar se queda: monta por capas y tiene criba, y
# eso este generador todavía no sabe hacerlo.

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


# LOS BOTONES DE CADA PASO YA NO SE ESCRIBEN AQUI. Los pinta el motor de la
# casa desde el contrato —`montaPasos()` en `assets/js/configurador-2026.js`—
# y esta funcion se quedó escribiendo un HTML que nadie leia: la plantilla
# solo deja el hueco `<div data-pv-pasos>`. Se quita para que no parezca que
# las dos reglas de Oscar viven en dos sitios; viven en el motor.


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
            if k not in ('id', 'nombre', 'expl', 'color', 'coste', 'nota'):
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
        # LA PRIMERA OPCIÓN MANDA… SALVO QUE OTRA DIGA `defecto`. Óscar,
        # 31/08/2026: «en la piel italiana quiero que por defecto comience
        # en pespunte blanco». Se marca en el JSON y no hace falta cambiar
        # el orden de los botones, que es otra cosa.
        estado[paso['id']] = next((o['id'] for o in ops if o.get('defecto')),
                                  ops[0]['id'])

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

  /* ---------- LAS PUERTAS ----------
     Un paso que solo aparece si otro lo abre. El pespunte es de la piel:
     con un brazalete de acero no hay nada que coser, y ensenarlo seria
     preguntar por algo que ese reloj no lleva. Se declara en el JSON

         "puertas": { "pespunte": { "paso": "correamat", "campo": "pespunte" } }

     y se lee asi: el paso `pespunte` se abre cuando la opcion elegida en
     `correamat` trae el campo `pespunte`. El motor esconde los cerrados y
     no les suma el coste; aqui se les quita ademas de la referencia y de
     la descripcion, que es lo que hace que el reloj se llame igual
     eligiendo un pespunte que el otro cuando no lleva ninguno. */
  var PUERTAS = %(puertas)s;

  /* ---------- LOS FILTROS ----------
     Un paso cuyas opciones dependen de lo elegido en otro. El color de la
     correa es del MATERIAL: eligiendo acero no se ensena el azul celeste
     del caucho. Se declara en el JSON

         "filtros": { "correa": { "paso": "correamat", "campo": "familia" } }

     y se lee asi: en `correa` solo salen las opciones cuyo `familia` sea el
     material elegido. Sin esto los dos pasos van cada uno por su lado: el
     29/08/2026 el volcador saco 23.040 referencias del Trinchera en vez de
     6.816 porque montaba brazaletes de acero con hebilla de piel. */
  var FILTROS = %(filtros)s;

  /* AÑADIDOS A PRECIO PLANO, por paso y opción. Óscar, 31/08/2026: «el
     precio de la caja de 39 es 10 € más que la caja de 36 en cualquier
     combinación». No es un coste: un coste pasa por el multiplicador y por
     el redondeo al 9,90, y diez euros de coste serían treinta de precio y
     distintos en cada combinación. Esto se suma AL FINAL, encima del precio
     ya hecho, así que la diferencia son diez euros clavados siempre.
     Se declara con `"pvp"` en la opción del JSON. */
  var PVP_EXTRA = %(pvpextra)s;
  function cuelgaDe(k) { return FILTROS[k] || null; }
  function valeEn(k, id, s) {
    var f = cuelgaDe(k);
    if (!f) return true;
    var o = OPCIONES[k] && OPCIONES[k][id];
    return !!o && o[f.campo] === (s || e)[f.paso];
  }
  function abierta(k, s) {
    var g = PUERTAS[k];
    if (!g) return true;
    var o = OPCIONES[g.paso] && OPCIONES[g.paso][(s || e)[g.paso]];
    return !!(o && o[g.campo]);
  }

  /* ---------- LA REFERENCIA ----------
     Es la que viaja al carrito y la que el servidor comprueba, asi que NO
     se puede cambiar de forma a la ligera: una referencia emitida ayer
     tiene que seguir resolviendose hoy.

     `{esf}` es lo elegido en ese paso y `{mov.tapa}` un dato de la opcion
     elegida. Un paso con la puerta cerrada no escribe nada, y el guion que
     le tocaba se cae con el: sin eso, un brazalete acabaria en `-A316S-` y
     el mismo reloj tendria dos referencias segun un pespunte que no lleva. */
  var PLANTILLA_REF = %(plantillaref)s;
  function referencia(e) {
    if (!PLANTILLA_REF) {
      return '%(codigo)s-' + ORDEN.filter(function (k) { return abierta(k, e); })
        .map(function (k) { return e[k]; }).join('-');
    }
    return PLANTILLA_REF.replace(/\{([a-z]+)(?:\.([a-z]+))?\}/g, function (_, paso, campo) {
      if (!abierta(paso, e)) return '';
      var v = e[paso];
      if (!campo) return v;
      var o = OPCIONES[paso] && OPCIONES[paso][v];
      return (o && o[campo]) || '';
    }).replace(/-{2,}/g, '-').replace(/-+$/, '');
  }
  function nombreDe(k) {
    if (!abierta(k)) return '';
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
  /* LA ESTANQUEIDAD PUEDE SER DE UNA PIEZA. El Trinchera aguanta 5 ATM
     salvo en titanio, que son 20: la caja lo dice en su propia opcion y
     manda sobre la del modelo. Vale para cualquier paso. */
  function agua(e) {
    for (var i = 0; i < ORDEN.length; i++) {
      var t = OPCIONES[ORDEN[i]], o = t && t[e[ORDEN[i]]];
      if (o && o.agua) return o.agua;
    }
    return %(agua)s;
  }

  /* ---------- LA FICHA TÉCNICA ----------
     Por defecto dice lo que el cliente lleva puesto, que es más de lo que
     decía antes: nada. Pero un modelo puede escribir la suya en el JSON,
     en `tecnica`, y entonces manda ella.

     Óscar, 01/09/2026, sobre el Tortuga: «Automático japonés · Caucho ·
     Negra · Clásica plata: esto no va en el apartado de caja». Tenía razón:
     el apartado se llama «Caja y materiales» y le estábamos metiendo la
     configuración entera, movimiento y correa incluidos.

     Cada entrada puede ser un texto o una TABLA por paso —`{"A": "…",
     "Q": "…"}`—, para que el movimiento se explique según cuál se elija.
     Dentro del texto, `{esf}`, `{caja}`… se cambian por el nombre de lo
     elegido en ese paso. */
  var TECNICA = %(tecnica)s;
  function deTecnica(k, porDefecto) {
    var v = TECNICA[k];
    if (v && typeof v === 'object') v = v[e[k]] || v['*'];
    if (!v) return porDefecto;
    return v.replace(/\{(\w+)\}/g, function (_, g) {
      return (nombreDe(g) || '').toLowerCase();
    });
  }
  function tecnica(e) {
    return { caja: deTecnica('caja', detalle(e) + '.'),
             mov: deTecnica('mov', nombreDe('mov')),
             esf: deTecnica('esf', nombreDe('esf')),
             agua: deTecnica('agua', agua(e)) };
  }

  window.LAORA_MODELO = {
    slug: %(slugjs)s, nombre: %(nombrejs)s,
    OPCIONES: OPCIONES, e: e,
    CORREAS: OPCIONES.correa || {}, CORREA_MAT: %(correamat)s,
    MATERIALES: OPCIONES.correamat || {}, CIERRES: OPCIONES.cierre || {},
    /* EL MONTAJE POR CAPAS, si el modelo lo trae. Se declara en el JSON:

           "montaje": { "img": "/assets/img/<modelo>/capas/", "v": "?v=1",
                        "pila": [{"capa": "esf", "grupo": "esf"}, ...],
                        "capas": { "esf": {"AZM": "esfera-azul-marino"}, ... } }

       `pila` es el orden de apilado (con `necesita` para lo que no puede
       flotar solo, como las agujas sin su esfera) y `capas` dice qué
       fichero dibuja cada opción. El que no traiga nada se queda sin
       dibujo y la ficha lo dice. Lo estrenó el Precisa el 30/08/2026. */
    CAPA: %(capa)s, CAPA_IMG: %(capaimg)s, SERIE_V: %(seriev)s,
    PILA: %(pila)s,
    /* LA MINIATURA DE LA CORREA, si el modelo la trae. Es la foto de la
       correa de verdad, suelta y entera, que el montaje no puede enseñar:
       sus capas se acaban en el borde del lienzo. Se declara en el JSON

           "miniatura": { "img": "/assets/img/<modelo>/miniaturas/",
                          "paso": "pasadores", "lado": "derecha",
                          "suelta": true,
                          "fotos": { "NEG": ["pasadores-negros"] },
                          "alt": { "pasadores-negros": "…" } }

       `paso` es de qué elección cuelga —por defecto el color de la correa,
       que es de donde colgaba cuando sólo la tenía el Lunar—; si ese paso
       lleva puerta y está cerrada, no se enseña nada. `lado` la manda a la
       otra esquina y `suelta` le quita la tarjeta blanca. */
    MINI: %(mini)s, MINI_IMG: %(miniimg)s, MINI_ALT: %(minialt)s,
    MINI_PASO: %(minipaso)s, MINI_LADO: %(minilado)s, MINI_SUELTA: %(minisuelta)s,
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
    PVP_EXTRA: PVP_EXTRA,
    precioExtra: function (s) {
      var t = 0;
      for (var k in PVP_EXTRA) {
        if (!abierta(k, s)) continue;
        var v = PVP_EXTRA[k][(s || e)[k]];
        if (v) t += v;
      }
      return t;
    },
    /* LO QUE ÓSCAR DA POR MUERTO. Firmas de combinación en el orden del
       contrato de pasos, sin el tamaño ni el calibre: una vale por las
       cuatro referencias. Ni se dibujan ni entran en el catálogo. Salen
       del `"vetos"` del JSON, que se llena con la lista que Óscar copia
       del panel de `?curar`. */
    VETOS: %(vetos)s,
    /* Las puertas: el motor esconde el paso cerrado y no le suma coste. */
    PUERTAS: PUERTAS, abierta: abierta,
    FILTROS: FILTROS, valeEn: valeEn,
    referencia: referencia, descripcion: descripcion,
    dichoCompleto: dichoCompleto, detalle: detalle, agua: agua,
    tecnica: tecnica
  };
</script>
<!-- El motor de precio y el configurador, los mismos para los diez. -->
<script src="/assets/js/precio-2026.js?v=2"></script>
<script src="/assets/js/configurador-2026.js?v=%(vjsconf)d"></script>""" % {
        'NOMBRE': d['nombre'].upper(), 'slug': d['slug'],
        'nombre': d['nombre'], 'nombrejs': js(d['nombre']), 'slugjs': js(d['slug']),
        'codigo': codigo, 'orden': js(orden),
        'opciones': json.dumps(opciones, ensure_ascii=False, indent=2).replace('\n', '\n  '),
        'estado': js(estado),
        'correamat': js(correa_mat),
        'agua': js(d.get('agua', '')),
        'puertas': js(d.get('puertas', {})),
        'filtros': js(d.get('filtros', {})),
        'plantillaref': js(d.get('referencia')) if d.get('referencia') else 'null',
        'listo': 'true' if d.get('listo') else 'false',
        'extra': js(d.get('extra', 0)),
        'combis': json.dumps(d.get('combinaciones', []), ensure_ascii=False),
        'mini': js(d.get('miniatura', {}).get('fotos', {})),
        'miniimg': js(d.get('miniatura', {}).get('img', '')),
        'minialt': js(d.get('miniatura', {}).get('alt', {})),
        'minipaso': js(d.get('miniatura', {}).get('paso', 'correa')),
        'minilado': js(d.get('miniatura', {}).get('lado', 'izquierda')),
        'minisuelta': 'true' if d.get('miniatura', {}).get('suelta') else 'false',
        'pvpextra': json.dumps(
            {p['id']: {o['id']: o['pvp'] for o in ops if o.get('pvp')}
             for p, ops in dentro if any(o.get('pvp') for o in ops)},
            ensure_ascii=False),
        'vetos': json.dumps([v.split('·')[0].strip().strip('"') if '·' in v else v
                             for v in d.get('vetos', [])], ensure_ascii=False),
        'capa': json.dumps(d.get('montaje', {}).get('capas', {}), ensure_ascii=False, indent=2).replace('\n', '\n  '),
        'capaimg': js(d.get('montaje', {}).get('img', '')),
        'seriev': js(d.get('montaje', {}).get('v', '')),
        'pila': json.dumps(d.get('montaje', {}).get('pila', []), ensure_ascii=False),
        'cadena': js(d.get('cadena')) if d.get('cadena') else 'ORDEN',
        'vjsconf': V_JS_CONFIG,
        'tecnica': json.dumps(d.get('tecnica') or {}, ensure_ascii=False, indent=2),
    }



def presentacion(d):
    """El <img> de la foto de bienvenida, si el modelo la trae.

    Va con `fetchpriority="high"` y SIN `lazy`: es lo primero que se ve al
    abrir la ficha, así que pedirla tarde sería enseñar un hueco gris justo
    donde tiene que estar el reloj."""
    m = d.get('montaje', {})
    nombre = m.get('bienvenida')
    if not nombre:
        return ''
    base = '/assets/img/%s-2026/presentacion/' % d['slug']
    v = m.get('bienvenida_v', '?v=1')
    return ('        <img class="pv-presenta" data-pv-presenta\n'
            '             src="%(b)s1200/%(n)s.avif%(v)s"\n'
            '             srcset="%(b)s480/%(n)s.avif%(v)s 480w,\n'
            '                     %(b)s1200/%(n)s.avif%(v)s 1200w,\n'
            '                     %(b)s1600/%(n)s.avif%(v)s 1600w"\n'
            '             sizes="(max-width: 900px) 100vw, 620px"\n'
            '             fetchpriority="high" decoding="async" '
            'width="1200" height="1200"\n'
            '             alt="%(a)s">\n') % {
        'b': base, 'n': nombre, 'v': v,
        'a': esc(m.get('bienvenida_alt', 'Hazlo tuyo: el laOra ' + d['nombre']))}


def cuantas(d, dentro):
    """Cuántos relojes distintos se pueden comprar de verdad.

    NO es multiplicar los pasos. Ese número miente por tres sitios: el
    modelo puede decir qué combinaciones existen —el Trinchera monta la
    esfera Murph solo en sus dos numerales—, un paso puede depender de otro
    —el color de la correa, de su material— y un paso con la puerta cerrada
    no multiplica nada —el pespunte de un brazalete de acero—. Multiplicando
    a lo bruto, el Trinchera decía 297.600 y son 6.816.

    Y SOLO CUENTA LO QUE TIENE PRECIO. Una correa sin coste se dibuja pero
    no se vende, así que no es una combinación que nadie pueda comprar; el
    volcador la deja fuera del catálogo por la misma razón. Este número sale
    en la descripción de la página: tiene que ser el de verdad.

    NI LO VETADO, por lo mismo: si el catálogo no lo lleva, la página no lo
    puede anunciar. La firma se arma igual que en el motor —los pasos del
    contrato menos el tamaño, el calibre y la mariposa, y en blanco el paso
    cerrado—, que es lo que hace que una línea de `vetos` valga por las
    cuatro referencias."""
    pasos = [(p['id'], ops) for p, ops in dentro]
    NO_FIRMAN = ('tamano', 'mov', 'mariposa')
    firman = [i for i, _ in pasos if i not in NO_FIRMAN]
    vetos = set(v.split('·')[0].strip().strip('"') if '·' in v else v
                for v in d.get('vetos', []))
    puertas = d.get('puertas', {})
    filtros = d.get('filtros', {})
    cadena = d.get('cadena') or []
    combis = d.get('combinaciones') or []

    def abierta(idp, elegido):
        g = puertas.get(idp)
        if not g:
            return True
        o = elegido.get(g['paso'])
        return bool(o and o.get(g['campo']))

    def vale(idp, o, elegido):
        f = filtros.get(idp)
        if not f:
            return True
        padre = elegido.get(f['paso'])
        return bool(padre) and o.get(f['campo']) == padre['id']

    def anda(i, elegido):
        if i == len(pasos):
            if vetos and '|'.join(
                    (elegido[k]['id'] if k in elegido else '') for k in firman) in vetos:
                return 0
            # Con lista de combinaciones, la terna elegida tiene que estar.
            if combis and cadena:
                firma = {k: elegido[k]['id'] for k in cadena if k in elegido}
                if not any(all(c.get(k) == v for k, v in firma.items())
                           for c in combis):
                    return 0
            return 1
        idp, ops = pasos[i]
        if not abierta(idp, elegido):
            return anda(i + 1, elegido)
        n = 0
        for o in ops:
            if 'coste' not in o or o['coste'] is None:
                continue                      # sin coste no se vende
            if not vale(idp, o, elegido):
                continue
            elegido[idp] = o
            n += anda(i + 1, elegido)
            del elegido[idp]
        return n

    return anda(0, {})


def ficha(d):
    listo = bool(d.get('listo'))
    dentro, _fuera = pasos_del_modelo(d)
    # UNA FICHA SIN NINGÚN PASO NO SE INDEXA. Medusa y Barlovento existen
    # como página para poder empezar a llenarlas, pero hoy no tienen ni una
    # pieza decidida: dejar que Google las liste sería anunciar un reloj que
    # no existe. En cuanto tengan un paso, el noindex se cae solo.
    noindex = '' if dentro else '<meta name="robots" content="noindex">\n'

    combinaciones = cuantas(d, dentro)

    cuerpo = io.open(PLANTILLA, encoding='utf-8').read() % {
        'nombre': esc(d['nombre']),
        'codigo': esc((d.get('codigo') or '') + (' · ' if d.get('codigo') else '') + d.get('clase', '')),
        'nuevo': '<span class="cv2-chip pv-chip-oro">Nuevo</span>' if not listo else '',
        # LA FOTO DE BIENVENIDA. Óscar, 31/08/2026: «al abrir la página solo
        # aparece la imagen de inicio, y según se señale el tamaño de la
        # caja aparece la caja del reloj sola». Se declara en el JSON:
        #
        #     "montaje": { "bienvenida": "trinchera-hazlo-tuyo",
        #                  "bienvenida_alt": "…", "bienvenida_v": "?v=1" }
        #
        # SIN FOTO NO SE PONE NADA. El visor se queda con el montaje por
        # capas, que sin capas no dibuja: un marco vacío dice la verdad
        # mejor que una foto de otro reloj.
        'presentacion': presentacion(d),
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
        n = cuantas(d, dentro)
        print('%-11s %2d pasos · %5d combinaciones · %s'
              % (slug, len(dentro), n,
                 'a la venta' if d.get('listo') else 'sin precio, NO se vende'))
        if fuera:
            print('%-11s    sin salir: %s' % ('',
                  ', '.join('%s (%s)' % f for f in fuera)))


if __name__ == '__main__':
    main()
