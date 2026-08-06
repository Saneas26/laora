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
import re
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO: Cloudflare sirve el CSS con max-age=14400.
V_CSS = 28
V_JS = 8

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
    <!-- El icono de ayuda (los auriculares) lo quitó Óscar el 05/08/2026. -->
    <!-- El carrito y la cuenta se quedan A LA VISTA pero SIN FUNCIÓN hasta
         que existan, por encargo de Óscar (05/08/2026). Van como botones
         desactivados y no como enlaces: antes apuntaban a /carrito y
         /cuenta, que no existen, y daban un 404. Un botón apagado se
         entiende; un 404 parece que la web está rota. -->
    <a class="header-icon profile-icon" href="/cuenta" aria-label="Tu cuenta"><span aria-hidden="true"></span></a>
    <button class="header-icon bag-icon" type="button" disabled aria-label="Carrito, todavía no disponible" title="Muy pronto"><span aria-hidden="true"></span><b>0</b></button>
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
def desde_de(slug, acabado=None):
    """El precio más bajo del reloj, o el de UN acabado concreto.

    Hace falta lo segundo porque no todos los acabados llevan lo mismo:
    el Cero Cero solo tiene zafiro y doble corona en el Levante, y
    anunciar eso con el precio del Alba sería mentir."""
    cfg = R[slug]['configurador']
    listas = [cfg['precios'][acabado]] if acabado else list(cfg['precios'].values())
    return min(p for l in listas for p in l if p is not None)


# Los OCHO relojes del catálogo, uno por exposición (Óscar, 06/08/2026).
# Antes eran tres. Las fotos son las del paquete `laora-heroes-acto-01`:
# todas 16:9, a sangre, con el reloj centrado abajo y el tercio superior
# limpio para el titular. Por eso ya no hay encuadre `cerca`: el recorte
# del Lunar existía para salvar una foto que no estaba pensada para esto.
#
# Bauhaus no entra: no está en el catálogo activo y no tiene configurador
# ni precio, así que no habría ni «desde» ni adónde llevar el botón.
ESCENAS = {
    'lunar':     'un paisaje lunar con un cohete difuminado al fondo',
    'cero-cero': 'un horizonte marino con una baliza',
    'bitacora':  'arquitectura madrileña',
    'trinchera': 'un mapa de campo sobre lona verde oliva',
    'precisa':   'un estudio geométrico en azul',
    'diver':     'una costa de basalto y agua profunda',
    'tortuga':   'una costa húmeda de verde oscuro',
    'coctel':    'la barra de un bar de noche, en ámbar',
}

# El orden en que se pasan. Delante el Lunar, que es el que Óscar puso de
# cara; detrás, los demás.
ORDEN = ['lunar', 'cero-cero', 'bitacora', 'diver', 'precisa', 'trinchera', 'tortuga', 'coctel']


def _corta(v):
    """`44 mm (buceo, estilo cojín)` → `44 mm`."""
    return re.split(r'[(,]', str(v or ''))[0].strip()


def _agua(acabado):
    """Los METROS de agua de ESTE acabado, y de ninguno más.

    OJO, esto es importante y costó un susto: la primera versión, si el
    acabado no traía dato, se caía al del modelo. Y el del modelo es el
    del MEJOR acabado. En el Trinchera eso hacía que la portada
    anunciara «200 m» —que son del Cenit, de 449 €— en la exposición del
    reloj de entrada, cuyo fabricante NO declara estanqueidad ninguna.
    Anunciar una resistencia al agua que nadie ha declarado no es un
    fallo de maquetación: es una promesa que el reloj puede no cumplir.

    Así que aquí no hay herencia. Si este acabado no lo dice, no se
    dice."""
    m = re.search(r'(\d+)\s*m\b', str(acabado.get('estanqueidad') or ''))
    return m.group(1) + ' m' if m else ''


def _movimiento(reloj, acabado):
    """El movimiento en dos palabras.

    OJO: la hoja trae ruido. El Trinchera tiene `AR25` como tipo de
    movimiento y `AX25` como estanqueidad —restos de una columna corrida
    al volcar—, así que cuando el tipo no parece una frase se tira del
    campo `movimiento`, que sí está bien."""
    tipo = str(acabado.get('movimientoTipo') or '')
    if ' ' not in tipo:                       # `AR25` y compañía: no es una frase
        tipo = str(acabado.get('movimiento') or reloj.get('movimiento') or '')
        dentro = re.search(r'\(([^)]*)\)', tipo)   # `VH31 (TMI Vh31b, cuarzo japonés)`
        if dentro:
            tipo = dentro.group(1).split(',')[-1]
    tipo = re.split(r'[(,]| con ', tipo)[0].strip()
    # «Cuarzo» a secas se queda corto al lado de los demás, que dicen de
    # dónde es. Si el calibre lo dice, se completa; si no, se queda así.
    if tipo.lower() == 'cuarzo':
        calibre = str(acabado.get('movimiento') or '')
        if re.search(r'japon|jap\u00f3n', calibre, re.I):
            tipo = 'Cuarzo japonés'
        elif re.search(r'suiz', calibre, re.I):
            tipo = 'Cuarzo suizo'
    return tipo[:1].upper() + tipo[1:]


