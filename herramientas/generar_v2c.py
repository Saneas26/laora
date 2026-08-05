#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · CONFIGURADOR DEL LUNAR  (lunarv2c)
============================================================
Escribe `lunarv2c.html`, la segunda página de pruebas invisible. No
toca nada de lo publicado ni de `lunarv2`: hoja y script propios
(`lunarv2c.css` y `lunarv2c.js`).

QUÉ ES
------------------------------------------------------------
La pantalla de comprar el Lunar, con el patrón de configuración de un
coche que pidió Óscar el 05/08/2026:

    «puedo ver a la vez, sin mover el cursor ni el scroll, el modelo
     que estoy eligiendo, y abajo una barra fija que no se mueve con
     el precio constante de las opciones que voy escogiendo. Todas las
     opciones tienen que caber en una sola pantalla, en PC y en móvil.»

De ahí salen las tres decisiones de la página:

  1. El reloj no se mueve nunca. Cambiar de opción solo cambia la foto
     y las cifras; no se abre nada, no se despliega nada, no hay scroll.
  2. El precio vive en una barra pegada abajo, siempre visible.
  3. La página entera mide una pantalla: `height: 100svh` sin scroll.

Lo que se copia de esa referencia es el PATRÓN de interfaz —visor
quieto, barra de precio permanente, opciones que no desplazan nada—,
no su código ni su imagen: aquí todo va con la tipografía, la paleta y
el logotipo de laOra.

LOS DATOS SALEN DE `catalogo.json`. Ni un precio escrito a mano.

LAS COMBINACIONES QUE NO EXISTEN
------------------------------------------------------------
La matriz `precios[acabado][correa]` tiene huecos a `null`, y son la
información más importante de esta pantalla: hoy el Cenit solo se monta
con el brazalete de acero y el Eclipse solo con el brazalete negro. Esas
correas se enseñan apagadas y con el motivo en el título, en vez de
esconderlas: si desaparecieran, parecería que la opción no existe.

LAS FOTOS QUE FALTAN
------------------------------------------------------------
Óscar quiere que la foto sea la del reloj CON la correa elegida. Hoy en
el repositorio solo hay foto del Lunar de acero y del Lunar negro, no
una por cada combinación. Así que:

  · la caja sí es fiel: acero en Alba y Cenit, negra en Eclipse;
  · la correa la enseña la muestra grande de la esquina del visor.

`FOTOS` de abajo es el mapa «acabado|correa → foto». En cuanto exista
una foto real de una combinación, se añade ahí una línea y esa pareja
deja de usar la foto genérica del acabado. Faltan ocho fotos: seis del
Alba (una por correa), una del Cenit y una del Eclipse.

USO
    python3 herramientas/generar_v2c.py
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO: Cloudflare sirve el CSS con max-age=14400.
V_CSS = 9
V_JS = 3

with open(os.path.join(RAIZ, 'assets/datos/catalogo.json'), encoding='utf-8') as f:
    RELOJES = json.load(f)['relojes']

# Óscar dio la pantalla por buena el 05/08/2026 y dijo que las fichas
# individuales del resto de relojes van a ser como esta. Por eso el
# modelo es una constante y no está escrito por todo el fichero: para
# el siguiente basta con cambiar el slug y la tabla de fotos de abajo.
SLUG = 'lunar'

LUNAR = {x['slug']: x for x in RELOJES}[SLUG]
CFG = LUNAR['configurador']

IMG = '/assets/img/relojes-2026'
V2 = '/assets/img/lunar-v2'
LOGO = V2 + '/laora-wordmark-dark.png'   # cabecera clara → logotipo en tinta


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


# ============================================================
# LAS FOTOS
# ------------------------------------------------------------
# Por acabado, que es lo que hoy existe de verdad. El comentario de
# `catalogo.json` lo dice: `lunar-acero` es el Lunar de acero y
# `lunar-front` es el Eclipse, negro integral.
# ============================================================
FOTO_ACABADO = {
    'alba': f'{IMG}/lunar-acero.webp',
    'cenit': f'{IMG}/lunar-acero.webp',
    'eclipse': f'{IMG}/lunar-front.webp',
}

# Mapa «acabado|correa → foto» para las combinaciones que YA tengan su
# foto propia. Hoy está vacío a propósito: no hay ninguna. En cuanto
# Óscar traiga una, se añade aquí y el configurador la sirve sola.
#   'alba|piel-marron': f'{V2}/lunar-alba-piel-marron.webp',
FOTOS = {}

