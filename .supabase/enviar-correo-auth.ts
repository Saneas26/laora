// ============================================================
// Grupo Saneas · Edge Function: enviar-correo-auth
// ------------------------------------------------------------
// SUSTITUYE al correo que manda Supabase por uno nuestro.
//
// POR QUÉ EXISTE
//   El proyecto de Supabase es UNO y lo comparten laOra y Activala.
//   Las plantillas y el remitente de Supabase son del PROYECTO, así
//   que sin esto los dos negocios mandan el mismo correo, en inglés
//   y firmado «Supabase Auth».
//
//   Con el «Send Email Hook» el correo lo mandamos nosotros, y aquí
//   sí se puede mirar de DÓNDE viene la petición y firmar cada una
//   con su marca:
//
//       laora.es     →  laOra · Grupo Saneas <laora@saneas.es>
//       activala.es  →  Activala · Grupo Saneas <activala@saneas.es>
//
//   La marca se decide por el `redirect_to`, que es la dirección a la
//   que vuelve el cliente: la manda la propia web al pedir el enlace.
//   No hace falta que la app envíe ningún identificador extra.
//
// DESPLIEGUE
//   1. supabase functions deploy enviar-correo-auth --no-verify-jwt
//      (JWT DESACTIVADO: quien llama es el propio Auth, no un usuario)
//   2. Authentication → Hooks → «Send Email» → HTTPS →
//      https://<proyecto>.supabase.co/functions/v1/enviar-correo-auth
//      Supabase genera ahí el secreto: se copia tal cual.
//   3. Secretos de la función:
//        RESEND_API_KEY            (ya existe, lo comparte con las demás)
//        SEND_EMAIL_HOOK_SECRET    (el del paso 2, formato v1,whsec_…)
//      SUPABASE_URL lo pone Supabase solo.
//
// SI ALGO FALLA
//   Este correo es el ÚNICO camino de entrada de los dos negocios. Si
//   la función devuelve error, nadie entra. Por eso aquí no se aborta
//   casi nunca: marca desconocida → se firma como Grupo Saneas; tipo
//   de correo desconocido → se manda igual con un texto genérico. Y
//   el interruptor del paso 2 se apaga en un clic: al apagarlo vuelve
//   el correo de Supabase, feo pero funcionando.
// ============================================================

/* ---------- las marcas de la casa ----------
   La lista es la misma de `24-grupo-saneas.js`, el componente que ya
   llevan las webs y las apps. Si allí se añade una, se añade aquí. */
const MARCAS = [
  { id: 'saneas', nombre: 'Saneas', url: 'https://saneas.es', que: 'nutrición que cambia hábitos' },
  { id: 'saneas-app', nombre: 'App Saneas', url: 'https://saneas.es/instala-app', que: 'tu método, en el móvil' },
  { id: 'activala', nombre: 'Activala', url: 'https://activala.es', que: 'casas en el sur de Gran Canaria' },
  { id: 'laora', nombre: 'laOra', url: 'https://laora.es', que: 'relojería honesta' },
  { id: 'acumula', nombre: 'Acumula', url: 'https://acumula.es', que: 'la economía de casa, clara' },
  { id: 'pordondevoy', nombre: 'Pordondevoy', url: 'https://pordondevoy-saneas.vercel.app', que: 'para el avión, sin conexión' },
  { id: 'asesorias', nombre: 'Asesora Saneas', url: 'https://saneas.es/asesorias', que: 'dedícate tú a la nutrición' },
];

/* ---------- quién firma cada correo ----------
   `dominios` son los del `redirect_to`. `tinta` es el color del texto
   y del botón; se eligen oscuros a propósito: este correo lo tiene que
   leer alguien de sesenta años en el móvil, al sol. */
type Marca = {
  id: string; nombre: string; remitente: string; web: string;
  tinta: string; papel: string; acento: string; dominios: string[];
  logo?: string; logoAncho?: number; logoAlto?: number;
};

