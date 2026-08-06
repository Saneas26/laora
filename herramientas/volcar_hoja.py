#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · VOLCAR LA HOJA «Catalogo laOra» AL CATÁLOGO DE LA WEB
============================================================
Óscar, 06/08/2026:

    «la hoja del sheet pasa a ser lo que manda por encima de cualquier
     dato que tengas historico»

Así que este fichero reescribe el bloque `configurador` de
`assets/datos/catalogo.json` a partir de la hoja. Precios, movimientos,
fichas técnicas y referencias salen de ahí y de ningún otro sitio.

ENTRADA
------------------------------------------------------------
`hoja.json`: la hoja «Catalogo laOra» exportada a JSON, una entrada por
fila, con los nombres de columna que usa `COLUMNAS` más abajo. Se saca
del libro 1hOEjyzjzHewt-CThFyJWeIREw6J56Rj5gEmc2w5z0cc, que es el que
Óscar mantiene.

    python3 herramientas/volcar_hoja.py ruta/a/hoja.json

LO QUE NO SALE A LA WEB
------------------------------------------------------------
La hoja es de trabajo y trae cosas que son de casa, no del cliente:
enlaces a proveedores, coste, subtotales, margen, y avisos internos
—«No declarado por el vendedor ⚠», «según ficha del vendedor»,
«Suministrada por laOra (fuera de AliExpress)»—. Nada de eso se copia.
Una celda que solo diga eso se queda a `null`, y una línea a `null` NO
se pinta: no hay «por confirmar» a la vista en ninguna parte.

LO QUE SE RESPETA DE LO QUE YA HABÍA
------------------------------------------------------------
  · EL LUNAR NO SE TOCA. Sus ocho referencias ya coinciden con la hoja
    en precio, movimiento, caja y estanqueidad, y los nombres de sus
    correas los dictó Óscar palabra por palabra.
  · EL TRINCHERA TAMPOCO, y no por estar bien: la hoja se contradice en
    dos celdas suyas y hasta que Óscar las corrija no se puede volcar.
    Está explicado en AUDITORIA_CATALOGO.md.
  · Los textos de `resumen` los escribió el equipo, no salen de la hoja.
    Se conservan SOLO si el calibre de ese acabado no ha cambiado. Si el
    movimiento es otro, la frase que lo describía ya no vale y se cae:
    antes que dejar un texto que miente, se queda sin texto.

CÓMO SE REPARTEN LAS FILAS EN LA PANTALLA
------------------------------------------------------------
La hoja tiene UNA FILA POR PRODUCTO VENDIBLE. La pantalla tiene dos
selectores. El reparto es este:

  · Dos filas del mismo acabado que solo se diferencien en el MOVIMIENTO
    son dos botones de acabado, y se distinguen por el calibre: el Cero
    Cero tiene tres Eclipse, y lo único que cambia es lo de dentro.
  · Dos filas que se diferencien en el EXTERIOR —caja, brazalete o
    correa— son dos opciones del segundo selector.

