/* ============================================================
   laOra · Pantalla de pago (sale del carrito)
   ------------------------------------------------------------
   Enseña lo que hay en la cesta, pide los datos de envío y deja
   elegir cómo pagar entre lo que haya activo en `pagos.js`.

   LO QUE ESTA PANTALLA **NO** HACE, A PROPÓSITO:
   - No fija el importe. Lo pinta para que la persona lo vea, pero
     el que se cobra lo recalcula el servidor leyendo `precios.js`.
     Si no cuadran, la Edge Function devuelve 409 y no se cobra.
   - No cobra los métodos manuales: crea el pedido en «pendiente»
     y enseña las instrucciones. Vale cuando se ve el dinero.
   - No desglosa impuestos. Ver LAORA_MOSTRAR_IMPUESTOS abajo.
   ============================================================ */

/* El desglose de base imponible + impuesto está APAGADO a propósito.
   laOra va a ser una S.L. y todavía no está decidido si se registra en
   Madrid o en Canarias, y el almacén está en Madrid. Según cómo quede,
   lo que se repercute puede ser IVA o IGIC, y puede depender de a dónde
   se envíe. Enseñar «IVA 21 %» en una factura equivocada no es un
   detalle de diseño: es un problema con Hacienda y con el cliente.
   Se enciende cuando lo confirme la asesoría. */
var LAORA_MOSTRAR_IMPUESTOS = false;

