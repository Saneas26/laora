/* ============================================================
   laOra · PRECIOS — única fuente de verdad
   ------------------------------------------------------------
   Este fichero manda. La web, el botón de reserva y el importe
   que se cobra salen todos de aquí. No hay precios escritos a
   mano en ningún otro sitio del checkout.

   CÓMO SE RELLENA
   - `precio` es el PRECIO FINAL AL PÚBLICO, con el IVA del 21%
     ya dentro, en euros. Un número, sin símbolo y sin comillas.
   - `precio: null` significa «este acabado todavía no está a la
     venta». Su botón no cobra: sale «Avísame del estreno», igual
     que hasta ahora. Así ningún acabado sin precio cerrado puede
     cobrar un importe inventado.
   - `horquilla` es solo el texto que ya se enseña en la ficha.
     No se usa para cobrar. Está aquí al lado para que rellenar
     `precio` sea mirar una línea.
   - `stock` son las UNIDADES QUE HAY HECHAS de ese acabado. Hoy
     está a 0 en todas. Cambia dos cosas cuando sube de 0:
       · la entrega pasa de «30 días» a lo que diga
         LAORA_ENTREGA_CON_STOCK, y
       · el pago pasa a ser COMPLETO de una vez, sin señal.

   SEÑAL O PAGO COMPLETO
   - Sin stock (se fabrica para ti): se cobra el SENAL_PORCENTAJE
     y el resto al enviarlo.
   - Con stock (está hecho y en el almacén de Madrid): se cobra
     entero de una vez, porque no hay nada que esperar.
   Ver `condiciones-de-venta.html`: la señal es a cuenta del precio
   y se devuelve entera si el cliente desiste en 14 días.
   ============================================================ */

var LAORA_SENAL_PORCENTAJE = 25;
var LAORA_IVA = 21;

var LAORA_PRECIOS = {
  'LO-01': {
    nombre: 'Lunar',
    /* Precios cerrados por Óscar el 30/07/2026, con el IVA del 21 % dentro.
       El acabado Levante queda DESCARTADO en este modelo (no existe, no se
       enseña). Eclipse todavía no está disponible: sin precio no se puede
       comprar, y su horquilla es solo orientativa y está sin revisar desde
       antes de cerrar estos dos precios. */
    acabados: {
      Alba:    { precio: 239.90, horquilla: 'Desde 239,90 €', stock: 0 },
      Cenit:   { precio: 379.90, horquilla: '379,90 €', stock: 0 },
      Eclipse: { precio: null,   horquilla: '550–750 €', stock: 0 }
    }
  },
  'LO-02': {
    nombre: 'Cero Cero',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 190 €', stock: 0 },
      Levante: { precio: null, horquilla: '280–380 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '400–560 €', stock: 0 },
      Eclipse: { precio: null, horquilla: '560–750 €', stock: 0 }
    }
  },
  'LO-03': {
    nombre: 'Bauhaus',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 170 €', stock: 0 },
      Levante: { precio: null, horquilla: '260–360 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '360–480 €', stock: 0 },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit', stock: 0 }
    }
  },
  'LO-04': {
    nombre: 'Precisa',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 190 €', stock: 0 },
      Levante: { precio: null, horquilla: '280–380 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '400–560 €', stock: 0 },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit', stock: 0 }
    }
  },
  'LO-05': {
    nombre: 'Trinchera',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 150 €', stock: 0 },
      Levante: { precio: null, horquilla: '230–320 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '330–450 €', stock: 0 },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit', stock: 0 }
    }
  },
  'LO-06': {
    nombre: 'Ocho Lados',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 250 €', stock: 0 },
      Levante: { precio: null, horquilla: '350–480 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '500–700 €', stock: 0 },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit', stock: 0 }
    }
  },
  /* LO-07 es el primero con precio cerrado (boceto de Óscar, 29/07/2026).
     Tres versiones, no cuatro: la Bitácora no lleva Eclipse. */
  'LO-07': {
    nombre: 'Bitácora',
    acabados: {
      Alba:    { precio: 250, horquilla: '250 €', stock: 0 },
      Levante: { precio: 320, horquilla: '320 €', stock: 0 },
      Cenit:   { precio: 420, horquilla: '420 €', stock: 0 }
    }
  },
  'LO-08': {
    nombre: 'Tortuga',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 180 €', stock: 0 },
      Levante: { precio: null, horquilla: '260–350 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '360–500 €', stock: 0 },
      Eclipse: { precio: null, horquilla: '500–650 €', stock: 0 }
    }
  },
  'LO-09': {
    nombre: 'Cóctel',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 180 €', stock: 0 },
      Levante: { precio: null, horquilla: '270–370 €', stock: 0 },
      Cenit:   { precio: null, horquilla: '380–500 €', stock: 0 },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit', stock: 0 }
    }
  }
};

