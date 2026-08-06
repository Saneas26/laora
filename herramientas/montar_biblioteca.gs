/**
 * laOra · LA BIBLIOTECA
 * ============================================================
 * Monta el esqueleto de la hoja que manda sobre todo: compras,
 * precios, diseño gráfico y web. Ocho pestañas, vacías de datos pero
 * con las fórmulas ya funcionando.
 *
 * LA REGLA, Y ES LA ÚNICA
 * ------------------------------------------------------------
 * Un dato, un sitio. El coste de un movimiento se escribe UNA vez en
 * COMPONENTES; las cinco referencias que lo montan lo miran allí. Por
 * eso la caja del Trinchera no puede volver a decir «PVD negro» en dos
 * filas y «plata» en las otras cuatro: solo hay una fila.
 *
 * LO QUE ESCRIBES TÚ         LO QUE SE CALCULA SOLO
 *   1 · PARÁMETROS             6 · PRECIOS
 *   2 · COMPONENTES            7 · COMPRAS
 *   3 · MOVIMIENTOS            8 · WEB
 *   4 · MODELOS
 *   5 · REFERENCIAS
 *
 * LAS DOS DESCRIPCIONES
 * ------------------------------------------------------------
 * Cada componente lleva `desc_compra` —lo que escribes en AliExpress,
 * con marcas ajenas y códigos de proveedor si hace falta— y `desc_web`
 * —lo único que ve el cliente—. La pestaña WEB solo lee la segunda, así
 * que ya no hay que filtrar nada: lo interno no puede escaparse porque
 * no está en la hoja que lee el generador.
 *
 * CÓMO SE USA
 * ------------------------------------------------------------
 *   1. Abre el libro «Catalogo laOra».
 *   2. Extensiones → Apps Script.
 *   3. Pega esto, guarda y pulsa ▶ sobre `montarBiblioteca`.
 *   4. Mira el registro (Ver → Registro de ejecución).
 *
 * LAS TRECE QUE YA HAY
 * ------------------------------------------------------------
 * El libro no estaba vacío: tiene Inicio, Modelos, Gama y acabados,
 * Línea Eclipse, Biblioteca BOM, Movimientos, Estándar calidad,
 * Escandallo, Opus compras, Catalogo final, Escandallo Claude,
 * Catalogo laOra y PVP_Claude.
 *
 * Dos de ellas —«Modelos» y «Movimientos»— se llamaban igual que dos de
 * las nuestras. Por eso las nuevas llevan el prefijo `BIB_`: no pueden
 * pisar nada, y de un vistazo se ve cuáles son del sistema nuevo.
 *
 * `rehacer()` se niega en redondo a borrar una pestaña que no empiece
 * por `BIB_`. NO TOCA ninguna de las trece.
 *
 * OJO: al rehacer una pestaña BIB_ se pierde lo que hubiera escrito en
 * ella. Mientras estemos migrando, ejecuta con la cabeza.
 */

// El libro YA TIENE 13 pestañas, y dos se llaman «Modelos» y «Movimientos».
// Por eso las nuevas van con prefijo: así no pueden pisar nada de lo que hay.
// Sin espacios ni acentos en el nombre, para que las fórmulas no necesiten
// comillas al referirse a ellas.
const PREFIJO = 'BIB_';
const CLAVES = ['PARAMETROS', 'COMPONENTES', 'MOVIMIENTOS', 'MODELOS',
                'REFERENCIAS', 'PRECIOS', 'COMPRAS', 'WEB'];

function hoja(clave) { return PREFIJO + clave; }

// Estas ocho y ninguna más. Las otras trece son intocables.
const HOJAS = CLAVES.map(hoja);

const AZUL = '#1a1a1a';       // cabecera de las que escribes tú
const GRIS = '#4a4a4a';       // cabecera de las que se calculan solas
const CALCULADA = '#f5f5f3';  // fondo de las columnas con fórmula

const EUR = '#,##0.00 "€"';
const PCT = '0.0%';
const FILAS = 300;            // hasta dónde llegan las fórmulas
const FILAS_COMP = 500;       // componentes: caben más


