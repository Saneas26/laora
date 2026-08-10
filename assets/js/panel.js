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

  /* PostgREST devuelve lo enlazado como lista cuando pueden ser varios
     y como objeto suelto cuando solo puede haber uno. La garantía es de
     las segundas —una por reloj—, así que llega como objeto. Esto se
     traga las dos formas y evita el fallo tonto de pedir `[0]` a algo
     que no es una lista. */
  function elPrimero(x) {
    if (!x) return null;
    return Array.isArray(x) ? (x[0] || null) : x;
  }

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
    if (cual === 'compras') cargarCompras();
    if (cual === 'cuentas') cargarCuentas();
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
        var g = r && elPrimero(r.garantias);
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

      /* La factura, antes de los botones: es lo primero que se mira
         cuando el cliente la reclama. */
      html += '<h4>Factura</h4>' + (p.factura_numero
        ? '<p><b>' + esc(p.factura_numero) + '</b> · ' + fecha(p.factura_fecha) +
          ' · <button type="button" class="pa-filtro" data-ver-factura>Ver e imprimir</button></p>'
        : '<p class="pa-mini">Sin emitir. El número lo pone la base, correlativo y sin saltos.</p>');

      html += '<h4>Qué hacer</h4><div class="pa-campos">' +
        /* Por dónde entró el dinero. Sin esto todo caía en «paypal» por
           defecto y el cuadre del banco era imposible. */
        '<label class="pa-campo"><span>Cobrado por</span><select class="pa-select" data-f="metodo">' +
        METODOS.map(function (m) {
          return '<option value="' + m[0] + '"' +
            (p.metodo === m[0] ? ' selected' : '') + '>' + esc(m[1]) + '</option>';
        }).join('') + '</select></label>' +
        campo('referencia', 'Referencia del cobro', p.referencia_pago) +
        campo('transportista', 'Transportista', p.transportista) +
        campo('seguimiento', 'Nº de seguimiento', p.seguimiento) +
        '</div><div class="pa-acciones">' +
        (p.estado === 'solicitado'
          ? '<button type="button" class="pa-boton" data-cobrado>Marcar cobrado</button>' : '') +
        (p.estado !== 'solicitado' && p.estado !== 'cancelado' && !p.factura_numero
          ? '<button type="button" class="pa-boton" data-facturar>Emitir factura</button>' : '') +
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
        api('cobrado', { id: p.id, metodo: val('metodo'), referencia: val('referencia') })
          .then(function () { avisar('Cobrado por ' + nombreMetodo(val('metodo')) + '. ' + p.numero + ' pasa a preparar.'); verPedido(p.id); cargarPedidos(); })
          .catch(function (e) { avisar(e.message, true); });
      });

      var bFactura = fichaCaja.querySelector('[data-facturar]');
      if (bFactura) bFactura.addEventListener('click', function () {
        api('facturar', { id: p.id })
          .then(function (d) { avisar('Factura ' + d.numero + ' emitida.'); verPedido(p.id); })
          .catch(function (e) { avisar(e.message, true); });
      });

      var bVer = fichaCaja.querySelector('[data-ver-factura]');
      if (bVer) bVer.addEventListener('click', function () { imprimirFactura(p.id); });

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
        var g = elPrimero(r.garantias);
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

  /* ============================================================
     LAS CUENTAS
     ------------------------------------------------------------
     Aquí NO se suma nada: los números llegan calculados por las
     vistas de la base. Si el cálculo viviera también en este
     archivo, un día dirían cosas distintas y no sabríamos a cuál
     hacer caso.
     ============================================================ */

  /* Los métodos, con su nombre de verdad. Los dos Bizum van
     separados porque con un solo «bizum» no se cuadra el banco:
     no se sabe cuál de los dos números recibió el dinero. */
  var METODOS = [
    ['bizum1', 'Bizum 1'], ['bizum2', 'Bizum 2'], ['tarjeta', 'Tarjeta'],
    ['paypal', 'PayPal'], ['transferencia', 'Transferencia'], ['efectivo', 'Efectivo']
  ];
  function nombreMetodo(m) {
    for (var i = 0; i < METODOS.length; i++) if (METODOS[i][0] === m) return METODOS[i][1];
    return m || 'sin indicar';
  }

  var CATEGORIAS = [
    ['envio', 'Envío'], ['embalaje', 'Embalaje'], ['comision', 'Comisión'],
    ['herramienta', 'Herramienta'], ['web', 'Web'], ['publicidad', 'Publicidad'],
    ['impuesto', 'Impuesto'], ['piezas', 'Piezas'], ['otro', 'Otro']
  ];

  function tabla(cabeceras, filas, pie) {
    if (!filas.length) return '<p class="pa-nada">Todavía no hay nada que contar.</p>';
    var th = cabeceras.map(function (c) {
      return '<th' + (c[1] ? ' class="n"' : '') + '>' + esc(c[0]) + '</th>';
    }).join('');
    return '<div class="pa-tabla-caja"><table class="pa-tabla"><thead><tr>' + th +
      '</tr></thead><tbody>' + filas.join('') + '</tbody>' +
      (pie ? '<tfoot><tr>' + pie + '</tr></tfoot>' : '') + '</table></div>';
  }

  /* El margen en rojo cuando es negativo: un número negativo entre
     otros positivos se pasa por alto si va del mismo color. */
  function dinero(v) {
    var n = Number(v) || 0;
    return '<td class="n' + (n < 0 ? ' pa-menos' : '') + '">' + euros(n) + '</td>';
  }

  function cargarCuentas() {
    var cajaAnio = document.querySelector('[data-cuentas-anio]');
    cajaAnio.innerHTML = '<p class="pa-nada">Cargando…</p>';
    /* El formulario de gasto se pinta SIEMPRE, aunque las cuentas
       fallen: si dependiera de ellas, un error de red dejaría a Óscar
       sin poder apuntar un gasto, que es justo cuando más rabia da. */
    pintarFormGasto();

    api('cuentas').then(function (d) {
      var y = d.ytd;
      cajaAnio.innerHTML =
        tarjeta('Ingresos ' + d.anio, euros(y.ingresos)) +
        tarjeta('Coste de piezas', euros(y.piezas)) +
        tarjeta('Gastos', euros(y.gastos)) +
        tarjeta('Margen', euros(y.margen), y.margen < 0 ? 'pa-urge' : '') +
        tarjeta('IVA a pagar', euros(y.iva_a_pagar), 'pa-ojo') +
        tarjeta('Pedidos cobrados', y.pedidos);

      document.querySelector('[data-tabla-trimestres]').innerHTML = tabla(
        [['Periodo'], ['Pedidos', 1], ['Ingresos', 1], ['Base', 1], ['IVA', 1],
         ['Piezas', 1], ['Gastos', 1], ['Margen', 1], ['IVA a pagar', 1]],
        d.trimestres.map(function (t) {
          return '<tr><td><b>' + t.anio + ' · ' + t.trimestre + 'T</b></td>' +
            '<td class="n">' + t.pedidos + '</td>' +
            dinero(t.ingresos) + dinero(t.base) + dinero(t.iva_repercutido) +
            dinero(t.piezas) + dinero(t.gastos) + dinero(t.margen) + dinero(t.iva_a_pagar) +
            '</tr>';
        }));

      document.querySelector('[data-tabla-anios]').innerHTML = tabla(
        [['Año'], ['Pedidos', 1], ['Ingresos', 1], ['Base', 1],
         ['Piezas', 1], ['Gastos', 1], ['Margen', 1]],
        d.anios.map(function (a) {
          return '<tr><td><b>' + a.anio + '</b></td>' +
            '<td class="n">' + a.pedidos + '</td>' +
            dinero(a.ingresos) + dinero(a.base) +
            dinero(a.piezas) + dinero(a.gastos) + dinero(a.margen) + '</tr>';
        }));

      document.querySelector('[data-tabla-metodos]').innerHTML = tabla(
        [['Periodo'], ['Dónde'], ['Pedidos', 1], ['Importe', 1]],
        d.metodos.map(function (m) {
          return '<tr><td>' + m.anio + ' · ' + m.trimestre + 'T</td>' +
            '<td><b>' + esc(nombreMetodo(m.metodo)) + '</b></td>' +
            '<td class="n">' + m.pedidos + '</td>' + dinero(m.importe) + '</tr>';
        }));

      cargarGastos();
    }).catch(function (e) {
      cajaAnio.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>';
    });
  }

  function pintarFormGasto() {
    var f = document.querySelector('[data-form-gasto]');
    if (f.dataset.listo) return;
    f.dataset.listo = '1';
    f.innerHTML =
      campo('g_fecha', 'Fecha', new Date().toISOString().slice(0, 10), 'date') +
      campo('g_concepto', 'Concepto', '') +
      '<label class="pa-campo"><span>Categoría</span><select class="pa-select" data-f="g_categoria">' +
      CATEGORIAS.map(function (c) {
        return '<option value="' + c[0] + '">' + esc(c[1]) + '</option>';
      }).join('') + '</select></label>' +
      campo('g_importe', 'Importe con IVA', '') +
      campo('g_iva', 'De eso, IVA', '') +
      campo('g_proveedor', 'Proveedor', '') +
      campo('g_enlace', 'Enlace o justificante', '') +
      '<div class="pa-acciones"><button type="submit" class="pa-boton">Apuntar el gasto</button></div>';

    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (k) {
        var i = f.querySelector('[data-f="' + k + '"]');
        return i ? i.value.trim() : '';
      };
      if (!v('g_concepto')) { avisar('Ponle un concepto al gasto.', true); return; }
      api('gasto_nuevo', {
        fecha: v('g_fecha'), concepto: v('g_concepto'), categoria: v('g_categoria'),
        importe: Number(String(v('g_importe')).replace(',', '.')),
        iva: Number(String(v('g_iva')).replace(',', '.')) || 0,
        proveedor: v('g_proveedor'), enlace: v('g_enlace')
      }).then(function () {
        avisar('Apuntado.');
        f.querySelector('[data-f="g_concepto"]').value = '';
        f.querySelector('[data-f="g_importe"]').value = '';
        f.querySelector('[data-f="g_iva"]').value = '';
        cargarCuentas();
      }).catch(function (e) { avisar(e.message, true); });
    });
  }

  function cargarGastos() {
    var caja = document.querySelector('[data-lista-gastos]');
    api('gastos').then(function (d) {
      caja.innerHTML = tabla(
        [['Fecha'], ['Concepto'], ['Categoría'], ['Importe', 1], ['IVA', 1], ['']],
        d.gastos.map(function (g) {
          var cat = CATEGORIAS.filter(function (c) { return c[0] === g.categoria; })[0];
          return '<tr><td>' + fecha(g.fecha) + '</td>' +
            '<td><b>' + esc(g.concepto) + '</b>' +
            (g.proveedor ? ' <span class="pa-mini">' + esc(g.proveedor) + '</span>' : '') +
            (g.enlace ? ' <a href="' + esc(g.enlace) + '" target="_blank" rel="noopener">ver</a>' : '') +
            '</td><td>' + esc(cat ? cat[1] : g.categoria) + '</td>' +
            dinero(g.importe) + dinero(g.iva) +
            '<td><button type="button" class="pa-filtro" data-borrar-gasto="' + g.id + '">Borrar</button></td></tr>';
        }));
      caja.querySelectorAll('[data-borrar-gasto]').forEach(function (b) {
        b.addEventListener('click', function () {
          if (!confirm('¿Borrar este gasto? No se puede deshacer.')) return;
          api('gasto_borrar', { id: b.dataset.borrarGasto })
            .then(function () { avisar('Borrado.'); cargarCuentas(); })
            .catch(function (e) { avisar(e.message, true); });
        });
      });
    }).catch(function (e) { caja.innerHTML = '<p class="pa-nada">' + esc(e.message) + '</p>'; });
  }

  /* ============================================================
     LA FACTURA IMPRESA
     ------------------------------------------------------------
     Se abre en una ventana aparte y se imprime a PDF con el diálogo
     del navegador. No se guarda un archivo en ningún sitio: lo que
     manda es la FILA del pedido, con su número y su fecha, y de ahí
     se puede volver a imprimir idéntica cuantas veces haga falta.
     Un PDF guardado sería una segunda verdad que se puede perder.

     EL EMISOR ES ÓSCAR COMO AUTÓNOMO, no una sociedad (10/08/2026).
     La SL está en camino; hasta que exista, quien factura es él, y una
     venta que caiga mañana tiene que poder facturarse hoy.

     EL DÍA QUE HAYA SL hay que cambiar estos datos Y ABRIR SERIE NUEVA
     de facturas: son dos emisores distintos y sus numeraciones no se
     mezclan. La serie de aquí es F{AA}-NNNN; la de la sociedad tendrá
     que llevar otra letra.

     Si algún campo se queda vacío, la factura sale con el hueco a la
     vista, en rojo, para que no se mande por error: una factura sin el
     NIF de quien la emite no vale para nada.
     ============================================================ */
  var EMISOR = {
    nombre: 'Óscar Belloso Jiménez',
    nif: '46922078P',
    direccion: 'San Juan, 9',
    cp: '28320', poblacion: 'Pinto', provincia: 'Madrid',
    email: 'hola@laora.es',
    web: 'laora.es'
  };

  /* «28013 Madrid Madrid» no lo escribe nadie: cuando la población y la
     provincia son la misma, se dice una vez. */
  function lugar(cp, poblacion, provincia) {
    var p = (poblacion || '').trim(), v = (provincia || '').trim();
    var cola = (v && v.toLowerCase() !== p.toLowerCase()) ? p + ' (' + v + ')' : p;
    return ((cp || '') + ' ' + cola).trim();
  }

  function imprimirFactura(id) {
    api('factura', { id: id }).then(function (d) {
      var p = d.pedido;
      if (!p.factura_numero) { avisar('Ese pedido todavía no tiene factura.', true); return; }

      var falta = !EMISOR.nombre || !EMISOR.nif || !EMISOR.direccion;
      var lineas = (p.pedido_lineas || []).map(function (l) {
        return '<tr><td>' + esc(l.modelo) + ' · ' + esc(l.acabado) +
          (l.correa ? ' · ' + esc(l.correa) : '') +
          '<br><small>' + esc(l.ref) + '</small></td>' +
          '<td class="n">' + l.cantidad + '</td>' +
          '<td class="n">' + euros(l.precio) + '</td>' +
          '<td class="n">' + euros(Number(l.precio) * Number(l.cantidad)) + '</td></tr>';
      }).join('');

      var cli = p.fac_nombre ? {
        nombre: p.fac_nombre, nif: p.fac_nif, direccion: p.fac_direccion,
        cp: p.fac_cp, poblacion: p.fac_poblacion, provincia: p.fac_provincia
      } : {
        nombre: p.env_nombre, nif: '', direccion: p.env_direccion,
        cp: p.env_cp, poblacion: p.env_poblacion, provincia: p.env_provincia
      };

      var html =
        '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">' +
        '<title>' + esc(p.factura_numero) + ' · laOra</title><style>' +
        'body{font:15px/1.5 -apple-system,system-ui,sans-serif;color:#1c1d1b;max-width:760px;' +
        'margin:0 auto;padding:40px 28px}h1{font-size:26px;margin:0 0 4px}' +
        '.gris{color:#6b6b64}.aviso{background:#f6d5cd;color:#8a2c14;padding:12px 14px;' +
        'border-radius:10px;font-weight:700;margin-bottom:22px}' +
        '.dos{display:flex;gap:40px;flex-wrap:wrap;margin:26px 0}.dos>div{flex:1;min-width:220px}' +
        'h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#6b6b64;margin:0 0 6px}' +
        'table{width:100%;border-collapse:collapse;margin-top:14px}' +
        'th,td{padding:9px 8px;text-align:left;border-bottom:1px solid #e3e0d8;vertical-align:top}' +
        'th{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#6b6b64}' +
        '.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}' +
        'tfoot td{border:0;padding-top:6px}tfoot .tot td{border-top:2px solid #1c1d1b;font-weight:700;font-size:17px}' +
        'small{color:#6b6b64}@media print{body{padding:0}.noimp{display:none}}' +
        '</style></head><body>' +
        (falta ? '<p class="aviso">FALTAN LOS DATOS FISCALES DEL EMISOR. ' +
                 'Rellénalos en EMISOR, dentro de assets/js/panel.js, antes de mandar esta factura.</p>' : '') +
        '<h1>Factura ' + esc(p.factura_numero) + '</h1>' +
        '<p class="gris">Fecha: ' + fecha(p.factura_fecha) + ' · Pedido ' + esc(p.numero) + '</p>' +
        '<div class="dos"><div><h2>Emisor</h2>' +
        '<b>' + esc(EMISOR.nombre || '(falta el nombre fiscal)') + '</b><br>' +
        'NIF ' + esc(EMISOR.nif || '(falta)') + '<br>' +
        esc(EMISOR.direccion || '(falta la dirección)') + '<br>' +
        esc(lugar(EMISOR.cp, EMISOR.poblacion, EMISOR.provincia)) + '<br>' +
        esc(EMISOR.email) + ' · ' + esc(EMISOR.web) +
        '</div><div><h2>Cliente</h2>' +
        '<b>' + esc(cli.nombre) + '</b><br>' +
        (cli.nif ? 'NIF ' + esc(cli.nif) + '<br>' : '') +
        esc(cli.direccion) + '<br>' +
        esc(lugar(cli.cp, cli.poblacion, cli.provincia)) +
        '</div></div>' +
        '<table><thead><tr><th>Concepto</th><th class="n">Uds</th>' +
        '<th class="n">Precio</th><th class="n">Importe</th></tr></thead>' +
        '<tbody>' + lineas + '</tbody><tfoot>' +
        (Number(p.envio) ? '<tr><td colspan="3" class="n">Envío</td><td class="n">' + euros(p.envio) + '</td></tr>' : '') +
        '<tr><td colspan="3" class="n">Base imponible</td><td class="n">' + euros(d.base) + '</td></tr>' +
        '<tr><td colspan="3" class="n">IVA ' + d.tipo_iva + ' %</td><td class="n">' + euros(d.iva) + '</td></tr>' +
        '<tr class="tot"><td colspan="3" class="n">Total</td><td class="n">' + euros(p.total) + '</td></tr>' +
        '</tfoot></table>' +
        '<p class="gris">Cobrado por ' + esc(nombreMetodo(p.metodo)) +
        (p.pagado_en ? ' el ' + fecha(p.pagado_en) : '') + '.</p>' +
        '<p class="noimp"><button onclick="print()">Imprimir o guardar en PDF</button></p>' +
        '</body></html>';

      var v = window.open('', '_blank');
      if (!v) { avisar('El navegador ha bloqueado la ventana de la factura.', true); return; }
      v.document.write(html);
      v.document.close();
    }).catch(function (e) { avisar(e.message, true); });
  }

  /* ---------- la lista de la compra ---------- */
  function cargarCompras() {
    var caja = document.querySelector('[data-lista-compras]');
    caja.innerHTML = '<p class="pa-nada">Cargando…</p>';
    api('compras').then(function (d) {
      var chip = document.querySelector('[data-chip-compras]');
      var piezas = d.compras.reduce(function (a, c) { return a + Number(c.unidades); }, 0);
      chip.textContent = piezas;
      chip.hidden = !piezas;

      caja.innerHTML = tabla(
        [['Qué'], ['Ref'], ['Pieza'], ['Uds', 1], ['Coste', 1], ['Para']],
        d.compras.map(function (c) {
          return '<tr><td><b>' + esc(c.tipo) + '</b></td>' +
            '<td>' + esc(c.ref) + '</td>' +
            '<td>' + esc(c.interno || '—') + (c.talla ? ' · ' + esc(c.talla) : '') +
            (c.link ? ' <a href="' + esc(c.link) + '" target="_blank" rel="noopener">comprar</a>' : '') +
            '</td><td class="n">' + c.unidades + '</td>' + dinero(c.coste_total) +
            '<td>' + esc((c.pedidos || []).join(', ')) + '</td></tr>';
        }));
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
