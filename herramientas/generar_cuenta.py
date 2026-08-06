#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · LA PANTALLA DE LA CUENTA
============================================================
Escribe `cuenta.html`. Óscar, 05/08/2026: crear cuenta de usuario y
socio del Club laOra.

CÓMO SE ENTRA
------------------------------------------------------------
Con el correo y nada más. Se pone la dirección, llega un enlace y se
entra. Sin contraseña: no la pide, no la guarda y no hay ninguna que
recuperar ni que custodiar. Lo eligió Óscar el 05/08/2026.

Es la misma pantalla para entrar y para darse de alta a propósito:
quien vuelve y quien llega por primera vez escriben lo mismo, y no hay
que adivinar de antemano si ya se tiene cuenta.

EL REMITENTE
------------------------------------------------------------
Los correos salen desde el dominio que ya está verificado —el de
Saneas— con el nombre visible «laOra», que es lo que ve el cliente en
su bandeja. Añadir `laora.es` como segundo dominio costaba 20 € al mes
y no aporta nada que el cliente note. El día que se quiera mover, es
una línea de configuración y nada de lo de aquí depende de eso.

LO QUE FALTA PARA QUE FUNCIONE
------------------------------------------------------------
Las dos claves públicas de Supabase en `assets/js/cuenta.js` —la URL
del proyecto y la `anon`—, que se sacan de Project Settings → API.
Mientras no estén, la pantalla se ve entera y lo dice al enviar, en vez
de fallar sin explicación.

USO
    python3 herramientas/generar_cuenta.py
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

V_CSS = 1
V_JS = 1
LOGO = '/assets/img/lunar-v2/laora-wordmark-dark.png'

VENTAJAS = [
    'Tu reloj registrado, con su referencia y su fecha de compra.',
    'La factura y la garantía, siempre a mano.',
    'El historial de cada revisión que pase por el taller.',
    'Aviso cuando toque mantenimiento.',
]

PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Entra en tu cuenta de laOra y en el Club laOra con tu correo, sin contraseña.">
<meta name="robots" content="noindex, nofollow">
<title>Tu cuenta · laOra</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<!-- GENERADO por herramientas/generar_cuenta.py — no editar a mano. -->
<link rel="stylesheet" href="/assets/css/cuenta.css?v={V_CSS}">
</head>
<body>

<header class="cu-cab">
  <a href="/" aria-label="laOra, inicio"><img src="{LOGO}" alt="laOra"></a>
  <a class="volver" href="/">Volver</a>
</header>

<main class="cu-cuerpo">
  <div class="cu-caja">
    <h1>Tu cuenta<br><em>y tu Club laOra.</em></h1>
    <p class="cu-entrada">Escribe tu correo y te enviamos un enlace para entrar. Sin contraseña: ni la pedimos ni la guardamos.</p>

    <form class="cu-form" data-form novalidate>
      <label for="correo">Tu correo</label>
      <input id="correo" name="correo" type="email" autocomplete="email"
             inputmode="email" placeholder="nombre@correo.es" required data-correo>
      <button class="cu-enviar" type="submit" data-enviar>Enviar el enlace</button>
      <p class="cu-aviso" data-aviso hidden></p>
    </form>

    <div class="cu-hecho" data-hecho hidden>
      <p data-hecho-texto></p>
    </div>

    <div class="cu-ventajas">
      <p>Qué hay dentro</p>
      <ul>
{''.join(f'        <li>{v}</li>' + chr(10) for v in VENTAJAS)}      </ul>
    </div>

    <p class="cu-legal">
      Solo guardamos tu correo y, cuando compres, los datos del pedido. No lo cedemos a nadie
      y puedes pedir que lo borremos cuando quieras. <a href="/privacidad.html">Cómo tratamos tus datos</a>.
    </p>
  </div>
</main>

<footer class="cu-aviso-marcas">
  <p>laOra es una marca independiente. No fabrica réplicas ni utiliza marcas, emblemas o logotipos ajenos. Las referencias a iconos relojeros se ofrecen únicamente como contexto del homenaje; no implican afiliación con sus fabricantes.</p>
</footer>

<script src="/assets/js/cuenta.js?v={V_JS}"></script>
</body>
</html>
"""

with open(os.path.join(RAIZ, 'cuenta.html'), 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print('cuenta.html escrito')