# ============================================================
# LAS MUESTRAS DE CORREA
# ------------------------------------------------------------
# Son el dibujo del material, no una foto ni un dato: sirven para ver
# de un vistazo qué se está eligiendo mientras no haya foto de cada
# combinación. El texto de cada correa —el que sí es información— sale
# tal cual de `catalogo.json`.
# ============================================================
MUESTRAS = {
    'brazalete-904l':
        'linear-gradient(150deg,#f2f3f4 0%,#b9bcc0 26%,#eef0f2 46%,#8f9398 70%,#d6d9dc 100%)',
    'brazalete-arroz':
        ('repeating-linear-gradient(135deg,#e9ebed 0 3px,#b7babe 3px 6px),'
         'linear-gradient(150deg,#eceef0,#9da1a6)'),
    'brazalete-acero':
        'linear-gradient(150deg,#eef0f1 0%,#b4b8bc 30%,#e6e8ea 52%,#93979c 76%,#cfd2d5 100%)',
    'brazalete-negro':
        'linear-gradient(150deg,#4a4c4e 0%,#232526 30%,#3d3f41 52%,#171819 78%,#303233 100%)',
    'piel-marron':
        ('repeating-linear-gradient(90deg,rgba(255,255,255,.05) 0 6px,rgba(0,0,0,.05) 6px 12px),'
         'linear-gradient(155deg,#8b5a33 0%,#6b4222 55%,#54331a 100%)'),
    'piel-negra':
        ('repeating-linear-gradient(90deg,rgba(255,255,255,.04) 0 6px,rgba(0,0,0,.06) 6px 12px),'
         'linear-gradient(155deg,#33322f 0%,#1e1d1c 55%,#131211 100%)'),
    'caucho':
        ('repeating-linear-gradient(45deg,rgba(255,255,255,.035) 0 4px,rgba(0,0,0,.05) 4px 8px),'
         'linear-gradient(150deg,#2b2c2d,#151616)'),
    'caucho-desplegable':
        ('repeating-linear-gradient(45deg,rgba(255,255,255,.035) 0 4px,rgba(0,0,0,.05) 4px 8px),'
         'linear-gradient(150deg,#343536 0%,#1a1b1b 60%,#4a4c4d 100%)'),
}

# ============================================================
# LA COMBINACIÓN DE PARTIDA
# La primera correa que tenga precio con el primer acabado, para que la
# pantalla abra siempre con algo que exista de verdad.
# ============================================================
ACABADOS = CFG['acabados']
CORREAS = CFG['correas']
PRECIOS = CFG['precios']


def disponible(acabado_id, indice):
    lista = PRECIOS.get(acabado_id, [])
    return indice < len(lista) and lista[indice] is not None


A_INICIAL = ACABADOS[0]['id']
C_INICIAL = next(i for i in range(len(CORREAS)) if disponible(A_INICIAL, i))
P_INICIAL = PRECIOS[A_INICIAL][C_INICIAL]

TODOS = [p for l in PRECIOS.values() for p in l if p is not None]


def ficha_corta(a):
    """Las cuatro líneas del acabado que de verdad cambian de uno a otro.
    Solo se escriben las que ese acabado tiene: lo que no esté confirmado
    en la hoja no se pinta, como en el resto del sitio."""
    filas = [('Movimiento', a.get('movimiento')),
             ('Cristal', a.get('cristal')),
             ('Caja', a.get('caja')),
             ('Estanqueidad', a.get('estanqueidad') or CFG['comunes'].get('Estanqueidad'))]
    return [[k, v] for k, v in filas if v]


def ficha_completa(a):
    """La ficha técnica entera del acabado, en los tres grupos del
    material aprobado. Solo se escribe la línea que tenga dato: lo que
    no esté confirmado en la hoja no se pinta, aquí tampoco."""
    c = CFG['comunes']
    grupos = [
        ('01', 'Movimiento', [
            ('MOVIMIENTO', a.get('movimiento')),
            ('TIPO', a.get('movimientoTipo')),
            ('FRECUENCIA', a.get('frecuencia')),
            ('AUTONOMÍA', a.get('autonomia')),
        ]),
        ('02', 'Caja y cristal', [
            ('CRISTAL', a.get('cristal')),
            ('CAJA', a.get('caja')),
            ('DIÁMETRO', c.get('Diámetro') or LUNAR.get('diametro')),
            ('ESTANQUEIDAD', a.get('estanqueidad') or c.get('Estanqueidad')),
            ('BISEL', a.get('bisel')),
            ('GROSOR', c.get('Grosor')),
        ]),
        ('03', 'Esfera y ajuste', [
            ('ESFERA', a.get('esfera') or c.get('Esfera')),
            ('LUMINISCENCIA', c.get('Luminiscencia')),
            ('ANCHO DE ASA', c.get('Ancho de asa')),
            ('CIERRE', c.get('Cierre')),
            ('FONDO', a.get('fondo') or c.get('Fondo')),
            ('CORONA', c.get('Corona')),
            ('PESO', a.get('peso')),
        ]),
    ]
    return [{'n': n, 'titulo': t, 'filas': [[k, v] for k, v in filas if v]}
            for n, t, filas in grupos]


