/* ============================================================
   laOra · LA PANTALLA DEL CARRITO
   ------------------------------------------------------------
   Pinta lo que hay en la cesta, deja cambiar cantidades y quitar
   líneas, y lleva la compra hasta el final por tres pasos: entrar,
   decir a dónde va, y pagar.

   El pedido se ESCRIBE antes de cobrar. Hasta el 06/08/2026 esta
   pantalla abría PayPal y ahí acababa todo: llegaba un ingreso suelto
   sin saber qué se había comprado ni a dónde mandarlo. Ahora la Edge
   Function `crear-pedido` guarda el pedido —recalculando el precio
   desde el catálogo, sin fiarse de lo que diga este navegador— y solo
   entonces se abre el pago.

   La cesta la sigue llevando `carrito.js`, en el propio navegador. Eso
   es lo que permite que quien se va a buscar el enlace del correo
   vuelva y lo encuentre todo como estaba.
   ============================================================ */
(function () {
  'use strict';

  var FUNCION = 'https://uikanfvigunjhzibnhxf.supabase.co/functions/v1/crear-pedido';

  var lista = document.querySelector('[data-lineas]');
  var vacio = document.querySelector('[data-vacio]');
  var resumen = document.querySelector('[data-resumen]');
  var total = document.querySelector('[data-total]');
  if (!lista) return;

  var pasoEntrar = document.querySelector('[data-paso-entrar]');
  var pasoDatos = document.querySelector('[data-paso-datos]');
  var pasoPagar = document.querySelector('[data-paso-pagar]');
  var continuar = document.querySelector('[data-continuar]');

  var PEDIDO = null;   // {numero, total} una vez hecho

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

  function decir(caja, texto, malo) {
    if (!caja) return;
    caja.textContent = texto || '';
    caja.hidden = !texto;
    caja.classList.toggle('ca-mal', !!malo);
  }

  /* ---------- 1. lo elegido ---------- */
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
        volverAlPrincipio();
      });
      mas.addEventListener('click', function () {
        laoraCarritoCantidad(i, (l.cantidad || 1) + 1);
        volverAlPrincipio();
      });
      cant.appendChild(menos); cant.appendChild(n); cant.appendChild(mas);
      lado.appendChild(cant);

      var quitar = el('button', 'ca-quitar', 'Quitar');
      quitar.type = 'button';
      quitar.addEventListener('click', function () { laoraCarritoQuitar(i); volverAlPrincipio(); });
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

  /* Si se toca la cesta después de haber hecho el pedido, lo que hay
     escrito ya no cuadra con lo que se ve. Se vuelve al principio: es
     preferible a cobrar por algo distinto de lo elegido. */
  function volverAlPrincipio() {
    PEDIDO = null;
    if (pasoPagar) pasoPagar.hidden = true;
    if (pasoDatos) pasoDatos.hidden = true;
    if (pasoEntrar) pasoEntrar.hidden = true;
    if (continuar) { continuar.hidden = false; continuar.disabled = false; }
    pintar();
  }

  /* ---------- 2. entrar ---------- */
  var formEntrar = document.querySelector('[data-form-entrar]');
  var avisoEntrar = document.querySelector('[data-aviso-entrar]');

  if (formEntrar) {
    formEntrar.addEventListener('submit', function (e) {
      e.preventDefault();
      var campo = formEntrar.querySelector('[data-correo]');
      var correo = (campo.value || '').trim();
      if (!correo || correo.indexOf('@') < 1) { decir(avisoEntrar, 'Escribe un correo válido.', true); return; }

      var boton = formEntrar.querySelector('[data-enviar-enlace]');
      boton.disabled = true;
      decir(avisoEntrar, 'Enviando…');

      /* Vuelve AQUÍ, no a la cuenta: así no pierde la compra. */
      laoraSesion.pedirEnlace(correo, '/carrito').then(function () {
        formEntrar.hidden = true;
        decir(avisoEntrar, 'Te hemos enviado un enlace a ' + correo +
          '. Ábrelo desde este mismo dispositivo y vuelves aquí, con tu cesta intacta.');
      }).catch(function () {
        boton.disabled = false;
        decir(avisoEntrar, 'No hemos podido enviar el enlace. Inténtalo dentro de un momento.', true);
      });
    });
  }

  /* ---------- 3. a dónde va ---------- */
  var formDatos = document.querySelector('[data-form-datos]');
  var avisoDatos = document.querySelector('[data-aviso-datos]');
  var quiereFactura = document.querySelector('[data-quiere-factura]');
  var bloqueFactura = document.querySelector('[data-bloque-factura]');

  if (quiereFactura && bloqueFactura) {
    quiereFactura.addEventListener('change', function () {
      bloqueFactura.hidden = !quiereFactura.checked;
    });
  }

  function valor(nombre) {
    var i = formDatos && formDatos.querySelector('[data-c="' + nombre + '"]');
    return i ? (i.value || '').trim() : '';
  }

  /* Rellena lo que ya sepamos de quien compra: si compró una vez, no
     tiene que volver a escribir su dirección. */
  function rellenar(socio) {
    if (!socio || !formDatos) return;
    ['nombre', 'apellidos', 'telefono', 'nif', 'direccion', 'cp', 'poblacion', 'provincia', 'pais']
      .forEach(function (k) {
        var i = formDatos.querySelector('[data-c="' + k + '"]');
        if (i && !i.value && socio[k]) i.value = socio[k];
      });
  }

  if (formDatos) {
    formDatos.addEventListener('submit', function (e) {
      e.preventDefault();
      var boton = formDatos.querySelector('[data-hacer-pedido]');
      boton.disabled = true;
      decir(avisoDatos, 'Guardando tu pedido…');

      var cuerpo = {
        metodo: 'paypal',
        lineas: laoraCarritoLeer().map(function (l) {
          return { ref: l.ref, cantidad: l.cantidad || 1 };
        }),
        envio: {
          nombre: valor('nombre'), apellidos: valor('apellidos'),
          telefono: valor('telefono'), nif: valor('nif'),
          direccion: valor('direccion'), cp: valor('cp'),
          poblacion: valor('poblacion'), provincia: valor('provincia'),
          pais: valor('pais') || 'España'
        }
      };
      if (quiereFactura && quiereFactura.checked) {
        cuerpo.factura = {
          nombre: valor('fac_nombre'), nif: valor('fac_nif'),
          direccion: valor('fac_direccion'), cp: valor('fac_cp'),
          poblacion: valor('fac_poblacion'), provincia: valor('fac_provincia')
        };
      }

      laoraSesion.token().then(function (t) {
        if (!t) throw new Error('sin sesión');
        return fetch(FUNCION, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + t },
          body: JSON.stringify(cuerpo)
        });
      }).then(function (r) {
        return r.json().then(function (d) { return { ok: r.ok, d: d }; });
      }).then(function (res) {
        if (!res.ok || !res.d.ok) throw new Error(res.d && res.d.error ? res.d.error : 'no se pudo');
        PEDIDO = res.d;
        decir(avisoDatos, '');
        formDatos.hidden = true;
        pasoDatos.hidden = true;
        pasoPagar.hidden = false;
        document.querySelector('[data-numero]').textContent = PEDIDO.numero;
        document.querySelector('[data-total-final]').textContent = euros(PEDIDO.total);
        pasoPagar.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }).catch(function (err) {
        boton.disabled = false;
        var m = String(err && err.message || '');
        decir(avisoDatos, m === 'sin sesión'
          ? 'Tu sesión ha caducado. Vuelve a entrar con tu correo.'
          : (m || 'No hemos podido guardar el pedido. Inténtalo en un momento.'), true);
        if (m === 'sin sesión') { pasoDatos.hidden = true; pasoEntrar.hidden = false; }
      });
    });
  }

  /* ---------- 4. pagar ----------
     PayPal se abre sin clave ni servidor: un enlace de paypal.me con el
     importe, a la cuenta @saneascom del Grupo Saneas.

     LO QUE ESTE CAMINO NO HACE: PayPal cobra, pero no dice qué se ha
     comprado. Por eso el número del pedido va al portapapeles y se pide
     ponerlo en el concepto; y aun así hay que cruzar el ingreso con el
     pedido a mano, desde el panel. Lo que lo resuelve de verdad es la
     pasarela con Mollie, que sí devuelve el pedido pagado. */
  var botonPagar = document.querySelector('[data-pagar]');
  if (botonPagar) {
    botonPagar.addEventListener('click', function () {
      if (!PEDIDO) return;
      try { navigator.clipboard.writeText(PEDIDO.numero); } catch (e) {}
      window.open('https://www.paypal.me/saneascom/' + Number(PEDIDO.total).toFixed(2) + 'EUR',
                  '_blank', 'noopener');
    });
  }

  /* ---------- el hilo que une los pasos ---------- */
  if (continuar) {
    continuar.addEventListener('click', function () {
      if (!laoraCarritoLeer().length) return;
      continuar.hidden = true;
      if (laoraSesion.hay()) {
        pasoDatos.hidden = false;
        pasoDatos.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        pasoEntrar.hidden = false;
        pasoEntrar.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  /* Si venimos del enlace del correo, se recoge la sesión y se salta
     directo a los datos: quien acaba de entrar ya sabe a qué venía. */
  var acabaDeEntrar = laoraSesion.recoger();

  pintar();

  if (laoraSesion.hay() && laoraCarritoLeer().length) {
    laoraSesion.quienSoy().then(function (u) {
      if (!u) return;
      var quien = document.querySelector('[data-quien]');
      if (quien) quien.textContent = 'Estás dentro como ' + u.email + '.';
      if (acabaDeEntrar) {
        continuar.hidden = true;
        pasoDatos.hidden = false;
      }
      return laoraSesion.consultar('socios?select=*&limit=1');
    }).then(function (filas) {
      if (filas && filas.length) rellenar(filas[0]);
    });
  }
})();
