#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · EL PROMPT DE CADA IMAGEN
============================================================
Escribe el encargo completo para el diseñador de imágenes a partir del
catálogo. Óscar dice el modelo y la variante; esto pone las normas —que
son siempre las mismas— y rellena la ficha de esa variante con lo que
ya está escrito en `assets/datos/catalogo.json`.

Se hizo porque el texto de las normas ocupa cuatro pantallas y se
repite en cada reloj. Repetirlo a mano es como se cuelan los errores:
una vez pones «gris» donde iba «marfil» y ya tienes una imagen que no
pega con las demás.

USO
    python3 herramientas/prompt_imagen.py lunar alba piel-negra
    python3 herramientas/prompt_imagen.py lunar alba piel-negra --vista cierre
    python3 herramientas/prompt_imagen.py --lista lunar

LO QUE NO HACE
    No inventa. Si un dato no está en el catálogo, escribe
    «— sin dato en el catálogo —» y lo lista al final para que se
    complete antes de encargar la imagen. Antes sin dato que con un
    dato inventado.
"""

import argparse
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGO = os.path.join(RAIZ, 'assets/datos/catalogo.json')
CARPETA_CATALOGO = 'assets/img/catalogo'

FALTA = '— sin dato en el catálogo —'

# El fondo de TODAS las imágenes aprobadas es este marfil cálido, no el
# gris que decía la primera versión de las normas. Se cambia aquí y se
# cambia en todos los encargos a la vez.
FONDO = 'marfil cálido muy claro, plano y sin degradado, el mismo de las imágenes ya aprobadas'


# ============================================================
# Las normas. Son iguales para todos los relojes.
# ============================================================
NORMAS = """Actúa como diseñador industrial, diseñador gráfico y fotógrafo de producto especializado en relojería. Tu trabajo consiste en desarrollar todas las imágenes de una colección de relojes laOra combinando referencias de cajas, esferas, agujas, biseles, brazaletes, correas y cierres.

IDENTIDAD laOra
La esfera debe llevar siempre este bloque de marca:

1. Logotipo `laOra`, respetando exactamente las mayúsculas y minúsculas:
   * `la` en minúsculas.
   * `O` en mayúscula.
   * `ra` en minúsculas.
   * Tipografía similar a Nunito Sans.
2. Dentro de la `O`, en su posición interior de las 12, incluir un pequeño triángulo amarillo con el vértice apuntando hacia abajo.
3. Debajo de `laOra`, colocar una línea horizontal fina.
4. Inmediatamente debajo de la línea, escribir el nombre del modelo en mayúsculas, centrado y con espaciado refinado.
5. Usar una tipografía geométrica semejante a Montserrat Arabic para el modelo.
6. Todo el bloque `laOra / línea / MODELO` debe estar centrado y situado por encima del eje de las agujas.
7. Nunca colocar el nombre del modelo a las 6.
8. No añadir logotipos, letras o grabados en caja, corona, pulsadores, brazalete, cierre o correa.
9. Conservar las inscripciones funcionales originales, como `TACHYMÈTRE`, números, índices y graduaciones del bisel.
10. Eliminar cualquier marca del fabricante de referencia, vendedor, tienda, watermark, flecha o texto comercial.

FUENTES DE REFERENCIA
Antes de generar una imagen:

1. Revisa las imágenes locales y las URLs proporcionadas.
2. Identifica claramente la función de cada referencia: caja, bisel, esfera, agujas, brazalete o correa, cierre, imagen maestra aprobada.
3. Usa la imagen maestra aprobada como base obligatoria.
4. Cambia únicamente los componentes solicitados.
5. Conserva intactos encuadre, proporciones, iluminación y componentes ya aprobados.
6. Si una URL tiene poca resolución, combínala con el material local del componente equivalente.
7. Si una referencia no se puede descargar o no permite identificar el componente, avisa antes de generar.

REGLAS PARA BRAZALETES
Antes de generar, describe expresamente: número de columnas de eslabones; ancho relativo o real de cada columna; acabado de cada columna, cepillado mate o pulido; alineación y desfase de las juntas; patrón de intercalado; ancho entre asas; reducción progresiva o taper; tipo de terminal; tipo de cierre.

No reconstruyas un brazalete aprobado si solo hay que añadir, eliminar o cambiar un elemento. Edita la imagen maestra y conserva su articulación original.

BRAZALETE DE TRES ESLABONES
* Dos columnas exteriores anchas.
* Una columna central ancha.
* Acero cepillado mate salvo indicación contraria.
* Mantener exactamente el intercalado y las juntas de la referencia aprobada.

