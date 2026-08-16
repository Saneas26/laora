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
V_CSS = 32
V_JS = 69

# LA FICHA TÉCNICA, APAGADA (Óscar, 13/08/2026)
# ------------------------------------------------------------
# «vamos a quitar ver ficha técnica del configurador, no la elimines
# porque la mandaremos a laorateca». Así que no se borra nada: el botón
# de la cabecera y el diálogo entero dejan de escribirse en la página,
# y el JavaScript que los maneja ya comprueba que existan. Para
# devolverlos, poner esto en True.
FICHA_TECNICA = False

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

# CUÁNTO SE METE EL BRAZALETE DETRÁS DE LA CAJA
# ------------------------------------------------------------
# En PÍXELES DE LA FOTO, sobre el lienzo de 1000 de ancho. Antes esto
# era una fracción que el JavaScript multiplicaba por un 240 que no
# correspondía a nada: no convertía a la escala a la que se ve la foto,
# así que el desplazamiento real era de cuatro píxeles y medio.
#
# MEDIDO en `LO-03-C1-E1.webp`, barriendo fila a fila y contando los
# tramos opacos de cada una:
#     y = 200  puntas de las asas, hueco de 268 px entre ellas
#     y = 272  el hueco se cierra: ahí empieza la caja maciza
# O sea, 72 px de asa. Con los 45 de antes el último eslabón se
# quedaba a 27 px de la caja, y ese aire es el que se veía.
#
# Con 80 el eslabón llega a la caja y se mete 8 px por detrás, que es
# lo justo para que no asome ninguna costura. El hueco entre asas mide
# 265 px y el brazalete 266: entra clavado.
SOLAPE = 80

def hay(rel):
    return os.path.exists(os.path.join(RAIZ, rel.lstrip('/')))


def ancho_webp(rel):
    """El ancho de la foto, leído de su cabecera. Lo necesita el `srcset`:
    si el navegador no sabe cuántos píxeles trae cada archivo, no puede
    elegir bien —y los lienzos no miden todos lo mismo desde que las fotos
    no se amplían (Óscar, 12/08/2026)."""
    import struct
    with open(os.path.join(RAIZ, rel.lstrip('/')), 'rb') as f_:
        d = f_.read(32)
    if d[:4] != b'RIFF' or d[8:12] != b'WEBP':
        return 0
    if d[12:16] == b'VP8X':
        return 1 + int.from_bytes(d[24:27], 'little')
    if d[12:16] == b'VP8 ':
        return struct.unpack('<H', d[26:28])[0] & 0x3fff
    if d[12:16] == b'VP8L':
        return 1 + (int.from_bytes(d[21:25], 'little') & 0x3fff)
    return 0


def con_version(rel):
    """La foto viaja con la HUELLA de su contenido detrás: …webp?v=a1b2c3d4.

    Óscar, 11/08/2026: rehice cuatro fotos de piel y él seguía viendo las
    viejas. El CSS y el JS ya llevaban `?v=`, pero las imágenes no, y
    Cloudflare las guarda cuatro horas con el mismo nombre. Ahora, si la
    foto cambia, cambia su dirección y el navegador la pide de nuevo;
    si no cambia, la dirección es la misma y sigue en caché."""
    import hashlib
    ruta = os.path.join(RAIZ, rel.lstrip('/'))
    with open(ruta, 'rb') as f_:
        huella = hashlib.md5(f_.read()).hexdigest()[:8]
    return f'{rel}?v={huella}'


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