const MARCAS_CORREO: Marca[] = [
  {
    id: 'laora', nombre: 'laOra',
    remitente: 'laOra · Grupo Saneas <laora@saneas.es>',
    web: 'https://laora.es',
    // El oro de la casa es #D4A94B, pero sobre blanco no llega a 4,5:1
    // y aquí hay texto pequeño. Este es el mismo oro, apagado hasta que
    // se lee: 5,3:1. El de arriba se queda para las pantallas grandes.
    tinta: '#090909', papel: '#F7F7F5', acento: '#8a6428',
    dominios: ['laora.es'],
    // El logotipo de la casa, el de verdad: la O es la esfera con el
    // triángulo del mediodía. Va como imagen porque en un correo no se
    // puede componer, y con `alt` para cuando el lector no baje las
    // imágenes: entonces se lee «laOra», que es lo importante.
    logo: 'https://laora.es/assets/img/lunar-v2/laora-wordmark-dark.png',
    logoAncho: 132, logoAlto: 43,
  },
  {
    id: 'activala', nombre: 'Activala',
    remitente: 'Activala · Grupo Saneas <activala@saneas.es>',
    web: 'https://activala.es',
    tinta: '#082c48', papel: '#f4f6f8', acento: '#3d7a1f',
    dominios: ['activala.es'],
  },
];

const GENERICA: Marca = {
  id: 'saneas', nombre: 'Grupo Saneas',
  remitente: 'Grupo Saneas <laora@saneas.es>',
  web: 'https://saneas.es',
  tinta: '#0f2f38', papel: '#f4f6f8', acento: '#1d6d7d',
  dominios: [],
};

function marcaDe(destino: string): Marca {
  let host = '';
  try { host = new URL(destino).hostname.replace(/^www\./, ''); } catch { /* vacío o roto */ }
  if (!host) return GENERICA;
  for (const m of MARCAS_CORREO) {
    for (const d of m.dominios) if (host === d || host.endsWith('.' + d)) return m;
  }
  return GENERICA;
}

/* ---------- firma del aviso (Standard Webhooks) ----------
   Sin esto, cualquiera que dé con la dirección de la función podría
   mandar correos en nuestro nombre. Se comprueba a mano con la
   criptografía del propio Deno para no depender de ningún paquete. */
const deB64 = (s: string) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
const aB64 = (b: Uint8Array) => btoa(String.fromCharCode(...b));

function iguales(a: string, b: string) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

async function firmaValida(cuerpo: string, cab: Headers, secreto: string) {
  const id = cab.get('webhook-id');
  const sello = cab.get('webhook-timestamp');
  const firmas = cab.get('webhook-signature');
  if (!id || !sello || !firmas) return false;

  // Un aviso de hace media hora es un aviso repetido por alguien.
  const ahora = Math.floor(Date.now() / 1000);
  if (Math.abs(ahora - Number(sello)) > 300) return false;

  const clave = await crypto.subtle.importKey(
    'raw', deB64(secreto.replace(/^v1,whsec_/, '')),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  );
  const mia = aB64(new Uint8Array(await crypto.subtle.sign(
    'HMAC', clave, new TextEncoder().encode(`${id}.${sello}.${cuerpo}`),
  )));

  for (const trozo of firmas.split(' ')) {
    const [version, valor] = trozo.split(',');
    if (version === 'v1' && valor && iguales(valor, mia)) return true;
  }
  return false;
}

/* ---------- el correo ---------- */
const esc = (s: unknown) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

type Texto = { asunto: string; titulo: string; entrada: string; boton: string; aviso: string };

