/* ============================================================
   laOra · LA FACTURA
   ------------------------------------------------------------
   El documento, en un solo sitio. Lo abren DOS pantallas: el panel
   de Óscar y la cuenta del cliente. Antes vivía dentro de
   `panel.js`, y el cliente —al que la web le promete «tu factura
   siempre a mano»— no tenía ninguna.

   Aquí no se decide nada: ni el número de factura, que lo pone la
   base con su serie correlativa, ni el IVA, que se saca DIVIDIENDO
   porque los precios de la web ya lo llevan dentro. Esto solo
   dibuja lo que ya está decidido.

   Uso:
     laoraFactura.abrir({ pedido, base, iva, tipo_iva })
   ============================================================ */
(function (global) {
  'use strict';

/* ============================================================
   LA FACTURA IMPRESA
   ------------------------------------------------------------
   Se abre en una ventana aparte y se imprime a PDF con el diálogo
   del navegador. No se guarda un archivo en ningún sitio: lo que
   manda es la FILA del pedido, con su número y su fecha, y de ahí
   se puede volver a imprimir idéntica cuantas veces haga falta.
   Un PDF guardado sería una segunda verdad que se puede perder.

   EL EMISOR ES ÓSCAR COMO AUTÓNOMO, no una sociedad (10/08/2026).
   La SL está en camino; hasta que exista, quien factura es él, y una
   venta que caiga mañana tiene que poder facturarse hoy.

   EL DÍA QUE HAYA SL hay que cambiar estos datos Y ABRIR SERIE NUEVA
   de facturas: son dos emisores distintos y sus numeraciones no se
   mezclan. La serie de aquí es F{AA}-NNNN; la de la sociedad tendrá
   que llevar otra letra.

   Si algún campo se queda vacío, la factura sale con el hueco a la
   vista, en rojo, para que no se mande por error: una factura sin el
   NIF de quien la emite no vale para nada.
   ============================================================ */
  /* Los datos fiscales van en el navegador a propósito: son los
     mismos que aparecen impresos en cualquier factura que salga de
     esta casa, y el cliente tiene derecho a verlos en la suya. */
  var EMISOR = {
    nombre: 'Óscar Belloso Jiménez',
    nif: '46922078P',
    direccion: 'San Juan, 9',
    cp: '28320', poblacion: 'Pinto', provincia: 'Madrid',
    email: 'hola@laora.es',
    web: 'laora.es'
  };

  var METODOS = {
    tarjeta: 'tarjeta', klarna: 'Klarna, en tres plazos', bizum: 'Bizum',
    paypal: 'PayPal', transferencia: 'transferencia', efectivo: 'efectivo',
    mollie: 'tarjeta'
  };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function euros(v) {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency', currency: 'EUR', minimumFractionDigits: 2
    }).format(Number(v) || 0);
  }
  function fecha(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString('es-ES',
      { day: '2-digit', month: '2-digit', year: 'numeric' });
  }
  function nombreMetodo(m) { return METODOS[m] || m || 'otro medio'; }

  /* «28013 Madrid Madrid» no lo escribe nadie: cuando la población y
     la provincia son la misma, se dice una vez. */
  function lugar(cp, poblacion, provincia) {
    var p = (poblacion || '').trim(), v = (provincia || '').trim();
    var cola = (v && v.toLowerCase() !== p.toLowerCase()) ? p + ' (' + v + ')' : p;
    return ((cp || '') + ' ' + cola).trim();
  }

  function html(d) {
    var p = d.pedido;
    var falta = !EMISOR.nombre || !EMISOR.nif || !EMISOR.direccion;

    var lineas = (p.pedido_lineas || []).map(function (l) {
      return '<tr><td>' + esc(l.modelo) + ' · ' + esc(l.acabado) +
        (l.correa ? ' · ' + esc(l.correa) : '') +
        '<br><small>' + esc(l.ref) + '</small></td>' +
        '<td class="n">' + l.cantidad + '</td>' +
        '<td class="n">' + euros(l.precio) + '</td>' +
        '<td class="n">' + euros(Number(l.precio) * Number(l.cantidad)) + '</td></tr>';
    }).join('');

    var cli = p.fac_nombre ? {
      nombre: p.fac_nombre, nif: p.fac_nif, direccion: p.fac_direccion,
      cp: p.fac_cp, poblacion: p.fac_poblacion, provincia: p.fac_provincia
    } : {
      nombre: p.env_nombre, nif: '', direccion: p.env_direccion,
      cp: p.env_cp, poblacion: p.env_poblacion, provincia: p.env_provincia
    };

    return         '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">' +
        '<title>' + esc(p.factura_numero) + ' · laOra</title><style>' +
        'body{font:15px/1.5 -apple-system,system-ui,sans-serif;color:#1c1d1b;max-width:760px;' +
        'margin:0 auto;padding:40px 28px}h1{font-size:26px;margin:0 0 4px}' +
        '.gris{color:#6b6b64}.aviso{background:#f6d5cd;color:#8a2c14;padding:12px 14px;' +
        'border-radius:10px;font-weight:700;margin-bottom:22px}' +
        '.dos{display:flex;gap:40px;flex-wrap:wrap;margin:26px 0}.dos>div{flex:1;min-width:220px}' +
        'h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#6b6b64;margin:0 0 6px}' +
        'table{width:100%;border-collapse:collapse;margin-top:14px}' +
        'th,td{padding:9px 8px;text-align:left;border-bottom:1px solid #e3e0d8;vertical-align:top}' +
        'th{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#6b6b64}' +
        '.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}' +
        'tfoot td{border:0;padding-top:6px}tfoot .tot td{border-top:2px solid #1c1d1b;font-weight:700;font-size:17px}' +
        'small{color:#6b6b64}@media print{body{padding:0}.noimp{display:none}}' +
        '</style></head><body>' +
        (falta ? '<p class="aviso">FALTAN LOS DATOS FISCALES DEL EMISOR. ' +
                 'Rellénalos en EMISOR, dentro de assets/js/panel.js, antes de mandar esta factura.</p>' : '') +
        '<h1>Factura ' + esc(p.factura_numero) + '</h1>' +
        '<p class="gris">Fecha: ' + fecha(p.factura_fecha) + ' · Pedido ' + esc(p.numero) + '</p>' +
        '<div class="dos"><div><h2>Emisor</h2>' +
        '<b>' + esc(EMISOR.nombre || '(falta el nombre fiscal)') + '</b><br>' +
        'NIF ' + esc(EMISOR.nif || '(falta)') + '<br>' +
        esc(EMISOR.direccion || '(falta la dirección)') + '<br>' +
        esc(lugar(EMISOR.cp, EMISOR.poblacion, EMISOR.provincia)) + '<br>' +
        esc(EMISOR.email) + ' · ' + esc(EMISOR.web) +
        '</div><div><h2>Cliente</h2>' +
        '<b>' + esc(cli.nombre) + '</b><br>' +
        (cli.nif ? 'NIF ' + esc(cli.nif) + '<br>' : '') +
        esc(cli.direccion) + '<br>' +
        esc(lugar(cli.cp, cli.poblacion, cli.provincia)) +
        '</div></div>' +
        '<table><thead><tr><th>Concepto</th><th class="n">Uds</th>' +
        '<th class="n">Precio</th><th class="n">Importe</th></tr></thead>' +
        '<tbody>' + lineas + '</tbody><tfoot>' +
        (Number(p.envio) ? '<tr><td colspan="3" class="n">Envío</td><td class="n">' + euros(p.envio) + '</td></tr>' : '') +
        '<tr><td colspan="3" class="n">Base imponible</td><td class="n">' + euros(d.base) + '</td></tr>' +
        '<tr><td colspan="3" class="n">IVA ' + d.tipo_iva + ' %</td><td class="n">' + euros(d.iva) + '</td></tr>' +
        '<tr class="tot"><td colspan="3" class="n">Total</td><td class="n">' + euros(p.total) + '</td></tr>' +
        '</tfoot></table>' +
        '<p class="gris">Cobrado por ' + esc(nombreMetodo(p.metodo)) +
        (p.pagado_en ? ' el ' + fecha(p.pagado_en) : '') + '.</p>' +
        '<p class="noimp"><button onclick="print()">Imprimir o guardar en PDF</button></p>' +
        '</body></html>';
  }

  function abrir(d) {
    var v = global.open('', '_blank');
    if (!v) return false;
    v.document.write(html(d));
    v.document.close();
    return true;
  }

  global.laoraFactura = { html: html, abrir: abrir, EMISOR: EMISOR };
})(window);
