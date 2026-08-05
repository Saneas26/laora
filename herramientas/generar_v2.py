#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LANDING V2 DEL LUNAR
============================================================
Escribe `lunarv2.html`, la página de pruebas invisible. NO toca nada de
lo publicado: ni `lunar.html`, ni `laora.css`, ni `ficha.js`. Tiene su
propia hoja (`lunarv2.css`) y su propio script (`lunarv2.js`).

DE DÓNDE SALE ESTA VERSIÓN (05/08/2026)
------------------------------------------------------------
Óscar trajo el material aprobado de su diseñador,
`laora-lunar-aprobado-2026-08-05.zip`, con el encargo textual:

    «respeta fuentes, tamaños, colores, absolutamente todo;
     no cambies nada, no modifiques nada; limítate a transportar
     el contenido y la información a la página. Lo único que hay
     que respetar es el logo de laOra, que es único.»

Así que esto sustituye entero al guion de doce pantallas del 04/08. El
material venía en Next.js y aquí no hay Node, de modo que el marcado de
abajo es la traducción literal de sus componentes de React:

    app/page.tsx                            → el orden de los actos
    app/components/Shell.tsx                → cabecera y pie
    app/components/LunarHero.tsx            → acto 1, portada
    app/components/LunarDialogue.tsx        → acto 2, conversación
    app/components/LunarPride.tsx           → acto 3, orgullo
    app/components/TrustCarousel.tsx        → acto 4, confianza
    app/components/MarketMap.tsx            → acto 5, decisión
    app/components/LunarSpecifications.tsx  → acto 6 y su ficha técnica

Mismas clases, mismo orden, mismos textos. Lo que allí era estado de
React —las flechas, el carrusel, las pestañas y la ficha técnica— está
en `lunarv2.js`, sin tocar ni una medida.

LAS DOS COSAS QUE NO SE COPIAN TAL CUAL
------------------------------------------------------------
1. EL LOGOTIPO, porque lo pidió Óscar. El material traía un wordmark con
   la O de la tipografía; aquí va el logotipo canónico, el círculo con el
   triángulo invertido a las 12, en claro sobre fondo oscuro y en tinta
   sobre fondo claro. Por eso la cabecera ya no necesita volver negro el
   logotipo con un filtro; la regla queda comentada en `lunarv2.css`.

2. LAS TARJETAS DE ABAJO, que salen de `catalogo.json` como todo lo demás
   del sitio. El material traía ahí precios calculados por fórmula
   —Tortuga 399 €, Precisa 329 €, Bauhaus 219 €— y la numeración vieja de
   los códigos. Esos precios ya se descartaron una vez, el 03/08. Donde
   no hay precio cerrado va el diámetro, igual que en la colección.

USO
    python3 herramientas/generar_v2.py
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO: Cloudflare sirve el CSS con max-age=14400.
V_CSS = 16
V_JS = 4

with open(os.path.join(RAIZ, 'assets/datos/catalogo.json'), encoding='utf-8') as f:
    RELOJES = json.load(f)['relojes']

R = {x['slug']: x for x in RELOJES}
LUNAR = R['lunar']

IMG = '/assets/img/relojes-2026'      # las fotos que ya estaban
V2 = '/assets/img/lunar-v2'           # las del material nuevo


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


# El precio del Lunar sale del configurador, no escrito a mano. El
# material aprobado exige «desde 219,90 €» y prohíbe expresamente volver
# a enseñar 209,90 €: hoy la hoja da exactamente eso, así que cuadran.
# Si algún día dejan de cuadrar, salta el aviso de abajo.
DESDE = min(x for l in LUNAR['configurador']['precios'].values() for x in l if x is not None)

# El logotipo NUNCA se escribe: aquí va en PNG porque el material lo
# maqueta como imagen y le da anchos fijos en la hoja.
LOGO_CLARO = V2 + '/laora-wordmark.png'        # sobre fondo oscuro
LOGO_OSCURO = V2 + '/laora-wordmark-dark.png'  # sobre fondo claro


# ============================================================
# CABECERA  ·  Shell.tsx
# La navegación es la aprobada en el documento de entrega:
# Relojes · Por qué laOra · Taller · Club laOra · laOrateca
# ============================================================
def marca(clase, fuente, sufijo=''):
    return f'<span class="{clase}"><img src="{fuente}" alt="laOra">{sufijo}</span>'