/* ============================================================
   1 · PARÁMETROS
   ============================================================
   Todos los números de los que cuelga el resto. Cada uno tiene
   nombre, y las fórmulas lo llaman por su nombre: así en PRECIOS
   se lee `margen_objetivo` y no `$B$9`.
*/
const PARAMETROS = [
  ['impuesto_venta',     0.21,  'tanto por uno',
   'El impuesto que va DENTRO del PVP. ⚠ REVISAR: Canarias es IGIC, no IVA, y desde el 01/07/2026 entra el REPEP. Vender a Península tampoco es un 21% sin más.'],
  ['comision_pago_pct',  0.034, 'tanto por uno',
   'La parte variable que se lleva la pasarela de cobro.'],
  ['comision_pago_fija', 0.35,  '€',
   'La parte fija que se lleva la pasarela por cada cobro.'],
  ['envio_medio',        6.00,  '€',
   'Lo que cuesta de media mandar un reloj, embalaje aparte.'],
  ['devoluciones_pct',   0.02,  'tanto por uno',
   'Provisión por devoluciones. Sube este número si empiezan a volver.'],
  ['provision_garantia', 4.00,  '€',
   'Lo que se aparta por reloj para la garantía de 5 años. Con un fallo del 5% y unos 100 € por avería atendida, salen ~5 €.'],
  ['colchon_inflacion',  0.20,  'tanto por uno',
   'Cuánto pueden subir los materiales sin que el precio deje de valer. El coste se calcula ya con esta subida encima.'],
  ['margen_objetivo',    50.00, '€',
   'Lo que tiene que dejar cada reloj limpio. Es la regla de Óscar y no se negocia.'],
  ['margen_minimo_pct',  0.22,  'tanto por uno',
   'Margen mínimo sobre PVP. Un reloj puede dejar 50 € y aun así ser mal negocio si es carísimo.'],
  ['moq_esferas',        10,    'uds',
   'Pedido mínimo de esferas. Es la única pieza que obliga a tener stock, y por eso decide cuántos acabados te puedes permitir.'],
  ['garantia_anios',     5,     'años',
   'Los años de garantía que se prometen. No se dice «para toda la vida»: eso no se puede cumplir y no hace falta.'],
];


