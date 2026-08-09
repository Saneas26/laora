#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · CONFIGURADOR DE CUATRO EJES  ·  MAQUETA
============================================================
Escribe una página por modelo —`lunar-nuevo.html`, `trinchera-nuevo.html`—
SUELTAS, que no enlaza nadie. `/lunar` y `/trinchera` siguen como están,
con su pantalla vieja y su hoja `configurador.css` sin tocar.

EL ORDEN LO FIJÓ ÓSCAR (08/08/2026)
------------------------------------------------------------
    «para el trinchera primero damos a elegir mecanismo, luego caja,
     luego esfera y luego brazalete»

Y antes, el mismo día:

    «las características tienen que estar por encima de brazalete»

Las dos cosas a la vez dan este orden, que vale para los ocho modelos:

    MOVIMIENTO → CAJA → ESFERA → características → BRAZALETE → variante

Las características van justo después de la esfera porque dependen de
las tres primeras elecciones: en cuanto están, ya se pueden escribir.

UN EJE CON UNA SOLA OPCIÓN NO SE PINTA
------------------------------------------------------------
No se le pide a nadie que elija entre una cosa. El Lunar tiene un solo
movimiento y el Precisa una sola caja: ahí va el dato, no un botón. El
Cóctel y el Diver no eligen esfera —viene dentro de la caja— y su eje
desaparece entero.

POR QUÉ LA CAJA VA EN FICHAS Y NO EN CUADROS
------------------------------------------------------------
El Trinchera tiene CATORCE cajas. Con los cuadros del brazalete —96 px
y su muestra dibujada— serían tres filas de 230 px y el panel se saldría
de la pantalla. Las fichas de texto miden 34 px de alto y las catorce
caben en tres renglones. Se encoge el envase, no la letra: el suelo
siguen siendo 12,5 px.

EL PRECIO
------------------------------------------------------------
Coste de las cuatro piezas × 2,7235, redondeado al 9,90 más cercano. Ni
una cifra escrita a mano. El multiplicador es el que reproduce exacta-
mente los 219,90 € que el Lunar tiene publicados hoy.

LOS DATOS
------------------------------------------------------------
`assets/datos/piezas.json`, volcado del libro `laora-biblioteca-materiales`
—pestañas Movimientos, Cajas, Esferas, Brazeletes y Compatibilidad— con
la numeración de piezas del 08/08/2026.

USO
    python3 herramientas/generar_configurador_v2.py
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO: Cloudflare sirve el CSS y el JS con max-age=14400.
V_CSS = 12
V_JS = 13

LOGO = '/assets/img/lunar-v2/laora-wordmark-dark.png'
MULT = 2.7235

with open(os.path.join(RAIZ, 'assets/datos/piezas.json'), encoding='utf-8') as f:
    PIEZAS = json.load(f)

# LAS FOTOS DE PIEZA
# ------------------------------------------------------------
# El nombre del archivo ES la referencia: no hay lista que mantener. La
# cabeza se busca en `cabezas/MODELO-CAJA-ESFERA.webp` y el brazalete en
# `brazaletes/REFERENCIA.webp`. Lo que no existe todavía sale con el
# aviso de «pendiente» y el brazalete dibujado de siempre.
#
# Las dos capas se montan con un SOLAPE: las mitades del brazalete se
# meten 45 px (de los 2400 del lienzo) dentro del hueco de la caja. La
# cabeza va encima y lo tapa, y así desaparece la rendija de luz que
# quedaba entre el último eslabón y la punta de las asas.
PIEZAS_IMG = '/assets/img/piezas'
SOLAPE = 45 / 2400          # en tanto por uno del alto del brazalete

def hay(rel):
    return os.path.exists(os.path.join(RAIZ, rel.lstrip('/')))


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


