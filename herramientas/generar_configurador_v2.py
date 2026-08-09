#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · CONFIGURADOR DE TRES EJES  ·  MAQUETA DEL LUNAR
============================================================
Escribe `lunar-nuevo.html`, una página SUELTA que no enlaza nadie.
`/lunar` sigue como está, con su pantalla de dos ejes y su hoja
`configurador.css` sin tocar. Esto es para mirarlo y decidir.

DE DÓNDE SALE (Óscar, 08/08/2026)
------------------------------------------------------------
    «desde el ordenador cuando llego a la ficha única de un reloj,
     ahora tengo tres opciones que elegir, movimiento, solo aquellos
     que tengan disponibles más de uno... caja si hay más de una
     igualmente, y correa brazalete donde sí habrá muchas opciones.
     Pero para que quepa en la misma pantalla, las opciones del
     brazalete, las cuadrículas tienen que ser más pequeñas. Y las
     características tienen que estar por encima de brazalete correa.»

De ahí, punto por punto:

  · Un eje con UNA sola opción no se pinta como elección. El Lunar
    tiene un solo movimiento —el VK63, desde que se retiró el
    ST1901— así que ahí no hay nada que elegir: se enseña el dato.
  · Las características suben por encima del brazalete.
  · Los cuadros del brazalete miden 96 px, no 150.
  · Debajo del brazalete, la paleta de color de esa familia.

LOS DATOS SON PROVISIONALES
------------------------------------------------------------
Salen de `assets/datos/piezas-lunar.json`, un volcado a mano de las
pestañas Movimientos, Cajas y Brazeletes del libro de materiales tal
como estaban el 08/08/2026. En cuanto se decida cómo quedan las tres
bibliotecas, esto se genera solo y ese fichero desaparece.

LOS NOMBRES PÚBLICOS ESTÁN SIN APROBAR
------------------------------------------------------------
En la hoja, cinco brazaletes se llaman «tipo Rolex», «tipo Omega»,
«tipo Daytona», «tipo Breitling» y «Ostra». En una página de venta no
puede salir ni uno. Los nombres que se leen aquí me los he inventado
yo para poder maquetar; hay que repasarlos uno a uno.

LA FOTO ES UN MONTAJE, NO UNA FOTO
------------------------------------------------------------
Óscar eligió el 08/08/2026 el montaje de dos capas: la cabeza del
reloj recortada de su foto, y detrás la banda del brazalete. Aquí la
banda todavía se DIBUJA con un degradado; cuando lleguen las fotos de
brazalete se cambia el degradado por un `<img>` y no se toca nada más.

El Lunar de bisel azul no tiene foto todavía: enseña la del negro con
un aviso encima, para que no se confunda con una foto real.

USO
    python3 herramientas/generar_configurador_v2.py
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO: Cloudflare sirve el CSS y el JS con max-age=14400.
V_CSS = 6
V_JS = 6

LOGO = '/assets/img/lunar-v2/laora-wordmark-dark.png'

with open(os.path.join(RAIZ, 'assets/datos/piezas-lunar.json'), encoding='utf-8') as f:
    D = json.load(f)


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


