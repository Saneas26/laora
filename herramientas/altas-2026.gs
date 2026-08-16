/**
 * ALTAS DEL LIBRO «laOra 2026» — reconstrucción componente a componente.
 *
 * Cada tanda de componentes nuevos que da Óscar entra aquí como una
 * función ALTA_<fecha> que escribe en la pestaña Piezas del libro
 * (openById — nunca con el ratón, ver memoria sheet-laora-escribir).
 * La captura en bruto de cada tanda vive en herramientas/capturas/.
 *
 * Uso: pegar el archivo entero en script.google.com y ejecutar la
 * función de la tanda. Cada alta es idempotente: si su primer ID ya
 * existe, no hace nada.
 */

var LIBRO_2026 = '1PqPDhpxj2RVbFXYo1u4iZjKA398TKJmCr6YbYBR8zOY';

/**
 * Tanda 1 — 16/08/2026. Proveedor multipieza del Lunar
 * (FJ wrist watch store, anuncio 1005007892634303): 18 componentes
 * elegidos por Óscar (7 cajas montadas, 3 cajas vacías, 2 brazaletes,
 * 1 esfera, 5 juegos de agujas). Captura completa:
 * capturas/2026-08-16-1005007892634303.json
 */
function ALTA_2026_08_16() {
  var LINK = 'https://es.aliexpress.com/item/1005007892634303.html';
  var FECHA = new Date(2026, 7, 16);
  // Aviso que comparten las 18 piezas (del anuncio, no de cada SKU)
  var COMUN = 'Ø39,7 mm · asas 20 mm · compat. VK63 (mov. NO incluido) · acero sin grado declarado · cristal y estanqueidad SIN declarar · tapa trasera opaca roscada a elegir sin cambio de precio: lisa / grabado Lunar / grabado Footprint (va en la columna Tapa de Referencias) · precio con -50% del 16/08, reverificar antes de comprar · envío pedido 4,52 €, devol. 90 días';

  var filas = [
    // ID, Tipo, Modelos, Nombre interno, Nombre web, Variante(SKU), Coste, Link, TarifaComo, Recargo, Notas
    ['P-001', 'Caja montada', 'Lunar', 'Caja montada acero bisel plata, esfera negra crono, agujas naranja/blanco', 'Caja acero, esfera negra, detalles naranjas', 'NO.44', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-002', 'Caja montada', 'Lunar', 'Caja montada acero bisel azul, esfera blanca contadores azules, agujas plata', 'Caja acero, esfera blanca, contadores azules', 'NO.23', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-003', 'Caja montada', 'Lunar', 'Caja montada acero bisel negro, esfera negra, agujas plata', 'Caja acero, esfera negra', 'NO.25', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-004', 'Caja montada', 'Lunar', 'Caja montada acero, esfera negra índices y agujas doradas', 'Caja acero, esfera negra, detalles dorados', 'NO.26', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-005', 'Caja montada', 'Lunar', 'Caja montada acero, esfera verde, agujas plata', 'Caja acero, esfera verde', 'NO.27', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-006', 'Caja montada', 'Lunar', 'Caja montada acero bisel azul, esfera azul contadores plata', 'Caja acero, esfera azul', 'NO.29', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-007', 'Caja montada', 'Lunar', 'Caja montada acero bisel plata, esfera panda blanca contadores negros', 'Caja acero, esfera panda', 'NO.43', 34.59, LINK, '', '', 'Incluye caja+bisel+cristal+esfera+agujas+corona+pulsadores. ' + COMUN],
    ['P-008', 'Caja vacía', 'Lunar', 'Caja vacía acero bisel taquimétrico negro', 'Caja acero, bisel negro', 'NO.1', 23.79, LINK, '', '', 'SIN esfera ni agujas; incluye bisel+cristal+corona+pulsadores. ' + COMUN],
    ['P-009', 'Caja vacía', 'Lunar', 'Caja vacía acero bisel taquimétrico azul', 'Caja acero, bisel azul', 'NO.8', 26.39, LINK, '', '', 'SIN esfera ni agujas; incluye bisel+cristal+corona+pulsadores. ' + COMUN],
    ['P-010', 'Caja vacía', 'Lunar', 'Caja vacía negra PVD bisel taquimétrico negro', 'Caja negra, bisel negro', 'NO.13', 29.59, LINK, '', '', 'SIN esfera ni agujas; recubrimiento tipo PVD (observado en foto). ' + COMUN],
    ['P-011', 'Brazalete', 'Lunar', 'Brazalete acero plateado 3 eslabones tipo oyster, endlinks curvos, cierre desplegable', 'Brazalete de acero', 'NO.10', 19.69, LINK, '', '', 'Ancho 20 mm; largo sin declarar; cierre desplegable con pulsador (observado). ' + COMUN],
    ['P-012', 'Brazalete', 'Lunar', 'Brazalete negro PVD 3 eslabones, endlinks curvos, cierre desplegable', 'Brazalete de acero negro', 'NO.20', 26.39, LINK, '', '', 'Ancho 20 mm; largo sin declarar; recubrimiento tipo PVD (observado). ' + COMUN],
    ['P-013', 'Esfera', 'Lunar', 'Esfera panda blanca contadores negros, índices aplicados, fecha ~4:30', 'Esfera panda', 'NO.30', 7.69, LINK, '', '', 'ALERTA: ventana de fecha ~4:30 y el VK63 NO tiene fecha (el de fecha es el VK64) — confirmar con vendedor ANTES de comprar. Ø sin declarar. ' + COMUN],
    ['P-014', 'Agujas', 'Lunar', 'Juego agujas plateadas/blancas con lume (h+m+seg crono+3 subagujas)', 'Agujas plateadas', 'NO.38', 4.09, LINK, '', '', 'ALERTA: aparentemente idéntico a NO.41 (P-017) al mismo precio — preguntar al vendedor antes de pedir ambos. Lume verde. ' + COMUN],
    ['P-015', 'Agujas', 'Lunar', 'Juego agujas azules con lume + 3 subagujas blancas', 'Agujas azules', 'NO.39', 4.09, LINK, '', '', 'Lume verde. ' + COMUN],
    ['P-016', 'Agujas', 'Lunar', 'Juego agujas naranjas con lume (minutero naranja, seg central blanco punta naranja) + 3 subagujas naranjas', 'Agujas naranjas', 'NO.40', 4.09, LINK, '', '', 'Lume verde. ' + COMUN],
    ['P-017', 'Agujas', 'Lunar', 'Juego agujas plateadas/blancas con lume + 3 subagujas plateadas', 'Agujas plateadas (2)', 'NO.41', 4.09, LINK, '', '', 'ALERTA: aparentemente idéntico a NO.38 (P-014) al mismo precio — preguntar al vendedor antes de pedir ambos. Lume verde. ' + COMUN],
    ['P-018', 'Agujas', 'Lunar', 'Juego agujas doradas con lume + 3 subagujas doradas', 'Agujas doradas', 'NO.42', 4.09, LINK, '', '', 'Lume verde. ' + COMUN]
  ];

  altaPiezas_('ALTA_2026_08_16', filas, FECHA);
}