/* ============================================================
   Las columnas de cada pestaña
   ============================================================
   [título, ancho, formato, nota de cabecera]
*/
const COLUMNAS = {

  'COMPONENTES': [
    ['id',              110, null, 'El código con el que lo llaman las referencias. Cortito y sin espacios: MOV-PT5000, CAJA-BIT-40, ESF-BIT-TIFFANY.'],
    ['tipo',            110, null, 'De qué familia es. La lista está cerrada para que no aparezcan «esferas» y «esfera» como si fueran dos cosas.'],
    ['nombre_interno',  200, null, 'Cómo lo llamas tú cuando hablas del asunto.'],
    ['desc_compra',     280, null, 'Lo que escribes en AliExpress para encontrarlo. Aquí SÍ van marcas ajenas, códigos de proveedor y lo que haga falta. Esto no sale nunca de la hoja.'],
    ['desc_web',        280, null, 'Lo único que lee el cliente. Sin marcas ajenas, sin «clon», sin códigos, sin a qué se parece.'],
    ['material',        140, null, null],
    ['acabado',         140, null, null],
    ['color',           110, null, null],
    ['diametro_mm',      90, '0.0', null],
    ['alto_mm',          80, '0.00', null],
    ['ancho_asa_mm',     90, '0', 'El ancho entre asas. Manda sobre qué correas valen.'],
    ['peso_g',           80, '0', null],
    ['proveedor',       150, null, null],
    ['enlace',          200, null, 'El enlace de compra. Interno: no sale a la web.'],
    ['coste_ud',        100, EUR, 'Lo que pagas por una. Esto se escribe AQUÍ y en ningún otro sitio.'],
    ['moq',              70, '0', 'Pedido mínimo. Las esferas van de 10 en 10.'],
    ['plazo_dias',       80, '0', null],
    ['fecha_precio',    100, 'dd/mm/yyyy', 'Cuándo comprobaste ese precio. En AliExpress un precio de hace seis meses no es un precio.'],
    ['activo',           70, null, null],
    ['notas_internas',  260, null, null],
  ],

  'MOVIMIENTOS': [
    ['id_componente',   110, null, 'El mismo id que en COMPONENTES. El coste vive allí; aquí solo van las specs.'],
    ['calibre',         120, null, null],
    ['fabricante',      130, null, null],
    ['pais',             90, null, null],
    ['tipo',            120, null, null],
    ['frecuencia_ah',   100, '#,##0', 'Alternancias por hora. 21.600 o 28.800 en los mecánicos.'],
    ['joyas',            70, '0', null],
    ['reserva_h',        80, '0', null],
    ['precision_dec',   130, null, 'La precisión que declara el fabricante, p. ej. «-20/+40 s/día». Es la declarada, no la medida.'],
    ['para_segundero',  110, null, 'Si el segundero se para al sacar la corona. El Miyota 8215 no lo hace.'],
    ['cuerda_manual',   110, null, null],
    ['calendario',      110, null, null],
    ['diametro_mm',      90, '0.0', null],
    ['alto_mm',          80, '0.00', null],
    ['compat_caja_nh35',130, null, 'La caja de NH35 es la barata y la que copa el mercado. Esto dice si entra directo, con espaciador, o no entra.'],
    ['arquitectura',    140, null, 'De qué familia es el diseño. El ST2130 y el PT5000 siguen la del ETA 2824-2, que es la que sabe reparar cualquier relojero del mundo.'],
    ['notas_reparacion',220, null, 'Si se repara o se sustituye, y qué repuestos hay.'],
    ['desc_web',        220, null, 'Cómo se nombra en la ficha. Nunca «clon de» ni de qué calibre ajeno viene.'],
  ],

  'MODELOS': [
    ['id_modelo',       110, null, 'LO-01, LO-05…'],
    ['nombre',          140, null, null],
    ['slug',            120, null, 'La dirección: laora.es/lunar → «lunar».'],
    ['papel',           120, null, 'Qué hace este reloj en el catálogo: entrada, volumen o firma. Si dos modelos tienen el mismo papel, sobra uno.'],
    ['relato_corto',    320, null, 'De qué va este reloj en una frase. Es de donde sale el texto de la ficha.'],
    ['publico',         220, null, null],
    ['competencia_marca',140, null, 'Contra quién compite de verdad.'],
    ['competencia_modelo',160, null, null],
    ['competencia_precio',120, EUR, 'A cuánto lo vende. ESTE es el techo, y es la columna que hoy no existe y que hizo falta.'],
    ['diametro_caja_mm', 110, '0.0', null],
    ['estanqueidad',    110, null, null],
    ['estado',          100, null, null],
    ['notas',           260, null, null],
  ],

  'REFERENCIAS': [
    ['ref',             170, null, 'Lo que se vende. LO-07_Bitacora_A01.'],
    ['id_modelo',       110, null, null],
    ['acabado',         110, null, null],
    ['id_movimiento',   130, null, 'De aquí en adelante NO se describe nada: solo se apunta al id de COMPONENTES. La descripción vive allí.'],
    ['id_caja',         130, null, null],
    ['id_esfera',       130, null, null],
    ['id_agujas',       130, null, null],
    ['id_cristal',      130, null, null],
    ['id_corona',       130, null, null],
    ['id_fondo',        130, null, null],
    ['id_correa',       130, null, null],
    ['id_brazalete',    130, null, null],
    ['id_packaging',    130, null, null],
    ['estado',          100, null, 'Solo las «activa» se publican.'],
    ['foto',            220, null, null],
    ['notas',           240, null, null],
  ],

  'PRECIOS': [
    ['ref',             170, null, null],
    ['modelo',          130, null, null],
    ['acabado',         110, null, null],
    ['coste_piezas',    110, EUR, 'La suma de las diez piezas de la referencia, mirando el coste en COMPONENTES.'],
    ['coste_ajustado',  120, EUR, 'El coste ya con el colchón de inflación encima. Es con este con el que se calcula, no con el de hoy.'],
    ['factor_neto',     100, '0.0000', 'De cada euro de PVP, lo que queda después del impuesto, la comisión variable y las devoluciones.'],
    ['cargos_fijos',    110, EUR, 'Comisión fija + envío + provisión de garantía.'],
    ['suelo_tecnico',   120, EUR, 'El PVP mínimo para que queden los 50 €. Por debajo de aquí se trabaja gratis.'],
    ['techo_mercado',   120, EUR, 'Lo que cobra la competencia. Vender por encima hay que saber por qué.'],
    ['pvp_propuesto',   120, EUR, 'Sale redondeado al x9,90 siguiente. Se puede escribir a mano encima: es una propuesta, no una orden.'],
    ['margen_eur',      110, EUR, null],
    ['margen_pct',       95, PCT, null],
    ['revision',        260, null, 'Dice OK, o dice qué falla.'],
  ],

  'COMPRAS': [
    ['id_componente',   120, null, null],
    ['desc_compra',     280, null, null],
    ['tipo',            110, null, null],
    ['coste_ud',        100, EUR, null],
    ['usado_en_refs',   110, '0', 'En cuántas referencias entra. Un componente con 0 es dinero parado sin motivo.'],
    ['stock_actual',    100, '0', '← ESTA LA ESCRIBES TÚ. Lo que tienes en el cajón.'],
    ['moq',              70, '0', null],
    ['coste_pedido_min',120, EUR, 'Lo que cuesta el pedido mínimo. Para las esferas son 10 × su precio.'],
    ['plazo_dias',       90, '0', null],
    ['inmovilizado',    110, EUR, 'Lo que tienes parado en esa pieza.'],
    ['notas',           240, null, null],
  ],

  'WEB': [
    ['ref',             170, null, 'Esta pestaña es lo ÚNICO que lee el generador. No tiene ni una columna de coste, así que no puede escaparse nada.'],
    ['slug_modelo',     120, null, null],
    ['modelo',          130, null, null],
    ['acabado',         110, null, null],
    ['pvp',             100, EUR, null],
    ['movimiento',      220, null, null],
    ['caja',            240, null, null],
    ['esfera',          240, null, null],
    ['agujas',          200, null, null],
    ['cristal',         180, null, null],
    ['correa',          220, null, null],
    ['diametro_mm',     100, '0.0', null],
    ['estanqueidad',    110, null, null],
    ['foto',            220, null, null],
    ['publicar',         90, null, null],
  ],
};


