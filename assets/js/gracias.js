/* ============================================================
   laOra · Página de «reserva recibida»
   ------------------------------------------------------------
   Se llega aquí de dos formas:
     ?estado=pagada          → volvió de Mollie y el pago está hecho
     ?estado=pendiente       → eligió Bizum o transferencia
   Con ?metodo=bizum|transferencia se enseñan las instrucciones.

   Los datos de cobro salen de `pagos.js`, que es la única fuente.
   Antes estaban escritos aquí también y era pedir un despiste: el
   día que cambie el IBAN se cambia en un sitio, no en dos. Van en
   claro porque hay que dárselos al cliente igualmente; no son
   secretos. La clave de Mollie sí lo es y NO vive en el repo.
   ============================================================ */

var LAORA_COBRO = {
  bizum:   (typeof LAORA_PAGOS !== 'undefined' && LAORA_PAGOS.bizum.telefono) || '',
  iban:    (typeof LAORA_PAGOS !== 'undefined' && LAORA_PAGOS.transferencia.iban) || '',
  titular: (typeof LAORA_PAGOS !== 'undefined' && LAORA_PAGOS.transferencia.titular) || ''
};

(function () {
  var caja = document.getElementById('gracias');
  if (!caja) return;

  var p = new URLSearchParams(location.search);
  var estado = p.get('estado') || 'pendiente';
  var metodo = p.get('metodo') || '';
  var codigo = p.get('codigo') || '';
  var importe = p.get('importe') || '';

  var ref = codigo ? '<p class="rsv-codigo">Tu referencia: <b>' + codigo + '</b></p>' : '';

  if (estado === 'pagada') {
    caja.innerHTML =
      '<span class="rsv-eyebrow">Hecho</span>' +
      '<h1>Tu reloj está reservado.</h1>' +
      '<p class="rsv-lead">Hemos recibido tu señal y tu unidad queda apartada a tu nombre. ' +
      'Te hemos enviado un correo con el resumen y las condiciones.</p>' +
      ref +
      '<p>Te escribiremos cuando el reloj esté montado, para cobrarte el resto y enviártelo. ' +
      'Ni antes ni sin avisar.</p>' +
      '<p>Y si cambias de idea, tienes 14 días para decírnoslo y te devolvemos la señal entera. ' +
      'Un mensaje basta.</p>' +
      '<a class="btn btn-carbon" href="/">Volver a la colección</a>';
    return;
  }

  var instrucciones = '';
  if (metodo === 'bizum') {
    instrucciones = LAORA_COBRO.bizum
      ? '<div class="rsv-datos"><h2>Envíanos la señal por Bizum</h2>' +
        '<p class="rsv-dato"><span>Número</span><b>' + LAORA_COBRO.bizum + '</b></p>' +
        (importe ? '<p class="rsv-dato"><span>Importe</span><b>' + laoraEuros(Number(importe)) + '</b></p>' : '') +
        (codigo ? '<p class="rsv-dato"><span>Concepto</span><b>' + codigo + '</b></p>' : '') +
        '<p class="rsv-ojo">Pon la referencia en el concepto: es lo que nos permite ' +
        'reconocer tu pago sin tener que preguntarte.</p></div>'
      : '<div class="rsv-datos"><p>Te enviamos el número de Bizum por correo ahora mismo.</p></div>';
  } else if (metodo === 'transferencia') {
    instrucciones = LAORA_COBRO.iban
      ? '<div class="rsv-datos"><h2>Haz la transferencia</h2>' +
        '<p class="rsv-dato"><span>Titular</span><b>' + LAORA_COBRO.titular + '</b></p>' +
        '<p class="rsv-dato"><span>IBAN</span><b>' + LAORA_COBRO.iban + '</b></p>' +
        (importe ? '<p class="rsv-dato"><span>Importe</span><b>' + laoraEuros(Number(importe)) + '</b></p>' : '') +
        (codigo ? '<p class="rsv-dato"><span>Concepto</span><b>' + codigo + '</b></p>' : '') +
        '<p class="rsv-ojo">Pon la referencia en el concepto: es lo que nos permite ' +
        'reconocer tu pago sin tener que preguntarte.</p></div>'
      : '<div class="rsv-datos"><p>Te enviamos el IBAN por correo ahora mismo.</p></div>';
  }

  caja.innerHTML =
    '<span class="rsv-eyebrow">Reserva anotada</span>' +
    '<h1>Nos falta tu pago para apartarla.</h1>' +
    '<p class="rsv-lead">Tenemos tus datos. <b>La unidad no queda apartada hasta que veamos ' +
    'la señal</b>, así que te lo decimos claro en vez de dejarte pensar que ya está hecho.</p>' +
    ref +
    instrucciones +
    '<p>En cuanto llegue te confirmamos por correo. Con Bizum suele ser el mismo día; ' +
    'con transferencia, uno o dos días hábiles.</p>' +
    '<p>Si prefieres pagar con tarjeta y que quede confirmado al momento, vuelve atrás ' +
    'y elige esa opción.</p>' +
    /* Aquí había un botón de WhatsApp. El canal se quitó de toda la web, así
       que llevaba a un número que ya no se atiende desde aquí. */
    '<a class="btn btn-carbon" href="/coleccion.html">Volver a la colección</a>';
})();
