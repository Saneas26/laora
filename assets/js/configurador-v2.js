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

  var SUB = ((D.ejes || {}).caja || {}).sub || null;
  var e = { mov: 0, caja: 0, esf: 0, brz: 0, v: 0, diam: null, color: null };
  if (SUB) { e.diam = SUB[0].valores[0]; e.color = SUB[1].valores[0]; }

  /* El FONDO no se elige: lo decide el movimiento. Sólida con el cuarzo,
     cristal con el automático, porque un automático se enseña por detrás
     y un cuarzo no hay nada que enseñar (Óscar, 08/08/2026). */
  function fondo() {
    var f = ((D.ejes || {}).mov || {}).fondo;
    return f ? f[D.mov[e.mov].ref] : null;
  }
  function cajaDe(diam, color) {
    var fo = fondo();
    for (var i = 0; i < D.caj.length; i++) {
      var c = D.caj[i];
      if (c.diam === diam && c.color === color && c.fondo === fo) return i;
    }
    return -1;
  }
  /* Al cambiar de movimiento o de tamaño puede desaparecer el color que
     estaba puesto —el titanio solo existe con fondo sólido—: se cae al
     primero que sí exista, no se deja una caja imposible. */
  function ajustaCaja() {
    if (!SUB) return;
    var i = cajaDe(e.diam, e.color);
    if (i < 0) {
      var colores = SUB[1].valores;
      for (var k = 0; k < colores.length; k++) {
        var j = cajaDe(e.diam, colores[k]);
        if (j >= 0) { e.color = colores[k]; i = j; break; }
      }
    }
    if (i >= 0) e.caja = i;
  }

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

  /* ---------- EL MONTAJE DE DOS CAPAS ----------
     Detrás el brazalete, delante la cabeza. Las dos fotos comparten
     lienzo y escala: la cabeza es 1000×1000 y el brazalete 1000×2400,
     con el hueco de la caja justo en el centro.

     Las dos mitades del brazalete se meten `solape` dentro del hueco y
     la cabeza las tapa: sin eso queda una rendija de luz entre el
     último eslabón y la punta del asa, y se ve.

     Mientras falten fotos, cada capa cae por separado a lo de antes:
     la cabeza a la foto vieja con el aviso de «pendiente», y el
     brazalete a la banda dibujada. */
  function pintaVisor() {
    var p = piezas();
    var refCab = D.codigo + '-' + p.caja.ref + (p.esf ? '-' + p.esf.ref : '');
    var cab = (D.cabezas || {})[refCab];
    $('[data-foto]').src = cab || D.fotoDefecto;
    $('[data-pendiente]').hidden = !!cab;
    document.querySelector('[data-montaje]').classList.toggle('con-foto', !!cab);

    var img = (D.brazaletes || {})[p.v.ref];
    var mitades = todos('[data-brz-img]');
    var bandas = todos('[data-correa]');
    if (img) {
      mitades.forEach(function (el, i) {
        el.src = img; el.hidden = false;
        el.style.setProperty('--solape', (i === 0 ? 1 : -1) * (D.solape || 0) * 240 + 'px');
      });
      bandas.forEach(function (el) { el.hidden = true; });
    } else {
      mitades.forEach(function (el) { el.hidden = true; });
      var fondo = dibujo(p.fam.nombre, p.v.nom);
      bandas.forEach(function (el) { el.hidden = false; el.style.background = fondo; });
    }
    /* El aviso de «va dibujado» solo cuando lo está de verdad. */
    var av = $('[data-aviso]');
    if (av) av.hidden = !!img;
  }

  function nombreEsf(o) {
    var n = ((D.ejes || {}).esf || {}).nombres || {};
    return n[o.ref] || o.nombre;
  }
  function nombreFam(f) {
    var n = ((D.ejes || {}).brz || {}).nombres || {};
    return n[f.id] || f.nombre;
  }

  function pintaSpecs() {
    var p = piezas();
    var filas = [['Movimiento', p.mov.cal], ['Acabado', p.mov.acabado], ['Caja', p.caja.nombre]];
    if (p.esf) filas.push(['Esfera', nombreEsf(p.esf)]);
    filas.push(['Brazalete', nombreFam(p.fam)]);
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
    $('[data-detalle]').textContent = nombreFam(p.fam) + ' · ' + p.fam.v.length +
      (p.fam.v.length === 1 ? ' acabado' : ' acabados') + ' · desde ' +
      euros(Math.min.apply(null, p.fam.v.map(function (x) { return x.c; })));
  }

  function pintaPrecio() {
    var p = piezas(), c = coste(), pvp = redondea(c * D.mult);
    $('[data-precio]').textContent = euros(pvp);
    $('[data-ref]').textContent = referencia();
    $('[data-barra-nombre]').textContent = p.caja.nombre +
      (p.esf ? ' · ' + nombreEsf(p.esf) : '') + ' · ' + nombreFam(p.fam);
    $('[data-barra-var]').textContent = p.v.nom;
    /* El desglose de coste NO se pinta: es información interna y el
       cliente no tiene por qué ver lo que nos cuesta cada pieza
       (Óscar, 08/08/2026). Vive en el panel de pedidos. */
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
    if (SUB) {
      ajustaCaja();
      todos('[data-sub]').forEach(function (el) {
        var cl = el.dataset.sub, v = el.dataset.valor;
        var vale = cl === 'diam' ? cajaDe(v, e.color) >= 0 || SUB[1].valores.some(function (c) { return cajaDe(v, c) >= 0; })
                                 : cajaDe(e.diam, v) >= 0;
        el.disabled = !vale;
        el.setAttribute('aria-pressed', String(v === (cl === 'diam' ? e.diam : e.color)));
      });
    } else {
      todos('[data-caja]').forEach(function (el) {
        el.setAttribute('aria-pressed', String(Number(el.dataset.caja) === e.caja)); });
    }
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
      el.style.background = dibujo(f.nombre + ' ' + nombreFam(f), f.v[0].nom);
    });
  }

  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-mov],[data-caja],[data-esf],[data-brz],[data-var],[data-sub]');
    if (!b || b.disabled) return;
    var d = b.dataset;
    if (d.sub !== undefined) { if (d.sub === 'diam') e.diam = d.valor; else e.color = d.valor; }
    else if (d.mov !== undefined) e.mov = Number(d.mov);
    else if (d.caja !== undefined) e.caja = Number(d.caja);
    else if (d.esf !== undefined) e.esf = Number(d.esf);
    else if (d.brz !== undefined) { e.brz = Number(d.brz); e.v = 0; }
    else e.v = Number(d.var);
    pinta();
  });

  pintaMuestras();
  pinta();
})();
