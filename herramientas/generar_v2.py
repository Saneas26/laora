#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LANDING V2 DEL LUNAR
============================================================
Rediseño completo de la ficha para el móvil, según el guion que Óscar
trajo de su equipo (04/08/2026). Se escribe en `lunarv2.html` y NO toca
nada de lo que ya está publicado: ni `lunar.html`, ni `laora.css`, ni
`ficha.js`. Tiene su propia hoja y su propio script.

LA IDEA: en el móvil la gente no lee, hace scroll. Doce pantallas, una
idea por pantalla, la foto mandando y el texto solo donde aporta.
Aproximadamente 80 % imagen, 15 % titular, 5 % texto.

USO
    python3 herramientas/generar_v2.py

LOS DATOS SALEN DEL MISMO `catalogo.json`. Ni un precio escrito a mano:
si mañana cambia la hoja, esta página cambia con ella.
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V_CSS = 9
V_JS = 1

with open(os.path.join(RAIZ, 'assets/datos/catalogo.json'), encoding='utf-8') as f:
    RELOJES = json.load(f)['relojes']

R = {x['slug']: x for x in RELOJES}['lunar']
CFG = R['configurador']
IMG = '/assets/img/relojes-2026'

# El logotipo nunca se escribe: es el isotipo. Misma regla que el resto del sitio.
MARCA = ('<span class="marca" aria-hidden="true">la<span class="o"></span>ra</span>'
         '<span class="sr">laOra</span>')


def euros(v):
    return f'{v:,.2f}'.replace(',', '·').replace('.', ',').replace('·', '.') + ' €'


DESDE = min(x for l in CFG['precios'].values() for x in l if x is not None)
HASTA = max(x for l in CFG['precios'].values() for x in l if x is not None)


# ============================================================
# 1 · HERO
# ============================================================
# Dos fotos, no una: la apaisada llena la pantalla del escritorio y deja
# aire a la izquierda para el texto; la cuadrada es la que se ve ENTERA y
# centrada en el móvil. Sirviéndolas con <picture> cada pantalla se lleva
# solo la suya, así que el móvil no se descarga la grande para nada.
HERO = f"""
  <section class="pantalla hero" id="arriba">
    <picture>
      <source media="(min-width: 900px)" srcset="{IMG}/lunar-portada-ancha.webp">
      <img class="hero-foto" src="{IMG}/lunar-portada-movil.webp"
           alt="Reloj Lunar de laOra en su acabado Eclipse, cronógrafo negro integral"
           fetchpriority="high">
    </picture>
    <div class="hero-texto">
      <h1>Lunar</h1>
      <p class="hero-linea">Cronógrafo inspirado en una leyenda.</p>
      <p class="hero-precio">desde <strong>{euros(DESDE)}</strong></p>
      <a class="boton" href="#comprar">Comprar ahora</a>
    </div>
    <span class="baja" aria-hidden="true"></span>
  </section>"""


# ============================================================
# 2 · EL GOLPE  ·  dos pantallas, y el scroll entre medias
# ============================================================
GOLPE = """
  <section class="pantalla golpe">
    <p class="enorme">¿Por qué un reloj así<br>cuesta más de <em>7.000 €</em>…</p>
  </section>

  <section class="pantalla golpe golpe-2">
    <p class="enorme">…si fabricar uno excelente<br>cuesta <em>una pequeña parte</em>?</p>
  </section>"""


# ============================================================
# 3 · EL PLANO LARGO
# El guion pedía un vídeo de diez segundos del reloj girando. No lo hay
# todavía, así que va la foto más cinematográfica a pantalla completa y
# el hueco del vídeo queda preparado: el día que exista se cambia el
# <img> por un <video> con las mismas clases y ya está.
# ============================================================
PLANO = f"""
  <section class="pantalla plano">
    <img src="{IMG}/lunar-hero.webp" alt="El Lunar en su acabado Eclipse, negro integral" loading="lazy">
    <p class="plano-pie">Eclipse. Negro integral.</p>
  </section>"""


