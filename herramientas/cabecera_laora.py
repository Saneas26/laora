#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LA CABECERA, UNA SOLA VEZ
============================================================
Óscar, 06/08/2026: «por el momento coloca la misma head en todas las
páginas».

Hasta hoy había cuatro cabeceras distintas, una por generador. Ahora
hay una, y vive aquí. La importan:

    generar.py                 → colección, filosofía, taller, club
    generar_configuradores.py  → las ocho pantallas de comprar
    generar_v2.py              → la portada
    generar_carrito.py         → el carrito
    generar_cuenta.py          → la cuenta

El panel NO la lleva: es el cuarto de atrás, no la tienda.

CÓMO SE USA
    from cabecera_laora import RECURSOS, marcado
    ...  {RECURSOS}          en el <head>
    ...  {marcado('relojes')} donde vaya la cabecera
    ...  {SCRIPT}            antes de cerrar el <body>

`marcado()` recibe cuál de las cinco secciones está activa, para
subrayarla: relojes · filosofia · taller · club · laorateca. Sin
argumento, ninguna.
"""

# SUBIR EN CADA CAMBIO de la hoja o del script: Cloudflare los sirve
# con max-age=14400 y sin esto el navegador se queda con la versión
# vieja hasta cuatro horas.
V_CAB_CSS = 2
V_CAB_JS = 1

_LOGO = '/assets/img/lunar-v2/laora-wordmark-dark.png?v=2'   # tinta, sobre fondo claro

RECURSOS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">\n'
    f'<link rel="stylesheet" href="/assets/css/cabecera-laora.css?v={V_CAB_CSS}">'
)

SCRIPT = f'<script src="/assets/js/cabecera-laora.js?v={V_CAB_JS}"></script>'


def _marca(clase, sufijo=''):
    """El logotipo NUNCA se escribe: va en imagen. `laOrateca` es el
    logotipo más el sufijo, para que no salga «LAORATECA» cuando el
    rótulo esté en versales."""
    return f'<span class="{clase}"><img src="{_LOGO}" alt="laOra">{sufijo}</span>'


_SECCIONES = [
    ('relojes',   '/coleccion.html',            'Relojes'),
    ('filosofia', '/filosofia.html',            None),          # «Por qué laOra»
    ('taller',    '/taller.html',               'Taller'),
    ('club',      '/club.html',                 None),          # «Club laOra»
    ('laorateca', '/laorateca.html',            None),          # «laOrateca»
]


def marcado(activa=''):
    enlaces = []
    for clave, url, texto in _SECCIONES:
        clase = ' class="active"' if clave == activa else ''
        if texto:
            dentro = texto
        elif clave == 'filosofia':
            dentro = 'Por qué ' + _marca('brand-word')
        elif clave == 'club':
            dentro = 'Club ' + _marca('brand-word')
        else:
            dentro = _marca('brand-word', 'teca')
        enlaces.append(f'    <a href="{url}"{clase}>{dentro}</a>')
    nav = '\n'.join(enlaces)

    return f"""<header class="site-header">
  <a class="brand" href="/" aria-label="laOra, inicio">{_marca('brand-logo')}</a>
  <button class="menu-toggle" type="button" aria-label="Abrir menú" aria-expanded="false" data-menu>
    <span></span><span></span>
  </button>
  <nav class="main-nav" aria-label="Navegación principal" data-nav>
{nav}
  </nav>
  <div class="header-actions">
    <a class="header-icon profile-icon" href="/cuenta" aria-label="Tu cuenta"><span aria-hidden="true"></span></a>
    <!-- `data-carrito-cuenta` es lo que busca `carrito.js` para pintar
         cuántas unidades hay. Sale oculto y aparece solo si hay algo:
         un cero permanente al lado del carrito parece una web rota. -->
    <a class="header-icon bag-icon" href="/carrito" aria-label="Tu carrito"><span aria-hidden="true"></span><b data-carrito-cuenta hidden>0</b></a>
  </div>
</header>"""
