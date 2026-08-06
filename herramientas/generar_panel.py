#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
laOra · EL PANEL DE ÓSCAR
============================================================
Escribe `panel.html`. Mismo modelo que el panel de Saneas, a
propósito: una página estática **sin ninguna clave dentro** que solo
sabe hablar con la Edge Function `panel-laora`. La contraseña se
escribe al entrar y no se guarda en ningún sitio salvo la pestaña
abierta (`sessionStorage`): al cerrarla, fuera.

Por qué así: el panel tiene que ver los pedidos de TODO el mundo, y
eso es justo lo que las políticas de filas impiden. Quien lo salta es
el service role, y esa llave no puede estar en un navegador. Así que
vive en la función y aquí no hay nada que robar.

CUATRO PANTALLAS
  · Resumen — cuánto hay de todo, de un vistazo
  · Pedidos — los que entran, cobrarlos, enviarlos, y el número de
    serie de cada reloj con su garantía
  · Socios  — quién es quién, sus compras, sus relojes y sus notas
  · Comentarios — la conversación privada y las valoraciones que
    esperan tu visto bueno

USO
    python3 herramientas/generar_panel.py
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

V_CSS = 1
V_JS = 1

LOGO = '/assets/img/lunar-v2/laora-wordmark-dark.png'

PAGINA = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>Panel · laOra</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<!-- GENERADO por herramientas/generar_panel.py — no editar a mano.
     Aquí NO hay ninguna clave: todo pasa por la Edge Function. -->
<link rel="stylesheet" href="/assets/css/panel.css?v={V_CSS}">
</head>
<body>

<!-- ---------- entrar ---------- -->
<section class="pa-puerta" data-puerta>
  <img class="pa-logo" src="{LOGO}" alt="laOra">
  <h1>Panel</h1>
  <form data-form-entrar>
    <label>
      <span>Contraseña</span>
      <input type="password" data-clave autocomplete="current-password" required autofocus>
    </label>
    <button type="submit">Entrar</button>
  </form>
  <p class="pa-mal" data-error-entrar hidden></p>
</section>

<!-- ---------- el panel ---------- -->
<div class="pa-todo" data-todo hidden>

  <header class="pa-cab">
    <img class="pa-logo-cab" src="{LOGO}" alt="laOra">
    <nav class="pa-nav">
      <button type="button" class="pa-tab" data-ir="resumen">Resumen</button>
      <button type="button" class="pa-tab" data-ir="pedidos">Pedidos<b data-chip-pedidos hidden></b></button>
      <button type="button" class="pa-tab" data-ir="socios">Socios</button>
      <button type="button" class="pa-tab" data-ir="comentarios">Comentarios<b data-chip-comentarios hidden></b></button>
    </nav>
    <button type="button" class="pa-salir" data-salir>Salir</button>
  </header>

  <main class="pa-cuerpo">

    <section class="pa-pantalla" data-pantalla="resumen">
      <div class="pa-tarjetas" data-resumen></div>
    </section>

    <section class="pa-pantalla" data-pantalla="pedidos" hidden>
      <div class="pa-filtros" data-filtros-pedidos>
        <button type="button" class="pa-filtro pa-activo" data-estado="todos">Todos</button>
        <button type="button" class="pa-filtro" data-estado="solicitado">Sin cobrar</button>
        <button type="button" class="pa-filtro" data-estado="pagado">Cobrados</button>
        <button type="button" class="pa-filtro" data-estado="preparando">Preparando</button>
        <button type="button" class="pa-filtro" data-estado="enviado">Enviados</button>
        <button type="button" class="pa-filtro" data-estado="entregado">Entregados</button>
      </div>
      <div data-lista-pedidos></div>
    </section>

    <section class="pa-pantalla" data-pantalla="socios" hidden>
      <div data-lista-socios></div>
    </section>

    <section class="pa-pantalla" data-pantalla="comentarios" hidden>
      <h2 class="pa-titulo2">La conversación</h2>
      <div data-lista-mensajes></div>
      <h2 class="pa-titulo2">Valoraciones</h2>
      <div class="pa-filtros" data-filtros-valoraciones>
        <button type="button" class="pa-filtro pa-activo" data-vestado="pendiente">Esperando</button>
        <button type="button" class="pa-filtro" data-vestado="publicada">Publicadas</button>
        <button type="button" class="pa-filtro" data-vestado="rechazada">Rechazadas</button>
        <button type="button" class="pa-filtro" data-vestado="todas">Todas</button>
      </div>
      <div data-lista-valoraciones></div>
    </section>

  </main>
</div>

<!-- la ficha, encima de todo -->
<div class="pa-manto" data-manto hidden>
  <div class="pa-ficha" role="dialog" aria-modal="true">
    <button type="button" class="pa-cerrar" data-cerrar aria-label="Cerrar">✕</button>
    <div data-ficha></div>
  </div>
</div>

<p class="pa-aviso" data-aviso hidden></p>

<script src="/assets/js/panel.js?v={V_JS}"></script>
</body>
</html>
"""

with open(os.path.join(RAIZ, 'panel.html'), 'w', encoding='utf-8') as f:
    f.write(PAGINA)

print('panel.html escrito')
