// ============================================================
// laOra · Edge Function: crear-reserva
// ------------------------------------------------------------
// Crea la reserva y, si el pago es por pasarela, la cobra con Mollie.
//
// REGLA DE ORO: el importe NO se acepta del navegador. Se lee de
// `precios.js` de la propia web (la única fuente de verdad) y se
// recalcula aquí. Lo que mande el cliente en `precio_total` solo se
// usa para comprobar que la página que vio coincide con lo que hay
// ahora; si no cuadra, se rechaza y no se cobra nada.
//
// Desplegar con «Enforce JWT verification» DESACTIVADO: la llama la
// web pública. El apikey anon viaja igual, pero no da acceso a nada:
// la tabla `reservas` es deny-all para anon.
//
// Secretos necesarios:
//   MOLLIE_API_KEY          live_… o test_…
//   SUPABASE_URL            (lo pone Supabase solo)
//   SUPABASE_SERVICE_ROLE_KEY (lo pone Supabase solo)
//   WEB_URL                 https://laora.es
// ============================================================

const WEB = Deno.env.get('WEB_URL') ?? 'https://laora.es';
const SENAL_PORCENTAJE = 25;

// ---------- precios: se leen de la web, no se duplican aquí ----------
let cachePrecios: { en: number; datos: Record<string, Record<string, number | null>> } | null = null;

async function precios() {
  if (cachePrecios && Date.now() - cachePrecios.en < 60_000) return cachePrecios.datos;

  const r = await fetch(`${WEB}/assets/js/precios.js`, { cache: 'no-store' });
  if (!r.ok) throw new Error('no se pudo leer la tabla de precios');
  const texto = await r.text();

  // Se extraen SOLO números con expresión regular. Nunca se ejecuta el fichero.
  const datos: Record<string, Record<string, number | null>> = {};
  const bloques = texto.split(/'(LO-\d\d)':/).slice(1);
  for (let i = 0; i < bloques.length; i += 2) {
    const ref = bloques[i];
    const cuerpo = bloques[i + 1];
    const acabados: Record<string, number | null> = {};
    for (const m of cuerpo.matchAll(/(\w+):\s*\{\s*precio:\s*(null|\d+(?:\.\d+)?)/g)) {
      acabados[m[1]] = m[2] === 'null' ? null : Number(m[2]);
    }
    datos[ref] = acabados;
  }

  cachePrecios = { en: Date.now(), datos };
  return datos;
}

async function entregaPrometida() {
  const r = await fetch(`${WEB}/assets/js/precios.js`, { cache: 'no-store' });
  const t = await r.text();
  const m = t.match(/var LAORA_ENTREGA\s*=\s*'([^']*)'/);
  return m ? m[1].trim() : '';
}

const dosDecimales = (n: number) => Math.round(n * 100) / 100;

function codigo() {
  const abc = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // sin I, O, 0, 1: se dictan por teléfono
  let s = '';
  const bytes = crypto.getRandomValues(new Uint8Array(6));
  for (const b of bytes) s += abc[b % abc.length];
  return `LAORA-${s}`;
}

