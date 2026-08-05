/* ============================================================
   laOra · LANDING V2 DEL LUNAR
   ------------------------------------------------------------
   Esto es lo que en el material aprobado del 05/08/2026 era estado de
   React. Nada de aquí cambia una medida, un color ni un texto: solo
   pone y quita las mismas clases que ponía y quitaba el componente.

     LunarHero.tsx            → la portada y sus dos vistas
     TrustCarousel.tsx        → el carrusel de confianza
     MarketMap.tsx            → las pestañas y el conmutador del móvil
     LunarSpecifications.tsx  → la ficha técnica
     Shell.tsx                → el menú del móvil

   Si este fichero no llega a cargarse, la página se lee entera: salen
   la portada, los seis actos y todos los textos. Lo único que se pierde
   es poder cambiar de vista, de pestaña y abrir la ficha técnica.
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 1 · el menú del móvil ---------- */
  (function menu() {
    var boton = document.querySelector('[data-menu]');
    var nav = document.querySelector('[data-nav]');
    if (!boton || !nav) return;

    boton.addEventListener('click', function () {
      var abierto = nav.classList.toggle('open');
      boton.setAttribute('aria-expanded', String(abierto));
      boton.setAttribute('aria-label', abierto ? 'Cerrar menú' : 'Abrir menú');
    });
  })();


  /* ---------- 2 · la portada ----------
     Dos vistas sobre la misma foto: la segunda es el acercamiento, y en
     la hoja se llama `.is-close`. Igual que en el componente, el índice
     da la vuelta con el resto de 2. */
  (function portada() {
    var media = document.querySelector('[data-hero]');
    if (!media) return;

    var puntos = media.querySelectorAll('[data-hero-vista]');
    var flechas = media.querySelectorAll('[data-hero-paso]');
    var vista = 0;

    function pintar() {
      media.classList.toggle('is-close', vista === 1);
      for (var i = 0; i < puntos.length; i++) {
        var esta = Number(puntos[i].dataset.heroVista) === vista;
        puntos[i].classList.toggle('active', esta);
        puntos[i].setAttribute('aria-pressed', String(esta));
      }
    }

    for (var i = 0; i < flechas.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () {
          vista = (vista + Number(boton.dataset.heroPaso) + 2) % 2;
          pintar();
        });
      })(flechas[i]);
    }
    for (var j = 0; j < puntos.length; j++) {
      (function (boton) {
        boton.addEventListener('click', function () {
          vista = Number(boton.dataset.heroVista);
          pintar();
        });
      })(puntos[j]);
    }
  })();


  /* ---------- 3 · el carrusel de confianza ----------
     El mismo salto del componente: el ancho de una tarjeta más los 18 px
     de separación. */
  (function carrusel() {
    var pista = document.querySelector('[data-carrusel]');
    if (!pista) return;

    var botones = document.querySelectorAll('[data-carrusel-paso]');
    for (var i = 0; i < botones.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () {
          var tarjeta = pista.querySelector('.trust-card');
          var ancho = (tarjeta ? tarjeta.offsetWidth : pista.clientWidth) + 18;
          pista.scrollBy({ left: Number(boton.dataset.carruselPaso) * ancho, behavior: 'smooth' });
        });
      })(botones[i]);
    }
  })();


  /* ---------- 4 · el mapa del precio ---------- */
  (function decision() {
    var caja = document.querySelector('[data-comparaciones]');
    var rutas = document.querySelector('[data-rutas]');
    if (!caja || !rutas) return;

    var datos;
    try { datos = JSON.parse(caja.textContent); } catch (e) { return; }

    var intro = document.querySelector('[data-intro]');
    var alternativas = document.querySelector('[data-alternativas]');
    var pestanas = document.querySelectorAll('[data-comparacion]');

    function texto(etiqueta, contenido) {
      var el = document.createElement(etiqueta);
      el.textContent = contenido;
      return el;
    }

    function pintar(clave) {
      var d = datos[clave];
      if (!d) return;

      intro.innerHTML = '';
      intro.appendChild(texto('strong', d.titulo));
      intro.appendChild(texto('span', d.intro));

      rutas.innerHTML = '';
      d.filas.forEach(function (fila) {
        var art = document.createElement('article');
        art.className = fila[4];
        art.appendChild(texto('span', fila[0]));
        art.appendChild(texto('b', fila[1]));
        art.appendChild(texto('strong', fila[2]));
        art.appendChild(texto('small', fila[3]));
        rutas.appendChild(art);
      });

      alternativas.innerHTML = '';
      alternativas.appendChild(texto('span', 'ALTERNATIVAS DE OTRAS MARCAS'));
      d.alternativas.forEach(function (par) {
        var div = document.createElement('div');
        div.appendChild(texto('b', par[0]));
        div.appendChild(texto('small', par[1]));
        alternativas.appendChild(div);
      });

      for (var i = 0; i < pestanas.length; i++) {
        var esta = pestanas[i].dataset.comparacion === clave;
        pestanas[i].classList.toggle('active', esta);
        pestanas[i].setAttribute('aria-pressed', String(esta));
      }
    }

    for (var i = 0; i < pestanas.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () { pintar(boton.dataset.comparacion); });
      })(pestanas[i]);
    }

    /* el conmutador que solo se ve en el móvil */
    var conmutador = document.querySelectorAll('[data-panel]');
    var paneles = {
      price: document.querySelector('[data-panel-price]'),
      movement: document.querySelector('[data-panel-movement]')
    };
    for (var k = 0; k < conmutador.length; k++) {
      (function (boton) {
        boton.addEventListener('click', function () {
          var elegido = boton.dataset.panel;
          for (var m = 0; m < conmutador.length; m++) {
            var esta = conmutador[m] === boton;
            conmutador[m].classList.toggle('active', esta);
            conmutador[m].setAttribute('aria-pressed', String(esta));
          }
          Object.keys(paneles).forEach(function (nombre) {
            if (paneles[nombre]) paneles[nombre].classList.toggle('mobile-active', nombre === elegido);
          });
        });
      })(conmutador[k]);
    }
  })();


  /* ---------- 5 · la ficha técnica ----------
     En React el overlay solo existe mientras está abierto, así que aquí
     se clona del <template> al abrir y se tira al cerrar. Se bloquea el
     scroll del fondo, el foco va al aspa y Escape cierra, como allí. */
  (function ficha() {
    var plantilla = document.querySelector('[data-ficha]');
    var abridor = document.querySelector('[data-abre-ficha]');
    if (!plantilla || !abridor) return;

    var overlay = null;
    var scrollPrevio = '';

    function conEscape(e) {
      if (e.key === 'Escape') cerrar();
    }

    function cerrar() {
      if (!overlay) return;
      overlay.parentNode.removeChild(overlay);
      overlay = null;
      document.body.style.overflow = scrollPrevio;
      document.removeEventListener('keydown', conEscape);
      abridor.focus();
    }

    abridor.addEventListener('click', function () {
      if (overlay) return;
      overlay = plantilla.content.firstElementChild.cloneNode(true);
      document.body.appendChild(overlay);

      scrollPrevio = document.body.style.overflow;
      document.body.style.overflow = 'hidden';

      var cierres = overlay.querySelectorAll('[data-cierra-ficha]');
      for (var i = 0; i < cierres.length; i++) {
        cierres[i].addEventListener('click', cerrar);
      }
      if (cierres.length) cierres[0].focus();

      document.addEventListener('keydown', conEscape);
    });
  })();

})();