def redondea(p):
    """Al 9,90 más cercano. El 9,90 de abajo se saca restando ANTES de
    truncar; ver el porqué —y el fallo que provocó— en
    `configurador-v2.js`."""
    bajo = int((p - 9.90) // 10) * 10 + 9.90
    alto = bajo + 10
    return bajo if (p - bajo) <= (alto - p) else alto


def pvp(mov, caja, color):
    return redondea((mov['coste'] + caja['coste'] + color['coste']) * D['multiplicador'])


MOV = D['movimientos']
CAJAS = D['cajas']
BRZ = D['brazaletes']

# El precio de arranque y el más barato posible, que es el que va en el
# rótulo del grupo: «desde X» tiene que ser verdad.
BARATO = min(pvp(MOV[0], c, col) for c in CAJAS for b in BRZ for col in b['colores'])


# ============================================================
# EL EJE DEL MOVIMIENTO
# ------------------------------------------------------------
# Con una sola opción no se pinta un grupo de botones: se pinta el
# dato. Pedirle a alguien que elija entre una cosa es hacerle perder
# un segundo y ensuciar la pantalla. Con dos o más, botones.
# ============================================================
def eje_movimiento():
    if len(MOV) == 1:
        m = MOV[0]
        return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Movimiento <b>uno solo</b></p>
      <div class="cf-fijo"><b>{m['nombre']}</b><span>{m['tipo']}</span></div>
    </div>'''
    botones = '\n'.join(
        f'        <button class="cf-caja" type="button" data-mov="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">'
        f'<b>{m["nombre"]}</b><span>{m["tipo"]}</span></button>'
        for i, m in enumerate(MOV))
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Movimiento <b>{len(MOV)} opciones</b></p>
      <div class="cf-cajas" role="group" aria-label="Elegir movimiento">
{botones}
      </div>
    </div>'''


def eje_caja():
    if len(CAJAS) == 1:
        c = CAJAS[0]
        return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Caja <b>una sola</b></p>
      <div class="cf-fijo"><b>{c['nombre']}</b><span>{c['specs'][1][1]}</span></div>
    </div>'''
    botones = '\n'.join(
        f'        <button class="cf-caja" type="button" data-caja="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">'
        f'<b>{c["nombre"]}</b><span>{c["specs"][3][1]}</span></button>'
        for i, c in enumerate(CAJAS))
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Caja <b>{len(CAJAS)} opciones</b></p>
      <div class="cf-cajas" role="group" aria-label="Elegir caja">
{botones}
      </div>
    </div>'''


def eje_brazalete():
    botones = '\n'.join(
        f'        <button class="cf-brazalete" type="button" data-brz="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">'
        f'<i style="background:{b["colores"][0]["muestra"]}"></i>'
        f'<span>{b["nombre"]}</span></button>'
        for i, b in enumerate(BRZ))
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Brazalete <b>{len(BRZ)} familias</b></p>
      <div class="cf-brazaletes" role="group" aria-label="Elegir brazalete">
{botones}
      </div>
      <p class="cf-detalle" data-detalle></p>
    </div>

    <div class="cf-grupo" data-grupo-color>
      <p class="cf-rotulo"><span data-rotulo-variante>Color</span></p>
      <div class="cf-colores" data-colores role="group" aria-label="Elegir color"></div>
    </div>'''


PAGINA = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Configura tu {D['nombre']} · laOra</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/configurador-v2.css?v={V_CSS}">

<header class="cf-cab">
  <a class="cf-marca" href="/coleccion.html" aria-label="Volver a la colección de laOra">
    <img src="{LOGO}" alt="laOra"><b>{D['nombre']}</b>
  </a>
  <p class="cf-ref">Ref. <b data-ref>—</b></p>
  <button class="cf-ficha-boton" type="button">Ver la ficha completa</button>
</header>

<div class="cf-cuerpo">

  <section class="cf-visor" aria-label="El reloj que estás configurando">
    <div class="cf-rotulos"><p class="cf-viendo" data-viendo aria-live="polite"></p></div>

    <div class="cf-montaje">
      <div class="cf-correa arriba" data-correa aria-hidden="true"></div>
      <div class="cf-cabeza">
        <img data-foto src="{CAJAS[0]['foto']}" alt="{D['nombre']} de laOra">
        <p class="cf-pendiente" data-pendiente hidden>Foto del bisel azul pendiente</p>
      </div>
      <div class="cf-correa abajo" data-correa aria-hidden="true"></div>
    </div>

    <p class="cf-desglose" data-desglose></p>
    <p class="cf-aviso-maqueta">La foto es un montaje de dos capas: la cabeza del reloj
      y, detrás, el brazalete. Aquí el brazalete todavía va dibujado.</p>
  </section>

  <section class="cf-panel" aria-label="Opciones del {D['nombre']}">
{eje_movimiento()}

{eje_caja()}

    <div class="cf-grupo">
      <p class="cf-rotulo">Características</p>
      <dl class="cf-specs" data-specs></dl>
    </div>

{eje_brazalete()}
  </section>
</div>

<footer class="cf-barra">
  <div class="cf-barra-izq">
    <b data-barra-nombre></b><span data-barra-color></span>
  </div>
  <p class="cf-precio"><b data-precio></b><span>Impuestos incluidos</span></p>
  <button class="cf-reservar" type="button">Reservar</button>
</footer>

<script type="application/json" data-piezas>{json.dumps(D, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
<script src="/assets/js/configurador-v2.js?v={V_JS}"></script>
'''

destino = os.path.join(RAIZ, 'lunar-nuevo.html')
with open(destino, 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print(f'lunar-nuevo.html escrito · {len(MOV)} movimiento(s) · {len(CAJAS)} cajas · '
      f'{len(BRZ)} familias de brazalete · desde {euros(BARATO)}')