def redondea(p):
    """Al 9,90 más cercano. El 9,90 de abajo se saca restando ANTES de
    truncar; ver el porqué —y el fallo que provocó— en el JavaScript."""
    bajo = int((p - 9.90) // 10) * 10 + 9.90
    return bajo if (p - bajo) <= (bajo + 10 - p) else bajo + 10


# ============================================================
# LOS EJES
# ============================================================
def fijo(rotulo, titulo, apunte):
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">{rotulo} <b>uno solo</b></p>
      <div class="cf-fijo"><b>{titulo}</b><span>{apunte}</span></div>
    </div>'''


def eje_tarjetas(clave, rotulo, pregunta, opciones, etiqueta):
    """Tarjetas de ancho REPARTIDO: dos se llevan media pantalla cada una,
    tres un tercio. Óscar, 08/08/2026. Por eso la rejilla se declara con
    tantas columnas como opciones y no con `auto-fit`."""
    botones = '\n'.join(
        f'        <button class="cf-tarjeta" type="button" data-{clave}="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{etiqueta(o)}</button>'
        for i, o in enumerate(opciones))
    p = f'\n      <p class="cf-pregunta">{pregunta}</p>' if pregunta else ''
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">{rotulo} <b>{len(opciones)} opciones</b></p>{p}
      <div class="cf-tarjetas" style="grid-template-columns:repeat({len(opciones)},1fr)" role="group" aria-label="Elegir {rotulo.lower()}">
{botones}
      </div>
    </div>'''


def eje_sub(clave, rotulo, valores, etiquetas):
    """Un sub-eje de la caja: tamaño o color. Las opciones que no existen
    con lo ya elegido se apagan, no se esconden."""
    botones = '\n'.join(
        f'        <button class="cf-ficha" type="button" data-sub="{clave}" data-valor="{v}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{etiquetas.get(v, v)}</button>'
        for i, v in enumerate(valores))
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">{rotulo}</p>
      <div class="cf-fichas" role="group" aria-label="Elegir {rotulo.lower()}">
{botones}
      </div>
    </div>'''


def eje_grupos(clave, rotulo, grupos, opciones, nombres):
    """La esfera del Trinchera va agrupada por familia: Murph y Khaki."""
    bloques = []
    for g in grupos:
        bs = '\n'.join(
            f'          <button class="cf-ficha" type="button" data-{clave}="{i}" '
            f'aria-pressed="{"true" if i == 0 else "false"}">{nombres.get(o["ref"], o["nombre"])}</button>'
            for i, o in enumerate(opciones) if o['ref'] in g['refs'])
        bloques.append(f'''      <p class="cf-subrotulo">{g['nombre']}</p>
        <div class="cf-fichas" role="group" aria-label="Elegir esfera {g['nombre']}">
{bs}
        </div>''')
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">{rotulo} <b>{len(opciones)} opciones</b></p>
{chr(10).join(bloques)}
    </div>'''


def eje_fichas(clave, rotulo, opciones, etiqueta):
    botones = '\n'.join(
        f'        <button class="cf-ficha" type="button" data-{clave}="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{etiqueta(o)}</button>'
        for i, o in enumerate(opciones))
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">{rotulo} <b>{len(opciones)} opciones</b></p>
      <div class="cf-fichas" role="group" aria-label="Elegir {rotulo.lower()}">
{botones}
      </div>
    </div>'''


def eje_brazalete(familias, nombres):
    botones = '\n'.join(
        f'        <button class="cf-brazalete" type="button" data-brz="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">'
        f'<i></i><span>{nombres.get(f["id"], f["nombre"])}</span></button>'
        for i, f in enumerate(familias))
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Brazalete <b>{len(familias)} familias</b></p>
      <div class="cf-brazaletes" role="group" aria-label="Elegir brazalete">
{botones}
      </div>
      <p class="cf-detalle" data-detalle></p>
    </div>

    <div class="cf-grupo" data-grupo-var>
      <p class="cf-rotulo"><span data-rotulo-var>Acabado</span> <b data-cuenta-var></b></p>
      <div class="cf-variantes" data-variantes role="group" aria-label="Elegir acabado"></div>
    </div>'''


def pantalla(slug):
    d = PIEZAS[slug]
    mov, caj, esf, brz = d['mov'], d['caj'], d['esf'], d['brz']

    # El más barato posible: es lo único que puede decir un «desde».
    # Si el brazalete es un EXTRA sobre lo que ya trae la caja —el Diver—,
    # no cuenta para el mínimo.
    suelo_brz = 0 if (d['incluido'] and d['extra']) else min(v['c'] for f in brz for v in f['v'])
    suelo_esf = min(e['coste'] for e in esf) if esf else 0
    barato = min(m['coste'] for m in mov) + min(c['coste'] for c in caj) + suelo_esf + suelo_brz

    ej = d.get('ejes', {})
    ejes = []

    tm = (ej.get('mov') or {}).get('tarjetas', {})
    if len(mov) == 1:
        ejes.append(fijo('Movimiento', mov[0]['rot'], mov[0]['cal']))
    else:
        ejes.append(eje_tarjetas('mov', 'Movimiento', (ej.get('mov') or {}).get('pregunta'), mov,
                                 lambda o: tm.get(o['ref'], o['rot'])))

    sub = (ej.get('caja') or {}).get('sub')
    if sub:
        for s_ in sub:
            ejes.append(eje_sub(s_['clave'], s_['rotulo'], s_['valores'], s_.get('etiqueta', {})))
    elif len(caj) == 1:
        ejes.append(fijo('Caja', caj[0]['nombre'], euros(caj[0]['coste'])))
    else:
        ejes.append(eje_fichas('caja', 'Caja', caj, lambda o: o['nombre']))

    ge = (ej.get('esf') or {})
    if len(esf) > 1 and ge.get('grupos'):
        ejes.append(eje_grupos('esf', 'Esfera', ge['grupos'], esf, ge.get('nombres', {})))
    elif len(esf) > 1:
        ejes.append(eje_fichas('esf', 'Esfera', esf, lambda o: o['nombre']))
    elif len(esf) == 1:
        ejes.append(fijo('Esfera', esf[0]['nombre'], 'con sus agujas'))

    ejes.append('''    <div class="cf-grupo">
      <p class="cf-rotulo">Características</p>
      <dl class="cf-specs" data-specs></dl>
    </div>''')
    ejes.append(eje_brazalete(brz, (ej.get('brz') or {}).get('nombres', {})))

    # Se comprueba EN DISCO qué fotos existen ya. Así el día que el
    # diseñador entregue una tanda, basta con copiarla y regenerar.
    cabezas = {}
    for c in caj:
        for e in (esf or [None]):
            ref = d['codigo'] + '-' + c['ref'] + ('-' + e['ref'] if e else '')
            rel = f'{PIEZAS_IMG}/cabezas/{ref}.webp'
            if hay(rel):
                cabezas[ref] = rel
    brazaletes = {}
    for f_ in brz:
        for v in f_['v']:
            rel = f'{PIEZAS_IMG}/brazaletes/{v["ref"]}.webp'
            if hay(rel):
                brazaletes[v['ref']] = rel

    datos = json.dumps({**d, 'mult': MULT, 'cabezas': cabezas,
                        'brazaletes': brazaletes, 'solape': SOLAPE,
                        'fotoDefecto': '/assets/img/catalogo/LO-01_Lunar_A01.webp'},
                       ensure_ascii=False).replace('<', chr(92) + 'u003c')

    html = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Configura tu {d['nombre']} · laOra</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/configurador-v2.css?v={V_CSS}">

<header class="cf-cab">
  <a class="cf-marca" href="/coleccion.html" aria-label="Volver a la colección de laOra">
    <img src="{LOGO}" alt="laOra"><b>{d['nombre']}</b>
  </a>
  <p class="cf-ref">Ref. <b data-ref>—</b></p>
  <button class="cf-ficha-boton" type="button">Ver la ficha completa</button>
</header>

<div class="cf-cuerpo">

  <section class="cf-visor" aria-label="El reloj que estás configurando">
    <div class="cf-montaje" data-montaje>
      <img class="cf-brz arriba" data-brz-img hidden alt="" aria-hidden="true">
      <img class="cf-brz abajo"  data-brz-img hidden alt="" aria-hidden="true">
      <div class="cf-correa arriba" data-correa aria-hidden="true"></div>
      <div class="cf-cabeza" data-cabeza>
        <img data-foto src="/assets/img/catalogo/LO-01_Lunar_A01.webp" alt="{d['nombre']} de laOra">
        <p class="cf-pendiente" data-pendiente hidden>Foto pendiente</p>
      </div>
      <div class="cf-correa abajo" data-correa aria-hidden="true"></div>
    </div>

    <p class="cf-aviso-maqueta" data-aviso hidden>La foto es un montaje de dos capas: la cabeza
      del reloj y, detrás, el brazalete. Aquí el brazalete todavía va dibujado.</p>
  </section>

  <section class="cf-panel" aria-label="Opciones del {d['nombre']}">
{chr(10).join(ejes)}
  </section>
</div>

<footer class="cf-barra">
  <div class="cf-barra-izq"><b data-barra-nombre></b><span data-barra-var></span></div>
  <p class="cf-precio"><b data-precio></b><span>Impuestos incluidos</span></p>
  <button class="cf-reservar" type="button">Reservar</button>
</footer>

<script type="application/json" data-piezas>{datos}</script>
<script src="/assets/js/configurador-v2.js?v={V_JS}"></script>
'''
    return html, barato


for slug in PIEZAS:
    html, barato = pantalla(slug)
    with open(os.path.join(RAIZ, f'{slug}-nuevo.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    d = PIEZAS[slug]
    # Se cuentan las que EXISTEN, no las del producto de los cuatro ejes:
    # una esfera puede no entrar en una caja, y desde el 09/08/2026 el
    # brazalete tampoco (el metal del brazalete sigue al de la caja).
    compat = (d.get('ejes', {}).get('brz') or {}).get('compat') or {}
    esferas = d['esf'] or [None]
    combis = 0
    for c in d['caj']:
        ok = compat.get(c['ref'])
        nv = sum(1 for f in d['brz'] for v in f['v'] if ok is None or v['ref'] in ok)
        ne = sum(1 for e_ in esferas if e_ is None or not e_.get('cajas')
                 or e_['cajas'].lower().startswith('todas')
                 or c['ref'] in [s.strip() for s in e_['cajas'].split(',')])
        combis += len(d['mov']) * ne * nv
    print(f'{slug}-nuevo.html · {combis} configuraciones'
          f' · desde {euros(redondea(barato * MULT))}')
