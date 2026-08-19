// ============================================================
// laOra · Edge Function: mollie-webhook
// ------------------------------------------------------------
// Mollie avisa aquí cada vez que cambia el estado de un pago.
// Nunca se fía del cuerpo que llega: Mollie solo manda el id, y
// somos nosotros los que preguntamos a Mollie qué ha pasado con
// nuestra propia clave. Así nadie puede marcar un pedido como
// pagado mandándonos un POST.
//
// ATIENDE DOS COSAS
//   · Los PEDIDOS de la tienda (lo de ahora). Se reconocen porque el
//     pago trae `metadata.pedido_id`, que le pone `pagar-pedido`.
//   · Las RESERVAS con señal del modelo antiguo, que siguen en pie.
//
// LOS ESTADOS, Y POR QUÉ
//   paid        → pagado. Es el caso normal: tarjeta, Bizum, PayPal.
//   authorized  → autorizado. Es Klarna: el dinero está reservado
//                 pero NO cobrado. Se captura al marcar el pedido
//                 como enviado, desde el panel. Hasta entonces, el
//                 pedido está en firme pero el dinero no ha entrado.
//   canceled / expired / failed → el pedido NO se cancela: se le
//                 borra la referencia del pago y vuelve a estar a la
//                 espera, para que el cliente pueda intentarlo otra
//                 vez sin llamar a nadie.
//
// Desplegar con «Enforce JWT verification» DESACTIVADO.
// Secretos: LAORA_MOLLIE_API_KEY (SUPABASE_URL y la clave secreta las pone Supabase)
// La service_role ha cambiado de nombre: antes SUPABASE_SERVICE_ROLE_KEY,
// ahora SUPABASE_SECRET_KEYS (un JSON con varias). Se aceptan las dos para
// que esto no se rompa el día que Supabase retire la vieja.
function claveSecreta(): string | null {
  const propia = Deno.env.get('LAORA_SERVICIO');
  if (propia) return propia;
  const vieja = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (vieja) return vieja;
  try {
    const json = Deno.env.get('SUPABASE_SECRET_KEYS');
    if (!json) return null;
    const d = JSON.parse(json);
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return d[0]?.api_key ?? d[0] ?? null;
    return d.default ?? d.secret ?? Object.values(d)[0] as string ?? null;
  } catch { return null; }
}

/* Lo que Mollie llama a cada forma de pago, en nuestro idioma. */
const METODOS: Record<string, string> = {
  creditcard: 'tarjeta', klarna: 'klarna', bizum: 'bizum',
  paypal: 'paypal', banktransfer: 'transferencia',
};

// ============================================================

Deno.serve(async (req) => {
  if (req.method !== 'POST') return new Response('método no permitido', { status: 405 });

  try {
    const cuerpo = new URLSearchParams(await req.text());
    const id = cuerpo.get('id');
    if (!id || !id.startsWith('tr_')) return new Response('sin id', { status: 400 });

    const MOLLIE = Deno.env.get('LAORA_MOLLIE_API_KEY');
    const SB = Deno.env.get('SUPABASE_URL');
    const SERVICE = claveSecreta();
    if (!MOLLIE || !SB || !SERVICE) return new Response('faltan secretos', { status: 500 });

    // Se pregunta a Mollie. Su respuesta es la única que vale.
    const r = await fetch(`https://api.mollie.com/v2/payments/${id}`, {
      headers: { Authorization: `Bearer ${MOLLIE}` },
    });
    if (!r.ok) {
      console.error('mollie:', await r.text());
      return new Response('mollie no responde', { status: 502 });
    }
    const pago = await r.json();

    const db = (ruta: string, cambios: unknown) =>
      fetch(`${SB}/rest/v1/${ruta}`, {
        method: 'PATCH',
        headers: {
          apikey: SERVICE,
          Authorization: `Bearer ${SERVICE}`,
          'Content-Type': 'application/json',
          'Content-Profile': 'laora',
          Prefer: 'return=minimal',
        },
        body: JSON.stringify(cambios),
      });

    // ---------- 1. los pedidos de la tienda ----------
    const pedidoId = pago.metadata?.pedido_id;
    if (pedidoId) {
      const cambios: Record<string, unknown> = { actualizado_en: new Date().toISOString() };

      if (pago.status === 'paid') {
        cambios.estado = 'pagado';
        cambios.pagado_en = pago.paidAt || new Date().toISOString();
        if (METODOS[pago.method]) cambios.metodo = METODOS[pago.method];
      } else if (pago.status === 'authorized') {
        // Klarna: reservado, todavía no cobrado. Se captura al enviar.
        cambios.estado = 'autorizado';
        if (METODOS[pago.method]) cambios.metodo = METODOS[pago.method];
      } else if (['canceled', 'expired', 'failed'].includes(pago.status)) {
        // Que pueda volver a intentarlo sin tener que llamar a nadie.
        cambios.referencia_pago = null;
      } else {
        return new Response('ok');   // open, pending… todavía no hay nada que hacer
      }

      const up = await db(`pedidos?id=eq.${encodeURIComponent(pedidoId)}`, cambios);
      if (!up.ok) {
        console.error('pedido:', await up.text());
        return new Response('no se pudo actualizar', { status: 502 });
      }
      return new Response('ok');
    }

    // ---------- 2. las reservas del modelo antiguo ----------
    const estados: Record<string, string> = {
      paid: 'pagada',
      canceled: 'cancelada',
      expired: 'cancelada',
      failed: 'cancelada',
    };
    const estado = estados[pago.status];
    if (!estado) return new Response('ok');

    const cambios: Record<string, unknown> = { estado };
    if (estado === 'pagada') cambios.pagada_en = new Date().toISOString();

    // Se localiza por el id de Mollie, no por lo que venga de fuera.
    const up = await db(`reservas?mollie_id=eq.${encodeURIComponent(id)}`, cambios);
    if (!up.ok) {
      console.error('supabase:', await up.text());
      return new Response('no se pudo actualizar', { status: 502 });
    }

    // Mollie reintenta si no recibe un 200.
    return new Response('ok');
  } catch (e) {
    console.error(e);
    return new Response('error', { status: 500 });
  }
});
