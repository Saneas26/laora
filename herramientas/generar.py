#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · GENERADOR DE PÁGINAS
============================================================
La web es HTML estático y sin proceso de compilación: lo que se sube a
Cloudflare son los .html que este fichero escribe. Lo que se evita con él
es la duplicación — la cabecera y el pie viven una sola vez.

MARCADO PORTADO TAL CUAL del material de Codex 2026-08-03 (`so/app`), que
venía en Next.js. Mismas clases, misma estructura y mismo orden de
secciones, para que el diseño salga idéntico con `assets/css/laora.css`,
que es su globals.css verbatim.

Lo único que no viene de ahí son la cabecera y el pie del Grupo Saneas,
que Óscar pidió conservar.

USO
    python3 herramientas/generar.py

Reescribe index.html, las cuatro páginas de sección y las ocho fichas.
NO toca privacidad.html, que se mantiene a mano.

Los datos de los relojes salen de assets/datos/catalogo.json, que es la
única fuente de verdad. No hay ni un dato de reloj escrito en un HTML.
"""

import json
import os
import sys

# La cabecera es la MISMA en todas las páginas desde el 06/08/2026 y vive
# en un solo sitio. Ver `herramientas/cabecera_laora.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cabecera_laora import (RECURSOS as CABECERA_RECURSOS,
                            SCRIPT as CABECERA_SCRIPT,
                            marcado as cabecera_comun)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO del fichero correspondiente: Cloudflare los sirve con
# max-age=14400 y sin esto el navegador se queda hasta cuatro horas con la
# versión antigua. Vale igual para el CSS que para el JS.
V_CSS = 41
V_CAB = 15
V_JS_HOME = 8
V_JS_FICHA = 14

# RELOJES QUE NO SE ENSEÑAN
# ------------------------------------------------------------
# 06/08/2026, Óscar: «hay que quitar el bauhaus». No está en el catálogo
# activo —no tiene configurador, ni precio, ni referencias en la hoja—,
# así que en la colección salía como una tarjeta que no lleva a ninguna
# venta. Se queda su ficha en `catalogo.json` por si algún día vuelve;
# lo que desaparece es su sitio en la web.
FUERA = {'bauhaus'}

with open(os.path.join(RAIZ, 'assets/datos/catalogo.json'), encoding='utf-8') as f:
    RELOJES = [r for r in json.load(f)['relojes'] if r['slug'] not in FUERA]

RELOJ = {r['slug']: r for r in RELOJES}
IMG = '/assets/img/relojes-2026'

# ============================================================
# EL LOGOTIPO NUNCA SE ESCRIBE
# ------------------------------------------------------------
# «laOra» no es una palabra: es el logotipo canónico, en Nunito Sans,
# todo en minúsculas salvo la O, que es el isotipo — el círculo con el
# triángulo invertido apuntando a las 12. Puede cambiar de COLOR según
# el fondo, pero nunca de fuente, de caja ni de forma.
#
# Por eso en cualquier rótulo en versales («COLECCIÓN laOra · 2026»,
# «Taller laOra · Madrid») va este trozo y no la palabra escrita: el
# `text-transform:uppercase` del rótulo lo habría convertido en «LAORA».
#
# El círculo es un span vacío, así que un lector de pantalla leería
# «lara»: al lado va la palabra, invisible pero audible.
# ============================================================
MARCA = ('<span class="cb-marca" aria-hidden="true">la<span class="o"></span>ra</span>'
         '<span class="solo-lectores">laOra</span>')


# ============================================================
# EL BLOQUE «01» DE LA FICHA
# ------------------------------------------------------------
# Por defecto explica el homenaje. El reloj que traiga `comparativa`
# lo cambia por una tabla que pone su precio al lado del de las
# referencias de su misma clase — Óscar quiere que esa comparación
# se vea, y que se vea en todos los modelos según se vayan cerrando.
# ============================================================

def historia_o_comparativa(r):
    c = r.get('comparativa')
    if not c:
        return f"""  <section class="pdp-story">
    <div>
      <p class="section-number">01 — EL HOMENAJE</p>
      <h2>Una referencia reconocible.<br><em>Una marca honesta.</em></h2>
    </div>
    <div>
      <p>{r['historia']}</p>
      <p>La esfera lleva únicamente el nombre {MARCA} y el del modelo. No utilizamos marcas, coronas, escudos ni emblemas de terceros.</p>
    </div>
  </section>"""

    def celda(f, clave, etiqueta):
        return '<td data-col="' + etiqueta + '">' + f[clave] + '</td>'

    NL = chr(10)
    filas = []
    for f in c['filas']:
        n = f['estrellas']
        # el nombre propio se dibuja con el logotipo, nunca escrito
        nombre = (MARCA + ' ' + f['modelo']) if f.get('nuestra') else f['modelo']
        clase = ' class="nuestra"' if f.get('nuestra') else ''
        filas.append(
            '          <tr' + clase + '>' + NL
            + '            <td class="cmp-estrellas">'
            + '<span aria-hidden="true">' + '★' * n + '☆' * (5 - n) + '</span>'
            + '<span class="solo-lectores">' + str(n) + ' de 5</span></td>' + NL
            + '            <th scope="row" data-col="Modelo">' + nombre + '</th>' + NL
            + '            ' + celda(f, 'pvp', 'PVP')
            + celda(f, 'mecanica', 'Calidad mecánica')
            + celda(f, 'precision', 'Precisión')
            + celda(f, 'mantenimiento', 'Mantenimiento') + NL
            + '          </tr>')

    cuerpo = '\n      '.join(f'<p>{t}</p>' for t in c['cuerpo'])
    cabeceras = '\n            '.join(
        f'<th scope="col">{t}</th>' for t in c['columnas'])

    return f"""  <section class="pdp-story pdp-comparativa">
    <div>
      <p class="section-number">{c['antetitulo']}</p>
      <h2>{c['titular']}</h2>
    </div>
    <div>
      {cuerpo}
      <p class="cmp-destacado">{c['destacado']}</p>
    </div>

    <div class="cmp-tabla">
      <table>
        <thead>
          <tr><th scope="col"><span class="solo-lectores">Valoración</span></th>
            {cabeceras}
          </tr>
        </thead>
        <tbody>
{NL.join(filas)}
        </tbody>
      </table>
      <p class="cmp-aviso">{c['aviso']}</p>
    </div>
  </section>"""


# ============================================================
# PARTES COMUNES
# ============================================================

def cabeza(titulo, descripcion, url, foto=f'{IMG}/bitacora-hero-full.webp'):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{descripcion}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="https://laora.es{url}">
<meta property="og:image" content="https://laora.es{foto}">
<meta property="og:locale" content="es_ES">
<meta property="og:type" content="website">
<title>{titulo}</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/manifest.json">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<!-- El diseño va en Georgia y Arial, como el original. Inter solo lo usa
     la palabra «Saneas» del pie, y Nunito Sans el logotipo. -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600&family=Nunito+Sans:wght@400&display=swap" rel="stylesheet">
<!-- GENERADO por herramientas/generar.py — no editar a mano.
     Los textos se cambian ahí; los datos de relojes, en
     assets/datos/catalogo.json. -->
<link rel="stylesheet" href="/assets/css/laora.css?v={V_CSS}">
{CABECERA_RECURSOS}
<!-- `cabecera.css` ya NO dibuja la cabecera —eso lo hace la común desde
     el 06/08/2026—, pero sigue haciendo falta: dentro está `.cb-marca`,
     el logotipo dibujado con la O como círculo, que estas páginas usan
     en los rótulos y en los textos de las fichas. Sin él se lee «lara». -->
<link rel="stylesheet" href="/assets/css/cabecera.css?v={V_CAB}">
</head>
<body>"""


