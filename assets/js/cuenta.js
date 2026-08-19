/* ============================================================
   laOra · CUENTA Y CLUB
   ------------------------------------------------------------
   Entrar sin contraseña: se pone el correo, llega un enlace y se
   entra. No se guarda ninguna contraseña, así que no hay ninguna que
   se pueda perder ni que haya que custodiar.

   LO QUE FALTABA HASTA EL 19/08/2026
   Esta página solo sabía pedir el correo. Quien entraba con su enlace
   volvía aquí y se encontraba OTRA VEZ el mismo formulario, como si no
   tuviera cuenta; y la lista de «qué hay dentro» prometía la factura,
   la garantía y el historial de un sitio que no existía. Ahora, si hay
   sesión, se entra directo a los pedidos.

   La sesión la lleva `sesion.js`, que es el mismo que usa el carrito:
   sabe renovar el token cuando caduca, cosa que aquí no se hacía.
   ============================================================ */
(function () {
  'use strict';

  var form = document.querySelector('[data-form]');
  var campo = document.querySelector('[data-correo]');
  var boton = document.querySelector('[data-enviar]');
  var aviso = document.querySelector('[data-aviso]');
  var hecho = document.querySelector('[data-hecho]');
  var puerta = document.querySelector('[data-puerta]');
  var dentro = document.querySelector('[data-dentro]');
  if (!form) return;

  function decir(texto, malo) {
    aviso.textContent = texto;
    aviso.hidden = !texto;
    aviso.classList.toggle('cu-error', !!malo);
  }

  var esc = function (s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  };

  function euros(v) {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency', currency: 'EUR', minimumFractionDigits: 2
    }).format(Number(v) || 0);
  }

  function fecha(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString('es-ES',
      { day: 'numeric', month: 'long', year: 'numeric' });
  }

  /* ---------- lo que se le dice a cada estado ----------
     El de la izquierda es el rótulo; el de la derecha, el color. Y
     `nota` explica lo que toca esperar, que es lo que de verdad quiere
     saber quien acaba de comprar. */
  var ESTADOS = {
    solicitado:  ['A la espera de pago', 'es-espera'],
    autorizado:  ['Aprobado por Klarna', 'es-espera'],
    pagado:      ['Pagado', 'es-bien'],
    preparando:  ['Preparándose', 'es-bien'],
    enviado:     ['En camino', 'es-camino'],
    entregado:   ['Entregado', 'es-bien'],
    cancelado:   ['Cancelado', ''],
    devuelto:    ['Devuelto', '']
  };

  function notaDe(p) {
    if (p.estado === 'solicitado') {
      return 'Tu pedido está guardado, pero todavía no nos consta el pago. ' +
             'Puedes terminarlo cuando quieras.';
    }
    if (p.estado === 'autorizado') {
      return 'Klarna ha aprobado tu pago a plazos. <b>El primer plazo no se te cobra ' +
             'hasta que tu reloj salga hacia tu casa</b>.';
    }
    if (p.estado === 'pagado' || p.estado === 'preparando') {
      return 'Lo estamos preparando. Te escribimos en cuanto salga, con su seguimiento.';
    }
    if (p.estado === 'enviado') {
      var s = 'Ya va de camino.';
      if (p.transportista) s += ' Lo lleva <b>' + esc(p.transportista) + '</b>.';
      if (p.seguimiento) s += ' Seguimiento: <b>' + esc(p.seguimiento) + '</b>.';
      return s;
    }
    if (p.estado === 'entregado') {
      return 'Entregado. Tu garantía de 3 años cuenta desde ese día.';
    }
    return '';
  }

  /* ---------- pintar un pedido ---------- */
  function pedidoHtml(p) {
    var e = ESTADOS[p.estado] || [p.estado, ''];
    var relojes = (p.pedido_lineas || []).map(function (l) {
      return '<li><b>' + esc(l.modelo) + '</b>' +
        (l.cantidad > 1 ? ' × ' + l.cantidad : '') +
        ' — ' + euros(Number(l.precio) * Number(l.cantidad)) +
        '<small>' + esc(l.acabado) + '<br>' + esc(l.correa) + '</small></li>';
    }).join('');

    var nota = notaDe(p);

    return '<li class="cu-pedido">' +
      '<div class="cu-pedido-alto">' +
        '<span class="cu-numero">Pedido ' + esc(p.numero) + '</span>' +
        '<span class="cu-fecha">' + esc(fecha(p.creado_en)) + '</span>' +
      '</div>' +
      '<span class="cu-estado ' + e[1] + '">' + esc(e[0]) + '</span>' +
      '<ul class="cu-relojes">' + relojes + '</ul>' +
      '<p class="cu-total"><span>Total</span><span>' + euros(p.total) + '</span></p>' +
      (nota ? '<p class="cu-nota">' + nota + '</p>' : '') +
      (p.estado === 'solicitado'
        ? '<button type="button" class="cu-pagar" data-pagar="' + esc(p.numero) + '">' +
          'Pagar ' + euros(p.total) + '</button>'
        : '') +
      '</li>';
  }

  /* ---------- dentro ---------- */
  function abrirDentro(usuario) {
    puerta.hidden = true;
    dentro.hidden = false;
    document.querySelector('[data-correo-dentro]').textContent = usuario.email || '';

    laoraSesion.consultar('pedidos?select=*,pedido_lineas(*)&order=creado_en.desc')
      .then(function (pedidos) {
        document.querySelector('[data-cargando]').hidden = true;
        if (!pedidos || !pedidos.length) {
          document.querySelector('[data-sin-nada]').hidden = false;
          return;
        }
        document.querySelector('[data-pedidos]').innerHTML = pedidos.map(pedidoHtml).join('');
      })
      .catch(function () {
        document.querySelector('[data-cargando]').textContent =
          'No hemos podido cargar tus pedidos. Vuelve a intentarlo en un momento.';
      });
  }

  /* Terminar de pagar un pedido que se quedó a medias: es el mismo
     camino del carrito, y el servidor devuelve el checkout que ya
     estuviera abierto en vez de crear otro. */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-pagar]');
    if (!b) return;
    b.disabled = true;
    b.textContent = 'Abriendo el pago…';

    laoraSesion.token().then(function (t) {
      if (!t) throw new Error('sin sesión');
      return fetch(laoraSesion.URL + '/functions/v1/pagar-pedido', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + t },
        body: JSON.stringify({ numero: b.dataset.pagar, metodo: '' })
      });
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (d && d.url) { window.location.href = d.url; return; }
      throw new Error((d && d.error) || 'no se pudo abrir el pago');
    }).catch(function (err) {
      b.disabled = false;
      b.textContent = String(err && err.message || 'No se ha podido abrir el pago');
    });
  });

  document.querySelector('[data-salir]').addEventListener('click', function () {
    laoraSesion.salir();
    window.location.href = '/cuenta';
  });

  /* ---------- de vuelta de la pasarela ----------
     Mollie devuelve aquí con `?pedido=` cuando el pago termina. No se
     dice «pagado»: quien lo confirma es el webhook, no esta vuelta. */
  var deLaPasarela = location.search.match(/[?&]pedido=([^&]+)/);
  if (deLaPasarela) {
    try { localStorage.removeItem('laora.pedido'); } catch (e) {}
    history.replaceState(null, '', location.pathname);
  }

  /* ---------- ¿quién eres? ----------
     Se recoge la sesión si viene del enlace del correo y, haya venido
     o no, se comprueba si ya hay una. Solo se enseña la puerta a quien
     de verdad está fuera. */
  var acabaDeEntrar = laoraSesion.recoger();

  if (laoraSesion.hay()) {
    laoraSesion.quienSoy().then(function (u) {
      if (u) { abrirDentro(u); return; }
      /* Había sesión, pero ya no vale. Se borra y se pide el correo,
         que es preferible a una pantalla vacía sin explicación. */
      laoraSesion.salir();
      if (acabaDeEntrar) decir('Tu enlace ha caducado. Pide otro y entras.', true);
    });
  } else if (location.hash.indexOf('error') >= 0) {
    /* Supabase manda el motivo en inglés. Aquí se dice en español y,
       sobre todo, se dice QUÉ HACER: casi siempre es que el enlace ya
       se había usado, porque solo vale una vez. */
    var codigo = (location.hash.match(/error_code=([^&]*)/) || [])[1] || '';
    decir(codigo === 'otp_expired'
      ? 'Ese enlace ya no sirve: caducan al poco rato y solo se pueden usar una vez. ' +
        'Pide otro aquí abajo y entras.'
      : 'El enlace no ha funcionado. Pide otro aquí abajo y entras.', true);
    history.replaceState(null, '', location.pathname);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var correo = (campo.value || '').trim();
    if (!correo || correo.indexOf('@') < 1) { decir('Escribe un correo válido.', true); return; }

    boton.disabled = true;
    decir('Enviando…');

    laoraSesion.pedirEnlace(correo, '/cuenta').then(function () {
      form.hidden = true;
      hecho.hidden = false;
      hecho.querySelector('[data-hecho-texto]').textContent =
        'Te hemos enviado un enlace a ' + correo + '. Ábrelo desde este mismo dispositivo ' +
        'y entrarás sin contraseña.';
    }).catch(function () {
      boton.disabled = false;
      decir('No hemos podido enviar el enlace. Inténtalo dentro de un momento.', true);
    });
  });
})();
