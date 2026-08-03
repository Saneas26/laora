#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · GENERADOR DE PÁGINAS
============================================================
La web sigue siendo HTML estático y sin proceso de compilación: lo que se
sube a Cloudflare son los .html que este fichero escribe. Lo que se evita
con él es la duplicación.

En la web anterior la cabecera y el pie del Grupo Saneas estaban copiados a
mano en once páginas: cualquier cambio había que hacerlo once veces y siempre
se olvidaba alguna. Aquí viven una sola vez y todas las páginas los heredan.

Las tarjetas de reloj se escriben en el HTML, no las pinta JavaScript: así
Google las lee y la página funciona aunque el JS no llegue a cargar.

USO
    python3 herramientas/generar.py

Reescribe index.html, las cuatro páginas de sección y las ocho fichas.
NO toca privacidad.html, que se mantiene a mano.

Los datos de los relojes salen de assets/datos/catalogo.json, que es la
única fuente de verdad. No hay ni un dato de reloj escrito en un HTML.
"""

import json
import os
import html as _html
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Versión de las hojas. SUBIRLAS EN CADA CAMBIO del CSS: Cloudflare lo sirve
# con max-age=14400 y sin esto el navegador se queda hasta cuatro horas con
# la hoja antigua.
V_CSS = 4
V_CAB = 12

with open(os.path.join(RAIZ, 'assets/datos/catalogo.json'), encoding='utf-8') as f:
    RELOJES = json.load(f)['relojes']


# ============================================================
# PARTES COMUNES
# ============================================================

def cabeza(titulo, descripcion, url, foto='/assets/img/relojes-2026/bitacora-hero-full.webp'):
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
<title>{titulo}</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/manifest.json">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<!-- Nunito Sans e Inter solo alimentan el logotipo y el pie del Grupo
     Saneas. El resto de la web va en Georgia y Arial. -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Nunito+Sans:wght@400&display=swap" rel="stylesheet">
<!-- GENERADO por herramientas/generar.py — no editar a mano.
     Los textos se cambian ahí; los datos de relojes, en
     assets/datos/catalogo.json. -->
<link rel="stylesheet" href="/assets/css/laora.css?v={V_CSS}">
<link rel="stylesheet" href="/assets/css/cabecera.css?v={V_CAB}">
</head>
<body>"""


def cabecera(activa=''):
    """La cabecera de siempre. `cabecera.js` le inyecta el desplegable del
    móvil y la deja fija al hacer scroll, así que aquí no hay nada de eso."""
    def enlace(href, texto, clave):
        cls = ' class="activo"' if activa == clave else ''
        return f'    <a href="{href}"{cls}>{texto}</a>'
    return f"""
<header class="cb cb-claro">
  <a class="cb-marca" href="/" aria-label="laOra, inicio">la<span class="o"></span>ra<sup>®</sup></a>
  <nav class="cb-menu" aria-label="Navegación principal">
{enlace('/coleccion.html', 'relojes', 'coleccion')}
{enlace('/filosofia.html', 'nuestra forma de hacer', 'filosofia')}
{enlace('/taller.html', 'taller y servicio', 'taller')}
    <!-- «laOra» no se escribe, se dibuja: es el logotipo canónico. La O es
         un span sin texto, así que un lector de pantalla leería «club lara»:
         de ahí el aria-label. -->
    <a class="cb-club" href="/club.html" aria-label="Club laOra">club <span class="cb-marca" aria-hidden="true">la<span class="o"></span>ra</span></a>
  </nav>
</header>"""


# El aviso legal del pie es lo que separa «homenaje» de «falsificación» a
# ojos de quien lea la web. No se quita de ninguna página.
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


def cierre(rotulo, titular, href, boton, href2, enlace2):
    return f"""
  <section class="cierre">
    <p class="rotulo oro">{rotulo}</p>
    <h2>{titular}</h2>
    <div class="fila-botones">
      <a class="boton boton-oscuro" href="{href}">{boton} <span aria-hidden="true">→</span></a>
      <a class="enlace" href="{href2}">{enlace2}</a>
    </div>
  </section>"""