def cabecera(activa=''):
    """LA MISMA EN TODAS LAS PÁGINAS desde el 06/08/2026, por encargo de
    Óscar: «coloca la misma head en todas las páginas».

    Hasta hoy había cuatro cabeceras distintas —esta, la de la portada,
    la de las pantallas de comprar y la del carrito— y navegar por el
    sitio parecía saltar entre cuatro webs. Ahora la dibuja una sola,
    `herramientas/cabecera_laora.py`.

    Aquí solo se traduce el nombre de la sección: esta parte del sitio
    la llamaba `coleccion` y la cabecera común la llama `relojes`."""
    return cabecera_comun({'coleccion': 'relojes'}.get(activa, activa))


# El aviso legal del pie es lo que separa «homenaje» de «falsificación» a
# ojos de quien lea la web. No se quita de ninguna página. Es el mismo texto
# que llevaba el pie del material original.
PIE = """
<footer>
  <a class="cb-marca" href="#inicio" aria-label="laOra, volver arriba">la<span class="o"></span>ra<sup>®</sup></a>
  <div class="pie-links">
    <a href="/coleccion.html">Relojes</a>
    <a href="/filosofia.html">Nuestra forma de hacer</a>
    <a href="/taller.html">Taller</a>
    <a href="/club.html">Club laOra</a>
    <a href="/privacidad.html">Privacidad</a>
  </div>
  <p class="pie-aviso">
    laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos
    ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje;
    no implican afiliación con sus fabricantes.
  </p>

  <!-- Rejilla del Grupo Saneas, la misma que el resto del sitio -->
  <div class="fg-title">Grupo <span class="saneas">Saneas</span></div>
  <div class="gp-grid">
    <a class="gp-item" href="https://saneas.es" target="_blank" rel="noopener">
      <img src="/assets/img/app-saneas-web.png" alt="Saneas web" loading="lazy"><b>Saneas web</b>
    </a>
    <a class="gp-item" href="https://saneas.es/instala-app" target="_blank" rel="noopener">
      <img src="/assets/img/app-saneas.png" alt="Saneas app" loading="lazy"><b>Saneas app</b>
    </a>
    <a class="gp-item" href="https://saneas.es/asesorias" target="_blank" rel="noopener">
      <span class="gp-ico"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span><b>Asesorías</b>
    </a>
    <a class="gp-item" href="https://pordondevoy-saneas.vercel.app" target="_blank" rel="noopener">
      <img src="/assets/img/app-pordondevoy.png" alt="APP Pordondevoy" loading="lazy"><b>Pordondevoy</b>
    </a>
    <a class="gp-item" href="https://activala.es" target="_blank" rel="noopener">
      <img src="/assets/img/app-activala.png" alt="Activala" loading="lazy"><b>Activala</b>
    </a>
    <a class="gp-item" href="https://acumula.es" target="_blank" rel="noopener">
      <img src="/assets/img/app-acumula.png?v=2" alt="APP Acumula" loading="lazy"><b>Acumula</b>
    </a>
  </div>

  <small>© 2026 laOra® · Todos los derechos reservados</small>
</footer>"""


def final_cta(kicker, titular, href, boton, href2, enlace2):
    return f"""
  <section class="final-cta">
    <p class="kicker">{kicker}</p>
    <h2>{titular}</h2>
    <div class="button-row">
      <a class="button primary" href="{href}">{boton}</a>
      <a class="text-link" href="{href2}">{enlace2}</a>
    </div>
  </section>"""


def scripts(extra=''):
    return f"""
{CABECERA_SCRIPT}{extra}
<script src="/assets/js/telemetria.js" defer></script>
</body>
</html>
"""


def precio_es(valor):
    """Precio en euros a la española. Con None devuelve cadena vacía."""
    if valor is None:
        return ''
    if float(valor).is_integer():
        return f'{int(valor):,}'.replace(',', '.') + ' €'
    return f'{valor:,.2f}'.replace(',', '@').replace('.', ',').replace('@', '.') + ' €'


# El original enseñaba «desde X €» en `.product-meta`. Mientras no haya
# precio cerrado en catalogo.json ese hueco lleva el diámetro, que es el
# otro dato que el visitante compara de un vistazo. Nunca una cifra
# inventada ni un «—».
def desde(r):
    """El precio más bajo que se puede pedir de verdad.

    Sale del CONFIGURADOR, que es lo que se volcó de la hoja, y no del
    campo `precio` del reloj: ese estaba escrito a mano y se quedó viejo
    en cuanto la hoja cambió. El listado enseñaba 169,90 € del Precisa
    cuando su Alba ya valía 199,90."""
    cfg = r.get('configurador')
    if cfg:
        vivos = [p for l in cfg['precios'].values() for p in l if p is not None]
        if vivos:
            return min(vivos)
    return r.get('precio')


def linea(clase, texto):
    """Un párrafo, o nada. Lo que no está escrito no se pinta: el Diver
    entró el 06/08/2026 con sus datos de la hoja y sin frase ni
    homenaje, que los escribe Óscar, y un <p> vacío deja un hueco raro
    en la tarjeta."""
    return f'            <p class="{clase}">{texto}</p>\n' if texto else ''


def tarjeta(r):
    p = desde(r)
    dato = 'desde ' + precio_es(p) if p is not None else r['diametro']
    return f"""          <article class="product-card">
            <a class="product-visual" href="/{r['slug']}.html">
              <img src="{r['foto']}" alt="Reloj {r['nombre']} de laOra" loading="lazy">
              <span class="product-code">{r['codigo']}</span>
              <span class="product-arrow" aria-hidden="true">↗</span>
            </a>
            <div class="product-meta"><p>{r['familia']}</p><p>{dato}</p></div>
            <h3><a href="/{r['slug']}.html">{r['nombre']}</a></h3>
{linea('product-line', r.get('frase'))}{linea('homage-label', r.get('homenaje'))}          </article>"""


# El «móvil» de Club laOra, calcado del componente ClubPhone del material.
TELEFONO = f"""        <div class="phone" role="img" aria-label="Vista previa de la aplicación Club laOra">
          <div class="phone-bar"><span>9:41</span><i></i></div>
          <div class="phone-greeting"><div><small>Buenos días</small><b>Tu Club laOra</b></div><span>OM</span></div>
          <div class="phone-member"><span>MIEMBRO Nº 0026</span><span>480 PUNTOS</span></div>
          <div class="phone-watch"><img src="{IMG}/tortuga-detail.webp" alt=""><div><small>MI RELOJ · LO—08</small><b>Tortuga</b><span>Garantía activa</span></div></div>
          <div class="phone-actions"><span><b>▤</b>Factura</span><span><b>◇</b>Garantía</span><span><b>↗</b>Taller</span></div>
          <div class="phone-notice"><small>SERVICIO</small><b>Tu revisión está al día</b><span>Ver pasaporte digital →</span></div>
          <div class="phone-nav"><span>⌂</span><span>◫</span><span>◎</span><span>○</span></div>
        </div>"""