/**
 * Motor común de las altas: exige la pestaña Piezas VACÍA por delante
 * de la fila donde escribe (nada viejo se mezcla), es idempotente por
 * el primer ID de la tanda, y respeta el orden de columnas del libro:
 * A ID · B Tipo · C Modelos · D Nombre interno · E Nombre web ·
 * F Variantes · G Coste € · H Fecha coste · I Link anuncio ·
 * J Tarifa como · K Recargo PVP € · L Estado · M Notas
 */
function altaPiezas_(nombre, filas, fecha) {
  var ss = SpreadsheetApp.openById(LIBRO_2026);
  var sh = ss.getSheetByName('Piezas');
  if (!sh) throw new Error('No existe la pestaña Piezas en el libro.');

  var rango = sh.getRange('A2:F400').getValues();
  var ids = rango.map(function (r) { return String(r[0]); });
  var pos = ids.indexOf(String(filas[0][0]));
  if (pos !== -1) {
    // Mismo ID + misma variante = esta tanda ya entró. Mismo ID con
    // otra variante = datos VIEJOS en la pestaña (regla nada-viejo).
    if (String(rango[pos][5]) === String(filas[0][5])) {
      Logger.log(nombre + ': ya estaba dada de alta (' + filas[0][0] + '/' + filas[0][5] + '). No se toca nada.');
      return;
    }
    throw new Error('La pestaña Piezas tiene datos VIEJOS (el ' + filas[0][0] + ' que hay no es de esta tanda). Ejecuta EMPEZAR_DE_CERO y repite.');
  }
  // Primera fila libre de la columna A
  var fila = 2;
  while (fila - 2 < ids.length && ids[fila - 2] !== '') fila++;

  var datos = filas.map(function (f) {
    return [f[0], f[1], f[2], f[3], f[4], f[5], f[6], fecha, f[7], f[8], f[9], 'Activa', f[10]];
  });
  sh.getRange(fila, 1, datos.length, 13).setValues(datos);
  sh.getRange(fila, 7, datos.length, 1).setNumberFormat('#,##0.00 €');
  sh.getRange(fila, 8, datos.length, 1).setNumberFormat('dd/mm/yyyy');
  Logger.log(nombre + ': ' + datos.length + ' piezas dadas de alta (filas ' + fila + '–' + (fila + datos.length - 1) + ').');
}
