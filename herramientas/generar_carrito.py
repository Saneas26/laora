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

LOS TRES PASOS (06/08/2026)
------------------------------------------------------------
La cesta ya no manda a PayPal a pelo. Antes de cobrar hay que saber
QUIÉN compra y A DÓNDE va el reloj, así que la pantalla tiene tres
pasos, uno debajo de otro y sin cambiar de página:

  1. lo elegido, y su total
  2. entrar —con el enlace del correo, sin contraseña—
  3. los datos del envío
  4. el pago: tarjeta, Bizum, PayPal o Klarna en tres plazos

El pedido se escribe en la base ANTES de cobrar, con la Edge Function
`crear-pedido`, que recalcula el precio desde el catálogo y no se fía
del navegador. Solo después se abre el cobro, y lo abre `pagar-pedido`,
que crea el pago en Mollie leyendo el importe de la base.

Quien no haya entrado no pierde nada: la cesta vive en su navegador y
sigue ahí cuando vuelve del enlace del correo, porque el enlace le
devuelve a esta misma pantalla.

USO
    python3 herramientas/generar_carrito.py
"""

import os
import sys

# La cabecera es la MISMA en todas las páginas desde el 06/08/2026.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cabecera_laora import RECURSOS as CAB_RECURSOS, SCRIPT as CAB_SCRIPT, marcado as cabecera

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

V_CSS = 9
V_JS = 8

V2 = '/assets/img/lunar-v2'
LOGO = V2 + '/laora-wordmark-dark.png'


def campo(nombre, etiqueta, tipo='text', ancho='', extra=''):
    """Un campo del formulario. `ancho` = clase de rejilla."""
    return (f'<label class="ca-campo {ancho}">'
            f'<span>{etiqueta}</span>'
            f'<input type="{tipo}" name="{nombre}" data-c="{nombre}" {extra}>'
            f'</label>')


ENVIO = ''.join([
    campo('nombre', 'Nombre', extra='required autocomplete="given-name"'),
    campo('apellidos', 'Apellidos', extra='autocomplete="family-name"'),
    campo('telefono', 'Teléfono', 'tel', extra='autocomplete="tel"'),
    campo('direccion', 'Dirección', ancho='ca-ancho', extra='required autocomplete="street-address"'),
    campo('cp', 'Código postal', extra='required autocomplete="postal-code" inputmode="numeric"'),
    campo('poblacion', 'Población', extra='required autocomplete="address-level2"'),
    campo('provincia', 'Provincia', extra='required autocomplete="address-level1"'),
    campo('pais', 'País', extra='autocomplete="country-name" value="España"'),
])

FACTURA = ''.join([
    campo('fac_nombre', 'Nombre o razón social', ancho='ca-ancho'),
    campo('fac_nif', 'NIF o CIF'),
    campo('fac_direccion', 'Dirección fiscal', ancho='ca-ancho'),
    campo('fac_cp', 'Código postal'),
    campo('fac_poblacion', 'Población'),
    campo('fac_provincia', 'Provincia'),
])

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
{CAB_RECURSOS}
<link rel="stylesheet" href="/assets/css/carrito.css?v={V_CSS}">
</head>
<body>

{cabecera()}

<!-- El título de la pantalla, debajo de la cabecera común. Antes la
     cabecera de esta página era distinta a la del resto del sitio;
     ahora es la misma y aquí solo queda lo que es de aquí. -->
<p class="ca-titulo">Tu carrito</p>

<main class="ca-cuerpo">
  <!-- Las líneas las pinta `carrito.js` con lo que haya en la cesta.
       Sin JavaScript no hay cesta que enseñar, así que el aviso de
       abajo es lo que se ve, y es cierto. -->
  <ol class="ca-lineas" data-lineas></ol>

  <p class="ca-vacio" data-vacio hidden>
    Todavía no has elegido nada.
    <a href="/coleccion.html">Ver la colección →</a>
  </p>

  <aside class="ca-resumen" data-resumen hidden>
    <div class="ca-suma">
      <span>Total</span>
      <strong data-total>—</strong>
    </div>
    <p class="ca-impuestos">Impuestos y envío incluidos.</p>
    <button class="ca-pagar" type="button" data-continuar>Continuar</button>
  </aside>

  <!-- ---------- paso 2: entrar ---------- -->
  <section class="ca-paso" data-paso-entrar hidden>
    <h2>Antes de nada, entra</h2>
    <p class="ca-explica">Sin contraseña: pones tu correo, te llega un enlace y vuelves aquí
      con todo lo que has elegido. Hace falta para saber de quién es el pedido y para que
      luego puedas ver tu compra, tu factura y tu garantía.</p>
    <form class="ca-form" data-form-entrar>
      <label class="ca-campo ca-ancho">
        <span>Tu correo</span>
        <input type="email" data-correo required autocomplete="email" placeholder="tucorreo@ejemplo.com">
      </label>
      <button class="ca-pagar" type="submit" data-enviar-enlace>Enviarme el enlace</button>
    </form>
    <p class="ca-aviso-paso" data-aviso-entrar hidden></p>
  </section>

  <!-- ---------- paso 3: a dónde va ---------- -->
  <section class="ca-paso" data-paso-datos hidden>
    <h2>¿A dónde te lo enviamos?</h2>
    <p class="ca-explica" data-quien></p>
    <form class="ca-form" data-form-datos>
      {ENVIO}
      <label class="ca-check ca-ancho">
        <input type="checkbox" data-quiere-factura>
        <span>Necesito factura a otros datos</span>
      </label>
      <div class="ca-factura ca-ancho" data-bloque-factura hidden>
        {FACTURA}
      </div>
      <button class="ca-pagar ca-ancho" type="submit" data-hacer-pedido>Hacer el pedido</button>
    </form>
    <p class="ca-aviso-paso" data-aviso-datos hidden></p>
  </section>

  <!-- ---------- paso 4: pagar ----------
       Desde el 19/08/2026 cobra Mollie, no un enlace de PayPal. Dos
       caminos: tarjeta o transferencia, y Klarna en tres plazos.
       Klarna va aparte a propósito: si saliera mezclado con los demás
       se cobraría al comprar, y con Klarna hay que cobrar al enviar.
       Klarna no cobra al comprar: autoriza, y el dinero se cobra
       cuando el reloj sale. Aquí se dice, porque es lo que pasa. -->
  <section class="ca-paso ca-hecho" data-paso-pagar hidden>
    <h2>Tu pedido <b data-numero></b></h2>
    <p class="ca-explica">Ya está guardado y lo tenemos apuntado. Solo queda el pago:
      elige cómo quieres pagarlo. Con tarjeta o con Klarna te llevamos a la pasarela de
      Mollie, y nosotros no vemos ni guardamos los datos de tu tarjeta en ningún momento.</p>
    <p class="ca-total-final">A pagar: <b data-total-final></b></p>

    <div class="ca-metodos" data-metodos>
      <button type="button" data-metodo="" aria-pressed="true">
        <b>Tarjeta o transferencia</b>
        <small>Con tarjeta, al momento</small>
      </button>
      <button type="button" data-metodo="klarna" aria-pressed="false">
        <b>Klarna, en 3 plazos</b>
        <small>3 pagos de <span data-plazo>—</span>, sin intereses (0&nbsp;% TAE)</small>
      </button>
      <button type="button" data-metodo="bizum" aria-pressed="false">
        <b>Bizum o PayPal</b>
        <small>Te damos los datos y lo confirmamos a mano</small>
      </button>
    </div>

    <!-- Los que no pasan por la pasarela. Los datos los pone el
         servidor al pulsar: no están en esta página. -->
    <div class="ca-manual" data-manual hidden>
      <p class="ca-manual-que">Haz un <b>Bizum de <span data-manual-importe></span></b> al número</p>
      <p class="ca-manual-numero" data-manual-bizum></p>
      <p class="ca-manual-que">poniendo <b data-manual-concepto></b> en el concepto,
        <button type="button" class="ca-copiar" data-copiar>copiar</button></p>
      <p class="ca-manual-o">o si lo prefieres,
        <a data-manual-paypal href="#" target="_blank" rel="noopener">paga con PayPal →</a></p>
      <p class="ca-manual-fin">En cuanto veamos el ingreso te lo confirmamos por correo,
        normalmente el mismo día. Tu pedido está guardado y no se pierde.</p>
    </div>

    <button class="ca-pagar" type="button" data-pagar>Pagar <span data-total-boton></span></button>
    <p class="ca-aviso-paso" data-aviso-pagar hidden></p>

    <!-- Klarna exige que el cliente vea su aviso ANTES de pagar -->
    <p class="ca-legal-pago">Si pagas a plazos con Klarna, es Klarna quien te concede el aplazamiento y
      quien trata tus datos para ello. Lee su
      <a href="https://www.klarna.com/es/legal/" target="_blank" rel="noopener">aviso de privacidad</a>
      antes de pagar. Con Klarna el primer plazo se cobra cuando tu reloj sale hacia tu casa.</p>

    <p class="ca-explica">En cuanto el pago se confirme te avisamos por correo. Puedes ver el pedido
      en <a href="/cuenta">tu cuenta</a> cuando quieras.</p>
  </section>
</main>

<footer class="ca-aviso">
  <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
</footer>

{CAB_SCRIPT}
<script src="/assets/js/sesion.js?v={V_JS}"></script>
<script src="/assets/js/carrito.js?v={V_JS}"></script>
<script src="/assets/js/carrito-pantalla.js?v={V_JS}"></script>
</body>
</html>
"""

with open(os.path.join(RAIZ, 'carrito.html'), 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print('carrito.html escrito')
