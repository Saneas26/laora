/* ============================================================
   laOra · CONFIGURADOR DE CUATRO EJES  ·  MAQUETA
   ------------------------------------------------------------
   El estado son cuatro índices —movimiento, caja, esfera, brazalete—
   más la variante elegida dentro del brazalete. De ahí sale TODO lo
   demás: la foto, las características, la referencia y el precio.

   EL PRECIO NO ESTÁ ESCRITO EN NINGUNA PARTE. Se suman las cuatro
   piezas, se multiplica y se redondea al 9,90 más cercano. Por eso una
   esfera nueva no obliga a decidir un precio: entra con el suyo puesto.
   ============================================================ */
(function () {
  'use strict';

  var D = JSON.parse(document.querySelector('[data-piezas]').textContent);
  var $ = function (s) { return document.querySelector(s); };
  var todos = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };

  var e = { mov: 0, caja: 0, esf: 0, brz: 0, v: 0 };

  function euros(v) { return v.toFixed(2).replace('.', ',') + ' €'; }

  /* Al 9,90 más cercano. OJO con el de abajo: la cuenta evidente
     —floor(p/10)*10 + 9,90— está mal y calla. Para 264,56 devuelve
     269,90, que está POR ENCIMA. Hay que restar el 9,90 ANTES de
     truncar. Con la versión mala, cinco de las siete configuraciones
     del Lunar salían diez euros caras. */
  function redondea(p) {
    var bajo = Math.floor((p - 9.90) / 10) * 10 + 9.90;
    return (p - bajo) <= (bajo + 10 - p) ? bajo : bajo + 10;
  }

  /* ---------- el DIBUJO del brazalete ----------
     Un rectángulo de color plano no parece un brazalete: parece una
     cinta. Aquí se le da el relieve del metal y la sombra entre
     eslabones. Cuando lleguen las fotos, esta función desaparece y la
     banda pasa a ser un <img>. */
  function mezcla(hex, con, cuanto) {
    var a = parseInt(hex.slice(1), 16), b = parseInt(con.slice(1), 16), out = 0, i;
    for (i = 16; i >= 0; i -= 8) {
      var v = Math.round((((a >> i) & 255) * (1 - cuanto)) + (((b >> i) & 255) * cuanto));
      out |= v << i;
    }
    return '#' + ('000000' + out.toString(16)).slice(-6);
  }

  var ESLABONES = 'repeating-linear-gradient(0deg,rgba(0,0,0,.16) 0 1.5px,' +
                  'rgba(255,255,255,.10) 1.5px 3px,rgba(0,0,0,0) 3px 15px)';
  var TEJIDO = 'repeating-linear-gradient(90deg,rgba(255,255,255,.07) 0 3px,rgba(0,0,0,.07) 3px 6px)';
  var COSTURA = 'repeating-linear-gradient(0deg,rgba(255,255,255,.30) 0 5px,rgba(0,0,0,0) 5px 11px)';

  /* El tono sale del NOMBRE de la variante, que es lo único que hay:
     la hoja no guarda el color en hexadecimal. Si no se reconoce, gris
     acero, que es lo que más abunda. */
  var TONOS = [
    [/negro|negra|black/i, '#26282a'], [/blanc/i, '#e9e7e2'],
    [/marr[óo]n oscuro|dark ?brown/i, '#4a2f1d'], [/marr[óo]n claro|light ?brown/i, '#a5744a'],
    [/marr[óo]n|brown/i, '#6b4222'], [/azul marino|navy/i, '#22334d'], [/azul|blue/i, '#2f4a6b'],
    [/verde militar/i, '#4a5238'], [/verde|green/i, '#3a5a40'], [/caqui|khaki/i, '#7a7351'],
    [/gris|grey|gray/i, '#7d8286'], [/rojo|red/i, '#7c2b26'], [/naranja|orange/i, '#b5622a'],
    [/beige/i, '#c8b89a'], [/oro rosa|rose ?gold/i, '#c9a08a'], [/oro|gold/i, '#cbae6d'],
    [/plata|silver|acero/i, '#c7cbcf']
  ];

  function tonos(nombre) {
    var t = [];
    TONOS.forEach(function (par) { if (par[0].test(nombre) && t.indexOf(par[1]) < 0) t.push(par[1]); });
    return t.length ? t.slice(0, 2) : ['#c7cbcf'];
  }

  function metal(c) {
    return mezcla(c, '#ffffff', .58) + ' 0%,' + mezcla(c, '#000000', .20) + ' 28%,' +
           mezcla(c, '#ffffff', .46) + ' 50%,' + mezcla(c, '#000000', .30) + ' 74%,' +
           mezcla(c, '#ffffff', .22) + ' 100%';
  }

  /* Un brazalete bicolor no es medio y medio en diagonal: es claro por
     fuera y el otro tono por el centro, que es por donde corren los
     eslabones del medio. */
  function dibujo(familia, nombreVar) {
    var t = tonos(nombreVar), textura = ESLABONES;
    if (/piel|ante|cuero/i.test(familia)) textura = COSTURA;
    else if (/lona|nailon|tela|caucho|goma/i.test(familia)) textura = TEJIDO;
    if (t.length > 1) {
      return textura + ',linear-gradient(90deg,' +
        mezcla(t[0], '#ffffff', .40) + ' 0 30%,' + mezcla(t[1], '#ffffff', .34) + ' 30% 42%,' +
        mezcla(t[1], '#000000', .12) + ' 42% 58%,' + mezcla(t[1], '#ffffff', .34) + ' 58% 70%,' +
        mezcla(t[0], '#000000', .18) + ' 70% 100%)';
    }
    return textura + ',linear-gradient(100deg,' + metal(t[0]) + ')';
  }

  /* ---------- estado ---------- */

  function piezas() {
    var f = D.brz[e.brz];
    return {
      mov: D.mov[e.mov], caja: D.caj[e.caja],
      esf: D.esf.length ? D.esf[e.esf] : null,
      fam: f, v: f.v[Math.min(e.v, f.v.length - 1)]
    };
  }

  /* El brazalete del Diver es un EXTRA: se suma a lo que ya trae la
     caja, no la sustituye. En los demás va dentro del precio. */
  function coste() {
    var p = piezas();
    return p.mov.coste + p.caja.coste + (p.esf ? p.esf.coste : 0) + p.v.c;
  }

  function referencia() {
    var p = piezas();
    var seg = [D.codigo, p.mov.ref, p.caja.ref];
    if (p.esf) seg.push(p.esf.ref);
    seg.push(p.v.ref);
    return seg.join('-');
  }

  /* Una esfera puede no entrar en todas las cajas: en el Lunar la negra
     solo va con el bisel negro. La hoja lo dice en `cajas`. */
  function esferaVale(esf, caja) {
    if (!esf.cajas || /todas/i.test(esf.cajas)) return true;
    return esf.cajas.split(',').map(function (s) { return s.trim(); }).indexOf(caja.ref) >= 0;
  }

  /* ---------- pintar ---------- */

  function pintaVisor() {
    var p = piezas();
    var foto = D.fotos[p.caja.ref];
    $('[data-foto]').src = foto || D.fotoDefecto;
    $('[data-pendiente]').hidden = !!foto;
    var fondo = dibujo(p.fam.nombre, p.v.nom);
    todos('[data-correa]').forEach(function (el) { el.style.background = fondo; });
    $('[data-viendo]').innerHTML = '<b>' + p.caja.nombre + '</b> <span>· ' +
      (p.esf ? p.esf.nombre + ' · ' : '') + p.fam.nombre + '</span>';
  }

  function pintaSpecs() {
    var p = piezas();
    var filas = [['Movimiento', p.mov.cal], ['Acabado', p.mov.acabado], ['Caja', p.caja.nombre]];
    if (p.esf) filas.push(['Esfera', p.esf.nombre]);
    filas.push(['Brazalete', p.fam.nombre]);
    $('[data-specs]').innerHTML = filas.map(function (f) {
      return '<dt>' + f[0] + '</dt><dd>' + f[1] + '</dd>';
    }).join('');
  }

  function pintaVariantes() {
    var p = piezas(), caja = $('[data-variantes]');
    caja.innerHTML = p.fam.v.map(function (v, i) {
      var t = tonos(v.nom);
      var fondo = t.length > 1
        ? 'linear-gradient(135deg,' + t[0] + ' 0 50%,' + t[1] + ' 50% 100%)' : t[0];
      return '<button class="cf-color" type="button" data-var="' + i + '"' +
        ' aria-pressed="' + (i === e.v) + '" title="' + v.nom + '" aria-label="' + v.nom + '"' +
        ' style="background:' + fondo + '"></button>';
    }).join('') + '<span class="cf-color-nombre" data-var-nombre></span>';
    $('[data-var-nombre]').textContent = p.v.nom;
    $('[data-cuenta-var]').textContent = p.fam.v.length + ' opciones';
    $('[data-grupo-var]').hidden = p.fam.v.length < 2;
    $('[data-detalle]').textContent = p.fam.nombre + ' · ' + p.fam.v.length +
      (p.fam.v.length === 1 ? ' acabado' : ' acabados') + ' · desde ' +
      euros(Math.min.apply(null, p.fam.v.map(function (x) { return x.c; })));
  }

  function pintaPrecio() {
    var p = piezas(), c = coste(), pvp = redondea(c * D.mult);
    $('[data-precio]').textContent = euros(pvp);
    $('[data-ref]').textContent = referencia();
    $('[data-barra-nombre]').textContent = p.caja.nombre + ' · ' + p.fam.nombre;
    $('[data-barra-var]').textContent = p.v.nom;
    $('[data-desglose]').innerHTML =
      '<b>Lo que hay que comprar</b><br>' +
      'Movimiento <i>' + p.mov.ref + '</i> ' + euros(p.mov.coste) + '<br>' +
      'Caja <i>' + p.caja.ref + '</i> ' + euros(p.caja.coste) + '<br>' +
      (p.esf ? 'Esfera <i>' + p.esf.ref + '</i> ' + euros(p.esf.coste) + '<br>' : '') +
      'Brazalete <i>' + p.v.ref + '</i> ' + euros(p.v.c) + '<br>' +
      'Suma <i>' + euros(c) + '</i><br>' +
      '× ' + String(D.mult).replace('.', ',') + ' → <b>' + euros(pvp) + '</b>';
  }

  function pinta() {
    /* Las esferas que no entran en la caja elegida se apagan, no se
       esconden: si desaparecieran, parecería que no existen. */
    if (D.esf.length) {
      var caja = D.caj[e.caja];
      if (!esferaVale(D.esf[e.esf], caja)) {
        for (var i = 0; i < D.esf.length; i++) {
          if (esferaVale(D.esf[i], caja)) { e.esf = i; break; }
        }
      }
      todos('[data-esf]').forEach(function (el) {
        var i = Number(el.dataset.esf);
        el.disabled = !esferaVale(D.esf[i], caja);
        el.setAttribute('aria-pressed', String(i === e.esf));
      });
    }
    todos('[data-mov]').forEach(function (el) {
      el.setAttribute('aria-pressed', String(Number(el.dataset.mov) === e.mov)); });
    todos('[data-caja]').forEach(function (el) {
      el.setAttribute('aria-pressed', String(Number(el.dataset.caja) === e.caja)); });
    todos('[data-brz]').forEach(function (el) {
      el.setAttribute('aria-pressed', String(Number(el.dataset.brz) === e.brz)); });
    pintaVariantes();
    pintaVisor();
    pintaSpecs();
    pintaPrecio();
  }

  function pintaMuestras() {
    todos('[data-brz] i').forEach(function (el, i) {
      var f = D.brz[i];
      el.style.background = dibujo(f.nombre, f.v[0].nom);
    });
  }

  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-mov],[data-caja],[data-esf],[data-brz],[data-var]');
    if (!b || b.disabled) return;
    var d = b.dataset;
    if (d.mov !== undefined) e.mov = Number(d.mov);
    else if (d.caja !== undefined) e.caja = Number(d.caja);
    else if (d.esf !== undefined) e.esf = Number(d.esf);
    else if (d.brz !== undefined) { e.brz = Number(d.brz); e.v = 0; }
    else e.v = Number(d.var);
    pinta();
  });

  pintaMuestras();
  pinta();
})();
