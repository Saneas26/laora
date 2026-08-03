/* ============================================================
   laOra · HOME
   ------------------------------------------------------------
   Tres piezas independientes: el pase de fotos del héroe, el mapa
   del precio y los cuatro modelos destacados. Cada una comprueba
   que su HTML existe antes de arrancar, así que si un día se quita
   una sección de la home el resto sigue funcionando.
   ============================================================ */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1 · pase de fotos del héroe ---------- */
  (function heroe() {
    var fotos = document.querySelectorAll('.h-hero-foto');
    var mandos = document.querySelectorAll('.h-hero-mandos [data-foto]');
    var pausa = document.querySelector('.h-hero-pausa');
    if (fotos.length < 2 || !mandos.length) return;

    var actual = 0, reloj = null, parado = reduce;

    function mostrar(i) {
      actual = (i + fotos.length) % fotos.length;
      for (var f = 0; f < fotos.length; f++) fotos[f].classList.toggle('activa', f === actual);
      for (var m = 0; m < mandos.length; m++) mandos[m].classList.toggle('activa', m === actual);
    }
    function arrancar() {
      if (parado) return;
      detener();
      reloj = window.setInterval(function () { mostrar(actual + 1); }, 6200);
    }
    function detener() { if (reloj) { window.clearInterval(reloj); reloj = null; } }

    for (var i = 0; i < mandos.length; i++) {
      (function (boton, indice) {
        boton.addEventListener('click', function () { mostrar(indice); arrancar(); });
      })(mandos[i], i);
    }

    if (pausa) {
      pausa.addEventListener('click', function () {
        parado = !parado;
        if (parado) { detener(); pausa.textContent = '▶'; pausa.setAttribute('aria-label', 'Reanudar el pase de imágenes'); }
        else { arrancar(); pausa.textContent = 'II'; pausa.setAttribute('aria-label', 'Pausar el pase de imágenes'); }
      });
      if (reduce) { pausa.textContent = '▶'; pausa.setAttribute('aria-label', 'Reanudar el pase de imágenes'); }
    }

    /* Con la pestaña de fondo no tiene sentido seguir cambiando fotos. */
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) detener(); else arrancar();
    });

    arrancar();
  })();


  /* ---------- 2 · el mapa del precio ----------
     Las cifras de mercado son ORIENTATIVAS y están fechadas en la
     nota legal de la sección. Si se actualizan, hay que actualizar
     también la fecha de esa nota en index.html. */
  (function mapa() {
    var contenedor = document.querySelector('[data-mapa-tarjetas]');
    var pestanas = document.querySelectorAll('[data-mapa]');
    if (!contenedor || !pestanas.length) return;

    var mapas = {
      lunar: {
        titulo: 'El cronógrafo lunar',
        intro: 'Del canal oficial al mercado irregular: cinco rutas que pueden parecer similares en una foto, pero no ofrecen lo mismo.',
        tarjetas: [
          { canal: '01 · Boutique oficial', nombre: 'Omega Speedmaster Moonwatch', precio: '7.700 €', nota: 'Nuevo, documentado y con garantía oficial.', irregular: false },
          { canal: '02 · Subasta', nombre: 'Catawiki y similares', precio: '≈ 5.800 € + gastos', nota: 'Ejemplo orientativo: usado; caja, papeles y estado dependen del lote.', irregular: false },
          { canal: '03 · Gris / usado', nombre: 'Chrono24', precio: '4.400–6.300 €', nota: 'Rango observado en referencias habituales. Autenticidad y set cambian el valor.', irregular: false },
          { canal: '04 · Piezas no originales', nombre: 'Marketplaces generalistas', precio: '650–1.250 €', nota: 'Relojes rehechos o con componentes de procedencia no acreditada.', irregular: true },
          { canal: '05 · Falsificación', nombre: '«Superclones»', precio: '600–1.650 €', nota: 'Marca suplantada, origen incierto y sin garantía legítima.', irregular: true }
        ],
        otras: [['Bulova Lunar Pilot', '549–659 €'],
                ['Seiko Prospex Speedtimer', '646–680 €'],
                ['Tissot PR516 Chronograph', '545–625 €']],
        modelo: 'Lunar',
        enlace: '/lunar.html',
        foto: '/assets/img/relojes-2026/lunar-front.webp',
        valor: 'Acero y cristal según configuración, movimiento identificado antes de la venta y control individual en Madrid. Sin licencias de marca ajena ni capas comerciales innecesarias.'
      },
      bitacora: {
        titulo: 'El deportivo integrado',
        intro: 'El precio de acceso cambia radicalmente entre boutique, reventa y falsificación. La silueta puede recordar a un icono; la identidad debe ser propia.',
        tarjetas: [
          { canal: '01 · Boutique oficial', nombre: 'Patek Philippe Nautilus', precio: '≈ 70.000 €', nota: 'Tarifa de referencia; disponibilidad extremadamente limitada.', irregular: false },
          { canal: '02 · Subasta', nombre: 'Casas especializadas', precio: 'Muy variable', nota: 'Referencia, material y documentación mandan.', irregular: false },
          { canal: '03 · Gris / usado', nombre: 'Chrono24', precio: '110.000–180.000 €', nota: 'Rango habitual para las referencias más demandadas, según estado y set.', irregular: false },
          { canal: '04 · Piezas no originales', nombre: 'Marketplaces generalistas', precio: '650–1.500 €', nota: 'Montajes con componentes no originales o procedencia no acreditada.', irregular: true },
          { canal: '05 · Falsificación', nombre: '«Superclones»', precio: '600–1.650 €', nota: 'Marca suplantada, origen incierto y sin garantía legítima.', irregular: true }
        ],
        otras: [['Tissot PRX Powermatic 80', '775–895 €'],
                ['Citizen Tsuyosa', '299–429 €']],
        modelo: 'Bitácora',
        enlace: '/bitacora.html',
        foto: '/assets/img/relojes-2026/bitacora-hero-full.webp',
        valor: 'Acero 316L, cristal y movimiento identificados según configuración, con control individual en Madrid. El precio se concentra en el reloj y en el servicio.'
      }
    };

    var elTitulo = document.querySelector('[data-mapa-titulo]');
    var elIntro = document.querySelector('[data-mapa-intro]');
    var elOtras = document.querySelector('[data-mapa-otras]');
    var elFoto = document.querySelector('[data-mapa-foto]');
    var elValor = document.querySelector('[data-mapa-valor]');
    var elEnlace = document.querySelector('[data-mapa-enlace]');

    function pintar(clave) {
      var d = mapas[clave];
      if (!d) return;

      elTitulo.textContent = d.titulo;
      elIntro.textContent = d.intro;

      contenedor.innerHTML = '';
      d.tarjetas.forEach(function (t) {
        var art = document.createElement('article');
        art.className = 'h-mapa-tarjeta' + (t.irregular ? ' irregular' : '');
        var p = document.createElement('p'); p.textContent = t.canal;
        var h = document.createElement('h3'); h.textContent = t.nombre;
        var s = document.createElement('strong'); s.textContent = t.precio;
        var n = document.createElement('small'); n.textContent = t.nota;
        art.append(p, h, s, n);
        contenedor.appendChild(art);
      });

      elOtras.innerHTML = '';
      d.otras.forEach(function (par) {
        var span = document.createElement('span');
        var b = document.createElement('b'); b.textContent = par[0];
        var small = document.createElement('small'); small.textContent = par[1];
        span.append(b, small);
        elOtras.appendChild(span);
      });

      elFoto.src = d.foto;
      elValor.textContent = d.valor;
      elEnlace.setAttribute('href', d.enlace);
      var nombres = document.querySelectorAll('[data-mapa-modelo]');
      for (var i = 0; i < nombres.length; i++) nombres[i].textContent = d.modelo;

      for (var p2 = 0; p2 < pestanas.length; p2++) {
        pestanas[p2].setAttribute('aria-pressed', String(pestanas[p2].dataset.mapa === clave));
      }
    }

    for (var i = 0; i < pestanas.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () { pintar(boton.dataset.mapa); });
      })(pestanas[i]);
    }

    pintar('lunar');
  })();


  /* ---------- 3 · los cuatro destacados ---------- */
  (function destacados() {
    var caja = document.querySelector('[data-destacados]');
    if (!caja || !window.LAORA_CATALOGO) return;
    var cuatro = window.LAORA_CATALOGO.slice(0, 4);
    caja.innerHTML = '';
    cuatro.forEach(function (r) {
      caja.appendChild(window.LAORA_TARJETA(r));
    });
  })();
})();