const CORS = {
  'Access-Control-Allow-Origin': WEB,
  'Access-Control-Allow-Headers': 'content-type, apikey, authorization',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const json = (cuerpo: unknown, status = 200) =>
  new Response(JSON.stringify(cuerpo), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
  if (req.method !== 'POST') return json({ error: 'método no permitido' }, 405);

  try {
    const b = await req.json();

    // ---------- validación de los datos del cliente ----------
    const obligatorios = ['ref', 'acabado', 'metodo', 'nombre', 'email',
                          'telefono', 'direccion', 'cp', 'poblacion', 'provincia'];
    for (const c of obligatorios) {
      if (!b[c] || String(b[c]).trim() === '') return json({ error: `falta ${c}` }, 400);
    }
    if (!['mollie', 'bizum', 'transferencia'].includes(b.metodo)) {
      return json({ error: 'método de pago no válido' }, 400);
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(b.email))) {
      return json({ error: 'correo no válido' }, 400);
    }
    const recorta = (v: unknown, max: number) => String(v ?? '').trim().slice(0, max);

    // ---------- el precio manda el servidor ----------
    const tabla = await precios();
    const precio = tabla[b.ref]?.[b.acabado];
    if (!precio) return json({ error: 'ese acabado no está a la venta' }, 409);

    const entrega = await entregaPrometida();
    if (!entrega) return json({ error: 'no hay fecha de entrega comprometida' }, 409);

    // Si lo que vio el cliente no es lo que hay ahora, se para. No se cobra de más
    // ni de menos sin que la persona lo sepa.
    if (b.precio_total != null && dosDecimales(Number(b.precio_total)) !== dosDecimales(precio)) {
      return json({ error: 'el precio ha cambiado, recarga la página' }, 409);
    }

    const senal = dosDecimales((precio * SENAL_PORCENTAJE) / 100);
    const resto = dosDecimales(precio - senal);

    // ---------- se guarda ----------
    const SB = Deno.env.get('SUPABASE_URL');
    const SERVICE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!SB || !SERVICE) return json({ error: 'configuración incompleta' }, 500);

    const reserva = {
      codigo: codigo(),
      ref: b.ref,
      modelo: recorta(b.modelo, 60),
      acabado: b.acabado,
      precio_total: precio,
      senal,
      resto,
      entrega_prometida: entrega,
      nombre: recorta(b.nombre, 120),
      email: recorta(b.email, 160),
      telefono: recorta(b.telefono, 40),
      direccion: recorta(b.direccion, 200),
      cp: recorta(b.cp, 10),
      poblacion: recorta(b.poblacion, 80),
      provincia: recorta(b.provincia, 80),
      metodo: b.metodo,
      estado: 'pendiente',
    };

    const guardar = await fetch(`${SB}/rest/v1/reservas`, {
      method: 'POST',
      headers: {
        apikey: SERVICE,
        Authorization: `Bearer ${SERVICE}`,
        'Content-Type': 'application/json',
        Prefer: 'return=representation',
      },
      body: JSON.stringify(reserva),
    });
    if (!guardar.ok) {
      console.error('supabase:', await guardar.text());
      return json({ error: 'no se pudo guardar la reserva' }, 502);
    }
    const [fila] = await guardar.json();

    // ---------- pagos manuales: no se cobra aquí ----------
    if (b.metodo !== 'mollie') {
      const url = `${WEB}/reserva-recibida.html?estado=pendiente&metodo=${b.metodo}` +
                  `&codigo=${encodeURIComponent(fila.codigo)}` +
                  `&importe=${encodeURIComponent(senal.toFixed(2))}`;
      return json({ url, codigo: fila.codigo });
    }

    // ---------- Mollie ----------
    const MOLLIE = Deno.env.get('MOLLIE_API_KEY');
    if (!MOLLIE) return json({ error: 'pasarela no configurada' }, 500);

    const pago = await fetch('https://api.mollie.com/v2/payments', {
      method: 'POST',
      headers: { Authorization: `Bearer ${MOLLIE}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: { currency: 'EUR', value: senal.toFixed(2) },
        description: `laOra ${fila.ref} «${fila.modelo}» ${fila.acabado} · señal ${SENAL_PORCENTAJE}%`,
        redirectUrl: `${WEB}/reserva-recibida.html?estado=pagada&codigo=${encodeURIComponent(fila.codigo)}`,
        cancelUrl: `${WEB}/reservar.html?ref=${fila.ref}&acabado=${encodeURIComponent(fila.acabado)}`,
        webhookUrl: `${SB}/functions/v1/mollie-webhook`,
        metadata: { reserva_id: fila.id, codigo: fila.codigo },
      }),
    });

    if (!pago.ok) {
      console.error('mollie:', await pago.text());
      // La reserva queda anotada como pendiente: nadie ha pagado nada.
      return json({ error: 'la pasarela no respondió' }, 502);
    }
    const p = await pago.json();

    await fetch(`${SB}/rest/v1/reservas?id=eq.${fila.id}`, {
      method: 'PATCH',
      headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ mollie_id: p.id }),
    });

    return json({ url: p._links.checkout.href, codigo: fila.codigo });
  } catch (e) {
    console.error(e);
    return json({ error: 'error inesperado' }, 500);
  }
});
