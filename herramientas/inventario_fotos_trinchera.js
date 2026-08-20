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

const L = motorDe('trinchera.html',
  'MOVS, CAJAS, ESFERAS, CORREAS, COLORES, NATOS, ANTES, PESPUNTES, CIERRES, MURPH_CORREA, ' +
  'MURPH_ANTE, SERIE, SERIE_CAJA, SERIE_ESF, SERIE_CORREA, NATO_FOTO, e, normaliza, pinta');

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
        const antes = correa==='ANTE' ? Object.keys(L.ANTES) : [null];
        const natos = correa==='NATO' ? Object.keys(L.NATOS) : [null];
        for (const p of pespuntes) for (const a of antes) for (const n of natos) {
          if (p) L.e.pesp = p; if (a) L.e.ante = a; if (n) L.e.nato = n;
          let k = diam + '-' + L.SERIE_CAJA[caja] + '-' + L.SERIE_ESF[esf] + '-' + L.SERIE_CORREA[correa];
          if (L.MURPH_CORREA[correa]) k += '-' + (L.e.pesp==='T'?'ptono':'pblanco');
          if (correa==='ANTE') k += '-' + (L.MURPH_ANTE[L.e.ante] || 'negro');
          if (correa==='NATO') k += '-' + L.NATO_FOTO[L.e.nato];
          claves.set(k, {caja, esf, correa});
        }
      }
    }
  }
}
const hay = Object.keys(L.SERIE);
const faltan = [...claves.keys()].filter(k => !hay.includes(k));
console.log('COMBINACIONES VISUALES DEL TRINCHERA:', claves.size);
console.log('  con foto:', hay.length, '· sin foto:', faltan.length);
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
require('fs').writeFileSync('/private/tmp/claude-501/-Users-oscar-Sites/354f8d8d-2f28-466c-8c36-41a8346c1298/scratchpad/faltan-trinchera.txt', faltan.sort().join('\n'));