# ============================================================
# 4 · LAS SEIS RAZONES  ·  una por pantalla
# `foto` a None = todavía no existe esa imagen. En vez de dejar un hueco
# roto, la pantalla se resuelve con tipografía sobre fondo, que en este
# diseño no desentona. Ver la lista de fotos pendientes al final.
# ============================================================
RAZONES = [
    dict(n='01', titulo='Cristal', dato='Zafiro',
         lineas=['No plástico.', 'No cristal mineral.'],
         nota='El zafiro solo lo raya un diamante. Es lo que llevan los relojes de cuatro cifras.',
         foto=None, tema='claro'),
    dict(n='02', titulo='Acero', dato='316L macizo',
         lineas=['No chapado.', 'No hueco.'],
         nota='El mismo acero quirúrgico que usa la relojería suiza. No suelta níquel ni se pica.',
         foto=f'{IMG}/lunar-detail.webp', tema='oscuro'),
    dict(n='03', titulo='Movimiento', dato='A elegir',
         lineas=['Seiko VK63 · mecacuarzo.', 'Seagull ST19 · rueda de columnas.'],
         nota='El japonés da el golpe seco de un cronógrafo mecánico con la precisión del cuarzo. '
              'El chino es mecánico entero, de cuerda manual.',
         foto=None, tema='claro'),
    dict(n='04', titulo='Ensamblado', dato='En Madrid',
         lineas=['Montado a mano.', 'Probado uno a uno.'],
         nota='Cada reloj se abre, se ajusta y se comprueba antes de salir. Con nombre y fecha.',
         foto=None, tema='oscuro'),
    dict(n='05', titulo='Hermeticidad', dato='50 metros',
         lineas=['Lluvia.', 'Ducha.', 'Manos.'],
         nota='Cifra del acabado Cenit. La declara el fabricante de la caja, y no la inflamos.',
         foto=None, tema='claro'),
    dict(n='06', titulo='Lumen', dato='Super-LumiNova',
         lineas=['Agujas.', 'Índices.'],
         nota='Se carga con la luz del día y se lee a oscuras. Sin pilas ni trucos.',
         foto=None, tema='oscuro'),
]


def razon(r):
    foto = (f'    <div class="razon-foto"><img src="{r["foto"]}" alt="{r["titulo"]} del Lunar" loading="lazy"></div>'
            if r['foto'] else '')
    lineas = '\n'.join(f'      <p class="razon-linea">{l}</p>' for l in r['lineas'])
    return f"""
  <section class="pantalla razon {r['tema']}{' con-foto' if r['foto'] else ''}">
{foto}
    <div class="razon-texto">
      <p class="razon-n">{r['n']}</p>
      <h2>{r['titulo']}</h2>
      <p class="razon-dato">{r['dato']}</p>
{lineas}
      <p class="razon-nota">{r['nota']}</p>
    </div>
  </section>"""


# ============================================================
# 5 · COMPARATIVA
# ============================================================
COMPARA = [
    ('Cristal de zafiro', True, True),
    ('Acero inoxidable 316L', True, True),
    ('Movimiento japonés', True, True),
    ('Garantía', True, True),
    ('Presupuesto en marketing', False, True),
    ('Presupuesto en joyería', False, True),
]


def fila_compara(t, a, b):
    def m(v):
        return ('<span class="si" aria-label="sí">✔</span>' if v
                else '<span class="no" aria-label="no">—</span>')
    return f'          <tr><th scope="row">{t}</th><td>{m(a)}</td><td>{m(b)}</td></tr>'


TABLA = f"""
  <section class="pantalla compara">
    <h2>Lo mismo dentro.<br><em>Otro precio fuera.</em></h2>
    <table>
      <thead>
        <tr><td></td><th scope="col">{MARCA}</th><th scope="col">Marca de lujo</th></tr>
      </thead>
      <tbody>
{chr(10).join(fila_compara(*c) for c in COMPARA)}
        <tr class="precio-fila">
          <th scope="row">Precio</th>
          <td><strong>{euros(DESDE)}</strong></td>
          <td><strong>7.500 €</strong></td>
        </tr>
      </tbody>
    </table>
    <p class="compara-aviso">Precio de referencia orientativo de un cronógrafo de acero de
    marca reconocida, consultado en agosto de 2026.</p>
  </section>"""