# El nombre del fichero de cada foto. Cuando Óscar sustituye una, NO se
# reutiliza el nombre: Cloudflare sirve la vieja desde su caché durante
# horas y parece que el cambio no ha entrado. Costó dos vueltas con la
# del Cóctel. Así que la foto nueva entra con nombre nuevo y la vieja se
# borra.
#
# 06/08/2026: la del Bitácora se cambió porque en la primera no se leían
# ni el logotipo ni el nombre del modelo en la esfera.
FOTO_ACTO = {
    'bitacora': 'bitacora-acto1-b',
}


# LOS TEXTOS DEL ACTO, UNO POR RELOJ
# ------------------------------------------------------------
# Óscar, 06/08/2026: «no siguen una estructura, sino te diré lo que hay
# que poner en cada uno». Así que aquí no se compone nada solo: lo que
# no esté escrito abajo se queda como estaba, con la frase de siempre y
# el renglón sacado del catálogo.
#
# El PRECIO no se escribe a mano: se pone {precio} y lo rellena el
# mínimo del configurador de ESE reloj. Si mañana cambia la hoja, el
# texto cambia solo y no se queda un precio viejo pintado en la portada.
#
# Los datos de la segunda línea del Lunar están comprobados contra la
# hoja: corona «Roscada (tipo Speedmaster)» y caja «Acero inoxidable
# 316L» en sus seis referencias Alba.
TEXTOS = {
    'lunar': {
        'frase': 'Un cronógrafo para los que no siguen el mismo camino.',
        'linea1': 'Cronógrafo mecacuarzo · 40 mm · 100 m',
        'linea2': 'Corona roscada · Acero 316L · Desde {precio}',
    },
    # 06/08/2026. Zafiro y doble corona son del LEVANTE, no del Alba: la
    # hoja dice «Mineral Hardlex (no es zafiro)» en el Alba y solo el
    # Levante lleva «2 coronas roscadas». Óscar eligió mantener las dos
    # cosas y subir el «desde» al acabado que sí las tiene, así que aquí
    # el precio NO es el mínimo del reloj sino el de ese acabado.
    # 06/08/2026, más tarde: lo cazó Óscar. Al subir el precio al Levante
    # se quedó «Cuarzo japonés» en el primer renglón, que es el
    # movimiento del ALBA. Las dos líneas hablaban de relojes distintos:
    # arriba el de 209,90 y abajo el de 279,90. Ahora las dos describen
    # el Levante, que es automático, de 41 mm y 100 m.
    'cero-cero': {
        'frase': 'Diseñado para misiones cotidianas.',
        'linea1': 'Automático · 41 mm · 100 m',
        'linea2': 'Cristal de zafiro · Doble corona · Desde {precio_levante}',
    },
    # 06/08/2026. Mismo caso que el Cero Cero y misma decisión de Óscar:
    # a 219,90 € el Bitácora es de CUARZO suizo; el automático empieza en
    # el Levante. Se mantiene «Automático» y el «desde» sube a ese
    # acabado. Comprobado que a 279,90 € siguen siendo ciertos el zafiro,
    # el acero 316L y los 40 mm.
    'bitacora': {
        'frase': 'El azul que no pasa desapercibido.',
        'linea1': 'Deportivo · Automático · 40 mm',
        'linea2': 'Acero 316L · Cristal de zafiro · Desde {precio_levante}',
    },
    # 06/08/2026, Óscar: «no me cambies nada de lo que yo te ponga, lo
    # tengo supervisado, aunque tú no lo puedas comprobar». Así que este
    # texto va literal.
    #
    # Lo que NO está en la hoja, por si algún día hay que defenderlo: la
    # casilla de luminiscencia del Diver dice «Según esfera laOra», que
    # es una nota de trabajo. El lumen lo pone Óscar, que es quien
    # decide la esfera.
    #
    # Aquí el precio va en su propia línea y sin «desde», como lo
    # escribió. 279,90 € es el Cenit, que es el único automático y tiene
    # precio único.
    'diver': {
        'frase': 'Serio bajo el agua. Divertido en todas partes.',
        'linea1': 'Automático Arquitectura suiza · 40 mm',
        'linea2': 'Resistencia al agua 300 m · Lumen de alto rendimiento',
        'precio': '{precio_cenit}',
    },
    # 06/08/2026. Texto de Óscar, literal. El segundo renglón lleva DOS
    # grupos separados por la barra —cuarzo a un precio, automático a
    # otro—, así que el punto se queda dentro de cada uno.
    'precisa': {
        'frase': 'La precisión también tiene estilo.',
        'linea1': 'Acero 316L · Cristal de zafiro · 40 mm',
        'linea2': 'Cuarzo · 229,90 € | Automático · 379,90 €',
        'precio': ' ',      # sin renglón de precio: ya va en el de arriba
    },
    # 06/08/2026. Texto de Óscar, literal. Los dos tamaños que anuncia
    # son los que se desbloquearon esta misma tarde al arreglar las dos
    # celdas rotas de la hoja: hasta hoy las cuatro cajas de 36 mm no se
    # podían ni pedir.
    'trinchera': {
        'frase': 'Dos tamaños. Tres acabados. Una actitud.',
        'linea1': 'Cuarzo japonés · 36 o 39 mm · Cristal de zafiro',
        'linea2': 'Plata · Cobre · Negro PVD · Desde {precio}',
    },
    # 06/08/2026. Texto de Óscar, literal. Los 44 mm son los que él
    # confirmó esta tarde, cuando el catálogo se contradecía consigo
    # mismo y decía 42 a nivel de modelo.
    'tortuga': {
        'frase': 'Nacido para ir despacio. Hecho para llegar hondo.',
        'linea1': 'Cuarzo japonés · 44 mm · 200 m',
        'linea2': 'Acero 316L · Desde {precio}',
    },
    # 06/08/2026. Texto de Óscar, literal, y con él quedan los ocho.
    # Segundo renglón de dos grupos, como el Precisa.
    'coctel': {
        'frase': 'Brilla cuando el día baja el ritmo.',
        'linea1': '40 mm · Correa de piel',
        'linea2': 'Cuarzo · 209,90 € | Automático Serie 9 · 349,90 €',
        'precio': ' ',      # los dos precios ya van en el renglón de arriba
    },
}