def scripts(extra=''):
    return f"""
<script src="/assets/js/cabecera.js?v=3"></script>{extra}
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


def tarjeta(r):
    """Tarjeta de producto. La misma en la home y en el listado: es el
    desajuste entre ficha y listado que hubo en la web anterior y que no
    se puede repetir si sale de un solo sitio.

    Si el modelo no tiene precio cerrado, la línea del precio no se pinta:
    no queda un hueco ni un «—», sencillamente no está."""
    precio = ''
    if r['precio'] is not None:
        precio = f'      <span class="p-precio">Desde {precio_es(r["precio"])}</span>\n'
    return f"""      <article class="p-tarjeta">
        <a class="p-foto" href="/{r['slug']}.html" aria-label="Ver {r['nombre']}">
          <img src="{r['foto']}" alt="{r['nombre']} de laOra, {r['familia'].lower()}" loading="lazy">
          <span class="p-codigo">{r['codigo']}</span>
          <span class="p-flecha" aria-hidden="true">↗</span>
        </a>
        <div class="p-meta"><p>{r['familia']}</p><p>{r['diametro']}</p></div>
        <h3>{r['nombre']}</h3>
        <p class="p-frase">{r['frase']}</p>
        <p class="p-homenaje">{r['homenaje']}</p>
        <div class="p-acciones">
{precio}          <a href="/{r['slug']}.html">Ver {r['nombre']} <span aria-hidden="true">→</span></a>
        </div>
      </article>"""


def escribir(nombre, contenido):
    with open(os.path.join(RAIZ, nombre), 'w', encoding='utf-8') as f:
        f.write(contenido)
    print('  ✓ ' + nombre)


# ============================================================
# HOME
# ============================================================

destacados = '\n'.join(tarjeta(r) for r in RELOJES[:4])

escribir('index.html', cabeza(
    'laOra® — Iconos que conoces, honestamente nuestros',
    'laOra — homenajes honestos a los grandes iconos de la relojería. Sin falsificaciones ni logotipos ajenos: marca propia, componentes identificados y montaje, control y servicio en Madrid.',
    '/') + cabecera() + f"""

