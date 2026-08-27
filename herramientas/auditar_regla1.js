/* ============================================================
   laOra · AUDITORÍA DE LA REGLA Nº1
   ------------------------------------------------------------
   «Nunca puede haber ninguna referencia por debajo de 50 € o de
    un 15 % de beneficio neto, jamás. Si eso ocurre, que cambia
    todo.»  — Óscar, 27/08/2026

   CÓMO FUNCIONA
     No recalcula nada por su cuenta: eso es lo que salió mal el
     26/08, cuando un enumerador casero contó 336 referencias
     donde hay 1.506 porque se dejaba los colores de correa.
     Aquí se ejecuta DOS VECES el volcador oficial —el mismo que
     escribe el catálogo del servidor— cambiando solo el suelo:
     una con la comisión al 2,5 % y otra al 5 %. Las referencias
     cuyo precio cambia entre las dos pasadas son EXACTAMENTE las
     que rompen la regla si el cliente paga por Klarna.

       node herramientas/auditar_regla1.js

     Sale con código 1 si alguna referencia rompe la regla, para
     poder engancharlo a un hook o a CI.
   ============================================================ */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const RAIZ = path.resolve(__dirname, '..');
const ORIGEN = path.join(RAIZ, 'herramientas/volcar_catalogo_2026.js');

/* El volcador, con tres retoques: la raíz fija (se ejecuta desde /tmp),
   el destino por variable de entorno (para no pisar el catálogo bueno)
   y el suelo parcheado. Nada más: el motor de precios es el mismo. */
function prepara() {
  let s = fs.readFileSync(ORIGEN, 'utf8');
  s = s.replace(/^const RAIZ = .*$/m, `const RAIZ = ${JSON.stringify(RAIZ)};`);
  s = s.replace('codigo = codigo.replace(abre,',
    "if (process.env.SUELO) codigo = codigo.replace(/var COMISION(_2026)? = 0\\.025/, (m, g) => 'var COMISION' + (g || '') + ' = ' + process.env.SUELO);\n  codigo = codigo.replace(abre,");
  s = s.replace(/^const destino = path\.join\(RAIZ, 'assets\/datos\/catalogo-2026\.json'\);$/m,
    'const destino = process.env.DESTINO;');
  const f = path.join(os.tmpdir(), 'laora-auditar-regla1.js');
  fs.writeFileSync(f, s);
  return f;
}

function pasada(script, suelo) {
  const destino = path.join(os.tmpdir(), `laora-cat-${suelo}.json`);
  execFileSync(process.execPath, [script], {
    env: { ...process.env, SUELO: suelo, DESTINO: destino }, stdio: 'ignore',
  });
  return JSON.parse(fs.readFileSync(destino, 'utf8')).refs;
}

const script = prepara();
const hoy = pasada(script, '0.025');
const duro = pasada(script, '0.05');

const rotas = Object.keys(hoy).filter((k) => hoy[k].p !== duro[k].p);
const eur = (n) => n.toFixed(2).replace('.', ',') + ' €';

console.log(`Catálogo: ${Object.keys(hoy).length} referencias.`);
if (!rotas.length) {
  console.log('✅ REGLA Nº1 CUMPLIDA: ninguna referencia baja de 50 € limpios');
  console.log('   ni del 15 % neto, ni siquiera pagando por Klarna.');
  process.exit(0);
}

console.log(`❌ REGLA Nº1 ROTA en ${rotas.length} referencias.`);
console.log('   Con Klarna al 5 % no llegan a 50 € limpios o al 15 % neto.');
console.log('   Precio que tendrían que tener para cumplirla:\n');
const porSubida = {};
for (const k of rotas) {
  const s = (duro[k].p - hoy[k].p).toFixed(2);
  (porSubida[s] = porSubida[s] || []).push(k);
}
for (const [subida, refs] of Object.entries(porSubida).sort((a, b) => b[0] - a[0])) {
  console.log(`  +${eur(+subida)} · ${refs.length} referencias`);
  for (const k of refs.slice(0, 5)) console.log(`      ${k}  ${eur(hoy[k].p)} → ${eur(duro[k].p)}`);
  if (refs.length > 5) console.log(`      … y ${refs.length - 5} más`);
}
console.log('\n  ARREGLO: poner COMISION (COMISION_2026 en el JS) a 0.05 en');
console.log('  precisa.html, trinchera.html, lunar.html, bitacora.html y');
console.log('  assets/js/configurador-v2.js. Después, volcar el catálogo.');
process.exit(1);
