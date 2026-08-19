// ============================================================
// laOra · Edge Function: pagar-pedido
// ------------------------------------------------------------
// Abre el cobro de un pedido que YA está escrito. Devuelve la
// dirección del checkout de Mollie: tarjeta o transferencia por un
// lado, y Klarna en tres plazos por otro.
//
// POR QUÉ EXISTE
//   Hasta hoy el carrito abría un enlace de paypal.me con el importe
//   y ahí se acababa: llegaba un ingreso suelto que había que cruzar
//   a mano con el pedido, y la web anunciaba un pago con Klarna que
//   en realidad no se podía usar. Esto lo cierra: Mollie cobra, avisa
//   por el webhook y el pedido queda pagado solo.
//
//   El Bizum y el PayPal de la casa NO pasan por aquí: van por fuera
//   de Mollie y se cobran a mano.
//
// EL IMPORTE NO SE ACEPTA DE FUERA
//   Aquí no entra ni un número del navegador. Solo el número de
//   pedido; el importe y las líneas se leen de la base de datos, que
//   es donde los escribió `crear-pedido` calculándolos del catálogo.
//
// NO SE COBRA DOS VECES
//   Si el pedido ya tiene un pago abierto en Mollie, se devuelve ESE
//   checkout, no uno nuevo. Un doble clic no puede acabar en dos
//   cobros (en Saneas ya pasó una vez, y con eso basta).
//
// KLARNA SE AUTORIZA, NO SE COBRA
//   Mollie lo pide por escrito al aprobar Klarna: primero se autoriza
//   y el dinero se captura cuando el pedido sale por la puerta, con
//   28 días de margen. Por eso Klarna va con `captureMode: manual` y
//   la captura la dispara el panel al marcar el pedido como enviado.
//   Con las demás formas de pago se cobra al momento, como siempre.
//
// DESPLIEGUE
//   supabase functions deploy pagar-pedido \
//     --project-ref uikanfvigunjhzibnhxf --no-verify-jwt
//   (JWT desactivado a propósito: el token lo comprobamos nosotros y
//   así el error que ve el cliente es nuestro y en español.)
//
//   Secretos: LAORA_MOLLIE_API_KEY (la de Mollie), LAORA_SERVICIO o
//   SUPABASE_SERVICE_ROLE_KEY, y los que pone Supabase solo.
// ============================================================

const WEB = Deno.env.get('LAORA_WEB_URL') ?? 'https://laora.es';

/* El webhook está desplegado con este nombre desde las reservas. */
const WEBHOOK = 'laora-mollie-webhook';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const json = (cuerpo: unknown, status = 200) =>
  new Response(JSON.stringify(cuerpo), {
    status,
    headers: { ...cors, 'Content-Type': 'application/json' },
  });

const dos = (n: number) => (Math.round(n * 100) / 100).toFixed(2);

/* Los métodos que se pueden pedir desde la web, con lo que hay que
   mandarle a Mollie. `null` = que enseñe todos los que tenga activos.

   OJO CON KLARNA: va en su propio botón y NO se mezcla con los demás.
   Si saliera dentro del checkout general, el pago se crearía con
   captura automática y se le cobraría al cliente antes de que su reloj
   saliera del taller, que es justo lo que Mollie prohíbe. Por eso el
   botón normal filtra los métodos y deja Klarna fuera.

   La cuenta tiene activos hoy (19/08/2026): tarjeta, Klarna y
   transferencia. El Bizum y el PayPal de la casa van por fuera de
   Mollie, así que aquí no aparecen. */
const METODOS: Record<string, string | string[] | null> = {
  '': null,
  tarjeta: ['creditcard', 'banktransfer'],
  klarna: 'klarna',
};

async function quienEs(token: string, url: string, anon: string) {
  const r = await fetch(`${url}/auth/v1/user`, {
    headers: { Authorization: `Bearer ${token}`, apikey: anon },
  });
  if (!r.ok) return null;
  const u = await r.json();
  return u?.id ? { id: u.id as string, email: (u.email as string) || '' } : null;
}