def escribir(nombre, contenido):
    with open(os.path.join(RAIZ, nombre), 'w', encoding='utf-8') as f:
        f.write(contenido)
    print('  ✓ ' + nombre)


# ============================================================
# HOME
# ============================================================

# Los cuatro destacados son los mismos que elegía el material.
# El Bauhaus salía aquí y se fue con el resto (06/08/2026). En su sitio
# entra el Diver, que sí está a la venta.
DESTACADOS = ['tortuga', 'precisa', 'diver', 'lunar']

CAPAS = [
    ('01', 'Cristal', 'Zafiro cuando la configuración lo incluye.'),
    ('02', 'Caja', 'Acero 316L o titanio según acabado.'),
    ('03', 'Esfera', 'Nombre y emblema laOra. Ninguna marca ajena.'),
    ('04', 'Movimiento', 'Siempre identificado; nunca descrito con vaguedades.'),
    ('05', 'Cierre', 'Construcción y ajuste explicados en cada ficha.'),
]

# ESTA YA NO ES LA PORTADA. El 05/08/2026 Óscar puso de portada la del
# material aprobado, que la escribe `herramientas/generar_v2.py` en
# `index.html`. Esta se sigue generando para no perderla y para poder
# comparar, pero vive en `home-anterior.html` y no está enlazada desde
# ninguna parte. Si algún día se vuelve a ella, se cambia este nombre
# por `index.html` y se quita el suyo del otro generador: son los dos
# únicos sitios donde se decide quién es la portada.
escribir('home-anterior.html', cabeza(
    'laOra · Homenajes honestos a los iconos de la relojería',
    'Relojes homenaje con marca propia, componentes identificados y montaje, ajuste, control y servicio en Madrid.',
    '/home-anterior.html') + cabecera() + f"""

<main>

  <section class="home-hero" id="inicio">
    <div class="hero-slideshow" role="img" aria-label="Reloj laOra Bitácora: vista completa, detalle de la esfera y movimiento automático">
      <img class="hero-slide hero-slide-full is-active" src="{IMG}/bitacora-hero-full.webp" alt="" aria-hidden="true" fetchpriority="high" decoding="async">
      <img class="hero-slide hero-slide-dial" src="{IMG}/bitacora-hero-dial.webp" alt="" aria-hidden="true" decoding="async">
      <img class="hero-slide hero-slide-movement" src="{IMG}/bitacora-hero-movement.webp" alt="" aria-hidden="true" decoding="async">
      <div class="hero-veil" aria-hidden="true"></div>

      <div class="hero-caption">
        <span>LO—02</span>
        <strong>Bitácora</strong>
        <small>Homenaje al deportivo integrado</small>
        <div class="hero-controls" aria-label="Control de imágenes">
          <button type="button" class="is-active" data-slide="0" aria-label="Mostrar imagen 1 de 3" aria-pressed="true"><span></span></button>
          <button type="button" data-slide="1" aria-label="Mostrar imagen 2 de 3" aria-pressed="false"><span></span></button>
          <button type="button" data-slide="2" aria-label="Mostrar imagen 3 de 3" aria-pressed="false"><span></span></button>
          <button type="button" class="hero-pause" aria-label="Pausar movimiento" aria-pressed="false">Ⅱ</button>
        </div>
      </div>
    </div>

    <div class="home-hero-copy">
      <p class="kicker">{MARCA} · Madrid · Colección 2026</p>
      <h1>Iconos que conoces.<br><em>Honestamente nuestros.</em></h1>
      <p>Homenajes a los grandes relojes del mundo, sin falsificaciones ni logotipos ajenos. Componentes seleccionados y cada unidad montada, ajustada y probada en Madrid.</p>
      <div class="button-row">
        <a class="button primary" href="/coleccion.html">Descubrir la colección <span aria-hidden="true">↘</span></a>
        <a class="text-link" href="/filosofia.html">Por qué hacemos homenajes</a>
      </div>
      <!-- PENDIENTE DE LA HOJA DE MATERIALES: aquí iba el «Desde X € ·
           impuestos incluidos» del original, en <span class="hero-price">.
           Hasta que estén los precios reales no se enseña ninguno. -->
    </div>
  </section>

  <section class="trust-strip" aria-label="Razones para confiar en laOra">
    <article><span>01</span><div><b>Marca propia</b><p>Sin emblemas ni logotipos ajenos.</p></div></article>
    <article><span>02</span><div><b>Montaje en Madrid</b><p>Ajuste y control unidad a unidad.</p></div></article>
    <article><span>03</span><div><b>Componentes identificados</b><p>Origen y movimiento, sin rodeos.</p></div></article>
    <article><span>04</span><div><b>Stock real</b><p>Envío en 48 h cuando se indica.</p></div></article>
    <article><span>05</span><div><b>Servicio cercano</b><p>Taller y posventa en España.</p></div></article>
  </section>

  <!-- Las cifras de mercado son ORIENTATIVAS, viven todas en
       assets/js/home.js y llevan su nota legal al pie de la sección.
       Si se actualizan, hay que actualizar también la fecha de la nota. -->
  <section class="market-map" id="mapa">
    <div class="market-map-head">
      <div>
        <p class="section-number">01 — EL MAPA DEL PRECIO</p>
        <h2>Lo que cuesta un icono.<br><em>Y lo que pagas realmente.</em></h2>
      </div>
      <div class="market-map-intro">
        <p>Una comparación de canales, riesgos y alternativas. Sin confundir homenaje con falsificación.</p>
        <div class="market-tabs" role="group" aria-label="Elegir comparación">
          <button type="button" class="active" data-mapa="lunar" aria-pressed="true">Speedmaster → Lunar</button>
          <button type="button" data-mapa="bitacora" aria-pressed="false">Nautilus → Bitácora</button>
        </div>
      </div>
    </div>

    <div class="market-map-body" aria-live="polite">
      <div class="market-context">
        <strong data-mapa-titulo>El cronógrafo lunar</strong>
        <span data-mapa-intro>Del canal oficial al mercado irregular: cinco rutas que pueden parecer similares en una foto, pero no ofrecen lo mismo.</span>
      </div>
      <div class="market-zones" aria-hidden="true">
        <span>Mercado original y trazable</span>
        <span>Mercado irregular / clones</span>
      </div>
      <div class="market-cards" data-mapa-tarjetas></div>

      <div class="market-bottom">
        <div class="market-alternatives">
          <p class="kicker">Alternativas de otras marcas</p>
          <div data-mapa-otras></div>
        </div>
        <article class="laora-value">
          <img src="{IMG}/lunar-acero.webp" alt="Reloj laOra Lunar" data-mapa-foto>
          <div class="laora-value-price">
            <!-- «laOra» NO se escribe: es el logotipo canónico, en minúsculas
                 salvo la O, que lleva el triángulo invertido a las 12. Aquí
                 solo cambia de color para leerse sobre el oro. -->
            <span><span class="cb-marca" aria-hidden="true">la<span class="o"></span>ra</span><span class="solo-lectores">laOra</span> · <b data-mapa-modelo>Lunar</b></span>
            <strong>209,90 €</strong>
          </div>
          <!-- Sin precio: el cuadro ya lo dice en grande, arriba. -->
          <p data-mapa-valor>Mismo acero, mismo cristal, mismos movimientos</p>
          <!-- El rótulo lo escribe entero home.js. Con un <b> dentro, el
               `display:inline-flex` del enlace se comía los espacios de los
               nodos de texto y salía «VERLUNAR→». -->
          <a href="/lunar.html" data-mapa-enlace>Ver Lunar →</a>
        </article>
      </div>

      <p class="market-footnote">Precios orientativos consultados en agosto de 2026; pueden variar por referencia, estado, impuestos, comisiones y envío. La presencia de una oferta no acredita su autenticidad. laOra no está afiliada a las marcas o plataformas citadas.</p>
    </div>
  </section>

  <section class="featured-products">
    <div class="product-grid compact">
{chr(10).join(tarjeta(RELOJ[s]) for s in DESTACADOS)}
    </div>
    <a class="button outline" href="/coleccion.html">Ver los ocho modelos →</a>
  </section>

  <section class="homage-manifesto">
    <div class="manifesto-media"><img src="{IMG}/precisa-hero.webp" alt="Reloj laOra Precisa de acero y esfera azul" loading="lazy"></div>
    <div class="manifesto-copy">
      <p class="kicker light">Homenaje no es falsificación</p>
      <h2>La inspiración se reconoce.<br><em>La identidad no se suplanta.</em></h2>
      <p>Un homenaje toma una arquitectura conocida como punto de partida. Una falsificación intenta hacerse pasar por otra marca. En laOra no ocultamos la referencia y nunca ponemos en la esfera un nombre que no sea el nuestro.</p>
      <ul>
        <li><span aria-hidden="true">✓</span> Marca, modelo y documentación laOra</li>
        <li><span aria-hidden="true">✓</span> Sin logotipos, coronas ni escudos de terceros</li>
        <li><span aria-hidden="true">✓</span> Sin historias de origen inventadas</li>
        <li><span aria-hidden="true">✓</span> Sin sugerir afiliaciones que no existen</li>
      </ul>
      <a class="text-link light" href="/filosofia.html">Nuestra forma de hacer →</a>
    </div>
  </section>

  <section class="quality-section">
    <div class="section-head">
      <p class="section-number">02 — CALIDAD DEMOSTRABLE</p>
      <h2>El misterio está en el reloj.<br><em>La confianza, en mostrarlo todo.</em></h2>
    </div>
    <div class="quality-grid">
      <div class="quality-watch">
        <img src="{IMG}/lunar-detail.webp" alt="Detalle del reloj laOra Lunar" loading="lazy">
        <span class="orbit orbit-a" aria-hidden="true"></span>
        <span class="orbit orbit-b" aria-hidden="true"></span>
      </div>
      <ol>
{chr(10).join(f'        <li><span>{n}</span><div><b>{t}</b><p>{d}</p></div></li>' for n, t, d in CAPAS)}
      </ol>
    </div>
  </section>

  <section class="madrid-section" id="taller">
    <img src="{IMG}/workshop-hero.webp" alt="Detalle del proceso de revisión de un reloj laOra" loading="lazy">
    <div class="madrid-overlay">
      <p class="kicker light">Taller {MARCA} · Madrid</p>
      <h2>Antes de llegar a tu muñeca,<br><em>pasa por nuestras manos.</em></h2>
      <ol><li>Inspección</li><li>Montaje</li><li>Ajuste</li><li>Pruebas</li><li>Control visual</li><li>Envío</li></ol>
      <a class="button light-button" href="/taller.html">Conocer el proceso</a>
    </div>
  </section>

  <section class="club-preview">
    <div class="club-copy">
      <p class="section-number">03 — Club {MARCA}</p>
      <h2>Tu reloj continúa<br><em>dentro de la app.</em></h2>
      <p>Certificado, factura, garantía, historial, contacto directo con el taller y ventajas por recomendación. Todo en un único lugar, privado por defecto.</p>
      <a class="button primary" href="/club.html"><span class="etiqueta">Conocer Club {MARCA} →</span></a>
    </div>
    <div class="club-phone-wrap">
{TELEFONO}
      <div class="float-card"><b>Pasaporte digital</b><span>LO—08 · Verificado</span></div>
    </div>
  </section>
""" + final_cta('Tu tiempo. Tu elección.',
                'Elige el icono.<br><em>Nosotros respondemos por el reloj.</em>',
                '/coleccion.html', 'Ver la colección',
                '/club.html', f'<span class="etiqueta">Conocer Club {MARCA}</span>') + """

</main>
""" + PIE + scripts(f'\n<script src="/assets/js/home.js?v={V_JS_HOME}"></script>'))