function textoDe(tipo: string, marca: Marca): Texto {
  const n = marca.nombre;
  switch (tipo) {
    case 'signup':
      return {
        asunto: `Confirma tu correo en ${n}`,
        titulo: 'Confirma tu correo',
        entrada: `Solo queda un paso para tener tu cuenta en ${n}. Pulsa el botón y confirmas que esta dirección es tuya.`,
        boton: 'Confirmar mi correo',
        aviso: 'El enlace caduca en una hora y sirve una sola vez.',
      };
    case 'recovery':
      return {
        asunto: `Cambiar tu contraseña en ${n}`,
        titulo: 'Cambiar la contraseña',
        entrada: 'Has pedido cambiar la contraseña. Pulsa el botón y eliges una nueva.',
        boton: 'Elegir contraseña nueva',
        aviso: 'El enlace caduca en una hora y sirve una sola vez. Hasta que no lo uses, tu contraseña de siempre sigue valiendo.',
      };
    case 'invite':
      return {
        asunto: `Te esperamos en ${n}`,
        titulo: 'Tu invitación',
        entrada: `Te han abierto una cuenta en ${n}. Pulsa el botón y la activas con esta misma dirección.`,
        boton: 'Activar mi cuenta',
        aviso: 'El enlace caduca en una hora y sirve una sola vez.',
      };
    case 'email_change':
    case 'email_change_new':
      return {
        asunto: `Confirma tu nueva dirección en ${n}`,
        titulo: 'Tu nueva dirección',
        entrada: 'Has pedido cambiar el correo de tu cuenta. Pulsa el botón y la nueva dirección queda confirmada.',
        boton: 'Confirmar esta dirección',
        aviso: 'El enlace caduca en una hora. Mientras no lo pulses, tu cuenta sigue con el correo anterior.',
      };
    default: // magiclink y cualquier otro que aparezca
      return {
        asunto: `Tu enlace para entrar en ${n}`,
        titulo: 'Ya puedes entrar',
        entrada: 'Pulsa el botón y estás dentro de tu cuenta. No hay contraseña que recordar: este enlace es la llave.',
        boton: `Entrar en ${n}`,
        aviso: 'El enlace caduca en una hora y sirve una sola vez.',
      };
  }
}

/* La parrilla del Grupo, en texto: los iconos son imágenes y casi
   todos los correos las bloquean hasta que el lector las pide. La
   marca que manda el correo no se repite: ya sabe dónde está. */
function pieGrupo(marca: Marca) {
  const S = '-apple-system,Segoe UI,Helvetica,Arial,sans-serif';

  /* Una por línea, no todas seguidas separadas por puntos: en un pie a
     13 px, seis casas en corrido no se leen, se saltan. */
  const filas = MARCAS
    .filter((m) => m.id !== marca.id && !(marca.id === 'saneas' && m.id === 'saneas-app'))
    .map((m) => `<tr><td style="padding:4px 0">` +
                `<a href="${m.url}" style="text-decoration:none;font:400 14px/1.4 ${S}">` +
                `<b style="color:#2b2b2b">${esc(m.nombre)}</b>` +
                `<span style="color:#5f5f5f"> · ${esc(m.que)}</span></a></td></tr>`)
    .join('\n      ');

  return `
    <p style="margin:0 0 10px;font:700 14px/1.5 ${S};color:#2b2b2b">
      ${esc(marca.nombre)} pertenece al Grupo Saneas, que también lo conforman:</p>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0">
      ${filas}
    </table>`;
}

