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

   Y desde el 19/08/2026 el pago es de verdad: `pagar-pedido` crea el
   cobro en Mollie con el importe que hay en la base —aquí no viaja
   ni un número— y devuelve la dirección del checkout. Se puede pagar
   con tarjeta, Bizum, PayPal o con Klarna en tres plazos.

   La cesta la sigue llevando `carrito.js`, en el propio navegador. Eso
   es lo que permite que quien se va a buscar el enlace del correo
   vuelva y lo encuentre todo como estaba.
   ============================================================ */
(function () {
  'use strict';

  var API = 'https://uikanfvigunjhzibnhxf.supabase.co/functions/v1/';
  var FUNCION = API + 'crear-pedido';
  var COBRO = API + 'pagar-pedido';

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

  /* EL PEDIDO PENDIENTE SE RECUERDA.
     La cesta se vacía al saltar a la pasarela, así que quien cierre el
     checkout sin pagar se quedaría sin cesta Y sin manera de volver a
     pagar lo que ya ha pedido. Se guarda aquí el número, y al volver a
     esta pantalla aparece otra vez el botón de pagar. El servidor se
     encarga de lo demás: si ese pago sigue abierto devuelve el mismo
     checkout, y si ya estaba pagado lo dice y aquí se olvida. */
  var LLAVE = 'laora.pedido';
  function recordar(p) {
    try { localStorage.setItem(LLAVE, JSON.stringify(p)); } catch (e) {}
  }
  function recordado() {
    try { return JSON.parse(localStorage.getItem(LLAVE) || 'null'); } catch (e) { return null; }
  }
  function olvidar() {
    try { localStorage.removeItem(LLAVE); } catch (e) {}
  }

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
      var detalle = [l.detalle, l.correa].filter(Boolean).join(' · ');
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
        if (formCodigo) formCodigo.hidden = false;
        decir(avisoEntrar, 'Te hemos enviado un correo a ' + correo +
          '. Si lo abres en este mismo dispositivo, el enlace te trae de vuelta con la ' +
          'cesta intacta. Y si lo lees en el móvil, escribe aquí abajo el código: sirve igual.');
      }).catch(function () {
        boton.disabled = false;
        decir(avisoEntrar, 'No hemos podido enviar el enlace. Inténtalo dentro de un momento.', true);
      });
    });
  }

  /* Entrar con el código, para quien no pueda con el enlace. Aquí
     importa más que en ningún sitio: quien lee el correo en el móvil
     mientras compraba en el ordenador perdería la cesta. */
  var formCodigo = document.querySelector('[data-form-codigo]');
  var avisoCodigo = document.querySelector('[data-aviso-codigo]');

  if (formCodigo) {
    formCodigo.addEventListener('submit', function (e) {
      e.preventDefault();
      var correo = (formEntrar.querySelector('[data-correo]').value || '').trim();
      var codigo = (formCodigo.querySelector('[data-codigo]').value || '').trim();
      if (!codigo) { decir(avisoCodigo, 'Escribe el código que te ha llegado.', true); return; }

      var b = formCodigo.querySelector('[data-entrar-codigo]');
      b.disabled = true;
      decir(avisoCodigo, 'Comprobando…');

      laoraSesion.entrarConCodigo(correo, codigo).then(function () {
        return laoraSesion.quienSoy();
      }).then(function (u) {
        if (!u) throw new Error('codigo');
        decir(avisoCodigo, '');
        formCodigo.hidden = true;
        decir(avisoEntrar, 'Ya estás dentro como ' + u.email + '.');
        pasoEntrar.hidden = true;
        pasoDatos.hidden = false;
        var quien = document.querySelector('[data-quien]');
        if (quien) quien.textContent = 'Estás dentro como ' + u.email + '.';
        laoraSesion.consultar('socios?select=*&limit=1').then(function (filas) {
          if (filas && filas.length) rellenar(filas[0]);
        });
        pasoDatos.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }).catch(function () {
        b.disabled = false;
        decir(avisoCodigo, 'Ese código no vale. Comprueba que lo has copiado entero, ' +
                           'y que es el del último correo.', true);
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
        metodo: 'tarjeta',   // la intención; la definitiva la elige en el paso 4
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
        recordar({ numero: PEDIDO.numero, total: PEDIDO.total });
        decir(avisoDatos, '');
        formDatos.hidden = true;
        pasoDatos.hidden = true;
        pasoPagar.hidden = false;
        document.querySelector('[data-numero]').textContent = PEDIDO.numero;
        document.querySelector('[data-total-final]').textContent = euros(PEDIDO.total);
        var enBoton = document.querySelector('[data-total-boton]');
        if (enBoton) enBoton.textContent = euros(PEDIDO.total);
        pintarPlazo(PEDIDO.total);
        pintarMetodo();
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
     Aquí no se calcula nada ni se manda ningún importe: solo el número
     del pedido. El dinero lo pone el servidor leyéndolo de la base,
     que es donde lo escribió `crear-pedido` desde el catálogo.

     Dos caminos: el pago normal —que Mollie resuelve con lo que tenga
     activo: tarjeta, Bizum, PayPal— y Klarna en tres plazos, que no
     cobra al comprar sino cuando el reloj sale hacia su casa. */
  var metodo = '';
  var avisoPagar = document.querySelector('[data-aviso-pagar]');
  var cajaMetodos = document.querySelector('[data-metodos]');
  var cajaManual = document.querySelector('[data-manual]');

  var aMano = function () { return metodo === 'bizum' || metodo === 'paypal'; };

  function pintarMetodo() {
    if (!cajaMetodos) return;
    Array.prototype.forEach.call(cajaMetodos.querySelectorAll('button'), function (b) {
      b.setAttribute('aria-pressed', String((b.dataset.metodo || '') === metodo));
    });
    /* El botón dice lo que va a pasar: con Bizum no se paga aquí, se
       enseñan los datos. Prometer «Pagar» y no cobrar nada confunde. */
    var b = document.querySelector('[data-pagar]');
    if (b) {
      b.firstChild.nodeValue = aMano() ? 'Ver cómo pagar ' : 'Pagar ';
      var tot = b.querySelector('[data-total-boton]');
      if (tot) tot.hidden = aMano();
    }
    if (cajaManual && !aMano()) cajaManual.hidden = true;
  }

  /* Los datos del pago a mano los pone el servidor, no esta página. */
  function pintarAMano(d) {
    if (!cajaManual) return;
    document.querySelector('[data-manual-importe]').textContent =
      String(d.importe).replace('.', ',') + ' €';
    var n = String(d.bizum || '');
    document.querySelector('[data-manual-bizum]').textContent =
      n.length === 9 ? n.slice(0, 3) + ' ' + n.slice(3, 6) + ' ' + n.slice(6) : n;
    document.querySelector('[data-manual-concepto]').textContent = d.concepto;
    document.querySelector('[data-manual-paypal]').href = d.paypal;
    cajaManual.hidden = false;
    cajaManual.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  var copiar = document.querySelector('[data-copiar]');
  if (copiar) {
    copiar.addEventListener('click', function () {
      var t = document.querySelector('[data-manual-concepto]').textContent;
      try {
        navigator.clipboard.writeText(t);
        copiar.textContent = 'copiado';
        setTimeout(function () { copiar.textContent = 'copiar'; }, 2000);
      } catch (e) {}
    });
  }

  if (cajaMetodos) {
    cajaMetodos.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      metodo = b.dataset.metodo || '';
      pintarMetodo();
    });
  }

  /* El tercio se redondea al céntimo HACIA ARRIBA, como en la ficha:
     tres plazos nunca pueden sumar menos que el total. */
  function pintarPlazo(total) {
    var p = document.querySelector('[data-plazo]');
    if (p) p.textContent = euros(Math.ceil(Number(total) / 3 * 100) / 100);
  }

  var botonPagar = document.querySelector('[data-pagar]');
  if (botonPagar) {
    botonPagar.addEventListener('click', function () {
      if (!PEDIDO) return;
      botonPagar.disabled = true;
      decir(avisoPagar, 'Abriendo el pago…');

      laoraSesion.token().then(function (t) {
        if (!t) throw new Error('sin sesión');
        return fetch(COBRO, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + t },
          body: JSON.stringify({ numero: PEDIDO.numero, metodo: metodo })
        });
      }).then(function (r) {
        return r.json().then(function (d) { return { ok: r.ok, d: d }; });
      }).then(function (res) {
        if (res.d && res.d.pagado) { olvidar(); throw new Error('Este pedido ya está pagado. Gracias.'); }

        /* A mano no se va a ninguna parte: los datos se enseñan aquí. */
        if (res.ok && res.d.manual) {
          laoraCarritoVaciar();
          pintarAMano(res.d);
          decir(avisoPagar, '');
          botonPagar.disabled = false;
          return;
        }

        if (!res.ok || !res.d.url) throw new Error(res.d && res.d.error ? res.d.error : 'no se pudo abrir el pago');
        /* La cesta ya no hace falta: lo que vale a partir de aquí es el
           pedido, que está escrito y se ve en «tu cuenta». */
        laoraCarritoVaciar();
        window.location.href = res.d.url;
      }).catch(function (err) {
        botonPagar.disabled = false;
        var m = String(err && err.message || '');
        decir(avisoPagar, m === 'sin sesión'
          ? 'Tu sesión ha caducado. Vuelve a entrar con tu correo.'
          : (m || 'No hemos podido abrir el pago. Inténtalo en un momento.'), true);
      });
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

  /* ¿Quedó un pedido hecho y sin pagar? Se enseña el paso del pago tal
     como estaba, para que pueda terminar sin repetir nada. */
  (function pendiente() {
    var p = recordado();
    if (!p || !p.numero || !laoraSesion.hay()) return;
    if (laoraCarritoLeer().length) return;   // hay cesta nueva: manda ella
    PEDIDO = p;
    if (continuar) continuar.hidden = true;
    pasoPagar.hidden = false;
    document.querySelector('[data-numero]').textContent = p.numero;
    document.querySelector('[data-total-final]').textContent = euros(p.total);
    var enBoton = document.querySelector('[data-total-boton]');
    if (enBoton) enBoton.textContent = euros(p.total);
    pintarPlazo(p.total);
    pintarMetodo();
    decir(avisoPagar, 'Este pedido está hecho y a la espera de pago.');
  })();

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
