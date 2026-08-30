/* ============================================================
   laOra · AUDITORÍA DE LA REGLA Nº1
   ------------------------------------------------------------
   «Nunca puede haber ninguna referencia por debajo de 50 € o de
    un 15 % de beneficio neto, jamás. Si eso ocurre, que cambia
    todo.»  — Óscar, 29/08/2026

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
  /* ⚠️ EL SUELO YA NO VIVE EN LA FICHA (29/08/2026): se fue a
     `assets/js/precio-2026.js`, que comparten los diez modelos. Parchear
     solo el cuerpo del configurador dejaba la constante intacta, las dos
     pasadas salían idénticas y el auditor decía VERDE sin haber probado
     nada. Se parchea TODO el fuente ensamblado, y si no aparece por
     ningún lado se aborta: un verde que no ha medido nada es peor que no
     tener auditor. */
  s = s.replace('const cuerpo = suelto || enLinea;',
    "if (process.env.SUELO) { const R = /var (COMISION(?:_2026)?) = 0\\.\\d+/g;  // cualquier valor: desde el 30/08 la buena ES 0.05, y esto caza a quien la baje\n"
    + "    const n = (precio.match(R) || []).length + (enLinea.match(R) || []).length + (suelto.match(R) || []).length;\n"
    + "    if (!n) throw new Error('AUDITOR CIEGO: no encuentro la constante del suelo en ' + fichero);\n"
    + "    precio = precio.replace(R, (m, g) => 'var ' + g + ' = ' + process.env.SUELO);\n"
    + "    enLinea = enLinea.replace(R, (m, g) => 'var ' + g + ' = ' + process.env.SUELO);\n"
    + "    suelto = suelto.replace(R, (m, g) => 'var ' + g + ' = ' + process.env.SUELO); }\n"
    + "  const cuerpo = suelto || enLinea;");
  /* las tres piezas se declaran con const en el volcador: hay que poder
     reasignarlas para parchearlas. */
  s = s.replace('  const precio = [...html.matchAll', '  let precio = [...html.matchAll');
  s = s.replace('  const suelto = [...html.matchAll', '  let suelto = [...html.matchAll');
  s = s.replace('  const enLinea = [...html.matchAll', '  let enLinea = [...html.matchAll');

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
/* LA PRIMERA PASADA ES EL CATÁLOGO DE VERDAD, el que cobra el servidor.
   Hasta el 30/08 se forzaba al 2,5 % —era lo que valía la constante— y
   al subir el suelo al 5 % esa pasada se convirtió en una mentira: medía
   un catálogo que ya no existe y cantaba en rojo el arreglo ya hecho. */
const hoy = JSON.parse(fs.readFileSync(
  path.join(RAIZ, 'assets/datos/catalogo-2026.json'), 'utf8')).refs;
const duro = pasada(script, '0.05');

const distintas = Object.keys(hoy).length !== Object.keys(duro).length ||
  Object.keys(hoy).some((k) => !(k in duro));
if (distintas) {
  console.log('✗ el catálogo del disco y el recién volcado no enumeran lo mismo:');
  console.log('  hay que volcar antes de auditar (node herramientas/volcar_catalogo_2026.js).');
  process.exit(1);
}
const rotas = Object.keys(hoy).filter((k) => hoy[k].p < duro[k].p);
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
console.log('\n  ARREGLO: COMISION tiene que valer 0.05 en assets/js/precio-2026.js');
console.log('  que es donde vive el suelo desde el 29/08. Si alguna ficha');
console.log('  vieja todavía lo lleva dentro, también ahí. Después, volcar');
console.log('  el catálogo con herramientas/volcar_catalogo_2026.js.');
process.exit(1);