CABECERA = f"""
<header class="site-header">
  <a class="brand" href="/" aria-label="laOra, inicio">{marca('brand-logo', LOGO_OSCURO)}</a>
  <button class="menu-toggle" type="button" aria-label="Abrir menú" aria-expanded="false" data-menu>
    <span></span><span></span>
  </button>
  <nav class="main-nav" aria-label="Navegación principal" data-nav>
    <a href="/coleccion.html">Relojes</a>
    <a href="/filosofia.html">Por qué {marca('brand-word', LOGO_OSCURO)}</a>
    <a href="/taller.html">Taller</a>
    <a href="/club.html">Club {marca('brand-word', LOGO_OSCURO)}</a>
    <a href="/filosofia.html#laorateca">{marca('brand-word', LOGO_OSCURO, 'teca')}</a>
  </nav>
  <div class="header-actions">
    <a class="header-icon support-icon" href="/taller.html" aria-label="Servicio y ayuda"><span aria-hidden="true"></span></a>
    <a class="header-icon profile-icon" href="/cuenta" aria-label="Mi cuenta"><span aria-hidden="true"></span></a>
    <a class="header-icon bag-icon" href="/carrito" aria-label="Carrito, 0 unidades"><span aria-hidden="true"></span><b>0</b></a>
  </div>
</header>"""


# ============================================================
# ACTO 1 · PORTADA  ·  LunarHero.tsx + page.tsx
# ------------------------------------------------------------
# TRES EXPOSICIONES, por encargo de Óscar (05/08/2026). Antes eran dos
# vistas de la MISMA foto del Lunar —la entera y un acercamiento—; se
# queda el acercamiento, que es la que eligió, y detrás entran el
# Bitácora y el Trinchera. Tres modelos, tres exposiciones.
#
# Al cambiar de exposición cambian la foto, el nombre, la línea de
# características, el precio y adónde llevan los dos botones. El precio
# es el mínimo del configurador de ESE reloj, sacado de `catalogo.json`.
#
# La línea de características del Lunar es la del material aprobado.
# Las otras dos se componen con datos de la hoja, no con la plantilla
# del Lunar: el Trinchera es de titanio y no de acero, y ni el Bitácora
# ni el Trinchera tienen el cristal confirmado en su acabado de entrada,
# así que ahí va el dato que sí está —el diámetro y la estanqueidad—.
# ============================================================
def desde_de(slug):
    cfg = R[slug]['configurador']
    return min(p for l in cfg['precios'].values() for p in l if p is not None)


EXPOSICIONES = [
    dict(slug='lunar', nombre='Lunar',
         foto=f'{V2}/lunar-hero-steel.webp',
         encuadre='cerca',          # el acercamiento, que es el que eligió Óscar
         alt='Reloj laOra Lunar de acero 316L pulido ante un cohete lunar difuminado',
         specs=['Movimiento Japonés', 'Zafiro', 'Acero 316L']),
    dict(slug='bitacora', nombre='Bitácora',
         foto=f'{IMG}/bitacora-hero-full.webp',
         encuadre='',
         alt='Reloj laOra Bitácora, deportivo integrado de acero',
         specs=['Cuarzo con fecha', '40 mm', '100 m']),
    dict(slug='trinchera', nombre='Trinchera',
         foto=f'{IMG}/trinchera-hero.webp',
         encuadre='',
         alt='Reloj laOra Trinchera, reloj de campo de titanio',
         specs=['Cuarzo de barrido', 'Titanio', '200 m']),
]

for e in EXPOSICIONES:
    e['precio'] = euros(desde_de(e['slug'])).replace(' €', '€')
    e['enlace'] = '/' + e['slug'] + '.html'

PRIMERA_EXPO = EXPOSICIONES[0]


def punto(i, e):
    activo = ' class="active"' if i == 0 else ''
    return (f'        <button type="button"{activo} aria-label="Ver el {e["nombre"]}" '
            f'aria-pressed="{"true" if i == 0 else "false"}" data-hero-vista="{i}"></button>\n')


