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
// Secretos: LAORA_MOLLIE_API_KEY · RESEND_API_KEY · INTERESADOS_EMAIL
//           (SUPABASE_URL y la clave secreta las pone Supabase)
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

/* ============================================================
   LOS DOS CORREOS DE UN PEDIDO PAGADO
   ------------------------------------------------------------
   · A Óscar, para que se entere en el momento y no cuando se
     acuerde de entrar en el panel.
   · Al cliente, que NO es opcional: la confirmación del contrato
     por escrito en soporte duradero es obligatoria (art. 98.7
     TRLGDCU). Lleva lo comprado, lo pagado, a dónde va, el derecho
     de desistimiento y la garantía.

   Se manda UNA sola vez por pedido: quien llama a esto ya se ha
   asegurado de que el pedido acaba de cambiar de estado.
   ============================================================ */
const esc = (v: unknown) =>
  String(v ?? '—').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const eur = (n: unknown) =>
  Number(n).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

async function avisar(
  pedido: any,
  leer: (ruta: string) => Promise<any>,
  esKlarna: boolean,
) {
  const RESEND = Deno.env.get('RESEND_API_KEY');
  const OSCAR = Deno.env.get('INTERESADOS_EMAIL');
  const WEB = Deno.env.get('LAORA_WEB_URL') ?? 'https://laora.es';
  if (!RESEND || !OSCAR) { console.error('sin RESEND_API_KEY o INTERESADOS_EMAIL'); return; }

  const lineas = await leer(`pedido_lineas?select=*&pedido_id=eq.${pedido.id}`);
  const socio = (await leer(`socios?select=email&id=eq.${pedido.socio_id}&limit=1`))[0];

  const enviar = (to: string, subject: string, html: string, replyTo?: string) =>
    fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${RESEND}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'laOra <laora@saneas.es>',
        to: [to], subject, html,
        ...(replyTo ? { reply_to: replyTo } : {}),
      }),
    });

  const relojes = (lineas || []).map((l: any) => `
    <tr><td style="border-top:1px solid #e7e9ee;padding:8px 0">
      <b>${esc(l.modelo)}</b>${l.cantidad > 1 ? ' × ' + l.cantidad : ''}<br>
      <span style="color:#6b7280;font-size:13px">${esc(l.acabado)}<br>${esc(l.correa)}<br>
      Ref. ${esc(l.ref)}</span></td>
    <td style="border-top:1px solid #e7e9ee;padding:8px 0;text-align:right;vertical-align:top">
      ${eur(Number(l.precio) * Number(l.cantidad))}</td></tr>`).join('');

  const envio = `${esc(pedido.env_nombre)}<br>${esc(pedido.env_direccion)}<br>
    ${esc(pedido.env_cp)} ${esc(pedido.env_poblacion)} (${esc(pedido.env_provincia)})<br>
    ${esc(pedido.env_pais)}${pedido.env_telefono ? '<br>Tel. ' + esc(pedido.env_telefono) : ''}`;

  /* ---------- 1. a Óscar ---------- */
  const aviso = esKlarna
    ? `<p style="background:#fdf0c9;padding:12px 14px;border-radius:8px">
         <b>Klarna: el dinero todavía NO está cobrado.</b> Está autorizado. Se cobra solo
         cuando marques el pedido como <b>enviado</b> en el panel, y hay 28 días de plazo
         desde hoy. Si se pasan, se pierde la autorización.</p>`
    : `<p style="background:#e8f5e9;padding:12px 14px;border-radius:8px">
         <b>Cobrado.</b> El dinero está en Mollie, camino de la cuenta.</p>`;

  await enviar(OSCAR,
    `laOra · pedido ${pedido.numero} · ${eur(pedido.total)} · ${esc(pedido.metodo)}`,
    `<div style="font-family:sans-serif;max-width:600px;color:#12161f">
      <h2 style="margin:0 0 4px">Pedido ${esc(pedido.numero)}</h2>
      <p style="color:#6b7280;margin:0 0 16px">${esc(socio?.email)} · ${esc(pedido.metodo)}</p>
      ${aviso}
      <table style="width:100%;border-collapse:collapse;font-size:14px">${relojes}
        <tr><td style="border-top:2px solid #12161f;padding:10px 0"><b>Total</b></td>
            <td style="border-top:2px solid #12161f;padding:10px 0;text-align:right"><b>${eur(pedido.total)}</b></td></tr>
      </table>
      <h3 style="margin:22px 0 6px;font-size:15px">A dónde va</h3>
      <p style="font-size:14px;line-height:1.6;margin:0">${envio}</p>
      ${pedido.fac_nif ? `<h3 style="margin:22px 0 6px;font-size:15px">Factura a</h3>
        <p style="font-size:14px;line-height:1.6;margin:0">${esc(pedido.fac_nombre)} · ${esc(pedido.fac_nif)}<br>
        ${esc(pedido.fac_direccion)}, ${esc(pedido.fac_cp)} ${esc(pedido.fac_poblacion)}</p>` : ''}
      <p style="margin-top:24px"><a href="${WEB}/panel" style="color:#C9A227">Abrir el panel</a></p>
    </div>`, socio?.email);

  /* ---------- 2. al cliente ---------- */
  if (!socio?.email) return;

  const cuandoCobra = esKlarna
    ? `<p style="font-size:14px;line-height:1.65">Has elegido pagar en tres plazos con Klarna.
       <b>El primer plazo no se te cobra hasta que tu reloj salga hacia tu casa</b>; Klarna te
       avisará. Hasta entonces no se te carga nada.</p>`
    : '';

  await enviar(socio.email,
    `Tu pedido ${pedido.numero} está confirmado · laOra`,
    `<div style="font-family:sans-serif;max-width:560px;margin:0 auto;color:#12161f">
      <p style="font-size:13px;color:#8a92a1;letter-spacing:.1em;text-transform:uppercase">
        laOra · pedido ${esc(pedido.numero)}</p>
      <h1 style="font-size:26px;letter-spacing:-1px;margin:0 0 10px">Gracias. Tu pedido está confirmado.</h1>
      <p style="font-size:16px;line-height:1.6;color:#454b57">Lo hemos recibido y ya está en marcha.
        Te escribimos otra vez cuando salga hacia tu casa, con su seguimiento. Ni antes, ni sin avisar.</p>
      ${cuandoCobra}
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:18px">${relojes}
        <tr><td style="border-top:2px solid #12161f;padding:10px 0"><b>Total pagado</b></td>
            <td style="border-top:2px solid #12161f;padding:10px 0;text-align:right"><b>${eur(pedido.total)}</b></td></tr>
      </table>
      <p style="font-size:13px;color:#8a92a1;margin-top:6px">IVA y envío incluidos.</p>
      <h3 style="margin:22px 0 6px;font-size:15px">Te lo enviamos a</h3>
      <p style="font-size:14px;line-height:1.6;margin:0">${envio}</p>
      <p style="font-size:14px;line-height:1.65;margin-top:22px">Tienes <b>14 días naturales</b>
        desde que lo recibas para devolverlo sin dar explicaciones. Nos lo dices respondiendo a
        este correo y te devolvemos el dinero entero, por el mismo medio con el que pagaste.
        No hay formularios ni preguntas.</p>
      <p style="font-size:14px;line-height:1.65">Tu reloj lleva <b>3 años de garantía</b>, con
        servicio técnico propio en España.</p>
      <p style="font-size:13px;color:#8a92a1;line-height:1.6">Puedes ver tu pedido en
        <a href="${WEB}/cuenta" style="color:#C9A227">tu cuenta</a>. Guarda este correo: es tu
        justificante de compra.</p>
    </div>`, OSCAR);
}

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

    const cabeceras = {
      apikey: SERVICE,
      Authorization: `Bearer ${SERVICE}`,
      'Content-Type': 'application/json',
      'Content-Profile': 'laora',
      'Accept-Profile': 'laora',
    };

    const db = (ruta: string, cambios: unknown, devolver = false) =>
      fetch(`${SB}/rest/v1/${ruta}`, {
        method: 'PATCH',
        headers: { ...cabeceras, Prefer: devolver ? 'return=representation' : 'return=minimal' },
        body: JSON.stringify(cambios),
      });

    const leer = (ruta: string) =>
      fetch(`${SB}/rest/v1/${ruta}`, { headers: cabeceras }).then((r) => r.json());

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

      /* MOLLIE LLAMA VARIAS VECES. Para no avisar dos veces del mismo
         pago, el cambio solo se aplica si el pedido NO estaba ya en ese
         estado: si la respuesta viene vacía es que ya estaba hecho, y
         entonces aquí no ha pasado nada nuevo. */
      const filtro = cambios.estado
        ? `pedidos?id=eq.${encodeURIComponent(pedidoId)}&estado=neq.${cambios.estado}`
        : `pedidos?id=eq.${encodeURIComponent(pedidoId)}`;

      const up = await db(filtro, cambios, true);
      if (!up.ok) {
        console.error('pedido:', await up.text());
        return new Response('no se pudo actualizar', { status: 502 });
      }
      const tocado = (await up.json())[0];

      if (tocado && (cambios.estado === 'pagado' || cambios.estado === 'autorizado')) {
        // Que falle un correo no puede hacer que Mollie reintente el
        // webhook: el pedido ya está bien anotado, que es lo que importa.
        try { await avisar(tocado, leer, cambios.estado === 'autorizado'); }
        catch (e) { console.error('aviso:', e); }
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
