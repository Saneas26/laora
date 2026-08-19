/* ============================================================
   laOra · VOLCADOR DEL CATÁLOGO 2026
   ------------------------------------------------------------
   Escribe `assets/datos/catalogo-2026.json`: TODAS las referencias
   que se pueden pedir hoy —Precisa, Trinchera, Lunar y Bitácora—
   con su precio y con los textos que se congelan en el pedido.

   POR QUÉ EXISTE
     El servidor no puede fiarse del precio que manda el navegador:
     necesita su propia lista. Pero tampoco puede haber dos motores
     de precio, uno en la ficha y otro en la Edge Function, porque
     el día que no cuadren alguien cobra de menos.
     Aquí no se copia nada: se EJECUTA el motor que hay dentro de
     cada ficha, el mismo que ve el cliente, y se vuelca lo que
     dice. Una sola fuente de verdad.

   CUÁNDO HAY QUE VOLVER A PASARLO
     Siempre que cambie algo de un configurador: un coste, una
     correa, una foto que abre o cierra una combinación, una regla.
     Si no se pasa, la web enseñará el precio nuevo y el servidor
     rechazará la referencia con «ya no está a la venta».

       node herramientas/volcar_catalogo_2026.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const RAIZ = path.resolve(__dirname, '..');

/* ---------- el arnés ----------
   Saca el configurador de la ficha y lo ejecuta fuera del navegador.
   Las fichas solo tocan el DOM al pintar y piden sus datos por fetch,
   así que basta con un DOM de mentira y con darles el manifiesto a
   mano cuando lo necesiten. */
function motorDe(fichero, exporta) {
  const html = fs.readFileSync(path.join(RAIZ, fichero), 'utf8');
  /* El configurador es el IIFE grande de la ficha. En vez de buscarle
     el cierre —que es traicionero, porque dentro hay más funciones que
     se cierran igual— se le mete al PRINCIPIO un exportador: una
     función que, cuando se la llama luego, devuelve las tripas ya
     rellenas. El hoisting hace el resto. */
  const i = html.indexOf('\n(function () {');
  const fin = html.indexOf('</script>', i);
  if (i < 0 || fin < 0) throw new Error('no encuentro el configurador dentro de ' + fichero);

  const abre = '(function () {';
  let codigo = html.slice(i, fin);
  codigo = codigo.replace(abre,
    abre + `\n  globalThis.__MOTOR = function () { return {${exporta}}; };\n`);

  /* La ficha, fuera del navegador, no tiene ni DOM ni observadores.
     Nada de eso hace falta para calcular precios: se le pone un
     decorado que no estorba y que devuelve siempre algo.

     PERO EL DECORADO RECUERDA. `botones()` escribe en el `innerHTML`
     de cada grupo la lista de opciones que el cliente ve, con su
     `data-v` y con `disabled` en las imposibles. Guardando ese HTML
     por selector, el enumerador puede LEER lo que la ficha ofrece en
     vez de tener una copia de las listas: el 19/08/2026 la copia se
     quedó vieja —la ficha ya daba «Ante» en el Murph y el catálogo no
     lo sabía— y esas referencias se quedaron sin poder venderse. */
  const cajas = new Map();

  function hazNodo(sel) {
    const estado = { innerHTML: '', hidden: false, textContent: '', disabled: false };
    const nodo = new Proxy(estado, {
      get: (t, k) => {
        if (k in t) return t[k];
        if (k === 'classList') return { toggle() {}, add() {}, remove() {}, contains: () => false };
        if (k === 'dataset') return {};
        if (k === 'style') return {};
        if (k === 'closest' || k === 'querySelector') return () => nodo;
        if (k === 'querySelectorAll') return () => [];
        if (['appendChild', 'addEventListener', 'setAttribute', 'scrollIntoView',
             'insertBefore', 'removeChild', 'getBoundingClientRect', 'observe',
             'unobserve', 'focus', 'remove'].includes(k)) return () => nodo;
        return '';
      },
      set: (t, k, v) => { t[k] = v; return true; },
    });
    cajas.set(sel, estado);
    return nodo;
  }

  const nodos = new Map();
  const nodo = (sel) => {
    if (!nodos.has(sel)) nodos.set(sel, hazNodo(sel));
    return nodos.get(sel);
  };

  globalThis.document = { querySelector: nodo, querySelectorAll: () => [],
                          createElement: () => nodo('(creado)'), addEventListener: () => {},
                          documentElement: nodo('(html)'), body: nodo('(body)') };
  globalThis.window = { location: {}, innerHeight: 800, innerWidth: 1200,
                        addEventListener: () => {}, matchMedia: () => ({ matches: false, addEventListener() {} }) };
  globalThis.IntersectionObserver = function () { return { observe() {}, unobserve() {}, disconnect() {} }; };
  globalThis.ResizeObserver = globalThis.IntersectionObserver;
  globalThis.requestAnimationFrame = () => 0;
  globalThis.fetch = () => new Promise(() => {});   // lo que haga falta se le pasa a mano

  /* Las opciones que la ficha ACABA de pintar en un grupo, sin las
     tachadas: son las que el cliente puede pulsar de verdad. */
  globalThis.__OPCIONES = (grupo) => {
    const caja = cajas.get('[data-pv="' + grupo + '"]');
    if (!caja) return [];
    return [...String(caja.innerHTML).matchAll(/data-v="([^"]+)"([^>]*)>/g)]
      .filter((m) => !/\bdisabled\b/.test(m[2]))
      .map((m) => m[1]);
  };

  new Function(codigo)();
  return globalThis.__MOTOR();
}