def _exposicion(slug):
    reloj = R[slug]
    acabado = reloj['configurador']['acabados'][0]
    return dict(
        slug=slug,
        nombre=reloj['nombre'],
        foto=f'/assets/img/heroes-2026/{FOTO_ACTO.get(slug, slug + "-acto1")}.webp',
        encuadre='',
        alt=f'Reloj laOra {reloj["nombre"]} sobre {ESCENAS[slug]}',
        specs=[
            _movimiento(reloj, acabado),
            _corta(acabado.get('diametro') or reloj.get('diametro')),
            # Cuando no hay metros declarados, la tercera casilla la ocupa
            # el cristal, que sí es un dato firme. Antes que callar un
            # hueco o rellenarlo con el dato de otro acabado.
            _agua(acabado) or _corta(acabado.get('cristal')),
        ],
    )


EXPOSICIONES = [_exposicion(s) for s in ORDEN]

for e in EXPOSICIONES:
    e['specs'] = [x for x in e['specs'] if x]          # nada vacío en el renglón
    e['precio'] = euros(desde_de(e['slug'])).replace(' €', '€')
    e['enlace'] = '/' + e['slug'] + '.html'

    t = TEXTOS.get(e['slug'])
    if t:
        # El «·» con el que Óscar escribe los renglones separa los datos;
        # en pantalla los separa la barra fina de la hoja de estilos, que
        # es la del material aprobado. Mismo contenido, misma tipografía.
        # `{precio}` es el mínimo del reloj; `{precio_levante}` —o el de
        # cualquier acabado— el de ESE acabado. Así ningún número va
        # escrito a mano y ninguno se queda viejo cuando cambie la hoja.
        precios = {'precio': euros(desde_de(e['slug']))}
        for a in R[e['slug']]['configurador']['acabados']:
            precios['precio_' + a['id'].replace('-', '_')] = euros(desde_de(e['slug'], a['id']))
        e['frase'] = t['frase']
        e['specs'] = [x.strip() for x in t['linea1'].split('·') if x.strip()]
        # Un `linea2` vacío es una decisión, no un olvido: significa que
        # el segundo renglón todavía no se puede publicar. Entonces
        # vuelve el precio suelto de siempre.
        # Dos formas de escribir un renglón, y las dos son de Óscar:
        #   «a · b · c»            → tres datos, separados por la barra
        #   «a · b | c · d»        → DOS grupos, y el punto se queda
        #                            dentro de cada uno como texto
        # Manda la barra si la hay: es el separador de más peso. Así el
        # Precisa puede decir «Cuarzo · 229,90 € | Automático · 379,90 €»
        # y sale exactamente como lo escribió.
        corte = '|' if '|' in t['linea2'] else '·'
        e['linea2'] = [x.strip().format(**precios)
                       for x in t['linea2'].split(corte) if x.strip()]
        # Un reloj puede querer el precio en su PROPIA línea y sin la
        # palabra «desde» —así lo escribió Óscar para el Diver—. Entonces
        # el renglón del precio deja de ser el de siempre y dice esto.
        # Un `precio` en blanco quiere decir «no pongas renglón de
        # precio»: el Precisa ya lleva los dos suyos en el renglón de
        # arriba, y repetirlos debajo sobraría.
        if t.get('precio') and t['precio'].strip():
            e['precioTexto'] = t['precio'].format(**precios)
        elif t.get('precio') is not None and not t['precio'].strip():
            e['sinPrecio'] = True
    else:
        e['frase'] = 'Llego el momento de'
        e['linea2'] = []