ACTO_1 = f"""
  <section class="home-hero">
    <div class="lunar-hero-media{' is-close' if PRIMERA_EXPO['encuadre'] == 'cerca' else ''}" role="img" aria-label="{PRIMERA_EXPO['alt']}" data-hero>
      <img class="lunar-hero-image" src="{PRIMERA_EXPO['foto']}" alt="" aria-hidden="true" loading="eager" fetchpriority="high">
      <div class="lunar-hero-veil" aria-hidden="true"></div>
      <button class="lunar-hero-arrow previous" type="button" aria-label="Reloj anterior" data-hero-paso="-1">‹</button>
      <button class="lunar-hero-arrow next" type="button" aria-label="Reloj siguiente" data-hero-paso="1">›</button>
      <div class="lunar-hero-dots" role="group" aria-label="Elegir reloj">
{''.join(punto(i, e) for i, e in enumerate(EXPOSICIONES))}      </div>
    </div>
    <div class="home-hero-copy lunar-home-copy">
      <p class="lunar-eyebrow">Llego el momento de</p>
      <h1 class="lunar-title"><img src="{LOGO_CLARO}" alt="laOra"><span data-hero-nombre>{PRIMERA_EXPO['nombre']}</span></h1>
      <!-- sin espacios alrededor de la barra: la separación la da el
           `padding` del <i> en la hoja, y con espacios además del padding
           la primera exposición salía algo más suelta que las otras dos -->
      <p class="lunar-specs" data-hero-specs>{'<i>|</i>'.join(PRIMERA_EXPO['specs'])}</p>
      <p class="lunar-price" data-hero-precio>desde {PRIMERA_EXPO['precio']}</p>
      <div class="lunar-actions"><a class="lunar-action reserve" href="{PRIMERA_EXPO['enlace']}" data-hero-reservar>Reservar</a><a class="lunar-action more" href="#lunar-detalle">Saber mas</a></div>
    </div>
  </section>

  <script type="application/json" data-exposiciones>{json.dumps(EXPOSICIONES, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>"""


# ============================================================
# ACTO 2 · CONVERSACIÓN  ·  LunarDialogue.tsx
# El texto va sin comillas, tal como lo pidió Óscar.
# ============================================================
ACTO_2 = f"""
  <section class="lunar-dialogue" aria-labelledby="lunar-dialogue-question">
    <img class="lunar-dialogue-image" src="{V2}/lunar-wrist.png" alt="Reloj Lunar en una muñeca con correa de piel marrón">
    <div class="lunar-dialogue-veil" aria-hidden="true"></div>
    <div class="lunar-dialogue-copy">
      <h2 id="lunar-dialogue-question">Qué chulo. ¿Cuál es?</h2>
      <p>Es un {marca('dialogue-brand', LOGO_OSCURO)}. Marca española, los montan en Madrid a mano. Zafiro, mecanismo Seiko. Doscientos noventa y nueve.</p>
    </div>
    <span class="lunar-dialogue-number" aria-hidden="true">02</span>
  </section>"""


# ============================================================
# ACTO 3 · ORGULLO  ·  LunarPride.tsx
# ============================================================
ACTO_3 = f"""
  <section class="lunar-pride" aria-labelledby="lunar-pride-title">
    <img class="lunar-pride-image" src="{V2}/lunar-pride-reflection-v2.png" alt="Reflejo de un hombre contemplando orgulloso su cronógrafo en un escaparate urbano">
    <div class="lunar-pride-veil" aria-hidden="true"></div>
    <div class="lunar-pride-copy">
      <p>el gesto</p>
      <h2 id="lunar-pride-title">No es mirar la hora</h2>
      <p>es enseñarlo, sin enseñarlo</p>
    </div>
    <span class="lunar-pride-number" aria-hidden="true">03</span>
  </section>"""


# ============================================================
# ACTO 4 · CARRUSEL DE CONFIANZA  ·  TrustCarousel.tsx
# ============================================================
CONFIANZA = [
    ('01', 'Marca propia', 'Sin emblemas ni logotipos ajenos.',
     'trust-marca-propia.png', 'Cronógrafo laOra de acero presentado en un estudio oscuro'),
    ('02', 'Montaje en Madrid', 'Ajuste y control unidad a unidad.',
     'trust-montaje-madrid-v2.png', 'Manos de relojero ajustando el mecanismo visible de un cronógrafo boca abajo'),
    ('03', 'Componentes identificados', 'Origen y movimiento, sin rodeos.',
     'trust-componentes.png', 'Componentes de un reloj dispuestos en un despiece técnico'),
    ('04', 'Stock real', 'Envío en 48 h cuando se indica.',
     'trust-stock-real-v2.png', 'Cajas cerradas laOra con sello negro preparadas para el envío'),
    ('05', 'Servicio cercano', 'Taller y posventa en España.',
     'trust-servicio-cercano-v2.png', 'Mensajero profesional entregando un paquete a domicilio en Madrid'),
]


def tarjeta_confianza(n, titulo, texto, foto, alt):
    return f"""      <article class="trust-card">
        <img src="{V2}/{foto}" alt="{alt}">
        <div class="trust-card-veil" aria-hidden="true"></div>
        <div class="trust-card-copy"><h2>{titulo}</h2><p>{texto}</p></div>
        <span class="trust-card-number" aria-hidden="true">{n}</span>
      </article>
"""


