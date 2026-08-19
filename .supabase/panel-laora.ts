// ============================================================
// laOra · Edge Function: panel-laora
// ------------------------------------------------------------
// El cuarto de atrás. Todo lo que ve y hace Óscar pasa por aquí.
//
// EL MODELO ES EL DE SANEAS, a propósito: una página estática sin
// secretos + esta función con el service role. La página NUNCA habla
// con la base directamente, así que en su JavaScript no hay ninguna
// clave que valga para nada. La única llave es la contraseña, que
// vive en el secreto `PANEL_LAORA_PASSWORD` y viaja en cada llamada.
//
// POR QUÉ ASÍ Y NO CON RLS: el panel tiene que ver los pedidos de
// TODO el mundo, que es justo lo que las políticas impiden. El
// service role las salta; por eso no puede estar en el navegador.
//
// DESPLIEGUE
//   supabase functions deploy panel-laora \
//     --project-ref uikanfvigunjhzibnhxf --no-verify-jwt
//   Secreto a poner: PANEL_LAORA_PASSWORD
//
// ACCIONES (POST con {clave, accion, ...})
//   entrar · resumen · pasarela · pedidos · pedido · cobrado · estado
//   (al marcar 'enviado' se COBRA el pago a plazos de Klarna)
//   serie  · socios  · socio   · mensajes · responder · leido
//   valoraciones · moderar
//   cuentas · compras · gastos · gasto_nuevo · gasto_borrar
//   facturar · factura
// ============================================================

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const json = (c: unknown, status = 200) =>
  new Response(JSON.stringify(c), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

const URL_SB = Deno.env.get('SUPABASE_URL')!;

/* La llave que salta las políticas de filas.
   `SUPABASE_SERVICE_ROLE_KEY` existe en el entorno, pero en este
   proyecto —que ya está en el sistema nuevo de claves— no vale para la
   API REST: devuelve 401. Por eso se guarda aparte la que sí funciona,
   en el secreto `LAORA_SERVICIO`. Se prueba primero esa; la otra queda
   de reserva por si algún día vuelve a valer.
   NUNCA sale de aquí: la página del panel no la ve. */
const SERVICIO = Deno.env.get('LAORA_SERVICIO') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

/* Toda la base pasa por aquí, siempre en el esquema `laora`. */
async function db(ruta: string, opciones: RequestInit = {}) {
  const r = await fetch(`${URL_SB}/rest/v1/${ruta}`, {
    ...opciones,
    headers: {
      apikey: SERVICIO,
      Authorization: `Bearer ${SERVICIO}`,
      'Content-Type': 'application/json',
      'Accept-Profile': 'laora',
      'Content-Profile': 'laora',
      Prefer: 'return=representation',
      ...(opciones.headers || {}),
    },
  });
  const texto = await r.text();
  if (!r.ok) {
    console.error('db', ruta, r.status, texto);
    throw new Error('la base ha dicho que no: ' + r.status);
  }
  return texto ? JSON.parse(texto) : null;
}

/* Comparación que tarda lo mismo acierte o falle: si tardara menos
   al fallar antes, se podría adivinar la contraseña letra a letra. */
function igual(a: string, b: string) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

const hoy = () => new Date().toISOString().slice(0, 10);

/* El número de serie que se propone: LO01-26-0007.
   Código del modelo sin guiones + año + correlativo de ESE modelo en
   ESE año. Se propone, no se impone: en el panel es un campo editable,
   porque el número puede venir grabado de fábrica. */
async function proponerSerie(ref: string) {
  const codigo = (ref.split('_')[0] || 'LO').replace(/-/g, '');
  const anio = new Date().getFullYear().toString().slice(-2);
  const prefijo = `${codigo}-${anio}-`;
  const previos = await db(
    `relojes?select=numero_serie&numero_serie=like.${encodeURIComponent(prefijo + '*')}`);
  let mayor = 0;
  for (const r of (previos || [])) {
    const n = parseInt(String(r.numero_serie).slice(prefijo.length), 10);
    if (!isNaN(n) && n > mayor) mayor = n;
  }
  return prefijo + String(mayor + 1).padStart(4, '0');
}

/* ============================================================
   COBRAR UN PAGO DE KLARNA
   ------------------------------------------------------------
   Klarna no cobra al comprar: autoriza. El dinero se captura
   cuando el pedido se envía, y Mollie da 28 días para hacerlo.
   Esto es lo que dispara ese cobro.

   No hace nada si el pedido se pagó con tarjeta, Bizum o PayPal
   —esos ya están cobrados— ni si no hay pago de Mollie detrás.
   ============================================================ */
async function capturarKlarna(pedidoId: string): Promise<
  { capturado: boolean; importe?: string; error?: string }
> {
  const MOLLIE = Deno.env.get('LAORA_MOLLIE_API_KEY');
  const filas = await db(`pedidos?select=id,numero,total,estado,referencia_pago&id=eq.${pedidoId}&limit=1`);
  const ped = filas[0];
  if (!ped || !ped.referencia_pago) return { capturado: false };
  if (!MOLLIE) return { error: 'Falta la clave de Mollie: no se puede cobrar el pago a plazos.' };

  const r = await fetch(`https://api.mollie.com/v2/payments/${ped.referencia_pago}`, {
    headers: { Authorization: `Bearer ${MOLLIE}` },
  });
  if (!r.ok) {
    console.error('mollie leer pago', await r.text());
    return { error: 'Mollie no responde. Vuelve a intentarlo en un momento.' };
  }
  const pago = await r.json();

  // Ya cobrado (tarjeta, Bizum…) o nada que capturar: se sigue.
  if (pago.status !== 'authorized') return { capturado: false };

  const cap = await fetch(`https://api.mollie.com/v2/payments/${ped.referencia_pago}/captures`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${MOLLIE}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      amount: pago.amount,
      description: `laOra · pedido ${ped.numero} enviado`,
    }),
  });
  if (!cap.ok) {
    console.error('mollie capturar', await cap.text());
    return { error: 'No se ha podido cobrar el pago a plazos. El pedido sigue sin enviar.' };
  }

  await db(`pedidos?id=eq.${pedidoId}`, {
    method: 'PATCH',
    body: JSON.stringify({ estado: 'pagado', pagado_en: new Date().toISOString() }),
  });
  return { capturado: true, importe: pago.amount?.value };
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'solo POST' }, 405);

  const CLAVE = Deno.env.get('PANEL_LAORA_PASSWORD');
  if (!CLAVE || !URL_SB || !SERVICIO) return json({ error: 'el panel no está configurado' }, 500);

  let p: any;
  try { p = await req.json(); } catch { return json({ error: 'petición ilegible' }, 400); }

  if (!p?.clave || !igual(String(p.clave), CLAVE)) {
    /* Un respiro antes de contestar: hace inviable probar contraseñas
       a lo bruto, y a quien la sabe no le molesta. */
    await new Promise((r) => setTimeout(r, 700));
    return json({ error: 'Contraseña incorrecta.' }, 401);
  }

  try {
    switch (p.accion) {

      // ---------- entrar ----------
      case 'entrar':
        return json({ ok: true });

      // ---------- el panorama ----------
      case 'resumen': {
        const [pedidos, socios, mensajes, valoraciones, relojes] = await Promise.all([
          db('pedidos?select=estado,total,creado_en&order=creado_en.desc'),
          db('socios?select=id'),
          db('mensajes?select=id&autor=eq.socio&leido_en=is.null'),
          db('valoraciones?select=id&estado=eq.pendiente'),
          db('relojes?select=id,estado'),
        ]);
        const porEstado: Record<string, number> = {};
        let facturado = 0;
        for (const x of pedidos) {
          porEstado[x.estado] = (porEstado[x.estado] || 0) + 1;
          if (x.estado !== 'cancelado' && x.estado !== 'devuelto') facturado += Number(x.total);
        }
        return json({
          ok: true,
          pedidos: pedidos.length,
          porEstado,
          facturado: Math.round(facturado * 100) / 100,
          socios: socios.length,
          mensajes_sin_leer: mensajes.length,
          valoraciones_pendientes: valoraciones.length,
          relojes_entregados: relojes.filter((r: any) => r.estado === 'entregado').length,
        });
      }

      // ---------- pedidos ----------
      case 'pedidos': {
        const filtro = p.estado && p.estado !== 'todos' ? `&estado=eq.${p.estado}` : '';
        const filas = await db(
          `pedidos?select=id,numero,creado_en,estado,total,metodo,env_nombre,env_poblacion,env_provincia,socio_id,` +
          `pedido_lineas(id,ref,modelo,acabado,correa,cantidad)` +
          `&order=creado_en.desc&limit=200${filtro}`);
        return json({ ok: true, pedidos: filas });
      }

      case 'pedido': {
        const filas = await db(
          `pedidos?select=*,pedido_lineas(*),socios(*)&id=eq.${p.id}&limit=1`);
        if (!filas.length) return json({ error: 'ese pedido no existe' }, 404);
        const pedido = filas[0];
        const ids = (pedido.pedido_lineas || []).map((l: any) => `"${l.id}"`).join(',');
        pedido.relojes = ids
          ? await db(`relojes?select=*,garantias(*)&linea_id=in.(${ids})`)
          : [];
        return json({ ok: true, pedido });
      }

      // ---------- el dinero ----------
      case 'cobrado': {
        const filas = await db(`pedidos?id=eq.${p.id}`, {
          method: 'PATCH',
          body: JSON.stringify({
            estado: 'pagado',
            pagado_en: new Date().toISOString(),
            metodo: p.metodo || 'paypal',
            referencia_pago: p.referencia || null,
          }),
        });
        return json({ ok: true, pedido: filas[0] });
      }

      // ---------- por dónde va ----------
      case 'estado': {
        const cambio: Record<string, unknown> = { estado: p.estado };
        let cobrado: string | null = null;

        if (p.estado === 'enviado') {
          cambio.enviado_en = new Date().toISOString();
          if (p.transportista) cambio.transportista = p.transportista;
          if (p.seguimiento) cambio.seguimiento = p.seguimiento;

          /* AQUÍ SE COBRA KLARNA. Al pagar a plazos el dinero queda
             reservado, no cobrado: Mollie lo exige por escrito y da 28
             días para capturarlo, contados desde que se autorizó. El
             momento es este, cuando el reloj sale por la puerta.
             Si la captura falla, el pedido NO se marca como enviado:
             es preferible repetir el clic a dar por enviado algo que
             no se ha cobrado. */
          const cobro = await capturarKlarna(String(p.id));
          if (cobro.error) return json({ error: cobro.error }, 502);
          cobrado = cobro.capturado ? cobro.importe! : null;
        }
        if (p.estado === 'entregado') cambio.entregado_en = new Date().toISOString();
        if (p.notas !== undefined) cambio.notas = p.notas;
        const filas = await db(`pedidos?id=eq.${p.id}`, {
          method: 'PATCH', body: JSON.stringify(cambio),
        });

        /* Al entregar, los relojes de ese pedido quedan entregados y su
           garantía echa a andar HOY. Es el momento exacto en que empieza
           a contar, y así no depende de que alguien se acuerde de ponerlo.
           En dos pasos porque PostgREST no admite subconsultas. */
        if (p.estado === 'entregado') {
          const lineas = await db(`pedido_lineas?select=id&pedido_id=eq.${p.id}`);
          const ids = lineas.map((l: any) => `"${l.id}"`).join(',');
          if (ids) {
            const relojes = await db(`relojes?linea_id=in.(${ids})`, {
              method: 'PATCH',
              body: JSON.stringify({ estado: 'entregado', entregado_en: hoy() }),
            });
            const suyos = relojes.map((r: any) => `"${r.id}"`).join(',');
            if (suyos) {
              await db(`garantias?reloj_id=in.(${suyos})`, {
                method: 'PATCH', body: JSON.stringify({ desde: hoy() }),
              });
            }
          }
        }
        return json({ ok: true, pedido: filas[0], cobrado });
      }

      // ---------- la pasarela: ¿real o de pruebas? ----------
      /* No devuelve la clave ni un trozo de ella: solo si empieza por
         `live_` o por `test_`, y qué formas de pago tiene activas la
         cuenta. Es la respuesta a «¿esto cobra de verdad?» sin que
         nadie tenga que ir a mirar un secreto. */
      case 'pasarela': {
        const MOLLIE = Deno.env.get('LAORA_MOLLIE_API_KEY');
        if (!MOLLIE) return json({ ok: true, hay: false });

        const modo = MOLLIE.startsWith('live_') ? 'real'
                   : MOLLIE.startsWith('test_') ? 'pruebas' : 'raro';

        /* Se le pide a Mollie con un importe de los nuestros: hay
           métodos que solo aparecen a partir de cierta cantidad. */
        const r = await fetch(
          'https://api.mollie.com/v2/methods?amount[value]=189.90&amount[currency]=EUR&locale=es_ES',
          { headers: { Authorization: `Bearer ${MOLLIE}` } });
        if (!r.ok) {
          console.error('mollie methods', await r.text());
          return json({ ok: true, hay: true, modo, error: 'Mollie no ha contestado.' });
        }
        const d = await r.json();
        const metodos = (d?._embedded?.methods || []).map((m: any) => m.description || m.id);
        return json({ ok: true, hay: true, modo, metodos });
      }

      // ---------- el reloj y su número ----------
      case 'proponer_serie':
        return json({ ok: true, numero_serie: await proponerSerie(String(p.ref || '')) });

      case 'serie': {
        // La línea, para copiar de ella lo que se vendió.
        const lineas = await db(`pedido_lineas?select=*,pedidos(socio_id)&id=eq.${p.linea_id}&limit=1`);
        if (!lineas.length) return json({ error: 'esa línea no existe' }, 404);
        const l = lineas[0];
        const socio = l.pedidos?.socio_id || null;
        const serie = String(p.numero_serie || '').trim();
        if (!serie) return json({ error: 'hace falta el número de serie' }, 400);

        // ¿Ya había uno asignado a esta línea? Entonces se corrige.
        const previos = await db(`relojes?select=id&linea_id=eq.${l.id}&limit=1`);
        const cuerpo = {
          numero_serie: serie, ref: l.ref, modelo: l.modelo, acabado: l.acabado,
          correa: l.correa, ficha: l.ficha, linea_id: l.id, socio_id: socio,
          estado: p.estado_reloj || 'asignado',
          notas: p.notas ?? null,
        };
        const reloj = previos.length
          ? (await db(`relojes?id=eq.${previos[0].id}`, { method: 'PATCH', body: JSON.stringify(cuerpo) }))[0]
          : (await db('relojes', { method: 'POST', body: JSON.stringify(cuerpo) }))[0];

        // Su garantía, si aún no la tiene.
        const meses = parseInt(p.meses, 10) || 24;
        const yaHay = await db(`garantias?select=id&reloj_id=eq.${reloj.id}&limit=1`);
        const garantia = yaHay.length
          ? (await db(`garantias?id=eq.${yaHay[0].id}`, {
              method: 'PATCH',
              body: JSON.stringify({ meses, desde: p.desde || hoy(), socio_id: socio }),
            }))[0]
          : (await db('garantias', {
              method: 'POST',
              body: JSON.stringify({
                reloj_id: reloj.id, socio_id: socio,
                desde: p.desde || hoy(), meses,
                hasta: hoy(),   // lo recalcula el disparador
                condiciones: p.condiciones || null,
              }),
            }))[0];

        return json({ ok: true, reloj, garantia });
      }

      case 'intervencion': {
        const fila = await db('intervenciones', {
          method: 'POST',
          body: JSON.stringify({
            reloj_id: p.reloj_id, fecha: p.fecha || hoy(),
            tipo: p.tipo || 'revision',
            en_garantia: p.en_garantia !== false,
            descripcion: String(p.descripcion || '').trim(),
            coste: Number(p.coste) || 0,
          }),
        });
        return json({ ok: true, intervencion: fila[0] });
      }

      // ---------- socios ----------
      case 'socios': {
        const filas = await db(
          'socios?select=id,creado_en,email,nombre,apellidos,telefono,poblacion,provincia,club_desde' +
          '&order=creado_en.desc&limit=500');
        return json({ ok: true, socios: filas });
      }

      case 'socio': {
        const filas = await db(`socios?select=*&id=eq.${p.id}&limit=1`);
        if (!filas.length) return json({ error: 'ese socio no existe' }, 404);
        const [pedidos, relojes, mensajes] = await Promise.all([
          db(`pedidos?select=id,numero,creado_en,estado,total&socio_id=eq.${p.id}&order=creado_en.desc`),
          db(`relojes?select=*,garantias(*)&socio_id=eq.${p.id}`),
          db(`mensajes?select=*&socio_id=eq.${p.id}&order=creado_en`),
        ]);
        return json({ ok: true, socio: filas[0], pedidos, relojes, mensajes });
      }

      case 'club': {
        const filas = await db(`socios?id=eq.${p.id}`, {
          method: 'PATCH',
          body: JSON.stringify({ club_desde: p.club ? (p.desde || hoy()) : null }),
        });
        return json({ ok: true, socio: filas[0] });
      }

      case 'notas_socio': {
        const filas = await db(`socios?id=eq.${p.id}`, {
          method: 'PATCH', body: JSON.stringify({ notas: p.notas ?? null }),
        });
        return json({ ok: true, socio: filas[0] });
      }

      // ---------- comentarios en privado ----------
      case 'mensajes': {
        const filas = await db(
          'mensajes?select=*,socios(nombre,apellidos,email)&order=creado_en.desc&limit=300');
        return json({ ok: true, mensajes: filas });
      }

      case 'responder': {
        const fila = await db('mensajes', {
          method: 'POST',
          body: JSON.stringify({
            socio_id: p.socio_id, pedido_id: p.pedido_id || null,
            autor: 'laora', texto: String(p.texto || '').trim(),
          }),
        });
        // Al contestar, lo suyo queda leído: no hace falta dos clics.
        await db(`mensajes?socio_id=eq.${p.socio_id}&autor=eq.socio&leido_en=is.null`, {
          method: 'PATCH', body: JSON.stringify({ leido_en: new Date().toISOString() }),
        });
        return json({ ok: true, mensaje: fila[0] });
      }

      case 'leido': {
        await db(`mensajes?socio_id=eq.${p.socio_id}&autor=eq.socio&leido_en=is.null`, {
          method: 'PATCH', body: JSON.stringify({ leido_en: new Date().toISOString() }),
        });
        return json({ ok: true });
      }

      // ---------- comentarios en público ----------
      case 'valoraciones': {
        const filtro = p.estado && p.estado !== 'todas' ? `&estado=eq.${p.estado}` : '';
        const filas = await db(
          `valoraciones?select=*,socios(nombre,apellidos,email)&order=creado_en.desc&limit=300${filtro}`);
        return json({ ok: true, valoraciones: filas });
      }

      case 'moderar': {
        const publicar = p.decision === 'publicar';
        const filas = await db(`valoraciones?id=eq.${p.id}`, {
          method: 'PATCH',
          body: JSON.stringify({
            estado: publicar ? 'publicada' : 'rechazada',
            publicada_en: publicar ? new Date().toISOString() : null,
            respuesta: p.respuesta ?? null,
          }),
        });
        return json({ ok: true, valoracion: filas[0] });
      }

      // ============================================================
      // LAS CUENTAS
      // ------------------------------------------------------------
      // Todo esto sale de las vistas de `panel-cuentas.sql`. Aquí no se
      // suma nada: si el cálculo viviera en dos sitios, un día dirían
      // cosas distintas y no sabríamos cuál creer.
      // ============================================================
      case 'cuentas': {
        const [trimestres, anios, metodos] = await Promise.all([
          db('cuentas_trimestre?select=*&limit=40'),
          db('cuentas_anio?select=*&limit=20'),
          db('cobros_metodo?select=*&limit=200'),
        ]);
        /* El año en curso, que es lo que se mira noventa veces al día.
           Se saca de los trimestres ya cerrados, no aparte. */
        const anio = new Date().getFullYear();
        const ytd = trimestres
          .filter((t: any) => Number(t.anio) === anio)
          .reduce((a: any, t: any) => ({
            pedidos: a.pedidos + Number(t.pedidos),
            ingresos: a.ingresos + Number(t.ingresos),
            piezas: a.piezas + Number(t.piezas),
            gastos: a.gastos + Number(t.gastos),
            margen: a.margen + Number(t.margen),
            iva_a_pagar: a.iva_a_pagar + Number(t.iva_a_pagar),
          }), { pedidos: 0, ingresos: 0, piezas: 0, gastos: 0, margen: 0, iva_a_pagar: 0 });
        for (const k of Object.keys(ytd)) {
          (ytd as any)[k] = Math.round((ytd as any)[k] * 100) / 100;
        }
        return json({ ok: true, anio, ytd, trimestres, anios, metodos });
      }

      // ---------- la lista de la compra ----------
      // Un pedido al proveedor en vez de cinco: la vista junta las
      // piezas de todos los pedidos cobrados y sin enviar.
      case 'compras': {
        const filas = await db('compra_pendiente?select=*');
        return json({ ok: true, compras: filas });
      }

      // ---------- los gastos que no son piezas ----------
      case 'gastos': {
        const desde = p.desde ? `&fecha=gte.${p.desde}` : '';
        const hasta = p.hasta ? `&fecha=lte.${p.hasta}` : '';
        const filas = await db(
          `gastos?select=*,pedidos(numero)&order=fecha.desc&limit=400${desde}${hasta}`);
        return json({ ok: true, gastos: filas });
      }

      case 'gasto_nuevo': {
        const concepto = String(p.concepto || '').trim();
        const importe = Number(p.importe);
        if (!concepto) return json({ error: 'hace falta el concepto' }, 400);
        if (!(importe >= 0)) return json({ error: 'el importe no es un número' }, 400);
        const filas = await db('gastos', {
          method: 'POST',
          body: JSON.stringify({
            fecha: p.fecha || hoy(),
            concepto,
            categoria: p.categoria || 'otro',
            importe,
            iva: Number(p.iva) || 0,
            proveedor: p.proveedor || null,
            factura: p.factura || null,
            enlace: p.enlace || null,
            pedido_id: p.pedido_id || null,
            notas: p.notas || null,
          }),
        });
        return json({ ok: true, gasto: filas[0] });
      }

      case 'gasto_borrar': {
        await db(`gastos?id=eq.${p.id}`, { method: 'DELETE' });
        return json({ ok: true });
      }

      // ---------- la factura ----------
      // El número lo pone la base con un candado, no esta función: dos
      // clics seguidos no pueden sacar dos números.
      case 'facturar': {
        const r = await fetch(`${URL_SB}/rest/v1/rpc/emitir_factura`, {
          method: 'POST',
          headers: {
            apikey: SERVICIO,
            Authorization: `Bearer ${SERVICIO}`,
            'Content-Type': 'application/json',
            'Content-Profile': 'laora',
          },
          body: JSON.stringify({ p_pedido: p.id }),
        });
        const texto = await r.text();
        if (!r.ok) return json({ error: texto }, 400);
        return json({ ok: true, numero: JSON.parse(texto) });
      }

      // Todo lo que hace falta para imprimir una factura, junto.
      case 'factura': {
        const filas = await db(
          `pedidos?select=*,pedido_lineas(*),socios(nombre,apellidos,email,telefono)&id=eq.${p.id}&limit=1`);
        if (!filas.length) return json({ error: 'ese pedido no existe' }, 404);
        const ped = filas[0];
        const total = Number(ped.total);
        return json({
          ok: true,
          pedido: ped,
          /* La base se saca DIVIDIENDO: los precios de la web ya llevan
             el IVA dentro. Multiplicar por 0,21 daría de menos. */
          base: Math.round((total / 1.21) * 100) / 100,
          iva: Math.round((total - total / 1.21) * 100) / 100,
          tipo_iva: 21,
        });
      }

      default:
        return json({ error: 'no sé hacer eso: ' + p.accion }, 400);
    }
  } catch (e) {
    console.error(p.accion, e);
    return json({ error: String((e as Error).message || e) }, 500);
  }
});