def precioVisible(e):
    """El renglón del precio se ve cuando el precio NO va ya dentro del
    segundo renglón. Si va dentro, saldría dos veces."""
    if e.get('sinPrecio'):
        return False
    return bool(e.get('precioTexto')) or not e['linea2']


def precioTexto(e):
    return e.get('precioTexto') or ('desde ' + e['precio'])


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
      <!-- LA FRASE DE ENCIMA SE QUITÓ el 06/08/2026, por encargo de
           Óscar: «vamos a quitar el comentario de los 8 relojes que está
           por encima de laOra nombre modelo».

           El texto NO se borra: sigue en `TEXTOS`, en el campo `frase`,
           y viaja en el JSON de las exposiciones. Volver a enseñarlo es
           devolver esta línea, nada más. Las ocho frases están escritas
           por Óscar y costaron su tiempo; no se tiran. -->
      <h1 class="lunar-title"><img src="{LOGO_CLARO}" alt="laOra"><span data-hero-nombre>{PRIMERA_EXPO['nombre']}</span></h1>
      <!-- sin espacios alrededor de la barra: la separación la da el
           `padding` del <i> en la hoja, y con espacios además del padding
           la primera exposición salía algo más suelta que las otras dos -->
      <p class="lunar-specs" data-hero-specs>{'<i>|</i>'.join(PRIMERA_EXPO['specs'])}</p>
      <p class="lunar-specs lunar-specs-2" data-hero-specs2{' hidden' if not PRIMERA_EXPO['linea2'] else ''}>{'<i>|</i>'.join(PRIMERA_EXPO['linea2'])}</p>
      <p class="lunar-price" data-hero-precio{'' if precioVisible(PRIMERA_EXPO) else ' hidden'}>{precioTexto(PRIMERA_EXPO)}</p>
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
    <img class="lunar-dialogue-image" src="{V2}/lunar-wrist.jpg" alt="Reloj Lunar en una muñeca con correa de piel marrón">
    <div class="lunar-dialogue-veil" aria-hidden="true"></div>
    <div class="lunar-dialogue-copy">
      <h2 id="lunar-dialogue-question">Qué chulo. ¿Cuál es?</h2>
      <p>Es un {marca('dialogue-brand', LOGO_OSCURO)}. Marca española, los montan en Madrid a mano. Zafiro, <b>mecanismos suizos y japoneses</b>. Doscientos diecinueve.</p>
    </div>
    <span class="lunar-dialogue-number" aria-hidden="true">02</span>
  </section>"""


# ============================================================
# ACTO 3 · ORGULLO  ·  LunarPride.tsx
# ============================================================
ACTO_3 = f"""
  <section class="lunar-pride" aria-labelledby="lunar-pride-title">
    <img class="lunar-pride-image" src="{V2}/lunar-pride-reflection-v2.jpg" alt="Reflejo de un hombre contemplando orgulloso su cronógrafo en un escaparate urbano">
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
    # La primera es el CÓCTEL y no otra vez el cronógrafo: en la portada
    # el Lunar ya sale en el hero, y verlo aquí de nuevo cansaba (Óscar,
    # 05/08/2026). Se eligió esta y no `coctel-hero`, que es la del
    # catálogo, porque el rótulo de la tarjeta va en blanco: medido, la
    # del catálogo tiene un fondo crema de brillo 207 y ahí el texto no
    # se lee; esta tiene 30, como la que sustituye. Y los marrones de la
    # esfera y de la correa mantienen los tonos del carrusel.
    ('01', 'Marca propia', 'Sin emblemas ni logotipos ajenos.',
     'coctel-bar-logo-alto.jpg', 'Reloj laOra Cóctel sobre la barra de un bar, con una copa al fondo'),
    ('02', 'Montaje en Madrid', 'Ajuste y control unidad a unidad.',
     'trust-montaje-madrid-v2.jpg', 'Manos de relojero ajustando el mecanismo visible de un cronógrafo boca abajo'),
    ('03', 'Componentes identificados', 'Origen y movimiento, sin rodeos.',
     'trust-componentes.jpg', 'Componentes de un reloj dispuestos en un despiece técnico'),
    ('04', 'Stock real', 'Envío en 48 h cuando se indica.',
     'trust-stock-real-v2.jpg', 'Cajas cerradas laOra con sello negro preparadas para el envío'),
    ('05', 'Servicio cercano', 'Taller y posventa en España.',
     'trust-servicio-cercano-v2.jpg', 'Mensajero profesional entregando un paquete a domicilio en Madrid'),
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
# ACTO 5 · EL MAPA DEL PRECIO  ·  MarketMap.tsx, rehecho
# ------------------------------------------------------------
# Óscar el 05/08/2026: «las tarjetas son muy grandes y los textos
# deberían ser mucho más grandes; ahora mismo eso no es nada atractivo
# de ver». Le doy la vuelta entera.
#
# QUÉ HABÍA: cinco tarjetas en columnas de la altura de media pantalla,
# con el nombre a 11 px, la nota a 9 px y el precio suelto dentro. Para
# comparar cinco precios había que leer cinco cajas y acordarse.
#
# QUÉ HAY AHORA: una barra por canal, todas contra la misma escala, de
# más caro a más barato, y el laOra al final. La comparación se ve, no
# se lee. Los cuerpos suben al mínimo que pide el propio documento de
# entrega —14 px en el ordenador— y el precio va a 22.
#
# LA ESCALA es lineal y honesta: el laOra sale como un hilo al lado de
# un icono de 7.700 €, y ese hilo ES el mensaje. Como una barra de un
# 0,1 % no se puede ver —el Nautilus llega a 180.000 €—, al lado de
# cada canal va cuántos laOra caben dentro, calculado sobre el precio
# MÁS BAJO de ese canal para no exagerar nunca.
#
# EL COLOR: una sola marca en oro, la nuestra, y el resto en gris. Es
# lo que la guía de visualización llama «emphasis», y es lo correcto
# cuando una serie es el asunto y las demás son el contexto. Se probó
# antes con tres colores —legítimo, irregular y laOra— y el validador
# lo tumbó: los dos grises de color no se distinguen ni con visión
# normal. Así que el mercado irregular se separa con su rótulo y con
# la trama diagonal, no con otro color.
# ============================================================
COMPARACIONES = {
    'lunar': dict(
        pestana='SPEEDMASTER → LUNAR',
        titulo='El cronógrafo lunar',
        intro='Del canal oficial al mercado irregular: cinco rutas que pueden parecer la misma en una foto y no ofrecen lo mismo.',
        nuestro='Lunar',
        filas=[
            # canal, nombre, precio escrito, mínimo, máximo, nota, tono
            ('01 · Boutique oficial', 'Omega Speedmaster Moonwatch', '7.700 €', 7700, 7700,
             'Nuevo, documentado y con garantía oficial.', 'regular'),
            ('02 · Subasta', 'Catawiki y similares', '≈ 5.800 € + gastos', 5800, 5800,
             'Usado. La caja, los papeles y el estado dependen del lote.', 'regular'),
            ('03 · Gris o usado', 'Chrono24', '4.400–6.300 €', 4400, 6300,
             'Rango habitual. La autenticidad y el conjunto cambian el valor.', 'regular'),
            ('04 · Piezas no originales', 'Marketplaces generalistas', '650–1.250 €', 650, 1250,
             'Reacondicionados o con componentes de procedencia no acreditada.', 'irregular'),
            ('05 · Falsificación', '«Superclones»', '600–1.650 €', 600, 1650,
             'Marca suplantada, origen incierto y sin garantía legítima.', 'irregular'),
        ],
        alternativas=[('Bulova Lunar Pilot', '549–659 €'),
                      ('Seiko Prospex Speedtimer', '646–680 €'),
                      ('Tissot PR516 Chronograph', '545–625 €')]),
    'bitacora': dict(
        pestana='NAUTILUS → BITÁCORA',
        titulo='El deportivo integrado',
        intro='Del canal oficial a la falsificación: cinco rutas con precios, riesgos y garantías completamente distintos.',
        nuestro='Bitácora',
        filas=[
            ('01 · Boutique oficial', 'Patek Philippe Nautilus', '≈ 70.000 €', 70000, 70000,
             'Precio de referencia y listas de espera interminables.', 'regular'),
            ('02 · Subasta', 'Casas especializadas', 'Muy variable', None, None,
             'Mandan la referencia, el material, el estado y la documentación.', 'regular'),
            ('03 · Gris o usado', 'Chrono24', '105.000–180.000 €', 105000, 180000,
             'El mercado secundario puede superar ampliamente el precio oficial.', 'regular'),
            ('04 · Piezas no originales', 'Marketplaces generalistas', '650–1.500 €', 650, 1500,
             'Montajes con componentes de procedencia no acreditada.', 'irregular'),
            ('05 · Falsificación', '«Superclones»', '600–1.650 €', 600, 1650,
             'Marca suplantada, origen incierto y sin garantía legítima.', 'irregular'),
        ],
        alternativas=[('Tissot PRX Powermatic 80', '≈ 750 €'),
                      ('Citizen Tsuyosa', '≈ 350 €')]),
}