<main class="sobre-claro">

  <!-- ============ 1 · HÉROE ============ -->
  <section class="h-hero" id="inicio">
    <div class="h-hero-fotos" aria-hidden="true">
      <img class="h-hero-foto activa" src="/assets/img/relojes-2026/bitacora-hero-full.webp" alt="" fetchpriority="high">
      <img class="h-hero-foto" src="/assets/img/relojes-2026/bitacora-hero-dial.webp" alt="" loading="lazy">
      <img class="h-hero-foto" src="/assets/img/relojes-2026/bitacora-hero-movement.webp" alt="" loading="lazy">
    </div>
    <div class="h-hero-velo" aria-hidden="true"></div>

    <div class="h-hero-copy">
      <p class="rotulo oro">laOra · Madrid · Colección 2026</p>
      <h1>Iconos que conoces.<br><em>Honestamente nuestros.</em></h1>
      <p class="entradilla">
        Homenajes a los grandes relojes del mundo, sin falsificaciones ni logotipos ajenos.
        Componentes seleccionados y cada unidad montada, ajustada y probada en Madrid.
      </p>
      <div class="fila-botones">
        <a class="boton boton-oscuro" href="/coleccion.html">Descubrir la colección <span aria-hidden="true">↘</span></a>
        <a class="enlace" href="/filosofia.html">Por qué hacemos homenajes</a>
      </div>
      <!-- PENDIENTE DE LA HOJA DE MATERIALES: aquí va el «desde X €».
           Hasta que estén los precios reales no se enseña ninguno. -->
    </div>

    <div class="h-hero-mandos" role="group" aria-label="Elegir imagen del reloj">
      <button type="button" class="activa" data-foto="0" aria-label="Reloj completo"><span></span></button>
      <button type="button" data-foto="1" aria-label="Detalle de la esfera"><span></span></button>
      <button type="button" data-foto="2" aria-label="Detalle del movimiento"><span></span></button>
      <button type="button" class="h-hero-pausa" aria-label="Pausar el pase de imágenes">II</button>
    </div>
  </section>

  <!-- ============ 2 · TIRA DE CONFIANZA ============ -->
  <section class="h-confianza" aria-label="Razones para confiar en laOra">
    <article><span>01</span><div><b>Marca propia</b><p>Sin emblemas ni logotipos ajenos.</p></div></article>
    <article><span>02</span><div><b>Montaje en Madrid</b><p>Ajuste y control unidad a unidad.</p></div></article>
    <article><span>03</span><div><b>Componentes identificados</b><p>Origen y movimiento, sin rodeos.</p></div></article>
    <article><span>04</span><div><b>Stock real</b><p>Envío en 48 h cuando se indica.</p></div></article>
    <article><span>05</span><div><b>Servicio cercano</b><p>Taller y posventa en España.</p></div></article>
  </section>

  <!-- ============ 3 · EL MAPA DEL PRECIO ============
       Las cifras de mercado son ORIENTATIVAS, viven todas en
       assets/js/home.js y llevan su nota legal al pie de la sección.
       Si se actualizan, hay que actualizar también la fecha de la nota. -->
  <section class="h-mapa" id="mapa">
    <div class="h-mapa-cab">
      <div>
        <p class="rotulo oro">01 — El mapa del precio</p>
        <h2>Lo que cuesta un icono.<br><em>Y lo que pagas realmente.</em></h2>
      </div>
      <div class="h-mapa-intro">
        <p>Una comparación de canales, riesgos y alternativas. Sin confundir homenaje con falsificación.</p>
        <div class="h-mapa-pestanas" role="group" aria-label="Elegir comparación">
          <button type="button" data-mapa="lunar" aria-pressed="true">Speedmaster → Lunar</button>
          <button type="button" data-mapa="bitacora" aria-pressed="false">Nautilus → Bitácora</button>
        </div>
      </div>
    </div>

    <div class="h-mapa-cuerpo" aria-live="polite">
      <div class="h-mapa-contexto">
        <strong data-mapa-titulo>El cronógrafo lunar</strong>
        <span data-mapa-intro>Del canal oficial al mercado irregular: cinco rutas que pueden parecer similares en una foto, pero no ofrecen lo mismo.</span>
      </div>

      <div class="h-mapa-zonas" aria-hidden="true">
        <span>Mercado original y trazable</span>
        <span>Mercado irregular / clones</span>
      </div>

      <div class="h-mapa-tarjetas" data-mapa-tarjetas></div>

      <div class="h-mapa-pie">
        <div class="h-mapa-otras">
          <p class="rotulo apagado">Alternativas de otras marcas</p>
          <div data-mapa-otras></div>
        </div>
        <article class="h-mapa-laora">
          <img src="/assets/img/relojes-2026/lunar-front.webp" alt="" aria-hidden="true" data-mapa-foto>
          <div class="h-mapa-laora-precio">
            <span>laOra · <b data-mapa-modelo>Lunar</b></span>
            <!-- PENDIENTE DE LA HOJA DE MATERIALES: el precio del modelo. -->
          </div>
          <p data-mapa-valor>Acero y cristal según configuración, movimiento identificado antes de la venta y control individual en Madrid. Sin licencias de marca ajena ni capas comerciales innecesarias.</p>
          <a href="/lunar.html" data-mapa-enlace>Ver <b data-mapa-modelo>Lunar</b> <span aria-hidden="true">→</span></a>
        </article>
      </div>

      <p class="h-mapa-nota">
        Precios orientativos consultados en agosto de 2026; pueden variar por referencia, estado,
        impuestos, comisiones y envío. La presencia de una oferta no acredita su autenticidad.
        laOra no está afiliada a las marcas o plataformas citadas.
      </p>
    </div>
  </section>

  <!-- ============ 4 · CUATRO MODELOS ============ -->
  <section class="h-destacados">
    <div class="p-rejilla compacta">
{destacados}
    </div>
    <a class="boton boton-linea" href="/coleccion.html">Ver los ocho modelos <span aria-hidden="true">→</span></a>
  </section>

  <!-- ============ 5 · HOMENAJE NO ES FALSIFICACIÓN ============ -->
  <section class="h-manifiesto">
    <div class="h-manifiesto-foto">
      <img src="/assets/img/relojes-2026/precisa-hero.webp" alt="Reloj laOra Precisa, de acero y esfera azul" loading="lazy">
    </div>
    <div class="h-manifiesto-copy">
      <p class="rotulo oro-claro">Homenaje no es falsificación</p>
      <h2>La inspiración se reconoce.<br><em>La identidad no se suplanta.</em></h2>
      <p class="entradilla">
        Un homenaje toma una arquitectura conocida como punto de partida. Una falsificación intenta
        hacerse pasar por otra marca. En laOra no ocultamos la referencia y nunca ponemos en la
        esfera un nombre que no sea el nuestro.
      </p>
      <ul>
        <li><span aria-hidden="true">✓</span> Marca, modelo y documentación laOra</li>
        <li><span aria-hidden="true">✓</span> Sin logotipos, coronas ni escudos de terceros</li>
        <li><span aria-hidden="true">✓</span> Sin historias de origen inventadas</li>
        <li><span aria-hidden="true">✓</span> Sin sugerir afiliaciones que no existen</li>
      </ul>
      <a class="enlace claro" href="/filosofia.html">Nuestra forma de hacer <span aria-hidden="true">→</span></a>
    </div>
  </section>

  <!-- ============ 6 · CALIDAD DEMOSTRABLE ============ -->
  <section class="h-calidad">
    <div class="cabecera-seccion">
      <p class="rotulo oro">02 — Calidad demostrable</p>
      <h2>El misterio está en el reloj.<br><em>La confianza, en mostrarlo todo.</em></h2>
    </div>
    <div class="h-calidad-rejilla">
      <div class="h-calidad-foto">
        <img src="/assets/img/relojes-2026/lunar-detail.webp" alt="Detalle del reloj laOra Lunar" loading="lazy">
        <span class="orbita orbita-a" aria-hidden="true"></span>
        <span class="orbita orbita-b" aria-hidden="true"></span>
      </div>
      <ol class="lista-numerada">
        <li><span>01</span><div><b>Cristal</b><p>Zafiro cuando la configuración lo incluye.</p></div></li>
        <li><span>02</span><div><b>Caja</b><p>Acero 316L o titanio según acabado.</p></div></li>
        <li><span>03</span><div><b>Esfera</b><p>Nombre y emblema laOra. Ninguna marca ajena.</p></div></li>
        <li><span>04</span><div><b>Movimiento</b><p>Siempre identificado; nunca descrito con vaguedades.</p></div></li>
        <li><span>05</span><div><b>Cierre</b><p>Construcción y ajuste explicados en cada ficha.</p></div></li>
      </ol>
    </div>
  </section>

  <!-- ============ 7 · MADRID ============ -->
  <section class="h-madrid" id="taller">
    <img src="/assets/img/relojes-2026/workshop-hero.webp" alt="Revisión de un reloj laOra en el taller" loading="lazy">
    <div class="h-madrid-copy">
      <p class="rotulo oro-claro">Taller laOra · Madrid</p>
      <h2>Antes de llegar a tu muñeca,<br><em>pasa por nuestras manos.</em></h2>
      <ol>
        <li>Inspección</li><li>Montaje</li><li>Ajuste</li>
        <li>Pruebas</li><li>Control visual</li><li>Envío</li>
      </ol>
      <a class="boton boton-claro" href="/taller.html">Conocer el proceso <span aria-hidden="true">→</span></a>
    </div>
  </section>

  <!-- ============ 8 · CLUB ============ -->
  <section class="h-club">
    <div class="h-club-copy">
      <p class="rotulo oro">03 — Club laOra</p>
      <h2>Tu reloj continúa<br><em>dentro de la app.</em></h2>
      <p class="entradilla">
        Certificado, factura, garantía, historial, contacto directo con el taller y ventajas por
        recomendación. Todo en un único lugar, privado por defecto.
      </p>
      <a class="boton boton-oscuro" href="/club.html">Conocer Club laOra <span aria-hidden="true">→</span></a>
    </div>
    <div class="h-club-movil">
      <!-- El móvil va dibujado en CSS y no como foto: así no hay una
           captura de pantalla que se quede vieja cada vez que cambie la app. -->
      <div class="movil" role="img" aria-label="Pantalla de Club laOra con el pasaporte digital de un reloj">
        <div class="movil-pantalla">
          <p class="rotulo oro-claro">Club laOra</p>
          <h4>Mi colección</h4>
          <div class="movil-ficha"><b>Tortuga · LO—08</b><span>Pasaporte digital · Verificado</span></div>
          <div class="movil-ficha"><b>Garantía</b><span>Activa · hasta 08/2028</span></div>
          <div class="movil-ficha"><b>Taller</b><span>Sin intervenciones abiertas</span></div>
        </div>
      </div>
      <div class="h-club-flotante"><b>Pasaporte digital</b><span>LO—08 · Verificado</span></div>
    </div>
  </section>
