/* ============================================================
   laOra · LANDING V2 DEL LUNAR
   ------------------------------------------------------------
   Lo justo: abrir el menú y que los acordeones no se queden todos
   abiertos a la vez. Todo lo demás lo hace el CSS.

   Si este fichero no llega a cargarse la página se sigue leyendo
   entera: el menú es un <nav> con enlaces normales y los acordeones
   son <details>, que abren y cierran sin JavaScript.
   ============================================================ */
(function () {
  'use strict';

  /* ---------- el menú ---------- */
  var boton = document.querySelector('.cab-boton');
  var menu = document.getElementById('menu');

  if (boton && menu) {
    var abrir = function (si) {
      menu.hidden = !si;
      boton.setAttribute('aria-expanded', String(si));
      boton.textContent = si ? '×' : '☰';
      boton.setAttribute('aria-label', si ? 'Cerrar menú' : 'Abrir menú');
    };

    boton.addEventListener('click', function () { abrir(menu.hidden); });

    /* al elegir destino, el menú sobra */
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') abrir(false);
    });

    /* fuera del menú y con Escape, también se cierra */
    document.addEventListener('click', function (e) {
      if (!menu.hidden && !menu.contains(e.target) && e.target !== boton) abrir(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) { abrir(false); boton.focus(); }
    });
  }

  /* ---------- los acordeones, de uno en uno ----------
     Dentro de un mismo bloque solo se queda abierto el último que se
     ha tocado. Con nueve especificaciones abiertas a la vez, la
     pantalla se convierte en el muro de texto del que veníamos. */
  var bloques = document.querySelectorAll('.acordeon');
  for (var i = 0; i < bloques.length; i++) {
    (function (bloque) {
      var fichas = bloque.querySelectorAll('details');
      for (var j = 0; j < fichas.length; j++) {
        (function (ficha) {
          ficha.addEventListener('toggle', function () {
            if (!ficha.open) return;
            for (var k = 0; k < fichas.length; k++) {
              if (fichas[k] !== ficha) fichas[k].open = false;
            }
          });
        })(fichas[j]);
      }
    })(bloques[i]);
  }
})();