BRAZALETE DE CINCO ESLABONES ANCHOS
Distribución transversal para 20 mm:
* Eslabón 1: 6 mm, cepillado mate.
* Eslabón 2: 1 mm, pulido brillante.
* Eslabón 3: 6 mm, cepillado mate.
* Eslabón 4: 1 mm, pulido brillante.
* Eslabón 5: 6 mm, cepillado mate.

Reglas de intercalado:
* Los eslabones 1 y 5 comparten altura y juntas.
* Los eslabones 2, 3 y 4 comparten exactamente longitud, altura y juntas.
* El grupo 2–3–4 está desplazado medio eslabón respecto a 1 y 5.
* Los eslabones 2 y 4 son piezas articuladas independientes, no líneas, surcos ni raíles continuos.
* El efecto final debe funcionar como una construcción de ladrillos intercalados.

BRAZALETE JUBILEE
* Dos filas exteriores anchas y cepilladas.
* Tres filas centrales de eslabones pequeños, redondeados y pulidos.
* Construcción densa, flexible, articulada e intercalada.
* Puede ser acero plata completo, negro PVD/DLC, o bicolor con exteriores plata y tres filas centrales en oro rosa.
* Mantener terminales ajustados y conexión natural con las asas.

ACABADOS
* Cepillado mate: grano fino, lineal y visible.
* Pulido: reflejo limpio y controlado, sin aspecto plástico.
* Acero plata: tono neutro realista.
* Oro rosa: cobre rosado refinado, nunca amarillo, naranja o bronce.
* Negro PVD/DLC: negro metálico con volumen y reflejos de borde; nunca una silueta sin detalles.
* No mezclar acabados salvo que se indique expresamente.

CIERRES
Para cada cierre define: tipo (mariposa, Oyster, desplegable u otro); estado, abierto o cerrado; número de brazos; longitud de cada tramo; posición de bisagras y pulsadores; presencia de seguro abatible; microajuste; acabado de tapa, laterales y franja central.

CIERRE OYSTER
* Tapa exterior estrecha y alargada.
* Seguro abatible más corto que la tapa principal.
* Brazo desplegable interior.
* Sistema de enganche reconocible.
* Canal de microajuste con posiciones claramente visibles.
* Si el brazalete tiene un eslabón central diferenciado, el cierre debe continuar su diseño mediante una franja central del mismo ancho.
* La franja central puede ser pulida; los laterales permanecen cepillados.
* En la vista cerrada, la parte sur o tapa principal conserva su longitud.
* La parte norte o seguro debe medir aproximadamente la mitad.
* No duplicar tapas, cierres, brazos o ramales del brazalete.

COMPOSICIÓN Y FOTOGRAFÍA
* Fotografía de producto premium y fotorrealista.
* Iluminación de estudio suave y controlada.
* Reflejos capaces de explicar materiales y acabados.
* Bordes perfectamente definidos.
* Proporciones mecánicamente plausibles.
* Sin accesorios, manos, cajas comerciales u objetos adicionales.
* Sin textos fuera de la esfera.
* No deformar eslabones, asas, corona, pulsadores o agujas.

CONTROL ANTES DE ENTREGAR
Comprueba visualmente: ¿`laOra` está escrito correctamente? ¿La `O` es mayúscula? ¿El triángulo amarillo está dentro de la `O` y apunta hacia abajo? ¿La línea divisoria aparece debajo? ¿El nombre del modelo está inmediatamente debajo y en mayúsculas? ¿Todo el bloque está por encima del eje? ¿Se ha eliminado cualquier nombre a las 6? ¿El taquímetro y su escala están completos? ¿El brazalete coincide con la referencia? ¿El número, ancho, acabado y desfase de los eslabones son correctos? ¿El cierre es mecánicamente coherente? ¿Se han eliminado todas las marcas del proveedor? ¿El fondo ofrece suficiente contraste? ¿Se ha modificado únicamente lo solicitado?

