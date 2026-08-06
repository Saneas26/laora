/**
 * laOra · PVP_Claude — ingeniería de precios de todo el catálogo
 * ============================================================
 * Reconstruye la hoja «PVP_Claude» entera: la borra y la escribe de
 * nuevo. No toca «Catalogo laOra», que sigue siendo la que manda; esta
 * la lee con fórmulas, así que si allí cambia un coste, aquí cambia el
 * margen solo.
 *
 * CÓMO SE USA
 *   Extensiones → Apps Script, pegar, guardar y ▶ sobre `montarPVP`.
 *
 * LA REGLA, EN UNA LÍNEA
 *   PVP = base del modelo + escalón del movimiento + suplemento Eclipse
 *
 *   · la BASE la pone la caja y la clase del reloj, no el movimiento
 *   · el ESCALÓN es el mismo en los ocho modelos: si el 9015 son +220 €,
 *     son +220 € en todos. Así el cliente compara y le cuadra
 *   · el ECLIPSE no es un escalón de gama, es un acabado: suplemento fijo
 *
 * LOS TRES SUELOS que cumple cada referencia
 *   1. beneficio limpio >= 50 €
 *   2. beneficio limpio >= 22 % del PVP  (el reloj caro deja más dinero)
 *   3. aguanta que los materiales suban un 20 % sin bajar de 50 €
 *
 * Cambias un número de las tablas de arriba y se recalculan las 51.
 */

const HOJA_ORIGEN = 'Catalogo laOra';
const HOJA = 'PVP_Claude';

const BASES = [
  ['Trinchera', 189.9],
  ['Tortuga', 199.9],
  ['Cero Cero', 209.9],
  ['Bitácora', 219.9],
  ['Cóctel', 229.9],
  ['Lunar', 249.9],
  ['Precisa', 249.9],
  ['Diver', 249.9]
];

// movimiento, lo que cuesta, escalón de gama
const PASOS = [
  ['Ronda 515-3', 9.89, 20],
  ['Seiko/TMI VK63', 27.59, 40],
  ['Seiko/TMI VH31', 16.06, 40],
  ['Miyota 8215', 34.59, 40],
  ['Seagull ST2130', 47.39, 80],
  ['Seiko NH35A', 61.99, 120],
  ['PT5000', 56.31, 140],
  ['Seiko NE15', 65.23, 180],
  ['Miyota 9015', 106.69, 220],
  ['Seagull ST19', 219.69, 280]
];

const SUPL_ECLIPSE = 20;

