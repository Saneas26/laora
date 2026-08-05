#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LA PANTALLA DEL CARRITO
============================================================
Escribe `carrito.html`. Óscar, 05/08/2026: «al pulsar reservar, que
lleve a la pantalla del carrito, donde solo hay eso: el carrito con los
artículos elegidos para pagar».

Así que aquí no hay portada, ni actos, ni recomendaciones, ni «también
te puede interesar». Solo lo que has elegido, lo que suma y el botón de
seguir.

LO QUE SE RECUPERA
------------------------------------------------------------
`assets/js/carrito.js` es el de la web anterior, tal cual, sacado de la
etiqueta `web-v1-antes-del-rediseno`. Guarda la cesta en el propio
navegador —`localStorage`—, así que no hace falta cuenta ni servidor
para que funcione, y ya trae el contador de la bolsa. Lo único que hay
que darle es una línea con `ref`, `nombre`, `acabado`, `precio` y la
foto.

LO QUE NO EXISTE TODAVÍA
------------------------------------------------------------
El cobro. El botón de abajo lleva a `/pagar.html`, que está en la
etiqueta pero con el diseño viejo y con la clave de Mollie sin poner.
Mientras no exista, el botón se pinta desactivado y lo dice: es
preferible a mandar a nadie a un 404 desde el paso de pagar.

USO
    python3 herramientas/generar_carrito.py
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

V_CSS = 1
V_JS = 1

V2 = '/assets/img/lunar-v2'
LOGO = V2 + '/laora-wordmark-dark.png'

PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Tu carrito en laOra.">
<meta name="robots" content="noindex, nofollow">
<title>Tu carrito · laOra</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400&display=swap" rel="stylesheet">
<!-- GENERADO por herramientas/generar_carrito.py — no editar a mano. -->
<link rel="stylesheet" href="/assets/css/carrito.css?v={V_CSS}">
</head>
<body>

<header class="ca-cab">
  <a class="ca-marca" href="/" aria-label="laOra, inicio"><img src="{LOGO}" alt="laOra"></a>
  <p class="ca-titulo">Tu carrito</p>
  <a class="ca-seguir" href="/">Seguir mirando</a>
</header>

<main class="ca-cuerpo">
  <!-- Las líneas las pinta `carrito.js` con lo que haya en la cesta.
       Sin JavaScript no hay cesta que enseñar, así que el aviso de
       abajo es lo que se ve, y es cierto. -->
  <ol class="ca-lineas" data-lineas></ol>

  <p class="ca-vacio" data-vacio hidden>
    Todavía no has elegido nada.
    <a href="/lunarv2c">Configura tu Lunar →</a>
  </p>

  <aside class="ca-resumen" data-resumen hidden>
    <div class="ca-suma">
      <span>Total</span>
      <strong data-total>—</strong>
    </div>
    <p class="ca-impuestos">Impuestos incluidos. El envío se calcula en el siguiente paso.</p>
    <button class="ca-pagar" type="button" data-pagar disabled>Pagar</button>
    <p class="ca-pendiente">El pago todavía no está abierto. Guarda tu configuración: la cesta se queda en este navegador.</p>
  </aside>
</main>

<footer class="ca-aviso">
  <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
</footer>

<script src="/assets/js/carrito.js?v={V_JS}"></script>
<script src="/assets/js/carrito-pantalla.js?v={V_JS}"></script>
</body>
</html>
"""

with open(os.path.join(RAIZ, 'carrito.html'), 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print('carrito.html escrito')
