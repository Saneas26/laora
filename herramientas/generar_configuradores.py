#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LA PANTALLA DE COMPRAR, UNA POR MODELO
============================================================
Escribe `/lunar`, `/cero-cero`, `/precisa`, `/trinchera` y `/bitacora`.
Las cinco son la MISMA pantalla: la que Óscar dio por buena el
05/08/2026 como `lunarv2c`. Lo único que cambia de una a otra son los
datos, y todos salen de `assets/datos/catalogo.json`.

QUÉ ES ESTA PANTALLA
------------------------------------------------------------
No es una landing. La landing es una sola —la portada— y habla de la
empresa y de lo que se siente al comprar un reloj nuestro. Esto es lo
que viene después: elegir acabado y correa, ver el precio y reservar.
Óscar lo pidió así el 06/08/2026:

    «yo solo quiero montar laora.es/lunar, laora.es/bitacora,
     laora.es/precisa... y que sean exactamente igual que el
     laora.es/lunarv2c, no quiero montar una landing para cada uno.»

De ahí las tres reglas que hereda de `lunarv2c`:

  1. El reloj no se mueve nunca. Cambiar de opción solo cambia la foto
     y las cifras; no se abre nada, no se despliega nada, no hay scroll.
  2. El precio vive en una barra pegada abajo, siempre visible.
  3. La página entera mide una pantalla: `height: 100svh` sin scroll.

NI UN DATO ESCRITO A MANO
------------------------------------------------------------
Precios, acabados, correas, fichas técnicas y REFERENCIAS salen del
catálogo. La referencia se compone aquí, en Python, y viaja ya hecha
dentro del JSON de la página: antes la componía también el JavaScript,
con su propia copia de las reglas, y las dos copias se desviaban (el
segundo Cenit del Precisa salía `C01` donde la hoja dice `C02`).

LAS COMBINACIONES QUE NO EXISTEN
------------------------------------------------------------
La matriz `precios[acabado][correa]` tiene huecos a `null`, y son la
información más importante de la pantalla: el Cenit del Lunar solo se
monta con el brazalete de acero. Esas correas se enseñan APAGADAS, no
escondidas: si desaparecieran, parecería que la opción no existe. Y
apagadas de verdad —`disabled`—, porque con `hidden` el navegador las
seguía dejando pulsar y el precio se quedaba en blanco.

LOS MODELOS SIN CORREA A ELEGIR
------------------------------------------------------------
El Precisa y el Bitácora llevan brazalete integrado: no hay nada que
elegir. En vez de dejar el grupo vacío, se fabrica una única opción con
el texto del brazalete que ya está en `comunes`, y sale marcada. La
pantalla es la misma; lo que cambia es que ahí no hay decisión.

LAS FOTOS
------------------------------------------------------------
`assets/img/catalogo/` tiene una foto por referencia, del paquete
aprobado del 06/08/2026. Se usan así:

  · LUNAR: foto por COMBINACIÓN. Su `README` empareja una a una las
    ocho referencias con las ocho correas, y coincide con el catálogo.
  · EL RESTO: foto por ACABADO. Sus paquetes numeran por caja o por
    movimiento, no por correa —el `A02` del Trinchera es la caja de
    bronce, no la NATO negra—, así que emparejar por número pondría
    una foto que no es la que se está eligiendo. Se sirve la primera
    del acabado, que sí es fiel en color y en caja.

Cuando el paquete de un modelo confirme la correspondencia por correa,
se añade su slug a `FOTO_POR_COMBINACION` y esa pantalla pasa sola a
enseñar la foto exacta.

EL BAUHAUS NO SE PUBLICA
------------------------------------------------------------
Sigue en el catálogo, pero está aparcado desde el 05/08/2026: no se
encuentran ni las cajas ni los movimientos. No se le abre una pantalla
de comprar a un reloj que hoy no se puede montar.

USO
    python3 herramientas/generar_configuradores.py
