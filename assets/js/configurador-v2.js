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
  /* CON QUE OPCION DESPIERTA LA PAGINA
     Por defecto, la primera de cada eje. Pero un modelo puede decir otra
     cosa: el Lunar arranca con el acero macizo de tres eslabones porque
     asi lo quiso Oscar el 10/08/2026, y no con el mas barato, que era la
     regla anterior. Se declara en `inicio` dentro de piezas.json. */
  if (D.inicio && D.inicio.brz) {
    for (var q0 = 0; q0 < D.brz.length; q0++) {
      if (D.brz[q0].id === D.inicio.brz) { e.brz = q0; break; }
    }
    e.v = D.inicio.v || 0;
  }
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

  /* ---------- la MUESTRA del brazalete ----------
     Mientras no hay foto, el cuadrito va dibujado. En cuanto la hay, se
     RECORTA DE LA FOTO DE VERDAD, que para eso está: no hace falta
     fotografiar los cuadritos aparte.

     Se recorta la franja de `y=380` a `y=470`, en mitad de la mitad de
     arriba. NO la de junto a la caja, que era lo primero que probé: ahí
     el Bitácora tiene el eslabón de unión, que es una plancha lisa, y
     el cuadrito salía como un rectángulo de color plano sin nada que
     dijera «brazalete». A esta altura se ven los eslabones.

     En horizontal, de `x=430` a `x=570`: bien por dentro del borde. El
     brazalete se estrecha por el medio y los últimos píxeles del canto
     son transparentes; recortando al ras, el cuadrito saldría mordido.
     Con estos 140 px las cuatro fotos que hay hoy son opacas del todo.

     Los porcentajes no dependen del tamaño en pantalla, y por eso el
     mismo recorte vale para la banda de 92x24 y para el círculo de
     30x30. El 50 % horizontal sale solo: el recorte está centrado en
     x=500 sobre un lienzo de 1000, y cualquier recorte centrado cae
     en la mitad. */
  function fotoVar(v) {
    return (D.brazaletes || {})[v.foto || v.ref] || null;
  }
  function muestraBanda(v, familia) {
    var u = fotoVar(v);
    return u ? 'url(' + u + ') 50% 16.45%/714.29% 2666.67% no-repeat'
             : dibujo(familia, v.nom);
  }
  function muestraChip(v) {
    var u = fotoVar(v);
    return u ? 'url(' + u + ') 50% 14.6%/714.29% 1714.29% no-repeat' : null;
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
    var ej = (D.ejes || {}).brz || {};
    /* `compatNo` es la lista negra por caja (Óscar, 11/08/2026): el
       acero negro es exclusivo de la caja Negra PVD, así que los
       biseles normales lo vetan aquí. */
    var no = (ej.compatNo || {})[caja.ref];
    if (no && no.indexOf(v.ref) >= 0) return false;
    var c = ej.compat;
    if (!c || !c[caja.ref]) return true;
    return c[caja.ref].indexOf(v.ref) >= 0;
  }
  function libres(fam, caja) {
    return fam.v.filter(function (v) { return varVale(v, caja); });
  }
  function famVale(fam, caja) { return libres(fam, caja).length > 0; }

  /* Al cambiar de caja puede caducar el brazalete que estaba puesto: se
     cae a la primera variante que sí valga, y si la familia entera se
     queda sin opciones, a la primera familia que las tenga.

     Y el viaje de vuelta (Óscar, 11/08/2026): si una caja te echó el
     brazalete —la Negra PVD solo admite los negros— y vuelves a una
     caja donde el tuyo sí vale, se te devuelve el que tenías. Elegir
     un brazalete a mano borra ese recuerdo: entonces mandas tú. */
  var brzAntes = null;
  function ajustaBrz() {
    var caja = D.caj[e.caja], i, k;
    if (brzAntes && varVale(D.brz[brzAntes.brz].v[brzAntes.v], caja)) {
      e.brz = brzAntes.brz; e.v = brzAntes.v; brzAntes = null;
    }
    var antes = { brz: e.brz, v: e.v }, cambio = false;
    if (!famVale(D.brz[e.brz], caja)) {
      for (i = 0; i < D.brz.length; i++) {
        if (famVale(D.brz[i], caja)) { e.brz = i; e.v = 0; cambio = true; break; }
      }
    }
    var f = D.brz[e.brz];
    if (e.v >= f.v.length || !varVale(f.v[e.v], caja)) {
      for (k = 0; k < f.v.length; k++) {
        if (varVale(f.v[k], caja)) { e.v = k; cambio = true; break; }
      }
    }
    if (cambio && !brzAntes) brzAntes = antes;
  }
  /* Elegir brazalete a mano solo borra el recuerdo si el recordado
     estaba disponible: entonces fue una decisión de verdad. Si la caja
     lo tenía escondido —en la Negra PVD todo es negro a la fuerza—,
     el paseo por eslabones no cuenta como cambio de opinión (Óscar,
     11/08/2026: «bisel negro conlleva a que el color es plata»). */
  function sueltaBrz() {
    if (brzAntes && varVale(D.brz[brzAntes.brz].v[brzAntes.v], D.caj[e.caja])) {
      brzAntes = null;
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
    /* SIN FOTO NO SE ENSEÑA OTRO RELOJ.
       Antes, cuando faltaba la cabeza, se caía a una foto de reserva que
       era el Lunar. En la página del Lunar colaba; en la de cualquier
       otro reloj se estaba enseñando un modelo que no era el que se
       vende, con su nombre en la esfera y todo. Ahora la foto se
       esconde y queda el hueco con el aviso, que no engaña a nadie. */
    /* LA FOTO ENTERA MANDA SOBRE TODO
       Si existe la foto de ESTA configuración ya montada, se pone esa y
       no se compone nada: ni mitades de brazalete ni bandas dibujadas.
       Es lo que quita la junta, que era el motivo del cambio. */
    /* La foto PROPIA manda; `foto` es el préstamo de un gemelo para
       mientras tanto (Óscar, 11/08/2026): en cuanto llega la de verdad,
       entra sola sin tocar datos. */
    var entera = (D.completas || {})[refCab + '-' + p.v.ref] ||
      (D.completas || {})[refCab + '-' + (p.v.foto || p.v.ref)];

    var cab = entera || (D.cabezas || {})[refCab];
    var foto = $('[data-foto]');
    if (cab) { foto.src = cab; foto.hidden = false; }
    else { foto.removeAttribute('src'); foto.hidden = true; }
    $('[data-pendiente]').hidden = !!cab;
    var montaje = document.querySelector('[data-montaje]');
    montaje.classList.toggle('con-foto', !!cab);
    montaje.classList.toggle('sin-cabeza', !cab);
    montaje.classList.toggle('entera', !!entera);

    if (entera) {
      todos('[data-brz-img]').forEach(function (el) { el.hidden = true; });
      todos('[data-correa]').forEach(function (el) { el.hidden = true; });
      var av0 = $('[data-aviso]');
      if (av0) av0.hidden = true;
      return;
    }

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
  /* ============================================================
     EL BRAZALETE EN TRES PASOS: MATERIAL, CIERRE, COLOR
     ------------------------------------------------------------
     Óscar, 10/08/2026: fuera las cuadrículas con imagen. Se elige el
     material a palo seco, luego el cierre y por último el color, y
     solo aparece lo que existe para ESTE reloj: los botones salen de
     las anotaciones de piezas.json, no de una lista fija. Un paso con
     una sola opción no se pinta: no se pregunta lo que no se elige.
     ============================================================ */
  var MAT = D.brz.length > 1 && D.brz.every(function (f) { return f.mat; });

  /* EL DETALLE DEL CIERRE (Óscar, 10/08/2026): al elegir el cierre,
     aparece su foto como tarjeta sobre el visor. Se va sola en cuanto
     se toca cualquier otra cosa, y también al pulsarla. */
  var VER_CIERRE = false;

  /* CUATRO PASOS (Óscar, 10/08/2026): material → eslabones → color →
     cierre. Cada paso filtra al siguiente y un paso con una sola opción
     no se pinta. El estado real sigue siendo (familia, variante): estos
     ejes solo deciden cuál queda puesta. */
  function varActual() { var f = D.brz[e.brz]; return f.v[Math.min(e.v, f.v.length - 1)]; }
  function matActual() { return D.brz[e.brz].mat; }
  /* ¿La tarjeta del cierre salta sola al tocar el brazalete? En los
     materiales de `cierreSoloAlPulsar` no: hay que pulsar el cierre. */
  function autoCierre() {
    var no = ((D.ejes || {}).brz || {}).cierreSoloAlPulsar || [];
    return no.indexOf(matActual()) < 0;
  }
  /* Cada material recuerda lo último que tuvo puesto (Óscar, 11/08/2026):
     quien pasea por piel y goma y vuelve al acero recupera SU acero, con
     su foto, y no la primera variante de la lista. */
  var ultimoDelMat = {};
  function tieneFoto(v) {
    var p = piezas();
    var refCab = D.codigo + '-' + p.caja.ref + (p.esf ? '-' + p.esf.ref : '');
    return !!((D.completas || {})[refCab + '-' + v.ref] ||
      (D.completas || {})[refCab + '-' + (v.foto || v.ref)]);
  }
  function candidatas(mat, esl, eti, cier) {
    /* La caja también corta aquí (Óscar, 11/08/2026): con la Negra PVD
       solo van los brazaletes negros de acero. `compat` decide. */
    var caja = D.caj[e.caja];
    var out = [];
    D.brz.forEach(function (f, fi) {
      if (f.mat !== mat) return;
      f.v.forEach(function (v, vi) {
        if (!varVale(v, caja)) return;
        if (esl !== null && (v.esl || '') !== esl) return;
        if (eti !== null && v.eti !== eti) return;
        if (cier !== null && v.cier !== cier) return;
        out.push({ fi: fi, vi: vi, v: v });
      });
    });
    return out;
  }
  function pon(x) { e.brz = x.fi; e.v = x.vi; }
  function unicos(lista, campo) {
    var u = [];
    lista.forEach(function (x) {
      var val = campo === 'esl' ? (x.v.esl || '') : x.v[campo];
      if (u.indexOf(val) < 0) u.push(val);
    });
    return u;
  }
  /* Al cambiar un paso se conserva lo elegido en los de abajo si sigue
     existiendo: quien tenía «Negro» y cambia de eslabones no debe perder
     su color porque sí. */
  function eligeMat(m) {
    var rec = ultimoDelMat[m];
    if (rec && D.brz[rec.brz] && D.brz[rec.brz].mat === m &&
        rec.v < D.brz[rec.brz].v.length &&
        varVale(D.brz[rec.brz].v[rec.v], D.caj[e.caja])) {
      e.brz = rec.brz; e.v = rec.v; return;
    }
    var v0 = varActual();
    var c = candidatas(m, v0.esl || '', v0.eti, null);
    if (!c.length) c = candidatas(m, null, v0.eti, null);
    if (!c.length) c = candidatas(m, null, null, null);
    /* A igualdad de todo, mejor la variante que ya tiene su foto hecha. */
    var cFoto = c.filter(function (x) { return tieneFoto(x.v); });
    pon(cFoto[0] || c[0]);
  }
  /* Entre las candidatas que quedan, manda este orden: cierre heredado
     CON foto hecha, cualquiera con foto, cierre heredado, la primera.
     La foto real pesa más que un cierre que el cliente no eligió. */
  function laMejor(c, cier) {
    var f;
    f = c.filter(function (x) { return x.v.cier === cier && tieneFoto(x.v); });
    if (f.length) return f[0];
    f = c.filter(function (x) { return tieneFoto(x.v); });
    if (f.length) return f[0];
    f = c.filter(function (x) { return x.v.cier === cier; });
    return f[0] || c[0];
  }
  function eligeEsl(esl) {
    var v0 = varActual();
    var c = candidatas(matActual(), esl, v0.eti, null);
    if (!c.length) c = candidatas(matActual(), esl, null, null);
    pon(laMejor(c, v0.cier));
  }
  function eligeEti(eti) {
    var v0 = varActual();
    var c = candidatas(matActual(), v0.esl || '', eti, null);
    if (!c.length) c = candidatas(matActual(), null, eti, null);
    pon(laMejor(c, v0.cier));
  }
  function eligeCier(cier) {
    var v0 = varActual();
    pon(candidatas(matActual(), v0.esl || '', v0.eti, cier)[0]);
  }

  function fichas(cont, lista, clave, puesta) {
    cont.innerHTML = lista.map(function (t) {
      return '<button class="cf-ficha" type="button" data-' + clave + '="' +
        String(t).replace(/"/g, '&quot;') + '"' +
        ' aria-pressed="' + (t === puesta) + '">' + t + '</button>';
    }).join('');
  }

  function pintaCierreDetalle() {
    var caja = $('[data-cierre-detalle]');
    if (!caja) return;
    /* Primero la foto de la familia; si no la hay, la del NOMBRE de la
       hebilla (Óscar, 11/08/2026): las pieles comparten hebillas. */
    var foto = (D.cierres || {})[D.brz[e.brz].id] ||
      (D.cierresNom || {})[varActual().cier];
    caja.hidden = !(VER_CIERRE && foto);
    if (caja.hidden) return;
    $('[data-cierre-img]').src = foto;
    /* El pie dice lo que de verdad se ve. Las dos mallas del Cero Cero
       llevan la MISMA hebilla y lo que las separa es el grosor, así que
       esa familia trae su propio pie y la tarjeta no miente. */
    var pieFam = (D.detallePies || {})[D.brz[e.brz].id];
    var nombreCier = varActual().cier;
    $('[data-cierre-pie]').textContent = pieFam ||
      (nombreCier ? 'El cierre · ' + nombreCier : 'El cierre');
  }

  function pintaMat() {
    var v0 = varActual();
    var caja = D.caj[e.caja];
    ultimoDelMat[matActual()] = { brz: e.brz, v: e.v };
    var mats = [];
    D.brz.forEach(function (f) {
      if (famVale(f, caja) && mats.indexOf(f.mat) < 0) mats.push(f.mat);
    });
    fichas($('[data-mats]'), mats, 'mat', matActual());
    $('[data-cuenta-mat]').textContent = mats.length > 1 ? mats.length + ' materiales' : 'uno solo';

    var esls = unicos(candidatas(matActual(), null, null, null), 'esl');
    /* De menos a más eslabones (Óscar, 11/08/2026): el 3 antes que el 5.
       Solo se reordenan entre sí los términos que empiezan por número;
       los de texto («Macizo») se quedan donde estaban. */
    var eslNums = esls.filter(function (t) { return /^\d/.test(t); })
      .sort(function (a, b) { return parseInt(a, 10) - parseInt(b, 10); });
    var eslK = 0;
    esls = esls.map(function (t) { return /^\d/.test(t) ? eslNums[eslK++] : t; });
    var ge = $('[data-grupo-esl]');
    ge.hidden = esls.length < 2;
    if (!ge.hidden) {
      fichas($('[data-esls]'), esls, 'esl', v0.esl || '');
      $('[data-cuenta-esl]').textContent = esls.length + ' opciones';
    }

    /* El color y el cierre se enseñan aunque solo quede uno (Óscar,
       11/08/2026): al irse el acero negro a la caja PVD, la página
       despertaba sin color ni cierre a la vista y parecía que faltaban.
       Con uno solo se pintan como dato, igual que el movimiento. */
    var pool = candidatas(matActual(), v0.esl || '', null, null);
    var etis = unicos(pool, 'eti');
    var gv = $('[data-grupo-var]');
    gv.hidden = etis.filter(Boolean).length < 1;
    if (!gv.hidden) {
      $('[data-variantes]').innerHTML = etis.map(function (eti) {
        var x = pool.filter(function (q) { return q.v.eti === eti; })[0].v;
        var estilo = 'background:' + (x.hex2
          ? 'linear-gradient(135deg,' + x.hex + ' 0 50%,' + x.hex2 + ' 50% 100%)'
          : (x.hex || '#c9cdd2'));
        if (x.bor) estilo += ';border:2px dashed ' + x.bor;
        return '<button class="cf-color" type="button" data-eti="' +
          eti.replace(/"/g, '&quot;') + '"' +
          ' aria-pressed="' + (eti === v0.eti) + '" title="' + eti + '"' +
          ' aria-label="' + eti + '" style="' + estilo + '"></button>';
      }).join('') + '<span class="cf-color-nombre">' + v0.eti + '</span>';
      $('[data-cuenta-var]').textContent =
        etis.length > 1 ? etis.length + ' colores' : 'uno solo';
    }

    var ciers = unicos(candidatas(matActual(), v0.esl || '', v0.eti, null), 'cier');
    var gc = $('[data-grupo-cier]');
    gc.hidden = ciers.filter(Boolean).length < 1;
    if (!gc.hidden) {
      fichas($('[data-ciers]'), ciers, 'cier', v0.cier);
      $('[data-cuenta-cier]').textContent =
        ciers.length > 1 ? ciers.length + ' opciones' : 'uno solo';
    }
  }

  function pintaVariantes() {
    if (MAT) { pintaMat(); return; }
    var p = piezas(), cont = $('[data-variantes]'), caja = D.caj[e.caja];
    if (!cont) return;
    var vale = libres(p.fam, caja);
    cont.innerHTML = p.fam.v.map(function (v, i) {
      if (!varVale(v, caja)) return '';
      /* El chip de la foto manda; el color inventado es el suplente. */
      var fondo = muestraChip(v);
      if (!fondo) {
        var t = tonos(v.nom);
        fondo = t.length > 1
          ? 'linear-gradient(135deg,' + t[0] + ' 0 50%,' + t[1] + ' 50% 100%)' : t[0];
      }
      return '<button class="cf-color" type="button" data-var="' + i + '"' +
        ' aria-pressed="' + (i === e.v) + '" title="' + v.nom + '"' +
        ' aria-label="' + v.nom + '" style="background:' + fondo + '"></button>';
    }).join('') + '<span class="cf-color-nombre" data-var-nombre></span>';
    $('[data-var-nombre]').textContent = p.v.nom;
    $('[data-cuenta-var]').textContent = vale.length + ' opciones';
    $('[data-grupo-var]').hidden = vale.length < 2;
    /* «desde 0,00 €» no se le dice a nadie: si no cuesta nada es porque ya
       viene con el reloj —la correa del Diver—, y eso se dice así. */
    var det = $('[data-detalle]');
    if (!det) return;
    var suelo = Math.min.apply(null, vale.map(function (x) { return x.c; }));
    det.textContent = nombreFam(p.fam) + ' · ' + vale.length +
      (vale.length === 1 ? ' versión' : ' versiones') +
      (suelo > 0 ? ' · desde ' + euros(suelo) : ' · ya viene con el reloj');
  }

  function pintaPrecio() {
    var p = piezas(), pvp = precio();
    $('[data-precio]').textContent = euros(pvp);
    /* La referencia ya no se enseña en la cabecera: es un código interno
       y el cliente no tiene por qué verlo (Óscar, 10/08/2026). Sigue
       viajando al carrito y a la ficha técnica, que es donde trabaja. */
    var ref_ = $('[data-ref]');
    if (ref_) ref_.textContent = referencia();
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
    pintaCierreDetalle();
  }

  function pintaMuestras() {
    todos('[data-brz] i').forEach(function (el, i) {
      var f = D.brz[i];
      el.style.background = muestraBanda(f.v[0], f.nombre + ' ' + nombreFam(f));
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

     Los costes de la hoja son BASE IMPONIBLE: el IVA se les suma. El
     embalaje y el envío NO: esos 9 € son lo que se paga en el mostrador,
     con el IVA ya dentro (Óscar, 10/08/2026).
     ============================================================ */
  var EMBALAJE = 2.00;       // con IVA dentro
  var ENVIO = 7.00;          // con IVA dentro

  /* EL FONDO DE GARANTÍA
     ------------------------------------------------------------
     No es un porcentaje plano del coste, y a propósito: lo que se
     rompe en un reloj es EL MOVIMIENTO, y los portes de ida y vuelta
     valen lo mismo tanto si el reloj cuesta 150 € como 560. Un tanto
     por ciento del total cobraría de más al caro y de menos al barato,
     que es justo al revés de lo que pasa.

     Una incidencia cuesta: el movimiento + 14 € de portes —ida y
     vuelta— + 5 € de piezas menores (junta, correa, pila).
     Se provisiona el 5 %: uno de cada veinte relojes vuelve.

     El 5 % es la parte que habrá que corregir con datos reales; las
     otras dos cifras son las de la casa. Con los movimientos de hoy
     sale entre 1,18 € el Cóctel de cuarzo y 4,32 € el Tortuga
     automático. */
  var GARANTIA_TASA = 0.05, GARANTIA_PORTES = 14.00, GARANTIA_PIEZAS = 5.00;
  function fondoGarantia(mov) {
    return (mov.coste + GARANTIA_PORTES + GARANTIA_PIEZAS) * GARANTIA_TASA;
  }
  var IVA = 0.21, IRPF = 0.20, SS = 0.05;
  var MIN_EUROS = 50, MIN_PORCENTAJE = 0.15;

  /* APAGADA DEL TODO, 12/08/2026, a petición de Óscar: «quítamela de
     momento, solo hazla invisible». No se ha borrado nada —la cuenta se
     sigue calculando igual—: basta con volver a poner este interruptor
     en true para que reaparezca con ?cuentas=1 como hasta ahora. */
  var CUENTAS_ENCENDIDAS = false;

  var VER_CUENTAS = CUENTAS_ENCENDIDAS && (function () {
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
  function sinIva(v) { return v / (1 + IVA); }
  function conIvaDe(v) { return v * (1 + IVA); }

  /* ------------------------------------------------------------
     EL PRECIO, Y SU SUELO

     El multiplicador manda casi siempre. Pero hay configuraciones
     —las más baratas del Trinchera y del Cóctel— en las que el
     ×2,7235 no llega a dejar los 50 € limpios que Óscar exige. En
     esas, y SOLO en esas, el precio sube al 9,90 siguiente que sí
     los deja. Son 296 de 10.948; las otras 10.652 no se enteran.

     Se despeja de las dos condiciones a la vez:
       50 € netos  →  PVP ≥ (50 / 0,75 + coste neto) × 1,21
       15 % del PVP →  PVP × (0,75/1,21 − 0,15) ≥ 0,75 × coste neto
     y se redondea HACIA ARRIBA, nunca hacia abajo: redondear al más
     cercano podría dejarlo otra vez por debajo del suelo.
     ------------------------------------------------------------ */
  function costeNeto(c, mov) {
    return c + sinIva(EMBALAJE) + sinIva(ENVIO) + fondoGarantia(mov);
  }

  function sube990(p) {
    var bajo = Math.floor((p - 9.90) / 10) * 10 + 9.90;
    return bajo >= p - 1e-9 ? bajo : bajo + 10;
  }

  function sueloPvp(cn) {
    var queda = 1 - IRPF - SS;                       // 0,75 de cada euro bruto
    var porEuros = (MIN_EUROS / queda + cn) * (1 + IVA);
    var margen = queda / (1 + IVA) - MIN_PORCENTAJE; // lo que gana el PVP por euro
    var porciento = margen > 0 ? queda * cn / margen : 0;
    return sube990(Math.max(porEuros, porciento));
  }

  function precio() {
    var c = coste();
    return Math.max(redondea(c * D.mult), sueloPvp(costeNeto(c, piezas().mov)));
  }

  function fila(etiqueta, valor, clase) {
    return '<tr' + (clase ? ' class="' + clase + '"' : '') + '><td>' + etiqueta +
           '</td><td>' + (typeof valor === 'string' ? valor : eu(valor)) + '</td></tr>';
  }

  /* ------------------------------------------------------------
     LAS TRES REGLAS QUE HACEN QUE ESTO CUADRE

     1. EL IVA DE LAS COMPRAS NO ES UN COSTE: se recupera. A Hacienda
        se le entrega el repercutido MENOS el soportado. Meterlo en el
        coste y además descontar el de la venta lo cuenta dos veces.

     2. LOS PRECIOS DE LA HOJA SON BASE IMPONIBLE. No llevan el IVA
        dentro: se les SUMA (Óscar, 10/08/2026). Por tanto el coste
        neto —el que de verdad pesa— es el de la hoja tal cual, y el
        desembolso real es ese × 1,21. Antes lo hacía al revés,
        dividiendo, y eso rebajaba el coste un 21 % que no existía.

     3. EL IRPF Y LA SS VAN SOBRE EL BENEFICIO, NO SOBRE LA VENTA. El
        modelo 130 es el 20 % del rendimiento NETO —ingresos menos
        gastos—, no de lo facturado. Aplicarlo a la venta se lleva 60 €
        donde debe llevarse 27.
     ------------------------------------------------------------ */
  function pintaCuentas() {
    var caja = $('[data-cuentas]');
    if (!caja) return;
    caja.hidden = !VER_CUENTAS;
    if (!VER_CUENTAS) return;

    var p = piezas();
    var lineas = [
      ['Movimiento', p.mov.coste],
      ['Caja', p.caja.coste],
      p.esf ? ['Esfera', p.esf.coste] : null,
      ['Brazalete', p.v.c]
    ].filter(Boolean);

    /* El fondo de garantía es una provisión nuestra, no una factura de
       nadie: no lleva IVA ni lo recupera. Entra en el coste neto y se
       queda fuera del cálculo del soportado. */
    var piezasCoste = coste();
    var garantia = fondoGarantia(p.mov);
    var embNeto = sinIva(EMBALAJE), envNeto = sinIva(ENVIO);
    var cn = costeNeto(piezasCoste, p.mov);
    var ivaSop = (conIvaDe(piezasCoste) - piezasCoste) +
                 (EMBALAJE - embNeto) + (ENVIO - envNeto);
    var conIva = cn + ivaSop;

    var porMult = redondea(piezasCoste * D.mult);
    var pvp = precio();
    var ivaRep = pvp - sinIva(pvp);
    var base = pvp - ivaRep;

    var bruto = base - cn;
    var irpf = bruto * IRPF, ss = bruto * SS;
    var neto = bruto - irpf - ss;

    var bienEuros = neto >= MIN_EUROS;
    var bienPorc = pvp > 0 && neto >= pvp * MIN_PORCENTAJE;
    var bien = bienEuros && bienPorc;

    caja.innerHTML =
      '<p class="cf-cuentas-t">Cuenta de explotación <i>solo tú · ?cuentas=0 para apagar</i></p>' +
      '<table><tbody>' +
      '<tr class="s"><td colspan="2">Costes</td></tr>' +
      lineas.map(function (x) { return fila(x[0], x[1]); }).join('') +
      fila('Embalaje · sin IVA', embNeto) +
      fila('Envío · sin IVA', envNeto) +
      fila('Fondo de garantía', garantia) +
      fila('Coste neto', cn, 'sub') +
      fila('+ IVA soportado 21 % · se recupera', ivaSop) +
      fila('Se desembolsa', conIva, 'sub') +

      '<tr class="s"><td colspan="2">Venta · ×' + String(D.mult).replace('.', ',') + '</td></tr>' +
      (pvp > porMult
        ? fila('Por multiplicador', porMult) +
          fila('Suelo · para llegar a ' + eu(MIN_EUROS) + ' limpios', pvp)
        : '') +
      fila('PVP', pvp, 'sub') +
      fila('IVA repercutido', -ivaRep) +
      fila('Base imponible', base, 'sub') +

      '<tr class="s"><td colspan="2">Beneficio</td></tr>' +
      fila('Base menos coste neto', bruto, 'sub') +
      fila('− IRPF 20 %', -irpf) +
      fila('− SS y otros 5 %', -ss) +
      fila('BENEFICIO NETO', neto, 'tot' + (bien ? '' : ' mal')) +
      fila('sobre el PVP', (Math.round(neto / pvp * 1000) / 10).toString().replace('.', ',') + ' %') +
      '<tr class="' + (bien ? 'ok' : 'mal') + '"><td colspan="2">' +
      (bien ? '✓' : '✗') + ' mínimo 50 € y 15 % del PVP (' + eu(pvp * MIN_PORCENTAJE) + ')' +
      '</td></tr>' +
      '</tbody></table>' +
      '<p class="cf-cuentas-ojo">A Hacienda, de IVA: <b>' + eu(ivaRep - ivaSop) + '</b>' +
      ' (repercutido menos soportado).<br>Sin mano de obra, por decisión tuya.</p>';
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
    /* La ficha larga (Óscar, 11/08/2026): cada pieza puede traer en
       `ficha` sus secciones de prosa y tablas, y aquí se pintan todas.
       El VK63 fue la primera; caja y brazalete vendrán detrás. */
    function secciones(lista) {
      (lista || []).forEach(function (s) {
        cuerpo += '<section><h3>' + s.h + '</h3>' +
          (s.p ? '<p class="cf-tec-prosa">' + s.p + '</p>' : '') +
          (s.t ? '<dl>' + s.t.map(function (r) {
            return '<dt>' + r[0] + '</dt><dd>' + r[1] + '</dd>';
          }).join('') + '</dl>' : '') + '</section>';
      });
    }
    secciones(p.mov.ficha);
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
    /* El acero se explica según el que esté puesto (Óscar, 11/08/2026):
       quien elige 904L lee sus ventajas sobre el 316 y sus pegas
       suavizadas, y quien elige 316 lee lo contrario. */
    secciones((D.fichaMat || {})[p.fam.mat]);
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
      precio: precio(),
      foto: $('[data-foto]').src
    });
    window.location.href = '/carrito.html';
  }

  document.addEventListener('click', function (ev) {
    if (ev.target.closest('[data-cierre-detalle]')) { VER_CIERRE = false; pinta(); return; }
    if (ev.target.closest('[data-abre-ficha]')) { abreTecnica(); return; }
    if (ev.target.closest('[data-reservar]')) { reservar(); return; }
    var b = ev.target.closest('[data-mov],[data-caja],[data-esf],[data-brz],[data-var],[data-sub],[data-mat],[data-esl],[data-eti],[data-cier]');
    if (!b || b.disabled) return;
    var d = b.dataset;
    if (d.sub !== undefined) { if (d.sub === 'diam') e.diam = d.valor; else e.color = d.valor; }
    else if (d.mov !== undefined) e.mov = Number(d.mov);
    else if (d.caja !== undefined) {
      e.caja = Number(d.caja);
      /* El bisel arrastra su esfera (Óscar, 10/08/2026): negro despierta
         con la negra y azul con la blanca. Después se puede cambiar
         entre las compatibles, esto solo decide con cuál se llega. */
      var par = (((D.ejes || {}).caja || {}).esfPar || {})[D.caj[e.caja].ref];
      if (par) for (var pi = 0; pi < D.esf.length; pi++) {
        if (D.esf[pi].ref === par) { e.esf = pi; break; }
      }
    }
    else if (d.esf !== undefined) e.esf = Number(d.esf);
    else if (d.brz !== undefined) { e.brz = Number(d.brz); e.v = 0; sueltaBrz(); }
    /* La tarjeta del cierre salta al tocar CUALQUIER paso del brazalete
       (Óscar, 11/08/2026): el paso del cierre casi nunca se pinta —al
       ser único se esconde— y la tarjeta no tenía por dónde salir. Solo
       aparece si la familia tiene su foto de cierre; si no, nada. */
    /* En piel y sintética la hebilla se ELIGE, y la tarjeta saltando a
       cada color era ruido (Óscar, 11/08/2026): ahí solo aparece si se
       pulsa el cierre. En los demás materiales el cierre es único y
       enseñarlo informa. La lista vive en los datos, no aquí. */
    else if (d.mat !== undefined) { eligeMat(d.mat); VER_CIERRE = autoCierre(); sueltaBrz(); }
    else if (d.esl !== undefined) { eligeEsl(d.esl); VER_CIERRE = autoCierre(); sueltaBrz(); }
    else if (d.eti !== undefined) { eligeEti(d.eti); VER_CIERRE = autoCierre(); sueltaBrz(); }
    else if (d.cier !== undefined) { eligeCier(d.cier); VER_CIERRE = true; sueltaBrz(); }
    else { e.v = Number(d.var); sueltaBrz(); }
    if (d.mov !== undefined || d.caja !== undefined || d.esf !== undefined ||
        d.brz !== undefined || d.var !== undefined || d.sub !== undefined) VER_CIERRE = false;
    pinta();
  });

  pintaMuestras();
  pinta();
})();
