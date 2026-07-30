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

   LA SEÑAL
   Se cobra el SEÑAL_PORCENTAJE del precio final. El resto se
   cobra al enviar el reloj. Ver `condiciones-de-venta.html`:
   la señal es a cuenta del precio y se devuelve entera si el
   cliente desiste dentro de los 14 días.
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
      Alba:    { precio: 239.90, horquilla: 'Desde 239,90 €' },
      Cenit:   { precio: 379.90, horquilla: '379,90 €' },
      Eclipse: { precio: null,   horquilla: '550–750 €' }
    }
  },
  'LO-02': {
    nombre: 'Cero Cero',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 190 €' },
      Levante: { precio: null, horquilla: '280–380 €' },
      Cenit:   { precio: null, horquilla: '400–560 €' },
      Eclipse: { precio: null, horquilla: '560–750 €' }
    }
  },
  'LO-03': {
    nombre: 'Bauhaus',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 170 €' },
      Levante: { precio: null, horquilla: '260–360 €' },
      Cenit:   { precio: null, horquilla: '360–480 €' },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit' }
    }
  },
  'LO-04': {
    nombre: 'Precisa',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 190 €' },
      Levante: { precio: null, horquilla: '280–380 €' },
      Cenit:   { precio: null, horquilla: '400–560 €' },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit' }
    }
  },
  'LO-05': {
    nombre: 'Trinchera',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 150 €' },
      Levante: { precio: null, horquilla: '230–320 €' },
      Cenit:   { precio: null, horquilla: '330–450 €' },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit' }
    }
  },
  'LO-06': {
    nombre: 'Ocho Lados',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 250 €' },
      Levante: { precio: null, horquilla: '350–480 €' },
      Cenit:   { precio: null, horquilla: '500–700 €' },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit' }
    }
  },
  /* LO-07 es el primero con precio cerrado (boceto de Óscar, 29/07/2026).
     Tres versiones, no cuatro: la Bitácora no lleva Eclipse. */
  'LO-07': {
    nombre: 'Bitácora',
    acabados: {
      Alba:    { precio: 250, horquilla: '250 €' },
      Levante: { precio: 320, horquilla: '320 €' },
      Cenit:   { precio: 420, horquilla: '420 €' }
    }
  },
  'LO-08': {
    nombre: 'Tortuga',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 180 €' },
      Levante: { precio: null, horquilla: '260–350 €' },
      Cenit:   { precio: null, horquilla: '360–500 €' },
      Eclipse: { precio: null, horquilla: '500–650 €' }
    }
  },
  'LO-09': {
    nombre: 'Cóctel',
    acabados: {
      Alba:    { precio: null, horquilla: 'Desde 180 €' },
      Levante: { precio: null, horquilla: '270–370 €' },
      Cenit:   { precio: null, horquilla: '380–500 €' },
      Eclipse: { precio: null, horquilla: 'Prima de +50–100 € sobre Cenit' }
    }
  }
};

/* Fecha de entrega comprometida. Es OBLIGATORIA para poder cobrar:
   sin fecha pactada, la ley da 30 días desde el pago. Se enseña en
   el checkout y se guarda con cada reserva.
   Formato libre y corto, p. ej. 'antes del 31 de marzo de 2027'. */
var LAORA_ENTREGA = '';

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
  return { ref: ref, modelo: m.nombre, acabado: nombre, precio: a.precio, horquilla: a.horquilla };
}
/* Se puede cobrar solo si hay precio Y fecha de entrega comprometida. */
function laoraSePuedeReservar(ref, nombre) {
  var a = laoraAcabado(ref, nombre);
  return !!(a && a.precio && LAORA_ENTREGA);
}