/* Las cadenas se guardan una sola vez: hay casi dos mil referencias y
   muchísimas comparten los mismos textos. */
const textos = [];
const indice = new Map();
const t = (s) => {
  s = String(s);
  if (indice.has(s)) return indice.get(s);
  indice.set(s, textos.length);
  textos.push(s);
  return textos.length - 1;
};

const refs = {};
function anota(ref, precio, nombre, detalle, correa, ficha, mm, hermanas) {
  if (refs[ref]) return false;                 // ya la teníamos por otro camino
  const f = {};
  for (const k of Object.keys(ficha)) if (ficha[k]) f[k] = t(ficha[k]);
  refs[ref] = { p: Math.round(precio * 100) / 100, n: t(nombre), a: t(detalle), c: t(correa), f };
  /* El diámetro de la caja, en milímetros. Lo usa el carrito para
     avisar de si el reloj le va a la muñeca de quien compra. */
  if (mm) refs[ref].mm = mm;
  /* Y el MISMO reloj en las otras medidas que existan, para poder
     cambiarlo sin salir del carrito: {36: 'LO-02-…', 39: 'LO-02-…'}. */
  if (hermanas && Object.keys(hermanas).length > 1) refs[ref].otras = hermanas;
  return true;
}

/* ============================================================
   LO-01 · PRECISA
   ============================================================ */
function precisa() {
  const L = motorDe('precisa.html', 'MOVS, ESFERAS, e, precio, referencia');
  let n = 0;
  for (const mov of Object.keys(L.MOVS)) {
    for (const esf of Object.keys(L.ESFERAS)) {
      L.e.mov = mov; L.e.esf = esf;
      const m = L.MOVS[mov];
      n += anota(L.referencia(), L.precio(),
        'Precisa ' + L.ESFERAS[esf].nombre,
        'Acero 316L 40 mm, brazalete integrado, tapa ' +
          (m.tapa === 'C' ? 'de cristal' : 'sólida') + ' · Esfera ' +
          L.ESFERAS[esf].nombre + ' · ' + m.nombre,
        'Brazalete integrado de acero 316L',
        { movimiento: m.tec, esfera: L.ESFERAS[esf].tec, agua: m.agua }, 40) ? 1 : 0;
    }
  }
  return n;
}

/* ============================================================
   LO-02 · TRINCHERA
   ------------------------------------------------------------
   AQUÍ NO HAY NINGUNA LISTA COPIADA A MANO.
   La primera versión de esto llevaba las opciones escritas —las
   correas de cada caja, las esferas de cada estilo— copiadas de la
   ficha. Duró un día: el 19/08/2026 Óscar añadió el ante al Murph y
   a la caja negra, la copia se quedó vieja y esas referencias no se
   podían vender, porque el servidor no las conocía.

   Ahora se le PREGUNTA a la ficha. Se fija un estado, se llama a
   `pinta()` —que es lo que hace el navegador— y se leen los botones
   que ha dibujado, saltándose los tachados. Cambie lo que cambie
   arriba, esto lo sigue.
   ============================================================ */
