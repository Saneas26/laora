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
     decorado que no estorba y que devuelve siempre algo. */
  const nodo = new Proxy({}, {
    get: (t, k) => k === 'classList' ? { toggle() {}, add() {}, remove() {}, contains: () => false }
      : k === 'dataset' ? {} : k === 'style' ? {}
      : ['appendChild', 'addEventListener', 'setAttribute', 'closest', 'querySelector',
         'scrollIntoView', 'insertBefore', 'removeChild', 'getBoundingClientRect',
         'observe', 'unobserve', 'focus', 'remove'].includes(k) ? () => nodo : '',
    set: () => true,
  });
  globalThis.document = { querySelector: () => nodo, querySelectorAll: () => [],
                          createElement: () => nodo, addEventListener: () => {},
                          documentElement: nodo, body: nodo };
  globalThis.window = { location: {}, innerHeight: 800, innerWidth: 1200,
                        addEventListener: () => {}, matchMedia: () => ({ matches: false, addEventListener() {} }) };
  globalThis.IntersectionObserver = function () { return { observe() {}, unobserve() {}, disconnect() {} }; };
  globalThis.ResizeObserver = globalThis.IntersectionObserver;
  globalThis.requestAnimationFrame = () => 0;
  globalThis.fetch = () => new Promise(() => {});   // lo que haga falta se le pasa a mano

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
   AQUÍ MANDAN LOS BOTONES, NO `normaliza()`.
   La primera versión de esto recorría el espacio entero y dejaba
   que `normaliza()` arreglara lo imposible. Salían 64 referencias
   que la web NO ofrece: `normaliza()` es más permisivo que las
   listas de botones —no rechaza la piel verde en el khaki, por
   ejemplo— y eso habría dejado al servidor aceptar relojes que no
   se pueden pedir por ninguna pantalla.
   Así que se copian las listas de `pinta()`, que son las que ve el
   cliente, y se pasa cada combinación por `normaliza()` solo para
   que ponga la tapa y limpie el color.
   ============================================================ */
function trinchera() {
  const L = motorDe('trinchera.html',
    'MOVS, CAJAS, ESFERAS, CORREAS, COLORES, MURPH_CAJA, e, precio, referencia, normaliza, agua');
  let n = 0;

  /* Las mismas listas que pinta la ficha, en el mismo orden. */
  const correasDe = (estilo, caja) =>
    estilo === 'M' ? ['PIELV', 'PIELN', 'PIELM', 'ACERO', 'PACK']
    : caja === 'BR' ? ['ANTE']
    : caja === 'TI' ? ['ANTE', 'PIELO']
    : caja === 'NG' ? ['NATON', 'NATOP', 'PIELN']
    : ['NATO', 'NATOP', 'PIELN', 'PIELM', 'ACERO'];   // el PACK sale tachado

  const esferasDe = (estilo, caja) =>
    caja === 'BR' || (caja === 'TI' && estilo !== 'M') ? ['BRZ']
    : estilo === 'M' ? ['MA', 'MB']
    : ['KR', 'KB'];

  const cajasDe = (estilo) =>
    estilo === 'M' ? Object.keys(L.MURPH_CAJA) : Object.keys(L.CAJAS);

  for (const estilo of ['K', 'M'])
  for (const mov of Object.keys(L.MOVS))
  for (const diam of ['36', '39'])
  for (const caja of cajasDe(estilo))
  for (const esf of esferasDe(estilo, caja))
  for (const correa of correasDe(estilo, caja))
  for (const color of (correa === 'NATOP' ? Object.keys(L.COLORES) : ['NEG'])) {
    Object.assign(L.e, { estilo, mov, diam, caja, esf, correa, color });
    L.normaliza();   // pone la tapa que toca y limpia lo que sobre
    const s = L.e;

    /* Si `normaliza()` ha tenido que cambiar algo, es que esa
       combinación no existe: se descarta en vez de anotar otra. */
    if (s.caja !== caja || s.esf !== esf || s.correa !== correa) continue;

    const esBronce = s.caja === 'BR';
    n += anota(L.referencia(), L.precio(),
      'Trinchera ' + (esBronce ? 'Bronce' : (s.caja === 'TI' ? 'Titanio' :
        (s.correa === 'PACK' ? 'Murph Pack' :
          (s.esf === 'MA' || s.esf === 'MB' ? 'Murph' : 'Militar')))),
      L.CAJAS[s.caja].nombre + ' ' + s.diam + ' mm, tapa ' +
        (s.tapa === 'C' ? 'de cristal' : 'sólida') + ' · ' + L.ESFERAS[s.esf].nombre +
        ' · ' + L.MOVS[s.mov].nombre,
      s.correa === 'NATOP'
        ? 'Nato + piel genuina, ' + L.COLORES[s.color][0].toLowerCase() + ', hebilla clásica'
        : L.CORREAS[s.correa].nombre,
      { movimiento: L.MOVS[s.mov].tec, caja: 'Caja de ' + L.CAJAS[s.caja].mat + '.',
        esfera: L.ESFERAS[s.esf].tec, correa: L.CORREAS[s.correa].tec, agua: L.agua() },
      Number(s.diam), hermanaDeDiametro(L, { estilo, mov, caja, esf, correa, color })) ? 1 : 0;
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
          for (const cierre of (L.esItaliana() ? Object.keys(L.CIERRES) : [null])) {
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
