/* ============================================================
   laOra · LA CABECERA — el menú del móvil
   ------------------------------------------------------------
   Lo único que necesita moverse en la cabecera: abrir y cerrar el
   menú en pantallas pequeñas. Va aparte para que TODAS las páginas
   puedan llevar la misma cabecera sin arrastrar el resto del script
   de la portada.

   Si este fichero no llega a cargarse, la cabecera se sigue leyendo y
   el logotipo, la cuenta y el carrito siguen funcionando: lo único
   que se pierde es desplegar el menú en el móvil.
   ============================================================ */
(function () {
  'use strict';

  var boton = document.querySelector('[data-menu]');
  var nav = document.querySelector('[data-nav]');
  if (!boton || !nav) return;

  boton.addEventListener('click', function () {
    var abierto = nav.classList.toggle('open');
    boton.setAttribute('aria-expanded', String(abierto));
    boton.setAttribute('aria-label', abierto ? 'Cerrar menú' : 'Abrir menú');
  });

  /* Al elegir un enlace, el menú se cierra. En una sola página no hace
     falta —se recarga—, pero si algún día hay un enlace interno queda
     resuelto y no cuesta nada. */
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) nav.classList.remove('open');
  });
})();