/* El nombre se guarda entero en una sola casilla; Klarna lo quiere
   partido en nombre y apellidos. */
function parteNombre(entero: string) {
  const trozos = String(entero || '').trim().split(/\s+/);
  const givenName = trozos.shift() || 'Cliente';
  return { givenName, familyName: trozos.join(' ') || givenName };
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'solo POST' }, 405);

  const URL_SB = Deno.env.get('SUPABASE_URL');
  const ANON = Deno.env.get('SUPABASE_ANON_KEY');
  const SERVICIO = Deno.env.get('LAORA_SERVICIO') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  const MOLLIE = Deno.env.get('LAORA_MOLLIE_API_KEY');
  if (!URL_SB || !ANON || !SERVICIO) return json({ error: 'configuración incompleta' }, 500);
  if (!MOLLIE) return json({ error: 'La pasarela no está configurada.' }, 500);

  const token = (req.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '').trim();
  if (!token) return json({ error: 'Hay que entrar antes de pagar.' }, 401);

  const socio = await quienEs(token, URL_SB, ANON);
  if (!socio) return json({ error: 'Tu sesión ha caducado. Vuelve a entrar.' }, 401);

  let cuerpo: any;
  try { cuerpo = await req.json(); } catch { return json({ error: 'petición ilegible' }, 400); }

  const numero = String(cuerpo?.numero || '').trim().slice(0, 30);
  if (!/^[A-Za-z0-9-]+$/.test(numero)) return json({ error: 'falta el número del pedido' }, 400);

  const metodoPedido = String(cuerpo?.metodo || '');
  if (!(metodoPedido in METODOS)) return json({ error: 'forma de pago no válida' }, 400);
  const metodoMollie = METODOS[metodoPedido];

  const rest = (ruta: string, opciones: RequestInit = {}) =>
    fetch(`${URL_SB}/rest/v1/${ruta}`, {
      ...opciones,
      headers: {
        apikey: SERVICIO,
        Authorization: `Bearer ${SERVICIO}`,
        'Content-Type': 'application/json',
        'Content-Profile': 'laora',
        'Accept-Profile': 'laora',
        Prefer: 'return=representation',
        ...(opciones.headers || {}),
      },
    });

  /* ---------- el pedido, y que sea suyo ---------- */
  const rPed = await rest(
    `pedidos?select=*,pedido_lineas(*)&numero=eq.${encodeURIComponent(numero)}` +
    `&socio_id=eq.${socio.id}&limit=1`);
  if (!rPed.ok) {
    console.error('pedido', rPed.status, await rPed.text());
    return json({ error: 'No hemos podido leer tu pedido.' }, 500);
  }
  const pedido = (await rPed.json())[0];
  if (!pedido) return json({ error: 'Ese pedido no existe o no es tuyo.' }, 404);

  if (['pagado', 'preparando', 'enviado', 'entregado'].includes(pedido.estado)) {
    return json({ error: 'Este pedido ya está pagado.', pagado: true }, 409);
  }
  if (pedido.estado === 'cancelado') {
    return json({ error: 'Este pedido está cancelado.' }, 409);
  }

  /* ---------- ¿ya había un pago abierto? ----------
     Se le pregunta a Mollie por él. Si sigue vivo, se devuelve el
     mismo checkout: dos clics no pueden ser dos cobros. */
  if (pedido.referencia_pago) {
    const r = await fetch(`https://api.mollie.com/v2/payments/${pedido.referencia_pago}`, {
      headers: { Authorization: `Bearer ${MOLLIE}` },
    });
    if (r.ok) {
      const viejo = await r.json();
      if (['open', 'pending'].includes(viejo.status) && viejo._links?.checkout?.href) {
        return json({ ok: true, url: viejo._links.checkout.href, reusado: true });
      }
      if (['paid', 'authorized'].includes(viejo.status)) {
        return json({ error: 'Este pedido ya está pagado.', pagado: true }, 409);
      }
    }
  }

  /* ---------- las líneas, tal como se vendieron ---------- */
  const lineas = (pedido.pedido_lineas || []) as any[];
  if (!lineas.length) return json({ error: 'Ese pedido no tiene nada dentro.' }, 409);

  const IVA = 21;
  const lines = lineas.map((l) => {
    const total = Number(l.precio) * Number(l.cantidad);
    return {
      type: 'physical',
      description: `${l.modelo} · ${l.correa || l.acabado}`.slice(0, 200),
      quantity: Number(l.cantidad),
      unitPrice: { currency: 'EUR', value: dos(Number(l.precio)) },
      totalAmount: { currency: 'EUR', value: dos(total) },
      vatRate: IVA.toFixed(2),
      /* El precio ya lleva el IVA dentro, así que se saca de él. */
      vatAmount: { currency: 'EUR', value: dos((total * IVA) / (100 + IVA)) },
      sku: String(l.ref).slice(0, 64),
      productUrl: `${WEB}/coleccion.html`,
    };
  });

  if (Number(pedido.envio) > 0) {
    lines.push({
      type: 'shipping_fee',
      description: 'Envío',
      quantity: 1,
      unitPrice: { currency: 'EUR', value: dos(Number(pedido.envio)) },
      totalAmount: { currency: 'EUR', value: dos(Number(pedido.envio)) },
      vatRate: IVA.toFixed(2),
      vatAmount: { currency: 'EUR', value: dos((Number(pedido.envio) * IVA) / (100 + IVA)) },
    } as any);
  }

  const { givenName, familyName } = parteNombre(pedido.env_nombre);
  const direccion = {
    givenName, familyName,
    streetAndNumber: String(pedido.env_direccion || '').slice(0, 200),
    postalCode: String(pedido.env_cp || ''),
    city: String(pedido.env_poblacion || ''),
    country: 'ES',
    email: socio.email,
    ...(pedido.env_telefono ? { phone: String(pedido.env_telefono) } : {}),
  };

  const pago: Record<string, unknown> = {
    amount: { currency: 'EUR', value: dos(Number(pedido.total)) },
    description: `laOra · pedido ${pedido.numero}`,
    redirectUrl: `${WEB}/cuenta.html?pedido=${encodeURIComponent(pedido.numero)}`,
    cancelUrl: `${WEB}/carrito.html`,
    webhookUrl: `${URL_SB}/functions/v1/${WEBHOOK}`,
    locale: 'es_ES',
    lines,
    billingAddress: direccion,
    shippingAddress: direccion,
    metadata: { pedido_id: pedido.id, numero: pedido.numero },
  };
  if (metodoMollie) pago.method = metodoMollie;

  /* Klarna: se autoriza ahora y se cobra al enviar. Es lo que Mollie
     exige y lo que evita cobrarle a alguien un reloj que aún no ha
     salido del taller. */
  if (metodoPedido === 'klarna') pago.captureMode = 'manual';

  const rPago = await fetch('https://api.mollie.com/v2/payments', {
    method: 'POST',
    headers: { Authorization: `Bearer ${MOLLIE}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(pago),
  });

  if (!rPago.ok) {
    console.error('mollie', rPago.status, await rPago.text());
    return json({ error: 'La pasarela no ha respondido. Inténtalo en un momento.' }, 502);
  }
  const p = await rPago.json();

  /* Se anota el pago ANTES de mandar a nadie a pagar: si esto fallara
     tendríamos un cobro sin pedido al que pegarlo. */
  const rUp = await rest(`pedidos?id=eq.${pedido.id}`, {
    method: 'PATCH',
    body: JSON.stringify({
      referencia_pago: p.id,
      metodo: metodoPedido || pedido.metodo,
      actualizado_en: new Date().toISOString(),
    }),
  });
  if (!rUp.ok) console.error('anotar pago', rUp.status, await rUp.text());

  return json({ ok: true, url: p._links?.checkout?.href, pago: p.id });
});
