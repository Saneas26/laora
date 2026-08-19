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
     El primero es el rótulo; el segundo, el color. Y `nota` explica lo
     que toca esperar, que es lo que de verdad quiere saber quien
     acaba de comprar. */
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
      return 'Entregado. Tu garantía echa a andar ese día.';
    }
    return '';
  }

  /* ---------- 01. mi colección ----------
     El reloj FÍSICO, con su número de serie y su garantía. Es lo que
     promete el Club y lo que convierte una compra en una propiedad. */
  function relojHtml(r) {
    var g = (r.garantias || [])[0];
    var vigente = g && g.hasta && new Date(g.hasta) >= new Date();
    var intervenciones = r.intervenciones || [];

    return '<li class="cu-ficha">' +
      '<div class="cu-ficha-alto"><span class="cu-titulo">' + esc(r.modelo) + '</span>' +
      (r.entregado_en ? '<span class="cu-fecha">Tuyo desde el ' + esc(fecha(r.entregado_en)) + '</span>' : '') +
      '</div>' +
      '<p class="cu-serie">Nº ' + esc(r.numero_serie) + ' · Ref. ' + esc(r.ref) + '</p>' +
      '<p class="cu-detalle">' + esc(r.acabado) + (r.correa ? '<br>' + esc(r.correa) : '') + '</p>' +
      (g
        ? '<span class="cu-estado ' + (vigente ? 'es-bien' : '') + '">' +
          (vigente ? 'Garantía activa hasta el ' + esc(fecha(g.hasta))
                   : 'Garantía terminada el ' + esc(fecha(g.hasta))) + '</span>'
        : '') +
      (intervenciones.length
        ? '<ul class="cu-relojes">' + intervenciones.map(function (i) {
            return '<li><b>' + esc(fecha(i.fecha)) + '</b> — ' + esc(i.descripcion) +
              '<small>' + esc(i.tipo) + (i.en_garantia ? ' · en garantía' : '') + '</small></li>';
          }).join('') + '</ul>'
        : '') +
      '</li>';
  }

  /* ---------- 02. mis pedidos ---------- */
  function pedidoHtml(p) {
    var e = ESTADOS[p.estado] || [p.estado, ''];
    var relojes = (p.pedido_lineas || []).map(function (l) {
      return '<li><b>' + esc(l.modelo) + '</b>' +
        (l.cantidad > 1 ? ' × ' + l.cantidad : '') +
        ' — ' + euros(Number(l.precio) * Number(l.cantidad)) +
        '<small>' + esc(l.acabado) + '<br>' + esc(l.correa) + '</small></li>';
    }).join('');

    var nota = notaDe(p);

    return '<li class="cu-ficha">' +
      '<div class="cu-ficha-alto">' +
        '<span class="cu-titulo">Pedido ' + esc(p.numero) + '</span>' +
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
      /* «Tu factura, siempre a mano» decía el Club. Ahora es verdad. */
      (p.factura_numero
        ? '<button type="button" class="cu-factura" data-factura="' + esc(p.numero) + '">' +
          'Ver mi factura ' + esc(p.factura_numero) + '</button>'
        : '') +
      '</li>';
  }

  /* ---------- 03. el taller ---------- */
  function pintarHilo(mensajes) {
    var hilo = document.querySelector('[data-hilo]');
    document.querySelector('[data-hilo-vacio]').hidden = !!(mensajes && mensajes.length);
    hilo.innerHTML = (mensajes || []).map(function (m) {
      return '<li class="' + (m.autor === 'socio' ? 'de-socio' : 'de-laora') + '">' +
        esc(m.texto).replace(/\n/g, '<br>') +
        '<time>' + esc(fecha(m.creado_en)) + '</time></li>';
    }).join('');
  }

  function cargarHilo() {
    return laoraSesion.consultar('mensajes?select=*&order=creado_en.asc')
      .then(pintarHilo);
  }

  /* ---------- 04. sus datos ---------- */
  var CAMPOS = ['nombre', 'apellidos', 'telefono', 'nif', 'direccion', 'cp', 'poblacion',
                'provincia', 'pais', 'muneca_cm', 'cumple_dia', 'cumple_mes',
                'nos_conocio', 'quiere_avisos'];

  function ponerDatos(socio) {
    if (!socio) return;
    CAMPOS.forEach(function (k) {
      var i = document.querySelector('[data-d="' + k + '"]');
      if (!i) return;
      if (i.type === 'checkbox') i.checked = !!socio[k];
      else if (socio[k] !== null && socio[k] !== undefined) i.value = socio[k];
    });
    /* En cuanto sabemos su nombre, se le llama por él y el correo se
       retira: ya no hace falta decirle con qué cuenta ha entrado
       cuando le estamos saludando por su nombre. Mientras no lo
       sepamos, el correo se queda: es lo único que le identifica. */
    var hola = document.querySelector('[data-hola]');
    var correo = document.querySelector('[data-correo-dentro]');
    if (socio.nombre) {
      if (hola) hola.textContent = 'Hola, ' + socio.nombre;
      if (correo) correo.hidden = true;
    } else {
      if (hola) hola.textContent = 'Hola';
      if (correo) correo.hidden = false;
    }
  }

  var formGuardar = document.querySelector('[data-form-datos]');
  var avisoDatos = document.querySelector('[data-aviso-datos]');

  function decirDatos(t, malo) {
    if (!avisoDatos) return;
    avisoDatos.textContent = t || '';
    avisoDatos.hidden = !t;
    avisoDatos.classList.toggle('cu-error', !!malo);
  }

  if (formGuardar) {
    formGuardar.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var b = formGuardar.querySelector('[data-guardar]');
      b.disabled = true;
      decirDatos('Guardando…');

      var cambios = {};
      CAMPOS.forEach(function (k) {
        var i = document.querySelector('[data-d="' + k + '"]');
        if (!i) return;
        if (i.type === 'checkbox') { cambios[k] = i.checked; return; }
        var v = (i.value || '').trim();
        /* Vacío es NULL, no cadena vacía: un número vacío rompería la
           columna, y un texto vacío ensucia la ficha. */
        cambios[k] = v === '' ? null : (i.type === 'number' ? Number(v.replace(',', '.')) : v);
      });
      /* Se anota CUÁNDO dijo que sí a los avisos: si algún día alguien
         pregunta por qué le escribimos, la respuesta está aquí. */
      if (cambios.quiere_avisos) cambios.avisos_desde = new Date().toISOString();
      cambios.actualizado_en = new Date().toISOString();

      laoraSesion.escribir('socios?id=eq.' + SOCIO.id, {
        method: 'PATCH',
        body: JSON.stringify(cambios)
      }).then(function () {
        b.disabled = false;
        decirDatos('Guardado. Gracias.');
        ponerDatos(Object.assign(SOCIO, cambios));
      }).catch(function () {
        b.disabled = false;
        decirDatos('No hemos podido guardarlo. Inténtalo en un momento.', true);
      });
    });
  }

  /* ---------- escribir al taller ---------- */
  var formMensaje = document.querySelector('[data-form-mensaje]');
  var avisoMensaje = document.querySelector('[data-aviso-mensaje]');

  if (formMensaje) {
    formMensaje.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var caja = formMensaje.querySelector('[data-mensaje]');
      var texto = (caja.value || '').trim();
      if (!texto) return;

      var b = formMensaje.querySelector('[data-enviar-mensaje]');
      b.disabled = true;

      laoraSesion.escribir('mensajes', {
        method: 'POST',
        body: JSON.stringify({ socio_id: SOCIO.id, autor: 'socio', texto: texto })
      }).then(function () {
        caja.value = '';
        b.disabled = false;
        avisoMensaje.hidden = false;
        avisoMensaje.classList.remove('cu-error');
        avisoMensaje.textContent = 'Enviado. Te contestamos por aquí y te avisamos por correo.';
        return cargarHilo();
      }).catch(function () {
        b.disabled = false;
        avisoMensaje.hidden = false;
        avisoMensaje.classList.add('cu-error');
        avisoMensaje.textContent = 'No hemos podido enviarlo. Inténtalo en un momento.';
      });
    });
  }

  /* ---------- el Club ----------
     La ley da 3 años de garantía a cualquiera. El Club los sube a 5, y
     va incluido con el reloj: se es socio desde que se paga el primero.
     Se dice solo cuando ya es verdad; prometerlo antes sería vender
     humo en su propia cuenta. */
  function pintarClub(socio) {
    var caja = document.querySelector('[data-club]');
    if (!caja || !socio || !socio.club_desde) return;
    caja.innerHTML = 'Eres <b>socio del Club laOra</b> desde el ' + esc(fecha(socio.club_desde)) +
      '. Por eso tu garantía es de <b>5 años</b> y no de los 3 que da la ley.';
    caja.hidden = false;
  }

  /* ---------- abrir la cuenta ---------- */
  var SOCIO = {};
  var PEDIDOS = [];

  function abrirDentro(usuario) {
    puerta.hidden = true;
    dentro.hidden = false;
    document.querySelector('[data-correo-dentro]').textContent = usuario.email || '';
    SOCIO.id = usuario.id;

    Promise.all([
      laoraSesion.consultar('socios?select=*&limit=1'),
      laoraSesion.consultar('pedidos?select=*,pedido_lineas(*)&order=creado_en.desc'),
      laoraSesion.consultar('relojes?select=*,garantias(*),intervenciones(*)&order=creado_en.desc'),
      cargarHilo()
    ]).then(function (r) {
      document.querySelector('[data-cargando]').hidden = true;

      var socio = (r[0] || [])[0];
      if (socio) { SOCIO = socio; ponerDatos(socio); pintarClub(socio); }

      var pedidos = r[1] || [];
      PEDIDOS = pedidos;
      var relojes = r[2] || [];

      if (relojes.length) {
        document.querySelector('[data-bloque-relojes]').hidden = false;
        document.querySelector('[data-relojes]').innerHTML = relojes.map(relojHtml).join('');
      }
      if (pedidos.length) {
        document.querySelector('[data-bloque-pedidos]').hidden = false;
        document.querySelector('[data-pedidos]').innerHTML = pedidos.map(pedidoHtml).join('');
      }
      if (!relojes.length && !pedidos.length) {
        document.querySelector('[data-sin-nada]').hidden = false;
      }
    }).catch(function () {
      document.querySelector('[data-cargando]').textContent =
        'No hemos podido abrir tu cuenta del todo. Vuelve a intentarlo en un momento.';
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

  /* La factura la dibuja `factura.js`, el MISMO documento que ve Óscar
     en su panel. El IVA se saca dividiendo, porque los precios de la
     web ya lo llevan dentro; multiplicar por 0,21 daría de menos. */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-factura]');
    if (!b) return;
    var pedido = (PEDIDOS || []).filter(function (p) { return p.numero === b.dataset.factura; })[0];
    if (!pedido) return;
    var total = Number(pedido.total);
    var ok = laoraFactura.abrir({
      pedido: pedido,
      base: Math.round((total / 1.21) * 100) / 100,
      iva: Math.round((total - total / 1.21) * 100) / 100,
      tipo_iva: 21
    });
    if (!ok) {
      b.textContent = 'Tu navegador ha bloqueado la ventana. Permítela y vuelve a pulsar.';
    }
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

  /* ---------- entrar con el código ----------
     El enlace se gasta al primer clic y solo sirve en el navegador que
     lo abre. Con el código se entra desde donde uno esté. */
  var formCodigo = document.querySelector('[data-form-codigo]');
  var avisoCodigo = document.querySelector('[data-aviso-codigo]');

  function decirCodigo(texto, malo) {
    if (!avisoCodigo) return;
    avisoCodigo.textContent = texto || '';
    avisoCodigo.hidden = !texto;
    avisoCodigo.classList.toggle('cu-error', !!malo);
  }

  if (formCodigo) {
    formCodigo.addEventListener('submit', function (e) {
      e.preventDefault();
      var correo = (campo.value || '').trim();
      var codigo = (formCodigo.querySelector('[data-codigo]').value || '').trim();
      if (!codigo) { decirCodigo('Escribe el código que te ha llegado.', true); return; }

      var b = formCodigo.querySelector('[data-entrar-codigo]');
      b.disabled = true;
      decirCodigo('Comprobando…');

      laoraSesion.entrarConCodigo(correo, codigo).then(function () {
        return laoraSesion.quienSoy();
      }).then(function (u) {
        if (!u) throw new Error('codigo');
        abrirDentro(u);
      }).catch(function () {
        b.disabled = false;
        decirCodigo('Ese código no vale. Comprueba que lo has copiado entero, ' +
                    'y que es el del último correo.', true);
      });
    });
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