ACTO_4 = ("""
  <section class="trust-carousel" aria-label="Cinco razones para confiar en laOra">
    <div class="trust-carousel-track" data-carrusel>
"""
          + ''.join(tarjeta_confianza(*c) for c in CONFIANZA)
          + """    </div>
    <button class="trust-carousel-arrow previous" type="button" aria-label="Ver tarjeta anterior" data-carrusel-paso="-1">‹</button>
    <button class="trust-carousel-arrow next" type="button" aria-label="Ver tarjeta siguiente" data-carrusel-paso="1">›</button>
  </section>""")


# ============================================================
# ACTO 5 · DECISIÓN DE COMPRA  ·  MarketMap.tsx
# Las dos comparaciones y la tabla de movimientos van en el HTML y las
# cambia `lunarv2.js`, igual que el estado de React.
# ============================================================
COMPARACIONES = {
    'lunar': dict(
        pestana='SPEEDMASTER → LUNAR',
        titulo='El cronógrafo lunar',
        intro='Del canal oficial al mercado irregular: cinco rutas que pueden parecer similares en una foto, pero no ofrecen lo mismo.',
        filas=[
            ('01 · BOUTIQUE OFICIAL', 'Omega Speedmaster Moonwatch', '7.700 €', 'Nuevo, documentado y con garantía oficial.', 'regular'),
            ('02 · SUBASTA', 'Catawiki / similares', '≈ 5.800 € + gastos', 'Ejemplo orientativo: usado; caja, papeles y estado dependen del lote.', 'regular'),
            ('03 · GRIS / USADO', 'Chrono24', '4.400–6.300 €', 'Rango observado en referencias habituales. Autenticidad y set cambian el valor.', 'regular'),
            ('04 · PIEZAS NO ORIGINALES', 'Marketplaces generalistas', '650–1.250 €', 'Relojes reacondicionados o con componentes de procedencia no acreditada.', 'irregular'),
            ('05 · FALSIFICACIÓN', '«Superclones»', '600–1.650 €', 'Marca suplantada, origen incierto y sin garantía legítima.', 'irregular'),
        ],
        alternativas=[('Bulova Lunar Pilot', '549–659 €'),
                      ('Seiko Prospex Speedtimer', '646–680 €'),
                      ('Tissot PR516 Chronograph', '545–625 €')]),
    'bitacora': dict(
        pestana='NAUTILUS → BITÁCORA',
        titulo='El deportivo integrado',
        intro='Del canal oficial a la falsificación: cinco rutas con precios, riesgos y garantías completamente distintos.',
        filas=[
            ('01 · BOUTIQUE OFICIAL', 'Patek Philippe Nautilus', '≈ 70.000 €', 'Precio de referencia y listas de espera interminables.', 'regular'),
            ('02 · SUBASTA', 'Casas especializadas', 'Muy variable', 'Referencia, material, estado y documentación mandan.', 'regular'),
            ('03 · GRIS / USADO', 'Chrono24', '105.000–180.000 €', 'El mercado secundario puede superar ampliamente el precio oficial.', 'regular'),
            ('04 · PIEZAS NO ORIGINALES', 'Marketplaces generalistas', '650–1.500 €', 'Montajes con componentes de procedencia no acreditada.', 'irregular'),
            ('05 · FALSIFICACIÓN', '«Superclones»', '600–1.650 €', 'Marca suplantada, origen incierto y sin garantía legítima.', 'irregular'),
        ],
        alternativas=[('Tissot PRX Powermatic 80', '≈ 750 €'),
                      ('Citizen Tsuyosa', '≈ 350 €')]),
}

MOVIMIENTOS = [
    ('★★★★★', 'Rolex Cosmograph Daytona', '16.550 €', 'Excelente', 'Muy buena', 'Alto', ''),
    ('★★★★★', 'Grand Seiko Tentagraph', '15.000 €', 'Excelente', 'Muy buena', 'Alto', ''),
    ('★★★★★', 'Omega Speedmaster Racing Master Chronometer', '11.000 €', 'Excelente', 'Muy buena', 'Alto', ''),
    ('★★★★☆', 'laOra Lunar · Seiko VK63', euros(DESDE), 'Muy alta', 'Excelente', 'Muy bajo', ' laora'),
    ('★★★☆☆', 'Seagull', '300 €', 'Buena', 'Buena', 'Medio', ''),
    ('★★☆☆☆', 'Miyota básicos — Citizen, Timex', '300 €', 'Correcta', 'Excelente', 'Muy bajo', ''),
]