""" + cierre('Tu tiempo. Tu elección.',
             'Elige el icono.<br><em>Nosotros respondemos por el reloj.</em>',
             '/coleccion.html', 'Ver la colección',
             '/club.html', 'Conocer Club laOra') + """

</main>
""" + PIE + scripts('\n<script src="/assets/js/home.js?v=2"></script>'))


# ============================================================
# COLECCIÓN
# ============================================================

listado = '\n'.join(tarjeta(r) for r in RELOJES)

escribir('coleccion.html', cabeza(
    'La colección — laOra®',
    'Ocho relojes laOra inspirados en grandes arquetipos de la relojería mundial. Marca propia, componentes identificados y montaje en Madrid.',
    '/coleccion.html', '/assets/img/relojes-2026/precisa-front.webp') + cabecera('coleccion') + f"""

<main class="sobre-claro" id="inicio">

  <section class="pagina-hero">
    <p class="rotulo oro">Colección laOra · 2026</p>
    <h1>Un icono para cada forma<br><em>de vivir el tiempo.</em></h1>
    <p class="entradilla">
      Elige por carácter, familia o uso. Cada ficha explica la referencia del homenaje,
      los componentes y el trabajo que hacemos en Madrid.
    </p>
  </section>

  <section class="c-listado">
    <div class="p-rejilla">
{listado}
    </div>
  </section>

  <section class="c-acabados">
    <div class="c-acabados-cab">
      <p class="rotulo oro">02 — Cuatro expresiones</p>
      <h2>El mismo homenaje.<br><em>Tu forma de llevarlo.</em></h2>
    </div>
    <div class="c-acabados-tarjetas">
      <article><span>01</span><h3>Alba</h3><b>Esencial</b><p>Precisión de cuarzo, diseño limpio y comodidad diaria.</p></article>
      <article><span>02</span><h3>Levante</h3><b>Refinado</b><p>Cuarzo con materiales y acabados superiores identificados.</p></article>
      <article><span>03</span><h3>Cenit</h3><b>Máxima expresión</b><p>La mejor ejecución disponible para cada familia.</p></article>
      <article class="oscura"><span>04</span><h3>Eclipse</h3><b>Carácter técnico</b><p>Negro integral o titanio, cuando la configuración lo permite.</p></article>
    </div>
  </section>