# ============================================================
# COLECCIÓN
# ============================================================

escribir('coleccion.html', cabeza(
    'Colección · laOra',
    'Ocho relojes laOra inspirados en grandes arquetipos de la relojería mundial.',
    '/coleccion.html', f'{IMG}/precisa-front.webp') + cabecera('coleccion') + f"""

<main id="inicio">

  <section class="page-hero collection-hero">
    <p class="kicker">Colección {MARCA} · 2026</p>
    <h1>Un icono para cada forma<br><em>de vivir el tiempo.</em></h1>
    <p>Elige por carácter, familia o uso. Cada ficha explica la referencia del homenaje, los componentes y el trabajo que hacemos en Madrid.</p>
  </section>

  <section class="collection-page">
    <div class="product-grid">
{chr(10).join(tarjeta(r) for r in RELOJES)}
    </div>
  </section>

  <section class="finish-system">
    <div>
      <p class="section-number">02 — CUATRO EXPRESIONES</p>
      <h2>El mismo homenaje.<br><em>Tu forma de llevarlo.</em></h2>
    </div>
    <div class="finish-cards">
      <article><span>01</span><h3>Alba</h3><b>Esencial</b><p>Precisión de cuarzo, diseño limpio y comodidad diaria.</p></article>
      <article><span>02</span><h3>Levante</h3><b>Refinado</b><p>Cuarzo con materiales y acabados superiores identificados.</p></article>
      <article><span>03</span><h3>Cenit</h3><b>Máxima expresión</b><p>La mejor ejecución disponible para cada familia.</p></article>
      <article class="dark"><span>04</span><h3>Eclipse</h3><b>Carácter técnico</b><p>Negro integral o titanio, cuando la configuración lo permite.</p></article>
    </div>
  </section>
""" + final_cta('Tu tiempo. Tu elección.',
                'Elige el icono.<br><em>Nosotros respondemos por el reloj.</em>',
                '/filosofia.html', 'Por qué hacemos homenajes',
                '/taller.html', 'Conocer el taller') + """

</main>
""" + PIE + scripts())


