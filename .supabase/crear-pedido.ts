// ============================================================
// laOra · Edge Function: crear-pedido
// ------------------------------------------------------------
// Convierte una cesta en un PEDIDO de verdad, antes de cobrar.
//
// POR QUÉ EXISTE
//   Hasta hoy la cesta abría PayPal y ahí se acababa todo: llegaba un
//   ingreso suelto, sin saber qué se había comprado ni a dónde había
//   que enviarlo. Ahora primero se escribe el pedido —con su número,
//   sus líneas y la dirección— y solo después se cobra.
//
// LA REGLA DEL DINERO
//   El precio NUNCA es el que dice el navegador. Se lee de
//   `catalogo-2026.json`, que NO se escribe a mano: lo vuelca
//   `herramientas/volcar_catalogo_2026.js` ejecutando el motor de
//   precios que hay dentro de cada ficha, el mismo que ve el cliente.
//   Quien manipule la cesta en su navegador no se lleva un reloj por un
//   euro: si la referencia no está en esa lista, no se vende.
//
//   OJO: si se toca un configurador y no se vuelve a pasar el volcador,
//   la web enseñará el precio nuevo y esto rechazará la referencia.
//
// QUIÉN PUEDE LLAMARLA
//   Solo alguien que haya entrado. La app manda su `access_token` en la
//   cabecera `Authorization`, y aquí se comprueba contra Supabase antes
//   de escribir nada. El socio del pedido es SIEMPRE el del token, no
//   uno que venga en el cuerpo: así nadie puede hacer un pedido a
//   nombre de otro.
//
// DESPLIEGUE
//   supabase functions deploy crear-pedido \
//     --project-ref uikanfvigunjhzibnhxf --no-verify-jwt
//   (JWT desactivado a propósito: el token lo comprobamos nosotros, y
//   así el error que ve el cliente es nuestro y en español.)
//   Secretos: los tres que Supabase pone solos —SUPABASE_URL,
//   SUPABASE_ANON_KEY y SUPABASE_SERVICE_ROLE_KEY—. No hace falta ninguno más.
// ============================================================

const CATALOGO = 'https://laora.es/assets/datos/catalogo-2026.json';

/* Los gastos de envío. Hoy van incluidos en el precio; el día que
   dejen de estarlo, se cambia aquí y en la pantalla del carrito. */
const ENVIO = 0;

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

/* ---------- el catálogo ----------
   Se pide una vez y se guarda mientras la función siga viva. Si laOra
   cambia un precio, tarda como mucho un rato en verse aquí. */
let catalogoCache: { cuando: number; datos: any } | null = null;

async function catalogo() {
  const ahora = Date.now();
  if (catalogoCache && (ahora - catalogoCache.cuando) < 300_000) return catalogoCache.datos;
  const r = await fetch(CATALOGO, { cache: 'no-store' });
  if (!r.ok) throw new Error('no se pudo leer el catálogo');
  const datos = await r.json();
  catalogoCache = { cuando: ahora, datos };
  return datos;
}

/* Lo que se vende hoy, por referencia. Las cadenas vienen
   deduplicadas —hay dos mil referencias y muchas comparten texto—, así
   que aquí se resuelven los índices. */
type Combinacion = {
  precio: number; modelo: string; acabado: string; correa: string;
  ficha: Record<string, string>;
};

async function combinacion(ref: string): Promise<Combinacion | null> {
  const cat = await catalogo();
  const r = cat.refs?.[ref];
  if (!r) return null;
  const T: string[] = cat.textos || [];
  const ficha: Record<string, string> = {};
  for (const k of Object.keys(r.f || {})) ficha[k] = T[r.f[k]] ?? '';
  return {
    precio: Number(r.p),
    /* Se congela lo que vio el cliente: si mañana cambia el catálogo,
       el pedido sigue diciendo exactamente qué se vendió. */
    modelo: T[r.n] ?? '', acabado: T[r.a] ?? '', correa: T[r.c] ?? '', ficha,
  };
}

/* ---------- quién llama ----------
   Se le pregunta a Supabase por el token. Si contesta con un usuario,
   es válido; no hace falta verificar firmas a mano. */
async function quienEs(token: string, url: string, anon: string) {
  const r = await fetch(`${url}/auth/v1/user`, {
    headers: { Authorization: `Bearer ${token}`, apikey: anon },
  });
  if (!r.ok) return null;
  const u = await r.json();
  return u?.id ? { id: u.id as string, email: (u.email as string) || '' } : null;
}

/* Los que la web ofrece hoy. El definitivo lo dirá Mollie cuando
   avise del pago: aquí solo se anota con qué se pensaba pagar. */
const METODOS = new Set(['tarjeta', 'klarna', 'bizum', 'paypal', 'transferencia']);

