/* ============================================================
   laOra · EL PANEL
   ------------------------------------------------------------
   Aquí no hay ninguna clave de la base. Todo pasa por la Edge
   Function `panel-laora`, que es la que tiene el service role. Lo
   único que viaja desde aquí es la contraseña que escribe Óscar, y
   solo vive en la pestaña abierta: al cerrarla, desaparece.

   Todas las llamadas son la misma: `api(accion, datos)`.
   ============================================================ */
(function () {
  'use strict';

  var FUNCION = 'https://uikanfvigunjhzibnhxf.supabase.co/functions/v1/panel-laora';
  var LLAVE = 'laora.panel';

  var puerta = document.querySelector('[data-puerta]');
  var todo = document.querySelector('[data-todo]');
  var manto = document.querySelector('[data-manto]');
  var fichaCaja = document.querySelector('[data-ficha]');
  var avisoCaja = document.querySelector('[data-aviso]');

  var CLAVE = '';
  var ESTADO_PEDIDOS = 'todos';
  var ESTADO_VALORACIONES = 'pendiente';

  /* ---------- utilidades ---------- */
  function api(accion, datos) {
    var cuerpo = Object.assign({ clave: CLAVE, accion: accion }, datos || {});
    return fetch(FUNCION, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cuerpo)
    }).then(function (r) {
      return r.json().then(function (d) {
        if (!r.ok || d.error) throw new Error(d.error || ('error ' + r.status));
        return d;
      });
    });
  }

  var temporizador;
  function avisar(texto, malo) {
    avisoCaja.textContent = texto;
    avisoCaja.hidden = false;
    avisoCaja.classList.toggle('pa-aviso-mal', !!malo);
    clearTimeout(temporizador);
    temporizador = setTimeout(function () { avisoCaja.hidden = true; }, malo ? 6000 : 3000);
  }

  function euros(v) {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(Number(v) || 0);
  }

  /* Todas las fechas del panel en hora de Madrid: es la que manda en
     la casa, y así no hay dos relojes distintos según quién mire. */
  function fecha(iso, conHora) {
    if (!iso) return '—';
    var o = { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Europe/Madrid' };
    if (conHora) { o.hour = '2-digit'; o.minute = '2-digit'; }
    return new Date(iso).toLocaleString('es-ES', o);
  }

  var esc = function (s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  };

  function nombreDe(s) {
    if (!s) return '(sin nombre)';
    var n = [s.nombre, s.apellidos].filter(Boolean).join(' ');
    return n || s.email || '(sin nombre)';
  }

  /* ---------- la puerta ---------- */
  var formEntrar = document.querySelector('[data-form-entrar]');
  var errorEntrar = document.querySelector('[data-error-entrar]');

  function abrir() {
    puerta.hidden = true;
    todo.hidden = false;
    ir('resumen');
  }

  formEntrar.addEventListener('submit', function (e) {
    e.preventDefault();
    CLAVE = document.querySelector('[data-clave]').value;
    errorEntrar.hidden = true;
    api('entrar').then(function () {
      /* En la pestaña, no en el disco: si alguien se deja el panel
         abierto, al cerrar la pestaña ya no hay nada guardado. */
      try { sessionStorage.setItem(LLAVE, CLAVE); } catch (err) {}
      abrir();
    }).catch(function (err) {
      CLAVE = '';
      errorEntrar.textContent = err.message;
      errorEntrar.hidden = false;
    });
  });

  document.querySelector('[data-salir]').addEventListener('click', function () {
    try { sessionStorage.removeItem(LLAVE); } catch (e) {}
    location.reload();
  });

  /* ---------- pantallas ---------- */
  function ir(cual) {
    document.querySelectorAll('[data-pantalla]').forEach(function (s) {
      s.hidden = s.dataset.pantalla !== cual;
    });
    document.querySelectorAll('[data-ir]').forEach(function (b) {
      b.classList.toggle('pa-activo', b.dataset.ir === cual);
    });
    if (cual === 'resumen') cargarResumen();
    if (cual === 'pedidos') cargarPedidos();
    if (cual === 'socios') cargarSocios();
    if (cual === 'comentarios') { cargarMensajes(); cargarValoraciones(); }
  }

  document.querySelectorAll('[data-ir]').forEach(function (b) {
    b.addEventListener('click', function () { ir(b.dataset.ir); });
  });

  /* ---------- resumen ---------- */
  function tarjeta(titulo, valor, clase) {
    return '<div class="pa-tarjeta ' + (clase || '') + '"><span>' + esc(titulo) +
           '</span><b>' + esc(valor) + '</b></div>';
  }

  function cargarResumen() {
    var caja = document.querySelector('[data-resumen]');
    caja.innerHTML = '<p class="pa-nada">Cargando…</p>';
    api('resumen').then(function (d) {
      var pe = d.porEstado || {};
      caja.innerHTML =
        tarjeta('Sin cobrar', pe.solicitado || 0, (pe.solicitado ? 'pa-urge' : '')) +
        tarjeta('Por preparar', (pe.pagado || 0), (pe.pagado ? 'pa-ojo' : '')) +
        tarjeta('En camino', pe.enviado || 0) +
        tarjeta('Entregados', pe.entregado || 0) +
        tarjeta('Pedidos en total', d.pedidos) +
        tarjeta('Vendido', euros(d.facturado)) +
        tarjeta('Socios', d.socios) +
        tarjeta('Mensajes sin leer', d.mensajes_sin_leer, (d.mensajes_sin_leer ? 'pa-urge' : '')) +
        tarjeta('Valoraciones a revisar', d.valoraciones_pendientes, (d.valoraciones_pendientes ? 'pa-ojo' : ''));

      var chipP = document.querySelector('[data-chip-pedidos]');
      chipP.textContent = pe.solicitado || '';
      chipP.hidden = !pe.solicitado;
      var chipC = document.querySelector('[data-chip-comentarios]');
      var pend = (d.mensajes_sin_leer || 0) + (d.valoraciones_pendientes || 0);
      chipC.textContent = pend || '';
      chipC.hidden = !pend;
    }).catch(function (e) { caja.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>'; });
  }

  /* ---------- pedidos ---------- */
  document.querySelectorAll('[data-filtros-pedidos] [data-estado]').forEach(function (b) {
    b.addEventListener('click', function () {
      ESTADO_PEDIDOS = b.dataset.estado;
      document.querySelectorAll('[data-filtros-pedidos] .pa-filtro')
        .forEach(function (o) { o.classList.toggle('pa-activo', o === b); });
      cargarPedidos();
    });
  });

  function cargarPedidos() {
    var caja = document.querySelector('[data-lista-pedidos]');
    caja.innerHTML = '<p class="pa-nada">Cargando…</p>';
    api('pedidos', { estado: ESTADO_PEDIDOS }).then(function (d) {
      if (!d.pedidos.length) { caja.innerHTML = '<p class="pa-nada">Nada por aquí todavía.</p>'; return; }
      caja.innerHTML = d.pedidos.map(function (p) {
        var que = (p.pedido_lineas || []).map(function (l) {
          return l.modelo + ' ' + l.acabado + (l.cantidad > 1 ? ' ×' + l.cantidad : '');
        }).join(' · ');
        return '<button type="button" class="pa-fila" data-pedido="' + p.id + '">' +
          '<div><h3>' + esc(p.numero) + ' — ' + esc(p.env_nombre) + '</h3>' +
          '<p>' + esc(que || 'sin líneas') + '</p>' +
          '<p>' + esc(p.env_poblacion) + ', ' + esc(p.env_provincia) + ' · ' + fecha(p.creado_en, true) + '</p></div>' +
          '<div class="pa-derecha"><p class="pa-importe">' + euros(p.total) + '</p>' +
          '<span class="pa-estado e-' + esc(p.estado) + '">' + esc(p.estado) + '</span></div>' +
          '</button>';
      }).join('');
      caja.querySelectorAll('[data-pedido]').forEach(function (b) {
        b.addEventListener('click', function () { verPedido(b.dataset.pedido); });
      });
    }).catch(function (e) { caja.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>'; });
  }

  function campo(clave, etiqueta, valor, tipo) {
    return '<label class="pa-campo"><span>' + esc(etiqueta) + '</span>' +
           '<input type="' + (tipo || 'text') + '" data-f="' + clave + '" value="' + esc(valor || '') + '"></label>';
  }

  function verPedido(id) {
    abrirFicha('<p class="pa-nada">Cargando…</p>');
    api('pedido', { id: id }).then(function (d) {
      var p = d.pedido;
      var socio = p.socios || {};
      var relojes = d.pedido.relojes || [];
      var porLinea = {};
      relojes.forEach(function (r) { porLinea[r.linea_id] = r; });

      var html = '<h2>' + esc(p.numero) + ' <span class="pa-estado e-' + esc(p.estado) + '">' +
                 esc(p.estado) + '</span></h2>';

      html += '<h4>Envío</h4><dl class="pa-datos">' +
        '<dt>A</dt><dd>' + esc(p.env_nombre) + '</dd>' +
        '<dt>Dirección</dt><dd>' + esc(p.env_direccion) + ', ' + esc(p.env_cp) + ' ' +
          esc(p.env_poblacion) + ' (' + esc(p.env_provincia) + '), ' + esc(p.env_pais) + '</dd>' +
        '<dt>Teléfono</dt><dd>' + esc(p.env_telefono || '—') + '</dd>' +
        '<dt>Correo</dt><dd>' + esc(socio.email || '—') + '</dd>' +
        '<dt>Pedido</dt><dd>' + fecha(p.creado_en, true) + '</dd>' +
        '<dt>Total</dt><dd><b>' + euros(p.total) + '</b> · ' + esc(p.metodo || '—') +
          (p.pagado_en ? ' · cobrado el ' + fecha(p.pagado_en, true) : ' · <b>sin cobrar</b>') + '</dd>' +
        (p.seguimiento ? '<dt>Envío</dt><dd>' + esc(p.transportista || '') + ' ' + esc(p.seguimiento) + '</dd>' : '') +
        '</dl>';

      if (p.fac_nif || p.fac_nombre) {
        html += '<h4>Factura a</h4><dl class="pa-datos">' +
          '<dt>Nombre</dt><dd>' + esc(p.fac_nombre || '') + '</dd>' +
          '<dt>NIF</dt><dd>' + esc(p.fac_nif || '') + '</dd>' +
          '<dt>Dirección</dt><dd>' + esc(p.fac_direccion || '') + ' ' + esc(p.fac_cp || '') + ' ' +
            esc(p.fac_poblacion || '') + '</dd></dl>';
      }

      html += '<h4>Lo comprado</h4>';
      (p.pedido_lineas || []).forEach(function (l) {
        var r = porLinea[l.id];
        var g = r && r.garantias && r.garantias[0];
        html += '<div class="pa-bloque" data-linea="' + l.id + '">' +
          '<h5>' + esc(l.modelo) + ' · ' + esc(l.acabado) + '</h5>' +
          '<p>' + esc(l.correa || '') + ' — Ref. ' + esc(l.ref) +
          (l.cantidad > 1 ? ' ×' + l.cantidad : '') + ' — ' + euros(l.precio) + '</p>' +
          '<div class="pa-campos">' +
            '<label class="pa-campo"><span>Número de serie</span>' +
              '<input type="text" data-serie value="' + esc(r ? r.numero_serie : '') + '" placeholder="sin asignar"></label>' +
            '<label class="pa-campo"><span>Garantía (meses)</span>' +
              '<input type="number" data-meses min="1" value="' + esc(g ? g.meses : 24) + '"></label>' +
          '</div>' +
          (g ? '<p>Cubre desde el ' + fecha(g.desde) + ' hasta el ' + fecha(g.hasta) + '.</p>' : '') +
          '<div class="pa-acciones">' +
            '<button type="button" class="pa-boton pa-suave" data-proponer="' + esc(l.ref) + '">Proponer número</button>' +
            '<button type="button" class="pa-boton" data-guardar-serie="' + l.id + '">Guardar el reloj</button>' +
          '</div></div>';
      });

      html += '<h4>Qué hacer</h4><div class="pa-campos">' +
        campo('referencia', 'Referencia del cobro', p.referencia_pago) +
        campo('transportista', 'Transportista', p.transportista) +
        campo('seguimiento', 'Nº de seguimiento', p.seguimiento) +
        '</div><div class="pa-acciones">' +
        (p.estado === 'solicitado'
          ? '<button type="button" class="pa-boton" data-cobrado>Marcar cobrado</button>' : '') +
        '<button type="button" class="pa-boton pa-suave" data-mover="preparando">Preparando</button>' +
        '<button type="button" class="pa-boton pa-suave" data-mover="enviado">Enviado</button>' +
        '<button type="button" class="pa-boton pa-suave" data-mover="entregado">Entregado</button>' +
        '<button type="button" class="pa-boton pa-suave" data-mover="cancelado">Cancelar</button>' +
        (socio.id ? '<button type="button" class="pa-boton pa-suave" data-ver-socio="' + socio.id + '">Ver al socio</button>' : '') +
        '</div>';

      abrirFicha(html);

      var val = function (k) {
        var i = fichaCaja.querySelector('[data-f="' + k + '"]');
        return i ? i.value.trim() : '';
      };

      var bCobrado = fichaCaja.querySelector('[data-cobrado]');
      if (bCobrado) bCobrado.addEventListener('click', function () {
        api('cobrado', { id: p.id, metodo: p.metodo || 'paypal', referencia: val('referencia') })
          .then(function () { avisar('Cobrado. ' + p.numero + ' pasa a preparar.'); verPedido(p.id); cargarPedidos(); })
          .catch(function (e) { avisar(e.message, true); });
      });

      fichaCaja.querySelectorAll('[data-mover]').forEach(function (b) {
        b.addEventListener('click', function () {
          api('estado', {
            id: p.id, estado: b.dataset.mover,
            transportista: val('transportista'), seguimiento: val('seguimiento')
          }).then(function () {
            avisar('Ahora está en «' + b.dataset.mover + '».');
            verPedido(p.id); cargarPedidos();
          }).catch(function (e) { avisar(e.message, true); });
        });
      });

      fichaCaja.querySelectorAll('[data-proponer]').forEach(function (b) {
        b.addEventListener('click', function () {
          api('proponer_serie', { ref: b.dataset.proponer }).then(function (d) {
            b.closest('[data-linea]').querySelector('[data-serie]').value = d.numero_serie;
          }).catch(function (e) { avisar(e.message, true); });
        });
      });

      fichaCaja.querySelectorAll('[data-guardar-serie]').forEach(function (b) {
        b.addEventListener('click', function () {
          var bloque = b.closest('[data-linea]');
          var serie = bloque.querySelector('[data-serie]').value.trim();
          if (!serie) { avisar('Escribe el número de serie.', true); return; }
          api('serie', {
            linea_id: b.dataset.guardarSerie,
            numero_serie: serie,
            meses: bloque.querySelector('[data-meses]').value
          }).then(function () { avisar('Reloj ' + serie + ' guardado, con su garantía.'); verPedido(p.id); })
            .catch(function (e) { avisar(e.message, true); });
        });
      });

      var bSocio = fichaCaja.querySelector('[data-ver-socio]');
      if (bSocio) bSocio.addEventListener('click', function () { verSocio(bSocio.dataset.verSocio); });

    }).catch(function (e) { abrirFicha('<p class="pa-nada">' + esc(e.message) + '</p>'); });
  }

  /* ---------- socios ---------- */
  function cargarSocios() {
    var caja = document.querySelector('[data-lista-socios]');
    caja.innerHTML = '<p class="pa-nada">Cargando…</p>';
    api('socios').then(function (d) {
      if (!d.socios.length) { caja.innerHTML = '<p class="pa-nada">Todavía no hay socios.</p>'; return; }
      caja.innerHTML = d.socios.map(function (s) {
        return '<button type="button" class="pa-fila" data-socio="' + s.id + '">' +
          '<div><h3>' + esc(nombreDe(s)) + (s.club_desde ? ' · <span class="pa-estado">Club</span>' : '') + '</h3>' +
          '<p>' + esc(s.email) + (s.telefono ? ' · ' + esc(s.telefono) : '') + '</p>' +
          '<p>' + esc([s.poblacion, s.provincia].filter(Boolean).join(', ') || 'sin dirección') + '</p></div>' +
          '<div class="pa-derecha"><p>' + fecha(s.creado_en) + '</p></div></button>';
      }).join('');
      caja.querySelectorAll('[data-socio]').forEach(function (b) {
        b.addEventListener('click', function () { verSocio(b.dataset.socio); });
      });
    }).catch(function (e) { caja.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>'; });
  }

  function verSocio(id) {
    abrirFicha('<p class="pa-nada">Cargando…</p>');
    api('socio', { id: id }).then(function (d) {
      var s = d.socio;
      var html = '<h2>' + esc(nombreDe(s)) + '</h2>' +
        '<h4>Quién es</h4><dl class="pa-datos">' +
        '<dt>Correo</dt><dd>' + esc(s.email) + '</dd>' +
        '<dt>Teléfono</dt><dd>' + esc(s.telefono || '—') + '</dd>' +
        '<dt>NIF</dt><dd>' + esc(s.nif || '—') + '</dd>' +
        '<dt>Dirección</dt><dd>' + esc([s.direccion, s.cp, s.poblacion, s.provincia, s.pais]
            .filter(Boolean).join(', ') || '—') + '</dd>' +
        '<dt>Desde</dt><dd>' + fecha(s.creado_en) + '</dd>' +
        '<dt>Club laOra</dt><dd>' + (s.club_desde ? 'sí, desde ' + fecha(s.club_desde) : 'no') + '</dd>' +
        '</dl>';

      html += '<h4>Sus pedidos</h4>';
      html += d.pedidos.length ? d.pedidos.map(function (p) {
        return '<div class="pa-bloque"><h5>' + esc(p.numero) + ' · ' + euros(p.total) +
          ' <span class="pa-estado e-' + esc(p.estado) + '">' + esc(p.estado) + '</span></h5>' +
          '<p>' + fecha(p.creado_en, true) + '</p></div>';
      }).join('') : '<p class="pa-nada">Ninguno.</p>';

      html += '<h4>Sus relojes</h4>';
      html += d.relojes.length ? d.relojes.map(function (r) {
        var g = r.garantias && r.garantias[0];
        return '<div class="pa-bloque"><h5>' + esc(r.numero_serie) + '</h5>' +
          '<p>' + esc(r.modelo) + ' · ' + esc(r.acabado) + ' · ' + esc(r.correa || '') + '</p>' +
          '<p>' + (g ? 'Garantía hasta el ' + fecha(g.hasta) + ' (' + esc(g.estado) + ')' : 'sin garantía abierta') + '</p></div>';
      }).join('') : '<p class="pa-nada">Ninguno todavía.</p>';

      html += '<h4>Notas tuyas <span style="text-transform:none;font-weight:400">— no las ve nadie más</span></h4>' +
        '<label class="pa-campo"><textarea data-notas>' + esc(s.notas || '') + '</textarea></label>' +
        '<div class="pa-acciones">' +
        '<button type="button" class="pa-boton" data-guardar-notas>Guardar notas</button>' +
        '<button type="button" class="pa-boton pa-suave" data-club>' +
          (s.club_desde ? 'Sacar del Club' : 'Meter en el Club') + '</button>' +
        '</div>';

      abrirFicha(html);

      fichaCaja.querySelector('[data-guardar-notas]').addEventListener('click', function () {
        api('notas_socio', { id: s.id, notas: fichaCaja.querySelector('[data-notas]').value })
          .then(function () { avisar('Notas guardadas.'); })
          .catch(function (e) { avisar(e.message, true); });
      });
      fichaCaja.querySelector('[data-club]').addEventListener('click', function () {
        api('club', { id: s.id, club: !s.club_desde })
          .then(function () { avisar(s.club_desde ? 'Fuera del Club.' : 'Dentro del Club.'); verSocio(s.id); cargarSocios(); })
          .catch(function (e) { avisar(e.message, true); });
      });
    }).catch(function (e) { abrirFicha('<p class="pa-nada">' + esc(e.message) + '</p>'); });
  }

  /* ---------- comentarios ---------- */
  function cargarMensajes() {
    var caja = document.querySelector('[data-lista-mensajes]');
    caja.innerHTML = '<p class="pa-nada">Cargando…</p>';
    api('mensajes').then(function (d) {
      if (!d.mensajes.length) { caja.innerHTML = '<p class="pa-nada">Nadie ha escrito todavía.</p>'; return; }
      /* Se agrupa por socio: la conversación se lee entera, no suelta. */
      var hilos = {};
      d.mensajes.slice().reverse().forEach(function (m) {
        var k = m.socio_id;
        if (!hilos[k]) hilos[k] = { socio: m.socios, id: k, lineas: [], pendientes: 0 };
        hilos[k].lineas.push(m);
        if (m.autor === 'socio' && !m.leido_en) hilos[k].pendientes++;
      });
      caja.innerHTML = Object.keys(hilos).map(function (k) {
        var h = hilos[k];
        var ultimo = h.lineas[h.lineas.length - 1];
        return '<div class="pa-bloque"><h5>' + esc(nombreDe(h.socio)) +
          (h.pendientes ? ' <span class="pa-estado e-solicitado">' + h.pendientes + ' sin leer</span>' : '') + '</h5>' +
          h.lineas.map(function (m) {
            return '<p><b>' + (m.autor === 'socio' ? esc(nombreDe(h.socio)) : 'laOra') + '</b> · ' +
              fecha(m.creado_en, true) + '<br>' + esc(m.texto) + '</p>';
          }).join('') +
          '<label class="pa-campo" style="margin-top:10px"><span>Contestar</span>' +
          '<textarea data-respuesta="' + esc(h.id) + '"></textarea></label>' +
          '<div class="pa-acciones"><button type="button" class="pa-boton" data-enviar="' + esc(h.id) + '">Enviar</button>' +
          (h.pendientes ? '<button type="button" class="pa-boton pa-suave" data-leido="' + esc(h.id) + '">Marcar leído</button>' : '') +
          '</div></div>';
      }).join('');

      caja.querySelectorAll('[data-enviar]').forEach(function (b) {
        b.addEventListener('click', function () {
          var t = caja.querySelector('[data-respuesta="' + b.dataset.enviar + '"]').value.trim();
          if (!t) { avisar('Escribe algo antes de enviar.', true); return; }
          api('responder', { socio_id: b.dataset.enviar, texto: t })
            .then(function () { avisar('Contestado.'); cargarMensajes(); cargarResumen(); })
            .catch(function (e) { avisar(e.message, true); });
        });
      });
      caja.querySelectorAll('[data-leido]').forEach(function (b) {
        b.addEventListener('click', function () {
          api('leido', { socio_id: b.dataset.leido })
            .then(function () { cargarMensajes(); cargarResumen(); })
            .catch(function (e) { avisar(e.message, true); });
        });
      });
    }).catch(function (e) { caja.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>'; });
  }

  document.querySelectorAll('[data-filtros-valoraciones] [data-vestado]').forEach(function (b) {
    b.addEventListener('click', function () {
      ESTADO_VALORACIONES = b.dataset.vestado;
      document.querySelectorAll('[data-filtros-valoraciones] .pa-filtro')
        .forEach(function (o) { o.classList.toggle('pa-activo', o === b); });
      cargarValoraciones();
    });
  });

  function cargarValoraciones() {
    var caja = document.querySelector('[data-lista-valoraciones]');
    caja.innerHTML = '<p class="pa-nada">Cargando…</p>';
    api('valoraciones', { estado: ESTADO_VALORACIONES }).then(function (d) {
      if (!d.valoraciones.length) { caja.innerHTML = '<p class="pa-nada">Nada aquí.</p>'; return; }
      caja.innerHTML = d.valoraciones.map(function (v) {
        return '<div class="pa-bloque"><h5>' + '★'.repeat(v.estrellas) + '☆'.repeat(5 - v.estrellas) +
          ' · ' + esc(v.modelo) + ' · ' + esc(nombreDe(v.socios)) +
          ' <span class="pa-estado">' + esc(v.estado) + '</span></h5>' +
          (v.titulo ? '<p><b>' + esc(v.titulo) + '</b></p>' : '') +
          '<p>' + esc(v.texto) + '</p>' +
          '<p>' + fecha(v.creado_en, true) + (v.firma ? ' · firma: ' + esc(v.firma) : '') + '</p>' +
          (v.estado === 'pendiente'
            ? '<div class="pa-acciones">' +
              '<button type="button" class="pa-boton" data-publicar="' + v.id + '">Publicar</button>' +
              '<button type="button" class="pa-boton pa-suave" data-rechazar="' + v.id + '">Rechazar</button></div>'
            : '') +
          '</div>';
      }).join('');
      caja.querySelectorAll('[data-publicar]').forEach(function (b) {
        b.addEventListener('click', function () {
          api('moderar', { id: b.dataset.publicar, decision: 'publicar' })
            .then(function () { avisar('Publicada.'); cargarValoraciones(); cargarResumen(); })
            .catch(function (e) { avisar(e.message, true); });
        });
      });
      caja.querySelectorAll('[data-rechazar]').forEach(function (b) {
        b.addEventListener('click', function () {
          api('moderar', { id: b.dataset.rechazar, decision: 'rechazar' })
            .then(function () { avisar('Rechazada. No sale en la web.'); cargarValoraciones(); cargarResumen(); })
            .catch(function (e) { avisar(e.message, true); });
        });
      });
    }).catch(function (e) { caja.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>'; });
  }

  /* ---------- la ficha de encima ---------- */
  function abrirFicha(html) {
    fichaCaja.innerHTML = html;
    manto.hidden = false;
  }
  function cerrarFicha() { manto.hidden = true; fichaCaja.innerHTML = ''; }

  document.querySelector('[data-cerrar]').addEventListener('click', cerrarFicha);
  manto.addEventListener('click', function (e) { if (e.target === manto) cerrarFicha(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrarFicha(); });

  /* Si ya se entró en esta pestaña, no se vuelve a preguntar. */
  try {
    var guardada = sessionStorage.getItem(LLAVE);
    if (guardada) {
      CLAVE = guardada;
      api('entrar').then(abrir).catch(function () {
        CLAVE = '';
        try { sessionStorage.removeItem(LLAVE); } catch (e) {}
      });
    }
  } catch (e) {}
})();