function trinchera() {
  const L = motorDe('trinchera.html',
    'MOVS, CAJAS, ESFERAS, CORREAS, COLORES, NATOS, ANTES, PESPUNTES, CIERRES, MURPH_CORREA, ' +
    'e, precio, referencia, normaliza, agua, pinta, conCierre');
  let n = 0;

  /* Lo que la ficha ofrece AHORA MISMO en un grupo, con el estado
     puesto. `pinta()` primero: es quien dibuja los botones.
     Hay grupos que NO se dibujan —las cajas y los diámetros están
     escritos en el HTML y la ficha solo los tacha—, así que si no hay
     botones se cae a la tabla de datos, que para eso está. */
  const ofrece = (grupo, deReserva) => {
    L.pinta();
    const v = globalThis.__OPCIONES(grupo);
    return v.length ? v : (deReserva || []);
  };

  const pon = (cambios) => { Object.assign(L.e, cambios); L.normaliza(); };

  for (const estilo of ['K', 'M'])
  for (const mov of Object.keys(L.MOVS))
  for (const diam of ['36', '39']) {
    pon({ estilo, mov, diam });
    for (const caja of ofrece('caja', Object.keys(L.CAJAS))) {
      pon({ estilo, mov, diam, caja });
      if (L.e.caja !== caja) continue;          // esa caja no existe en este estilo

      for (const esf of ofrece('esf', [L.e.esf])) {
        pon({ estilo, mov, diam, caja, esf });
        if (L.e.esf !== esf) continue;

        for (const correa of ofrece('correa', [L.e.correa])) {
          pon({ estilo, mov, diam, caja, esf, correa });
          if (L.e.correa !== correa) continue;

          /* Las dimensiones que solo aparecen con ciertas correas: el
             color del nato+piel, el tono del ante, el pespunte de la
             piel del Murph y el cierre de cualquier piel. Se preguntan
             igual, y si el grupo no está pintado, se pasa de largo. */
          const colores   = correa === 'NATOP' ? ofrece('color', Object.keys(L.COLORES)) : [null];
          /* El nato pasó a ser UNO con cinco colores (Óscar, 19/08/2026), y
             comparte el grupo «color» del HTML con el nato+piel y el ante. */
          const natos     = correa === 'NATO' ? ofrece('color', Object.keys(L.NATOS || {})) : [null];
          const antes     = (correa === 'ANTE' && estilo === 'M') ? ofrece('ante', Object.keys(L.ANTES || {})) : [null];
          const pespuntes = (estilo === 'M' && L.MURPH_CORREA[correa]) ? ofrece('pesp', Object.keys(L.PESPUNTES || {})) : [null];

          for (const color of colores)
          for (const nato of natos)
          for (const ante of antes)
          for (const pesp of pespuntes) {
            pon({ estilo, mov, diam, caja, esf, correa });
            if (color) L.e.color = color;
            if (nato) L.e.nato = nato;
            if (ante) L.e.ante = ante;
            if (pesp) L.e.pesp = pesp;
            const cierres = L.conCierre() ? ofrece('cierre', Object.keys(L.CIERRES)) : [null];

            for (const cierre of cierres) {
              if (cierre) L.e.cierre = cierre;
              const s = L.e;
              const esBronce = s.caja === 'BR';
              n += anota(L.referencia(), L.precio(),
                'Trinchera ' + (esBronce ? 'Bronce' : (s.caja === 'TI' ? 'Titanio' :
                  (s.correa === 'PACK' ? 'Murph Pack' :
                    (s.esf === 'MA' || s.esf === 'MB' ? 'Murph' : 'Militar')))),
                L.CAJAS[s.caja].nombre + ' ' + s.diam + ' mm, tapa ' +
                  (s.tapa === 'C' ? 'de cristal' : 'sólida') + ' · ' + L.ESFERAS[s.esf].nombre +
                  ' · ' + L.MOVS[s.mov].nombre,
                s.correa === 'NATO'
                  ? 'Nato ' + L.NATOS[s.nato][0].toLowerCase() + ', hebilla clásica plateada'
                  : s.correa === 'NATOP'
                  ? 'Nato + piel genuina, ' + L.COLORES[s.color][0].toLowerCase() + ', hebilla clásica'
                  : (s.correa === 'ANTE' && s.estilo === 'M' && L.ANTES && L.ANTES[s.ante])
                  ? 'Ante ' + L.ANTES[s.ante][0].toLowerCase()
                  : L.CORREAS[s.correa].nombre,
                { movimiento: L.MOVS[s.mov].tec, caja: 'Caja de ' + L.CAJAS[s.caja].mat + '.',
                  esfera: L.ESFERAS[s.esf].tec,
                  correa: s.correa === 'NATO'
                    ? 'nato ' + L.NATOS[s.nato][0].toLowerCase() + ' de 20 mm con hebilla clásica plateada'
                    : L.CORREAS[s.correa].tec,
                  agua: L.agua() },
                Number(s.diam), hermanaDeDiametro(L, Object.assign({}, s))) ? 1 : 0;
            }
          }
        }
      }
    }
  }
  return n;
}