Las combinaciones que no existen se enseñan apagadas, no escondidas,
que es como lo pidió Óscar el 05/08/2026.
"""

import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGO = os.path.join(RAIZ, 'assets/datos/catalogo.json')

# Modelos que este volcado NO toca, y por qué.
INTACTOS = {
    'lunar': 'ya coincide con la hoja; las correas las nombró Óscar',
    'trinchera': 'la hoja se contradice en A01 y L01 (ver AUDITORIA_CATALOGO.md)',
}

# El Bauhaus no está en la hoja: se le quita el configurador para que no
# siga publicando dos precios que no salen de ninguna parte.
SIN_DATOS = {'bauhaus'}

CODIGO_SLUG = {
    'LO-01': 'lunar', 'LO-02': 'cero-cero', 'LO-04': 'precisa',
    'LO-05': 'trinchera', 'LO-06': 'diver', 'LO-07': 'bitacora',
    'LO-08': 'tortuga', 'LO-09': 'coctel',
}

ORDEN_ACABADO = {'Alba': 0, 'Levante': 1, 'Cenit': 2, 'Eclipse': 3}


# ============================================================
# LIMPIAR LO QUE ES DE CASA
# ============================================================
# Lo que va DENTRO de un paréntesis y es de casa: se tira el paréntesis
# entero, no un trozo. Quitando solo la frase quedaban muñones —«C3
# verde (» — que además se publicaban.
PARENTESIS_INTERNO = re.compile(
    r'\s*\([^)]*\b('
    r'ficha del (vendedor|proveedor|fabricante)'
    r'|declarado por el vendedor|grado no declarado|no declarad[oa]'
    r'|incl(uido|\.)?\s+en|caja NH-style|asiento|ajuste directo'
    r'|requiere anillo|variante|esfera laOra|vestir'
    r')[^)]*\)', re.I)

# Y lo que es de casa sin paréntesis que lo tape.
BASURA = re.compile(
    r'\s*(⚠.*$'
    r'|;?\s*índices según esfera laOra.*$'
    r'|,?\s*según (la )?ficha del (vendedor|fabricante|proveedor).*$'
    r'|,?\s*declarado por el vendedor'
    r')', re.I)

# MARCAS DE OTRAS CASAS. La hoja describe las cajas por el reloj al que
# se parecen —«tonneau estilo PRX», «textura Grenade (estilo Aquanaut)»—
# porque así es como se piden al proveedor. En la web no se nombra a otra
# marca ni se dice a qué se parece: eso es lo que separa un homenaje de
# una copia. Se quita el paréntesis entero o la coletilla.
AJENAS = (r'PRX|Aquanaut|Nautilus|Speedmaster|Seamaster|Submariner|Moonwatch'
          r'|Rolex|Omega|Patek|Tissot|SKX|62MAS|6105|6309|Grenade|Daytona'
          r'|Goutent|MATELION')
MARCA_AJENA = re.compile(
    r'\s*(\([^)]*(' + AJENAS + r')[^)]*\)'
    r'|,?\s*(estilo|tipo)\s+(' + AJENAS + r')\b[^,;)]*'
    r'|\b(' + AJENAS + r')\b)', re.I)

# «(especificación laOra)», «(según lote)»: de dónde sale el dato es
# cosa nuestra, no del cliente.
PROCEDENCIA = re.compile(r'\s*\([^)]*\b(especificación laOra|según lote)[^)]*\)', re.I)

# Filas que la hoja marca como no cerradas. No se publican: un reloj
# cuyo movimiento está «por confirmar» no se puede poner a la venta.
PENDIENTE = re.compile(r'por confirmar|pendiente', re.I)

VACIO = re.compile(
    r'^\s*(no declarad[oa][^.]*'
    r'|textura'          # lo que quedaba de «Textura Grenade (estilo …)»
    r'|n/?a'
    r'|suministrad[oa]s? por laOra.*'
    r'|según esfera laOra.*'
    r'|esfera suministrada por laOra.*'
    r')\s*$', re.I)


def limpiar(v):
    """Deja el dato tal cual lo puede leer un cliente, o `None`.

    `None` significa que esa línea NO se pinta. Es a propósito: la hoja
    marca con ⚠ y con «no declarado» lo que el proveedor no confirma, y
    eso no se publica ni como dato ni como «por confirmar»."""
    if v is None:
        return None
    s = str(v).strip()
    if not s or VACIO.match(s):
        return None
    s = PARENTESIS_INTERNO.sub('', s)
    s = PROCEDENCIA.sub('', s)
    s = MARCA_AJENA.sub('', s)
    s = BASURA.sub('', s)
    s = re.sub(r'\s*\([^)]*$', '', s)          # paréntesis que se quedó sin cerrar
    s = re.sub(r'\s*\(\s*\)', '', s)
    if re.fullmatch(r'[A-Z]{1,3}\s?\d{1,4}', s.strip()):
        return None                            # «BK25», «G30»: código de proveedor
    s = re.sub(r'\s{2,}', ' ', s).strip(' ;,·-')
    if not s or VACIO.match(s):
        return None
    return s


def sin_tildes(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def ident(s):
    s = sin_tildes(s).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


# ============================================================
# EL SEGUNDO SELECTOR
# ------------------------------------------------------------
# Qué distingue a dos referencias del mismo acabado por fuera. Se mira
# el conjunto que se compra, la correa y las señas de la caja: si dos
# filas coinciden en todo esto, para el cliente son el mismo reloj por
# fuera y no se le enseñan dos veces.
# ============================================================
CLAVE_EXTERIOR = ('correa', 'cajaMat', 'diametro', 'cajaAcab',
                  'brazMat', 'brazAcab', 'brazCierre')


def clave_exterior(f):
    """Dos filas son el mismo reloj POR FUERA si coinciden en esto.

    Se compara con los valores ya limpios, y sin la columna
    «Caja/conjunto»: esa es la de compras —dice qué se le pide al
    proveedor y con qué anillo se monta—, y dos filas idénticas para el
    cliente traen ahí textos distintos. Comparándola salían opciones
    duplicadas: el Precisa daba tres cuando solo tiene una."""
    return tuple(limpiar(f.get(c)) or '' for c in CLAVE_EXTERIOR)


def titulo_exterior(fila):
    """El rótulo del botón: lo que lleva puesto, en cristiano.

    Sale de la columna «Brazalete/correa», que es la que describe lo que
    se ve. Se le quitan los paréntesis de almacén —«(incl. en la caja)»,
    «(20 mm)»— porque el ancho ya va en la ficha técnica."""
    # La hoja copia a veces el título entero del anuncio del proveedor:
    # «Correa de reloj de silicona de 20mm y 22mm para Rolex SUBMARINER,
    # pulsera de buceo resistente al agua para Seiko SKX007…». Se corta
    # en el primer «para» ANTES de limpiar: si se limpiara primero, se
    # irían las marcas y quedaría el esqueleto de la frase pegado.
    crudo = str(fila.get('correa') or '')
    crudo = re.sub(r'\s+para\s+.*$', '', crudo, flags=re.I)
    base = limpiar(crudo) or limpiar(fila.get('brazMat')) or 'Incluido'
    base = re.sub(r'\s*\bde\s+\d+\s*mm\s+y\s+\d+\s*mm', '', base, flags=re.I)
    base = re.sub(r'\s*,?\s*\d+[,.]\d+\s*mm', '', base)   # «1,0 mm» de grosor
    base = re.sub(r'^Correa de reloj\b', 'Correa', base, flags=re.I)
    base = re.sub(r'\s*\(\s*\d+\s*mm\s*\)', '', base)
    base = re.sub(r'\s*,?\s*\d+\s*mm\b', '', base)
    base = re.sub(r'\s*de\s+\d+\s*mm\s+y\s+\d+\s*mm', '', base)
    return re.sub(r'\s{2,}', ' ', base).strip(' ,;·')


def detalle_exterior(fila):
    partes = [limpiar(fila.get('brazAcab')), limpiar(fila.get('brazCierre'))]
    partes = [p for p in partes if p]
    return ' · '.join(partes)


# ============================================================
# LA FICHA DE CADA ACABADO
# ============================================================
def acabado_desde(fila):
    """Las señas técnicas de una fila, con los nombres que usa el
    generador de las pantallas. Solo lo que la hoja confirma."""
    return {k: v for k, v in {
        'movimiento': limpiar(fila.get('calibre')) or limpiar(fila.get('mov')),
        'movimientoTipo': limpiar(fila.get('tipo')),
        'frecuencia': limpiar(fila.get('frecuencia')),
        'autonomia': limpiar(fila.get('reserva')),
        'cajaMaterial': limpiar(fila.get('cajaMat')),
        'diametro': limpiar(fila.get('diametro')),
        'estanqueidad': limpiar(fila.get('wr')),
        'bisel': limpiar(fila.get('biselTipo')),
        'cristal': limpiar(fila.get('cristal')),
        'esfera': limpiar(fila.get('esferaColor')),
        'fondo': limpiar(fila.get('fondo')),
        'peso': limpiar(fila.get('peso')),
    }.items() if v}


COMUNES_POSIBLES = [
    ('Grosor', 'grosor'), ('Índices', 'indices'), ('Luminiscencia', 'lumen'),
    ('Ancho de asa', 'brazAncho'), ('Ajuste', 'brazAjuste'), ('Corona', 'corona'),
]


def comunes_de(filas):
    """Lo que es igual en TODAS las filas del modelo. Lo que varía se
    queda en su acabado; si se subiera aquí, un acabado leería el dato
    de otro."""
    out = {}
    for etiqueta, campo in COMUNES_POSIBLES:
        vals = {limpiar(f.get(campo)) for f in filas}
        if len(vals) == 1:
            v = vals.pop()
            if v:
                out[etiqueta] = v
    return out


# ============================================================
# EL VOLCADO
# ============================================================
def configurador(filas, previo):
    """Construye el `configurador` de un modelo a partir de sus filas."""
    # 1. los botones de acabado: acabado + calibre
    grupos = {}
    for f in filas:
        clave = (f['acabado'], limpiar(f.get('calibre')) or f.get('mov'))
        grupos.setdefault(clave, []).append(f)

    def orden(clave):
        return (ORDEN_ACABADO.get(clave[0], 9), min(x['pvp'] for x in grupos[clave]))

    claves = sorted(grupos, key=orden)

    # 2. el segundo selector: la unión de los exteriores del modelo,
    #    en el orden en que aparecen en la hoja
    exteriores = []
    for f in filas:
        k = clave_exterior(f)
        if k not in exteriores:
            exteriores.append(k)

    def indice(f):
        return exteriores.index(clave_exterior(f))

    # una fila por exterior, para sacar de ella el rótulo
    muestra = {}
    for f in filas:
        muestra.setdefault(indice(f), f)

    # Dos exteriores pueden llevar la MISMA correa y ser relojes
    # distintos: los dos Eclipse de Ronda 515 del Bitácora comparten la
    # goma negra y cambian de caja —negra y oro rosa—. Si el rótulo solo
    # dijera la correa, saldrían dos botones idénticos. Cuando eso pasa,
    # manda la caja.
    titulos = [titulo_exterior(muestra[i]) for i in range(len(exteriores))]
    repes = {t for t in titulos if titulos.count(t) > 1}
    usados = set()
    correas = []
    for i in range(len(exteriores)):
        f = muestra[i]
        t = titulos[i]
        if t in repes:
            caja = limpiar(f.get('cajaAcab')) or limpiar(f.get('cajaMat'))
            if caja:
                # minúscula solo si la palabra no es una sigla: si no,
                # «PVD negro» salía «pVD negro»
                if len(caja) > 1 and caja[1].islower():
                    caja = caja[0].lower() + caja[1:]
                t = f'{t} · caja {caja}'
        ide = ident(t)[:34] or f'opcion-{i + 1}'
        while ide in usados:
            ide += '-2'
        usados.add(ide)
        correas.append({'id': ide, 'nombre': t, 'detalle': detalle_exterior(f)})

    # 3. los precios y las referencias, casilla a casilla
    previoAcabados = {a['id']: a for a in (previo or {}).get('acabados', [])}
    acabados, precios = [], {}
    nombresUsados = set()
    for clave in claves:
        nombre, calibre = clave
        rs = grupos[clave]
        base = ident(nombre)
        ide = base
        if ide in nombresUsados:
            # el trozo del calibre que lo identifica: «NH35A», «9015»,
            # «VH31». Es lo mismo que se enseña en el botón.
            corto = next((w for w in re.findall(r'[A-Za-z]*\d+[A-Za-z]*',
                                                calibre or '') if len(w) >= 3), '')
            ide = base + '-' + (ident(corto) or str(len(nombresUsados)))
        nombresUsados.add(ide)

        a = {'id': ide, 'nombre': nombre}
        a.update(acabado_desde(rs[0]))

        # el `resumen` lo escribió el equipo, no la hoja: se conserva
        # SOLO si el calibre no ha cambiado
        viejo = previoAcabados.get(ide)
        if viejo and viejo.get('resumen') and viejo.get('movimiento') == a.get('movimiento'):
            a['resumen'] = viejo['resumen']
        if viejo and viejo.get('descriptor') and viejo.get('movimiento') == a.get('movimiento'):
            a['descriptor'] = viejo['descriptor']

        fila = [None] * len(correas)
        refs = [None] * len(correas)
        for r in rs:
            fila[indice(r)] = round(r['pvp'], 2)
            refs[indice(r)] = r['ref']
        a['refs'] = refs
        acabados.append(a)
        precios[ide] = fila

    return {'acabados': acabados, 'correas': correas, 'precios': precios,
            'comunes': comunes_de(filas)}


def main(ruta):
    with open(ruta, encoding='utf-8') as f:
        hoja = json.load(f)
    with open(CATALOGO, encoding='utf-8') as f:
        cat = json.load(f)

    porSlug, pendientes = {}, []
    for f in hoja:
        slug = CODIGO_SLUG.get(f['ref'].split('_')[0])
        if not slug:
            continue
        # La hoja marca así lo que todavía no está cerrado. No se
        # publica: un reloj cuyo movimiento está «por confirmar» no se
        # puede poner a la venta.
        if PENDIENTE.search(str(f.get('calibre', '')) + str(f.get('mov', ''))):
            pendientes.append((f['ref'], limpiar(f.get('mov')) or f.get('mov')))
            continue
        porSlug.setdefault(slug, []).append(f)

    relojes = {r['slug']: r for r in cat['relojes']}
    for slug, filas in porSlug.items():
        if slug in INTACTOS:
            print(f'  {slug:11} intacto — {INTACTOS[slug]}')
            continue
        r = relojes.get(slug)
        if r is None:
            print(f'  {slug:11} ⚠ no está en catalogo.json: hay que crearlo a mano')
            continue
        antes = r.get('configurador')
        r['configurador'] = configurador(filas, antes)
        cfg = r['configurador']
        n = sum(1 for l in cfg['precios'].values() for p in l if p is not None)
        ps = [p for l in cfg['precios'].values() for p in l if p is not None]
        print(f'  {slug:11} {len(cfg["acabados"])} acabados · {len(cfg["correas"])} opciones · '
              f'{n} referencias · de {min(ps):.2f} a {max(ps):.2f} €')

    for slug in SIN_DATOS:
        r = relojes.get(slug)
        if not r:
            continue
        fuera = r.pop('configurador', None) is not None
        # y también el «desde» del listado: era un precio escrito a mano
        # que no sale de la hoja. Sin dato, la tarjeta enseña el diámetro,
        # que es lo que hace desde siempre cuando no hay precio cerrado.
        if r.get('precio') is not None:
            r['precio'] = None
            fuera = True
        if fuera:
            print(f'  {slug:11} sin precio ni configurador: no está en la hoja')

    with open(CATALOGO, 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)
        f.write('\n')
    if pendientes:
        print('\nFUERA por estar sin cerrar en la hoja:')
        for ref, mov in pendientes:
            print(f'  {ref:30} {mov}')

    print('\ncatalogo.json reescrito')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'hoja.json')