# el precio de partida de cada uno de los nuestros, de `catalogo.json`
COMPARACIONES['lunar']['desde'] = desde_de('lunar')
COMPARACIONES['bitacora']['desde'] = desde_de('bitacora')

MOVIMIENTOS = [
    ('★★★★★', 'Rolex Cosmograph Daytona', '16.550 €', 'Excelente', 'Muy buena', 'Alto', ''),
    ('★★★★★', 'Grand Seiko Tentagraph', '15.000 €', 'Excelente', 'Muy buena', 'Alto', ''),
    ('★★★★★', 'Omega Speedmaster Racing Master Chronometer', '11.000 €', 'Excelente', 'Muy buena', 'Alto', ''),
    ('★★★★☆', 'laOra Lunar · Seiko VK63', euros(DESDE), 'Muy alta', 'Excelente', 'Muy bajo', ' laora'),
    ('★★★☆☆', 'Seagull', '300 €', 'Buena', 'Buena', 'Medio', ''),
    ('★★☆☆☆', 'Miyota básicos — Citizen, Timex', '300 €', 'Correcta', 'Excelente', 'Muy bajo', ''),
]


def fila_movimiento(estrellas, modelo, precio, calidad, precision, mant, extra):
    return (f'            <div class="movement-row{extra}" role="row"><span>{estrellas}</span>'
            f'<b>{modelo}</b><strong>{precio}</strong><span>{calidad}</span>'
            f'<span>{precision}</span><span>{mant}</span></div>\n')


