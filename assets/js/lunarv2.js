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
    var elFrase = document.querySelector('[data-hero-frase]');
    var elSpecs = document.querySelector('[data-hero-specs]');
    var elSpecs2 = document.querySelector('[data-hero-specs2]');
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
      if (elFrase) elFrase.textContent = e.frase || 'Llego el momento de';
      if (elReservar) elReservar.setAttribute('href', e.enlace);

      /* Los renglones de datos: uno o dos según el reloj. Los separa la
         barra fina de la hoja, no el punto con el que se escriben. */
      function renglon(caja, datos) {
        if (!caja) return;
        caja.innerHTML = '';
        (datos || []).forEach(function (dato, n) {
          if (n) { var sep = document.createElement('i'); sep.textContent = '|'; caja.appendChild(sep); }
          caja.appendChild(document.createTextNode(dato));
        });
        caja.hidden = !(datos && datos.length);
      }
      renglon(elSpecs, e.specs);
      renglon(elSpecs2, e.linea2);

      /* El precio suelto solo cuando NO va dentro del segundo renglón:
         si no, saldría dos veces. */
      if (elPrecio) {
        /* `precioTexto` lo trae el reloj que quiere el precio en su
           propia línea y sin «desde». Si no lo trae, el de siempre; y si
           el precio ya va dentro del segundo renglón, este se esconde
           para que no salga dos veces. */
        elPrecio.textContent = e.precioTexto || ('desde ' + e.precio);
        elPrecio.hidden = !!e.sinPrecio ||
                          (!e.precioTexto && !!(e.linea2 && e.linea2.length));
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

  /* ---------- 3b · el empujoncito del carrusel ----------
     Óscar, 17/08/2026: en el teléfono la tarjeta ocupa casi toda la
     pantalla y no hay flechas, así que nadie adivina que eso se mueve de
     lado. Cuando el carrusel entra en pantalla se le da un empujón corto
     y vuelve solo: la tarjeta de al lado asoma y se entiende el gesto.

     Reglas de la casa:
     · solo en el teléfono —de 721 px para arriba están las flechas—,
     · una sola vez y solo si el cliente no lo ha tocado ya,
     · nunca con «reducir movimiento» activado en el sistema,
     · el `scroll-snap` se apaga durante el empujón: con `mandatory` el
       navegador pelea contra la animación y sale a tirones.

     El recorrido es un seno: sale y vuelve al mismo sitio sin que haya
     que encadenar dos animaciones ni dejar el carrusel a medias. */
  (function empujoncito() {
    var pista = document.querySelector('[data-carrusel]');
    if (!pista || !window.IntersectionObserver || !window.requestAnimationFrame) return;
    if (!window.matchMedia) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!window.matchMedia('(max-width: 720px)').matches) return;

    var animando = false, hecho = false;

    pista.addEventListener('scroll', function () {
      if (!animando) hecho = true;          // lo ha movido el cliente: sobra el aviso
    }, { passive: true });

    function empuja() {
      var tarjeta = pista.querySelector('.trust-card');
      var ancho = tarjeta ? tarjeta.offsetWidth : pista.clientWidth;
      var distancia = Math.max(38, Math.min(64, ancho * 0.18));
      var duracion = 900, inicio = null;
      var snapPrevio = pista.style.scrollSnapType;

      animando = true;
      pista.style.scrollSnapType = 'none';

      function paso(ahora) {
        if (inicio === null) inicio = ahora;
        var p = (ahora - inicio) / duracion;
        if (p >= 1) {
          pista.scrollLeft = 0;
          pista.style.scrollSnapType = snapPrevio;
          animando = false;
          return;
        }
        pista.scrollLeft = distancia * Math.sin(Math.PI * p);
        window.requestAnimationFrame(paso);
      }
      window.requestAnimationFrame(paso);
    }

    var vigia = new IntersectionObserver(function (entradas) {
      for (var i = 0; i < entradas.length; i++) {
        if (!entradas[i].isIntersecting) continue;
        vigia.disconnect();
        if (hecho) return;
        if (pista.scrollLeft > 4) return;
        if (pista.scrollWidth <= pista.clientWidth + 8) return;
        window.setTimeout(function () { if (!hecho) empuja(); }, 420);
      }
    }, { threshold: 0.45 });

    vigia.observe(pista);
  })();

  /* ---------- 4 · lo que no mejora el reloj ----------
     RETIRADO el 11/08/2026. Era un tramo de cinco pantallas que se
     quedaba pegado y sacaba los cuatro costes de uno en uno según
     bajabas. Óscar lo quitó: «quitar esa animación… que sea una página
     normal». Los costes están ahora dentro de la propia imagen, así que
     no hay nada que animar ni nada que escuchar en el scroll. */

  /* ---------- 5 · el mapa del precio ----------
     Rehecho el 05/08/2026: una barra por canal contra la misma escala,
     en vez de cinco tarjetas de media pantalla. Al cambiar de pestaña se
     vuelve a dibujar el mapa entero con los datos del otro icono.

     La geometría es la misma que calcula el generador para la primera
     pestaña: barra desde cero hasta el precio más bajo del canal y una
     prolongación con trama hasta el más alto. El múltiplo se saca del
     precio más bajo, para no exagerar nunca. */
  (function decision() {
    var caja = document.querySelector('[data-comparaciones]');
    var regular = document.querySelector('[data-mp-regular]');
    if (!caja || !regular) return;

    var datos;
    try { datos = JSON.parse(caja.textContent); } catch (e) { return; }

    var irregular = document.querySelector('[data-mp-irregular]');
    var nuestro = document.querySelector('[data-mp-nuestro]');
    var intro = document.querySelector('[data-mp-intro]');
    var alternativas = document.querySelector('[data-alternativas]');
    var pestanas = document.querySelectorAll('[data-comparacion]');
    var logo = (document.querySelector('.mp-logo img') || {}).src || '';

    function el(etiqueta, clase, texto) {
      var e = document.createElement(etiqueta);
      if (clase) e.className = clase;
      if (texto !== undefined) e.textContent = texto;
      return e;
    }

    function euros(v) {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency', currency: 'EUR',
        minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2
      }).format(v);
    }

    function fila(f, tope, desde, nombreNuestro) {
      var canal = f[0], nombre = f[1], precio = f[2], minimo = f[3], maximo = f[4], nota = f[5], tono = f[6];
      var li = el('li', 'mp-fila ' + tono);

      var quien = el('div', 'mp-quien');
      quien.appendChild(el('p', 'mp-canal', canal));
      quien.appendChild(el('h3', '', nombre));
      quien.appendChild(el('p', 'mp-nota', nota));

      var pista = el('div', 'mp-pista');
      var cifras = el('div', 'mp-cifras');
      cifras.appendChild(el('p', 'mp-precio', precio));

      if (minimo) {
        var solido = Math.max(minimo / tope * 100, 0.5);
        var s = el('span', 'mp-solido');
        s.style.width = solido.toFixed(2) + '%';
        pista.appendChild(s);
        var extra = maximo ? (maximo - minimo) / tope * 100 : 0;
        if (extra > 0.2) {
          var r = el('span', 'mp-rango');
          r.style.left = solido.toFixed(2) + '%';
          r.style.width = extra.toFixed(2) + '%';
          pista.appendChild(r);
        }
        var m = el('p', 'mp-multiplo', '×' + Math.round(minimo / desde));
        m.appendChild(el('span', '', 'el ' + nombreNuestro));
        cifras.appendChild(m);
      } else {
        var i = el('span', 'mp-solido mp-indefinido');
        i.style.width = '100%';
        pista.appendChild(i);
        var sc = el('p', 'mp-multiplo mp-sincifra', 'sin cifra');
        sc.appendChild(el('span', '', 'de referencia'));
        cifras.appendChild(sc);
      }

      li.appendChild(quien); li.appendChild(pista); li.appendChild(cifras);
      return li;
    }

    function pintar(clave) {
      var d = datos[clave];
      if (!d) return;

      var topes = d.filas.map(function (f) { return f[4]; }).filter(Boolean);
      var tope = topes.length ? Math.max.apply(null, topes) : 1;

      if (intro) intro.textContent = d.intro;

      regular.innerHTML = '';
      irregular.innerHTML = '';
      d.filas.forEach(function (f) {
        (f[6] === 'irregular' ? irregular : regular).appendChild(fila(f, tope, d.desde, d.nuestro));
      });

      /* la nuestra, que es la única fila con color */
      nuestro.innerHTML = '';
      var li = el('li', 'mp-fila nuestro');
      var quien = el('div', 'mp-quien');
      quien.appendChild(el('p', 'mp-canal', 'Aquí estamos'));
      var h3 = el('h3');
      if (logo) {
        var marca = el('span', 'mp-logo');
        var img = document.createElement('img');
        img.src = logo; img.alt = 'laOra';
        marca.appendChild(img);
        h3.appendChild(marca);
      }
      h3.appendChild(document.createTextNode(' ' + d.nuestro));
      quien.appendChild(h3);
      quien.appendChild(el('p', 'mp-nota', 'Marca propia, componentes identificados y montaje en Madrid.'));
      var pista = el('div', 'mp-pista');
      var s = el('span', 'mp-solido');
      s.style.width = Math.max(d.desde / tope * 100, 0.8).toFixed(2) + '%';
      pista.appendChild(s);
      var cifras = el('div', 'mp-cifras');
      cifras.appendChild(el('p', 'mp-precio', 'desde ' + euros(d.desde)));
      var uno = el('p', 'mp-multiplo mp-base', '×1');
      uno.appendChild(el('span', '', 'el punto de partida'));
      cifras.appendChild(uno);
      li.appendChild(quien); li.appendChild(pista); li.appendChild(cifras);
      nuestro.appendChild(li);

      alternativas.innerHTML = '';
      alternativas.appendChild(el('span', '', 'Alternativas de otras marcas'));
      d.alternativas.forEach(function (par) {
        var div = document.createElement('div');
        div.appendChild(el('b', '', par[0]));
        div.appendChild(el('small', '', par[1]));
        alternativas.appendChild(div);
      });

      for (var i = 0; i < pestanas.length; i++) {
        var esta = pestanas[i].dataset.comparacion === clave;
        pestanas[i].classList.toggle('active', esta);
        pestanas[i].setAttribute('aria-pressed', String(esta));
      }
    }

    for (var k = 0; k < pestanas.length; k++) {
      (function (boton) {
        boton.addEventListener('click', function () { pintar(boton.dataset.comparacion); });
      })(pestanas[k]);
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
