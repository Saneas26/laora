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