DATOS = {
    'codigo': LUNAR['codigo'],
    'modelo': LUNAR['nombre'],
    'inicial': {'acabado': A_INICIAL, 'correa': C_INICIAL},
    'precios': PRECIOS,
    'fotos': FOTOS,
    'acabados': {a['id']: {'nombre': a['nombre'],
                           'descriptor': a.get('descriptor', ''),
                           'resumen': a.get('resumen', ''),
                           'refSufijo': a.get('refSufijo', ''),
                           'foto': FOTO_ACABADO.get(a['id'], LUNAR['foto']),
                           'ficha': ficha_corta(a),
                           'grupos': ficha_completa(a)} for a in ACABADOS},
    'correas': [{'id': c['id'], 'nombre': c['nombre'], 'detalle': c['detalle'],
                 'muestra': MUESTRAS.get(c['id'], '#d8d8d4')} for c in CORREAS],
}


def boton_acabado(a):
    desde = min([p for p in PRECIOS.get(a['id'], []) if p is not None] or [0])
    return (f'        <button type="button" data-acabado="{a["id"]}" aria-pressed="false">'
            f'<b>{a["nombre"]}</b><small>desde {euros(desde)}</small></button>\n')


def boton_correa(i, c):
    muestra = MUESTRAS.get(c['id'], '#d8d8d4')
    return (f'        <button type="button" data-correa="{i}" aria-pressed="false">'
            f'<span class="tira" style="background:{muestra}"></span>'
            f'<span>{c["nombre"]}</span></button>\n')


PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Configurador del Lunar de laOra: acabado, brazalete o correa y precio, en una sola pantalla.">
<!-- PÁGINA DE PRUEBAS: invisible a propósito, sin enlazar desde ningún sitio. -->
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#151715">
<title>Configura tu Lunar · laOra</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400&display=swap" rel="stylesheet">
<!-- GENERADO por herramientas/generar_v2c.py — no editar a mano. -->
<link rel="stylesheet" href="/assets/css/lunarv2c.css?v={V_CSS}">
</head>
<body>

<header class="cfg-cab">
  <span class="cfg-marca"><img src="{LOGO}" alt="laOra"><b>Lunar</b></span>
  <span class="ref">Ref. <span data-ref>—</span></span>
  <!-- El rótulo del enlace va en dos piezas: en el teléfono no caben
       cuatro palabras al lado del logotipo sin montarse encima de la
       referencia, y recortar con puntos suspensivos deja un enlace que
       no se entiende. -->
  <button class="cfg-ficha-boton" type="button" data-abre-ficha><span class="largo">Ver la ficha completa</span><span class="corto">Ficha</span></button>
</header>

<div class="cfg-cuerpo">

  <!-- EL VISOR · lo único que cambia al elegir, y sin moverse de sitio -->
  <section class="cfg-visor" aria-label="El reloj que estás configurando">
    <img class="cfg-foto" data-foto
         src="{FOTO_ACABADO[A_INICIAL]}"
         alt="Reloj laOra Lunar, acabado {ACABADOS[0]['nombre']}, con {CORREAS[C_INICIAL]['nombre'].lower()}"
         fetchpriority="high">
    <div class="cfg-muestra" aria-hidden="true">
      <span class="tira" data-muestra-tira style="background:{MUESTRAS.get(CORREAS[C_INICIAL]['id'], '#d8d8d4')}"></span>
      <span data-muestra-nombre>{CORREAS[C_INICIAL]['nombre']}</span>
    </div>
    <p class="cfg-viendo" data-viendo aria-live="polite"><b>{ACABADOS[0]['nombre']}</b> · {CORREAS[C_INICIAL]['nombre']}</p>
    <!-- La referencia también aquí: en el teléfono no cabe en la
         cabecera, y es el dato con el que Óscar busca en la hoja. -->
    <p class="cfg-ref-visor">Ref. <span data-ref>—</span></p>
  </section>

  <!-- LAS OPCIONES · todas a la vista, sin desplegar nada -->
  <section class="cfg-panel" aria-label="Opciones del Lunar">

    <div class="cfg-grupo">
      <p class="cfg-rotulo">Acabado <b>{len(ACABADOS)} opciones</b></p>
      <div class="cfg-acabados" role="group" aria-label="Elegir acabado">
{''.join(boton_acabado(a) for a in ACABADOS)}      </div>
      <p class="cfg-nota" data-nota>{ACABADOS[0].get('resumen', '')}</p>
    </div>

    <div class="cfg-grupo">
      <p class="cfg-rotulo">Brazalete o correa <b data-rotulo-correa>—</b></p>
      <div class="cfg-correas" role="group" aria-label="Elegir brazalete o correa">
{''.join(boton_correa(i, c) for i, c in enumerate(CORREAS))}      </div>
    </div>

    <div class="cfg-nota">
      <dl data-ficha></dl>
    </div>

  </section>