const limpio = (v: unknown, max = 120) => String(v ?? '').trim().slice(0, max);

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'solo POST' }, 405);

  const URL_SB = Deno.env.get('SUPABASE_URL');
  const ANON = Deno.env.get('SUPABASE_ANON_KEY');
  /* En este proyecto `SUPABASE_SERVICE_ROLE_KEY` existe pero la API
     REST la rechaza —está en el sistema nuevo de claves—, así que la
     buena se guarda en el secreto `LAORA_SERVICIO`. */
  const SERVICIO = Deno.env.get('LAORA_SERVICIO') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!URL_SB || !ANON || !SERVICIO) return json({ error: 'configuración incompleta' }, 500);

  const cabecera = req.headers.get('Authorization') || '';
  const token = cabecera.replace(/^Bearer\s+/i, '').trim();
  if (!token) return json({ error: 'Hay que entrar antes de hacer el pedido.' }, 401);

  const socio = await quienEs(token, URL_SB, ANON);
  if (!socio) return json({ error: 'Tu sesión ha caducado. Vuelve a entrar.' }, 401);

  let cuerpo: any;
  try { cuerpo = await req.json(); } catch { return json({ error: 'petición ilegible' }, 400); }

  const lineas = Array.isArray(cuerpo?.lineas) ? cuerpo.lineas : [];
  if (!lineas.length) return json({ error: 'La cesta está vacía.' }, 400);
  if (lineas.length > 20) return json({ error: 'Demasiadas líneas en un pedido.' }, 400);

  const e = cuerpo?.envio || {};
  const faltan = ['nombre', 'direccion', 'cp', 'poblacion', 'provincia']
    .filter((k) => !limpio(e[k]));
  if (faltan.length) return json({ error: 'Faltan datos del envío: ' + faltan.join(', ') }, 400);

  /* ---------- el precio, desde el catálogo ---------- */
  try { await catalogo(); }
  catch { return json({ error: 'No hemos podido comprobar los precios. Inténtalo en un momento.' }, 503); }

  const preparadas: any[] = [];
  let importe = 0;

  for (const l of lineas) {
    const ref = limpio(l?.ref, 80);
    const c = await combinacion(ref);
    if (!c) return json({ error: `La referencia ${ref || '(vacía)'} ya no está a la venta.` }, 409);

    const cantidad = Math.max(1, Math.min(5, parseInt(l?.cantidad, 10) || 1));
    importe += c.precio * cantidad;
    preparadas.push({
      ref, modelo: c.modelo, acabado: c.acabado, correa: c.correa,
      precio: c.precio, cantidad, ficha: c.ficha,
    });
  }

  importe = Math.round(importe * 100) / 100;
  const total = Math.round((importe + ENVIO) * 100) / 100;

  /* ---------- se escribe ---------- */
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

  // El socio, por si es su primera compra.
  await rest('socios?on_conflict=id', {
    method: 'POST',
    headers: { Prefer: 'resolution=ignore-duplicates' },
    body: JSON.stringify({ id: socio.id, email: socio.email }),
  });

  // Sus datos, al día con lo que acaba de escribir.
  await rest(`socios?id=eq.${socio.id}`, {
    method: 'PATCH',
    body: JSON.stringify({
      nombre: limpio(e.nombre), apellidos: limpio(e.apellidos),
      telefono: limpio(e.telefono, 40), nif: limpio(e.nif, 20) || null,
      direccion: limpio(e.direccion, 200), cp: limpio(e.cp, 10),
      poblacion: limpio(e.poblacion), provincia: limpio(e.provincia),
      pais: limpio(e.pais) || 'España',
    }),
  });

  // El número, con el candado que evita dos iguales a la vez.
  const rNum = await fetch(`${URL_SB}/rest/v1/rpc/siguiente_numero_pedido`, {
    method: 'POST',
    headers: {
      apikey: SERVICIO, Authorization: `Bearer ${SERVICIO}`,
      'Content-Type': 'application/json', 'Content-Profile': 'laora',
    },
    body: '{}',
  });
  if (!rNum.ok) return json({ error: 'No hemos podido numerar el pedido.' }, 500);
  const numero = (await rNum.json()) as string;

  const f = cuerpo?.factura || {};
  const rPed = await rest('pedidos', {
    method: 'POST',
    body: JSON.stringify({
      numero, socio_id: socio.id,
      importe, envio: ENVIO, total,
      metodo: METODOS.has(String(cuerpo?.metodo)) ? String(cuerpo.metodo) : 'tarjeta',
      estado: 'solicitado',
      env_nombre: [limpio(e.nombre), limpio(e.apellidos)].filter(Boolean).join(' '),
      env_telefono: limpio(e.telefono, 40),
      env_direccion: limpio(e.direccion, 200),
      env_cp: limpio(e.cp, 10),
      env_poblacion: limpio(e.poblacion),
      env_provincia: limpio(e.provincia),
      env_pais: limpio(e.pais) || 'España',
      fac_nombre: limpio(f.nombre) || null,
      fac_nif: limpio(f.nif, 20) || null,
      fac_direccion: limpio(f.direccion, 200) || null,
      fac_cp: limpio(f.cp, 10) || null,
      fac_poblacion: limpio(f.poblacion) || null,
      fac_provincia: limpio(f.provincia) || null,
    }),
  });

  if (!rPed.ok) {
    console.error('pedido', rPed.status, await rPed.text());
    return json({ error: 'No hemos podido guardar el pedido.' }, 500);
  }
  const pedido = (await rPed.json())[0];

  const rLin = await rest('pedido_lineas', {
    method: 'POST',
    body: JSON.stringify(preparadas.map((p) => ({ ...p, pedido_id: pedido.id }))),
  });

  if (!rLin.ok) {
    // Sin líneas, el pedido no vale para nada: mejor no dejarlo suelto.
    console.error('lineas', rLin.status, await rLin.text());
    await rest(`pedidos?id=eq.${pedido.id}`, { method: 'DELETE' });
    return json({ error: 'No hemos podido guardar lo que has elegido.' }, 500);
  }

  return json({ ok: true, numero, total, importe, envio: ENVIO, pedido_id: pedido.id });
});
