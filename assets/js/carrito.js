/* ============================================================
   laOra · Carrito
   ------------------------------------------------------------
   Cesta en el propio navegador (localStorage). No hay cuenta de
   usuario ni servidor de por medio: si vacías el navegador, se
   vacía el carrito. Es lo correcto para una web sin login.

   OJO con el dinero: aquí se guardan `ref` y `detalle`, y el
   precio SOLO para pintarlo. Quien decide lo que se cobra sigue
   siendo el servidor (Edge Function `laora-crear-reserva`, que
   recalcula desde precios.js). Si alguien manipula el carrito,
   lo único que consigue es ver un número falso en su pantalla.
   ============================================================ */

var LAORA_CARRITO_CLAVE = 'laora.carrito.v1';

function laoraCarritoLeer() {
  try {
    var v = JSON.parse(localStorage.getItem(LAORA_CARRITO_CLAVE) || '[]');
    return Array.isArray(v) ? v : [];
  } catch (e) { return []; }
}

function laoraCarritoGuardar(lineas) {
  try { localStorage.setItem(LAORA_CARRITO_CLAVE, JSON.stringify(lineas)); } catch (e) {}
  laoraCarritoPintarContador();
  document.dispatchEvent(new CustomEvent('laora:carrito', { detail: lineas }));
}

function laoraCarritoUnidades() {
  return laoraCarritoLeer().reduce(function (n, l) { return n + (l.cantidad || 1); }, 0);
}

function laoraCarritoAnadir(linea) {
  var lineas = laoraCarritoLeer();
  var igual = lineas.filter(function (l) {
    return l.ref === linea.ref && l.detalle === linea.detalle &&
           (l.esfera || '') === (linea.esfera || '') &&
           JSON.stringify(l.extras || []) === JSON.stringify(linea.extras || []);
  })[0];
  if (igual) igual.cantidad = (igual.cantidad || 1) + 1;
  else { linea.cantidad = 1; lineas.push(linea); }
  laoraCarritoGuardar(lineas);
  /* Se apunta lo último que ha entrado para que la pantalla del
     carrito pueda decir QUÉ se ha añadido. Vale para un solo viaje: se
     lee y se borra, porque al recargar ya no es una noticia. */
  try { sessionStorage.setItem('laora.ultimo', linea.nombre || ''); } catch (e) {}
  return lineas;
}

function laoraCarritoQuitar(i) {
  var lineas = laoraCarritoLeer();
  lineas.splice(i, 1);
  laoraCarritoGuardar(lineas);
}

/* Se vacía al saltar al pago: a partir de ahí lo que vale es el
   pedido, que ya está escrito y con su número. Dejar la cesta llena
   invita a comprar dos veces lo mismo. */
function laoraCarritoVaciar() {
  laoraCarritoGuardar([]);
}

function laoraCarritoCantidad(i, n) {
  var lineas = laoraCarritoLeer();
  if (!lineas[i]) return;
  lineas[i].cantidad = Math.max(1, Math.min(9, n));
  laoraCarritoGuardar(lineas);
}

function laoraCarritoTotal() {
  return laoraCarritoLeer().reduce(function (t, l) {
    return t + (Number(l.precio) || 0) * (l.cantidad || 1);
  }, 0);
}

/* El número en el icono de la bolsa. Si no hay nada, no se pinta:
   un cero permanente es ruido. */
function laoraCarritoPintarContador() {
  var n = laoraCarritoUnidades();
  Array.prototype.forEach.call(document.querySelectorAll('[data-carrito-cuenta]'), function (e) {
    e.textContent = n;
    e.hidden = n === 0;
  });
}

document.addEventListener('DOMContentLoaded', laoraCarritoPintarContador);
/* otra pestaña puede haber cambiado el carrito */
window.addEventListener('storage', function (e) {
  if (e.key === LAORA_CARRITO_CLAVE) laoraCarritoPintarContador();
});