def ruta(canal, nombre, precio, nota, tono):
    return (f'            <article class="{tono}"><span>{canal}</span><b>{nombre}</b>'
            f'<strong>{precio}</strong><small>{nota}</small></article>\n')


def fila_movimiento(estrellas, modelo, precio, calidad, precision, mant, extra):
    return (f'            <div class="movement-row{extra}" role="row"><span>{estrellas}</span>'
            f'<b>{modelo}</b><strong>{precio}</strong><span>{calidad}</span>'
            f'<span>{precision}</span><span>{mant}</span></div>\n')


PRIMERA = COMPARACIONES['lunar']

ACTO_5 = f"""
  <div id="lunar-detalle">
    <section class="decision-act" aria-labelledby="decision-title">
      <header class="decision-head">
        <div>
          <p class="decision-kicker">01 — EL MAPA DEL PRECIO</p>
          <h2 id="decision-title">Lo que cuesta un icono.<br><em>Y lo que pagas realmente.</em></h2>
        </div>
        <p>Una comparación de canales, riesgos y alternativas. Sin confundir homenaje con falsificación.</p>
      </header>

      <div class="decision-mobile-switch" role="group" aria-label="Elegir información">
        <button type="button" class="active" aria-pressed="true" data-panel="price">El precio</button>
        <button type="button" aria-pressed="false" data-panel="movement">El movimiento</button>
      </div>

      <div class="decision-main">
        <section class="decision-price-panel mobile-active" aria-label="Mapa del precio" data-panel-price>
          <div class="decision-model-tabs" role="group" aria-label="Elegir comparación">
            <button type="button" class="active" aria-pressed="true" data-comparacion="lunar">{COMPARACIONES['lunar']['pestana']}</button>
            <button type="button" aria-pressed="false" data-comparacion="bitacora">{COMPARACIONES['bitacora']['pestana']}</button>
          </div>
          <div class="decision-panel-intro" data-intro><strong>{PRIMERA['titulo']}</strong><span>{PRIMERA['intro']}</span></div>
          <div class="decision-market-labels" aria-hidden="true"><span>MERCADO ORIGINAL Y TRAZABLE</span><span>MERCADO IRREGULAR / CLONES</span></div>
          <div class="decision-routes" data-rutas>
{''.join(ruta(*f) for f in PRIMERA['filas'])}          </div>
          <div class="decision-alternatives" data-alternativas>
            <span>ALTERNATIVAS DE OTRAS MARCAS</span>
{''.join(f'            <div><b>{n}</b><small>{p}</small></div>' + chr(10) for n, p in PRIMERA['alternativas'])}          </div>
        </section>

        <section class="decision-movement-panel" aria-label="Comparación del movimiento" data-panel-movement>
          <div class="movement-intro">
            <p>01 — POR QUÉ ESTE MOVIMIENTO</p>
            <h3>Dónde hemos puesto <em>el presupuesto.</em></h3>
            <span>Seiko VK63: precisión del cuarzo, tacto de cronógrafo mecánico y mantenimiento mínimo. <b>±20 segundos al mes aproximadamente.</b></span>
          </div>
          <div class="movement-table" role="table" aria-label="Comparación de movimientos">
            <div class="movement-row movement-header" role="row"><span>VALORACIÓN</span><span>MODELO</span><span>PVP</span><span>CALIDAD</span><span>PRECISIÓN</span><span>MANT.</span></div>
{''.join(fila_movimiento(*m) for m in MOVIMIENTOS)}          </div>
        </section>
      </div>

      <article class="decision-answer">
        <img src="{IMG}/lunar-front.webp" alt="Reloj laOra Lunar">
        <div class="decision-product"><span>Reloj</span><div><img src="{LOGO_CLARO}" alt="laOra"><b>· LUNAR</b></div></div>
        <strong class="decision-price">{euros(DESDE)}</strong>
        <p>Mismo acero, mismo cristal, mismos movimientos</p>
        <a href="/lunar.html">VER LUNAR →</a>
      </article>

      <p class="decision-footnote">Precios orientativos consultados en agosto de 2026; pueden variar por referencia, estado, impuestos, comisiones y envío. La presencia de una oferta no acredita su autenticidad. Las marcas citadas pertenecen a sus titulares y no están afiliadas a laOra.</p>
    </section>
  </div>"""