/* Listas cerradas. Sin esto vuelven los «balístico» y «balistico». */
const VALIDACIONES = {
  'COMPONENTES': {
    'tipo': ['movimiento', 'caja', 'esfera', 'agujas', 'cristal', 'corona',
             'fondo', 'correa', 'brazalete', 'packaging', 'junta', 'otro'],
    'activo': ['sí', 'no'],
  },
  'MOVIMIENTOS': {
    'tipo': ['automático', 'cuerda manual', 'cuarzo', 'mecacuarzo'],
    'para_segundero': ['sí', 'no'],
    'cuerda_manual': ['sí', 'no'],
    'calendario': ['sin fecha', 'fecha', 'día y fecha', 'GMT', 'cronógrafo'],
    'compat_caja_nh35': ['directo', 'espaciador', 'no entra'],
  },
  'MODELOS': {
    'papel': ['entrada', 'volumen', 'firma'],
    'estado': ['activo', 'borrador', 'archivado'],
  },
  'REFERENCIAS': {
    'acabado': ['Alba', 'Levante', 'Cenit', 'Eclipse'],
    'estado': ['activa', 'borrador', 'archivada'],
  },
};


/* ============================================================
   Utilidades
   ============================================================ */

function col(hoja, titulo) {
  const defs = COLUMNAS[hoja];
  for (let i = 0; i < defs.length; i++) if (defs[i][0] === titulo) return i + 1;
  throw new Error('No existe la columna «' + titulo + '» en ' + hoja);
}

function letra(n) {
  let s = '';
  while (n > 0) { const r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = (n - r - 1) / 26; }
  return s;
}