// ref, modelo, acabado, movimiento (nombre unificado, el que usa PASOS)
const REFS = [
  ['LO-01_Lunar_A01', 'Lunar', 'Alba', 'Seiko/TMI VK63'],
  ['LO-01_Lunar_A02', 'Lunar', 'Alba', 'Seiko/TMI VK63'],
  ['LO-01_Lunar_A03', 'Lunar', 'Alba', 'Seiko/TMI VK63'],
  ['LO-01_Lunar_A04', 'Lunar', 'Alba', 'Seiko/TMI VK63'],
  ['LO-01_Lunar_A05', 'Lunar', 'Alba', 'Seiko/TMI VK63'],
  ['LO-01_Lunar_A06', 'Lunar', 'Alba', 'Seiko/TMI VK63'],
  ['LO-01_Lunar_C01', 'Lunar', 'Cenit', 'Seagull ST19'],
  ['LO-01_Lunar_E01', 'Lunar', 'Eclipse', 'Seiko/TMI VK63'],
  ['LO-02_CeroCero_A01', 'Cero Cero', 'Alba', 'Seiko/TMI VH31'],
  ['LO-02_CeroCero_L01', 'Cero Cero', 'Levante', 'Seiko NH35A'],
  ['LO-02_CeroCero_C01', 'Cero Cero', 'Cenit', 'Miyota 9015'],
  ['LO-02_CeroCero_E01-VH31', 'Cero Cero', 'Eclipse', 'Seiko/TMI VH31'],
  ['LO-02_CeroCero_E01-NH35', 'Cero Cero', 'Eclipse', 'Seiko NH35A'],
  ['LO-02_CeroCero_E01-9015', 'Cero Cero', 'Eclipse', 'Miyota 9015'],
  ['LO-04_Precisa_A01', 'Precisa', 'Alba', 'Seiko/TMI VH31'],
  ['LO-04_Precisa_L01', 'Precisa', 'Levante', 'Miyota 8215'],
  ['LO-04_Precisa_C01', 'Precisa', 'Cenit', 'Miyota 9015'],
  ['LO-04_Precisa_E01', 'Precisa', 'Eclipse', 'Miyota 9015'],
  ['LO-05_Trinchera_A01', 'Trinchera', 'Alba', 'Seiko/TMI VH31'],
  ['LO-05_Trinchera_A02', 'Trinchera', 'Alba', 'Seiko/TMI VH31'],
  ['LO-05_Trinchera_A03', 'Trinchera', 'Alba', 'Seiko/TMI VH31'],
  ['LO-05_Trinchera_A04', 'Trinchera', 'Alba', 'Seiko/TMI VH31'],
  ['LO-05_Trinchera_L01', 'Trinchera', 'Levante', 'Seagull ST2130'],
  ['LO-05_Trinchera_L02', 'Trinchera', 'Levante', 'Seagull ST2130'],
  ['LO-05_Trinchera_L03', 'Trinchera', 'Levante', 'Seagull ST2130'],
  ['LO-05_Trinchera_L04', 'Trinchera', 'Levante', 'Seagull ST2130'],
  ['LO-05_Trinchera_C01', 'Trinchera', 'Cenit', 'PT5000'],
  ['LO-05_Trinchera_C02', 'Trinchera', 'Cenit', 'PT5000'],
  ['LO-05_Trinchera_C03', 'Trinchera', 'Cenit', 'PT5000'],
  ['LO-05_Trinchera_C04', 'Trinchera', 'Cenit', 'PT5000'],
  ['LO-05_Trinchera_E01', 'Trinchera', 'Eclipse', 'Seiko/TMI VH31'],
  ['LO-05_Trinchera_E02', 'Trinchera', 'Eclipse', 'Seagull ST2130'],
  ['LO-05_Trinchera_E03', 'Trinchera', 'Eclipse', 'Miyota 9015'],
  ['LO-06_Diver_A01', 'Diver', 'Alba', 'Seiko/TMI VH31'],
  ['LO-06_Diver_C01', 'Diver', 'Cenit', 'Seiko NH35A'],
  ['LO-06_Diver_E01', 'Diver', 'Eclipse', 'PT5000'],
  ['LO-07_Bitacora_A01', 'Bitácora', 'Alba', 'Ronda 515-3'],
  ['LO-07_Bitacora_L01', 'Bitácora', 'Levante', 'Seiko NH35A'],
  ['LO-07_Bitacora_C01', 'Bitácora', 'Cenit', 'Miyota 9015'],
  ['LO-07_Bitacora_E01', 'Bitácora', 'Eclipse', 'Ronda 515-3'],
  ['LO-07_Bitacora_E01-OR', 'Bitácora', 'Eclipse', 'Ronda 515-3'],
  ['LO-07_Bitacora_E02', 'Bitácora', 'Eclipse', 'Seiko NH35A'],
  ['LO-07_Bitacora_E03', 'Bitácora', 'Eclipse', 'Miyota 9015'],
  ['LO-08_Tortuga_A01', 'Tortuga', 'Alba', 'Seiko/TMI VH31'],
  ['LO-08_Tortuga_L01', 'Tortuga', 'Levante', 'Seiko NH35A'],
  ['LO-08_Tortuga_C01', 'Tortuga', 'Cenit', 'Seiko NE15'],
  ['LO-08_Tortuga_E01', 'Tortuga', 'Eclipse', 'Seiko/TMI VH31'],
  ['LO-08_Tortuga_E02', 'Tortuga', 'Eclipse', 'Seiko NH35A'],
  ['LO-09_Coctel_A01', 'Cóctel', 'Alba', 'Seiko/TMI VH31'],
  ['LO-09_Coctel_L01', 'Cóctel', 'Levante', 'Seiko NH35A'],
  ['LO-09_Coctel_C01', 'Cóctel', 'Cenit', 'Miyota 9015']
];