function montarHtml(marca: Marca, t: Texto, enlace: string, codigo: string) {
  const S = '-apple-system,Segoe UI,Helvetica,Arial,sans-serif';
  return `<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(t.asunto)}</title></head>
<body style="margin:0;padding:0;background:${marca.papel}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${marca.papel}">
<tr><td align="center" style="padding:32px 16px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:14px;border:1px solid #e6e4df">
    <tr><td style="padding:34px 30px 8px">
      ${marca.logo
        ? `<img src="${marca.logo}" width="${marca.logoAncho}" height="${marca.logoAlto}" alt="${esc(marca.nombre)}"
             style="display:block;border:0;outline:none;text-decoration:none;width:${marca.logoAncho}px;height:${marca.logoAlto}px;font:700 20px/1.2 Georgia,serif;color:${marca.tinta}">`
        : `<p style="margin:0;font:700 20px/1.2 Georgia,'Times New Roman',serif;letter-spacing:.02em;color:${marca.tinta}">${esc(marca.nombre)}</p>`}
      <div style="height:3px;width:44px;margin:12px 0 0;background:${marca.acento}"></div>
    </td></tr>

    <tr><td style="padding:22px 30px 0">
      <h1 style="margin:0 0 14px;font:700 25px/1.25 ${S};color:${marca.tinta}">${esc(t.titulo)}</h1>
      <p style="margin:0;font:400 17px/1.6 ${S};color:#33312e">${esc(t.entrada)}</p>
    </td></tr>

    ${enlace ? `
    <tr><td style="padding:26px 30px 0" align="center">
      <a href="${esc(enlace)}" style="display:inline-block;padding:16px 30px;border-radius:10px;background:${marca.tinta};color:#ffffff;font:700 17px/1 ${S};text-decoration:none">${esc(t.boton)}</a>
    </td></tr>
    <tr><td style="padding:20px 30px 0">
      <p style="margin:0 0 6px;font:400 14px/1.5 ${S};color:#6b6862">Si el botón no te funciona, copia esta dirección en el navegador:</p>
      <p style="margin:0;font:400 13px/1.5 ${S};color:${marca.acento};word-break:break-all">${esc(enlace)}</p>
    </td></tr>
    <!-- EL CÓDIGO, SIEMPRE (19/08/2026). El enlace vale una sola vez y
         solo entra en el navegador donde se abre: si el correo lo
         previsualiza, o si se lee en el móvil y se estaba comprando en
         el ordenador, no sirve. El código se escribe donde uno esté. -->
    <tr><td style="padding:22px 30px 0" align="center">
      <p style="margin:0 0 6px;font:400 14px/1.5 ${S};color:#6b6862">O escribe este código en la misma pantalla donde lo pediste:</p>
      <p style="margin:0;font:700 32px/1.2 ${S};letter-spacing:.22em;color:${marca.tinta}">${esc(codigo)}</p>
    </td></tr>` : `
    <tr><td style="padding:24px 30px 0" align="center">
      <p style="margin:0 0 8px;font:400 15px/1.5 ${S};color:#6b6862">Tu código:</p>
      <p style="margin:0;font:700 34px/1.2 ${S};letter-spacing:.22em;color:${marca.tinta}">${esc(codigo)}</p>
    </td></tr>`}

    <tr><td style="padding:22px 30px 30px">
      <p style="margin:0 0 8px;font:400 15px/1.6 ${S};color:#6b6862">${esc(t.aviso)}</p>
      <p style="margin:0;font:400 15px/1.6 ${S};color:#6b6862">Si no lo has pedido tú, no hagas nada: sin pulsar, no ocurre nada.</p>
    </td></tr>
  </table>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px">
    <tr><td style="padding:22px 8px 0">
      ${pieGrupo(marca)}
      <p style="margin:16px 0 0;font:400 13px/1.6 ${S};color:#6b6b6b">
        Este correo te llega porque alguien ha pedido entrar en ${esc(marca.nombre)} con esta dirección.
        No es publicidad y no tiene baja: es el correo que te deja usar tu cuenta.</p>
    </td></tr>
  </table>
</td></tr></table>
</body></html>`;
}

function montarTexto(marca: Marca, t: Texto, enlace: string, codigo: string) {
  const otras = MARCAS.filter((m) => m.id !== marca.id)
    .map((m) => `  ${m.nombre} — ${m.que}: ${m.url}`).join('\n');
  const cuerpo = enlace
    ? `${t.boton}:\n${enlace}\n\nO escribe este código en la misma pantalla donde lo pediste: ${codigo}`
    : `Tu código: ${codigo}`;
  return `${t.titulo}

${t.entrada}

${cuerpo}

${t.aviso}
Si no lo has pedido tú, no hagas nada: sin pulsar, no ocurre nada.

—
${marca.nombre} pertenece al Grupo Saneas, que también lo conforman:
${otras}

Este correo te llega porque alguien ha pedido entrar en ${marca.nombre} con esta
dirección. No es publicidad y no tiene baja: es el correo que te deja usar tu cuenta.`;
}

