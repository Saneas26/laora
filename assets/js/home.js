/* ============================================================
   laOra · HOME
   ------------------------------------------------------------
   Reproduce los dos componentes con estado del material original
   (BitacoraHero y MarketMap), que allí eran React. Mismas clases y
   mismo comportamiento: 6.200 ms entre imágenes, `is-active` en la
   diapositiva y en su mando, `active` en la pestaña del mapa.

   Los cuatro modelos destacados NO se pintan aquí: van escritos en
   el HTML por el generador, para que Google los lea y la página
   funcione aunque este fichero no llegue a cargar.
   ============================================================ */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1 · el pase de fotos del héroe ---------- */
  (function heroe() {
    var slides = document.querySelectorAll('.hero-slide');
    var mandos = document.querySelectorAll('.hero-controls [data-slide]');
    var pausa = document.querySelector('.hero-pause');
    if (slides.length < 2 || !mandos.length) return;

    var actual = 0, reloj = null, parado = reduce;

    function mostrar(i) {
      actual = (i + slides.length) % slides.length;
      for (var s = 0; s < slides.length; s++) slides[s].classList.toggle('is-active', s === actual);
      for (var m = 0; m < mandos.length; m++) {
        mandos[m].classList.toggle('is-active', m === actual);
        mandos[m].setAttribute('aria-pressed', String(m === actual));
      }
    }
    function arrancar() {
      detener();
      if (parado) return;
      reloj = window.setInterval(function () { mostrar(actual + 1); }, 6200);
    }
    function detener() { if (reloj) { window.clearInterval(reloj); reloj = null; } }

    for (var i = 0; i < mandos.length; i++) {
      (function (boton, indice) {
        boton.addEventListener('click', function () { mostrar(indice); arrancar(); });
      })(mandos[i], i);
    }

    if (pausa) {
      /* con movimiento reducido el original ni siquiera pintaba el botón */
      if (reduce) { pausa.remove(); pausa = null; }
      else pausa.addEventListener('click', function () {
        parado = !parado;
        pausa.textContent = parado ? '▶' : 'Ⅱ';
        pausa.setAttribute('aria-pressed', String(parado));
        pausa.setAttribute('aria-label', parado ? 'Reanudar movimiento' : 'Pausar movimiento');
        arrancar();
      });
    }

    /* con la pestaña de fondo no tiene sentido seguir cambiando fotos */
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) detener(); else arrancar();
    });

    arrancar();
  })();


  /* ---------- 2 · el mapa del precio ----------
     Las cifras son ORIENTATIVAS y están fechadas en la nota legal de la
     sección (`.market-footnote`, en el HTML). Si se actualizan aquí, hay
     que actualizar también esa fecha. */
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
          { canal: '02 · Subasta', nombre: 'Catawiki / similares', precio: '≈ 5.800 € + gastos', nota: 'Ejemplo orientativo: usado; caja, papeles y estado dependen del lote.', irregular: false },
          { canal: '03 · Gris / usado', nombre: 'Chrono24', precio: '4.400–6.300 €', nota: 'Rango observado en referencias habituales. Autenticidad y set cambian el valor.', irregular: false },
          { canal: '04 · Piezas no originales', nombre: 'Marketplaces generalistas', precio: '650–1.250 €', nota: 'Relojes rehechos o con componentes de procedencia no acreditada.', irregular: true },
          { canal: '05 · Falsificación', nombre: '«Superclones»', precio: '600–1.650 €', nota: 'Marca suplantada, origen incierto y sin garantía legítima.', irregular: true }
        ],
        otras: [['Bulova Lunar Pilot', '549–659 €'],
                ['Seiko Prospex Speedtimer', '646–680 €'],
                ['Tissot PR516 Chronograph', '545–625 €']],
        modelo: 'Lunar',
        enlace: '/lunar.html',
        foto: '/assets/img/relojes-2026/lunar-front.webp'
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
        foto: '/assets/img/relojes-2026/bitacora-hero-full.webp'
      }
    };

    var elTitulo = document.querySelector('[data-mapa-titulo]');
    var elIntro = document.querySelector('[data-mapa-intro]');
    var elOtras = document.querySelector('[data-mapa-otras]');
    var elFoto = document.querySelector('[data-mapa-foto]');
    var elEnlace = document.querySelector('[data-mapa-enlace]');

    function pintar(clave) {
      var d = mapas[clave];
      if (!d) return;

      elTitulo.textContent = d.titulo;
      elIntro.textContent = d.intro;

      contenedor.innerHTML = '';
      d.tarjetas.forEach(function (t) {
        var art = document.createElement('article');
        art.className = 'market-card' + (t.irregular ? ' irregular' : '');
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
      /* El texto del cuadro ya NO cambia con la pestaña: desde el 03/08/2026
         es la misma frase para los dos modelos, escrita en el HTML. Es una
         afirmación de colección («desde…»), no del modelo de la pestaña. */

      elEnlace.setAttribute('href', d.enlace);
      /* El rótulo del enlace se escribe de una pieza: el enlace es un
         inline-flex y con el nombre en su propio <b> se perdían los
         espacios de alrededor («VERLUNAR→»). */
      elEnlace.textContent = 'Ver ' + d.modelo + ' →';
      var nombres = document.querySelectorAll('.laora-value-price [data-mapa-modelo]');
      for (var i = 0; i < nombres.length; i++) nombres[i].textContent = d.modelo;

      for (var p2 = 0; p2 < pestanas.length; p2++) {
        var esta = pestanas[p2].dataset.mapa === clave;
        pestanas[p2].classList.toggle('active', esta);
        pestanas[p2].setAttribute('aria-pressed', String(esta));
      }
    }

    for (var i = 0; i < pestanas.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () { pintar(boton.dataset.mapa); });
      })(pestanas[i]);
    }

    pintar('lunar');
  })();
})();
