/* ============================================================
   laOra · LOS PRECIOS DE LA COLECCIÓN, AL DÍA
   ------------------------------------------------------------
   Las tarjetas de `coleccion.html` llevan el precio escrito dentro:
   en el `data-anadir` que va a la cesta, en el `data-var` de cada
   miniatura-variante y en la línea que lee el cliente.

   El que MANDA es el del catálogo del servidor: es el que cobra
   `crear-pedido`. Si la tarjeta dice 249,90 y el servidor cobra
   259,90, el cliente ve un precio y paga otro — y eso no es un
   descuadre estético, es una venta con sorpresa.

   Esto los pone todos de acuerdo. No decide ningún precio: los copia
   del catálogo, que a su vez sale del motor de cada ficha.

       node herramientas/sincronizar_precios.js

   Lo lanza solo el hook de git cuando cambia una ficha.
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const RAIZ = path.resolve(__dirname, '..');

const cat = JSON.parse(fs.readFileSync(path.join(RAIZ, 'assets/datos/catalogo-2026.json'), 'utf8'));
const p = path.join(RAIZ, 'coleccion.html');
let html = fs.readFileSync(p, 'utf8');

const eu = (n) => n.toFixed(2).replace('.', ',') + ' €';
let tocados = 0, sinCatalogo = [];

/* Un atributo con JSON dentro: se lee, se le corrige el precio y se
   vuelve a escribir igual que estaba. */
function arregla(attr, saca) {
  html = html.replace(new RegExp(attr + "='([^']+)'", 'g'), (todo, crudo) => {
    let d;
    try { d = JSON.parse(crudo.replace(/&#39;/g, "'").replace(/&amp;/g, '&')); }
    catch { return todo; }
    const dentro = saca(d);
    if (!dentro || !dentro.ref) return todo;
    const r = cat.refs[dentro.ref];
    if (!r) { sinCatalogo.push(dentro.ref); return todo; }
    if (Math.abs(Number(dentro.precio) - r.p) < 0.001) return todo;
    dentro.precio = r.p;
    tocados++;
    return attr + "='" + JSON.stringify(d).replace(/'/g, '&#39;') + "'";
  });
}

arregla('data-anadir', (d) => d);
arregla('data-var', (d) => d.anadir);

/* Y el precio que LEE el cliente, dentro de cada tarjeta: se busca el
   `data-anadir` de esa tarjeta y se copia su precio a la lista. */
html = html.replace(
  /(data-anadir='([^']+)'[\s\S]*?)/g, (m) => m);   // (se deja como está: el precio de la lista va aparte)

html = html.replace(/<article class="cv2-tarjeta[\s\S]*?<\/article>/g, (tarjeta) => {
  const m = tarjeta.match(/data-anadir='([^']+)'/);
  if (!m) return tarjeta;
  let d;
  try { d = JSON.parse(m[1].replace(/&#39;/g, "'").replace(/&amp;/g, '&')); } catch { return tarjeta; }
  const r = cat.refs[d.ref];
  if (!r) return tarjeta;
  tarjeta = tarjeta.replace(/(<li class="cv2-precio-lista">)[^<]*(<\/li>)/,
    (t, a, b) => {
      if (t.indexOf(eu(r.p)) >= 0) return t;
      tocados++;
      return a + eu(r.p) + b;
    });
  /* Y LA LÍNEA DE LOS PLAZOS, si la tarjeta la lleva (Óscar, 20/08/2026):
     un tercio del precio redondeado hacia arriba al céntimo, igual que
     la caja de Klarna de la ficha. Se recalcula con cada precio. */
  const plazo = eu(Math.ceil(r.p / 3 * 100) / 100);
  tarjeta = tarjeta.replace(/(<li class="cv2-plazos">)[^<]*(<\/li>)/,
    (t, a, b) => {
      if (t.indexOf(plazo) >= 0) return t;
      tocados++;
      return a + 'ó 3 plazos de ' + plazo + b;
    });
  return tarjeta;
});

fs.writeFileSync(p, html);
console.log(tocados
  ? `precios puestos al día en la colección: ${tocados}`
  : 'la colección ya estaba al día');
if (sinCatalogo.length) {
  console.log('⚠️  referencias que el catálogo no conoce (no se tocan): ' +
              [...new Set(sinCatalogo)].join(', '));
}