"""

import glob
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SUBIR EN CADA CAMBIO: Cloudflare sirve el CSS y el JS con max-age=14400.
V_CSS = 27
V_JS = 8

with open(os.path.join(RAIZ, 'assets/datos/catalogo.json'), encoding='utf-8') as f:
    RELOJES = {r['slug']: r for r in json.load(f)['relojes']}

# Los que se publican, en el orden de la colección. El Bauhaus no está
# en la hoja «Catalogo laOra» y se queda fuera: no se le abre pantalla
# de comprar a un reloj cuyo precio no sale de ninguna parte. El DIVER
# (LO-06) sí está en la hoja, con cuatro referencias, pero todavía no
# tiene entrada en `catalogo.json` ni sitio en la colección.
MODELOS = ['lunar', 'cero-cero', 'precisa', 'trinchera', 'diver', 'bitacora',
           'tortuga', 'coctel']

# Modelos verificados a mano cuya referencia compuesta coincide con el
# nombre de su foto. Los volcados de la hoja no hacen falta aquí: su
# referencia YA es la de la hoja, que es como se llaman las fotos.
FOTO_POR_COMBINACION = {'lunar'}

CATALOGO = '/assets/img/catalogo'
LOGO = '/assets/img/lunar-v2/laora-wordmark-dark.png?v=2'   # cabecera clara → logotipo en tinta

FOTOS_EN_DISCO = sorted(
    os.path.basename(p)[:-5]
    for p in glob.glob(os.path.join(RAIZ, 'assets/img/catalogo/*.webp')))

# El paquete de fotos no escribe el modelo siempre igual: la referencia
# del Diver es `LO-06_Diver_A01` y su foto, `LO-06_DIVER_A01`. Se busca
# sin distinguir mayúsculas para que una diferencia de teclado no deje
# un reloj sin su foto.
FOTOS_POR_CLAVE = {n.lower(): n for n in FOTOS_EN_DISCO}


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


def sin_tildes(s):
    """`Bitácora` → `Bitacora`. Las referencias de la hoja y los nombres
    de las fotos van sin tildes; el nombre del reloj, con ellas."""
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


# ============================================================
# LAS MUESTRAS DE CORREA
# ------------------------------------------------------------
# Son el DIBUJO del material, no una foto ni un dato: sirven para ver de
# un vistazo qué se está eligiendo. El texto de cada correa —el que sí es
# información— sale tal cual del catálogo.
# ============================================================
ACERO = 'linear-gradient(150deg,#eef0f1 0%,#b4b8bc 30%,#e6e8ea 52%,#93979c 76%,#cfd2d5 100%)'
NAILON = 'repeating-linear-gradient(90deg,rgba(255,255,255,.06) 0 3px,rgba(0,0,0,.07) 3px 6px)'

MUESTRAS = {
    'brazalete-904l':
        'linear-gradient(150deg,#f2f3f4 0%,#b9bcc0 26%,#eef0f2 46%,#8f9398 70%,#d6d9dc 100%)',
    'brazalete-arroz':
        ('repeating-linear-gradient(135deg,#e9ebed 0 3px,#b7babe 3px 6px),'
         'linear-gradient(150deg,#eceef0,#9da1a6)'),
    'brazalete-acero': ACERO,
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
    # Cero Cero
    'oyster': ACERO,
    'milanesa':
        ('repeating-linear-gradient(60deg,#e4e6e8 0 2px,#adb1b5 2px 4px),'
         'linear-gradient(150deg,#eceef0,#a2a6ab)'),
    'nato':
        (NAILON + ',linear-gradient(150deg,#1d1e1f 0%,#1d1e1f 34%,#c2611d 34%,'
                  '#c2611d 50%,#1d1e1f 50%,#1d1e1f 100%)'),
    # Trinchera
    'verde': NAILON + ',linear-gradient(150deg,#5a6340 0%,#3f4630 55%,#2e331f 100%)',
    'negra': NAILON + ',linear-gradient(150deg,#2c2d2e 0%,#1a1b1c 55%,#0f1010 100%)',
    # la que se fabrica cuando el modelo lleva brazalete integrado
    'incluido': ACERO,
}

# Y para las que llegan de la hoja, que traen el nombre que traigan: la
# muestra se elige por el MATERIAL que dice su nombre. Es un dibujo del
# material, no una foto, así que con acertar el material basta; lo que
# no puede pasar es que salga un cuadrado gris sin significado.
PIEL_AZUL = ('repeating-linear-gradient(90deg,rgba(255,255,255,.05) 0 6px,rgba(0,0,0,.05) 6px 12px),'
             'linear-gradient(155deg,#2f4a6b 0%,#1f3550 55%,#152539 100%)')
NAILON_VERDE = MUESTRAS['verde']

# Se busca por MATERIAL y por COLOR, y en este orden: la primera pareja
# que encaje manda. Sin el color, la NATO verde militar del Trinchera
# salía negra —la muestra decía «nailon» y nada más— y en el botón se
# veía una correa que no era la del reloj.
POR_MATERIAL = [
    (('nailon', 'verde'), NAILON_VERDE), (('nato', 'verde'), NAILON_VERDE),
    (('piel', 'azul'), PIEL_AZUL), (('cuero', 'azul'), PIEL_AZUL),
    (('piel', 'marron'), MUESTRAS['piel-marron']),
    (('piel',), MUESTRAS['piel-negra']), (('cuero',), MUESTRAS['piel-negra']),
    (('milanesa',), MUESTRAS['milanesa']), (('malla',), MUESTRAS['milanesa']),
    (('nailon',), MUESTRAS['negra']), (('nato',), MUESTRAS['negra']),
    (('caucho',), MUESTRAS['caucho']), (('goma',), MUESTRAS['caucho']),
    (('silicona',), MUESTRAS['caucho']),
    (('904',), MUESTRAS['brazalete-904l']),
    (('pvd',), MUESTRAS['brazalete-negro']), (('negr',), MUESTRAS['brazalete-negro']),
    (('bronce',), 'linear-gradient(150deg,#c9a06a 0%,#9a7444 32%,#d8b784 54%,'
                  '#7e5c33 78%,#b58e5c 100%)'),
    (('titanio',), 'linear-gradient(150deg,#dcdcd8 0%,#a9a9a4 30%,#cfcfca 52%,'
                   '#8d8d88 76%,#c2c2bd 100%)'),
    (('acero',), ACERO), (('brazalete',), ACERO),
]


def muestra_de(correa):
    """El dibujo del material de esta correa."""
    if correa['id'] in MUESTRAS:
        return MUESTRAS[correa['id']]
    texto = sin_tildes(f'{correa["nombre"]} {correa.get("detalle", "")}').lower()
    for pistas, fondo in POR_MATERIAL:
        if all(p in texto for p in pistas):
            return fondo
    return '#d8d8d4'


def correas_de(cfg):
    """Las correas que se pueden elegir. Si el modelo lleva brazalete
    integrado, el catálogo no trae ninguna: se fabrica una sola opción
    con el texto que ya está en `comunes`, para que la pantalla siga
    diciendo qué lleva puesto el reloj en vez de callarse."""
    if cfg['correas']:
        return cfg['correas']
    c = cfg.get('comunes', {})
    texto = c.get('Brazalete') or c.get('Correa')
    if not texto:
        return [{'id': 'incluido', 'nombre': 'Brazalete incluido', 'detalle': ''}]
    esCorrea = not c.get('Brazalete')
    return [{'id': 'incluido',
             'nombre': 'Correa incluida' if esCorrea else 'Brazalete incluido',
             'detalle': texto}]


def referencia(reloj, acabado, indice):
    """La referencia de la hoja.

    Si el acabado trae `refs`, son las de la hoja tal cual, casilla por
    casilla: es lo que deja `herramientas/volcar_hoja.py` y no hay nada
    que componer. Solo se compone en los modelos que aún no se han
    volcado, y entonces la regla es la de la hoja de materiales: código
    + modelo sin tildes + inicial del acabado + número + sufijo del
    movimiento.

    El número NO es siempre el de la correa: cuando un modelo tiene dos
    Cenit distintos, la hoja los numera `C01` y `C02` aunque los dos se
    monten con la misma correa. Por eso manda `refNum` del catálogo, que
    puede ser un número suelto o uno por correa."""
    refs = acabado.get('refs')
    if refs is not None:
        # Volcado de la hoja: la casilla vacía se queda vacía. Antes se
        # componía una referencia igualmente y la página se llevaba
        # códigos que no existen —`LO-07_Bitacora_E04`— en las casillas
        # de las combinaciones que no se pueden pedir.
        return refs[indice] if indice < len(refs) and refs[indice] else ''
    codigo = reloj['codigo'].replace('—', '-').replace('–', '-').replace(' ', '')
    modelo = sin_tildes(reloj['nombre']).replace(' ', '')
    letra = acabado.get('refLetra') or acabado['nombre'][0].upper()
    num = acabado.get('refNum')
    if isinstance(num, list):
        num = num[indice] if indice < len(num) else None
    if not num:
        num = '%02d' % (indice + 1)
    return f'{codigo}_{modelo}_{letra}{num}{acabado.get("refSufijo") or ""}'


def foto_de(reloj, acabado, ref):
    """La foto que se sirve para esta combinación.

    Por combinación solo en los modelos cuyo paquete lo confirma; en el
    resto, la primera del acabado. Si no hubiera ninguna del acabado, la
    del modelo: nunca se deja el visor sin foto."""
    slug = reloj['slug']
    # La foto exacta solo cuando la REFERENCIA es de fiar: o la trae la
    # hoja (`refs`, que deja `volcar_hoja.py`) o el modelo está en la
    # lista de los verificados. En el Trinchera, que aún se compone la
    # referencia a mano, `A02` es la NATO negra para la web y la caja de
    # bronce para el paquete de fotos: coincidiría el nombre del archivo
    # y saldría un reloj que no es el que se está eligiendo.
    fiable = bool(acabado.get('refs')) or slug in FOTO_POR_COMBINACION
    exacta = FOTOS_POR_CLAVE.get((ref or '').lower())
    if fiable and exacta:
        return f'{CATALOGO}/{exacta}.webp'
    codigo = reloj['codigo'].replace('—', '-').replace('–', '-').replace(' ', '')
    inicio = f'{codigo}_{sin_tildes(reloj["nombre"]).replace(" ", "")}_' \
             f'{acabado.get("refLetra") or acabado["nombre"][0].upper()}'
    for nombre in FOTOS_EN_DISCO:
        if nombre.lower().startswith(inicio.lower()):
            return f'{CATALOGO}/{nombre}.webp'
    return reloj['foto']


def ficha_corta(cfg, a):
    """Las cuatro líneas del acabado que de verdad cambian de uno a otro.
    Solo se escriben las que ese acabado tiene: lo que no esté confirmado
    en la hoja no se pinta, como en el resto del sitio."""
    filas = [('Movimiento', a.get('movimiento')),
             ('Cristal', a.get('cristal') or cfg['comunes'].get('Cristal')),
             ('Caja', a.get('caja') or a.get('cajaMaterial') or cfg['comunes'].get('Caja')),
             ('Estanqueidad', a.get('estanqueidad') or cfg['comunes'].get('Estanqueidad'))]
    return [[k, v] for k, v in filas if v]


def ficha_completa(reloj, cfg, a):
    """La ficha técnica entera del acabado, en los tres grupos del
    material aprobado. Solo se escribe la línea que tenga dato."""
    c = cfg['comunes']
    grupos = [
        ('01', 'Movimiento', [
            ('MOVIMIENTO', a.get('movimiento')),
            ('TIPO', a.get('movimientoTipo')),
            ('FRECUENCIA', a.get('frecuencia')),
            ('AUTONOMÍA', a.get('autonomia')),
        ]),
        ('02', 'Caja y cristal', [
            ('CRISTAL', a.get('cristal') or c.get('Cristal')),
            ('CAJA', a.get('caja') or a.get('cajaMaterial') or c.get('Caja')),
            # El de la opción manda si lo trae: ver `configurador.js`.
            ('DIÁMETRO', a.get('diametro') or c.get('Diámetro') or reloj.get('diametro')),
            ('ESTANQUEIDAD', a.get('estanqueidad') or c.get('Estanqueidad')),
            ('BISEL', a.get('bisel') or c.get('Bisel')),
            ('GROSOR', c.get('Grosor')),
        ]),
        ('03', 'Esfera y ajuste', [
            ('ESFERA', a.get('esfera') or c.get('Esfera')),
            ('ÍNDICES', c.get('Índices')),
            ('AGUJAS', c.get('Agujas')),
            ('LUMINISCENCIA', c.get('Luminiscencia')),
            ('ANCHO DE ASA', c.get('Ancho de asa')),
            ('AJUSTE', c.get('Ajuste')),
            ('CIERRE', c.get('Cierre')),
            ('FONDO', a.get('fondo') or c.get('Fondo')),
            ('CORONA', c.get('Corona')),
            ('PESO', a.get('peso')),
        ]),
    ]
    return [{'n': n, 'titulo': t, 'filas': [[k, v] for k, v in filas if v]}
            for n, t, filas in grupos]


def escribir(nombre, contenido):
    with open(os.path.join(RAIZ, nombre), 'w', encoding='utf-8') as f:
        f.write(contenido)


# ============================================================
# UNA PANTALLA POR MODELO
# ============================================================
def pantalla(slug):
    reloj = RELOJES[slug]
    cfg = reloj['configurador']
    acabados = cfg['acabados']
    correas = correas_de(cfg)
    precios = cfg['precios']
    nombre = reloj['nombre']

    def precio(idAcabado, i):
        lista = precios.get(idAcabado, [])
        return lista[i] if i < len(lista) and lista[i] is not None else None

    # LA COMBINACIÓN DE PARTIDA: la más barata que se pueda pedir de
    # verdad. Es la cifra que el visitante trae en la cabeza desde la
    # colección, y la pantalla tiene que abrir con ella.
    combinaciones = [(a, i, precio(a['id'], i))
                     for a in acabados for i in range(len(correas))
                     if precio(a['id'], i) is not None]
    if not combinaciones:
        raise SystemExit(f'{slug}: no hay ni una combinación con precio')
    aInicial, cInicial, pInicial = min(combinaciones, key=lambda t: t[2])

    todos = [p for _, _, p in combinaciones]

    # NOMBRES QUE SE REPITEN. El Bitácora tiene tres Eclipse y el Cero
    # Cero, cuatro: lo que los distingue es el movimiento, no el nombre.
    # Sin decirlo, salían botones idénticos —dos al mismo precio— y no
    # había manera de saber cuál se estaba pulsando. Se añade el calibre,
    # que es lo primero de `movimiento`, tal cual está en el catálogo.
    repetidos = {a['nombre'] for a in acabados
                 if sum(1 for b in acabados if b['nombre'] == a['nombre']) > 1}

    def calibre(a):
        """El calibre a secas: «Seiko/TMI NH35A, 11½ líneas, 24 rubíes»
        → «Seiko/TMI NH35A».

        Se corta por la primera coma Y se quitan los paréntesis: cortando
        solo por la coma, «VH31 (TMI Vh31b, cuarzo japonés)» dejaba
        «VH31 (TMI Vh31b», con el paréntesis abierto, en el botón."""
        if a['nombre'] not in repetidos:
            return ''
        m = re.sub(r'\s*\([^)]*\)?', '', a.get('movimiento') or '')
        return m.split(',')[0].strip()

    # Referencias y fotos, ya resueltas: el navegador no compone nada.
    datosAcabados = {}
    for a in acabados:
        # La casilla que no se puede pedir no lleva referencia. En los
        # modelos que aún se componen a mano —el Lunar— se componía
        # igualmente y la página se llevaba códigos que no existen,
        # `LO-01_Lunar_C08`, en las combinaciones apagadas.
        refs = [referencia(reloj, a, i) if precio(a['id'], i) is not None else ''
                for i in range(len(correas))]
        datosAcabados[a['id']] = {
            'nombre': a['nombre'],
            # lo que se lee en el visor, en la barra y en la ficha: con
            # el calibre cuando el nombre no basta para distinguirlo
            'etiqueta': a['nombre'] + (f' {calibre(a)}' if calibre(a) else ''),
            'descriptor': a.get('descriptor', ''),
            'resumen': a.get('resumen', ''),
            'refs': refs,
            'fotos': [foto_de(reloj, a, r) for r in refs],
            'foto': foto_de(reloj, a, refs[0]),
            'ficha': ficha_corta(cfg, a),
            'grupos': ficha_completa(reloj, cfg, a),
        }

    datos = {
        'modelo': nombre,
        'inicial': {'acabado': aInicial['id'], 'correa': cInicial},
        'precios': precios,
        'acabados': datosAcabados,
        # `diametro` solo cuando la opción lo trae: el Trinchera monta
        # el mismo acabado en 39 y en 36 mm, y la ficha técnica tiene
        # que decir el de la caja elegida, no el del acabado.
        'correas': [{'id': c['id'], 'nombre': c['nombre'],
                     'detalle': c.get('detalle', ''),
                     'diametro': c.get('diametro'),
                     'muestra': muestra_de(c)} for c in correas],
    }

    fotoInicial = datosAcabados[aInicial['id']]['fotos'][cInicial]
    correaInicial = correas[cInicial]
    muestraInicial = muestra_de(correaInicial)

    def botonAcabado(a):
        desde = min([p for p in precios.get(a['id'], []) if p is not None] or [0])
        cal = calibre(a)
        return (f'        <button type="button" data-acabado="{a["id"]}" aria-pressed="false">'
                f'<b>{a["nombre"]}</b>{f"<i>{cal}</i>" if cal else ""}'
                f'<small>desde {euros(desde)}</small></button>\n')

    def botonCorrea(i, c):
        return (f'        <button type="button" data-correa="{i}" aria-pressed="false">'
                f'<span class="tira" style="background:{muestra_de(c)}"></span>'
                f'<span>{c["nombre"]}</span></button>\n')

    # El rótulo del grupo de correas: cuando no hay nada que elegir se
    # dice «Incluido», en vez de un «1 opción» que parece un error. El
    # rótulo de la izquierda es siempre el mismo —repetir ahí el nombre
    # del brazalete lo dejaba dicho dos veces seguidas.
    # Cuando lo que se elige es la caja y no la correa, el rótulo lo
    # dice: lo pone el volcado en `rotuloOpciones`.
    rotuloCorreas = cfg.get('rotuloOpciones') or 'Brazalete o correa'
    tituloCorreas = f'<b>{len(correas)} opciones</b>' if len(correas) > 1 else '<b>Incluido</b>'

    # CUANDO NO HAY NADA QUE ELEGIR, NO SE PINTA UN BOTÓN.
    # El Precisa y el Bitácora llevan brazalete integrado: una sola
    # opción. Como botón dentro de la rejilla, esa única muestra se
    # estiraba a todo el ancho del panel y —al ser cuadrada— salía un
    # azulejo de 690 px de alto que echaba el precio fuera de la
    # pantalla. Y además mentía: parecía que había algo que decidir.
    # Aquí se dice lo que lleva puesto, en una línea, y ya está.
    if len(correas) > 1:
        bloqueCorreas = (
            f'      <div class="cfg-correas" role="group" aria-label="Elegir brazalete o correa"'
            f' style="--correas:{min(4, len(correas))}">\n'
            + ''.join(botonCorrea(i, c) for i, c in enumerate(correas))
            + '      </div>')
    else:
        u = correas[0]
        detalle = f'<small>{u["detalle"]}</small>' if u.get('detalle') else ''
        bloqueCorreas = (
            f'      <p class="cfg-correa-unica">'
            f'<span class="tira" style="background:{muestra_de(u)}"></span>'
            f'<span><b>{u["nombre"]}</b>{detalle}</span></p>')

    # LO MISMO PARA EL ACABADO. El Bitácora (09/08/2026, Óscar: «no hay
    # acabados ni nombres de ningún acabado») deja de tener niveles: es
    # un solo modelo con una sola configuración de movimiento, caja,
    # esfera y brazalete. Con un único acabado no se pinta ni el grupo
    # ni el rótulo «Acabado» — igual que arriba con la correa, decir
    # «1 opción» sería mentir: aquí no hay nada que elegir.
    if len(acabados) > 1:
        bloqueAcabados = (
            '    <div class="cfg-grupo">\n'
            f'      <p class="cfg-rotulo">Acabado <b>{len(acabados)} opciones</b></p>\n'
            '      <div class="cfg-acabados" role="group" aria-label="Elegir acabado">\n'
            + ''.join(botonAcabado(a) for a in acabados)
            + '      </div>\n'
            f'      <p class="cfg-nota" data-nota>{aInicial.get("resumen", "")}</p>\n'
            '    </div>')
    else:
        bloqueAcabados = ''

    # Las dos etiquetas que normalmente empiezan por el nombre del
    # acabado —«Alba · 40 mm...»— se quedan solo con la correa cuando
    # no hay acabado que nombrar, en vez de arrastrar un « · » suelto.
    tieneAcabado = bool(aInicial['nombre'])
    altAcabado = f", acabado {aInicial['nombre']}" if tieneAcabado else ''
    viendoHTML = ((f"<b>{aInicial['nombre']}</b> · " if tieneAcabado else '')
                  + correaInicial['nombre'])
    eleccionTexto = ((f"{aInicial['nombre']} · " if tieneAcabado else '')
                     + correaInicial['nombre'])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Configura tu {nombre} de laOra: acabado, brazalete o correa y precio, en una sola pantalla. Desde {euros(min(todos))}.">
<meta name="theme-color" content="#151715">
<title>Configura tu {nombre} · laOra</title>
<link rel="canonical" href="https://laora.es/{slug}">
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400&display=swap" rel="stylesheet">
<!-- GENERADO por herramientas/generar_configuradores.py — no editar a mano. -->
<link rel="stylesheet" href="/assets/css/configurador.css?v={V_CSS}">
</head>
<body class="{' '.join(c for c in (
    'cfg-muchos' if len(acabados) > 6 or len(correas) > 4 else '',
    'cfg-apretado' if len(correas) > 8 else '') if c) or 'cfg-normal'}">

<header class="cfg-cab">
  <!-- El logotipo es el único camino de vuelta que tiene esta pantalla:
       sin él sería un callejón sin salida. No se le añade un menú porque
       aquí solo se hace una cosa, que es elegir el reloj. -->
  <a class="cfg-marca" href="/coleccion.html" aria-label="Volver a la colección de laOra"><img src="{LOGO}" alt="laOra"><b>{nombre}</b></a>
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
         src="{fotoInicial}"
         alt="Reloj laOra {nombre}{altAcabado}, con {correaInicial['nombre'].lower()}"
         fetchpriority="high">
    <div class="cfg-muestra" aria-hidden="true">
      <span class="tira" data-muestra-tira style="background:{muestraInicial}"></span>
      <span data-muestra-nombre>{correaInicial['nombre']}</span>
    </div>
    <!-- Los dos rótulos van JUNTOS y en flujo normal dentro de este
         bloque, no sueltos y colocados cada uno por su cuenta. Cuando
         eran hermanos absolutos, un acabado de nombre largo —«Eclipse
         Seiko NH35A · Brazalete incluido»— pasaba a dos líneas y la
         segunda caía encima de la referencia: dos textos superpuestos,
         ilegibles los dos. Así el segundo siempre baja. -->
    <div class="cfg-rotulos">
      <p class="cfg-viendo" data-viendo aria-live="polite">{viendoHTML}</p>
      <!-- La referencia también aquí: en el teléfono no cabe en la
           cabecera, y es el dato con el que Óscar busca en la hoja. -->
      <p class="cfg-ref-visor">Ref. <span data-ref>—</span></p>
    </div>
  </section>

  <!-- LAS OPCIONES · todas a la vista, sin desplegar nada -->
  <section class="cfg-panel" aria-label="Opciones del {nombre}">

{bloqueAcabados}

    <div class="cfg-grupo">
      <p class="cfg-rotulo">{rotuloCorreas} <b data-rotulo-correa>{tituloCorreas}</b></p>
      <!-- `--correas` es cuántas columnas caben de verdad. La rejilla
           era siempre de cuatro, así que con tres correas quedaba una
           columna vacía y los tres nombres partidos en dos líneas por
           falta de ancho. Ahora la rejilla tiene el ancho de lo que hay. -->
{bloqueCorreas}
    </div>

    <div class="cfg-nota">
      <dl data-ficha></dl>
    </div>

  </section>
</div>

<!-- LA BARRA · pegada abajo, con el precio de lo elegido -->
<footer class="cfg-barra">
  <span class="lado">
    <span class="eleccion" data-eleccion>{eleccionTexto}</span>
    <span class="ref">Ref. <span data-ref>—</span></span>
  </span>
  <span class="cfg-precio">
    <strong data-precio>{euros(pInicial)}</strong>
    <span>Impuestos incluidos</span>
  </span>
  <button class="cfg-reservar" type="button" data-reservar>Reservar</button>
</footer>

<!-- LA FICHA TÉCNICA COMPLETA
     Se monta al pulsar y se tira al cerrar, como el overlay del
     material aprobado: mientras no está abierta, no existe en la
     página. No cambia la dirección ni mueve la pantalla de debajo.

     Los datos NO van escritos: los rellena `configurador.js` con la
     combinación que haya elegida en ese momento. Si fueran fijos, quien
     configurase el Cenit leería la ficha del acabado de partida. -->
<template data-plantilla-ficha>
  <div class="cfg-overlay" role="dialog" aria-modal="true" aria-labelledby="cfg-ficha-titulo">
    <div class="cfg-overlay-caja">
      <header class="cfg-overlay-cab">
        <div>
          <p>{reloj['codigo']} · FICHA TÉCNICA COMPLETA</p>
          <h2 id="cfg-ficha-titulo">Todo el {nombre}.<br><em>Dato a dato.</em></h2>
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

<script type="application/json" data-cfg>{json.dumps(datos, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
<script src="/assets/js/carrito.js?v=1"></script>
<script src="/assets/js/configurador.js?v={V_JS}"></script>
</body>
</html>
"""


for slug in MODELOS:
    escribir(slug + '.html', pantalla(slug))
    reloj = RELOJES[slug]
    cfg = reloj['configurador']
    correas = correas_de(cfg)
    reales = [(a['id'], i) for a in cfg['acabados'] for i in range(len(correas))
              if i < len(cfg['precios'].get(a['id'], []))
              and cfg['precios'][a['id']][i] is not None]
    conFoto = sum(
        1 for a in cfg['acabados'] for i in range(len(correas))
        if (a['id'], i) in reales
        and foto_de(reloj, a, referencia(reloj, a, i)).startswith(CATALOGO))
    print(f'{slug + ".html":16} {len(cfg["acabados"])} acabados · {len(correas)} correas · '
          f'{len(reales)} combinaciones · {conFoto} con foto de catálogo')

print(f'\nfotos disponibles en assets/img/catalogo: {len(FOTOS_EN_DISCO)}')
print('foto por combinación solo en: ' + ', '.join(sorted(FOTO_POR_COMBINACION)))
