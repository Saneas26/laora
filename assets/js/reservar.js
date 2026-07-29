/* ============================================================
   laOra · Checkout de reserva
   ------------------------------------------------------------
   Compra directa: un reloj, un acabado, una señal. Sin carrito.

   Tres formas de pagar:
     mollie        → pasarela (tarjeta, Bizum de pasarela, etc.)
     bizum         → Bizum manual al teléfono de laOra, sin comisión
     transferencia → transferencia al IBAN de laOra, sin comisión

   Las dos manuales NO cobran aquí: crean la reserva en estado
   «pendiente de pago» y le enseñan al cliente las instrucciones.
   La reserva no vale hasta que Óscar ve el dinero y la confirma.
   ============================================================ */
(function () {
  var caja = document.getElementById('reserva');
  if (!caja) return;

  var params = new URLSearchParams(location.search);
  var ref = params.get('ref');
  var acabado = params.get('acabado');
  var a = (typeof laoraAcabado === 'function') ? laoraAcabado(ref, acabado) : null;

  /* --- Puerta: sin precio cerrado o sin fecha de entrega, no se cobra --- */
  if (!a || !laoraSePuedeReservar(ref, acabado)) {
    caja.innerHTML =
      '<div class="rsv-aviso">' +
      '<h1>Este acabado todavía no está a la venta</h1>' +
      '<p>Aún no hemos cerrado precio y fecha de entrega, así que no podemos ' +
      'cobrarte nada. Déjanos tu correo y eres el primero en saberlo.</p>' +
      '<a class="btn btn-carbon" href="/' + (ref ? '?modelo=' + encodeURIComponent(ref) : '') +
      '#interesados">Avísame del estreno</a>' +
      '</div>';
    return;
  }

  var senal = laoraSenal(a.precio);
  var resto = Math.round((a.precio - senal) * 100) / 100;
  var baseImponible = Math.round((a.precio / (1 + LAORA_IVA / 100)) * 100) / 100;
  var cuotaIva = Math.round((a.precio - baseImponible) * 100) / 100;

  caja.innerHTML =
    '<div class="rsv-grid">' +

    '<div class="rsv-resumen">' +
      '<span class="rsv-eyebrow">Tu reserva</span>' +
      '<h1>' + a.ref + ' «' + a.modelo + '»</h1>' +
      '<p class="rsv-acabado">Acabado <b>' + a.acabado + '</b></p>' +
      '<dl class="rsv-cuentas">' +
        '<dt>Precio del reloj</dt><dd>' + laoraEuros(a.precio) + '</dd>' +
        '<dt class="rsv-menor">Base imponible</dt><dd class="rsv-menor">' + laoraEuros(baseImponible) + '</dd>' +
        '<dt class="rsv-menor">IVA (' + LAORA_IVA + ' %)</dt><dd class="rsv-menor">' + laoraEuros(cuotaIva) + '</dd>' +
        '<dt class="rsv-total">Pagas ahora (' + LAORA_SENAL_PORCENTAJE + ' %)</dt>' +
        '<dd class="rsv-total">' + laoraEuros(senal) + '</dd>' +
        '<dt>Pagas al recibirlo</dt><dd>' + laoraEuros(resto) + '</dd>' +
      '</dl>' +
      '<p class="rsv-entrega"><b>Entrega:</b> ' + LAORA_ENTREGA + '</p>' +
      '<p class="rsv-desist">Puedes echarte atrás en los 14 días siguientes sin dar ' +
      'explicaciones y te devolvemos la señal <b>entera</b>. No es una promesa nuestra: ' +
      'es tu derecho de desistimiento.</p>' +
    '</div>' +

    '<form class="rsv-form" id="rsvForm" novalidate>' +
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

      '<h2>Cómo quieres pagar la señal</h2>' +
      '<div class="rsv-pagos">' +
        '<label class="rsv-pago"><input type="radio" name="metodo" value="mollie" checked>' +
          '<span><b>Tarjeta o Bizum</b><small>Pago inmediato y seguro. La reserva queda ' +
          'confirmada al momento.</small></span></label>' +
        '<label class="rsv-pago"><input type="radio" name="metodo" value="bizum">' +
          '<span><b>Bizum a mano</b><small>Te damos el número y nos envías la señal tú. ' +
          'Confirmamos en cuanto llegue, normalmente el mismo día.</small></span></label>' +
        '<label class="rsv-pago"><input type="radio" name="metodo" value="transferencia">' +
          '<span><b>Transferencia</b><small>Te damos el IBAN. Confirmamos en cuanto llegue, ' +
          'de uno a dos días hábiles.</small></span></label>' +
      '</div>' +

      '<label class="rsv-check"><input type="checkbox" name="condiciones" required>' +
        '<span>He leído y acepto las <a href="/condiciones-de-venta.html" target="_blank">' +
        'condiciones de venta</a> y la <a href="/privacidad.html" target="_blank">' +
        'política de privacidad</a>.</span></label>' +
      '<label class="rsv-check"><input type="checkbox" name="entrega" required>' +
        '<span>Entiendo que estoy reservando un reloj que todavía se está fabricando y que ' +
        'la entrega está prevista ' + LAORA_ENTREGA + '.</span></label>' +

      '<button class="btn btn-carbon rsv-enviar" type="submit">' +
        'Reservar · ' + laoraEuros(senal) + '</button>' +
      '<p class="rsv-error" id="rsvError" hidden></p>' +
    '</form>' +
    '</div>';

  var form = document.getElementById('rsvForm');
  var error = document.getElementById('rsvError');
  var boton = form.querySelector('.rsv-enviar');

  function fallo(texto) {
    error.textContent = texto;
    error.hidden = false;
    boton.disabled = false;
    boton.textContent = 'Reservar · ' + laoraEuros(senal);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    error.hidden = true;

    if (!form.checkValidity()) {
      var primero = form.querySelector(':invalid');
      if (primero) primero.focus();
      fallo('Falta algo por rellenar o marcar.');
      return;
    }

    boton.disabled = true;
    boton.textContent = 'Un momento…';

    var d = new FormData(form);
    var reserva = {
      ref: a.ref,
      modelo: a.modelo,
      acabado: a.acabado,
      precio_total: a.precio,
      senal: senal,
      metodo: d.get('metodo'),
      entrega_prometida: LAORA_ENTREGA,
      nombre: d.get('nombre'),
      email: d.get('email'),
      telefono: d.get('telefono'),
      direccion: d.get('direccion'),
      cp: d.get('cp'),
      poblacion: d.get('poblacion'),
      provincia: d.get('provincia')
    };

    if (!LAORA_SUPABASE_URL) {
      fallo('El sistema de reservas todavía no está conectado. Escríbenos por WhatsApp y lo hacemos a mano.');
      return;
    }

    fetch(LAORA_SUPABASE_URL + '/functions/v1/crear-reserva', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: LAORA_SUPABASE_KEY },
      body: JSON.stringify(reserva)
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.j && res.j.error ? res.j.error : 'error');
        /* Mollie devuelve la URL de su pasarela; los métodos manuales, la página de gracias. */
        location.href = res.j.url;
      })
      .catch(function () {
        fallo('No hemos podido crear la reserva. No se te ha cobrado nada. Inténtalo otra vez o escríbenos por WhatsApp.');
      });
  });
})();
