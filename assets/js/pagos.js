/* ============================================================
   laOra · FORMAS DE PAGO — única fuente de verdad
   ------------------------------------------------------------
   Aquí se dice qué formas de pago existen y con qué datos. La
   pantalla de pago lee esto: no hay ningún método escrito a mano
   en el HTML.

   REGLA: un método sin sus datos NO se enseña como si funcionara.
   Sale visible pero marcado como «todavía no disponible», igual
   que un acabado sin precio no enseña botón de compra. Es la
   misma idea: nunca ofrecer algo que no puede cobrar.

   CÓMO SE ACTIVA CADA UNO
   - `transferencia` y `bizum` son MANUALES y no cuestan comisión.
     Solo necesitan el IBAN y el teléfono. En cuanto los pongas
     aquí, funcionan: el pedido queda «pendiente» y el cliente ve
     las instrucciones. Se confirma cuando ves el dinero.
   - `tarjeta`, `bizum_automatico` y `paypal` van por **Mollie**:
     no hacen falta tres integraciones, Mollie las presenta todas.
     Se activan poniendo `LAORA_MOLLIE_API_KEY` como secreto de la
     Edge Function (es una credencial: la pone Óscar) y `activo:true`.
   - `sumup` necesitaría su propia integración aparte. Está aquí
     apagado y sin escribir: no se inventa un cobro que no existe.
   ============================================================ */

/* PONER A `true` el día que `LAORA_MOLLIE_API_KEY` esté como secreto de la
   Edge Function. Mientras esté en `false`, tarjeta, Bizum inmediato y PayPal
   salen visibles pero apagados. Es a propósito: el navegador no puede saber
   si el servidor tiene la clave, y es peor dejar que alguien rellene todo el
   formulario para llevarse un error que decirle la verdad desde el principio.

   LA CLAVE DE MOLLIE NO SE ESCRIBE AQUÍ NI EN NINGÚN FICHERO DEL REPO.
   El build output de Cloudflare Pages es `/`: todo lo que hay en el repo se
   publica en laora.es. Una clave `live_` aquí quedaría a la vista de
   cualquiera. Su sitio es Supabase → Edge Functions → Secrets, con el nombre
   `LAORA_MOLLIE_API_KEY`, que es donde la busca `crear-reserva.ts`. */
var LAORA_MOLLIE_LISTO = false;

var LAORA_PAGOS = {

  /* ---------- sin comisión, a mano ---------- */
  transferencia: {
    activo: true,
    comision: false,
    titulo: 'Transferencia',
    resumen: 'Te damos el IBAN y haces la transferencia tú. Sin comisión.',
    plazo: 'Confirmamos en cuanto llegue, de uno a dos días hábiles.',
    iban: 'ES22 1583 0001 1990 6408 6644',
    titular: 'laOra'
  },

  bizum: {
    activo: true,
    comision: false,
    titulo: 'Bizum a mano',
    resumen: 'Te damos el número y nos envías el importe tú. Sin comisión.',
    plazo: 'Confirmamos en cuanto llegue, normalmente el mismo día.',
    telefono: '+34 689 806 987'
  },

  /* ---------- pago inmediato, con comisión ---------- */
  tarjeta: {
    activo: true,
    comision: true,
    via: 'mollie',
    titulo: 'Tarjeta de crédito o débito',
    resumen: 'Pago inmediato y seguro. El pedido queda confirmado al momento.',
    plazo: 'Al instante.'
  },

  bizum_automatico: {
    activo: true,
    comision: true,
    via: 'mollie',
    titulo: 'Bizum inmediato',
    resumen: 'El mismo Bizum, pero automático: no hay que esperar a que lo revisemos.',
    plazo: 'Al instante.'
  },

  paypal: {
    activo: true,
    comision: true,
    via: 'mollie',
    titulo: 'PayPal',
    resumen: 'Pagas con tu cuenta de PayPal. El pedido queda confirmado al momento.',
    plazo: 'Al instante.'
  },

  sumup: {
    activo: false,
    comision: true,
    via: 'sumup',
    titulo: 'SumUp',
    resumen: 'Pago con tarjeta a través de SumUp.',
    plazo: 'Al instante.'
  }
};

/* Orden en que se enseñan. Primero los que no cuestan comisión. */
var LAORA_PAGOS_ORDEN = ['transferencia', 'bizum', 'tarjeta', 'bizum_automatico', 'paypal', 'sumup'];

/* ---- utilidades (no tocar) ---- */

/* Un método está listo para cobrar si está activo Y tiene sus datos. */
function laoraPagoListo(clave) {
  var m = LAORA_PAGOS[clave];
  if (!m || !m.activo) return false;
  if (clave === 'transferencia') return !!m.iban;
  if (clave === 'bizum') return !!m.telefono;
  if (m.via === 'mollie') return !!LAORA_MOLLIE_LISTO;
  return true;
}

/* El método que se manda al servidor. Las tres de Mollie son el mismo
   `mollie` para la Edge Function; lo que cambia es lo que se le enseña
   al cliente y qué método preselecciona la pasarela. */
function laoraPagoMetodoServidor(clave) {
  var m = LAORA_PAGOS[clave];
  if (!m) return null;
  if (m.via === 'mollie') return 'mollie';
  if (m.via === 'sumup') return 'sumup';
  return clave;
}

function laoraPagosDisponibles() {
  return LAORA_PAGOS_ORDEN.filter(function (k) { return LAORA_PAGOS[k] && LAORA_PAGOS[k].activo; });
}