# ============================================================
# 6 · GALERÍA  ·  una foto enorme detrás de otra
# ============================================================
GALERIA = '\n'.join(f"""
  <section class="pantalla foto-sola">
    <img src="{g}" alt="Lunar de laOra, vista {n + 1}" loading="lazy">
  </section>""" for n, g in enumerate([f'{IMG}/lunar-acero.webp', f'{IMG}/lunar-detail.webp',
                                       f'{IMG}/lunar-front.webp']))


# ============================================================
# 7 · ESPECIFICACIONES  ·  en acordeón, para quien quiera leerlas
# Salen del catálogo: el acabado de entrada más lo que es común.
# ============================================================
PRIMERO = CFG['acabados'][0]
ESPECS = [
    ('Caja', [PRIMERO.get('caja'), CFG['comunes'].get('Grosor'), PRIMERO.get('diametro')]),
    ('Movimiento', [PRIMERO.get('movimiento'), PRIMERO.get('movimientoTipo'),
                    PRIMERO.get('frecuencia'), PRIMERO.get('autonomia')]),
    ('Cristal', [PRIMERO.get('cristal')]),
    ('Bisel', [PRIMERO.get('bisel')]),
    ('Esfera', [CFG['comunes'].get('Esfera'), CFG['comunes'].get('Luminiscencia')]),
    ('Corona y fondo', [CFG['comunes'].get('Corona'), CFG['comunes'].get('Fondo')]),
    ('Correa', [f'{len(CFG["correas"])} opciones', CFG['comunes'].get('Ancho de asa')]),
    ('Peso', [PRIMERO.get('peso')]),
    ('Garantía', ['Dos años', 'Revisión incluida el primer año']),
]


def especificacion(n, titulo, valores):
    filas = '\n'.join(f'        <li>{v}</li>' for v in valores if v)
    abierta = ' open' if n == 0 else ''
    return f"""      <details{abierta}>
        <summary>{titulo}</summary>
        <ul>
{filas}
        </ul>
      </details>"""


ACORDEON = f"""
  <section class="pantalla especs">
    <h2>Especificaciones</h2>
    <div class="acordeon">
{chr(10).join(especificacion(n, t, v) for n, (t, v) in enumerate(ESPECS))}
    </div>
    <p class="especs-nota">Datos del acabado de entrada. Cada acabado cambia el movimiento,
    el bisel y el cristal.</p>
  </section>"""


# ============================================================
# 8 · FILOSOFÍA
# ============================================================
FILOSOFIA = f"""
  <section class="pantalla filosofia">
    <p class="enorme">Todo el dinero<br>tenía que ir <em>al reloj</em>.</p>
    <p class="filosofia-lista">No al marketing.<br>No a la joyería.<br>No a una caja de lujo.</p>
    <p class="filosofia-cierre">Por eso nació {MARCA}.</p>
  </section>"""


# ============================================================
# 9 · LO QUE LLEGA A CASA
# El guion pedía tres fotos —caja, reloj y faja—. No existen todavía, así
# que la pantalla lo cuenta con palabras hasta que las haya.
# ============================================================
PAQUETE = """
  <section class="pantalla paquete">
    <h2>Lo que llega a casa</h2>
    <ol>
      <li><span>01</span> El reloj, montado y probado.</li>
      <li><span>02</span> Una caja sobria. Sin terciopelo ni luces.</li>
      <li><span>03</span> Su ficha, con el número de serie y la fecha de montaje.</li>
    </ol>
  </section>"""


# ============================================================
# 10 · PRECIO
# ============================================================
COMPRAR = f"""
  <section class="pantalla comprar" id="comprar">
    <p class="comprar-modelo">Lunar</p>
    <p class="comprar-precio">{euros(DESDE)}</p>
    <p class="comprar-rango">Hasta {euros(HASTA)} según acabado y correa</p>
    <a class="boton grande" href="/lunar.html">Elegir acabado</a>
    <ul class="comprar-notas">
      <li>Envío en 24-48 h</li>
      <li>Dos años de garantía</li>
      <li>Impuestos incluidos</li>
    </ul>
  </section>"""