# Los datos de la otra pestaña viajan en un JSON que lee `lunarv2.js`,
# igual que el objeto `comparisons` del componente.
DATOS_COMPARACIONES = json.dumps(COMPARACIONES, ensure_ascii=False).replace('<', '\\u003c')


# ============================================================
# ACTO 6 · ESPECIFICACIONES  ·  LunarSpecifications.tsx
# La ficha técnica se monta al pulsar, como en React, donde el overlay
# solo existe mientras está abierto: por eso va en un <template>.
# ============================================================
DESTACADOS = [
    ('01', 'VK63', 'Mecacuarzo Seiko/TMI'),
    ('02', '316L', 'Caja de acero · 40 mm'),
    ('03', 'Zafiro', 'Cristal plano'),
    ('04', '100 m', 'Estanqueidad · 10 ATM'),
    ('05', 'Taquímetro', 'Bisel de aluminio negro'),
    ('06', '904L', 'Brazalete de acero · 20 mm'),
]

GRUPOS_TECNICOS = [
    ('01', 'Movimiento', [
        ('MOVIMIENTO', 'Mecacuarzo Seiko/TMI VK63'),
        ('TIPO', 'Cronógrafo mecacuarzo'),
        ('FRECUENCIA', 'Cuarzo de 32.768 Hz; cronógrafo a 1/1 s con vuelta a cero mecánica'),
        ('AUTONOMÍA', 'Pila SR927SW, unos 3 años'),
    ]),
    ('02', 'Caja y cristal', [
        ('CRISTAL', 'Zafiro plano'),
        ('CAJA', 'Acero inoxidable 316L, pulido y satinado'),
        ('DIÁMETRO', '40 mm'),
        ('ESTANQUEIDAD', '100 m (10 ATM)'),
        ('BISEL', 'Fijo con escala taquimétrica, inserto de aluminio anodizado negro'),
        ('GROSOR', 'unos 13 mm'),
    ]),
    ('03', 'Esfera y ajuste', [
        ('ESFERA', 'Negra con tres subesferas, índices con detalles naranja'),
        ('LUMINISCENCIA', 'Super-LumiNova'),
        ('ANCHO DE ASA', '20 mm'),
        ('FONDO', 'Atornillado, acero macizo'),
        ('CORONA', 'Roscada'),
        ('PESO', 'de unos 100 g con caucho a unos 120 g con brazalete'),
        ('REFERENCIA', 'LO—01'),
    ]),
]


def destacado(n, valor, etiqueta):
    return f'      <li><span>{n}</span><div><strong>{valor}</strong><p>{etiqueta}</p></div></li>\n'


def grupo_tecnico(n, titulo, filas):
    lineas = ''.join(f'            <div><dt>{a}</dt><dd>{b}</dd></div>\n' for a, b in filas)
    return f"""        <section class="technical-group">
          <header><span>{n}</span><h3>{titulo}</h3></header>
          <dl>
{lineas}          </dl>
        </section>
"""


ACTO_6 = f"""
  <section class="lunar-spec-act" aria-labelledby="lunar-spec-title">
    <div class="lunar-spec-stage" aria-hidden="true"><img src="{IMG}/lunar-front.webp" alt=""></div>

    <header class="lunar-spec-intro">
      <p>LO—01 · ESPECIFICACIONES</p>
      <h2 id="lunar-spec-title">Todo identificado. <em>Nada escondido.</em></h2>
    </header>

    <ol class="lunar-spec-highlights">
{''.join(destacado(*d) for d in DESTACADOS)}    </ol>

    <div class="lunar-spec-footer">
      <span>LO—01 · LUNAR</span>
      <button type="button" data-abre-ficha>Ver ficha técnica completa</button>
      <strong>desde {euros(DESDE)}</strong>
    </div>
  </section>

  <template data-ficha>
    <div class="technical-overlay" role="dialog" aria-modal="true" aria-labelledby="technical-title">
      <div class="technical-overlay-head">
        <div>
          <p>LO—01 · FICHA TÉCNICA COMPLETA</p>
          <h2 id="technical-title">Todo el Lunar.<br><em>Dato a dato.</em></h2>
        </div>
        <div class="technical-reference"><span>Referencia</span><strong>LO-01_Lunar_A04</strong></div>
        <button type="button" aria-label="Cerrar ficha técnica" data-cierra-ficha>×</button>
      </div>
      <div class="technical-groups">
{''.join(grupo_tecnico(*g) for g in GRUPOS_TECNICOS)}      </div>
      <div class="technical-overlay-footer">
        <p>Seiko/TMI VK63 · Zafiro · Acero 316L · 100 m</p>
        <button class="technical-close-bottom" type="button" data-cierra-ficha>Cerrar ficha</button>
      </div>
    </div>
  </template>"""


