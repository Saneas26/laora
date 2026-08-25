#!/usr/bin/env node
/*
 * Cuántas fotos necesita DE VERDAD el Trinchera.
 *
 * Le pregunta a la ficha todas las combinaciones que ofrece, calcula la
 * clave de foto de cada una y la compara con las que hay en SERIE. Lo
 * importante no es el número de huecos, sino cuántas IMÁGENES MADRE
 * hacen falta: una por caja × tipo de correa. El resto —los colores del
 * nato y del ante, los dos pespuntes y las cinco esferas— se derivan
 * con recolorear_*.py y trasplantar_esfera.py, sin generar nada.
 *
 * Uso: node herramientas/inventario_fotos_trinchera.js
 */
const RAIZ_FIX='/Users/oscar/Sites/laora';
process.chdir('/Users/oscar/Sites/laora');
const src = require('fs').readFileSync('herramientas/volcar_catalogo_2026.js','utf8');
// reutilizo motorDe recortando el módulo
const trozo0 = src.slice(src.indexOf('function motorDe'), src.indexOf('function anota'));
const trozo = trozo0.replace(/RAIZ/g, 'RAIZ_FIX');
eval(src.slice(src.indexOf('const fs'), src.indexOf('function motorDe')).replace(/RAIZ/g,'RAIZ_FIX') + trozo);

/* Se le pregunta a la ficha CÓMO SE LLAMA la foto de cada configuración
   —`claveSerie()`— y si la tiene —`serieFoto()`—, en vez de rehacer aquí la
   regla del nombre. Estaba copiada, y se quedó vieja: no sabía de los cuatro
   colores de la piel del khaki ni de que la piel y el ante comparten foto
   entre medidas, así que daba por perdidas fotos que estaban publicadas. */
const L = motorDe('trinchera.html',
  'MOVS, CAJAS, ESFERAS, CORREAS, natos, ANTES, PESPUNTES, CIERRES, MURPH_CORREA, ' +
  'PIELES_K, SERIE, claveSerie, serieFoto, e, normaliza, pinta');

const ofrece = (g, res) => { L.pinta(); const v = globalThis.__OPCIONES(g); return v.length ? v : (res||[]); };
const pon = (c) => { Object.assign(L.e, c); L.normaliza(); };

const claves = new Map();
for (const estilo of ['K','M'])
for (const diam of ['36','39']) {
  pon({estilo, mov:'Q', diam});
  for (const caja of ofrece('caja', Object.keys(L.CAJAS))) {
    pon({estilo, mov:'Q', diam, caja}); if (L.e.caja !== caja) continue;
    for (const esf of ofrece('esf', [L.e.esf])) {
      pon({estilo, mov:'Q', diam, caja, esf}); if (L.e.esf !== esf) continue;
      for (const correa of ofrece('correa', [L.e.correa])) {
        pon({estilo, mov:'Q', diam, caja, esf, correa}); if (L.e.correa !== correa) continue;
        const pespuntes = (estilo==='M' && L.MURPH_CORREA[correa]) ? Object.keys(L.PESPUNTES) : [null];
        const antes  = correa==='ANTE'  ? Object.keys(L.ANTES) : [null];
        const natos  = correa==='NATO'  ? Object.keys(L.natos()) : [null];
        const pieles = correa==='PIELO' ? Object.keys(L.PIELES_K) : [null];
        for (const p of pespuntes) for (const a of antes) for (const n of natos) for (const pk of pieles) {
          if (p) L.e.pesp = p; if (a) L.e.ante = a; if (n) L.e.nato = n; if (pk) L.e.pielk = pk;
          const k = L.claveSerie();
          if (k) claves.set(k, {caja, esf, correa, tiene: !!L.serieFoto()});
        }
      }
    }
  }
}
/* «Tiene foto» es lo que dice la ficha, no lo que hay en la tabla: una
   configuración de 39 con piel o con ante se resuelve con la foto de 36. */
const faltan = [...claves.keys()].filter(k => !claves.get(k).tiene);
console.log('COMBINACIONES VISUALES DEL TRINCHERA:', claves.size);
console.log('  con foto:', claves.size - faltan.length, '· sin foto:', faltan.length);
console.log();
const porCaja = {};
faltan.forEach(k => { const c = k.split('-')[1]; porCaja[c] = (porCaja[c]||0)+1; });
console.log('las que faltan, por caja:', porCaja);
const porDiam = {};
faltan.forEach(k => { const d = k.split('-')[0]; porDiam[d] = (porDiam[d]||0)+1; });
console.log('por diámetro:', porDiam);
const porCorrea = {};
faltan.forEach(k => { const c = claves.get(k).correa; porCorrea[c] = (porCorrea[c]||0)+1; });
console.log('por correa:', porCorrea);
/* La lista se escribe donde se ejecuta, o donde diga el primer argumento.
   Antes iba a una carpeta temporal de una sesión concreta, que ya no existe:
   la herramienta reventaba con ENOENT al terminar el trabajo bien hecho. */
require('fs').writeFileSync(process.argv[2] || 'faltan-trinchera.txt', faltan.sort().join('\n'));