PRIMERA = COMPARACIONES['lunar']


def barra(fila, tope, desde):
    """Una fila del mapa.

    La barra va desde CERO hasta el precio, que es como se lee una
    magnitud de un vistazo. Cuando el canal es un rango, el tramo sólido
    llega al precio más bajo y una prolongación más clara marca hasta
    dónde sube: así se ve a la vez lo que cuesta como poco y lo que
    puede llegar a costar.

    El múltiplo se calcula sobre el precio MÁS BAJO del canal, de modo
    que la cifra que se enseña es siempre la más conservadora.
    """
    canal, nombre, precio, minimo, maximo, nota, tono = fila
    if minimo:
        solido = max(minimo / tope * 100, 0.5)
        extra = max((maximo - minimo) / tope * 100, 0) if maximo else 0
        marca_html = (f'<span class="mp-solido" style="width:{solido:.2f}%"></span>'
                      + (f'<span class="mp-rango" style="left:{solido:.2f}%;width:{extra:.2f}%"></span>'
                         if extra > 0.2 else ''))
        multiplo = f'<p class="mp-multiplo">×{round(minimo / desde)}<span>el {PRIMERA["nuestro"]}</span></p>'
    else:
        marca_html = '<span class="mp-solido mp-indefinido" style="width:100%"></span>'
        multiplo = '<p class="mp-multiplo mp-sincifra">sin cifra<span>de referencia</span></p>'
    return f"""          <li class="mp-fila {tono}">
            <div class="mp-quien"><p class="mp-canal">{canal}</p><h3>{nombre}</h3><p class="mp-nota">{nota}</p></div>
            <div class="mp-pista">{marca_html}</div>
            <div class="mp-cifras"><p class="mp-precio">{precio}</p>{multiplo}</div>
          </li>
"""


