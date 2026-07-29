// ============================================================
// laOra · Edge Function: avisar-reserva
// ------------------------------------------------------------
// Dos correos por cada movimiento de una reserva:
//   1. a Óscar, para que sepa que hay trabajo
//   2. al cliente, que es OBLIGATORIO: la confirmación por escrito
//      del contrato en soporte duradero (art. 98.7 TRLGDCU)
//
// Desplegar con «Enforce JWT verification» DESACTIVADO: la llama
// el trigger de la base.
// Secretos: RESEND_API_KEY · INTERESADOS_EMAIL · WEB_URL
// ============================================================

const WEB = Deno.env.get('WEB_URL') ?? 'https://laora.es';

const esc = (s: unknown) =>
  String(s ?? '—').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const eur = (n: unknown) =>
  Number(n).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

Deno.serve(async (req) => {
  try {
    const { record: r } = await req.json();
    if (!r?.codigo) return new Response('sin datos', { status: 400 });

    const RESEND = Deno.env.get('RESEND_API_KEY');
    const OSCAR = Deno.env.get('INTERESADOS_EMAIL');
    if (!RESEND || !OSCAR) return new Response('faltan secretos', { status: 500 });

    const enviar = (to: string, subject: string, html: string, replyTo?: string) =>
      fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${RESEND}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: 'laOra <laora@saneas.es>',
          to: [to],
          subject,
          html,
          ...(replyTo ? { reply_to: replyTo } : {}),
        }),
      });

    const pagada = r.estado === 'pagada';
    const manual = r.metodo !== 'mollie';

    // ---------- 1. aviso interno ----------
    const interno = `
      <h2 style="font-family:sans-serif">Reserva ${esc(r.codigo)} · ${esc(r.estado)}</h2>
      <table border="0" cellpadding="6" style="font-family:sans-serif;font-size:14px">
        <tr><td><b>Reloj</b></td><td>${esc(r.ref)} «${esc(r.modelo)}» · ${esc(r.acabado)}</td></tr>
        <tr><td><b>Precio</b></td><td>${eur(r.precio_total)}</td></tr>
        <tr><td><b>Señal</b></td><td>${eur(r.senal)} (${esc(r.metodo)})</td></tr>
        <tr><td><b>Resto</b></td><td>${eur(r.resto)}</td></tr>
        <tr><td><b>Cliente</b></td><td>${esc(r.nombre)} · ${esc(r.telefono)} · ${esc(r.email)}</td></tr>
        <tr><td><b>Envío</b></td><td>${esc(r.direccion)}, ${esc(r.cp)} ${esc(r.poblacion)} (${esc(r.provincia)})</td></tr>
        <tr><td><b>Entrega</b></td><td>${esc(r.entrega_prometida)}</td></tr>
      </table>
      ${manual && !pagada
        ? '<p style="font-family:sans-serif;background:#fdf0c9;padding:12px 14px;border-radius:8px">' +
          '<b>Pendiente de cobro manual.</b> Cuando veas el dinero, pon la reserva en «pagada» ' +
          'en el Table Editor. El cliente recibe la confirmación solo.</p>'
        : ''}`;
    await enviar(OSCAR, `laOra · reserva ${r.codigo} · ${r.estado}`, interno, r.email);

    // ---------- 2. correo al cliente ----------
    const cabecera = `
      <div style="font-family:sans-serif;max-width:560px;margin:0 auto;color:#12161f">
      <p style="font-size:13px;color:#8a92a1;letter-spacing:.1em;text-transform:uppercase">
        laOra · reserva ${esc(r.codigo)}</p>`;

    const detalle = `
      <table border="0" cellpadding="7" style="font-size:14px;width:100%;border-collapse:collapse">
        <tr><td style="border-top:1px solid #e7e9ee">Reloj</td>
            <td style="border-top:1px solid #e7e9ee;text-align:right"><b>${esc(r.ref)} «${esc(r.modelo)}»</b></td></tr>
        <tr><td style="border-top:1px solid #e7e9ee">Acabado</td>
            <td style="border-top:1px solid #e7e9ee;text-align:right"><b>${esc(r.acabado)}</b></td></tr>
        <tr><td style="border-top:1px solid #e7e9ee">Precio (IVA incluido)</td>
            <td style="border-top:1px solid #e7e9ee;text-align:right">${eur(r.precio_total)}</td></tr>
        <tr><td style="border-top:1px solid #e7e9ee">Señal</td>
            <td style="border-top:1px solid #e7e9ee;text-align:right"><b>${eur(r.senal)}</b></td></tr>
        <tr><td style="border-top:1px solid #e7e9ee">Pendiente al enviarte el reloj</td>
            <td style="border-top:1px solid #e7e9ee;text-align:right">${eur(r.resto)}</td></tr>
        <tr><td style="border-top:1px solid #e7e9ee">Entrega comprometida</td>
            <td style="border-top:1px solid #e7e9ee;text-align:right">${esc(r.entrega_prometida)}</td></tr>
      </table>`;

    const derechos = `
      <p style="font-size:14px;line-height:1.65">Tienes <b>14 días naturales</b> para echarte
      atrás sin dar explicaciones. Nos lo dices por WhatsApp o respondiendo a este correo y te
      devolvemos la señal <b>entera</b>, en un máximo de 14 días y por el mismo medio con el
      que pagaste. No hay formularios ni preguntas.</p>
      <p style="font-size:14px;line-height:1.65">Tu reloj lleva <b>3 años de garantía</b>, que
      es la que manda la ley española, con servicio técnico propio en España.</p>
      <p style="font-size:13px;color:#8a92a1;line-height:1.6">Las
      <a href="${WEB}/condiciones-de-venta.html" style="color:#C9A227">condiciones de venta</a>
      completas y la <a href="${WEB}/privacidad.html" style="color:#C9A227">política de
      privacidad</a>. Guarda este correo: es tu justificante.</p></div>`;

    let cuerpo: string;
    let asunto: string;

    if (pagada) {
      asunto = `Tu ${r.ref} «${r.modelo}» está reservado · ${r.codigo}`;
      cuerpo = cabecera +
        `<h1 style="font-size:26px;letter-spacing:-1px">Tu reloj está reservado.</h1>
         <p style="font-size:16px;line-height:1.6;color:#454b57">Hemos recibido tu señal y tu
         unidad queda apartada a tu nombre. Te escribiremos cuando esté montado, para cobrarte
         el resto y enviártelo. Ni antes, ni sin avisar.</p>` + detalle + derechos;
    } else if (manual) {
      asunto = `Reserva anotada · falta tu pago · ${r.codigo}`;
      cuerpo = cabecera +
        `<h1 style="font-size:26px;letter-spacing:-1px">Nos falta tu pago para apartarla.</h1>
         <p style="font-size:16px;line-height:1.6;color:#454b57">Tenemos tus datos.
         <b>La unidad no queda apartada hasta que veamos la señal</b>, así que te lo decimos
         claro. Envíanos ${eur(r.senal)} por ${esc(r.metodo)} poniendo
         <b>${esc(r.codigo)}</b> en el concepto, y te confirmamos en cuanto llegue.</p>` +
        detalle + derechos;
    } else {
      asunto = `Reserva ${r.codigo} · ${r.estado}`;
      cuerpo = cabecera +
        `<h1 style="font-size:26px;letter-spacing:-1px">Tu reserva está ${esc(r.estado)}.</h1>` +
        detalle + derechos;
    }

    await enviar(r.email, asunto, cuerpo, OSCAR);
    return new Response('ok');
  } catch (e) {
    console.error(e);
    return new Response('error', { status: 500 });
  }
});
