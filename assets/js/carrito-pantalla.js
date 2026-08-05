/* ============================================================
   laOra · LA PANTALLA DEL CARRITO
   ------------------------------------------------------------
   Pinta lo que hay en la cesta, deja cambiar cantidades y quitar
   líneas, y suma. La cesta la lleva `carrito.js`, que es el de la web
   anterior y guarda en el propio navegador.

   El botón de pagar se queda desactivado mientras no exista la pantalla
   de cobro: es preferible a mandar a alguien a un 404 desde el paso de
   pagar.
   ============================================================ */
(function () {
  'use strict';

  var lista = document.querySelector('[data-lineas]');
  var vacio = document.querySelector('[data-vacio]');
  var resumen = document.querySelector('[data-resumen]');
  var total = document.querySelector('[data-total]');
  if (!lista) return;

  function euros(v) {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency', currency: 'EUR',
      minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2
    }).format(v || 0);
  }

  function el(t, c, txt) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (txt !== undefined) e.textContent = txt;
    return e;
  }

  function pintar() {
    var lineas = laoraCarritoLeer();
    lista.innerHTML = '';

    lineas.forEach(function (l, i) {
      var li = el('li', 'ca-linea');

      if (l.foto) {
        var img = document.createElement('img');
        img.src = l.foto;
        img.alt = l.nombre || 'Reloj laOra';
        li.appendChild(img);
      } else {
        li.appendChild(el('div'));
      }

      var medio = el('div');
      medio.appendChild(el('h2', '', l.nombre || 'Reloj laOra'));
      var detalle = [l.acabado, l.correa].filter(Boolean).join(' · ');
      if (detalle) medio.appendChild(el('p', 'ca-detalle', detalle));
      if (l.ref) medio.appendChild(el('p', 'ca-ref', 'Ref. ' + l.ref));
      li.appendChild(medio);

      var lado = el('div', 'ca-lado');
      lado.appendChild(el('p', 'ca-precio', euros(Number(l.precio) * (l.cantidad || 1))));

      var cant = el('div', 'ca-cantidad');
      var menos = el('button', '', '−');
      menos.type = 'button';
      menos.setAttribute('aria-label', 'Quitar una unidad');
      var n = el('span', '', String(l.cantidad || 1));
      var mas = el('button', '', '+');
      mas.type = 'button';
      mas.setAttribute('aria-label', 'Añadir una unidad');
      menos.addEventListener('click', function () {
        var c = (l.cantidad || 1) - 1;
        if (c < 1) laoraCarritoQuitar(i); else laoraCarritoCantidad(i, c);
        pintar();
      });
      mas.addEventListener('click', function () {
        laoraCarritoCantidad(i, (l.cantidad || 1) + 1);
        pintar();
      });
      cant.appendChild(menos); cant.appendChild(n); cant.appendChild(mas);
      lado.appendChild(cant);

      var quitar = el('button', 'ca-quitar', 'Quitar');
      quitar.type = 'button';
      quitar.addEventListener('click', function () { laoraCarritoQuitar(i); pintar(); });
      lado.appendChild(quitar);

      li.appendChild(lado);
      lista.appendChild(li);
    });

    var hay = lineas.length > 0;
    if (vacio) vacio.hidden = hay;
    if (resumen) resumen.hidden = !hay;
    if (total) total.textContent = euros(laoraCarritoTotal());
    if (typeof laoraCarritoPintarContador === 'function') laoraCarritoPintarContador();
  }

  /* ---------- PAGAR ----------
     PayPal se puede abrir hoy sin clave ni servidor: un enlace de
     paypal.me con el importe, a la cuenta @saneascom del Grupo Saneas.

     LO QUE ESTE CAMINO NO HACE, y hay que saberlo: PayPal cobra, pero
     no le dice a nadie QUÉ se ha comprado ni A DÓNDE se envía. El
     importe llega suelto. Por eso, antes de abrir el pago, la
     referencia de lo elegido se copia al concepto y se le pide a quien
     compra que la deje puesta; y aun así hace falta que alguien cruce
     el ingreso con el pedido a mano.

     Lo que resuelve eso de verdad es la pasarela con Mollie, que sí
     devuelve el pedido pagado. Está pendiente de su clave. */
  var botonPagar = document.querySelector('[data-pagar]');
  if (botonPagar) {
    var lineas = laoraCarritoLeer();
    if (lineas.length) {
      botonPagar.disabled = false;
      botonPagar.textContent = 'Pagar con PayPal';
      botonPagar.addEventListener('click', function () {
        var total = laoraCarritoTotal();
        var refs = laoraCarritoLeer().map(function (l) {
          return l.ref + (l.cantidad > 1 ? ' x' + l.cantidad : '');
        }).join(', ');
        /* el importe con punto decimal, que es como lo espera paypal.me */
        var url = 'https://www.paypal.me/saneascom/' + total.toFixed(2) + 'EUR';
        try { navigator.clipboard.writeText(refs); } catch (e) {}
        window.open(url, '_blank', 'noopener');
      });
      var nota = document.querySelector('.ca-pendiente');
      if (nota) {
        nota.textContent = 'Se abre PayPal con el importe. Pon en el concepto tu referencia: ' + 
          lineas.map(function (l) { return l.ref; }).join(', ') +
          ' — la copiamos al portapapeles al pulsar.';
      }
    }
  }

  pintar();
})();