/* El Trinchera es el único que se hace en dos medidas. Aquí se
   averigua cómo se llama el MISMO reloj en cada una, para poder
   cambiarlo desde el carrito sin rehacer el pedido. */
function hermanaDeDiametro(L, base) {
  const guardado = Object.assign({}, L.e);
  const salida = {};
  for (const d of ['36', '39']) {
    Object.assign(L.e, base, { diam: d });
    L.normaliza();
    salida[d] = L.referencia();
  }
  Object.assign(L.e, guardado);
  return salida;
}

/* ============================================================
   LO-03 · LUNAR
   El único que necesita el manifiesto: de él salen las reglas de
   qué correa encaja con qué cabeza.
   ============================================================ */
function lunar() {
  const L = motorDe('lunar.html',
    'MOV, CAJAS, ESFERAS, AGUJAS, TAPAS, CORREAS, CIERRES, TIPOS, CATALOGO, e, ' +
    'precio, referencia, correaActual, pespuntesDe, esItaliana, tipoVale, colorVale, pespunteVale, ' +
    'setM: function (m) { M = m; }');
  L.setM(JSON.parse(fs.readFileSync(path.join(RAIZ, 'assets/img/lunar-config/manifest.json'), 'utf8')));

  const e = L.e;
  const AGUA = '10 ATM (100 metros): vale para nadar y ducharse, no para bucear con botella. ' +
               'La corona y los pulsadores no deben accionarse dentro del agua.';
  let n = 0;

  for (const k of Object.keys(L.CATALOGO)) {
    const [caja, esfera, agujas] = k.split('|');
    e.caja = caja; e.esfera = esfera; e.agujas = agujas;

    for (const tipo of Object.keys(L.TIPOS)) {
      if (!L.tipoVale(tipo)) continue;
      for (const color of Object.keys(L.TIPOS[tipo].colores)) {
        if (!L.colorVale(tipo, color)) continue;
        const ps = L.pespuntesDe(tipo, color);
        const pespuntes = ps ? Object.keys(ps).filter((p) => L.pespunteVale(tipo, color, p)) : [null];

        for (const pes of pespuntes) {
          e.tipo = tipo; e.color = color; if (pes) e.pespunte = pes;
          /* CON LA PIEL ITALIANA, EL `null` TAMBIÉN CUENTA.
             El cierre solo entra en la referencia si el cliente toca
             una hebilla; si no la toca, la ficha genera la referencia
             SIN cierre y cobra el de acero plateado. Esa referencia
             existe de verdad —es la que sale al entrar y elegir piel
             italiana sin más— y si no está aquí, el servidor rechaza
             el pedido con «esa referencia ya no está a la venta». */
          for (const cierre of (L.esItaliana() ? [null, ...Object.keys(L.CIERRES)] : [null])) {
            e.cierre = cierre;
            for (const tapa of [null, ...Object.keys(L.TAPAS)]) {
              e.tapa = tapa;
              n += anota(L.referencia(), L.precio(),
                'Lunar ' + L.ESFERAS[e.esfera].nombre,
                L.CAJAS[e.caja].nombre + ' · esfera ' + L.ESFERAS[e.esfera].nombre.toLowerCase() +
                  ' · agujas ' + L.AGUJAS[e.agujas].nombre.toLowerCase() +
                  (e.tapa ? ' · tapa ' + L.TAPAS[e.tapa].nombre.toLowerCase() : '') +
                  ' · ' + L.MOV.nombre,
                L.TIPOS[e.tipo].nombre + ' ' + L.TIPOS[e.tipo].colores[e.color].nombre.toLowerCase() +
                  (L.pespuntesDe() ? ' · pespunte ' + L.pespuntesDe()[e.pespunte].nombre.toLowerCase() : '') +
                  ((L.esItaliana() && e.cierre) ? ' · ' + L.CIERRES[e.cierre].nombre.toLowerCase() : ''),
                { movimiento: L.MOV.tec,
                  caja: L.CAJAS[e.caja].tec + ' Cristal mineral y tapa trasera roscada y sólida' +
                        (e.tapa ? ', ' + L.TAPAS[e.tapa].tec : '') + '.',
                  esfera: 'Lunar con ' + L.ESFERAS[e.esfera].tec + ' a las 4:30, agujas ' +
                          L.AGUJAS[e.agujas].nombre.toLowerCase() + ' con lume, y ' +
                          L.CORREAS[L.correaActual()].tec +
                          ((L.esItaliana() && e.cierre) ? ', con ' + L.CIERRES[e.cierre].tec : '') + '.',
                  agua: AGUA }, 39.7) ? 1 : 0;
            }
          }
        }
      }
    }
  }
  return n;
}