function rehacer(ss, nombre) {
  // Cinturón: aquí no se borra nada que no lleve nuestro prefijo. Si alguna
  // vez alguien cambia un nombre a mano, el guion se para en vez de tragarse
  // una pestaña con datos.
  if (nombre.indexOf(PREFIJO) !== 0) {
    throw new Error('Me niego a tocar «' + nombre + '»: no es una pestaña de la biblioteca.');
  }
  const vieja = ss.getSheetByName(nombre);
  if (vieja) ss.deleteSheet(vieja);
  return ss.insertSheet(nombre);
}


/* ============================================================
   El montaje
   ============================================================ */

function montarBiblioteca() {
  const ss = SpreadsheetApp.getActive();

  const ajenas = ss.getSheets()
    .map(function (h) { return h.getName(); })
    .filter(function (n) { return HOJAS.indexOf(n) < 0; });
  Logger.log('Pestañas que NO se tocan: ' + (ajenas.join(', ') || '—'));
  Logger.log('');

  montarParametros(ss);
  ['COMPONENTES', 'MOVIMIENTOS', 'MODELOS', 'REFERENCIAS',
   'PRECIOS', 'COMPRAS', 'WEB'].forEach(function (c) { montarTabla(ss, c); });

  formulasPrecios(ss);
  formulasCompras(ss);
  formulasWeb(ss);

  ss.setActiveSheet(ss.getSheetByName(hoja('PARAMETROS')));

  Logger.log('');
  Logger.log('✔ Biblioteca montada: ' + HOJAS.join(' · '));
  Logger.log('  Empieza por COMPONENTES. Sin piezas no hay costes, y sin costes no hay precios.');
}


function montarParametros(ss) {
  const h = rehacer(ss, hoja('PARAMETROS'));
  const cab = ['Parámetro', 'Valor', 'Unidad', 'Qué es', 'Nombre en fórmulas'];

  h.getRange(1, 1, 1, cab.length).setValues([cab])
    .setFontWeight('bold').setFontColor('#ffffff').setBackground(AZUL);

  const filas = PARAMETROS.map(function (p) {
    return [p[0], p[1], p[2], p[3], p[0]];
  });
  h.getRange(2, 1, filas.length, 5).setValues(filas);

  // los tantos por uno como porcentaje, y los euros como euros
  PARAMETROS.forEach(function (p, i) {
    const c = h.getRange(i + 2, 2);
    if (p[2] === '€') c.setNumberFormat(EUR);
    else if (p[2] === 'tanto por uno') c.setNumberFormat('0.00%');
    else c.setNumberFormat('#,##0');
  });

  h.getRange(2, 2, filas.length, 1).setBackground('#fff8e1');  // la columna que se toca
  h.setColumnWidth(1, 170); h.setColumnWidth(2, 100);
  h.setColumnWidth(3, 110); h.setColumnWidth(4, 520); h.setColumnWidth(5, 170);
  h.getRange(1, 4, filas.length + 1, 1).setWrap(true);
  h.setFrozenRows(1);

  // Los nombres. Con esto las fórmulas se leen solas.
  ss.getNamedRanges().forEach(function (r) {
    if (PARAMETROS.some(function (p) { return p[0] === r.getName(); })) r.remove();
  });
  PARAMETROS.forEach(function (p, i) {
    ss.setNamedRange(p[0], h.getRange(i + 2, 2));
  });

  Logger.log('✔ PARÁMETROS · ' + PARAMETROS.length + ' valores con nombre');
  Logger.log('  ⚠ impuesto_venta está a 0,21 provisionalmente. Hay que decidirlo: Canarias, IGIC y el REPEP del 01/07/2026.');
}