</div>

<!-- LA BARRA · pegada abajo, con el precio de lo elegido -->
<footer class="cfg-barra">
  <span class="lado">
    <span class="eleccion" data-eleccion>{ACABADOS[0]['nombre']} · {CORREAS[C_INICIAL]['nombre']}</span>
    <span class="ref">Ref. <span data-ref>—</span></span>
  </span>
  <span class="cfg-precio">
    <strong data-precio>{euros(P_INICIAL)}</strong>
    <span>Impuestos incluidos</span>
  </span>
  <button class="cfg-reservar" type="button" data-reservar>Reservar</button>
</footer>

<!-- LA FICHA TÉCNICA COMPLETA
     Se monta al pulsar y se tira al cerrar, como el overlay del
     material aprobado: mientras no está abierta, no existe en la
     página. No cambia la dirección ni mueve la pantalla de debajo.

     Los tres grupos —Movimiento, Caja y cristal, Esfera y ajuste— y el
     titular son los del material del 05/08/2026. Lo que cambia es de
     dónde salen los datos: NO van escritos, los rellena `lunarv2c.js`
     con la combinación que haya elegida en ese momento. Si el material
     los trajera escritos, quien configurase el Cenit —cuerda manual—
     leería la ficha del mecacuarzo del Alba. -->
<template data-plantilla-ficha>
  <div class="cfg-overlay" role="dialog" aria-modal="true" aria-labelledby="cfg-ficha-titulo">
    <div class="cfg-overlay-caja">
      <header class="cfg-overlay-cab">
        <div>
          <p>{LUNAR['codigo']} · FICHA TÉCNICA COMPLETA</p>
          <h2 id="cfg-ficha-titulo">Todo el {LUNAR['nombre']}.<br><em>Dato a dato.</em></h2>
        </div>
        <p class="cfg-overlay-ref"><span>Referencia</span><strong data-ref>—</strong></p>
        <button class="cfg-overlay-x" type="button" aria-label="Cerrar la ficha técnica" data-cierra-ficha>×</button>
      </header>
      <div class="cfg-overlay-grupos" data-grupos></div>
      <footer class="cfg-overlay-pie">
        <p data-overlay-resumen></p>
        <button class="cfg-ficha-boton" type="button" data-cierra-ficha>Cerrar ficha</button>
      </footer>
    </div>
  </div>
</template>

<script type="application/json" data-cfg>{json.dumps(DATOS, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
<script src="/assets/js/carrito.js?v=1"></script>
<script src="/assets/js/lunarv2c.js?v={V_JS}"></script>
</body>
</html>
"""

destino = os.path.join(RAIZ, 'lunarv2c.html')
with open(destino, 'w', encoding='utf-8') as f:
    f.write(PAGINA)

combinaciones = sum(1 for a in ACABADOS for i in range(len(CORREAS)) if disponible(a['id'], i))
print(f'lunarv2c.html escrito · {len(ACABADOS)} acabados · {len(CORREAS)} correas · '
      f'{combinaciones} combinaciones reales · de {euros(min(TODOS))} a {euros(max(TODOS))}')
faltan = [f'{a["nombre"]} + {CORREAS[i]["nombre"]}'
          for a in ACABADOS for i in range(len(CORREAS))
          if disponible(a['id'], i) and f'{a["id"]}|{CORREAS[i]["id"]}' not in FOTOS]
print(f'fotos propias que faltan ({len(faltan)}): ' + '; '.join(faltan))