# el logotipo, que en la fila nuestra va sobre fondo claro
MARCA_TXT = marca('mp-logo', LOGO_OSCURO)


def mapa(c):
    tope = max([f[4] for f in c['filas'] if f[4]] or [1])
    regular = ''.join(barra(f, tope, c['desde']) for f in c['filas'] if f[6] == 'regular')
    irregular = ''.join(barra(f, tope, c['desde']) for f in c['filas'] if f[6] == 'irregular')
    nuestra = f"""          <li class="mp-fila nuestro">
            <div class="mp-quien"><p class="mp-canal">Aquí estamos</p><h3>{MARCA_TXT} {c['nuestro']}</h3><p class="mp-nota">Marca propia, componentes identificados y montaje en Madrid.</p></div>
            <div class="mp-pista"><span class="mp-solido" style="width:{max(c['desde'] / tope * 100, 0.8):.2f}%"></span></div>
            <div class="mp-cifras"><p class="mp-precio">desde {euros(c['desde'])}</p><p class="mp-multiplo mp-base">×1<span>el punto de partida</span></p></div>
          </li>
"""
    return regular, irregular, nuestra


FILAS_HTML_REGULAR, FILAS_HTML_IRREGULAR, NUESTRA_HTML = mapa(PRIMERA)
ALTERNATIVAS_HTML = ''.join(
    f'        <div><b>{n}</b><small>{p}</small></div>\n' for n, p in PRIMERA['alternativas'])

ACTO_5 = f"""
  <div id="lunar-detalle">
    <section class="decision-act" aria-labelledby="decision-title">
      <header class="decision-head">
        <div>
          <p class="decision-kicker">01 — EL MAPA DEL PRECIO</p>
          <h2 id="decision-title">Lo que cuesta un icono.<br><em>Y lo que pagas realmente.</em></h2>
        </div>
        <p data-mp-intro>{PRIMERA['intro']}</p>
      </header>

      <div class="decision-model-tabs" role="group" aria-label="Elegir comparación">
        <button type="button" class="active" aria-pressed="true" data-comparacion="lunar">{COMPARACIONES['lunar']['pestana']}</button>
        <button type="button" aria-pressed="false" data-comparacion="bitacora">{COMPARACIONES['bitacora']['pestana']}</button>
      </div>

      <!-- EL MAPA · una barra por canal, todas contra la misma escala.
           Las cifras van FUERA de la barra, siempre legibles, y el
           múltiplo cuenta lo que una barra tan corta no puede enseñar. -->
      <div class="mp">
        <p class="mp-grupo">Mercado original y trazable</p>
        <ol class="mp-lista" data-mp-regular>
{FILAS_HTML_REGULAR}        </ol>

        <p class="mp-grupo mp-grupo-irregular">Mercado irregular y clones</p>
        <ol class="mp-lista mp-irregular" data-mp-irregular>
{FILAS_HTML_IRREGULAR}        </ol>

        <p class="mp-grupo mp-grupo-nuestro">Nuestra propuesta</p>
        <ol class="mp-lista mp-nuestra" data-mp-nuestro>
{NUESTRA_HTML}        </ol>
      </div>

      <div class="mp-alternativas" data-alternativas>
        <span>Alternativas de otras marcas</span>
{ALTERNATIVAS_HTML}      </div>

      <section class="decision-movement-panel" aria-label="Comparación del movimiento">
        <div class="movement-intro">
          <p>02 — POR QUÉ ESTE MOVIMIENTO</p>
          <h3>Dónde hemos puesto <em>el presupuesto.</em></h3>
          <span>Seiko VK63: precisión del cuarzo, tacto de cronógrafo mecánico y mantenimiento mínimo. <b>±20 segundos al mes aproximadamente.</b></span>
        </div>
        <div class="movement-table" role="table" aria-label="Comparación de movimientos">
          <div class="movement-row movement-header" role="row"><span>Valoración</span><span>Modelo</span><span>PVP</span><span>Calidad</span><span>Precisión</span><span>Mant.</span></div>
{''.join(fila_movimiento(*m) for m in MOVIMIENTOS)}        </div>
      </section>

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

# ============================================================
# LAS TRES SECCIONES RETIRADAS · GUARDADAS
# ------------------------------------------------------------
# Óscar las quitó el 05/08/2026: las tres que iban justo detrás del acto
# de las especificaciones. Eran, por orden, las cuatro tarjetas de
# relojes, el manifiesto de «homenaje no es falsificación» y el bloque
# de calidad demostrable.
#
# Quedan aquí enteras, como el pie, para volver a ponerlas cuando lo
# pida: se le quita el `_` al nombre y se vuelve a poner `{_TRES_GUARDADAS}`
# delante de `{CIERRE}` en la página.
# ============================================================
_TRES_GUARDADAS = f"""
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