def redondea(p):
    """Al 9,90 más cercano. El 9,90 de abajo se saca restando ANTES de
    truncar; ver el porqué —y el fallo que provocó— en el JavaScript."""
    bajo = int((p - 9.90) // 10) * 10 + 9.90
    return bajo if (p - bajo) <= (bajo + 10 - p) else bajo + 10


# ------------------------------------------------------------
# EL SUELO DEL PRECIO
#
# Copia exacta de lo que hace el configurador —está explicado allí, en
# assets/js/configurador-v2.js—. Tiene que estar aquí porque el «desde»
# de la colección sale de esta cuenta, y si las dos no coincidieran la
# colección anunciaría un precio que la ficha no da.
#
# Óscar, 10/08/2026: los costes de la hoja son BASE IMPONIBLE; el
# embalaje y el envío, los 9 €, llevan el IVA dentro.
# ------------------------------------------------------------
EMBALAJE, ENVIO = 2.00, 7.00          # con IVA dentro
G_TASA, G_PORTES, G_PIEZAS = 0.05, 14.00, 5.00
IVA, IRPF, SS = 0.21, 0.20, 0.05
MIN_EUROS, MIN_PORCENTAJE = 50, 0.15


def coste_neto(c, mov):
    garantia = (mov['coste'] + G_PORTES + G_PIEZAS) * G_TASA
    return c + (EMBALAJE + ENVIO) / (1 + IVA) + garantia


def sube990(p):
    bajo = int((p - 9.90) // 10) * 10 + 9.90
    return bajo if bajo >= p - 1e-9 else bajo + 10


def suelo_pvp(cn):
    queda = 1 - IRPF - SS
    por_euros = (MIN_EUROS / queda + cn) * (1 + IVA)
    margen = queda / (1 + IVA) - MIN_PORCENTAJE
    por_ciento = queda * cn / margen if margen > 0 else 0
    return sube990(max(por_euros, por_ciento))


def base_de(mov, c):
    return max(redondea(c * MULT), suelo_pvp(coste_neto(c, mov)))


def pvp_de(mov, c, recargo=0, c_gemela=None):
    """El recargo NO es una suma a secas sino una diferencia mínima con la
    caja gemela: Óscar quiere la de 39 mm diez euros por encima de la de
    36 (13/08/2026), y como el titanio de 39 cuesta menos de fabricar,
    sumar diez a su precio lo dejaba empatado. Ver el JavaScript."""
    base = base_de(mov, c)
    if not recargo:
        return base
    return max(base, (base_de(mov, c_gemela) if c_gemela is not None else base) + recargo)


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


def eje_fichas(clave, rotulo, opciones, etiqueta, hook=''):
    botones = '\n'.join(
        f'        <button class="cf-ficha" type="button" data-{clave}="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{etiqueta(o)}</button>'
        for i, o in enumerate(opciones))
    return f'''    <div class="cf-grupo"{hook}>
      <p class="cf-rotulo">{rotulo} <b>{len(opciones)} opciones</b></p>
      <div class="cf-fichas" role="group" aria-label="Elegir {rotulo.lower()}">
{botones}
      </div>
    </div>'''


def caja_por_mov():
    """La caja depende del movimiento. En el Precisa el cuarzo va en caja
    sólida —en un cuarzo no hay nada que enseñar por detrás— y el
    automático puede elegir entre dos.

    Van los dos envases en la página y el JavaScript enseña el que toca,
    porque esto cambia al cambiar de mecanismo: si el movimiento trae una
    sola caja se pinta el dato, y si trae varias, sus fichas."""
    return '''    <div class="cf-grupo">
      <p class="cf-rotulo">Caja <b data-caja-cuenta>la que pide el movimiento</b></p>
      <div class="cf-fijo" data-caja-uno><b data-caja-fijo></b></div>
      <div class="cf-fichas" data-cajas role="group" aria-label="Elegir caja" hidden></div>
      <p class="cf-caja-apunte" data-caja-apunte hidden></p>
    </div>'''


def brazalete_fijo(nombre, apunte):
    """Un solo brazalete y un solo acabado: el del pack. No se pregunta,
    pero los ganchos del acabado tienen que existir igual —el JavaScript
    los escribe siempre— así que van en un grupo escondido."""
    return f'''    <div class="cf-grupo">
      <p class="cf-rotulo">Brazalete <b>uno solo</b></p>
      <div class="cf-fijo"><b>{nombre}</b><span>{apunte}</span></div>
      <p class="cf-detalle" data-detalle hidden></p>
    </div>

    <div class="cf-grupo" data-grupo-var hidden>
      <p class="cf-rotulo"><span data-rotulo-var>Versión</span> <b data-cuenta-var></b></p>
      <div class="cf-variantes" data-variantes role="group" aria-label="Elegir versión"></div>
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
      <p class="cf-rotulo"><span data-rotulo-var>Versión</span> <b data-cuenta-var></b></p>
      <div class="cf-variantes" data-variantes role="group" aria-label="Elegir versión"></div>
    </div>'''


def eje_brazalete_mat():
    """El brazalete en tres pasos y SIN cuadrículas de imagen: material,
    cierre y color (Óscar, 10/08/2026). Solo se enseña lo que existe para
    este modelo: los botones los escribe el JavaScript a partir de las
    anotaciones `mat`/`cier`/`eti` de piezas.json, así que una opción que
    no está en los datos no puede aparecer. Cierre y color desaparecen
    enteros cuando solo hay uno: no se pregunta lo que no se elige."""
    return '''    <div class="cf-grupo">
      <p class="cf-rotulo">Brazalete <b data-cuenta-mat></b></p>
      <div class="cf-fichas" data-mats role="group" aria-label="Elegir material del brazalete"></div>
    </div>

    <div class="cf-grupo" data-grupo-esl>
      <p class="cf-rotulo">Eslabones <b data-cuenta-esl></b></p>
      <div class="cf-fichas" data-esls role="group" aria-label="Elegir eslabones"></div>
    </div>

    <div class="cf-grupo" data-grupo-var>
      <p class="cf-rotulo">Color <b data-cuenta-var></b></p>
      <div class="cf-variantes" data-variantes role="group" aria-label="Elegir color"></div>
    </div>

    <div class="cf-grupo" data-grupo-cier>
      <p class="cf-rotulo">Cierre <b data-cuenta-cier></b></p>
      <div class="cf-fichas" data-ciers role="group" aria-label="Elegir cierre"></div>
    </div>'''


def vale_esf(e_, c):
    cj = (e_.get('cajas') or '').strip()
    return (not cj) or cj.lower().startswith('todas') or \
        c['ref'] in [s.strip() for s in cj.split(',')]


def validas(d):
    """El coste de cada configuración que EXISTE DE VERDAD. No es el
    producto de los cuatro ejes: al movimiento puede venirle impuesta la
    caja —el Precisa—, una esfera puede no entrar en una caja, puede no
    haber esfera que elegir porque viene en el pack, y el brazalete tiene
    que hacer juego con la caja —el Bitácora—.

    Contar a ciegas daba números inflados: el Lunar decía 330 y son 220.
    Y el «desde» salía de sumar los mínimos de cada eje por separado, que
    a veces no se pueden dar a la vez."""
    ej = d.get('ejes', {})
    por_mov = (ej.get('caja') or {}).get('porMov') or {}
    compat = (ej.get('brz') or {}).get('compat') or {}
    compat_no = (ej.get('brz') or {}).get('compatNo') or {}
    vetos = set(ej.get('veto') or [])
    por_ref = {c['ref']: c for c in d['caj']}
    # El brazalete del Diver es un EXTRA sobre lo que ya trae la caja.
    extra = bool(d['incluido']) and d['extra']
    for m in d['mov']:
        pm = por_mov.get(m['ref'])
        refs_mov = (pm.get('refs') or [pm['ref']]) if pm else None
        cajas = ([c for c in d['caj'] if c['ref'] in refs_mov]
                 if refs_mov else d['caj'])
        for c in cajas:
            esfs = [x for x in d['esf'] if vale_esf(x, c)] or [None]
            ok = compat.get(c['ref'])
            no = compat_no.get(c['ref']) or []
            brzs = [v for f in d['brz'] for v in f['v']
                    if (ok is None or v['ref'] in ok) and v['ref'] not in no] \
                or [{'c': 0}]
            for x in esfs:
                for v in brzs:
                    # El veto fino: los tres a la vez, o esfera y brazalete
                    # para todas las cajas (ver el JavaScript)
                    if x and vetos and (
                            f"{c['ref']}-{x['ref']}-{v.get('ref','')}" in vetos
                            or f"{x['ref']}-{v.get('ref','')}" in vetos):
                        continue
                    resto = (m['coste'] + (x['coste'] if x else 0)
                             + (0 if extra else v['c']))
                    gem = por_ref.get(c.get('sobre'))
                    yield (m, resto + c['coste'], c.get('recargo', 0),
                           resto + gem['coste'] if gem else None)


BOTON_FICHA_HTML = ('<button class="cf-ficha-boton" type="button" data-abre-ficha>'
                    'Ver la ficha completa</button>')


def manto_html(d):
    """El diálogo de la ficha técnica. Sigue aquí entero, sin usar, para
    el día que se monte en laOrateca."""
    return f"""<div class="cf-manto" data-manto hidden>
  <div class="cf-tec" role="dialog" aria-modal="true" aria-labelledby="cf-tec-t">
    <header class="cf-tec-cab">
      <div>
        <p class="cf-tec-eyebrow">{d['codigo']} · FICHA TÉCNICA</p>
        <h2 id="cf-tec-t">Todo el {d['nombre']}.<br><em>Dato a dato.</em></h2>
      </div>
      <p class="cf-tec-ref"><span>Referencia</span><strong data-tec-ref>—</strong></p>
      <button class="cf-tec-x" type="button" data-cierra-tec aria-label="Cerrar la ficha">×</button>
    </header>
    <div class="cf-tec-cuerpo" data-tec-cuerpo></div>
    <footer class="cf-tec-pie">
      <p data-tec-pie></p>
      <button class="cf-ficha-boton" type="button" data-cierra-tec>Cerrar</button>
    </footer>
  </div>
</div>"""


def piezas_ficha(d):
    """El botón y el diálogo de la ficha técnica, o nada si está apagada."""
    if not FICHA_TECNICA:
        return ('<!-- La ficha técnica se fue a laOrateca (Óscar, 13/08/2026): '
                'el botón y el diálogo no se escriben. FICHA_TECNICA = True los devuelve. -->',
                '')
    return BOTON_FICHA_HTML, manto_html(d)


def pantalla(slug):
    d = PIEZAS[slug]
    mov, caj, esf, brz = d['mov'], d['caj'], d['esf'], d['brz']
    BOTON_FICHA, MANTO_FICHA = piezas_ficha(d)

    # El «desde» es el PRECIO más bajo que se puede pagar, no el coste
    # más bajo: desde que hay suelo, la configuración más barata de
    # fabricar no siempre es la más barata de comprar.
    precios = [pvp_de(m, c, r, g) for m, c, r, g in validas(d)]
    barato, combis = min(precios), len(precios)

    ej = d.get('ejes', {})
    ejes = []

    tm = (ej.get('mov') or {}).get('tarjetas', {})
    if len(mov) == 1:
        # La casilla y la ficha de características no tienen por qué decir lo
        # mismo (Óscar, 12/08/2026): si el movimiento trae un `apunte` propio,
        # manda ese —y si viene vacío, la casilla enseña solo su título—.
        ejes.append(fijo('Movimiento', mov[0]['rot'],
                         mov[0].get('apunte', mov[0]['cal'])))
    else:
        ejes.append(eje_tarjetas('mov', 'Movimiento', (ej.get('mov') or {}).get('pregunta'), mov,
                                 lambda o: tm.get(o['ref'], o['rot'])))

    sub = (ej.get('caja') or {}).get('sub')
    if sub:
        for s_ in sub:
            ejes.append(eje_sub(s_['clave'], s_['rotulo'], s_['valores'], s_.get('etiqueta', {})))
    elif (ej.get('caja') or {}).get('porMov'):
        ejes.append(caja_por_mov())
    elif len(caj) == 1:
        # NUNCA el coste: es lo que nos cuesta a nosotros, no lo que paga
        # el cliente (Óscar, 08/08/2026). El Diver es el primero que llega
        # aquí, con una sola caja, y estuvo a punto de publicar los 69,57.
        ejes.append(fijo('Caja', caj[0]['nombre'],
                         (ej.get('caja') or {}).get('apunte', 'con su esfera y sus agujas')))
    else:
        ejes.append(eje_fichas('caja', 'Caja', caj, lambda o: o['nombre']))

    ge = (ej.get('esf') or {})
    if ge.get('auto'):
        # La esfera no se elige: la manda el bisel (Óscar, 10/08/2026).
        # Ni botón ni dato suelto: ya sale en las características.
        pass
    elif len(esf) > 1 and ge.get('grupos'):
        ejes.append(eje_grupos('esf', 'Esfera', ge['grupos'], esf, ge.get('nombres', {})))
    elif len(esf) > 1:
        # `data-grupo-esf` porque puede desaparecer entero: en el Precisa
        # automático la esfera viene en el pack y no hay nada que elegir.
        ejes.append(eje_fichas('esf', 'Esfera', esf, lambda o: o['nombre'],
                               hook=' data-grupo-esf'))
    elif len(esf) == 1:
        ejes.append(fijo('Esfera', esf[0]['nombre'], 'con sus agujas'))

    # LAS CARACTERÍSTICAS SE VAN AL VISOR (Óscar, 13/08/2026)
    # ------------------------------------------------------------
    # Estuvieron en una segunda columna del panel desde el 10/08, y esa
    # columna le comía la mitad del ancho a las elecciones —el Trinchera
    # tiene catorce cajas y cincuenta y cinco correas—. Ahora el panel es
    # de una sola columna y las características van dentro de la foto,
    # arriba a la izquierda, donde hay sitio de sobra y no estorban.
    # El `<dl data-specs>` que las rellena está ahora en la sección del
    # visor; aquí solo queda no partir la pantalla en dos.
    if len(brz) == 1 and len(brz[0]['v']) == 1:
        ejes.append(brazalete_fijo((ej.get('brz') or {}).get('nombres', {}).get(brz[0]['id'], brz[0]['nombre']),
                                   (ej.get('brz') or {}).get('apunte', 'en el pack de la caja')))
    elif all(f.get('mat') for f in brz):
        ejes.append(eje_brazalete_mat())
    else:
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
    # El archivo se llama como la referencia de pedido, salvo cuando no
    # hay referencia: el brazalete del Precisa viene con la caja y no se
    # pide aparte, pero hay que fotografiarlo. Para esos, `foto`.
    brazaletes = {}
    for f_ in brz:
        for v in f_['v']:
            nom = v.get('foto') or v['ref']
            rel = f'{PIEZAS_IMG}/brazaletes/{nom}.webp'
            if nom and hay(rel):
                brazaletes[nom] = rel

    # EL DETALLE DEL CIERRE
    # ------------------------------------------------------------
    # Una foto por familia de brazalete, en cierres/FAMILIA.webp. Al
    # elegir el cierre, la web la ensena como tarjeta sobre el visor
    # (Oscar, 10/08/2026). Solo viaja la que existe en disco.
    # La tarjeta no siempre enseña un cierre: en la malla gruesa del Cero
    # Cero enseña el GROSOR, porque las dos mallas llevan la misma hebilla
    # y lo que cambia son los 2,8 mm (Óscar, 12/08/2026). Por eso la
    # familia puede traer su propio pie y decir lo que de verdad se ve.
    cierres = {}
    detalle_pies = {}
    for f_ in brz:
        rel = f'{PIEZAS_IMG}/cierres/{f_["id"]}.webp'
        if hay(rel):
            cierres[f_['id']] = con_version(rel)
            if f_.get('detallePie'):
                detalle_pies[f_['id']] = f_['detallePie']

    # Y una foto por NOMBRE de hebilla (Oscar, 11/08/2026): las pieles
    # comparten hebillas entre correas, asi que la foto se busca por el
    # nombre del cierre —«Hebilla clasica plateada» → cierres/hebilla-
    # clasica-plateada.webp— y vale para todas las que la lleven. La de
    # familia, si existe, manda.
    def slug_cierre(nombre):
        import unicodedata
        s = unicodedata.normalize('NFD', nombre)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        return s.lower().replace(' ', '-')

    # Y la más fina de todas: FAMILIA + CIERRE, en cierres/B15-hebilla-
    # clasica-plateada.webp (Óscar, 13/08/2026). El nato lleva las mismas
    # hebillas que la piel pero la foto enseña la correa entera, así que
    # no puede ser la misma tarjeta. Esta manda sobre las otras dos.
    cierres_fam = {}
    for f_ in brz:
        for v_ in f_['v']:
            nom = v_.get('cier') or ''
            clave = f'{f_["id"]}|{nom}'
            if not nom or clave in cierres_fam:
                continue
            rel = f'{PIEZAS_IMG}/cierres/{f_["id"]}-{slug_cierre(nom)}.webp'
            if hay(rel):
                cierres_fam[clave] = con_version(rel)

    cierres_nom = {}
    for f_ in brz:
        for v_ in f_['v']:
            nom = v_.get('cier') or ''
            if not nom or nom in cierres_nom:
                continue
            rel = f'{PIEZAS_IMG}/cierres/{slug_cierre(nom)}.webp'
            if hay(rel):
                cierres_nom[nom] = con_version(rel)

    # LA FOTO ENTERA, UNA POR CONFIGURACION
    # ------------------------------------------------------------
    # Oscar, 10/08/2026: se acabo el montaje de dos capas. Cuando existe
    # la foto del reloj YA MONTADO se usa esa y no se compone nada, que
    # es lo que quita la junta. El nombre encadena caja, esfera y
    # brazalete: LO-03-C1-E1-Brz-316-A05.webp
    #
    # Conviven las dos cosas a proposito: mientras no esten las 240, la
    # configuracion que tenga su foto entera la usa y el resto sigue con
    # lo que haya. Asi cada tanda que llega se ve el mismo dia.
    # Tambien la CAJA puede tomar prestada la foto de otra: en el Precisa
    # el cuarzo y el automatico se ven exactamente igual por delante —solo
    # cambia el fondo, que no sale en la foto— y seria absurdo guardar dos
    # veces el mismo archivo (Oscar, 12/08/2026). La suya manda; la
    # prestada solo entra si la suya no esta.
    completas = {}
    peques = {}          # la copia de 1200 px, para el móvil
    for c in caj:
        for e_ in (esf or [None]):
            suf = f'-{e_["ref"]}' if e_ else ''
            for f_ in brz:
                for v in f_['v']:
                    # La configuracion SIEMPRE se guarda con su propia
                    # referencia —es como la busca el visor—; lo que se
                    # presta es el archivo. Primero la foto propia y solo
                    # si no esta, la de la gemela: la malla de 2,8 mm del
                    # Cero Cero se ve igual que la de 2,3 (Oscar,
                    # 12/08/2026), y las pieles que solo cambian de
                    # hebilla comparten foto porque la hebilla no sale.
                    clave = f'{d["codigo"]}-{c["ref"]}{suf}-{v["ref"]}'
                    puesta = False
                    for nom in (v['ref'], v.get('foto') or v['ref']):
                        for refc in (c['ref'], c.get('foto') or c['ref']):
                            arch = f'{d["codigo"]}-{refc}{suf}-{nom}.webp'
                            rel = f'{PIEZAS_IMG}/completas/{arch}'
                            if hay(rel):
                                completas[clave] = con_version(rel)
                                # La copia ligera para el móvil, si existe
                                chico = f'{PIEZAS_IMG}/completas/1200/{arch}'
                                if hay(chico):
                                    peques[clave] = [con_version(chico), ancho_webp(rel)]
                                puesta = True
                                break
                        if puesta:
                            break

    # Las claves que empiezan por _ son notas de casa —por qué una pieza
    # está fuera, qué hay que revisar—: se quedan en el JSON y NO viajan
    # a la página, que la lee cualquiera con el botón derecho.
    d = {k: v for k, v in d.items() if not k.startswith('_')}

    datos = json.dumps({**d, 'mult': MULT, 'cabezas': cabezas,
                        'brazaletes': brazaletes, 'completas': completas, 'peques': peques, 'cierres': cierres,
                        'cierresNom': cierres_nom, 'cierresFam': cierres_fam,
                        'detallePies': detalle_pies,
                        'solape': SOLAPE},
                       ensure_ascii=False).replace('<', chr(92) + 'u003c')

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Configura tu {d['nombre']} · laOra</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/configurador-v2.css?v={V_CSS}">
</head>
<body>

<header class="cf-cab">
  <a class="cf-marca" href="/coleccion.html" aria-label="Volver a la colección de laOra">
    <img src="{LOGO}" alt="laOra"><b>{d['nombre']}</b>
  </a>
  {BOTON_FICHA}
</header>

<div class="cf-cuerpo">

  <section class="cf-visor" aria-label="El reloj que estás configurando">
    <!-- Lo que llevas elegido, dentro de la foto y a la izquierda del
         todo (Óscar, 13/08/2026). Sin rótulo: cada línea se explica
         sola, y un «Características» encima solo quitaría sitio. -->
    <dl class="cf-specs" data-specs aria-label="Lo que llevas elegido"></dl>

    <div class="cf-montaje" data-montaje>
      <img class="cf-brz arriba" data-brz-img hidden alt="" aria-hidden="true">
      <img class="cf-brz abajo"  data-brz-img hidden alt="" aria-hidden="true">
      <div class="cf-correa arriba" data-correa aria-hidden="true"></div>
      <div class="cf-cabeza" data-cabeza>
        <img data-foto alt="{d['nombre']} de laOra" hidden>
        <p class="cf-pendiente" data-pendiente hidden>Foto pendiente</p>
      </div>
      <div class="cf-correa abajo" data-correa aria-hidden="true"></div>
    </div>

    <!-- La tarjeta del cierre cuelga del VISOR, no de la cabeza ni del
         montaje: la cabeza mide cero en modo «foto pendiente» y el
         montaje es un pasillo estrecho; el visor siempre tiene cuerpo
         y la esquina es suya. -->
    <figure class="cf-cierre-detalle" data-cierre-detalle hidden>
      <img data-cierre-img alt="Detalle del cierre">
      <figcaption data-cierre-pie></figcaption>
    </figure>

    <aside class="cf-cuentas" data-cuentas hidden aria-label="Cuenta de explotación"></aside>

    <!-- El aviso de «el brazalete va dibujado» se retira de la pantalla
         (Óscar, 13/08/2026: «comentarios solo a mí, no en pantalla»). Era
         una nota de taller: el cliente no tiene por qué enterarse de cómo
         montamos la foto. El JavaScript que lo encendía sigue ahí y no
         estorba —comprueba que exista—, así que para recuperarlo basta
         con devolver este párrafo. -->

    <!-- Óscar, 12/08/2026: que nadie compre creyendo que la imagen es una
         fotografía del reloj terminado. Va en todas, siempre, chiquita y
         en la esquina, sin tapar el reloj. -->
    <p class="cf-aviso-imagen">La imagen puede contener errores de diseño*</p>
  </section>

  <section class="cf-panel" aria-label="Opciones del {d['nombre']}">
{chr(10).join(ejes)}
  </section>
</div>

<footer class="cf-barra">
  <div class="cf-barra-izq"><b data-barra-nombre></b><span data-barra-var></span></div>
  <p class="cf-precio"><b data-precio></b><span>Impuestos incluidos</span></p>
  <button class="cf-reservar" type="button" data-reservar>Reservar</button>
</footer>

{MANTO_FICHA}

<script type="application/json" data-piezas>{datos}</script>
<script src="/assets/js/carrito.js?v=1"></script>
<script src="/assets/js/configurador-v2.js?v={V_JS}"></script>
</body>
</html>
'''
    return html, barato, combis


# El nombre del archivo publicado. Solo el Cero Cero difiere del slug,
# porque su página lleva guion desde el principio y hay enlaces puestos.
ARCHIVO = {'cerocero': 'cero-cero'}

# EL «DESDE» LO CALCULA QUIEN COBRA
# ------------------------------------------------------------
# El listado de la colección anunciaba su propio mínimo, sacado del
# catálogo viejo, y los dos números se separaron: prometía el Precisa
# «desde 229,90 €» cuando su página más barata vale 269,90. Un precio
# anunciado que no se puede conseguir no es una errata, es publicidad
# engañosa. Desde el 10/08/2026 el mínimo se escribe aquí, donde se
# calcula, y la colección lo lee.
desde = {}

# EL TRINCHERA YA NO SE GENERA (Óscar, 15/08/2026): su página es la ficha
# de producto nueva, escrita A MANO sobre el catálogo DetalleTrinchera del
# sheet (196 referencias). Si este bucle la escribiera, la pisaría.
NO_GENERAR = {'trinchera', 'precisa', 'bitacora'}

for slug in PIEZAS:
    if slug in NO_GENERAR:
        continue
    html, barato, combis = pantalla(slug)
    nombre = ARCHIVO.get(slug, slug) + '.html'
    with open(os.path.join(RAIZ, nombre), 'w', encoding='utf-8') as f:
        f.write(html)
    desde[nombre[:-5]] = barato
    print(f'{nombre} · {combis} configuraciones'
          f' · desde {euros(desde[nombre[:-5]])}')

# El Trinchera no pasa por el bucle pero su «desde» sigue siendo real:
# cuarzo + caja de acero + esfera khaki + nato + logo, por el motor.
# (El nato+piel cuesta menos pero SE VENDE a nato+10 —Óscar, 16/08—,
# así que el mínimo del catálogo vuelve a ser el nato normal.)
desde['trinchera'] = redondea((15.05 + 23 + 17.29 + 5.69 + 3.78) * MULT)

# El Precisa tampoco: cuarzo + caja sólida integrada + esfera + logo.
desde['precisa'] = redondea((15.05 + 62.99 + 10.39 + 3.78) * MULT)

# Ni el Bitácora (ficha a mano del 16/08): automático + caja plata +
# esfera + silicona, con el coste SIN logo de su configurador de siempre.
desde['bitacora'] = redondea((59.01 + 29.57 + 21.39 + 6.39) * MULT)

with open(os.path.join(RAIZ, 'assets/datos/desde.json'), 'w', encoding='utf-8') as f:
    json.dump(desde, f, ensure_ascii=False, indent=1, sort_keys=True)
print('assets/datos/desde.json escrito')