function montarPVP() {
  const libro = SpreadsheetApp.getActive();
  let h = libro.getSheetByName(HOJA);
  if (h) libro.deleteSheet(h);
  h = libro.insertSheet(HOJA);

  const O = "'" + HOJA_ORIGEN + "'!";
  // columnas de «Catalogo laOra»: AD materiales, AE montaje, AF garantía,
  // AG logística, AH IVA deducible, AJ PVP actual
  const busca = (col) => 'VLOOKUP($A{F},' + O + '$A:$AJ,' + col + ',FALSE)';

  let f = 1;
  const pon = (fila, col, valores) => h.getRange(fila, col, 1, valores.length).setValues([valores]);
  const titulo = (texto) => { h.getRange(f, 1).setValue(texto)
      .setFontWeight('bold').setFontSize(12).setFontColor('#1c1d1b'); f += 1; };

  h.getRange(1, 1).setValue('PVP laOra · ingeniería de precios')
      .setFontWeight('bold').setFontSize(16);
  h.getRange(2, 1).setValue('PVP = base del modelo + escalón del movimiento + suplemento Eclipse. '
      + 'Los costes se leen de «' + HOJA_ORIGEN + '»: si allí cambian, aquí cambia el margen solo.')
      .setFontColor('#6c6c64');
  f = 4;

  titulo('PARÁMETROS');
  const params = [
    ['Colchón de proveedor', 0.20, 'lo que pueden subir los materiales sin romper el suelo de 50 €'],
    ['Beneficio mínimo (€)', 50, 'suelo en euros, pase lo que pase'],
    ['Beneficio mínimo (% del PVP)', 0.22, 'el reloj caro tiene que dejar más dinero, no el mismo'],
    ['Suplemento Eclipse (€)', SUPL_ECLIPSE, 'el negro integral es un acabado, no un escalón de gama'],
    ['Factor PVP → neto', null, '÷1,21 de IVA y ×0,75 de IRPF 20 % + SS 5 %'],
  ];
  const filaParam = {};
  params.forEach((p, i) => {
    const fi = f + i;
    h.getRange(fi, 1).setValue(p[0]);
    if (p[1] === null) h.getRange(fi, 2).setFormula('=0.75/1.21');
    else h.getRange(fi, 2).setValue(p[1]);
    h.getRange(fi, 3).setValue(p[2]).setFontColor('#6c6c64').setFontStyle('italic');
    filaParam[p[0]] = fi;
  });
  const P_COLCHON = 'B' + filaParam['Colchón de proveedor'];
  const P_EUR     = 'B' + filaParam['Beneficio mínimo (€)'];
  const P_PCT     = 'B' + filaParam['Beneficio mínimo (% del PVP)'];
  const P_ECL     = 'B' + filaParam['Suplemento Eclipse (€)'];
  const P_NETO    = 'B' + filaParam['Factor PVP → neto'];
  h.getRange(filaParam['Colchón de proveedor'], 2).setNumberFormat('0 %');
  h.getRange(filaParam['Beneficio mínimo (% del PVP)'], 2).setNumberFormat('0 %');
  h.getRange(filaParam['Factor PVP → neto'], 2).setNumberFormat('0.00000');
  f += params.length + 1;

  titulo('BASE POR MODELO — la pone la caja y la clase del reloj, no el movimiento');
  pon(f, 1, ['Modelo', 'Base']); h.getRange(f, 1, 1, 2).setFontWeight('bold'); f += 1;
  const B0 = f;
  h.getRange(f, 1, BASES.length, 2).setValues(BASES);
  h.getRange(f, 2, BASES.length, 1).setNumberFormat('#,##0.00 €');
  f += BASES.length; const B1 = f - 1; f += 1;

  titulo('ESCALÓN POR MOVIMIENTO — el mismo en los ocho modelos');
  pon(f, 1, ['Movimiento', 'Lo que cuesta', 'Escalón']);
  h.getRange(f, 1, 1, 3).setFontWeight('bold'); f += 1;
  const E0 = f;
  h.getRange(f, 1, PASOS.length, 3).setValues(PASOS);
  h.getRange(f, 2, PASOS.length, 2).setNumberFormat('#,##0.00 €');
  f += PASOS.length; const E1 = f - 1; f += 1;

  titulo('LAS ' + REFS.length + ' REFERENCIAS');
  const CAB = ['Referencia', 'Modelo', 'Acabado', 'Movimiento',
               'Materiales netos', 'Fijos', 'Coste hoy',
               'Base', 'Escalón', 'Eclipse',
               'PVP hoy', 'PVP propuesto', 'Diferencia',
               'Beneficio', 'Margen', 'Beneficio si suben 20 %',
               '¿Cumple?', 'Aguanta subida de'];
  pon(f, 1, CAB);
  h.getRange(f, 1, 1, CAB.length).setFontWeight('bold').setBackground('#f4f0e8')
      .setWrap(true).setVerticalAlignment('bottom');
  f += 1;
  const D0 = f;

  const filas = REFS.map(function (r, i) {
    const n = D0 + i;
    const b = (col) => busca(col).replace('{F}', n);
    return [
      r[0], r[1], r[2], r[3],
      '=' + b(30) + '-' + b(34),
      '=' + b(31) + '+' + b(32) + '+' + b(33),
      '=E' + n + '+F' + n,
      '=VLOOKUP($B' + n + ',$A$' + B0 + ':$B$' + B1 + ',2,FALSE)',
      '=VLOOKUP($D' + n + ',$A$' + E0 + ':$C$' + E1 + ',3,FALSE)',
      '=IF($C' + n + '="Eclipse",$' + P_ECL + ',0)',
      '=' + b(36),
      '=MAX(H' + n + '+I' + n + '+J' + n + ',K' + n + ')',
      '=L' + n + '-K' + n,
      '=L' + n + '*$' + P_NETO + '-G' + n,
      '=N' + n + '/L' + n,
      '=L' + n + '*$' + P_NETO + '-(E' + n + '*(1+$' + P_COLCHON + ')+F' + n + ')',
      '=IF(AND(N' + n + '>=MAX($' + P_EUR + ',$' + P_PCT + '*L' + n + '),P' + n + '>=$' + P_EUR + '),"Sí","REVISAR")',
      '=(L' + n + '*$' + P_NETO + '-F' + n + '-MAX($' + P_EUR + ',$' + P_PCT + '*L' + n + '))/E' + n + '-1',
    ];
  });
  h.getRange(D0, 1, filas.length, CAB.length).setValues(filas);
  const D1 = D0 + filas.length - 1;

  h.getRange(D0, 5, filas.length, 3).setNumberFormat('#,##0.00 €');
  h.getRange(D0, 8, filas.length, 6).setNumberFormat('#,##0.00 €');
  h.getRange(D0, 14, filas.length, 1).setNumberFormat('#,##0.00 €');
  h.getRange(D0, 16, filas.length, 1).setNumberFormat('#,##0.00 €');
  h.getRange(D0, 15, filas.length, 1).setNumberFormat('0 %');
  h.getRange(D0, 18, filas.length, 1).setNumberFormat('0 %');
  h.getRange(D0, 12, filas.length, 1).setFontWeight('bold');

  // el que no cumpla, en rojo
  const rojo = SpreadsheetApp.newConditionalFormatRule()
      .whenTextEqualTo('REVISAR')
      .setBackground('#f8d7d7').setFontColor('#7a1414')
      .setRanges([h.getRange(D0, 17, filas.length, 1)]).build();
  // el que va justo de colchón, en ámbar
  const ambar = SpreadsheetApp.newConditionalFormatRule()
      .whenNumberLessThan(0.10)
      .setBackground('#fdf0d5')
      .setRanges([h.getRange(D0, 18, filas.length, 1)]).build();
  h.setConditionalFormatRules([rojo, ambar]);

  // resumen al pie
  f = D1 + 2;
  titulo('RESUMEN');
  const R = [
    ['Referencias', '=COUNTA($A$' + D0 + ':$A$' + D1 + ')', ''],
    ['Precios distintos', '=COUNTA(UNIQUE($L$' + D0 + ':$L$' + D1 + '))', ''],
    ['Entrada de marca', '=MIN($L$' + D0 + ':$L$' + D1 + ')', ''],
    ['Tope de gama', '=MAX($L$' + D0 + ':$L$' + D1 + ')', ''],
    ['Subida media', '=AVERAGE($M$' + D0 + ':$M$' + D1 + ')', 'sobre el PVP de hoy'],
    ['Beneficio mínimo', '=MIN($N$' + D0 + ':$N$' + D1 + ')', ''],
    ['Beneficio mediano', '=MEDIAN($N$' + D0 + ':$N$' + D1 + ')', ''],
    ['Margen mediano', '=MEDIAN($O$' + D0 + ':$O$' + D1 + ')', ''],
    ['Referencias a revisar', '=COUNTIF($Q$' + D0 + ':$Q$' + D1 + ',"REVISAR")', 'tienen que ser 0'],
  ];
  R.forEach(function (r, i) {
    h.getRange(f + i, 1).setValue(r[0]);
    h.getRange(f + i, 2).setFormula(r[1]);
    h.getRange(f + i, 3).setValue(r[2]).setFontColor('#6c6c64').setFontStyle('italic');
  });
  h.getRange(f + 2, 2, 3, 1).setNumberFormat('#,##0.00 €');
  h.getRange(f + 5, 2, 2, 1).setNumberFormat('#,##0.00 €');
  h.getRange(f + 7, 2).setNumberFormat('0 %');

  h.setFrozenRows(D0 - 1);
  h.autoResizeColumns(1, CAB.length);
  h.getRange(1, 1, h.getMaxRows(), h.getMaxColumns()).setVerticalAlignment('middle');
  SpreadsheetApp.flush();
  Logger.log('PVP_Claude montada: ' + REFS.length + ' referencias, filas ' + D0 + '–' + D1);
}