# ============================================================
# EL CIERRE DE LA PÁGINA  ·  el resto de page.tsx
# Las cuatro tarjetas salen de catalogo.json: código, familia, precio,
# frase y homenaje. Donde no hay precio cerrado va el diámetro.
# ============================================================
def tarjeta(slug, foto):
    r = R[slug]
    if r['precio'] is not None:
        dato = 'desde ' + euros(r['precio'])
    else:
        dato = r['diametro']
    return f"""      <article class="product-card">
        <a class="product-visual" href="/{slug}.html">
          <img src="{foto}" alt="Reloj {r['nombre']} de laOra" loading="lazy">
          <span class="product-code">{r['codigo']}</span>
          <span class="product-arrow">↗</span>
        </a>
        <div class="product-meta"><p>{r['familia']}</p><p>{dato}</p></div>
        <h3><a href="/{slug}.html">{r['nombre']}</a></h3>
        <p class="product-line">{r['frase']}</p>
        <p class="homage-label">{r['homenaje']}</p>
      </article>
"""


TARJETAS = [('lunar', f'{IMG}/lunar-front.webp'),
            ('precisa', f'{IMG}/precisa-front.webp'),
            ('bauhaus', f'{IMG}/bauhaus-profile.webp'),
            ('tortuga', f'{IMG}/tortuga-detail.webp')]

CAPAS = [
    ('01', 'Cristal', 'Zafiro cuando la configuración lo incluye.'),
    ('02', 'Caja', 'Acero 316L o titanio según acabado.'),
    ('03', 'Esfera', 'Nombre y emblema laOra. Ninguna marca ajena.'),
    ('04', 'Movimiento', 'Siempre identificado; nunca descrito con vaguedades.'),
    ('05', 'Cierre', 'Construcción y ajuste explicados en cada ficha.'),
]

CIERRE = f"""
  <section class="featured-products">
    <div class="product-grid compact">
{''.join(tarjeta(*t) for t in TARJETAS)}    </div>
    <a class="button outline" href="/coleccion.html">Ver los ocho modelos →</a>
  </section>

  <section class="homage-manifesto">
    <div class="manifesto-media"><img src="{IMG}/precisa-hero.webp" alt="Reloj laOra Precisa de acero y esfera azul"></div>
    <div class="manifesto-copy"><p class="kicker light">Homenaje no es falsificación</p><h2>La inspiración se reconoce.<br><em>La identidad no se suplanta.</em></h2><p>Un homenaje toma una arquitectura conocida como punto de partida. Una falsificación intenta hacerse pasar por otra marca. En laOra no ocultamos la referencia y nunca ponemos en la esfera un nombre que no sea el nuestro.</p><ul><li><span>✓</span> Marca, modelo y documentación laOra</li><li><span>✓</span> Sin logotipos, coronas ni escudos de terceros</li><li><span>✓</span> Sin historias de origen inventadas</li><li><span>✓</span> Sin sugerir afiliaciones que no existen</li></ul><a class="text-link light" href="/filosofia.html">Nuestra forma de hacer →</a></div>
  </section>

  <section class="quality-section">
    <div class="section-head"><p class="section-number">02 — CALIDAD DEMOSTRABLE</p><h2>El misterio está en el reloj.<br><em>La confianza, en mostrarlo todo.</em></h2></div>
    <div class="quality-grid">
      <div class="quality-watch"><img src="{IMG}/lunar-detail.webp" alt="Detalle del reloj laOra Lunar"><span class="orbit orbit-a"></span><span class="orbit orbit-b"></span></div>
      <ol>
{''.join(f'        <li><span>{n}</span><div><b>{t}</b><p>{x}</p></div></li>' + chr(10) for n, t, x in CAPAS)}      </ol>
    </div>
  </section>

  <section class="madrid-section">
    <img src="{IMG}/workshop-hero.webp" alt="Detalle del proceso de revisión de un reloj laOra">
    <div class="madrid-overlay"><p class="kicker light">Taller laOra · Madrid</p><h2>Antes de llegar a tu muñeca,<br><em>pasa por nuestras manos.</em></h2><ol><li>Inspección</li><li>Montaje</li><li>Ajuste</li><li>Pruebas</li><li>Control visual</li><li>Envío</li></ol><a class="button light-button" href="/taller.html">Conocer el proceso</a></div>
  </section>

  <section class="club-preview">
    <div class="club-copy"><p class="section-number">03 — CLUB LAORA</p><h2>Tu reloj continúa<br><em>dentro de la app.</em></h2><p>Certificado, factura, garantía, historial, contacto directo con el taller y ventajas por recomendación. Todo en un único lugar, privado por defecto.</p><a class="button primary" href="/club.html">Conocer Club laOra →</a></div>
    <div class="club-phone-wrap">
      <div class="phone" aria-label="Vista previa de la aplicación Club laOra">
        <div class="phone-bar"><span>9:41</span><i></i></div>
        <div class="phone-greeting"><div><small>Buenos días</small><b>Tu Club laOra</b></div><span>OM</span></div>
        <div class="phone-member"><span>MIEMBRO Nº 0026</span><span>480 PUNTOS</span></div>
        <div class="phone-watch"><img src="{IMG}/tortuga-detail.webp" alt="Reloj Tortuga registrado en Club laOra"><div><small>MI RELOJ · LO—08</small><b>Tortuga</b><span>Garantía activa</span></div></div>
        <div class="phone-actions"><span><b>▤</b>Factura</span><span><b>◇</b>Garantía</span><span><b>↗</b>Taller</span></div>
        <div class="phone-notice"><small>SERVICIO</small><b>Tu revisión está al día</b><span>Ver pasaporte digital →</span></div>
        <div class="phone-nav"><span>⌂</span><span>◫</span><span>◎</span><span>○</span></div>
      </div>
      <div class="float-card"><b>Pasaporte digital</b><span>LO—08 · Verificado</span></div>
    </div>
  </section>

  <section class="final-cta"><p class="kicker">Tu tiempo. Tu elección.</p><h2>Elige el icono.<br><em>Nosotros respondemos por el reloj.</em></h2><div class="button-row"><a class="button primary" href="/coleccion.html">Ver la colección</a><a class="text-link" href="/club.html">Conocer Club laOra</a></div></section>"""


