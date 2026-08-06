/* ============================================================
   laOra · EL CONFIGURADOR, EL MISMO PARA TODOS LOS MODELOS
   ------------------------------------------------------------
   Sirve a /lunar, /cero-cero, /precisa, /trinchera y /bitacora.
   Todo lo que pinta sale del <script type="application/json"
   data-cfg> que escribe `herramientas/generar_configuradores.py`
   desde `assets/datos/catalogo.json`. Aquí no hay ni un precio, ni
   un nombre, ni una foto, ni una referencia escritos a mano.

   LAS DOS REGLAS DE LA PÁGINA, que son las que pidió Óscar:
     · elijas lo que elijas, la pantalla NO se mueve;
     · el precio de lo elegido está SIEMPRE a la vista.

   Por eso aquí no hay ni un `scrollTo`, ni un `scrollIntoView`, ni
   nada que abra o cierre bloques: cambiar de opción solo cambia la
   foto, la muestra y las cifras. Lo que se ve, se queda donde está.

   Si este fichero no llega a cargarse, la página se sigue leyendo:
   salen la primera foto, el precio de la combinación de partida y
   todas las opciones. Lo único que se pierde es poder cambiarlas.
   ============================================================ */
(function () {
  'use strict';

  var caja = document.querySelector('[data-cfg]');
  if (!caja) return;

  var D;
  try { D = JSON.parse(caja.textContent); } catch (e) { return; }
  if (!D || !D.acabados || !D.correas) return;

  var elFoto = document.querySelector('[data-foto]');
  var elViendo = document.querySelector('[data-viendo]');
  var elTira = document.querySelector('[data-muestra-tira]');
  var elTiraNombre = document.querySelector('[data-muestra-nombre]');
  var elPrecio = document.querySelector('[data-precio]');
  var elEleccion = document.querySelector('[data-eleccion]');
  var elRefs = document.querySelectorAll('[data-ref]');
  var elNota = document.querySelector('[data-nota]');
  var elFicha = document.querySelector('[data-ficha]');
  var elRotuloCorrea = document.querySelector('[data-rotulo-correa]');
  var elReservar = document.querySelector('[data-reservar]');

  var botonesAcabado = document.querySelectorAll('[data-acabado]');
  var botonesCorrea = document.querySelectorAll('[data-correa]');

  var acabado = D.inicial.acabado;
  var correa = D.inicial.correa;

  function precio(a, c) {
    var lista = D.precios[a] || [];
    var v = lista[c];
    return (v === null || v === undefined) ? null : v;
  }

  function hayAlguna(a) {
    for (var i = 0; i < D.correas.length; i++) if (precio(a, i) !== null) return i;
    return -1;
  }

  function cuantas(a) {
    var n = 0;
    for (var i = 0; i < D.correas.length; i++) if (precio(a, i) !== null) n++;
    return n;
  }

  function euros(v) {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency', currency: 'EUR',
      minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2
    }).format(v);
  }

  /* La referencia y la foto vienen YA RESUELTAS del generador, una por
     cada pareja de acabado y correa. Antes se componían aquí, con una
     segunda copia de las reglas de la hoja de materiales, y las dos
     copias se desviaron: el segundo Cenit del Precisa salía `C01`
     donde la hoja dice `C02`, porque el número se sacaba de la correa.
     Ahora la regla vive en un solo sitio, en Python. */
  function referencia() {
    var a = D.acabados[acabado];
    return (a.refs && a.refs[correa]) || '—';
  }

  function foto() {
    var a = D.acabados[acabado];
    return (a.fotos && a.fotos[correa]) || a.foto;
  }

  function pintar() {
    var a = D.acabados[acabado];
    var c = D.correas[correa];
    var p = precio(acabado, correa);

    /* la foto, con un fundido corto para que el cambio no dé un salto */
    var nueva = foto();
    if (elFoto && elFoto.getAttribute('src') !== nueva) {
      elFoto.classList.add('cambiando');
      var siguiente = new Image();
      siguiente.onload = function () {
        elFoto.src = nueva;
        elFoto.classList.remove('cambiando');
      };
      siguiente.onerror = function () { elFoto.classList.remove('cambiando'); };
      siguiente.src = nueva;
    }
    if (elFoto) elFoto.alt = 'Reloj laOra ' + D.modelo + ', acabado ' + a.nombre + ', con ' + c.nombre.toLowerCase();

    if (elViendo) elViendo.innerHTML = '<b>' + a.nombre + '</b> · ' + c.nombre;
    if (elTira) elTira.setAttribute('style', 'background:' + c.muestra);
    if (elTiraNombre) elTiraNombre.textContent = c.nombre;

    if (elPrecio) elPrecio.textContent = p === null ? '—' : euros(p);
    if (elEleccion) elEleccion.textContent = a.nombre + ' · ' + c.nombre;
    for (var i = 0; i < elRefs.length; i++) elRefs[i].textContent = referencia();
    if (elNota) elNota.textContent = a.resumen || '';

    /* la ficha corta del acabado */
    if (elFicha) {
      elFicha.innerHTML = '';
      (a.ficha || []).forEach(function (par) {
        var dt = document.createElement('dt'); dt.textContent = par[0];
        var dd = document.createElement('dd'); dd.textContent = par[1];
        elFicha.appendChild(dt); elFicha.appendChild(dd);
      });
    }

    /* cuántas correas tiene este acabado: si solo tiene una, se dice,
       para que no parezca que las demás se han roto. Y si el modelo
       entero lleva brazalete integrado, no hay nada que elegir: no se
       cuentan opciones, se dice que va incluido. */
    if (elRotuloCorrea) {
      var n = cuantas(acabado);
      elRotuloCorrea.textContent = D.correas.length === 1
        ? 'Incluido'
        : (n === 1 ? 'Este acabado se monta solo con esta'
                   : n + ' opciones para este acabado');
    }

    for (var j = 0; j < botonesAcabado.length; j++) {
      var esteA = botonesAcabado[j].dataset.acabado === acabado;
      botonesAcabado[j].setAttribute('aria-pressed', String(esteA));
    }
    for (var k = 0; k < botonesCorrea.length; k++) {
      var idx = Number(botonesCorrea[k].dataset.correa);
      var disponible = precio(acabado, idx) !== null;
      botonesCorrea[k].disabled = !disponible;
      botonesCorrea[k].setAttribute('aria-pressed', String(idx === correa));
      botonesCorrea[k].title = disponible
        ? D.correas[idx].nombre + ' · ' + euros(precio(acabado, idx))
        : D.correas[idx].nombre + ' — no se monta con el acabado ' + a.nombre;
    }

    /* el botón ya no es un enlace: añade la combinación a la cesta y
       lleva a la pantalla del carrito, que es lo único que hay ahí */
    if (elReservar) elReservar.disabled = (p === null);
  }

  /* ---------- la ficha técnica completa ----------
     Pantalla nueva por encima de la página: se monta al pulsar y se
     tira al cerrar. NO cambia la dirección, no navega a ningún sitio y
     no mueve ni un píxel de lo que hay debajo: al cerrar, la pantalla
     está exactamente como estaba.

     Se rellena con la combinación que esté elegida en ese momento, no
     con una ficha escrita: quien configure el Cenit lee la ficha del
     Cenit. */
  (function ficha() {
    var plantilla = document.querySelector('[data-plantilla-ficha]');
    var abridor = document.querySelector('[data-abre-ficha]');
    if (!plantilla || !abridor) return;

    var overlay = null;

    function conEscape(e) { if (e.key === 'Escape') cerrar(); }

    function cerrar() {
      if (!overlay) return;
      overlay.parentNode.removeChild(overlay);
      overlay = null;
      document.removeEventListener('keydown', conEscape);
      abridor.focus();
    }

    function linea(clave, valor) {
      var div = document.createElement('div');
      var dt = document.createElement('dt'); dt.textContent = clave;
      var dd = document.createElement('dd'); dd.textContent = valor;
      div.appendChild(dt); div.appendChild(dd);
      return div;
    }

    function rellenar(caja) {
      var a = D.acabados[acabado];
      var c = D.correas[correa];
      var destino = caja.querySelector('[data-grupos]');
      destino.innerHTML = '';

      (a.grupos || []).forEach(function (g, indice) {
        var sec = document.createElement('section');
        sec.className = 'cfg-overlay-grupo';
        var cab = document.createElement('header');
        var num = document.createElement('span'); num.textContent = g.n;
        var tit = document.createElement('h3'); tit.textContent = g.titulo;
        cab.appendChild(num); cab.appendChild(tit);
        var dl = document.createElement('dl');
        g.filas.forEach(function (par) { dl.appendChild(linea(par[0], par[1])); });

        /* la correa elegida y la referencia cierran el último grupo:
           son lo único que depende de la elección de correa */
        if (indice === (a.grupos.length - 1)) {
          dl.appendChild(linea('BRAZALETE O CORREA', c.nombre + ' · ' + c.detalle));
          dl.appendChild(linea('REFERENCIA', referencia()));
        }
        sec.appendChild(cab); sec.appendChild(dl);
        destino.appendChild(sec);
      });

      var refs = caja.querySelectorAll('[data-ref]');
      for (var i = 0; i < refs.length; i++) refs[i].textContent = referencia();

      var resumen = caja.querySelector('[data-overlay-resumen]');
      if (resumen) resumen.textContent = a.nombre + ' · ' + c.nombre + ' · ' + euros(precio(acabado, correa));
    }

    abridor.addEventListener('click', function () {
      if (overlay) return;
      overlay = plantilla.content.firstElementChild.cloneNode(true);
      rellenar(overlay);
      document.body.appendChild(overlay);

      var cierres = overlay.querySelectorAll('[data-cierra-ficha]');
      for (var i = 0; i < cierres.length; i++) cierres[i].addEventListener('click', cerrar);
      /* clic en el fondo oscurecido, fuera de la caja */
      overlay.addEventListener('click', function (e) { if (e.target === overlay) cerrar(); });
      if (cierres.length) cierres[0].focus();

      document.addEventListener('keydown', conEscape);
    });
  })();


  for (var i = 0; i < botonesAcabado.length; i++) {
    (function (boton) {
      boton.addEventListener('click', function () {
        acabado = boton.dataset.acabado;
        /* Si la correa puesta no se monta con el acabado nuevo, se pasa
           a la primera que sí. Nunca se queda una combinación que no
           existe ni un precio en blanco. */
        if (precio(acabado, correa) === null) {
          var otra = hayAlguna(acabado);
          if (otra >= 0) correa = otra;
        }
        pintar();
      });
    })(botonesAcabado[i]);
  }

  for (var j = 0; j < botonesCorrea.length; j++) {
    (function (boton) {
      boton.addEventListener('click', function () {
        var idx = Number(boton.dataset.correa);
        if (precio(acabado, idx) === null) return;
        correa = idx;
        pintar();
      });
    })(botonesCorrea[j]);
  }

  if (elReservar) {
    elReservar.addEventListener('click', function () {
      var a = D.acabados[acabado], c = D.correas[correa], p = precio(acabado, correa);
      if (p === null) return;
      laoraCarritoAnadir({
        ref: referencia(),
        nombre: D.modelo,
        acabado: a.nombre,
        correa: c.nombre,
        precio: p,
        foto: foto()
      });
      window.location.href = '/carrito.html';
    });
  }

  pintar();
})();