Genera la imagen directamente cuando las referencias sean suficientes. Si existe una contradicción entre el texto y una imagen, detente e indica exactamente cuál es la contradicción antes de generar."""


VISTAS = {
    'frontal': ('Vista frontal principal',
                'Reloj completo, perfectamente centrado, corona a las 3, correa o brazalete '
                'completo y simétrico, sombra suave.'),
    'cierre':  ('Detalle del cierre',
                'Primer plano del cierre. Iluminación lateral que permita distinguir todos los '
                'componentes. Nunca negro sobre negro.'),
    'lamina':  ('Lámina doble del cierre',
                'Una sola imagen horizontal. A la izquierda, cierre abierto con el microajuste; '
                'a la derecha, cierre cerrado con la tapa exterior. Misma escala y material, '
                'sin textos ni líneas divisorias.'),
    'tresacuartos': ('Vista de tres cuartos', 'El reloj girado, mostrando el canto de la caja y el perfil.'),
    'lateral': ('Vista lateral', 'Perfil completo: grosor de caja, corona y pulsadores.'),
    'muneca': ('Reloj sobre muñeca', 'Sobre muñeca, iluminación de estudio, sin más objetos.'),
}


def limpio(t):
    """Para nombres de archivo: sin tildes, sin espacios, en minúsculas."""
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def cargar():
    with open(CATALOGO, encoding='utf-8') as f:
        return json.load(f)['relojes']


def buscar(relojes, slug):
    for r in relojes:
        if r.get('slug') == slug:
            return r
    disponibles = ', '.join(sorted(x.get('slug', '') for x in relojes))
    raise SystemExit('No encuentro el modelo «%s». Hay: %s' % (slug, disponibles))


def listar(r):
    cfg = r.get('configurador') or {}
    print('%s · %s' % (r.get('codigo'), r.get('nombre')))
    print('\nACABADOS')
    for a in cfg.get('acabados', []):
        print('  %-16s %s' % (a.get('id'), a.get('movimiento') or ''))
    print('\nCORREAS')
    for c in cfg.get('correas', []):
        print('  %-28s %s' % (c.get('id'), c.get('nombre')))


def referencia(r, acabado, indice):
    """La referencia de venta de esa combinación, si el catálogo la tiene."""
    refs = acabado.get('refs')
    if refs and indice < len(refs) and refs[indice]:
        return refs[indice]
    num = acabado.get('refNum')
    if num and indice < len(num) and num[indice]:
        letra = (acabado.get('id') or '?')[0].upper()
        codigo = (r.get('codigo') or '').replace('—', '-').replace(' ', '')
        return '%s_%s_%s%s' % (codigo, r.get('nombre'), letra, num[indice])
    return None


def precio(cfg, acabado_id, indice):
    p = (cfg.get('precios') or {}).get(acabado_id)
    if isinstance(p, list) and indice < len(p) and p[indice] is not None:
        return p[indice]
    if isinstance(p, list) and len(p) == 1 and p[0] is not None:
        return p[0]
    return None


def linea(etiqueta, valor, faltantes):
    if valor in (None, '', []):
        faltantes.append(etiqueta)
        valor = FALTA
    return '* %s: %s' % (etiqueta, valor)


def construir(r, acabado, correa, indice, vista, maestra, cambiar, mantener):
    cfg = r['configurador']
    com = cfg.get('comunes') or {}
    faltan = []

    nombre = r.get('nombre')
    codigo = (r.get('codigo') or '').replace('—', '-')
    ref = referencia(r, acabado, indice)
    pvp = precio(cfg, acabado.get('id'), indice)

    caja = acabado.get('caja')
    es_negra = 'pvd' in (caja or '').lower() or 'negro' in (caja or '').lower()
    metal = 'negro PVD satinado' if es_negra else 'acero plata, pulido y satinado'

    detalle_correa = correa.get('detalle') or ''
    cierre = detalle_correa.split('·')[-1].strip() if '·' in detalle_correa else None
    if not cierre:
        cierre = 'hebilla de acero' if 'piel' in (correa.get('id') or '') else None

    titulo_vista, desc_vista = VISTAS.get(vista, VISTAS['frontal'])

    especificacion = '\n'.join([
        linea('Caja', caja, faltan),
        linea('Asas', 'integradas en la caja, mismo acabado (%s)' % metal, faltan),
        linea('Corona', '%s, %s' % (com.get('Corona', 'corona de acero'), metal), faltan),
        linea('Pulsadores', 'cilíndricos, %s' % metal, faltan)
        if r.get('familia') == 'Cronógrafo' else '* Pulsadores: no lleva',
        linea('Bisel', acabado.get('bisel'), faltan),
        linea('Inscripciones del bisel', acabado.get('inscripcionesBisel'), faltan),
        linea('Esfera', com.get('Esfera'), faltan),
        linea('Subesferas', acabado.get('subesferas'), faltan),
        linea('Índices', acabado.get('indices'), faltan),
        linea('Agujas', acabado.get('agujas'), faltan),
        linea('Correa o brazalete', '%s — %s' % (correa.get('nombre'), detalle_correa), faltan),
        linea('Cierre', cierre, faltan),
        linea('Cristal', acabado.get('cristal'), faltan),
        linea('Diámetro', acabado.get('diametro') or r.get('diametro'), faltan),
        linea('Ancho de asa', com.get('Ancho de asa'), faltan),
        linea('Fondo', com.get('Fondo'), faltan),
    ])

    archivo = '[NÚMERO]-laora-%s-%s-%s-v1.png' % (
        limpio(nombre), limpio(acabado.get('id')), limpio(correa.get('id')))

    partes = [NORMAS, '', '=' * 60, '', 'MODELO', '',
              '* Nombre del modelo: %s' % nombre,
              '* Código interno: %s' % codigo,
              '* Referencia de venta: %s' % (ref or FALTA),
              '* Imagen maestra aprobada: %s' % maestra,
              '* Formato final: imagen de catálogo fotorrealista.',
              '* Fondo: %s' % FONDO,
              '* Vista principal: frontal, centrada, simétrica y con el reloj completo.',
              '* No improvises componentes que no aparezcan en las referencias.',
              '', 'ESPECIFICACIÓN DEL RELOJ', '', especificacion,
              '', 'IMAGEN QUE HAY QUE GENERAR', '',
              '* %s' % titulo_vista, '* %s' % desc_vista,
              '* Fondo: %s' % FONDO,
              '', 'DATOS PARA ESTA VARIANTE', '',
              '* Acabado: %s' % (acabado.get('nombre') or acabado.get('id')),
              '* Movimiento: %s' % (acabado.get('movimiento') or FALTA),
              '* Cambiar únicamente: %s' % cambiar,
              '* Mantener intacto: %s' % mantener,
              '* Nombre del archivo: %s' % archivo]

    if pvp:
        partes.insert(partes.index('ESPECIFICACIÓN DEL RELOJ') - 1, '')

    texto = '\n'.join(p for p in partes if p is not None)
    return texto, faltan, ref, pvp


def principal():
    ap = argparse.ArgumentParser(description='El encargo de imagen de una variante de laOra.')
    ap.add_argument('modelo')
    ap.add_argument('acabado', nargs='?')
    ap.add_argument('correa', nargs='?')
    ap.add_argument('--vista', default='frontal', choices=sorted(VISTAS))
    ap.add_argument('--maestra', help='Imagen aprobada que sirve de base.')
    ap.add_argument('--cambiar', default='la correa y su cierre')
    ap.add_argument('--mantener', default='caja, bisel, esfera, subesferas, índices, agujas, '
                                          'corona, pulsadores, encuadre, iluminación y fondo')
    ap.add_argument('--lista', action='store_true', help='Enseña acabados y correas del modelo.')
    args = ap.parse_args()

    relojes = cargar()
    r = buscar(relojes, args.modelo)
    if args.lista or not args.acabado:
        return listar(r)

    cfg = r['configurador']
    acabados = {a.get('id'): a for a in cfg['acabados']}
    if args.acabado not in acabados:
        raise SystemExit('Acabados de %s: %s' % (r['nombre'], ', '.join(acabados)))
    acabado = acabados[args.acabado]

    correas = cfg['correas']
    indice = next((i for i, c in enumerate(correas) if c.get('id') == args.correa), None)
    if indice is None:
        raise SystemExit('Correas de %s: %s' % (r['nombre'], ', '.join(c.get('id') for c in correas)))
    correa = correas[indice]

    maestra = args.maestra
    if not maestra:
        ref = referencia(r, acabado, indice)
        candidata = os.path.join(CARPETA_CATALOGO, '%s.webp' % ref) if ref else None
        maestra = candidata if candidata and os.path.exists(os.path.join(RAIZ, candidata)) else FALTA

    texto, faltan, ref, pvp = construir(r, acabado, correa, indice, args.vista,
                                        maestra, args.cambiar, args.mantener)
    print(texto)

    if faltan or pvp or ref:
        print('\n' + '=' * 60)
        print('NOTAS PARA ÓSCAR (esto NO se envía al diseñador)')
        if ref:
            print('  Referencia: %s%s' % (ref, '  ·  %.2f €' % pvp if pvp else ''))
        if faltan:
            print('  Faltan en el catálogo, complétalos antes de encargar:')
            for f in faltan:
                print('    · %s' % f)


if __name__ == '__main__':
    principal()
