/* ============================================================
   laOra · EL EMPUJONCITO DE LAS TIRAS QUE SE DESLIZAN
   ------------------------------------------------------------
   Óscar, 17/08/2026: «en el móvil ocupa prácticamente toda la pantalla
   y puede pasar desapercibido que sea un scroll».

   En el teléfono, una tira horizontal cuyas tarjetas ocupan casi el
   ancho de la pantalla no parece una tira: parece una tarjeta suelta.
   Cuando la primera entra en pantalla se le da un empujón corto y
   vuelve sola: asoma la siguiente y el gesto se entiende sin explicarlo.

   Reglas de la casa:
   · solo en el teléfono, donde no hay flechas visibles,
   · UNA SOLA VEZ POR PÁGINA —la de la colección tiene cinco tiras y
     cinco empujones seguidos serían un tic—,
   · nunca si el cliente ya la ha movido con el dedo,
   · nunca con «reducir movimiento» activado en el sistema,
   · el `scroll-snap` se apaga durante el empujón: con `mandatory` el
     navegador pelea contra la animación y sale a tirones.

   El recorrido es un seno: sale y vuelve al mismo sitio en un solo
   trazo, sin encadenar animaciones ni dejar la tira a medias.
   ============================================================ */
(function () {
  'use strict';

  /* Cada tira con su corte: la portada esconde las flechas a partir de
     720 px; la colección se apila en columna a partir de 820. */
  var TIRAS = [
    { sel: '[data-carrusel]', media: '(max-width: 720px)' },  /* portada · confianza */
    { sel: '.cv2-tarjetas',   media: '(max-width: 820px)' }   /* colección · una tira por familia */
  ];

  if (!window.IntersectionObserver || !window.requestAnimationFrame || !window.matchMedia) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var gastado = false;   /* el empujón de esta página, ya dado */

  function empuja(pista) {
    var hijo = pista.firstElementChild;
    var ancho = hijo ? hijo.offsetWidth : pista.clientWidth;
    var distancia = Math.max(38, Math.min(64, ancho * 0.18));
    var duracion = 900, inicio = null;
    var snapPrevio = pista.style.scrollSnapType;
    /* De dónde sale y a dónde vuelve. NO se da por hecho que sea el cero:
       las tiras de la colección arrancan en 20 px por su propio relleno,
       y devolverlas a cero les movía el sitio. */
    var base = pista.scrollLeft;

    pista.dataset.empujando = '1';
    pista.style.scrollSnapType = 'none';

    function paso(ahora) {
      if (inicio === null) inicio = ahora;
      var p = (ahora - inicio) / duracion;
      if (p >= 1) {
        pista.scrollLeft = base;
        pista.style.scrollSnapType = snapPrevio;
        delete pista.dataset.empujando;
        return;
      }
      pista.scrollLeft = base + distancia * Math.sin(Math.PI * p);
      window.requestAnimationFrame(paso);
    }
    window.requestAnimationFrame(paso);
  }

  function vigila(pista) {
    var tocado = false;

    pista.addEventListener('scroll', function () {
      if (!pista.dataset.empujando) tocado = true;   /* lo ha movido el cliente */
    }, { passive: true });

    var vigia = new IntersectionObserver(function (entradas) {
      for (var i = 0; i < entradas.length; i++) {
        if (!entradas[i].isIntersecting) continue;
        vigia.disconnect();
        /* Quien dice si el cliente la ha tocado es el oyente de arriba, no
           el `scrollLeft`: las tiras de la colección no empiezan en cero. */
        if (gastado || tocado) return;
        if (pista.scrollWidth <= pista.clientWidth + 8) return;
        gastado = true;
        window.setTimeout(function () { if (!tocado) empuja(pista); }, 420);
      }
    }, { threshold: 0.45 });

    vigia.observe(pista);
  }

  for (var i = 0; i < TIRAS.length; i++) {
    if (!window.matchMedia(TIRAS[i].media).matches) continue;
    var pistas = document.querySelectorAll(TIRAS[i].sel);
    for (var j = 0; j < pistas.length; j++) vigila(pistas[j]);
  }
})();