""" + cierre('Tu tiempo. Tu elección.',
             'Elige el icono.<br><em>Nosotros respondemos por el reloj.</em>',
             '/filosofia.html', 'Por qué hacemos homenajes',
             '/taller.html', 'Conocer el taller') + """

</main>
""" + PIE + scripts())


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

fichas_proceso = '\n'.join(
    f'    <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in PROCESO)

escribir('filosofia.html', cabeza(
    'Nuestra forma de hacer — laOra®',
    'Por qué laOra crea homenajes honestos y cómo selecciona, monta y controla cada reloj en Madrid. Sin réplicas ni logotipos ajenos.',
    '/filosofia.html', '/assets/img/relojes-2026/workshop-hero.webp') + cabecera('filosofia') + f"""

<main id="inicio">

  <section class="pagina-hero-foto">
    <img src="/assets/img/relojes-2026/workshop-hero.webp" alt="Reloj laOra durante su revisión en el taller">
    <div>
      <p class="rotulo oro-claro">Filosofía laOra</p>
      <h1>No inventamos los iconos.<br><em>Elegimos cómo honrarlos.</em></h1>
      <p class="entradilla claro">
        Sin herencias ficticias. Sin hacer pasar un reloj por lo que no es.
        La inspiración se cuenta; la calidad se demuestra.
      </p>
    </div>
  </section>

  <section class="bloque-dos sobre-claro">
    <p class="rotulo oro">01 — El punto de partida</p>
    <div><h2>La relojería también es<br><em>memoria compartida.</em></h2></div>
    <div>
      <p>Hay diseños que trascienden una referencia concreta y se convierten en lenguajes: el reloj de buceo de caja cojín, el cronógrafo lunar, el reloj de campaña, el deportivo integrado o la esfera de cóctel.</p>
      <p>laOra nace para acercar esos lenguajes a más personas con una propuesta independiente, transparente y atendida en España.</p>
    </div>
  </section>

  <section class="fi-honestidad">
    <div>
      <p class="rotulo oro-claro">Homenaje, con todas las letras</p>
      <h2>Reconocer el origen<br><em>también es diseñar confianza.</em></h2>
    </div>
    <div class="fi-columnas">
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

  <section class="rejilla-fichas sobre-claro">
    <div class="rejilla-fichas-cab">
      <p class="rotulo oro">02 — El proceso</p>
      <h2>De una referencia universal<br><em>a un reloj laOra.</em></h2>
    </div>
{fichas_proceso}
  </section>

  <section class="fi-origen sobre-claro">
    <div>
      <p class="rotulo oro">03 — Origen sin eufemismos</p>
      <h2>Componentes internacionales.<br><em>Responsabilidad cercana.</em></h2>
      <p>Buscamos cada componente donde puede fabricarse con la calidad y el coste adecuados. En Madrid concentramos el montaje, el ajuste, el control y el servicio que determinan la experiencia final.</p>
    </div>
    <img src="/assets/img/relojes-2026/box.webp" alt="Presentación del reloj laOra Tortuga en su caja" loading="lazy">
  </section>