PIE = f"""
<footer class="site-footer">
  <div class="footer-top">
    <div>{marca('brand-logo', LOGO_CLARO)}<p>Homenajes honestos a los iconos mundiales de la relojería. Marca propia, montaje y servicio en Madrid.</p></div>
    <div class="footer-links"><a href="/coleccion.html">Colección</a><a href="/filosofia.html">Filosofía</a><a href="/club.html">Club laOra</a><a href="/taller.html">Taller</a></div>
    <div class="footer-links"><a href="/carrito">Carrito</a><a href="/cuenta">Mi cuenta</a><a href="mailto:hola@laora.es">hola@laora.es</a><a href="#legal">Aviso legal</a></div>
  </div>
  <div class="footer-bottom" id="legal">
    <span>© 2026 laOra®</span>
    <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
  </div>
</footer>"""


DESCRIPCION = ('Relojes homenaje con marca propia, componentes identificados y montaje, '
               'ajuste, control y servicio en Madrid.')

PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{DESCRIPCION}">
<!-- PÁGINA DE PRUEBAS: invisible a propósito. No está enlazada desde
     ninguna otra página y aquí se le pide al buscador que no la indexe. -->
<meta name="robots" content="noindex, nofollow">
<meta property="og:title" content="laOra · Homenajes honestos a los iconos de la relojería">
<meta property="og:description" content="{DESCRIPCION}">
<meta property="og:locale" content="es_ES">
<meta property="og:type" content="website">
<title>laOra · Homenajes honestos a los iconos de la relojería</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<!-- GENERADO por herramientas/generar_v2.py — no editar a mano.
     Porte del material aprobado el 05/08/2026. Mismas clases, mismo
     orden y mismos textos que los componentes de React del zip. -->
<link rel="stylesheet" href="/assets/css/lunarv2.css?v={V_CSS}">
</head>
<body>
{CABECERA}

<main>
{ACTO_1}
{ACTO_2}
{ACTO_3}
{ACTO_4}
{ACTO_5}
{ACTO_6}
{CIERRE}
</main>
{PIE}

<script type="application/json" data-comparaciones>{DATOS_COMPARACIONES}</script>
<script src="/assets/js/lunarv2.js?v={V_JS}"></script>
</body>
</html>
"""

destino = os.path.join(RAIZ, 'lunarv2.html')
with open(destino, 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print(f'lunarv2.html escrito · 6 actos · el Lunar desde {euros(DESDE)}')
if abs(DESDE - 219.90) > 0.001:
    print('  ⚠ OJO: el material aprobado dice «desde 219,90 €» y la hoja da '
          f'{euros(DESDE)}. Habla con Óscar antes de publicar esto.')
