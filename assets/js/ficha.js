/* ============================================================
   laOra · FICHA DE RELOJ
   ------------------------------------------------------------
   Solo la galería: cambiar la miniatura cambia la foto grande.

   Las miniaturas ya vienen escritas en el HTML desde el generador,
   así que si el JavaScript no llega a cargarse la ficha se sigue
   leyendo entera con su primera foto. No hay nada aquí de lo que
   dependa el contenido.
   ============================================================ */
(function () {
  'use strict';

  var grande = document.querySelector('[data-foto-grande]');
  var minis = document.querySelectorAll('[data-mini]');
  if (!grande || minis.length < 2) return;

  function elegir(boton) {
    grande.src = boton.dataset.mini;
    for (var i = 0; i < minis.length; i++) {
      minis[i].setAttribute('aria-current', String(minis[i] === boton));
    }
  }

  for (var i = 0; i < minis.length; i++) {
    (function (boton) {
      boton.addEventListener('click', function () { elegir(boton); });
    })(minis[i]);
  }
})();
