/* ============================================================
   laOra · FICHA DE RELOJ
   ------------------------------------------------------------
   Dos cosas: la galería y el configurador.

   Todo lo que pinta el configurador viene del <script
   type="application/json" data-configurador> que escribe el
   generador desde assets/datos/catalogo.json. Ahí NO hay nada
   interno: ni proveedores, ni enlaces de compra, ni coste, ni
   margen. Solo lo que ve el cliente.

   Si este fichero no llega a cargarse, la ficha se sigue leyendo
   entera: sale la primera foto, el precio de entrada y las
   especificaciones del primer acabado, que van escritas en el
   HTML. Lo único que se pierde es poder cambiar de opción.
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 1 · la galería ---------- */
  (function galeria() {
    var grande = document.querySelector('[data-foto-grande]');
    var minis = document.querySelectorAll('[data-mini]');
    if (!grande || minis.length < 2) return;

    function elegir(boton) {
      grande.src = boton.dataset.mini;
      for (var i = 0; i < minis.length; i++) {
        minis[i].classList.toggle('active', minis[i] === boton);
      }
    }
    for (var i = 0; i < minis.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () { elegir(boton); });
      })(minis[i]);
    }
  })();


  /* ---------- 2 · el configurador ---------- */
  (function configurador() {
    var caja = document.querySelector('[data-configurador]');
    if (!caja) return;

    var d;
    try { d = JSON.parse(caja.textContent); } catch (e) { return; }
    if (!d || !d.acabados || !d.correas) return;

    var elPrecio = document.querySelector('[data-precio]');
    var elResumen = document.querySelector('[data-resumen-acabado]');
    var elRef = document.querySelector('[data-ref]');
    var elReservar = document.querySelector('[data-reservar]');

    var acabado = d.acabados[0];
    var correa = d.correas[0];

    /* La referencia se compone igual que en la hoja de materiales:
       LO-01_Lunar_A01 → modelo + inicial del acabado + número de correa.
       Así lo que el cliente ve en la web y lo que Óscar busca en la hoja
       es la misma cadena. */
    function referencia() {
      var i = d.acabados.indexOf(acabado);
      var j = d.correas.indexOf(correa);
      var letra = acabado.nombre.charAt(0).toUpperCase();
      var codigo = d.codigo.replace(/[—–-]/g, '-').replace(/\s/g, '');
      return codigo + '_' + d.modelo.replace(/\s/g, '') + '_' + letra + ('0' + (j + 1)).slice(-2);
    }

    function euros(v) {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency', currency: 'EUR',
        minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2
      }).format(v);
    }

    function pintar() {
      var j = d.correas.indexOf(correa);
      var lista = d.precios[acabado.id] || [];
      var precio = lista[j];

      if (elPrecio) elPrecio.textContent = precio === undefined ? '' : euros(precio);
      if (elResumen) elResumen.textContent = acabado.resumen || '';
      if (elRef) elRef.textContent = referencia();

      /* la ficha técnica que depende del acabado */
      var campos = document.querySelectorAll('[data-spec]');
      for (var i = 0; i < campos.length; i++) {
        var clave = campos[i].dataset.spec;
        if (acabado[clave]) campos[i].textContent = acabado[clave];
      }

      /* el botón se lleva la combinación elegida a la reserva */
      if (elReservar) {
        elReservar.setAttribute('href',
          '/reservar.html?ref=' + encodeURIComponent(referencia()) +
          '&acabado=' + encodeURIComponent(acabado.nombre) +
          '&correa=' + encodeURIComponent(correa.nombre));
      }
    }

    function grupo(nombre, lista, alElegir) {
      var cont = document.querySelector('[data-grupo="' + nombre + '"]');
      if (!cont) return;
      var botones = cont.querySelectorAll('[data-' + nombre + ']');
      for (var i = 0; i < botones.length; i++) {
        (function (boton, indice) {
          boton.addEventListener('click', function () {
            for (var k = 0; k < botones.length; k++) {
              var esta = botones[k] === boton;
              botones[k].setAttribute('aria-selected', String(esta));
              if (esta) botones[k].removeAttribute('tabindex');
              else botones[k].setAttribute('tabindex', '-1');
            }
            alElegir(lista[indice]);
            pintar();
          });
        })(botones[i], i);
      }
    }

    grupo('acabado', d.acabados, function (v) { acabado = v; });
    grupo('correa', d.correas, function (v) { correa = v; });

    pintar();
  })();
})();