# ============================================================
# LA HISTORIA, EN CUATRO ACTOS
# ------------------------------------------------------------
# Óscar, 07/08/2026. Sustituye a los tres actos que había —«el punto de
# partida», «el proceso» y «origen sin eufemismos»—, que contaban la
# marca desde dentro: qué hacemos y cómo. Esto la cuenta desde fuera,
# desde el que compra, y en su idioma.
#
# LOS TEXTOS SON DE ÓSCAR, PALABRA POR PALABRA. El titular de cada acto
# es su propio resumen —«quiero un reloj que me haga sentir algo»— y el
# cuerpo, su voz en primera persona. Aquí no se reescribe nada.
#
# Poca letra y grande, que es como lo pidió: el titular manda y la voz
# va debajo, en un tamaño que se lee sin acercarse.
# ============================================================
ACTOS = [
    ('01', 'El deseo',
     'Quiero un reloj que me haga sentir algo.',
     'Mira, a mí siempre me han gustado los relojes buenos. De esos que te los pones '
     'y notas que están bien hechos. Pero no tengo 8.000 € para un reloj… y aunque los '
     'tuviera, tampoco sé si me los gastaría.'),
    ('02', 'El problema',
     'Lo bueno es inaccesible y lo barato genera dudas.',
     'Entonces te pones a mirar. Los de las grandes marcas cuestan una barbaridad. Los '
     'baratos de internet prometen mucho, pero no sabes qué te va a llegar. En segunda '
     'mano igual aciertas… o igual te comes el problema de otro. Y si lo compras fuera, '
     'como falle, búscate la vida.'),
    ('03', 'La respuesta',
     'Seleccionamos, montamos, comprobamos y respondemos aquí.',
     'Y entonces encontré laOra. Ellos buscan buenas piezas, descartan las que no les '
     'convencen y las traen a Madrid. Aquí montan cada reloj, comprueban que funcione '
     'bien, lo ajustan si hace falta y miran que aguante el agua que promete. No te llega '
     'una caja directa de una fábrica que está a 10.000 kilómetros.'),
    ('04', 'La recompensa',
     'Tengo el reloj que quería, puedo pagarlo y estoy tranquilo.',
     'Al final me llevé un reloj que tiene la presencia y la calidad que estaba buscando, '
     'pero a un precio que puedo pagar. Sé qué lleva, sé quién lo ha montado y, si algún '
     'día pasa algo, tengo a alguien aquí que responde.'),
]


def acto(n, etiqueta, titular, voz):
    return f'''      <article>
        <span>{n}</span>
        <p class="acto-etiqueta">{etiqueta}</p>
        <h3>{titular}</h3>
        <blockquote>{voz}</blockquote>
      </article>'''


HISTORIA = f"""  <section class="historia">
    <!-- La frase de arriba se fue al acto 1 el 07/08/2026, así que aquí
         ya no se repite: se entra directo por los cuatro actos. -->
    <ol class="historia-actos">
{chr(10).join(acto(*a) for a in ACTOS)}
    </ol>

    <p class="historia-cierre">Eso es {MARCA}: un gran reloj,<br><em>sin pagar una fortuna y sin jugártela.</em></p>
  </section>"""


# ============================================================
# NUESTRA FORMA DE HACER
# ============================================================

PROCESO = [
    ('01', 'Estudiamos', 'Partimos de arquetipos que han demostrado su valor con el tiempo.'),
    ('02', 'Seleccionamos', 'Comparamos proveedores, materiales, movimientos y tolerancias.'),
    ('03', 'Firmamos', 'La esfera, la documentación y el servicio llevan una sola marca: laOra.'),
    ('04', 'Montamos', 'Reunimos los componentes y completamos cada unidad en Madrid.'),
    ('05', 'Probamos', 'Ajustamos, revisamos y preparamos el reloj antes del envío.'),
    ('06', 'Respondemos', 'Garantía, repuestos y servicio siguen aquí después de la compra.'),
]

escribir('filosofia.html', cabeza(
    'Nuestra forma de hacer · laOra',
    'Por qué laOra crea homenajes honestos y cómo selecciona, monta y controla cada reloj en Madrid.',
    '/filosofia.html', f'{IMG}/workshop-hero.webp') + cabecera('filosofia') + f"""

<main id="inicio">

  <section class="philosophy-hero">
    <img src="{IMG}/workshop-hero.webp" alt="Reloj laOra Trinchera durante su revisión">
    <!-- 07/08/2026, Óscar: «borra todo del acto 1 y coloca esto». Antes
         abría con la marca hablando de sí misma; ahora abre la historia
         del que compra, que es de quien va la página. La foto y el fondo
         se quedan: lo que cambia es lo que se dice encima. El texto
         anterior está en el historial de git, no aquí. -->
    <div>
      <p class="kicker light">La historia</p>
      <h1>Quería un gran reloj.<br><em>No podía pagar una gran marca.</em><br>Tampoco quería comprar a ciegas.<br><em>Por eso elegí {MARCA}.</em></h1>
    </div>
  </section>

{HISTORIA}

  <section class="honesty-block">
    <div>
      <p class="kicker light">Homenaje, con todas las letras</p>
      <h2>Reconocer el origen<br><em>también es diseñar confianza.</em></h2>
    </div>
    <div class="honesty-columns">
      <article>
        <span>SÍ</span>
        <h3>Lo que hacemos</h3>
        <ul>
          <li>Explicar el arquetipo que inspira cada pieza.</li>
          <li>Usar exclusivamente la marca y los nombres laOra.</li>
          <li>Identificar movimiento, materiales y proceso.</li>
          <li>Responder en Madrid por montaje y servicio.</li>
        </ul>
      </article>
      <article>
        <span>NO</span>
        <h3>Lo que no hacemos</h3>
        <ul>
          <li>Imitar logotipos, firmas o emblemas ajenos.</li>
          <li>Sugerir que existe una afiliación inexistente.</li>
          <li>Inventar procedencias o tradición manufacturera.</li>
          <li>Ocultar el origen internacional de componentes.</li>
        </ul>
      </article>
    </div>
  </section>

""" + final_cta('Sin apellido prestado',
                'La calidad no necesita<br><em>una historia inventada.</em>',
                '/coleccion.html', 'Ver los relojes',
                '/taller.html', 'Conocer el taller') + """

</main>
""" + PIE + scripts())


# ============================================================
# TALLER Y SERVICIO
# ============================================================

PASOS = [
    ('01', 'Recepción', 'Comprobamos referencias, acabados y estado de cada componente.'),
    ('02', 'Montaje', 'Ensamblamos la unidad siguiendo la ficha técnica del modelo.'),
    ('03', 'Ajuste', 'Verificamos funcionamiento y regulamos cuando el movimiento lo permite.'),
    ('04', 'Pruebas', 'Aplicamos los controles confirmados para esa configuración.'),
    ('05', 'Control visual', 'Revisamos esfera, agujas, caja, cierre y terminaciones.'),
    ('06', 'Preparación', 'Documentamos, embalamos y expedimos desde stock real.'),
]

SERVICIOS = [
    ('01', 'Garantía', 'Condiciones y fechas siempre accesibles en tu pasaporte digital.'),
    ('02', 'Mantenimiento', 'Cambio de pila, revisión, limpieza y conservación según configuración.'),
    ('03', 'Repuestos', 'Disponibilidad comunicada de forma clara antes de aprobar cualquier trabajo.'),
    ('04', 'Persona real', 'Un equipo que conoce la referencia y el historial de tu unidad.'),
]