/* ---- ENTREGA ----
   Sin stock el reloj se fabrica para el cliente y el plazo es de 30 días
   desde el pago, que es además lo que da la ley cuando no hay otra fecha
   pactada. Con stock el reloj ya está en el almacén de Madrid y solo hay
   que enviarlo; mientras `CON_STOCK` esté vacío se usa el mismo plazo de
   30 días, que nunca promete de menos. */
/* ¡OJO! `LAORA_ENTREGA` TIENE QUE SER UN TEXTO ENTRE COMILLAS SIMPLES.
   La Edge Function NO ejecuta este fichero: lo descarga y lo lee con la
   expresión /var LAORA_ENTREGA\s*=\s*'([^']*)'/. Si aquí se pone una
   variable en lugar de un literal, el servidor lee cadena vacía, cree que
   no hay fecha comprometida y DEJA DE COBRAR TODO con un 409. Pasó al
   escribir esto y no se vio hasta replicar el parser a mano. */
var LAORA_ENTREGA = '30 días desde el pago';

var LAORA_ENTREGA_SIN_STOCK = LAORA_ENTREGA;
var LAORA_ENTREGA_CON_STOCK = '';   // ← p. ej. 'sale de Madrid en 24-48 h'

/* ---- utilidades (no tocar) ---- */
function laoraSenal(precio) {
  return Math.round(precio * LAORA_SENAL_PORCENTAJE) / 100;
}
function laoraEuros(n) {
  return n.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
}
function laoraAcabado(ref, nombre) {
  var m = LAORA_PRECIOS[ref];
  if (!m || !m.acabados[nombre]) return null;
  var a = m.acabados[nombre];
  return { ref: ref, modelo: m.nombre, acabado: nombre, precio: a.precio,
           horquilla: a.horquilla, stock: a.stock || 0 };
}
/* Se puede cobrar solo si hay precio Y fecha de entrega comprometida. */
function laoraSePuedeReservar(ref, nombre) {
  var a = laoraAcabado(ref, nombre);
  return !!(a && a.precio && LAORA_ENTREGA);
}

function laoraHayStock(ref, nombre) {
  var a = laoraAcabado(ref, nombre);
  return !!(a && a.stock > 0);
}

function laoraEntregaDe(ref, nombre) {
  return laoraHayStock(ref, nombre)
    ? (LAORA_ENTREGA_CON_STOCK || LAORA_ENTREGA_SIN_STOCK)
    : LAORA_ENTREGA_SIN_STOCK;
}

/* ---- SEÑAL O PAGO COMPLETO ----
   Con stock se cobra entero; sin stock, la señal. En un pedido con varias
   líneas basta que una se fabrique para que todo el pedido vaya con señal:
   partirlo en dos cobros sería peor de entender y peor de devolver.

   OJO, ESTO ESTÁ CAPADO A PROPÓSITO: la Edge Function que cobra todavía
   cobra SIEMPRE el 25 %. Mientras `LAORA_SERVIDOR_SOPORTA_STOCK` sea
   `false`, la web se comporta como el servidor y no promete un pago
   completo que el servidor no haría. Se pone a `true` el día que se
   despliegue la función actualizada, y no antes: si no, la pantalla diría
   un importe y se cobraría otro. Hoy da igual porque todo el stock es 0. */
var LAORA_SERVIDOR_SOPORTA_STOCK = false;

function laoraPagoCompleto(items) {
  if (!LAORA_SERVIDOR_SOPORTA_STOCK) return false;
  return items.length > 0 && items.every(function (i) { return laoraHayStock(i.ref, i.acabado); });
}