"""


# lo que sigue en pie detrás del acto 6
CIERRE = f"""
  <section class="madrid-section">
    <img src="{IMG}/workshop-hero.webp" alt="Detalle del proceso de revisión de un reloj laOra">
    <div class="madrid-overlay"><p class="kicker light">Taller laOra · Madrid</p><h2>Antes de llegar a tu muñeca,<br><em>pasa por nuestras manos.</em></h2><ol><li>Inspección</li><li>Montaje</li><li>Ajuste</li><li>Pruebas</li><li>Control visual</li><li>Envío</li></ol>
      <!-- Óscar (05/08/2026): el botón que llevaba al taller se retira y
           en su sitio queda la garantía, como titular. -->
      <p class="madrid-garantia">Garantía de fabricación<br><em>hasta 5 años.</em></p></div>
  </section>

  <section class="club-preview">
    <div class="club-copy"><p class="section-number">CLUB LAORA</p><h2>Tu reloj continúa<br><em>dentro de la app.</em></h2><p>Certificado, factura, garantía, historial, contacto directo con el taller y ventajas por recomendación. Todo en un único lugar, privado por defecto.</p><a class="button primary" href="/club.html">Conocer Club laOra →</a></div>
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


# ============================================================
# EL PIE · GUARDADO Y RETIRADO
# ------------------------------------------------------------
# Óscar lo quitó de la portada el 05/08/2026: «el pie final de página
# de momento lo quitamos, déjalo almacenado». Aquí está entero, tal cual
# estaba, para volver a ponerlo cuando lo pida: se le quita el `_` al
# nombre y se vuelve a poner `{PIE}` en la página, al final.
#
# También se va con él el `hola@laora.es`, que es lo que pidió: ningún
# correo electrónico en la web.
#
# LO ÚNICO QUE NO SE VA es el aviso de marcas, que queda abajo en una
# línea. No es decoración: la portada nombra Omega, Patek Philippe,
# Rolex y Seiko en el acto del precio, y ese aviso es lo que separa el
# homenaje de la falsificación. Es de las cosas que Óscar no negocia.
# ============================================================
_PIE_GUARDADO = f"""
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



# El aviso de marcas, que se queda aunque el pie se vaya.
PIE = """
<footer class="aviso-marcas">
  <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
</footer>"""


DESCRIPCION = ('Relojes homenaje con marca propia, componentes identificados y montaje, '
               'ajuste, control y servicio en Madrid.')

PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{DESCRIPCION}">
<meta property="og:image" content="https://laora.es/assets/img/lunar-v2/lunar-hero-steel.webp">
<meta property="og:title" content="laOra · Homenajes honestos a los iconos de la relojería">
<meta property="og:description" content="{DESCRIPCION}">
<meta property="og:locale" content="es_ES">
<meta property="og:type" content="website">
<title>laOra · Homenajes honestos a los iconos de la relojería</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<!-- GENERADO por herramientas/generar_v2.py — no editar a mano.
     PORTADA de laora.es desde el 05/08/2026. Porte del material
     aprobado: mismas clases, mismo orden y mismos textos que los
     componentes de React del zip. -->
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

# ESTA ES LA PORTADA desde el 05/08/2026, por decisión de Óscar: la que
# ve cualquiera que entre en laora.es. Ya no es una página de pruebas,
# así que se escribe en `index.html` y sin `noindex`. La anterior sigue
# generándose, en `home-anterior.html`, y `/lunarv2` salta aquí.
destino = os.path.join(RAIZ, 'index.html')
with open(destino, 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print(f'lunarv2.html escrito · 6 actos · el Lunar desde {euros(DESDE)}')
if abs(DESDE - 219.90) > 0.001:
    print('  ⚠ OJO: el material aprobado dice «desde 219,90 €» y la hoja da '
          f'{euros(DESDE)}. Habla con Óscar antes de publicar esto.')