escribir('taller.html', cabeza(
    'Taller y servicio · laOra',
    'Montaje, ajuste, pruebas y servicio técnico de los relojes laOra en Madrid.',
    '/taller.html', f'{IMG}/workshop-hero.webp') + cabecera('taller') + f"""

<main id="inicio">

  <section class="workshop-hero">
    <img src="{IMG}/workshop-hero.webp" alt="Reloj laOra durante el control final">
    <div>
      <p class="kicker light">Taller y servicio · Madrid</p>
      <h1>Aquí empieza<br><em>la responsabilidad.</em></h1>
      <p>Los componentes pueden venir de distintos especialistas. El montaje, el control y la persona que responde están cerca.</p>
    </div>
  </section>

  <section class="workshop-intro">
    <p class="section-number">01 — ANTES DEL ENVÍO</p>
    <div>
      <h2>Seis pasos.<br><em>Una unidad cada vez.</em></h2>
      <p>No publicamos pruebas que no estén confirmadas para una referencia concreta. La ficha de cada reloj indica exactamente qué se comprueba.</p>
    </div>
  </section>

  <section class="workshop-steps">
{chr(10).join(f'    <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in PASOS)}
  </section>

  <section class="service-panel">
    <div>
      <p class="kicker light">Después de la compra</p>
      <h2>Servicio sin<br><em>intermediarios.</em></h2>
      <p>Desde Club laOra puedes identificar tu reloj, abrir una consulta, adjuntar imágenes, solicitar recogida y seguir el estado de la intervención.</p>
      <a class="button gold" href="/club.html"><span class="etiqueta">Ver Club {MARCA}</span></a>
    </div>
    <div class="service-list">
{chr(10).join(f'      <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in SERVICIOS)}
    </div>
  </section>
""" + final_cta('Seguimos aquí',
                'Elige el reloj.<br><em>Nos ocupamos del resto.</em>',
                '/coleccion.html', 'Ver la colección',
                'mailto:taller@laora.es', 'Contactar con el taller') + """

</main>
""" + PIE + scripts())


# ============================================================
# CLUB laOra
# ============================================================

VENTAJAS = [
    ('01', 'Mi colección', 'Referencias, números de serie y configuraciones en un espacio privado.'),
    ('02', 'Pasaporte digital', 'Certificado, factura, manual, garantía e historial de mantenimiento.'),
    ('03', 'Taller directo', 'Consultas con fotos, diagnóstico, recogida y seguimiento de la reparación.'),
    ('04', 'Cuidado del reloj', 'Recordatorios y consejos según movimiento, hermeticidad y materiales.'),
    ('05', 'Recomendaciones', 'Código personal, seguimiento y ventajas explicadas con claridad.'),
    ('06', 'Acceso reservado', 'Nuevos acabados, correas y lanzamientos cuando estén realmente disponibles.'),
]

escribir('club.html', cabeza(
    'Club laOra · laOra',
    'Colección, documentación, garantía y contacto con el taller en una sola aplicación.',
    '/club.html') + cabecera('club') + f"""

<main id="inicio">

  <section class="club-hero">
    <div>
      <p class="kicker light">Club {MARCA} · Incluido con tu reloj</p>
      <h1>La relación no <span class="aire">termina</span><br><em>cuando recibes el reloj.</em></h1>
      <p>Tu colección, documentación, garantía, servicio y ventajas en un único lugar. Una app útil, no otro programa publicitario.</p>
      <div class="button-row"><a class="text-link light" href="#funciones">Ver cómo funciona</a></div>
    </div>
    <div class="club-hero-device">
{TELEFONO}
      <span class="device-glow" aria-hidden="true"></span>
    </div>
  </section>

  <section class="club-promise">
    <p class="section-number">01 — UNA RELACIÓN ÚTIL</p>
    <div><h2>Tu reloj, su historia<br><em>y nuestro taller.</em></h2></div>
    <div>
      <p>Cuando abres Club laOra sabes exactamente qué tienes, qué cubre tu garantía, dónde está tu factura y con quién hablar si necesitas algo.</p>
      <p>Todo es privado por defecto y tú decides qué parte de tu colección quieres compartir.</p>
    </div>
  </section>

  <section class="benefits-section" id="funciones">
    <div class="section-head">
      <p class="section-number">02 — TODO EN SU SITIO</p>
      <h2>Un club que sirve<br><em>para algo.</em></h2>
    </div>
    <div class="benefits-grid">
{chr(10).join(f'      <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in VENTAJAS)}
    </div>
  </section>

  <section class="club-journey">
    <div>
      <p class="kicker light">Cómo funciona</p>
      <h2>Desde la compra<br><em>hasta el próximo servicio.</em></h2>
    </div>
    <ol>
      <li><span>01</span><p>Compras o registras tu laOra.</p></li>
      <li><span>02</span><p>Aparece automáticamente en tu colección.</p></li>
      <li><span>03</span><p>Conservas toda su documentación.</p></li>
      <li><span>04</span><p>Contactas con el taller cuando lo necesitas.</p></li>
      <li><span>05</span><p>Transfieres la propiedad si algún día cambia de muñeca.</p></li>
    </ol>
  </section>

  <section class="privacy-section">
    <div>
      <p class="section-number">03 — PRIVACIDAD CLARA</p>
      <h2>Tu colección es tuya.<br><em>También sus datos.</em></h2>
    </div>
    <div>
      <p>Guardamos únicamente la información necesaria para documentar el reloj, prestar el servicio y mantener tu cuenta.</p>
      <ul>
        <li>Escaparate privado por defecto.</li>
        <li>Control sobre qué compartes.</li>
        <li>Exportación y eliminación de la cuenta.</li>
        <li>Transferencia de propiedad con tu aprobación.</li>
      </ul>
    </div>
  </section>
""" + final_cta(f'Club {MARCA}',
                'Todo lo importante.<br><em>Siempre en su sitio.</em>',
                '/coleccion.html', 'Descubrir la colección',
                '/taller.html', 'Conocer el taller') + """

</main>
""" + PIE + scripts())


# ============================================================
# LAS OCHO FICHAS
# ------------------------------------------------------------
# Se generan del catálogo, así que ficha y listado no pueden
# desajustarse. En la web anterior el Lunar costaba 269,90 € en el
# listado y 239,90 € en su ficha justamente por escribirlos a mano
# en dos sitios.
#
# Lo que no está confirmado NO se pinta: si `hermeticidad` es null,
# esa línea no existe en el HTML. Nada de «por confirmar» a la vista.
#
# YA NO SON OCHO. Desde el 06/08/2026, cinco modelos tienen pantalla de
# comprar —el patrón de `lunarv2c`— y la escribe
# `herramientas/generar_configuradores.py`. Este fichero las salta: si
# no lo hiciera, ejecutar el generador antiguo devolvería `/lunar` a la
# ficha anterior sin que nadie se diera cuenta.
# ============================================================

DEL_CONFIGURADOR = {'lunar', 'cero-cero', 'precisa', 'trinchera', 'bitacora',
                    'tortuga', 'coctel', 'diver'}

