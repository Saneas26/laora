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
  /* El Precisa no elige caja: se la impone el movimiento. Cuarzo → caja
     sólida, automático → caja de cristal. */
  var PORMOV = ((D.ejes || {}).caja || {}).porMov || null;
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

  /* La esfera elegida, o NINGUNA. Las cuatro del Precisa son del cuarzo:
     con el automático la esfera viene dentro del pack de la caja, así que
     no hay nada que elegir ni nada que cobrar. Si la que estaba puesta no
     entra en la caja nueva, se cae a la primera que sí. */
  function esfDe(caja) {
    if (!D.esf.length) return null;
    if (esferaVale(D.esf[e.esf], caja)) return D.esf[e.esf];
    for (var i = 0; i < D.esf.length; i++) {
      if (esferaVale(D.esf[i], caja)) { e.esf = i; return D.esf[i]; }
    }
    return null;
  }

  function piezas() {
    var f = D.brz[e.brz], caja = D.caj[e.caja];
    return {
      mov: D.mov[e.mov], caja: caja, esf: esfDe(caja),
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
    /* El brazalete solo entra en la referencia si se compra aparte. El
       del Precisa viene en el pack de la caja: no hay nada que pedir. */
    if (p.v.ref) seg.push(p.v.ref);
    return seg.join('-');
  }

  /* Una esfera puede no entrar en todas las cajas: en el Lunar la negra
     solo va con el bisel negro. La hoja lo dice en `cajas`. */
  function esferaVale(esf, caja) {
    if (!esf.cajas || /todas/i.test(esf.cajas)) return true;
    return esf.cajas.split(',').map(function (s) { return s.trim(); }).indexOf(caja.ref) >= 0;
  }

  /* ---------- EL METAL DEL BRAZALETE SIGUE AL DE LA CAJA ----------
     Regla de Óscar (09/08/2026) para el Bitácora: una caja de oro con un
     brazalete de plata no se vende, así que no se ofrece. `compat` dice,
     por cada caja, qué variantes de brazalete la acompañan. El modelo que
     no la traiga lo admite todo, como hasta ahora. */
  function varVale(v, caja) {
    var c = ((D.ejes || {}).brz || {}).compat;
    if (!c || !c[caja.ref]) return true;
    return c[caja.ref].indexOf(v.ref) >= 0;
  }
  function libres(fam, caja) {
    return fam.v.filter(function (v) { return varVale(v, caja); });
  }
  function famVale(fam, caja) { return libres(fam, caja).length > 0; }

  /* Al cambiar de caja puede caducar el brazalete que estaba puesto: se
     cae a la primera variante que sí valga, y si la familia entera se
     queda sin opciones, a la primera familia que las tenga. */
  function ajustaBrz() {
    var caja = D.caj[e.caja], i, k;
    if (!famVale(D.brz[e.brz], caja)) {
      for (i = 0; i < D.brz.length; i++) {
        if (famVale(D.brz[i], caja)) { e.brz = i; e.v = 0; break; }
      }
    }
    var f = D.brz[e.brz];
    if (e.v >= f.v.length || !varVale(f.v[e.v], caja)) {
      for (k = 0; k < f.v.length; k++) {
        if (varVale(f.v[k], caja)) { e.v = k; break; }
      }
    }
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

    /* El nombre del archivo no siempre es la referencia de pedido: el
       brazalete del Precisa viene con la caja y no tiene referencia, pero
       hay que fotografiarlo igual. Para esos, `foto`. */
    var img = (D.brazaletes || {})[p.v.foto || p.v.ref];
    var mitades = todos('[data-brz-img]');
    var bandas = todos('[data-correa]');
    if (img) {
      mitades.forEach(function (el, i) {
        el.src = img; el.hidden = false;
        /* El solape viene en píxeles de la FOTO (lienzo de 1000 de
           ancho), así que hay que pasarlo a píxeles de pantalla con la
           escala a la que se está viendo. Antes se multiplicaba por un
           240 fijo y el brazalete se movía cuatro píxeles: se quedaba
           colgado de la punta del asa, sin llegar a la caja. */
        var escala = (document.querySelector('[data-montaje]').clientWidth || 1000) / 1000;
        el.style.setProperty('--solape',
          (i === 0 ? 1 : -1) * (D.solape || 0) * escala + 'px');
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
    /* Ya NO hay acabados. Un modelo, y el cliente lo monta entero
       (Óscar, 10/08/2026): Alba, Levante, Cenit y Eclipse no existen. */
    var filas = [['Movimiento', p.mov.cal], ['Caja', p.caja.nombre]];
    var pack = ((D.ejes || {}).esf || {}).enPack;
    if (p.esf) filas.push(['Esfera', nombreEsf(p.esf)]);
    else if (D.esf.length && pack) filas.push(['Esfera', pack]);
    filas.push(['Brazalete', nombreFam(p.fam)]);
    $('[data-specs]').innerHTML = filas.map(function (f) {
      return '<dt>' + f[0] + '</dt><dd>' + f[1] + '</dd>';
    }).join('');
  }

  /* La versión que no va con la caja NO SE PINTA. Aquí sí se esconde, al
     revés que la esfera: «es frustrante ver algo que no puedes elegir»
     (Óscar, 10/08/2026). El índice del botón sigue siendo el de la lista
     entera, que es lo que lee el estado. */
  function pintaVariantes() {
    var p = piezas(), cont = $('[data-variantes]'), caja = D.caj[e.caja];
    var vale = libres(p.fam, caja);
    cont.innerHTML = p.fam.v.map(function (v, i) {
      if (!varVale(v, caja)) return '';
      var t = tonos(v.nom);
      var fondo = t.length > 1
        ? 'linear-gradient(135deg,' + t[0] + ' 0 50%,' + t[1] + ' 50% 100%)' : t[0];
      return '<button class="cf-color" type="button" data-var="' + i + '"' +
        ' aria-pressed="' + (i === e.v) + '" title="' + v.nom + '"' +
        ' aria-label="' + v.nom + '" style="background:' + fondo + '"></button>';
    }).join('') + '<span class="cf-color-nombre" data-var-nombre></span>';
    $('[data-var-nombre]').textContent = p.v.nom;
    $('[data-cuenta-var]').textContent = vale.length + ' opciones';
    $('[data-grupo-var]').hidden = vale.length < 2;
    /* «desde 0,00 €» no se le dice a nadie: si no cuesta nada es porque ya
       viene con el reloj —la correa del Diver—, y eso se dice así. */
    var suelo = Math.min.apply(null, vale.map(function (x) { return x.c; }));
    $('[data-detalle]').textContent = nombreFam(p.fam) + ' · ' + vale.length +
      (vale.length === 1 ? ' versión' : ' versiones') +
      (suelo > 0 ? ' · desde ' + euros(suelo) : ' · ya viene con el reloj');
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
    /* La caja va PRIMERO porque de ella cuelgan la esfera y el brazalete.
       Si la manda el movimiento, aquí es donde se pone. */
    if (PORMOV) {
      var pm = PORMOV[D.mov[e.mov].ref];
      if (pm) {
        for (var q = 0; q < D.caj.length; q++) if (D.caj[q].ref === pm.ref) e.caja = q;
        var bn = $('[data-caja-fijo]'), ba = $('[data-caja-apunte]');
        if (bn) bn.textContent = D.caj[e.caja].nombre;
        if (ba) ba.textContent = pm.apunte || '';
      }
    }
    /* La esfera que no entra en la caja elegida NO SE PINTA. Antes salía
       tachada, y Óscar lo zanjó el 10/08/2026: «es frustrante no poder
       elegir algo que ves». Y si no entra NINGUNA es que la esfera viene
       en el pack: se va el eje entero.

       Al esconder botones hay que rehacer la cuenta del rótulo, o diría
       «3 opciones» enseñando dos. */
    if (D.esf.length) {
      var caja = D.caj[e.caja];
      var hay = esfDe(caja) !== null;
      var ge = $('[data-grupo-esf]');
      if (ge) ge.hidden = !hay;
      var vivas = 0;
      todos('[data-esf]').forEach(function (el) {
        var i = Number(el.dataset.esf);
        var vale = esferaVale(D.esf[i], caja);
        el.hidden = !vale;
        if (vale) vivas++;
        el.setAttribute('aria-pressed', String(hay && i === e.esf));
      });
      var cuenta = ge && ge.querySelector('.cf-rotulo b');
      if (cuenta) cuenta.textContent = vivas + (vivas === 1 ? ' opción' : ' opciones');
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
    ajustaBrz();
    todos('[data-brz]').forEach(function (el) {
      var i = Number(el.dataset.brz);
      el.disabled = !famVale(D.brz[i], D.caj[e.caja]);
      el.setAttribute('aria-pressed', String(i === e.brz));
    });
    pintaVariantes();
    pintaVisor();
    pintaSpecs();
    pintaPrecio();
    pintaCuentas();
  }

  function pintaMuestras() {
    todos('[data-brz] i').forEach(function (el, i) {
      var f = D.brz[i];
      el.style.background = dibujo(f.nombre + ' ' + nombreFam(f), f.v[0].nom);
    });
  }

  /* ============================================================
     LA CUENTA DE EXPLOTACIÓN  ·  SOLO PARA ÓSCAR
     ------------------------------------------------------------
     Encargo del 10/08/2026, mientras se prueba el configurador. Es
     información INTERNA: enseña lo que nos cuesta cada pieza. Por eso
     NO sale por defecto.

     Se enciende una vez con  ?cuentas=1  y se queda encendida en ESE
     navegador; se apaga con ?cuentas=0. Así Óscar la ve siempre y un
     cliente no se la encuentra jamás.

     TRES NÚMEROS ESTÁN A CERO porque no los tengo: embalaje, envío y
     fondo de garantías. Salen marcados «por fijar» en pantalla. No me
     los invento: con cifras inventadas, la comprobación de que el
     beneficio llega a 50 € no valdría nada.
     ============================================================ */
  var EMBALAJE = 0;          // por fijar
  var ENVIO = 0;             // por fijar
  var GARANTIAS = 0;         // por fijar · fondo por reloj
  var IVA = 0.21, IRPF = 0.20, RETEN = 0.05;
  var MIN_EUROS = 50, MIN_PORCENTAJE = 0.15;

  var VER_CUENTAS = (function () {
    var m = /[?&]cuentas=([01])/.exec(location.search);
    try {
      if (m) {
        if (m[1] === '1') localStorage.setItem('laora.cuentas', '1');
        else localStorage.removeItem('laora.cuentas');
      }
      return localStorage.getItem('laora.cuentas') === '1';
    } catch (err) { return !!m && m[1] === '1'; }
  })();

  function eu(v) { return (Math.round(v * 100) / 100).toFixed(2).replace('.', ',') + ' €'; }

  function fila(etiqueta, valor, clase) {
    return '<tr' + (clase ? ' class="' + clase + '"' : '') + '><td>' + etiqueta +
           '</td><td>' + (typeof valor === 'string' ? valor : eu(valor)) + '</td></tr>';
  }

  function pintaCuentas() {
    var caja = $('[data-cuentas]');
    if (!caja) return;
    caja.hidden = !VER_CUENTAS;
    if (!VER_CUENTAS) return;

    var p = piezas();
    var piezasCoste = [
      ['Movimiento', p.mov.coste],
      ['Caja', p.caja.coste],
      p.esf ? ['Esfera', p.esf.coste] : null,
      ['Brazalete', p.v.c]
    ].filter(Boolean);

    var sub1 = coste();
    var ivaSop = sub1 * IVA;
    /* EL SUBTOTAL 2 ES EL PVP, con los impuestos DENTRO (Óscar,
       10/08/2026: «el IVA repercutido no se suma al subtotal 2, se
       resta»). Por eso el IVA se saca DIVIDIENDO entre 1,21, no
       multiplicando por 0,21: sobre 219,90 la diferencia son 8,02 € de
       más, que es el error clásico de aplicar el tipo al bruto. */
    var sub2 = sub1 * D.mult;                 // el multiplicador de la web
    var ivaRep = sub2 - sub2 / (1 + IVA);
    var total1 = sub2 - ivaRep;               // la base imponible
    var total2 = total1 - ivaSop;

    var ivaAPagar = ivaRep - ivaSop;
    /* «(pvp − el iva resultante)». El PVP es el Subtotal 2, NO el Total 1:
       el Total 1 ya lleva descontado el IVA repercutido, así que restarle
       otra vez el IVA a pagar lo contaría dos veces. Ese error daba 39,65 €
       de beneficio en el Lunar más barato cuando son 68,29. */
    var base = sub2 - ivaAPagar;
    var irpf = base * IRPF;
    var cinco = base * RETEN;
    var otros = EMBALAJE + ENVIO + GARANTIAS;
    var beneficio = base - irpf - cinco - sub1 - otros;

    var bienEuros = beneficio >= MIN_EUROS;
    var bienPorc = sub1 > 0 && beneficio >= sub1 * MIN_PORCENTAJE;
    var bien = bienEuros && bienPorc;

    var pvpBarra = redondea(sub2);            // lo que cobra la barra de abajo

    caja.innerHTML =
      '<p class="cf-cuentas-t">Cuenta de explotación <i>solo tú · ?cuentas=0 para apagar</i></p>' +
      '<table><tbody>' +
      '<tr class="s"><td colspan="2">Compra</td></tr>' +
      piezasCoste.map(function (x) { return fila(x[0], x[1]); }).join('') +
      fila('Subtotal 1', sub1, 'sub') +
      fila('IVA soportado', ivaSop) +
      fila('Total compra', sub1 + ivaSop, 'sub') +

      '<tr class="s"><td colspan="2">Venta · ×' + String(D.mult).replace('.', ',') + '</td></tr>' +
      fila('Subtotal 2 · el PVP', sub2, 'sub') +
      fila('IVA repercutido · dentro', -ivaRep) +
      fila('Total 1 · base', total1, 'sub') +
      fila('Total 2 · menos IVA sop.', total2) +

      '<tr class="s"><td colspan="2">Beneficio</td></tr>' +
      fila('IVA a pagar', ivaAPagar) +
      fila('PVP sin ese IVA', base, 'sub') +
      fila('− IRPF 20 %', -irpf) +
      fila('− 5 %', -cinco) +
      fila('− piezas', -sub1) +
      fila('− embalaje y envío', EMBALAJE + ENVIO ? -(EMBALAJE + ENVIO) : 'por fijar') +
      fila('− garantías', GARANTIAS ? -GARANTIAS : 'por fijar') +
      fila('BENEFICIO', beneficio, 'tot' + (bien ? '' : ' mal')) +
      '<tr class="' + (bien ? 'ok' : 'mal') + '"><td colspan="2">' +
      (bien ? '✓' : '✗') + ' mínimo 50 € y 15 % del coste (' + eu(sub1 * MIN_PORCENTAJE) + ')' +
      '</td></tr>' +
      '</tbody></table>' +
      /* Lo que queda por decidir está ahora en la COMPRA: los anuncios
         de AliExpress dicen «el precio incluye el IVA», así que el
         Subtotal 1 ya lo lleva dentro y sumarle otro 21 % lo cuenta dos
         veces. Se avisa, no se corrige solo: es decisión de Óscar. */
      '<p class="cf-cuentas-ojo">La barra cobra <b>' + eu(pvpBarra) + '</b> y el Subtotal 2 da <b>' +
      eu(sub2) + '</b>: cuadra.<br>Ojo: si el coste de las piezas ya lleva el IVA dentro,' +
      ' sumarle otro 21 % lo cuenta dos veces.</p>';
  }

  /* ============================================================
     LA FICHA TÉCNICA
     ------------------------------------------------------------
     Se rellena con la configuración que haya puesta en ese momento,
     no con datos escritos: si fueran fijos, quien montase el
     automático leería la ficha del cuarzo.

     Solo dice lo que la biblioteca de piezas SABE. El movimiento
     tiene su párrafo entero —viene de la pestaña Calibres—; de la
     caja y la esfera hoy solo hay el nombre, y no me invento ni el
     diámetro ni la estanqueidad.
     ============================================================ */
  function bloque(titulo, filas) {
    var f = filas.filter(function (x) { return x[1]; }).map(function (x) {
      return '<dt>' + x[0] + '</dt><dd>' + x[1] + '</dd>';
    }).join('');
    return f ? '<section><h3>' + titulo + '</h3><dl>' + f + '</dl></section>' : '';
  }

  function pintaTecnica() {
    var p = piezas();
    var cuerpo = '';
    cuerpo += '<section><h3>Movimiento</h3><p class="cf-tec-prosa">' +
      (p.mov.specs || p.mov.cal) + '</p></section>';
    cuerpo += bloque('Caja y esfera', [
      ['Caja', p.caja.nombre],
      ['Esfera', p.esf ? nombreEsf(p.esf) : ((D.ejes || {}).esf || {}).enPack],
      ['Modelo', D.nombre]
    ]);
    cuerpo += bloque('Brazalete o correa', [
      ['Familia', nombreFam(p.fam)],
      ['Versión', p.v.nom],
      ['Incluido', D.incluido || null]
    ]);
    $('[data-tec-cuerpo]').innerHTML = cuerpo;
    $('[data-tec-ref]').textContent = referencia();
    $('[data-tec-pie]').textContent =
      p.caja.nombre + (p.esf ? ' · ' + nombreEsf(p.esf) : '') + ' · ' + nombreFam(p.fam) +
      ' — ' + $('[data-precio]').textContent;
  }

  var manto = $('[data-manto]');
  function abreTecnica() { pintaTecnica(); manto.hidden = false; }
  function cierraTecnica() { manto.hidden = true; }
  if (manto) {
    manto.addEventListener('click', function (ev) {
      if (ev.target === manto || ev.target.closest('[data-cierra-tec]')) cierraTecnica();
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') cierraTecnica();
    });
  }

  /* ---------- reservar ----------
     La cesta vive en el navegador (`carrito.js`). Aquí solo se le
     entrega la línea, con la MISMA referencia que verá Óscar en el
     panel: si en la cesta pusiera otra cosa, no se sabría qué montar. */
  function reservar() {
    if (typeof laoraCarritoAnadir !== 'function') return;
    var p = piezas();
    laoraCarritoAnadir({
      ref: referencia(),
      nombre: D.nombre,
      detalle: p.caja.nombre + (p.esf ? ' · ' + nombreEsf(p.esf) : ''),
      correa: nombreFam(p.fam) + (p.v.nom ? ' · ' + p.v.nom : ''),
      precio: redondea(coste() * D.mult),
      foto: $('[data-foto]').src
    });
    window.location.href = '/carrito.html';
  }

  document.addEventListener('click', function (ev) {
    if (ev.target.closest('[data-abre-ficha]')) { abreTecnica(); return; }
    if (ev.target.closest('[data-reservar]')) { reservar(); return; }
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
