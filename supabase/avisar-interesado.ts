// ============================================================
// laOra · Edge Function: avisar-interesado
// Avisa por correo (Resend) cuando alguien deja el formulario de la web.
// El correo de destino sale del secreto INTERESADOS_EMAIL: JAMÁS en el código.
// Desplegar como Edge Function con «Enforce JWT verification» DESACTIVADO
// (la llama el trigger interno de la base, no un cliente).
// Secretos necesarios: RESEND_API_KEY · INTERESADOS_EMAIL
// ============================================================

Deno.serve(async (req) => {
  try {
    const { record } = await req.json();
    if (!record?.email) return new Response('sin datos', { status: 400 });

    const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY');
    const DESTINO = Deno.env.get('INTERESADOS_EMAIL');
    if (!RESEND_API_KEY || !DESTINO) return new Response('faltan secretos', { status: 500 });

    const esc = (s: unknown) =>
      String(s ?? '—').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    const html = `
      <h2 style="font-family:sans-serif">Nuevo interesado en laOra</h2>
      <table border="0" cellpadding="6" style="font-family:sans-serif;font-size:14px">
        <tr><td><b>Nombre</b></td><td>${esc(record.nombre)}</td></tr>
        <tr><td><b>Email</b></td><td>${esc(record.email)}</td></tr>
        <tr><td><b>WhatsApp</b></td><td>${esc(record.whatsapp)}</td></tr>
        <tr><td><b>Modelo</b></td><td>${esc(record.modelo || 'Toda la colección')}</td></tr>
        <tr><td><b>Mensaje</b></td><td>${esc(record.mensaje)}</td></tr>
      </table>`;

    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'laOra <laora@saneas.es>', // dominio ya verificado en Resend (el plan Free solo admite 1)
        reply_to: record.email,
        to: [DESTINO],
        subject: `laOra · nuevo interesado: ${record.nombre}${record.modelo ? ' · ' + record.modelo : ''}`,
        html,
      }),
    });

    if (!r.ok) return new Response('resend: ' + (await r.text()), { status: 502 });
    return new Response('ok');
  } catch (e) {
    return new Response('error: ' + e, { status: 500 });
  }
});
