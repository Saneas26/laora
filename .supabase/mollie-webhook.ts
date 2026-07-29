// ============================================================
// laOra · Edge Function: mollie-webhook
// ------------------------------------------------------------
// Mollie avisa aquí cada vez que cambia el estado de un pago.
// Nunca se fía del cuerpo que llega: Mollie solo manda el id, y
// somos nosotros los que preguntamos a Mollie qué ha pasado con
// nuestra propia clave. Así nadie puede marcar una reserva como
// pagada mandándonos un POST.
//
// Desplegar con «Enforce JWT verification» DESACTIVADO.
// Secretos: LAORA_MOLLIE_API_KEY (SUPABASE_URL y la clave secreta las pone Supabase)
// La service_role ha cambiado de nombre: antes SUPABASE_SERVICE_ROLE_KEY,
// ahora SUPABASE_SECRET_KEYS (un JSON con varias). Se aceptan las dos para
// que esto no se rompa el día que Supabase retire la vieja.
function claveSecreta(): string | null {
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

    const estados: Record<string, string> = {
      paid: 'pagada',
      canceled: 'cancelada',
      expired: 'cancelada',
      failed: 'cancelada',
    };
    const estado = estados[pago.status];
    if (!estado) return new Response('ok'); // open, pending… todavía no hay nada que hacer

    const cambios: Record<string, unknown> = { estado };
    if (estado === 'pagada') cambios.pagada_en = new Date().toISOString();

    // Se localiza por el id de Mollie, no por lo que venga de fuera.
    const up = await fetch(`${SB}/rest/v1/reservas?mollie_id=eq.${encodeURIComponent(id)}`, {
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