(function () {
  var caja = document.getElementById('pago');
  if (!caja) return;

  var euros = (typeof laoraEuros === 'function') ? laoraEuros : function (n) { return n + ' €'; };

  function aviso(titulo, texto, boton) {
    caja.innerHTML =
      '<div class="rsv-aviso">' +
      '<h1>' + titulo + '</h1>' +
      '<p>' + texto + '</p>' +
      (boton || '<a class="btn btn-carbon" href="/coleccion.html">Ver la colección</a>') +
      '</div>';
  }

  /* ---------- 1 · ¿hay algo que cobrar? ---------- */
  var lineas = (typeof laoraCarritoLeer === 'function') ? laoraCarritoLeer() : [];
  if (!lineas.length) {
    aviso('Tu cesta está vacía',
      'No hay nada que pagar todavía. Elige tu reloj y vuelve por aquí.');
    return;
  }

  /* ---------- 2 · puertas: nada se cobra sin precio y sin fecha ---------- */
  var sinPrecio = lineas.filter(function (l) {
    var a = (typeof laoraAcabado === 'function') ? laoraAcabado(l.ref, l.acabado) : null;
    return !a || !a.precio;
  });
  if (sinPrecio.length) {
    aviso('Hay algo en la cesta que todavía no está a la venta',
      'Estos acabados aún no tienen precio cerrado, así que no podemos cobrarlos: ' +
      sinPrecio.map(function (l) { return l.modelo + ' ' + l.acabado; }).join(', ') +
      '. Quítalos de la cesta y seguimos.',
      '<a class="btn btn-carbon" href="/carrito.html">Volver a la cesta</a>');
    return;
  }

  if (typeof LAORA_ENTREGA === 'undefined' || !LAORA_ENTREGA) {
    aviso('Todavía no podemos cobrarte',
      'No tenemos cerrada una fecha de entrega comprometida, y sin fecha pactada ' +
      'no nos parece honesto cobrar por adelantado. Es cuestión de días.',
      '<a class="btn btn-carbon" href="/coleccion.html">Ver la colección</a>');
    return;
  }

  /* ---------- 3 · las cuentas ---------- */
  /* El precio de cada línea se relee de precios.js: si cambió desde que se
     metió en la cesta, manda el de ahora, no el que se guardó. */
  var total = 0;
  var detalle = lineas.map(function (l) {
    var a = laoraAcabado(l.ref, l.acabado);
    var cantidad = l.cantidad || 1;
    var extras = (l.extras || []).reduce(function (s, e) { return s + (e.precio || 0); }, 0);
    var unidad = a.precio + extras;
    var subtotal = unidad * cantidad;
    total += subtotal;
    return { ref: a.ref, modelo: a.modelo, acabado: a.acabado, esfera: l.esfera || '',
             extras: l.extras || [], cantidad: cantidad, unidad: unidad, subtotal: subtotal };
  });
  total = Math.round(total * 100) / 100;

  var senal = (typeof laoraSenal === 'function') ? laoraSenal(total) : total;
  var resto = Math.round((total - senal) * 100) / 100;

  /* ---------- 4 · métodos de pago ---------- */
  var disponibles = (typeof laoraPagosDisponibles === 'function') ? laoraPagosDisponibles() : [];
  var sinComision = disponibles.filter(function (k) { return !LAORA_PAGOS[k].comision; });
  var conComision = disponibles.filter(function (k) { return LAORA_PAGOS[k].comision; });
  var hayAlguno = disponibles.some(laoraPagoListo);

  function pinta(clave, primero) {
    var m = LAORA_PAGOS[clave];
    var listo = laoraPagoListo(clave);
    return '<label class="rsv-pago pg-pago' + (listo ? '' : ' pg-pago-no') + '">' +
      '<input type="radio" name="metodo" value="' + clave + '"' +
        (listo && primero ? ' checked' : '') + (listo ? '' : ' disabled') + '>' +
      '<span><b>' + m.titulo + '</b>' +
      '<small>' + m.resumen + ' ' + m.plazo + '</small>' +
      (listo ? '' : '<small class="pg-no">Todavía no disponible.</small>') +
      '</span></label>';
  }

  var primeroListo = disponibles.filter(laoraPagoListo)[0];

  var bloquePagos =
    (sinComision.length
      ? '<p class="pg-grupo">Sin comisión · lo revisamos a mano</p>' +
        '<div class="rsv-pagos">' +
        sinComision.map(function (k) { return pinta(k, k === primeroListo); }).join('') +
        '</div>'
      : '') +
    (conComision.length
      ? '<p class="pg-grupo">Pago inmediato</p>' +
        '<div class="rsv-pagos">' +
        conComision.map(function (k) { return pinta(k, k === primeroListo); }).join('') +
        '</div>'
      : '');

  /* ---------- 5 · a pintar ---------- */
  caja.innerHTML =
    '<div class="rsv-grid">' +

    '<div class="rsv-resumen">' +
      '<span class="rsv-eyebrow">Tu pedido</span>' +
      '<h1>' + (detalle.length === 1 ? '1 reloj' : detalle.length + ' relojes') + '</h1>' +

      '<ul class="pg-lineas">' +
      detalle.map(function (d) {
        return '<li><span class="pg-l-nom">' + d.ref + ' «' + d.modelo + '»' +
          (d.cantidad > 1 ? ' <b>×' + d.cantidad + '</b>' : '') + '</span>' +
          '<span class="pg-l-det">Acabado ' + d.acabado +
          (d.esfera ? ' · esfera ' + d.esfera : '') +
          (d.extras.length ? ' · ' + d.extras.map(function (e) { return e.nombre; }).join(', ') : '') +
          '</span>' +
          '<span class="pg-l-precio">' + euros(d.subtotal) + '</span></li>';
      }).join('') +
      '</ul>' +

      '<dl class="rsv-cuentas">' +
        '<dt>Total del pedido</dt><dd>' + euros(total) + '</dd>' +
        (LAORA_MOSTRAR_IMPUESTOS ? impuestos(total) : '') +
        '<dt class="rsv-total">Pagas ahora (' + LAORA_SENAL_PORCENTAJE + ' %)</dt>' +
        '<dd class="rsv-total">' + euros(senal) + '</dd>' +
        '<dt>Pagas al recibirlo</dt><dd>' + euros(resto) + '</dd>' +
      '</dl>' +

      '<p class="rsv-entrega"><b>Entrega:</b> ' + LAORA_ENTREGA + '</p>' +
      '<p class="rsv-desist">Puedes echarte atrás en los 14 días siguientes sin dar ' +
      'explicaciones y te devolvemos la señal <b>entera</b>. No es una promesa nuestra: ' +
      'es tu derecho de desistimiento.</p>' +
      '<a class="pg-volver" href="/carrito.html">← Cambiar la cesta</a>' +
    '</div>' +

    '<form class="rsv-form" id="pgForm" novalidate>' +
      '<h2>Tus datos</h2>' +
      '<label>Nombre y apellidos<input name="nombre" required autocomplete="name"></label>' +
      '<label>Correo<input name="email" type="email" required autocomplete="email"></label>' +
      '<label>Teléfono<input name="telefono" required autocomplete="tel" ' +
        'inputmode="tel" placeholder="Para avisarte del envío"></label>' +

      '<h2>Dirección de envío</h2>' +
      '<label>Dirección<input name="direccion" required autocomplete="street-address"></label>' +
      '<div class="rsv-fila">' +
        '<label>Código postal<input name="cp" required autocomplete="postal-code" inputmode="numeric"></label>' +
        '<label>Población<input name="poblacion" required autocomplete="address-level2"></label>' +
      '</div>' +
      '<label>Provincia<input name="provincia" required autocomplete="address-level1"></label>' +

      '<h2>Cómo quieres pagar</h2>' +
      bloquePagos +
      (hayAlguno ? '' :
        '<p class="pg-ninguno">Todavía no hay ninguna forma de pago activa. ' +
        'No podemos cobrarte, y preferimos decírtelo así.</p>') +

      '<label class="rsv-check"><input type="checkbox" name="condiciones" required>' +
        '<span>He leído y acepto las <a href="/condiciones-de-venta.html" target="_blank">' +
        'condiciones de venta</a> y la <a href="/privacidad.html" target="_blank">' +
        'política de privacidad</a>.</span></label>' +
      '<label class="rsv-check"><input type="checkbox" name="entrega" required>' +
        '<span>Entiendo que estoy comprando un reloj que todavía se está fabricando y que ' +
        'la entrega está prevista ' + LAORA_ENTREGA + '.</span></label>' +

      '<button class="btn btn-carbon rsv-enviar" type="submit"' + (hayAlguno ? '' : ' disabled') + '>' +
        'Pagar · ' + euros(senal) + '</button>' +
      '<p class="rsv-error" id="pgError" hidden></p>' +
    '</form>' +
    '</div>';

  function impuestos(t) {
    var base = Math.round((t / (1 + LAORA_IVA / 100)) * 100) / 100;
    return '<dt class="rsv-menor">Base imponible</dt><dd class="rsv-menor">' + euros(base) + '</dd>' +
           '<dt class="rsv-menor">Impuesto (' + LAORA_IVA + ' %)</dt>' +
           '<dd class="rsv-menor">' + euros(Math.round((t - base) * 100) / 100) + '</dd>';
  }

  /* ---------- 6 · enviar ---------- */
  var form = document.getElementById('pgForm');
  var error = document.getElementById('pgError');
  var boton = form.querySelector('.rsv-enviar');
  var textoBoton = boton.textContent;

  function falla(texto) {
    error.textContent = texto;
    error.hidden = false;
    boton.disabled = false;
    boton.textContent = textoBoton;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    error.hidden = true;

    if (!form.checkValidity()) {
      var primero = form.querySelector(':invalid');
      if (primero) primero.focus();
      falla('Falta algo por rellenar o marcar.');
      return;
    }

    var d = new FormData(form);
    var elegido = d.get('metodo');
    if (!elegido || !laoraPagoListo(elegido)) {
      falla('Elige una forma de pago disponible.');
      return;
    }

    boton.disabled = true;
    boton.textContent = 'Un momento…';

    var pedido = {
      /* Varias líneas: lo entiende `laora-crear-pedido`. */
      lineas: detalle.map(function (x) {
        return { ref: x.ref, modelo: x.modelo, acabado: x.acabado,
                 esfera: x.esfera, extras: x.extras, cantidad: x.cantidad };
      }),
      precio_total: total,
      metodo: laoraPagoMetodoServidor(elegido),
      metodo_elegido: elegido,
      entrega_prometida: LAORA_ENTREGA,
      nombre: d.get('nombre'), email: d.get('email'), telefono: d.get('telefono'),
      direccion: d.get('direccion'), cp: d.get('cp'),
      poblacion: d.get('poblacion'), provincia: d.get('provincia')
    };

    if (typeof LAORA_SUPABASE_URL === 'undefined' || !LAORA_SUPABASE_URL) {
      falla('El sistema de pagos todavía no está conectado. No se te ha cobrado nada.');
      return;
    }

    function llama(funcion, cuerpo) {
      return fetch(LAORA_SUPABASE_URL + '/functions/v1/' + funcion, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: LAORA_SUPABASE_KEY },
        body: JSON.stringify(cuerpo)
      }).then(function (r) {
        return r.json().catch(function () { return {}; })
          .then(function (j) { return { ok: r.ok, estado: r.status, j: j }; });
      });
    }

    /* `laora-crear-pedido` acepta la cesta entera y es la que toca. Mientras
       no esté desplegada devuelve 404, y entonces se recae en la de siempre,
       que solo sabe de un reloj. Con más de uno se dice la verdad en vez de
       cobrar un pedido a medias. */
    llama('laora-crear-pedido', pedido).then(function (res) {
      if (res.estado === 404) {
        if (detalle.length > 1 || detalle[0].cantidad > 1) {
          falla('Por ahora solo podemos cobrar un reloj por pedido. Deja uno en la cesta ' +
                'y repite, o escríbenos y lo hacemos a mano. No se te ha cobrado nada.');
          return null;
        }
        var uno = detalle[0];
        return llama('laora-crear-reserva', {
          ref: uno.ref, modelo: uno.modelo, acabado: uno.acabado,
          precio_total: uno.subtotal, metodo: pedido.metodo,
          entrega_prometida: LAORA_ENTREGA,
          nombre: pedido.nombre, email: pedido.email, telefono: pedido.telefono,
          direccion: pedido.direccion, cp: pedido.cp,
          poblacion: pedido.poblacion, provincia: pedido.provincia
        });
      }
      return res;
    }).then(function (res) {
      if (!res) return;
      if (!res.ok) {
        falla((res.j && res.j.error ? res.j.error : 'No hemos podido crear el pedido') +
              '. No se te ha cobrado nada.');
        return;
      }
      /* La cesta se vacía solo cuando el servidor ha dicho que sí. */
      if (typeof laoraCarritoGuardar === 'function') laoraCarritoGuardar([]);
      location.href = res.j.url;
    }).catch(function () {
      falla('No hemos podido crear el pedido. No se te ha cobrado nada. Inténtalo otra vez.');
    });
  });
})();
