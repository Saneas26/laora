/**
 * laOra · arreglar cuatro celdas de «Catalogo laOra»
 * ============================================================
 * Las cuatro las está corrigiendo hoy la web al vuelo, o filtrando.
 * Cuando este guion las deje bien en la hoja, la web las coge solas y
 * se puede borrar la tabla `CORRECCIONES` de `volcar_hoja.py`.
 *
 * CÓMO SE USA
 *   1. Abre el libro «Catalogo laOra».
 *   2. Extensiones → Apps Script.
 *   3. Pega esto, guarda y pulsa ▶ sobre `arreglarCatalogoLaOra`.
 *   4. Mira el registro (Ver → Registro de ejecución): dice celda por
 *      celda qué ha cambiado.
 *
 * No toca ninguna otra fila ni ninguna otra columna.
 */

const HOJA = 'Catalogo laOra';

// Columna A = Ref. El resto se busca por el título de la fila 1, así que
// da igual si mañana se mueve una columna de sitio.
//
// La columna de la correa es la Y y NO TIENE TÍTULO en la fila 1 —ahí
// hay un número del bloque de piezas—, así que esa va por letra. Si
// algún día se le pone título, se cambia 'Y' por el título y listo.
const CAMBIOS = [
  {
    ref: 'LO-05_Trinchera_A01',
    motivo: 'Óscar, 06/08/2026: en Alba la caja es plata o bronce; ' +
            'el PVD negro es solo del Eclipse. Su «Caja/conjunto» ya ' +
            'dice «39mm plata solido».',
    celdas: {
      'Caja — Material': 'Acero inoxidable 316L, plata',
      'Caja — Acabado': 'Acero pulido/cepillado (plata)',
      // el cierre traía el código del proveedor en vez del cierre
      'Brazalete — Tipo de cierre': 'Hebilla de acero',
      // y la correa, sin tilde, partía en dos una opción que es una
      'Y': 'Correa NATO de nailon balístico verde militar 20mm',
    },
  },
  {
    ref: 'LO-05_Trinchera_L01',
    motivo: 'Mismo caso que el A01: es plata, no PVD negro.',
    celdas: {
      'Caja — Material': 'Acero inoxidable 316L, plata',
      'Caja — Acabado': 'Acero pulido/cepillado (plata)',
      'Y': 'Correa NATO de nailon balístico verde militar 20mm',
    },
  },
  {
    ref: 'LO-08_Tortuga_C01',
    motivo: 'Óscar lo dio por bueno el 06/08/2026 y ya está a la venta. ' +
            'La nota de compras se va de la celda del dato. OJO: la ' +
            'columna «Movimiento» dice NH36A y esta dice NE15, y los ' +
            'rubíes, la frecuencia y la reserva de esta fila son los del ' +
            'NE15. Hay que decidir cuál es y dejar las dos iguales.',
    celdas: {
      'Movimiento — Calibre': 'Seiko NE15 (equiv. 6R15)',
    },
  },
];


function letraACol(letra) {
  let n = 0;
  for (let i = 0; i < letra.length; i++) n = n * 26 + letra.charCodeAt(i) - 64;
  return n - 1;
}


function arreglarCatalogoLaOra() {
  const hoja = SpreadsheetApp.getActive().getSheetByName(HOJA);
  if (!hoja) throw new Error('No encuentro la hoja «' + HOJA + '»');

  const datos = hoja.getDataRange().getValues();
  const titulos = datos[0].map(String);

  let tocadas = 0;
  CAMBIOS.forEach(function (cambio) {
    const fila = datos.findIndex(function (f) { return String(f[0]).trim() === cambio.ref; });
    if (fila < 0) {
      Logger.log('✗ No encuentro la referencia ' + cambio.ref);
      return;
    }
    Logger.log('— ' + cambio.ref + ' · ' + cambio.motivo);
    Object.keys(cambio.celdas).forEach(function (titulo) {
      // por título, o por letra cuando la columna no tiene título
      const col = /^[A-Z]{1,2}$/.test(titulo)
        ? letraACol(titulo)
        : titulos.indexOf(titulo);
      if (col < 0) {
        Logger.log('   ✗ No encuentro la columna «' + titulo + '»');
        return;
      }
      const nombre = /^[A-Z]{1,2}$/.test(titulo) ? 'columna ' + titulo : titulo;
      const antes = String(datos[fila][col]);
      const ahora = cambio.celdas[titulo];
      if (antes === ahora) {
        Logger.log('   = ' + nombre + ': ya estaba bien');
        return;
      }
      hoja.getRange(fila + 1, col + 1).setValue(ahora);
      Logger.log('   ✔ ' + nombre);
      Logger.log('       antes: ' + antes);
      Logger.log('       ahora: ' + ahora);
      tocadas++;
    });
  });

  Logger.log('');
  Logger.log(tocadas + ' celdas cambiadas.');
}