""" + cierre('Sin apellido prestado',
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
    'Taller y servicio — laOra®',
    'Montaje, ajuste, pruebas y servicio técnico de los relojes laOra en Madrid. Seis pasos, una unidad cada vez.',
    '/taller.html', '/assets/img/relojes-2026/workshop-hero.webp') + cabecera('taller') + f"""

<main id="inicio">

  <section class="pagina-hero-foto">
    <img src="/assets/img/relojes-2026/workshop-hero.webp" alt="Reloj laOra durante el control final">
    <div>
      <p class="rotulo oro-claro">Taller y servicio · Madrid</p>
      <h1>Aquí empieza<br><em>la responsabilidad.</em></h1>
      <p class="entradilla claro">
        Los componentes pueden venir de distintos especialistas. El montaje, el control
        y la persona que responde están cerca.
      </p>
    </div>
  </section>

  <section class="bloque-dos sobre-claro">
    <p class="rotulo oro">01 — Antes del envío</p>
    <div><h2>Seis pasos.<br><em>Una unidad cada vez.</em></h2></div>
    <div><p>No publicamos pruebas que no estén confirmadas para una referencia concreta. La ficha de cada reloj indica exactamente qué se comprueba.</p></div>
  </section>

  <section class="t-pasos sobre-claro" style="padding-top:90px">
{chr(10).join(f'    <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in PASOS)}
  </section>

  <section class="t-servicio">
    <div>
      <p class="rotulo oro-claro">Después de la compra</p>
      <h2>Servicio sin<br><em>intermediarios.</em></h2>
      <p class="entradilla claro">Desde Club laOra puedes identificar tu reloj, abrir una consulta, adjuntar imágenes, solicitar recogida y seguir el estado de la intervención.</p>
      <a class="boton boton-oro" href="/club.html">Ver Club laOra <span aria-hidden="true">→</span></a>
    </div>
    <div class="t-servicio-lista">
{chr(10).join(f'      <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in SERVICIOS)}
    </div>
  </section>
""" + cierre('Seguimos aquí',
             'Elige el reloj.<br><em>Nos ocupamos del resto.</em>',
             '/coleccion.html', 'Ver la colección',
             'mailto:taller@laora.es', 'Escribir al taller') + """

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

MOVIL = """
      <div class="movil" role="img" aria-label="Pantalla de Club laOra con el pasaporte digital de un reloj">
        <div class="movil-pantalla">
          <p class="rotulo oro-claro">Club laOra</p>
          <h4>Mi colección</h4>
          <div class="movil-ficha"><b>Tortuga · LO—08</b><span>Pasaporte digital · Verificado</span></div>
          <div class="movil-ficha"><b>Garantía</b><span>Activa · hasta 08/2028</span></div>
          <div class="movil-ficha"><b>Taller</b><span>Sin intervenciones abiertas</span></div>
        </div>
      </div>"""

escribir('club.html', cabeza(
    'Club laOra — laOra®',
    'Colección, documentación, garantía y contacto con el taller en una sola aplicación. Privado por defecto.',
    '/club.html') + cabecera('club') + f"""

<main id="inicio">

  <section class="cl-hero">
    <div>
      <p class="rotulo oro-claro">Club laOra · Incluido con tu reloj</p>
      <h1>La relación no termina<br><em>cuando recibes el reloj.</em></h1>
      <p class="entradilla claro">
        Tu colección, documentación, garantía, servicio y ventajas en un único lugar.
        Una app útil, no otro programa publicitario.
      </p>
      <div class="fila-botones">
        <a class="enlace claro" href="#funciones">Ver cómo funciona</a>
      </div>
    </div>
    <div class="cl-hero-movil">{MOVIL}
    </div>
  </section>

  <section class="bloque-dos sobre-claro">
    <p class="rotulo oro">01 — Una relación útil</p>
    <div><h2>Tu reloj, su historia<br><em>y nuestro taller.</em></h2></div>
    <div>
      <p>Cuando abres Club laOra sabes exactamente qué tienes, qué cubre tu garantía, dónde está tu factura y con quién hablar si necesitas algo.</p>
      <p>Todo es privado por defecto y tú decides qué parte de tu colección quieres compartir.</p>
    </div>
  </section>

  <section class="rejilla-fichas sobre-claro" id="funciones">
    <div class="rejilla-fichas-cab">
      <p class="rotulo oro">02 — Todo en su sitio</p>
      <h2>Un club que sirve<br><em>para algo.</em></h2>
    </div>
{chr(10).join(f'    <article><span>{n}</span><h3>{t}</h3><p>{d}</p></article>' for n, t, d in VENTAJAS)}
  </section>

  <section class="cl-camino sobre-claro">
    <div>
      <p class="rotulo oro">Cómo funciona</p>
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

  <section class="cl-privacidad sobre-claro">
    <div>
      <p class="rotulo oro">03 — Privacidad clara</p>
      <h2>Tu colección es tuya.<br><em>También sus datos.</em></h2>
    </div>
    <div>
      <p class="entradilla">Guardamos únicamente la información necesaria para documentar el reloj, prestar el servicio y mantener tu cuenta.</p>
      <ul>
        <li>Escaparate privado por defecto.</li>
        <li>Control sobre qué compartes.</li>
        <li>Exportación y eliminación de la cuenta.</li>
        <li>Transferencia de propiedad con tu aprobación.</li>
      </ul>
    </div>
  </section>
""" + cierre('Club laOra',
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
# ============================================================

for i, r in enumerate(RELOJES):
    anterior = RELOJES[(i - 1) % len(RELOJES)]
    siguiente = RELOJES[(i + 1) % len(RELOJES)]

    specs = [(k, v) for k, v in [
        ('Familia', r['familia']),
        ('Diámetro', r['diametro']),
        ('Movimiento', r['movimiento']),
        ('Hermeticidad', r['hermeticidad']),
        ('Referencia', r['codigo']),
    ] if v]

    # Datos estructurados para Google. SIN precio: `offers` solo se escribe
    # cuando haya precio cerrado, porque un Product con un precio inventado
    # es justo lo que penaliza el buscador.
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

    minis = '\n'.join(
        f'        <button type="button" data-mini="{g}" aria-current="{str(n == 0).lower()}"'
        f' aria-label="Ver imagen {n + 1} de {r["nombre"]}"><img src="{g}" alt="" loading="lazy"></button>'
        for n, g in enumerate(r['galeria']))

    filas = '\n'.join(f'        <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in specs)

    tecnica = '\n'.join(
        f'        <li><span>{str(n + 1).zfill(2)}</span><div><b>{k}</b><p>{v}</p></div></li>'
        for n, (k, v) in enumerate(r['fichaTecnica']))

    asunto = quote(f'Consulta sobre el {r["nombre"]} {r["codigo"]}')

    escribir(r['slug'] + '.html', cabeza(
        f'{r["nombre"]} {r["codigo"]} — laOra®',
        r['descripcion'], f'/{r["slug"]}.html', r['foto']) + cabecera('coleccion') + f"""

<main class="sobre-claro" id="inicio">
<script type="application/ld+json">{ld}</script>

  <section class="f-hero">
    <div class="f-galeria">
      <div class="f-galeria-grande">
        <img src="{r['galeria'][0]}" alt="{r['nombre']} de laOra, vista seleccionada" data-foto-grande fetchpriority="high">
      </div>
      <div class="f-miniaturas" role="group" aria-label="Vistas de {r['nombre']}">
{minis}
      </div>
    </div>
    <div class="f-datos">
      <p class="rotulo apagado">{r['codigo']} · {r['familia']}</p>
      <h1>{r['nombre']}</h1>
      <p class="f-homenaje">{r['homenaje']}</p>
      <p class="f-descripcion">{r['descripcion']}</p>
      <dl class="f-especificaciones">
{filas}
      </dl>
      <!-- PENDIENTE DE LA HOJA DE MATERIALES: precio, movimiento y
           hermeticidad. Mientras estén a null en catalogo.json aquí no se
           pinta ninguna cifra ni ninguna línea sin dato. -->
      <div class="fila-botones">
        <a class="boton boton-oscuro" href="mailto:hola@laora.es?subject={asunto}">Preguntar por el {r['nombre']} <span aria-hidden="true">→</span></a>
      </div>
      <p class="f-nota">Montado, ajustado y probado en Madrid antes de cada envío.</p>
    </div>
  </section>

  <section class="f-historia">
    <div>
      <p class="rotulo oro">01 — El homenaje</p>
      <h2>Una referencia reconocible.<br><em>Una marca honesta.</em></h2>
    </div>
    <div>
      <p>{r['historia']}</p>
      <p>La esfera lleva únicamente el nombre laOra y el del modelo. No utilizamos marcas, coronas, escudos ni emblemas de terceros.</p>
    </div>
  </section>

  <section class="f-detalle">
    <div class="f-detalle-foto">
      <img src="{r['galeria'][1] if len(r['galeria']) > 1 else r['foto']}" alt="Detalle constructivo de {r['nombre']}" loading="lazy">
    </div>
    <div class="f-detalle-copy">
      <p class="rotulo oro">02 — Lo que recibes</p>
      <h2>Todo identificado.<br><em>Nada escondido.</em></h2>
      <ol class="lista-numerada">
{tecnica}
      </ol>
    </div>
  </section>

  <section class="f-servicio">
    <p class="rotulo oro-claro">Taller laOra · Madrid</p>
    <h2>Antes de llegar a tu muñeca,<br><em>pasa por nuestras manos.</em></h2>
    <ol>
      <li>Recepción e inspección</li><li>Montaje</li><li>Ajuste</li>
      <li>Pruebas</li><li>Control visual</li><li>Preparación y envío</li>
    </ol>
    <a class="enlace claro" href="/taller.html">Conocer el taller <span aria-hidden="true">→</span></a>
  </section>
""" + cierre('Sigue por la colección',
             f'Antes: {anterior["nombre"]}.<br><em>Después: {siguiente["nombre"]}.</em>',
             f'/{siguiente["slug"]}.html', f'Ver {siguiente["nombre"]}',
             '/coleccion.html', 'Volver a la colección') + """

</main>
""" + PIE + scripts('\n<script src="/assets/js/ficha.js?v=1"></script>'))


print(f'\nListo: {4 + len(RELOJES)} páginas generadas.')