for i, r in enumerate(RELOJES):
    if r['slug'] in DEL_CONFIGURADOR:
        continue
    siguiente = RELOJES[(i + 1) % len(RELOJES)]
    anterior = RELOJES[(i - 1) % len(RELOJES)]

    # ---- LAS CURIOSIDADES ----
    # Van entre la foto y la noticia. Cada una abre una VENTANA EMERGENTE de
    # verdad, con <dialog>: fondo oscurecido, Escape la cierra, el foco se
    # queda dentro y no se puede tabular por detras. Todo eso lo da el
    # navegador; no hay libreria ni truco de posicionamiento.
    #
    # El texto va escrito en la pagina aunque el dialogo este cerrado, asi
    # que Google lo lee. Si el JavaScript no llegara a cargar, los botones
    # no abririan: es el unico punto de la ficha que depende de el.
    cur = r.get('curiosidades')
    if cur:
        def boton(n, c):
            ide = 'cur-' + r['slug'] + '-' + c['id']
            return ('          <button type="button" data-abre="' + ide + '">\n'
                    '            <span class="cur-num">' + str(n + 1).zfill(2) + '</span>\n'
                    '            <span class="cur-titulo">' + c['titulo'] + '</span>\n'
                    '            <span class="cur-gancho">' + c['gancho'] + '</span>\n'
                    '            <span class="cur-mas" aria-hidden="true">Leer</span>\n'
                    '          </button>')

        def ventana(n, c):
            ide = 'cur-' + r['slug'] + '-' + c['id']
            parrafos = '\n'.join('        <p>' + t + '</p>' for t in c['cuerpo'])
            return ('      <dialog class="cur-ventana" id="' + ide + '" aria-labelledby="t-' + ide + '">\n'
                    '        <button type="button" class="cur-cerrar" data-cierra aria-label="Cerrar">&times;</button>\n'
                    '        <p class="cur-orden">Curiosidad ' + str(n + 1).zfill(2) + ' de ' + str(len(cur)) + '</p>\n'
                    '        <h2 id="t-' + ide + '">' + c['titulo'] + '</h2>\n'
                    + parrafos + '\n'
                    '      </dialog>')

        curiosidades = ('\n      <section class="curiosidades" aria-labelledby="rot-' + r['slug'] + '">\n'
                        '        <p class="cur-rotulo" id="rot-' + r['slug'] + '">'
                        + str(len(cur)) + ' curiosidades</p>\n'
                        '        <div class="cur-botones">\n'
                        + '\n'.join(boton(n, c) for n, c in enumerate(cur)) + '\n'
                        '        </div>\n'
                        + '\n'.join(ventana(n, c) for n, c in enumerate(cur)) + '\n'
                        '      </section>')
    else:
        curiosidades = ''

    # ---- LA HISTORIA DEL ORIGINAL ----
    # Va DEBAJO DE LA FOTO, en la columna izquierda, que es donde sobraba
    # espacio en blanco desde que el configurador estiró la columna derecha.
    # Nombra la marca y el modelo con todas sus letras, así que lleva su
    # propio aviso legal pegado: aquí es donde hace falta, no solo en el pie.
    h = r.get('historiaOriginal')
    if h:
        parrafos = '\n'.join(f'          <p>{t}</p>' for t in h['cuerpo'])
        hitos = '\n'.join(
            f'          <li><b>{a}</b><span>{t}</span></li>' for a, t in h['datos'])
        historia = f"""
      <article class="pdp-historia">
        <p class="ph-antetitulo">{h['antetitulo']} · {h['original']}</p>
        <h2>{h['titular']}</h2>
        <p class="ph-entradilla">{h['entradilla']}</p>
        <div class="ph-cuerpo">
{parrafos}
        </div>
        <ol class="ph-hitos">
{hitos}
        </ol>
        <p class="ph-cierre">{h['cierre']}</p>
        <p class="ph-aviso">{h['aviso']}</p>
      </article>"""
    else:
        historia = ''

    # ---- CONFIGURADOR ----
    # Solo los modelos que ya tienen su fila en el catálogo final. El resto
    # sigue como estaba, sin precio ni selector, hasta que se vuelquen.
    cfg = r.get('configurador')
    if cfg:
        def opcion(attr, ident, nombre, detalle, primera, clase=''):
            sel = ' aria-selected="true"' if primera else ' aria-selected="false" tabindex="-1"'
            cls = f' class="{clase}"' if clase else ''
            return (f'          <button type="button" role="tab" data-{attr}="{ident}"{cls}{sel}>'
                    f'<span>{nombre}</span><small>{detalle}</small></button>')

        # LA FICHA ABRE POR LA COMBINACIÓN MÁS BARATA que se pueda pedir, no
        # por la primera de la lista (Óscar, 04/08/2026). Se busca aquí y se
        # escribe ya marcada, para que la página cargue bien aunque el JS
        # tarde o no llegue. `ficha.js` calcula lo mismo y coincide.
        barata = min(
            ((a, j, p)
             for a in cfg['acabados']
             for j, p in enumerate(cfg['precios'][a['id']]) if p is not None),
            key=lambda t: t[2])
        acEleg, correaEleg, precioEleg = barata

        # El Eclipse es la gama en negro y su tarjeta va en grafito con la
        # letra en blanco puro, en los ocho modelos. Óscar, 03/08/2026.
        acabados = '\n'.join(
            opcion('acabado', a['id'], a['nombre'], a['descriptor'], a is acEleg,
                   'op-eclipse' if a['nombre'].startswith('Eclipse') else '')
            for a in cfg['acabados'])
        # El grupo de correa solo existe si hay algo que elegir. El Bauhaus
        # va siempre con el mismo brazalete, así que ahí no se pinta: un
        # desplegable de una sola opción no es una elección, es un estorbo.
        if len(cfg['correas']) > 1:
            correas = '\n'.join(
                opcion('correa', c['id'], c['nombre'], c['detalle'], n == correaEleg)
                for n, c in enumerate(cfg['correas']))
            grupoCorrea = f'''
        <p class="config-titulo" id="cfg-correa">Elige brazalete o correa</p>
        <div class="config-opciones" role="tablist" aria-labelledby="cfg-correa" data-grupo="correa">
{correas}
        </div>'''
        else:
            grupoCorrea = ''
        # El precio va EN MEDIO de los dos grupos, no arriba del todo: así
        # queda a la vista mientras se elige y se ve cambiar. Arriba se
        # quedaba fuera de pantalla en cuanto bajabas a los acabados.
        configurador = f"""      <div class="config">
        <p class="config-titulo" id="cfg-acabado">Elige acabado</p>
        <div class="config-opciones" role="tablist" aria-labelledby="cfg-acabado" data-grupo="acabado">
{acabados}
        </div>
        <p class="config-nota" data-resumen-acabado>{acEleg['resumen']}</p>

        <div class="pdp-price">
          <strong data-precio>{precio_es(precioEleg)}</strong>
          <span>Impuestos incluidos</span>
        </div>{grupoCorrea}
      </div>

      <!-- EL BOTÓN DE RESERVA ESTÁ ESPERANDO A SU PÁGINA.
           Óscar eligió recuperar el sistema de reserva con señal (03/08/2026),
           pero `reservar.html` todavía no está rehecha con el diseño nuevo:
           las de la web anterior usaban hojas que ya no existen. Hasta
           entonces NO se pinta, para no dejar un botón que lleve a un 404.

           Cuando exista, se descomenta esto y ya funciona: `ficha.js` le
           escribe la referencia, el acabado y la correa elegidos en la URL.
      <a class="button primary full" href="/reservar.html" data-reservar>Reservar este {r['nombre']}</a>
           -->
      <p class="config-ref">Referencia <b data-ref>—</b></p>"""
    else:
        configurador = ('      <!-- Sin configurador: este modelo todavía no está volcado\n'
                        '           del catálogo final de la hoja de materiales. -->')

    specs = [(k, v) for k, v in [
        ('Familia', r['familia']),
        ('Tamaño', r['diametro']),
        ('Movimiento', r['movimiento']),
        ('Hermeticidad', r['hermeticidad']),
        ('Referencia', r['codigo']),
    ] if v]

    # Datos estructurados para Google. SIN `offers`: solo se escribe cuando
    # haya precio cerrado, porque un Product con un precio inventado es
    # justo lo que penaliza el buscador.
    datos = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': 'laOra ' + r['nombre'],
        'sku': r['codigo'],
        'brand': {'@type': 'Brand', 'name': 'laOra'},
        'description': r['descripcion'],
        'image': ['https://laora.es' + g for g in r['galeria']],
    }
    ld = json.dumps(datos, ensure_ascii=False).replace('<', '\\u003c')

    # Con qué foto abre la ficha: la del acabado elegido si la tiene —el
    # Eclipse enseña la suya, en negro— y si no, la primera de la galería.
    foto_ini = (acEleg.get('foto') if cfg else None) or r['galeria'][0]

    def mini(n, g):
        activa = ' class="active"' if g == foto_ini else ''
        return (f'          <button type="button" data-mini="{g}"{activa}'
                f' aria-label="Ver imagen {n + 1} de {r["nombre"]}">'
                f'<img src="{g}" alt=""></button>')

    minis = '\n'.join(mini(n, g) for n, g in enumerate(r['galeria']))

    if cfg:
        # con configurador, la ficha técnica se parte en dos: lo que cambia
        # con el acabado (lo reescribe ficha.js) y lo que es igual siempre.
        variables = [('Movimiento', 'movimiento'), ('Tipo', 'movimientoTipo'),
                     ('Frecuencia', 'frecuencia'), ('Autonomía', 'autonomia'),
                     ('Cristal', 'cristal'), ('Caja', 'caja'),
                     ('Diámetro', 'diametro'), ('Estanqueidad', 'estanqueidad'),
                     ('Bisel', 'bisel'), ('Esfera', 'esfera'), ('Fondo', 'fondo')]
        primera = acEleg
        # solo se escriben las líneas que ese modelo tiene: el Lunar no
        # distingue el fondo por acabado, el Bauhaus sí (macizo o de cristal),
        # y el Cero Cero cambia de estanqueidad (100 o 200 m) y de esfera
        # (con ventana de fecha o sin ella) según el acabado. Lo que un modelo
        # no distinga se queda en `comunes` y se pinta una sola vez.
        #
        # La línea se crea si la tiene CUALQUIER acabado, no solo el primero:
        # en el Lunar la estanqueidad la declara la hoja únicamente para el
        # Cenit, y mirando solo al Alba esa fila no llegaba a existir. Cuando
        # el acabado elegido no la tiene, `ficha.js` la esconde.
        def alguno(cl):
            return next((a[cl] for a in cfg['acabados'] if a.get(cl)), None)

        filas = '\n'.join(
            f'        <div{"" if primera.get(cl) else " hidden"}><dt>{et}</dt>'
            f'<dd data-spec="{cl}">{primera.get(cl, "")}</dd></div>'
            for et, cl in variables if alguno(cl))
        filas += '\n' + '\n'.join(
            f'        <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in cfg['comunes'].items())
        filas += f'\n        <div><dt>Peso</dt><dd data-spec="peso">{primera["peso"]}</dd></div>'
        filas += f'\n        <div><dt>Referencia</dt><dd>{r["codigo"]}</dd></div>'
        # los datos que necesita ficha.js, ya limpios de todo lo interno
        datos_cfg = json.dumps({'acabados': cfg['acabados'], 'correas': cfg['correas'],
                                'precios': cfg['precios'], 'codigo': r['codigo'],
                                'modelo': r['nombre']}, ensure_ascii=False)
        configurador += ('\n      <script type="application/json" data-configurador>'
                         + datos_cfg.replace('<', '\\u003c') + '</script>')
    else:
        filas = '\n'.join(f'        <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in specs)

    tecnica = '\n'.join(
        f'        <li><span>{str(n + 1).zfill(2)}</span><div><b>{k}</b><p>{v}</p></div></li>'
        for n, (k, v) in enumerate(r['fichaTecnica']))

    escribir(r['slug'] + '.html', cabeza(
        f'{r["nombre"]} · laOra', r['descripcion'],
        f'/{r["slug"]}.html', r['foto']) + cabecera('coleccion') + f"""

<main id="inicio">
<script type="application/ld+json">{ld}</script>

  <section class="pdp-hero">
    <div class="pdp-gallery">
      <div class="pdp-main-image">
        <img src="{foto_ini}" alt="{r['nombre']}, vista seleccionada" data-foto-grande fetchpriority="high">
      </div>
      <div class="pdp-thumbs" role="group" aria-label="Vistas del producto">
{minis}
      </div>
    </div>
    <div class="pdp-buy">
      <p class="kicker">{r['codigo']} · {r['familia']}</p>
      <h1>{r['nombre']}</h1>
      <p class="pdp-homage">{r['homenaje']}</p>
      <p class="pdp-description">{r['descripcion']}</p>
{configurador}
      <dl class="live-specs">
{filas}
      </dl>
      <p class="buy-note">Montado, ajustado y probado en Madrid antes de cada envío.</p>
    </div>
{curiosidades}
{historia}
  </section>

{historia_o_comparativa(r)}

  <section class="exploded-section">
    <div class="exploded-media"><img src="{r['galeria'][1] if len(r['galeria']) > 1 else r['foto']}" alt="Detalle constructivo de {r['nombre']}" loading="lazy"></div>
    <div class="exploded-copy">
      <p class="section-number">02 — LO QUE RECIBES</p>
      <h2>Todo identificado.<br><em>Nada escondido.</em></h2>
      <ol>
{tecnica}
      </ol>
    </div>
  </section>

  <section class="pdp-service">
    <div>
      <p class="kicker light">Taller {MARCA} · Madrid</p>
      <h2>Antes de llegar a tu muñeca,<br><em>pasa por nuestras manos.</em></h2>
    </div>
    <ol><li>Recepción e inspección</li><li>Montaje</li><li>Ajuste</li><li>Pruebas</li><li>Control visual</li><li>Preparación y envío</li></ol>
    <a class="text-link light" href="/taller.html">Conocer el taller →</a>
  </section>
""" + final_cta('Sigue por la colección',
                f'Antes: {anterior["nombre"]}.<br><em>Después: {siguiente["nombre"]}.</em>',
                f'/{siguiente["slug"]}.html', f'Ver {siguiente["nombre"]}',
                '/coleccion.html', 'Volver a la colección') + """

</main>
""" + PIE + scripts(f'\n<script src="/assets/js/ficha.js?v={V_JS_FICHA}"></script>'))


print(f'\nListo: {5 + len(RELOJES) - len(DEL_CONFIGURADOR)} páginas generadas.')
print(f'{len(DEL_CONFIGURADOR)} fichas las escribe ahora '
      'herramientas/generar_configuradores.py: '
      + ', '.join(sorted(DEL_CONFIGURADOR)))
