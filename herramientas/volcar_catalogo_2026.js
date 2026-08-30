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

  /* ⚠️ EL MOTOR YA NO ESTÁ DENTRO DE LA FICHA (29/08/2026). La ficha se
     quedó con sus PIEZAS y el configurador se fue a
     `/assets/js/configurador-2026.js`, que comparten los diez modelos. Así
     que aquí hay que juntar las dos partes antes de ejecutar nada: primero
     lo que la ficha define en línea, y detrás el motor, igual que hace el
     navegador. Las fichas que todavía lo lleven dentro siguen valiendo:
     entonces no hay `<script src>` que buscar y el trozo de fuera va
     vacío. */
  const enLinea = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]).join('\n');
  /* El motor de precio va delante de todo: lo usan los dos, el que ya
     tiene el configurador fuera y el que todavía lo lleva dentro. */
  const precio = [...html.matchAll(/<script[^>]*\bsrc="(\/assets\/js\/precio-[^"?]+)/g)]
    .map((m) => fs.readFileSync(path.join(RAIZ, m[1].replace(/^\//, '')), 'utf8'))
    .join('\n');
  const suelto = [...html.matchAll(/<script[^>]*\bsrc="(\/assets\/js\/configurador-[^"?]+)/g)]
    .map((m) => fs.readFileSync(path.join(RAIZ, m[1].replace(/^\//, '')), 'utf8'))
    .join('\n');
  /* ⚠️ EL IIFE BUENO ES EL DEL MOTOR, no el primero que aparezca. La ficha
     lleva otro IIFE al final —el de la lupa— y buscando «(function () {»
     sobre todo el texto se cazaba ése: el exportador entraba en un ámbito
     donde las piezas no existen y saltaba «MOVS is not defined». Se busca
     en el trozo del motor si lo hay, y en la ficha solo cuando no. */
  const cuerpo = suelto || enLinea;
  const antes = precio + '\n' + (suelto ? enLinea + '\n' : '');

  /* En vez de buscarle el cierre al IIFE —que es traicionero, porque dentro
     hay más funciones que se cierran igual— se le mete al PRINCIPIO un
     exportador: una función que, cuando se la llama luego, devuelve las
     tripas ya rellenas. El hoisting hace el resto. */
  const i = cuerpo.indexOf('\n(function () {');
  if (i < 0) throw new Error('no encuentro el configurador de ' + fichero);

  const abre = '(function () {';
  let codigo;
  if (suelto) {
    /* ⚠️ AL MOTOR DE LA CASA NO SE LE INYECTA NADA. Él deja lo suyo en
       `window.__LAORA_MOTOR` —su puerta de servicio, escrita en el propio
       motor— y aquí solo se recoge.

       Antes se le metía un exportador al principio del IIFE, confiando en
       el hoisting. Con el motor dentro de la ficha funcionaba; al sacarlo
       a su fichero dejó de ver las funciones —los `var` sí, las `function`
       no— y el volcado se paraba con «costes is not defined». Adivinar
       dónde empieza el ámbito de un fichero ajeno es frágil por
       definición, y esto lo quita de en medio. */
    codigo = antes + cuerpo;
  } else {
    /* Con el motor todavía DENTRO de la ficha —el Trinchera— sigue el
       apaño de siempre: exportador al principio del IIFE, que ahí el
       hoisting sí funciona. Cuando el Trinchera pase al motor de la casa,
       esta rama se cae. */
    codigo = precio + '\n' + cuerpo.slice(i).replace(abre,
      abre + `\n  globalThis.__MOTOR = function () { return {${exporta}}; };\n`);
  }

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
        /* `getAttribute` devuelve cadena vacía, no el nodo: la ficha la
           compara con la URL que va a poner —«si ya es ésta, no la
           toques»— y devolver un nodo haría que nunca coincidiera. Faltaba,
           y la ficha se paró entera al leer el `src` de la foto del cierre:
           el volcador no falla con un aviso, revienta. */
        if (k === 'getAttribute') return () => '';
        if (k === 'closest' || k === 'querySelector') return () => nodo;
        if (k === 'querySelectorAll') return () => [];
        if (['appendChild', 'addEventListener', 'setAttribute', 'scrollIntoView',
             'insertBefore', 'removeChild', 'getBoundingClientRect', 'observe',
             'unobserve', 'focus', 'remove', 'removeAttribute',
             'replaceChildren', 'contains', 'matches'].includes(k)) return () => nodo;
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
  /* `new Image()` es la precarga de capas. Desde que el montaje por piezas
     es LA ficha —29/08/2026, se acabó el `?capas`— la precarga corre
     siempre, también aquí. Un objeto con `src` basta: no hay que bajar
     nada, solo dejar que el guion siga. */
  globalThis.Image = function () { return { set src(v) {}, get src() { return ''; } }; };
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
  /* El de la casa deja su puerta de servicio en `window`; el viejo, un
     `__MOTOR` global. Se prueba primero la puerta buena. */
  var puerta = globalThis.window && globalThis.window.__LAORA_MOTOR;
  if (puerta) { delete globalThis.window.__LAORA_MOTOR; return puerta; }
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
/* ============================================================
   LOS MODELOS GENERADOS
   ------------------------------------------------------------
   Una sola función para todos los que llevan el configurador de la casa
   y no tienen reglas propias: Precisa, Cóctel, Tortuga, Diver y los que
   vengan. No hay ninguna lista copiada aquí. Se le PREGUNTA a la ficha:
   qué pasos tiene —del contrato—, qué opciones hay en cada uno, y se
   recorren todas las combinaciones pidiéndole a ella el precio y la
   referencia.

   La primera versión de esto llevaba las opciones escritas a mano,
   copiadas de la ficha. Duró un día: el 19/08/2026 Óscar añadió el ante
   al Murph, la copia se quedó vieja y esas referencias no se podían
   vender porque el servidor no las conocía. No se repite.
   ============================================================ */
function generado(slug, nombre, clase, mm) {
  const L = motorDe(slug + '.html',
    'e, precio, referencia, normaliza, pinta, agua');
  const M = globalThis.window.__LAORA_ULTIMO;
  if (!M || !M.OPCIONES) return 0;

  /* Los pasos que de verdad tienen algo que elegir, en el orden del
     contrato. Los vacíos no multiplican nada. */
  const pasos = M.PASOS
    .map((p) => [p.id, Object.keys(M.OPCIONES[p.id] || {})])
    .filter(([, ops]) => ops.length);

  let n = 0;
  const anda = (i) => {
    if (i === pasos.length) {
      L.normaliza();
      const p = L.precio();
      /* Sin coste no hay precio: la ficha devuelve `null` y esa combinación
         no entra en el catálogo. No se vende lo que no se sabe cuánto
         cuesta. */
      if (p === null || p === undefined || !isFinite(p)) return;
      const dicho = pasos
        .map(([id, _]) => (M.OPCIONES[id][L.e[id]] || {}).nombre)
        .filter(Boolean);
      /* EL DIÁMETRO Y LAS HERMANAS. Si el modelo tiene paso de tamaño, el
         diámetro sale de lo elegido —el Trinchera vende 36 y 39— y de paso
         se apunta el MISMO reloj en las otras medidas, para poder cambiarlo
         desde el carrito sin volver a configurarlo. Lo hacía a mano la
         función del Trinchera; ahora vale para cualquiera que tenga el paso. */
      let diametro = mm, hermanas = null;
      const tam = pasos.find(([id]) => id === 'tamano');
      if (tam) {
        diametro = parseInt(L.e.tamano, 10) || mm;
        const guardado = L.e.tamano;
        hermanas = {};
        for (const v of tam[1]) {
          L.e.tamano = v;
          L.normaliza();
          hermanas[parseInt(v, 10) || v] = L.referencia();
        }
        L.e.tamano = guardado;
        L.normaliza();
      }
      n += anota(L.referencia(), p, nombre + ' ' + (dicho[dicho.length - 1] || ''),
        dicho.join(' · '), dicho[dicho.length - 1] || '',
        { modelo: clase, agua: L.agua() }, diametro, hermanas) ? 1 : 0;
      return;
    }
    const [id, ops] = pasos[i];
    for (const v of ops) { L.e[id] = v; anda(i + 1); }
  };
  anda(0);
  return n;
}

/* ============================================================
   LO-02 · TRINCHERA
   ------------------------------------------------------------
   AQUÍ HABÍA 235 LÍNEAS y se fueron el 29/08/2026 con el configurador
   viejo, por orden de Óscar: «quita todo lo que tengas en el configurador
   del trinchera». Recorrían a mano sus estilos, sus natos por medida, sus
   antes, sus pieles y sus vetos, y hacían falta porque la ficha llevaba
   dentro reglas que nadie más entendía.

   Ahora el Trinchera se genera como los otros ocho, así que lo recorre
   `generado()`, que le pregunta a la ficha en vez de tener una copia de
   sus listas.
   ============================================================ */
/* ============================================================
   LO-03 · LUNAR
   El único que necesita el manifiesto: de él salen las reglas de
   qué correa encaja con qué cabeza.
   ============================================================ */
function lunar() {
  /* EL LUNAR, DESDE CERO (Óscar, 26/08/2026): «el lunar lo vamos a hacer
     desde cero de nuevo» y «desde cero, por tanto todo lo anterior no nos
     vale». La ficha se ha reescrito entera con el mecanismo del Trinchera y
     hoy tiene UNA sola configuración —la base: esfera negra, bisel negro,
     agujas blancas, caja de acero, brazalete de acero y cristal mineral—
     todavía sin costes.

     LO QUE HABÍA AQUÍ Y SE VA. Desde el 25/08 este volcador copiaba tal cual
     las 1.944 referencias del Lunar viejo del catálogo anterior, porque
     faltaba el manifiesto de sus fotos. Eran referencias de un reloj que ya
     no se configura así, y el servidor las seguía dando por vendibles: quien
     llegara a una por un enlace guardado podía comprarla. Se han ido con el
     resto del Lunar viejo.

     SIN COSTES NO HAY REFERENCIAS. Mientras la ficha diga que no los tiene,
     el Lunar no aporta ni una: no se puede vender lo que no se sabe lo que
     cuesta. En cuanto Óscar dé los costes, esto enumera solo. */
  const L = motorDe('lunar.html',
    'MOVS, CAJAS, ESFERAS, BISELES, AGUJAS, CORREAS, CRISTALES, PAQUETES, ' +
    'COSTES_PUESTOS, costes, MM, e, precio, referencia, normaliza, pinta, agua, ' +
    'vetada, firma, sinVeto, AGUJAS_LIBRES');
  if (!L.COSTES_PUESTOS) {
    console.log('ℹ️  el Lunar no aporta referencias: se está rehaciendo desde cero y\n' +
                '    todavía no tiene costes. Las 1.944 del Lunar viejo ya no se copian.');
    return 0;
  }
  L.sinVeto(true);
  const e = L.e;
  let n = 0;
  /* SE RECORRE LA TABLA DE PAQUETES, no el producto de todas las casillas.
     El proveedor vende la caja montada con bisel, esfera y agujas dentro, y
     sólo en las combinaciones que él monta: cruzarlo todo daría referencias
     que nadie puede fabricar, y con un precio repartido a ojo.

     LAS AGUJAS SÍ SE CRUZAN (Óscar, 28/08/2026: «déjame todas las opciones
     puestas por defecto, luego te diré yo las combinaciones que no
     quiero»). La ficha ya las deja elegir libres, así que el catálogo tiene
     que enumerar lo mismo: si no, un cliente mete en el carrito una
     referencia que el servidor no conoce. Es el paquete el que pone el
     coste, y en la hoja de compra no cambia con el color de las agujas.

     Y LO QUE NO TIENE COSTE NO ENTRA. `costes()` devuelve null cuando la
     correa no tiene precio de compra: sin coste no hay precio, y sin precio
     no se vende. */
  for (const mov of Object.keys(L.MOVS))
  for (const p of L.PAQUETES)
  for (const agujas of (L.AGUJAS_LIBRES ? Object.keys(L.AGUJAS) : [p.agujas]))
  for (const correa of Object.keys(L.CORREAS))
  /* EL PESPUNTE, en las familias que lo eligen (29/08/2026). Es un paso más
     de la ficha, así que el catálogo tiene que enumerar lo mismo: si no, el
     cliente mete en el carrito una referencia que el servidor no conoce.
     En las que no lo eligen, una sola vuelta. */
  for (const pespunte of (L.M.CON_PESPUNTE_DE(correa) ? ['T', 'B'] : ['T']))
  /* EL AÑADIDO DE LA MARIPOSA (30/08/2026): donde la correa lo ofrece hay
     DOS referencias, sin y con. Se prueban los tres candidatos y
     `normaliza` descarta lo que ese estado no ofrece: si tras normalizar
     no es lo que se pedía, esa vuelta sobra. */
  for (const mariposa of ['SIN', 'MARP', 'MARN']) {
    e.mov = mov; e.caja = p.caja; e.cristal = p.cristal;
    e.esf = p.esf; e.bisel = p.bisel; e.agujas = agujas; e.correa = correa;
    e.pespunte = pespunte; e.mariposa = mariposa;
    L.normaliza();
    if (e.mariposa !== mariposa) continue;
    if (L.vetada(L.firma())) continue;
    if (L.costes() === null) continue;
    const caja = p.caja, cristal = p.cristal, c = p;
    n += anota(L.referencia(), L.precio(),
      'Lunar',
      L.CAJAS[caja].nombre + ' · esfera ' + L.ESFERAS[c.esf].nombre.toLowerCase() +
        ' · bisel ' + L.BISELES[c.bisel].nombre.toLowerCase() +
        ' · ' + L.CRISTALES[cristal].nombre.toLowerCase() +
        ' · ' + L.MOVS[mov].nombre +
        (e.mariposa !== 'SIN' ? ' · con mariposa de recambio' : ''),
      L.CORREAS[correa].nombre,
      { movimiento: L.MOVS[mov].tec,
        caja: 'Caja de ' + L.CAJAS[caja].mat + ' de ' + L.MM + ' mm, ' +
              L.CRISTALES[cristal].tec + '.',
        esfera: L.ESFERAS[c.esf].tec + ' Bisel: ' + L.BISELES[c.bisel].tec +
                '. Agujas: ' + L.AGUJAS[agujas].tec + '.',
        agua: L.agua() },
      /* El diámetro va al catálogo para que el carrito pueda avisar de si el
         reloj le va a la muñeca de quien compra, igual que hace el Trinchera
         con sus 36 y 39. */
      L.MM, null) ? 1 : 0;
  }
  return n;
}


/* ============================================================
   LO-04 · BITÁCORA
   La foto es la lista de validez: solo existe lo fotografiado.
   ============================================================ */
/* La Bitácora pasó al generador el 29/08/2026: su función a mano se
   fue con ella. Ahora la recorre `generado()`, que le pregunta a la ficha
   en vez de tener una copia de sus listas. */

/* ---------- a escribir ---------- */
const cuenta = {
  Precisa: generado('precisa', 'Precisa', 'Deportivo de brazalete integrado', 40),
  Trinchera: generado('trinchera', 'Trinchera', 'Reloj de campo'),
  Lunar: lunar(),
  'Bitácora': generado('bitacora', 'Bitácora', 'Deportivo de brazalete integrado', 40),
  'Cero Cero': generado('cero-cero', 'Cero Cero', 'Buceo', 40),
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