/* ============================================================
   LO-04 · BITÁCORA
   La foto es la lista de validez: solo existe lo fotografiado.
   ============================================================ */
function bitacora() {
  const L = motorDe('bitacora.html',
    'CAJAS, ESFERAS, BRZ, MOV, ORDEN_CAJAS, ORDEN_ESF, ORDEN_BRZ, e, precio, referencia, existe');
  let n = 0;
  for (const caja of L.ORDEN_CAJAS)
  for (const esf of L.ORDEN_ESF)
  for (const brz of L.ORDEN_BRZ) {
    if (!L.existe(caja, esf, brz)) continue;
    Object.assign(L.e, { caja, esf, brz });
    n += anota(L.referencia(), L.precio(),
      'Bitácora ' + L.ESFERAS[esf].nombre,
      'Caja ' + L.CAJAS[caja].nombre + ' 40 mm · Esfera ' + L.ESFERAS[esf].nombre + ' · ' + L.MOV.nombre,
      L.BRZ[brz].nombre + ', ' + L.BRZ[brz].cierre,
      { movimiento: L.MOV.tec, caja: 'Caja de ' + L.CAJAS[caja].mat + '.',
        correa: L.BRZ[brz].tec }, 40) ? 1 : 0;
  }
  return n;
}

/* ---------- a escribir ---------- */
const cuenta = {
  Precisa: precisa(), Trinchera: trinchera(), Lunar: lunar(), 'Bitácora': bitacora(),
};

const destino = path.join(RAIZ, 'assets/datos/catalogo-2026.json');
fs.writeFileSync(destino, JSON.stringify({
  generado: new Date().toISOString().slice(0, 10),
  aviso: 'GENERADO por herramientas/volcar_catalogo_2026.js desde las fichas. No editar a mano.',
  textos, refs,
}));

const total = Object.keys(refs).length;
const kb = (fs.statSync(destino).size / 1024).toFixed(0);
console.log(Object.entries(cuenta).map(([k, v]) => `${k}: ${v}`).join(' · '));
console.log(`TOTAL ${total} referencias · ${textos.length} textos · ${kb} KB`);
const precios = [...new Set(Object.values(refs).map((r) => r.p))].sort((a, b) => a - b);
console.log('precios: ' + precios.map((p) => p.toFixed(2).replace('.', ',')).join(' · ') + ' €');