function montarTabla(ss, clave) {
  const h = rehacer(ss, hoja(clave));
  const nombre = clave;                       // la clave interna de COLUMNAS
  const defs = COLUMNAS[nombre];
  const calculada = ['PRECIOS', 'COMPRAS', 'WEB'].indexOf(nombre) >= 0;
  const filas = nombre === 'COMPONENTES' || nombre === 'COMPRAS' ? FILAS_COMP : FILAS;

  const cab = h.getRange(1, 1, 1, defs.length);
  cab.setValues([defs.map(function (d) { return d[0]; })])
     .setFontWeight('bold').setFontColor('#ffffff')
     .setBackground(calculada ? GRIS : AZUL);

  defs.forEach(function (d, i) {
    h.setColumnWidth(i + 1, d[1]);
    if (d[2]) h.getRange(2, i + 1, filas, 1).setNumberFormat(d[2]);
    if (d[3]) h.getRange(1, i + 1).setNote(d[3]);
  });

  if (calculada) h.getRange(2, 1, filas, defs.length).setBackground(CALCULADA);

  const vals = VALIDACIONES[nombre];
  if (vals) {
    Object.keys(vals).forEach(function (titulo) {
      const regla = SpreadsheetApp.newDataValidation()
        .requireValueInList(vals[titulo], true).setAllowInvalid(false).build();
      h.getRange(2, col(nombre, titulo), filas, 1).setDataValidation(regla);
    });
  }

  h.setFrozenRows(1);
  h.setFrozenColumns(1);
  Logger.log('✔ ' + hoja(nombre) + ' · ' + defs.length + ' columnas');
}


/* ============================================================
   Las fórmulas
   ============================================================ */

function formulasPrecios(ss) {
  const h = ss.getSheetByName(hoja('PRECIOS'));
  const CO = hoja('COMPONENTES');
  const RE = hoja('REFERENCIAS');
  const MO = hoja('MODELOS');

  // las diez ranuras de piezas de REFERENCIAS, de id_movimiento a id_packaging
  const desde = col('REFERENCIAS', 'id_movimiento');
  const hasta = col('REFERENCIAS', 'id_packaging');
  const sumas = [];
  for (let c = desde; c <= hasta; c++) {
    sumas.push('SUMIF(' + CO + '!$A$2:$A$' + FILAS_COMP + ',' + RE + '!' +
               letra(c) + '2,' + CO + '!$O$2:$O$' + FILAS_COMP + ')');
  }

  const f = {
    'ref':            '=IF(' + RE + '!A2="","",' + RE + '!A2)',
    'modelo':         '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!B2,' + MO + '!$A$2:$B$100,2,FALSE),""))',
    'acabado':        '=IF($A2="","",' + RE + '!C2)',
    'coste_piezas':   '=IF($A2="","",' + sumas.join('+') + ')',
    'coste_ajustado': '=IF($A2="","",$D2*(1+colchon_inflacion))',
    'factor_neto':    '=IF($A2="","",1/(1+impuesto_venta)-comision_pago_pct-devoluciones_pct)',
    'cargos_fijos':   '=IF($A2="","",comision_pago_fija+envio_medio+provision_garantia)',
    // el PVP que deja exactamente el margen objetivo
    'suelo_tecnico':  '=IF($A2="","",($E2+$G2+margen_objetivo)/$F2)',
    'techo_mercado':  '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!B2,' + MO + '!$A$2:$I$100,9,FALSE),""))',
    // redondeado al x9,90 siguiente. Se puede pisar a mano.
    'pvp_propuesto':  '=IF($A2="","",CEILING($H2-9.9,10)+9.9)',
    'margen_eur':     '=IF(OR($A2="",$J2=""),"",$J2*$F2-$G2-$E2)',
    'margen_pct':     '=IF(OR($J2="",$J2=0),"",$K2/$J2)',
    'revision':       '=IF(OR($A2="",$J2=""),"",IF(AND($K2>=margen_objetivo,$L2>=margen_minimo_pct,' +
                      'OR($I2="",$J2<=$I2)),"OK",TRIM(REGEXREPLACE(' +
                      'IF($K2<margen_objetivo,"no llega al margen objetivo · ","")&' +
                      'IF($L2<margen_minimo_pct,"margen % bajo · ","")&' +
                      'IF(AND($I2<>"",$J2>$I2),"por encima del mercado · ",""),' +
                      '"\\s*·\\s*$",""))))',
  };
  aplicar(h, 'PRECIOS', f, FILAS);
  Logger.log('✔ ' + hoja('PRECIOS') + ' · motor montado (coste → suelo → techo → PVP → margen)');
}


