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
     TRES EXPOSICIONES, una por reloj. Antes eran dos encuadres de la
     misma foto del Lunar; desde el 05/08/2026 son el Lunar —con el
     acercamiento, que es el encuadre que eligió Óscar—, el Bitácora y
     el Trinchera.

     Al pasar de una a otra cambian la foto, el nombre, la línea de
     características, el precio y adónde lleva el botón. Todo sale del
     <script data-exposiciones> que escribe el generador: aquí no hay ni
     un precio ni un nombre escritos. */
  (function portada() {
    var media = document.querySelector('[data-hero]');
    var caja = document.querySelector('[data-exposiciones]');
    if (!media || !caja) return;

    var lista;
    try { lista = JSON.parse(caja.textContent); } catch (e) { return; }
    if (!lista || !lista.length) return;

    var puntos = media.querySelectorAll('[data-hero-vista]');
    var flechas = media.querySelectorAll('[data-hero-paso]');
    var foto = media.querySelector('.lunar-hero-image');
    var elNombre = document.querySelector('[data-hero-nombre]');
    var elSpecs = document.querySelector('[data-hero-specs]');
    var elPrecio = document.querySelector('[data-hero-precio]');
    var elReservar = document.querySelector('[data-hero-reservar]');
    var vista = 0;

    function pintar() {
      var e = lista[vista];

      /* La foto se precarga antes de ponerla, para que el cambio no
         enseñe el hueco vacío a medio cargar. Y se apunta CUÁL se pidió:
         pasando rápido de una a otra, la que tardaba menos en cargar
         llegaba la última y se quedaba puesta la foto de un reloj con el
         nombre y el precio de otro. Si al cargar ya no es la que toca,
         se descarta. */
      if (foto && foto.getAttribute('src') !== e.foto) {
        var pedida = vista;
        var siguiente = new Image();
        siguiente.onload = function () {
          if (pedida === vista) foto.src = e.foto;
        };
        siguiente.src = e.foto;
      }
      media.classList.toggle('is-close', e.encuadre === 'cerca');
      media.setAttribute('aria-label', e.alt);

      if (elNombre) elNombre.textContent = e.nombre;
      if (elPrecio) elPrecio.textContent = 'desde ' + e.precio;
      if (elReservar) elReservar.setAttribute('href', e.enlace);
      if (elSpecs) {
        elSpecs.innerHTML = '';
        e.specs.forEach(function (dato, n) {
          if (n) { var sep = document.createElement('i'); sep.textContent = '|'; elSpecs.appendChild(sep); }
          elSpecs.appendChild(document.createTextNode(dato));
        });
      }

      for (var i = 0; i < puntos.length; i++) {
        var esta = Number(puntos[i].dataset.heroVista) === vista;
        puntos[i].classList.toggle('active', esta);
        puntos[i].setAttribute('aria-pressed', String(esta));
      }
    }

    for (var i = 0; i < flechas.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () {
          /* con el número de exposiciones, no con un 2 fijo: antes eran
             dos encuadres y ahora son tres relojes */
          var n = lista.length;
          vista = (vista + Number(boton.dataset.heroPaso) + n) % n;
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
