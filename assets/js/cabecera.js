/* Cabecera pegada: en cuanto se hace scroll, se queda fija y visible
   el resto de la página. Sin esto, `.cb` (position:absolute) desaparece
   para siempre pasado el primer scroll y no hay forma de navegar.
   No toca `.cb-home`: la home ya tiene su propio mecanismo (aparece
   oculta y entra al primer roce), más rico y no hace falta duplicarlo. */
(function () {
  var cab = document.querySelector('.cb:not(.cb-home)');
  if (!cab) return;

  var UMBRAL = 80;
  var pegada = null;
  var pedido = false;

  function revisa() {
    pedido = false;
    var y = window.scrollY || document.documentElement.scrollTop || 0;
    var debe = y > UMBRAL;
    if (debe === pegada) return;
    pegada = debe;
    cab.classList.toggle('cb-pegada', debe);
  }

  /* setTimeout en vez de requestAnimationFrame: esto es un simple
     cambio de clase, no una animación, y así no depende de que el
     navegador esté pintando fotogramas (una pestaña en segundo
     plano puede dejar de darlos). */
  addEventListener('scroll', function () {
    if (pedido) return;
    pedido = true;
    setTimeout(revisa, 60);
  }, { passive: true });

  revisa();
})();

/* ============================================================
   DESPLEGABLE DE MÓVIL
   ------------------------------------------------------------
   Por debajo de 900 px el menú no cabe en una fila. Hasta ahora
   simplemente se escondía y en el móvil no había forma de navegar.
   El botón se INYECTA desde aquí en vez de añadirlo al HTML de cada
   página: así lo tienen todas las del sitio sin tocar ni una.
   ============================================================ */
(function () {
  var cab = document.querySelector('.cb');
  if (!cab) return;
  var menu = cab.querySelector('.cb-menu');
  var bolsa = cab.querySelector('.cb-bolsa');
  if (!menu) return;

  if (!menu.id) menu.id = 'cb-menu';

  var boton = document.createElement('button');
  boton.type = 'button';
  boton.className = 'cb-hamburguesa';
  boton.setAttribute('aria-expanded', 'false');
  boton.setAttribute('aria-controls', menu.id);
  boton.setAttribute('aria-label', 'Abrir el menú');
  boton.innerHTML = '<span></span><span></span><span></span>';
  /* antes de la bolsa: deja el logo a la izquierda y el par
     botón + bolsa junto al borde derecho */
  if (bolsa) cab.insertBefore(boton, bolsa);
  else cab.appendChild(boton);

  function abrir(si) {
    cab.setAttribute('data-menu', si ? 'abierto' : 'cerrado');
    boton.setAttribute('aria-expanded', si ? 'true' : 'false');
    boton.setAttribute('aria-label', si ? 'Cerrar el menú' : 'Abrir el menú');
  }
  abrir(false);

  boton.addEventListener('click', function () {
    abrir(boton.getAttribute('aria-expanded') !== 'true');
  });

  /* al elegir un destino se cierra: si es un ancla de la propia página
     el panel se quedaría abierto tapando aquello a lo que acaba de saltar */
  menu.addEventListener('click', function (e) {
    if (e.target.closest('a')) abrir(false);
  });

  addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && boton.getAttribute('aria-expanded') === 'true') {
      abrir(false);
      boton.focus();
    }
  });

  /* si se ensancha la ventana hasta el menú de escritorio, el panel
     abierto dejaría el icono en aspa sin panel que cerrar */
  addEventListener('resize', function () {
    if (innerWidth > 900) abrir(false);
  });
})();