function formulasCompras(ss) {
  const h = ss.getSheetByName(hoja('COMPRAS'));
  const CO = hoja('COMPONENTES');
  const RE = hoja('REFERENCIAS');
  const d = col('REFERENCIAS', 'id_movimiento');
  const m = col('REFERENCIAS', 'id_packaging');

  const f = {
    'id_componente':   '=IF(' + CO + '!A2="","",' + CO + '!A2)',
    'desc_compra':     '=IF($A2="","",' + CO + '!D2)',
    'tipo':            '=IF($A2="","",' + CO + '!B2)',
    'coste_ud':        '=IF($A2="","",' + CO + '!O2)',
    'usado_en_refs':   '=IF($A2="","",COUNTIF(' + RE + '!$' + letra(d) + '$2:$' +
                       letra(m) + '$' + FILAS + ',$A2))',
    // stock_actual se escribe a mano: no lleva fórmula
    'moq':             '=IF($A2="","",' + CO + '!P2)',
    'coste_pedido_min':'=IF($A2="","",$D2*$G2)',
    'plazo_dias':      '=IF($A2="","",' + CO + '!Q2)',
    'inmovilizado':    '=IF($A2="","",$D2*N($F2))',
  };
  aplicar(h, 'COMPRAS', f, FILAS_COMP);

  // la columna que sí se escribe, marcada
  h.getRange(2, col('COMPRAS', 'stock_actual'), FILAS_COMP, 1).setBackground('#fff8e1');

  Logger.log('✔ ' + hoja('COMPRAS') + ' · stock_actual se escribe a mano; lo demás sale solo');
}


function formulasWeb(ss) {
  const h = ss.getSheetByName(hoja('WEB'));
  const CO = hoja('COMPONENTES');
  const RE = hoja('REFERENCIAS');
  const MO = hoja('MODELOS');
  const PR = hoja('PRECIOS');
  const RANGO = CO + '!$A$2:$E$' + FILAS_COMP;   // id → desc_web (columna 5)

  function pieza(titulo) {
    return '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!' +
           letra(col('REFERENCIAS', titulo)) + '2,' + RANGO + ',5,FALSE),""))';
  }

  const f = {
    'ref':          '=IF(' + RE + '!A2="","",' + RE + '!A2)',
    'slug_modelo':  '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!B2,' + MO + '!$A$2:$C$100,3,FALSE),""))',
    'modelo':       '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!B2,' + MO + '!$A$2:$B$100,2,FALSE),""))',
    'acabado':      '=IF($A2="","",' + RE + '!C2)',
    'pvp':          '=IF($A2="","",' + PR + '!J2)',
    'movimiento':   pieza('id_movimiento'),
    'caja':         pieza('id_caja'),
    'esfera':       pieza('id_esfera'),
    'agujas':       pieza('id_agujas'),
    'cristal':      pieza('id_cristal'),
    'correa':       pieza('id_correa'),
    'diametro_mm':  '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!B2,' + MO + '!$A$2:$J$100,10,FALSE),""))',
    'estanqueidad': '=IF($A2="","",IFERROR(VLOOKUP(' + RE + '!B2,' + MO + '!$A$2:$K$100,11,FALSE),""))',
    'foto':         '=IF($A2="","",' + RE + '!' + letra(col('REFERENCIAS', 'foto')) + '2)',
    'publicar':     '=IF($A2="","",' + RE + '!' + letra(col('REFERENCIAS', 'estado')) + '2="activa")',
  };
  aplicar(h, 'WEB', f, FILAS);
  Logger.log('✔ ' + hoja('WEB') + ' · solo desc_web y PVP. Ni una columna de coste.');
}


/* `destino` es la pestaña. Ojo: NO se llama `hoja`, que es el nombre de
   la función que compone los nombres con prefijo. */
function aplicar(destino, clave, formulas, filas) {
  Object.keys(formulas).forEach(function (titulo) {
    const c = col(clave, titulo);
    // Se escribe en la fila 2 y se copia hacia abajo: copiando, Sheets
    // ajusta las referencias fila a fila, que es justo lo que hace falta.
    // (Se escribe en notación con coma; la hoja la traduce al «;» de España.)
    const primera = destino.getRange(2, c);
    primera.setFormula(formulas[titulo]);
    if (filas > 1) primera.copyTo(destino.getRange(3, c, filas - 1, 1));
  });
}