/* ---------- la llamada ---------- */
Deno.serve(async (req) => {
  const cuerpo = await req.text();

  const secreto = Deno.env.get('SEND_EMAIL_HOOK_SECRET');
  const RESEND = Deno.env.get('RESEND_API_KEY');
  const API = Deno.env.get('SUPABASE_URL');
  if (!secreto || !RESEND || !API) {
    console.error('faltan secretos');
    return new Response(JSON.stringify({ error: { http_code: 500, message: 'configuración incompleta' } }),
      { status: 500, headers: { 'Content-Type': 'application/json' } });
  }

  if (!await firmaValida(cuerpo, req.headers, secreto)) {
    return new Response('firma no válida', { status: 401 });
  }

  let user: { email?: string }, d: Record<string, string>;
  try {
    const p = JSON.parse(cuerpo);
    user = p.user; d = p.email_data;
  } catch {
    return new Response('cuerpo ilegible', { status: 400 });
  }
  if (!user?.email || !d) return new Response('sin datos', { status: 400 });

  const destino = d.redirect_to || d.site_url || '';
  const marca = marcaDe(destino);
  const t = textoDe(d.email_action_type, marca);

  /* ---------- A DÓNDE LLEVA EL BOTÓN ----------
     EN LAORA, A UNA PÁGINA DE LA CASA, no a la puerta de Supabase.

     La puerta de Supabase canjea la llave en cuanto se ABRE el enlace, y
     Outlook y Hotmail tienen un escáner que abre los enlaces de cada
     correo antes de entregarlo: la llave llegaba muerta, y con ella el
     código de seis cifras, que es la misma. Le pasó a Óscar el
     29/08/2026 dándose de alta desde otro teléfono con una cuenta de
     Hotmail: «el botón no hace nada y el código tampoco».

     `laora.es/entrar` enseña un botón y canjea la llave cuando EL
     CLIENTE lo pulsa (token_hash por POST). Un escáner carga la página
     pero no pulsa botones, así que la llave sobrevive.

     LAS DEMÁS MARCAS SIGUEN CON EL ENLACE DIRECTO a propósito: la
     página `/entrar` existe en laora.es y en ningún otro sitio, y
     mandar a Activala a una página que no tiene sería dejarla sin
     entrada. Cuando cada casa tenga la suya, se añade aquí su rama.

     En «reauthentication» no hay enlace, solo código. */
  const enlace = d.email_action_type === 'reauthentication' ? '' :
    marca.id === 'laora'
      ? `${marca.web}/entrar?llave=${encodeURIComponent(d.token_hash)}` +
        `&tipo=${encodeURIComponent(d.email_action_type)}` +
        (destino ? `&vuelve=${encodeURIComponent(destino)}` : '')
      : `${API}/auth/v1/verify?token=${encodeURIComponent(d.token_hash)}` +
        `&type=${encodeURIComponent(d.email_action_type)}` +
        (destino ? `&redirect_to=${encodeURIComponent(destino)}` : '');

  const envio = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${RESEND}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: marca.remitente,
      to: [user.email],
      reply_to: marca.remitente.replace(/^.*</, '').replace(/>$/, ''),
      subject: t.asunto,
      html: montarHtml(marca, t, enlace, d.token),
      text: montarTexto(marca, t, enlace, d.token),
      headers: { 'X-Entity-Ref-ID': `${marca.id}-${d.email_action_type}` },
    }),
  });

  if (!envio.ok) {
    const detalle = await envio.text();
    console.error('Resend', envio.status, detalle);
    // Se lo devolvemos a Supabase para que el cliente vea que no salió
    // y lo pueda volver a pedir, en vez de esperar un correo que no llega.
    return new Response(JSON.stringify({ error: { http_code: 500, message: 'no se pudo enviar el correo' } }),
      { status: 500, headers: { 'Content-Type': 'application/json' } });
  }

  return new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } });
});