# ============================================================
# 11 · PREGUNTAS  ·  cinco, ni una más
# ============================================================
PREGUNTAS = [
    ('¿Es una copia?',
     'No. No lleva ninguna marca ajena, ni corona, ni escudo, ni logotipo de nadie. '
     'En la esfera solo va nuestro nombre. Es un homenaje a una arquitectura conocida, '
     'y lo decimos abiertamente.'),
    ('¿Por qué cuesta tan poco?',
     'Porque no hay tienda en una calle cara, ni campaña, ni intermediarios. El dinero '
     'se va en la caja, el cristal y el movimiento, que es donde se nota.'),
    ('¿Puedo mojarlo?',
     'Con el acabado Cenit, que declara 50 metros: lluvia, ducha y lavarte las manos, sí. '
     'Bucear, no. Y siempre con la corona enroscada.'),
    ('¿Qué pasa si se estropea?',
     'Dos años de garantía. Se repara en Madrid, no se manda a ningún sitio.'),
    ('¿Cuánto tarda en llegar?',
     'De 24 a 48 horas si está montado. Si eliges una combinación que hay que preparar, '
     'te decimos la fecha antes de cobrarte nada.'),
]

FAQ = f"""
  <section class="pantalla faq">
    <h2>Preguntas</h2>
    <div class="acordeon">
{chr(10).join(f'''      <details>
        <summary>{p}</summary>
        <p>{r}</p>
      </details>''' for p, r in PREGUNTAS)}
    </div>
  </section>"""


# ============================================================
# CABECERA Y PIE  ·  los dos, al mínimo
# ============================================================
CABECERA = f"""
<header class="cab">
  <a class="cab-marca" href="/" aria-label="laOra, inicio">la<span class="o"></span>ra</a>
  <button class="cab-boton" type="button" aria-expanded="false" aria-controls="menu"
          aria-label="Abrir menú">☰</button>
  <nav class="cab-menu" id="menu" hidden>
    <a href="#comprar">Comprar</a>
    <a href="/filosofia.html">Filosofía</a>
    <a href="/taller.html">Garantía</a>
    <a href="/club.html">Mi cuenta</a>
  </nav>
</header>"""

PIE = f"""
<footer class="pie">
  <a class="cab-marca" href="#arriba" aria-label="laOra, volver arriba">la<span class="o"></span>ra</a>
  <nav>
    <a href="/coleccion.html">Relojes</a>
    <a href="/filosofia.html">Filosofía</a>
    <a href="/taller.html">Garantía</a>
    <a href="/privacidad.html">Privacidad</a>
  </nav>
  <p>{MARCA} es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o
  logotipos ajenos.</p>
  <small>© 2026 laOra®</small>
</footer>"""


PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{R['descripcion']}">
<meta name="robots" content="noindex">
<meta property="og:title" content="Lunar · laOra">
<meta property="og:description" content="{R['descripcion']}">
<meta property="og:image" content="https://laora.es{IMG}/lunar-portada-ancha.webp">
<meta property="og:locale" content="es_ES">
<meta name="theme-color" content="#0a0a0a">
<title>Lunar · laOra</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400&display=swap" rel="stylesheet">
<!-- GENERADO por herramientas/generar_v2.py — no editar a mano.
     Esta página es el rediseño para el móvil y no comparte NADA con el
     resto del sitio: ni hoja de estilo ni script. Se puede romper sin
     tocar lo que está publicado. -->
<link rel="stylesheet" href="/assets/css/lunarv2.css?v={V_CSS}">
</head>
<body>
{CABECERA}
<main>
{HERO}
{GOLPE}
{PLANO}
{''.join(razon(r) for r in RAZONES)}
{TABLA}
{GALERIA}
{ACORDEON}
{FILOSOFIA}
{PAQUETE}
{COMPRAR}
{FAQ}
</main>
{PIE}
<script src="/assets/js/lunarv2.js?v={V_JS}"></script>
</body>
</html>
"""

destino = os.path.join(RAIZ, 'lunarv2.html')
with open(destino, 'w', encoding='utf-8') as f:
    f.write(PAGINA)

pantallas = PAGINA.count('class="pantalla')
print(f'lunarv2.html escrito · {pantallas} pantallas · '
      f'desde {euros(DESDE)} hasta {euros(HASTA)}')
faltan = [r['titulo'] for r in RAZONES if not r['foto']]
print('fotos que faltan en «las razones»:', ', '.join(faltan))
