/**
 * laOra · LA BIBLIOTECA
 * ============================================================
 * La hoja que manda sobre todo: comprar, vender y publicar. Once
 * pestañas. Se monta vacía pero con las fórmulas ya tirando, y con los
 * movimientos ya sembrados.
 *
 * DE CERO
 * ------------------------------------------------------------
 * Óscar, 06/08/2026: «quiero empezar de cero». No se migra nada del
 * libro viejo. Los precios de aquella «Biblioteca BOM» eran
 * estimaciones de hace semanas y la realidad salió bastante más cara:
 * el NH35A se estimó en 28,50 € y son 60-67 €.
 *
 * LA REGLA, Y ES LA ÚNICA
 * ------------------------------------------------------------
 * Un dato, un sitio. El coste de un movimiento se escribe UNA vez, en
 * COMPONENTES. Las referencias que lo montan lo miran allí. Por eso no
 * puede volver a pasar que la misma caja diga «PVD negro» en dos filas
 * y «plata» en otras cuatro.
 *
 * LAS ONCE PESTAÑAS
 * ------------------------------------------------------------
 *   LAS QUE ESCRIBES TÚ            LAS QUE SE CALCULAN SOLAS
 *   1 · PARAMETROS                  9 · PRECIOS
 *   2 · COMPONENTES                10 · COMPRAS
 *   3 · MOVIMIENTOS                11 · WEB
 *   4 · CAJAS
 *   5 · ESFERAS
 *   6 · CORREAS
 *   7 · MODELOS
 *   8 · REFERENCIAS
 *
 * COMPONENTES lleva lo que TODA pieza tiene: qué es, a quién se le
 * compra, cuánto cuesta, cuántas hay que pedir y cuánto tarda. Las
 * cuatro familias con muchas specs —movimientos, cajas, esferas y
 * correas— tienen su propia pestaña, enganchada por el mismo `id`. Así
 * caben la frecuencia, la reserva de marcha, el estilo del brazalete y
 * hasta el micro-ajuste del cierre, sin una tabla de sesenta columnas
 * medio vacías.
 *
 * LAS DOS DESCRIPCIONES
 * ------------------------------------------------------------
 * Cada componente lleva `desc_compra` —lo que escribes en AliExpress,
 * con marcas ajenas y códigos de proveedor si hace falta— y `desc_web`
 * —lo único que ve el cliente—. La pestaña WEB solo lee la segunda, y
 * no tiene ni una columna de coste: lo interno no puede escaparse
 * porque no está en la hoja que lee el generador.
 *
 * VA EN UN LIBRO NUEVO
 * ------------------------------------------------------------
 * Lo primero que hace `montarBiblioteca` es comprobar que el libro está
 * vacío. Si tiene pestañas ajenas con datos, se para y dice cuáles.
 *
 * CÓMO SE USA
 * ------------------------------------------------------------
 *   1. Libro nuevo → Extensiones → Apps Script.
 *   2. Pega esto, guarda y pulsa ▶ sobre `montarBiblioteca`.
 *   3. Ver → Registro de ejecución.
 *
 * OJO: al volver a ejecutarlo se rehacen las once y se pierde lo que
 * hubiera escrito en ellas.
 */

const CLAVES = ['PARAMETROS', 'COMPONENTES', 'MOVIMIENTOS', 'CAJAS', 'ESFERAS',
                'CORREAS', 'MODELOS', 'REFERENCIAS', 'PRECIOS', 'COMPRAS', 'WEB'];
const HOJAS = CLAVES.slice();

const AZUL = '#1a1a1a';       // cabecera de las que escribes tú
const GRIS = '#4a4a4a';       // cabecera de las que se calculan solas
const CALCULADA = '#f5f5f3';  // fondo de las columnas con fórmula
const AMARILLO = '#fff8e1';   // celda que se toca a mano

const EUR = '#,##0.00 "€"';
const PCT = '0.0%';
const FECHA = 'dd/mm/yyyy';
const FILAS = 300;            // hasta dónde llegan las fórmulas
const FILAS_COMP = 500;       // componentes: caben más


/* ============================================================
   1 · PARAMETROS
   ============================================================
   Todos los números de los que cuelga el resto, cada uno con nombre.
   Así en PRECIOS se lee `margen_objetivo` y no `$B$9`.
*/
const PARAMETROS = [
  ['multiplicador',      2.80,  'veces',
   '★ EL NÚMERO QUE MANDA. El PVP sale de multiplicar por esto lo que cuesta el reloj. A x2,0 no se gana; x2,5 es el mínimo; x3,0 es lo sano. Se sube o se baja aquí y se recalcula el catálogo entero.'],

  ['impuesto_venta',     0.21,  'tanto por uno',
   'El impuesto que va DENTRO del PVP. Ojo: no es tuyo ni te cuesta, lo cobras y lo ingresas. ⚠ REVISAR: en Canarias es IGIC, no IVA, y el 01/07/2026 entra el REPEP.'],
  ['irpf',               0.20,  'tanto por uno',
   'Se aplica SOBRE EL BENEFICIO, nunca sobre la venta. Aplicarlo al PVP da un número mucho peor que la realidad.'],
  ['ss_modo',            'cuota', 'porcentaje | cuota',
   'Cómo contar la Seguridad Social. «porcentaje» usa ss_pct sobre el beneficio. «cuota» reparte la cuota mensual entre los relojes que vendes al mes, que es lo que pasa de verdad.'],
  ['ss_pct',             0.05,  'tanto por uno',
   'Solo se usa si ss_modo = «porcentaje».'],
  ['cuota_ss_mes',     300.00,  '€/mes',
   'Lo que pagas de autónomo al mes. Es fijo: lo pagas vendas uno o vendas treinta.'],
  ['unidades_mes',         10,  'uds/mes',
   'Cuántos relojes esperas vender al mes. ⚠ Este número cambia el resultado más que casi ningún otro: con cuota de 300 € y 5 relojes, la SS son 60 € POR RELOJ; con 30, son 10 €.'],

  ['comision_pago_pct',  0.034, 'tanto por uno',
   'La parte variable que se lleva la pasarela de cobro. Va sobre el PVP entero, impuesto incluido.'],
  ['comision_pago_fija', 0.35,  '€',
   'La parte fija que se lleva la pasarela por cada cobro.'],
  ['packaging',          2.00,  '€',
   'La caja, el estuche y lo que va dentro.'],
  ['envio',              7.00,  '€',
   'Mandar el reloj al cliente.'],
  ['montaje_y_control',  8.00,  '€',
   'Montarlo, regularlo y comprobarlo antes de enviarlo. Es lo que te permite prometer cinco años con un movimiento chino: no lo da la fábrica, lo das tú.'],
  ['provision_garantia', 4.00,  '€',
   'Lo que se aparta por reloj para la garantía. Con un 5 % de averías y unos 100 € por avería atendida, salen unos 5 €.'],
  ['devoluciones_pct',   0.02,  'tanto por uno',
   'Provisión por devoluciones. Sube este número si empiezan a volver.'],

  ['colchon_inflacion',  0.20,  'tanto por uno',
   'Cuánto pueden subir los materiales sin que el precio deje de valer. El coste se calcula ya con esta subida encima, para no revisar precios en cada pedido.'],
  ['limpio_minimo',     40.00,  '€',
   'Por debajo de esto, el aviso salta. No es un objetivo: es el suelo por debajo del cual el reloj no compensa.'],
  ['moq_esferas',          10,  'uds',
   'Pedido mínimo de esferas. Es la única pieza que obliga a tener stock, y por eso decide cuántos acabados te puedes permitir.'],
  ['garantia_anios',        5,  'años',
   'Los años de garantía que se prometen. No se dice «para toda la vida»: eso no se puede cumplir y no hace falta.'],
];


/* ============================================================
   Las columnas · [título, ancho, formato, nota de cabecera]
   ============================================================ */
const COLUMNAS = {

  'COMPONENTES': [
    ['id',              130, null, 'El código con el que lo llaman las referencias. Corto y sin espacios: MOV-PT5000, CAJA-BIT-40, ESF-BIT-TIFFANY.'],
    ['tipo',            110, null, 'De qué familia es. Lista cerrada, para que no convivan «esferas» y «esfera» como si fueran dos cosas.'],
    ['nombre_interno',  200, null, 'Cómo lo llamas tú cuando hablas del asunto.'],
    ['desc_compra',     300, null, 'Lo que escribes en AliExpress para encontrarlo. Aquí SÍ van marcas ajenas y códigos de proveedor. Esto no sale nunca de la hoja.'],
    ['desc_web',        280, null, 'Lo único que lee el cliente. Sin marcas ajenas, sin «clon», sin códigos, sin a qué se parece.'],
    ['material',        150, null, null],
    ['acabado',         150, null, null],
    ['color',           120, null, null],
    ['peso_g',           80, '0.0', null],
    ['proveedor',       150, null, null],
    ['ref_proveedor',   130, null, 'El código del vendedor. Interno.'],
    ['enlace',          220, null, 'El enlace de compra. Interno: no sale a la web.'],
    ['coste_ud',        100, EUR, 'Lo que pagas por UNA. Esto se escribe AQUÍ y en ningún otro sitio del libro.'],
    ['moq',              70, '0', 'Pedido mínimo. Las esferas van de 10 en 10.'],
    ['plazo_dias',       90, '0', null],
    ['fecha_precio',    110, FECHA, 'Cuándo comprobaste ese precio. En AliExpress un precio de hace seis meses no es un precio.'],
    ['verificado',      100, null, 'Si el precio y la spec están comprobados de verdad, o son estimación.'],
    ['estado',          120, null, 'Dónde está la compra: buscando, candidato, muestra pedida, validado, descartado.'],
    ['activo',           80, null, null],
    ['notas_internas',  300, null, null],
  ],

  'MOVIMIENTOS': [
    ['id_componente',   130, null, 'El mismo id que en COMPONENTES. El coste vive allí; aquí solo van las specs.'],
    ['calibre',         120, null, null],
    ['fabricante',      140, null, null],
    ['pais',            100, null, null],
    ['tipo',            130, null, null],
    ['frecuencia_ah',   110, '#,##0', 'Alternancias por hora. 18.000 en el ST36, 21.600 en el NH35, 28.800 en el PT5000 y el 9015. Más alto = segundero más suave.'],
    ['joyas',            70, '0', null],
    ['reserva_h',        90, '0', 'Horas de marcha con cuerda completa.'],
    ['precision_dec',   140, null, 'La que declara el fabricante, p. ej. «-20/+40 s/día». Es la DECLARADA, no la medida.'],
    ['para_segundero',  120, null, 'Si el segundero se para al sacar la corona, para ponerlo en hora al segundo. El Miyota 8215 no lo hace.'],
    ['cuerda_manual',   120, null, 'Si se le puede dar cuerda a mano.'],
    ['calendario',      120, null, null],
    ['posicion_fecha',  120, null, 'A las 3, a las 6… Manda sobre qué esferas encajan.'],
    ['subesferas',      110, null, 'Cuántas y dónde. Para cronógrafos.'],
    ['diametro_mm',     100, '0.0', null],
    ['alto_mm',          90, '0.00', null],
    ['compat_caja_nh35',140, null, 'La caja de NH35 es la barata y la que copa el mercado. Dice si entra directo, con anillo espaciador, o no entra.'],
    ['arquitectura',    150, null, 'De qué familia es el diseño. El ST2130 y el PT5000 siguen la del ETA 2824-2, que es la que sabe reparar cualquier relojero del mundo.'],
    ['repuestos',       140, null, 'Si se consiguen piezas sueltas.'],
    ['notas_reparacion',260, null, 'Si se repara o se sustituye. El NH35 no se repara: sale más caro que uno nuevo.'],
    ['desc_web',        220, null, 'Cómo se nombra en la ficha. Nunca «clon de» ni de qué calibre ajeno viene.'],
  ],

  'CAJAS': [
    ['id_componente',   130, null, null],
    ['forma',           120, null, 'Redonda, tonneau, cojín, octogonal…'],
    ['diametro_mm',     100, '0.0', null],
    ['l2l_mm',           90, '0.0', 'De asa a asa. Manda sobre a qué muñeca le vale más que el diámetro.'],
    ['grosor_mm',       100, '0.00', null],
    ['ancho_asa_mm',    110, '0', 'El ancho entre asas. Manda sobre qué correas valen.'],
    ['material',        150, null, null],
    ['acabado',         160, null, null],
    ['bisel_tipo',      130, null, 'Fijo, giratorio unidireccional, bidireccional…'],
    ['bisel_material',  130, null, 'Cerámica, aluminio, acero…'],
    ['fondo_tipo',      130, null, 'Roscado, atornillado, con visor de zafiro…'],
    ['corona_tipo',     120, null, 'Roscada o de presión. La roscada es la que da estanqueidad de verdad.'],
    ['estanqueidad_m',  120, '0', 'En metros. Solo el valor que se pueda RESPALDAR con ensayo.'],
    ['cristal_incluido',130, null, null],
    ['aloja_movimiento',150, null, 'Para qué calibre está hecho el alojamiento: NH3x, ETA 2824, 6497…'],
    ['integrado',       110, null, 'Si el brazalete es integrado y va con la caja como conjunto.'],
    ['desc_web',        260, null, null],
  ],

  'ESFERAS': [
    ['id_componente',   130, null, null],
    ['color',           130, null, null],
    ['acabado',         150, null, 'Sunburst, mate, soleil, degradado, esmalte…'],
    ['indices',         150, null, 'Aplicados o impresos. Los aplicados son lo que separa un reloj de 100 € de uno de 250 €.'],
    ['numeracion',      130, null, 'Romanos, árabes, barras, mixta…'],
    ['lume',             90, null, null],
    ['tipo_lume',       120, null, 'BGW9, C3, Super-LumiNova…'],
    ['ventanilla_fecha',130, null, null],
    ['posicion_fecha',  120, null, 'Tiene que coincidir con la del movimiento.'],
    ['subesferas',      120, null, null],
    ['diametro_mm',     100, '0.0', null],
    ['logo_3d',         100, null, 'Si el logo va en relieve metálico. Es la pieza que te distingue: nadie más puede comprarla.'],
    ['texto_esfera',    200, null, 'Lo que va impreso. Solo laOra: jamás una marca ajena.'],
    ['esteril',          90, null, 'Sin ninguna marca al comprarla.'],
    ['compat_movimiento',150, null, 'Para qué calibre están los pies y la ventanilla.'],
    ['desc_web',        260, null, null],
  ],

  'CORREAS': [
    ['id_componente',   130, null, null],
    ['tipo',            110, null, 'Brazalete o correa.'],
    ['estilo',          150, null, 'Oyster, jubilee, milanesa, NATO, piel, caucho, cordura…'],
    ['material',        150, null, null],
    ['acabado',         150, null, null],
    ['color',           120, null, null],
    ['ancho_asa_mm',    110, '0', 'Tiene que coincidir con el de la caja.'],
    ['ancho_cierre_mm', 120, '0', 'Cuánto estrecha hacia el cierre. Un buen taper se nota.'],
    ['eslabones_macizos',140, null, 'RECHAZAR huecos: es el defecto típico de la gama barata.'],
    ['endlinks_macizos',140, null, 'La pieza que une con la caja. Donde más se ve un brazalete malo.'],
    ['tipo_cierre',     160, null, 'Desplegable con seguridad, hebilla, mariposa…'],
    ['micro_ajuste',    120, null, 'Si el cierre se ajusta fino sin quitar eslabones.'],
    ['longitud_mm',     110, '0', null],
    ['integrado',       110, null, 'Si solo vale para SU caja.'],
    ['desc_web',        260, null, null],
  ],

  'MODELOS': [
    ['id_modelo',       110, null, 'LO-01, LO-05…'],
    ['nombre',          140, null, null],
    ['slug',            120, null, 'La dirección: laora.es/lunar → «lunar».'],
    ['papel',           120, null, 'Qué hace en el catálogo: entrada, volumen o firma. Si dos modelos tienen el mismo papel, sobra uno.'],
    ['relato_corto',    340, null, 'De qué va este reloj en una frase. De aquí sale el texto de la ficha.'],
    ['publico',         240, null, null],
    ['competencia_marca',150, null, 'Contra quién compite de verdad. Interno.'],
    ['competencia_modelo',170, null, null],
    ['competencia_precio',130, EUR, 'A cuánto lo vende. ESTE es el techo. Sin esta columna la hoja solo sabe calcular hacia arriba desde el coste, y así salen precios que el mercado no paga.'],
    ['estado',          110, null, null],
    ['notas',           280, null, null],
  ],

  'REFERENCIAS': [
    ['ref',             180, null, 'Lo que se vende. LO-07_Bitacora_A01.'],
    ['id_modelo',       110, null, null],
    ['acabado',         110, null, null],
    ['id_movimiento',   140, null, 'De aquí en adelante NO se describe nada: solo se apunta al id de COMPONENTES. La descripción vive allí.'],
    ['id_caja',         140, null, null],
    ['id_esfera',       140, null, null],
    ['id_agujas',       140, null, null],
    ['id_cristal',      140, null, null],
    ['id_corona',       140, null, null],
    ['id_fondo',        140, null, null],
    ['id_correa',       140, null, null],
    ['id_brazalete',    140, null, null],
    ['id_packaging',    140, null, null],
    ['estado',          110, null, 'Solo las «activa» se publican.'],
    ['foto',            240, null, null],
    ['notas',           260, null, null],
  ],

  // La cascada entera, de lo que cuesta a lo que queda limpio en el bolsillo.
  'PRECIOS': [
    ['ref',             180, null, null],
    ['modelo',          130, null, null],
    ['acabado',         110, null, null],
    ['coste_piezas',    110, EUR, 'La suma de las diez piezas, mirando el coste en COMPONENTES.'],
    ['coste_ajustado',  120, EUR, 'El coste con el colchón de inflación encima. Se calcula con este, no con el de hoy.'],
    ['costes_directos', 120, EUR, 'Packaging + envío + montaje y control + provisión de garantía. Lo que cuesta cada reloj además de sus piezas.'],
    ['pvp_propuesto',   120, EUR, 'El multiplicador aplicado al coste total, redondeado al x9,90 siguiente. Se puede escribir encima a mano.'],
    ['techo_mercado',   120, EUR, 'Lo que cobra la competencia por el equivalente.'],
    ['base_sin_iva',    120, EUR, 'Lo que queda del PVP al quitarle el impuesto. El impuesto no es tuyo: lo cobras y lo ingresas.'],
    ['comision',        110, EUR, 'Lo que se lleva la pasarela de cobro.'],
    ['devoluciones',    110, EUR, null],
    ['beneficio',       120, EUR, 'El rendimiento antes de impuestos. SOBRE ESTO se calcula el IRPF, no sobre la venta.'],
    ['irpf',            100, EUR, null],
    ['seg_social',      110, EUR, 'Según ss_modo. En modo «cuota» es la parte de tu cuota de autónomo que le toca a este reloj: cuota_ss_mes ÷ unidades_mes.'],
    ['limpio',          120, EUR, '★ LO QUE TE QUEDA. Después de piezas, gastos, impuesto, comisión, IRPF y Seguridad Social.'],
    ['limpio_pct',      100, PCT, 'Lo limpio como parte del PVP.'],
    ['multiplicador',   110, '0.00', 'A cuánto estás vendiendo sobre lo que cuestan las piezas.'],
    ['revision',        320, null, 'Dice OK, o dice qué falla.'],
  ],

  'COMPRAS': [
    ['id_componente',   130, null, null],
    ['desc_compra',     300, null, null],
    ['tipo',            110, null, null],
    ['coste_ud',        100, EUR, null],
    ['usado_en_refs',   120, '0', 'En cuántas referencias entra. Un componente con 0 es dinero parado sin motivo.'],
    ['stock_actual',    110, '0', '← ESTA LA ESCRIBES TÚ. Lo que tienes en el cajón.'],
    ['moq',              70, '0', null],
    ['coste_pedido_min',130, EUR, 'Lo que cuesta el pedido mínimo. Para las esferas, 10 × su precio.'],
    ['plazo_dias',       90, '0', null],
    ['inmovilizado',    120, EUR, 'Lo que tienes parado en esa pieza.'],
    ['estado',          120, null, null],
    ['notas',           260, null, null],
  ],

  // Lo ÚNICO que lee el generador de la web. Ni una columna de coste.
  'WEB': [
    ['ref',             180, null, 'Esta pestaña es lo único que lee el generador. No tiene ni una columna de coste, así que no puede escaparse nada interno.'],
    ['slug_modelo',     120, null, null],
    ['modelo',          130, null, null],
    ['acabado',         110, null, null],
    ['pvp',             100, EUR, null],
    ['movimiento',      220, null, null],
    ['calibre',         120, null, null],
    ['tipo_movimiento', 130, null, null],
    ['frecuencia_ah',   110, '#,##0', null],
    ['joyas',            70, '0', null],
    ['reserva_h',        90, '0', null],
    ['calendario',      120, null, null],
    ['caja',            240, null, null],
    ['caja_material',   150, null, null],
    ['diametro_mm',     100, '0.0', null],
    ['grosor_mm',       100, '0.00', null],
    ['l2l_mm',           90, '0.0', null],
    ['ancho_asa_mm',    110, '0', null],
    ['estanqueidad_m',  120, '0', null],
    ['cristal',         180, null, null],
    ['esfera',          240, null, null],
    ['esfera_color',    120, null, null],
    ['indices',         150, null, null],
    ['lume',             90, null, null],
    ['agujas',          200, null, null],
    ['correa',          220, null, null],
    ['correa_estilo',   140, null, null],
    ['cierre',          160, null, null],
    ['foto',            240, null, null],
    ['publicar',         90, null, null],
  ],
};


/* Listas cerradas. Sin esto vuelven los «balístico» y «balistico». */
const SI_NO = ['sí', 'no'];
const VALIDACIONES = {
  'COMPONENTES': {
    'tipo': ['movimiento', 'caja', 'esfera', 'agujas', 'cristal', 'corona',
             'fondo', 'correa', 'brazalete', 'bisel', 'junta', 'packaging', 'otro'],
    'verificado': ['sí', 'no', 'estimado'],
    'estado': ['buscando', 'candidato', 'muestra pedida', 'validado', 'descartado'],
    'activo': SI_NO,
  },
  'MOVIMIENTOS': {
    'tipo': ['automático', 'cuerda manual', 'cuarzo', 'mecacuarzo', 'solar'],
    'para_segundero': SI_NO,
    'cuerda_manual': SI_NO,
    'calendario': ['sin fecha', 'fecha', 'día y fecha', 'GMT', 'cronógrafo'],
    'compat_caja_nh35': ['directo', 'espaciador', 'no entra'],
  },
  'CAJAS': {
    'corona_tipo': ['roscada', 'de presión'],
    'integrado': SI_NO,
  },
  'ESFERAS': {
    'indices': ['aplicados', 'impresos', 'mixtos'],
    'lume': SI_NO,
    'ventanilla_fecha': SI_NO,
    'logo_3d': SI_NO,
    'esteril': SI_NO,
  },
  'CORREAS': {
    'tipo': ['brazalete', 'correa'],
    'eslabones_macizos': SI_NO,
    'endlinks_macizos': SI_NO,
    'micro_ajuste': SI_NO,
    'integrado': SI_NO,
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
   LA SIEMBRA · los movimientos de la tarde del 06/08/2026
   ============================================================
   Precios comprobados por Óscar en AliExpress ese día, ordenando por
   pedidos y quedándose con los más vendidos y mejor valorados.

   Una celda vacía es una celda que NO SABEMOS. No se rellena a ojo:
   antes sin dato que con un dato inventado.
*/
const HOY = '06/08/2026';

// id · nombre · desc_compra · desc_web · coste · verificado · notas
const MOV_COMPONENTE = [
  ['MOV-NH35A',  'Seiko NH35A',      'Seiko NH35A automatic movement (Japan)',        'Seiko NH35A',        61.99, 'sí',       'Mercado 60-67 €. NO hay sobreprecio: es lo que vale. Lo monta todo el mundo.'],
  ['MOV-NH36A',  'Seiko NH36A',      'Seiko NH36A day-date automatic movement',       'Seiko NH36A',        65.23, 'sí',       'El NH35 con día además de fecha.'],
  ['MOV-NH34',   'Seiko NH34 GMT',   'Seiko NH34 GMT movement',                       'Seiko NH34 GMT',     55.00, 'estimado', 'Rango 45-70 €. GMT de oficina: se ajusta la aguja de 24 h, no la hora local.'],
  ['MOV-PT5000', 'Peacock PT5000',   'PT5000 automatic movement 25 jewels',           'Peacock PT5000',     56.15, 'sí',       'Cuesta lo mismo que un NH35 y late más fino. El cambio sale gratis.'],
  ['MOV-ST2130', 'Seagull ST2130',   'Seagull ST2130 automatic movement',             'Seagull ST2130',     47.39, 'sí',       'El más barato de los buenos, y ya lo compras.'],
  ['MOV-ST36',   'Seagull ST36',     'Seagull ST3600 6497 hand winding movement',     'Seagull ST36',       30.59, 'sí',       '31 € y NADIE lo monta: Pagani no vende cuerda manual. 36,6 mm: NO entra en caja de NH35, necesita caja propia.'],
  ['MOV-ST1901', 'Seagull ST1901',   'Seagull ST1901 column wheel chronograph',       'Seagull ST1901',    115.00, 'estimado', 'Rango 90-140 €. Cronógrafo de rueda de columnas: el movimiento más noble que se puede comprar por ese dinero.'],
  ['MOV-9015',   'Miyota 9015',      'Miyota 9015 automatic movement',                'Miyota 9015',       107.00, 'estimado', 'Rango 104-110 €. ⚠ Es el doble que un PT5000 y NO diferencia de nada: lo usa medio mercado. Revisar si compensa.'],
  ['MOV-9039',   'Miyota 9039',      'Miyota 9039 no date automatic movement',        'Miyota 9039',       126.99, 'sí',       '⚠ Caro y ESCASO: 15-20 unidades vendidas en AliExpress. Buscar proveedor especializado o descartar.'],
  ['MOV-8215',   'Miyota 8215',      'Miyota 8215 automatic movement',                'Miyota 8215',        20.00, 'estimado', 'Rango 15-25 €. NO para el segundero. Viejo y basto: valorar quitarlo.'],
  ['MOV-VH31',   'Seiko VH31',       'Seiko VH31 sweep quartz movement',              'Seiko VH31',         16.00, 'estimado', 'Rango 12-20 €. Segundero a 4 pasos por segundo: casi parece automático.'],
  ['MOV-VK63',   'Seiko VK63',       'Seiko VK63 meca-quartz chronograph movement',   'Seiko VK63',         32.00, 'estimado', 'Rango 25-40 €. Mecacuarzo: la aguja del crono arranca y vuelve a cero de golpe.'],
  ['MOV-R715',   'Ronda 715',        'Ronda 715 swiss quartz movement',               'Ronda 715',          12.59, 'sí',       '★ Cuesta LO MISMO que el VH31 japonés y permite decir «movimiento suizo». Comprobar antes la letra pequeña: «Swiss made» y «Swiss movement» no son lo mismo. Volúmenes bajos: tener dos vendedores.'],
  ['MOV-R5030',  'Ronda 5030.D',     'Ronda 5030.D swiss quartz chronograph',         'Ronda 5030.D',       75.00, 'estimado', 'Rango 60-90 €. Cronógrafo suizo.'],
  ['MOV-OS20',   'Miyota OS20',      'Miyota OS20 quartz chronograph movement',       'Miyota OS20',        11.00, 'estimado', 'Rango 8-15 €. Crono de cuarzo normal: se nota la diferencia con el VK.'],
  ['MOV-2035',   'Miyota 2035',      'Miyota 2035 quartz movement',                   'Miyota 2035',         2.00, 'estimado', 'El cuarzo más vendido del planeta y el de la gama de 60 €. NO usar.'],
];

// id · calibre · fabricante · país · tipo · frec · joyas · reserva · precisión ·
// hacking · cuerda · calendario · pos.fecha · subesferas · Ø · alto · compat · arquitectura · repuestos · notas · desc_web
const MOV_SPECS = [
  ['MOV-NH35A', 'NH35A', 'Seiko Time Module', 'Japón', 'automático', 21600, 24, 41, '-20/+40 s/día', 'sí', 'sí', 'fecha', 'a las 3', '', 27.4, 5.32, 'directo', 'Seiko NH', 'abundantes', 'No se repara: se sustituye. Una revisión cuesta más que el movimiento nuevo.', 'Seiko NH35A'],
  ['MOV-NH36A', 'NH36A', 'Seiko Time Module', 'Japón', 'automático', 21600, 24, 41, '-20/+40 s/día', 'sí', 'sí', 'día y fecha', 'a las 3', '', 27.4, 5.32, 'directo', 'Seiko NH', 'abundantes', 'Igual que el NH35A.', 'Seiko NH36A'],
  ['MOV-NH34', 'NH34', 'Seiko Time Module', 'Japón', 'automático', 21600, 24, 41, '-20/+40 s/día', 'sí', 'sí', 'GMT', 'a las 3', '', 27.4, '', 'directo', 'Seiko NH', 'abundantes', '', 'Seiko NH34 GMT'],
  ['MOV-PT5000', 'PT5000', 'Peacock (Liaoning)', 'China', 'automático', 28800, 25, 41, '', 'sí', 'sí', 'fecha', 'a las 3', '', 25.6, 4.60, 'espaciador', 'ETA 2824-2', 'intercambiables en buena parte con 2824', 'SÍ se repara: la arquitectura 2824 es la que más se trabaja en talleres de todo el mundo. Muchos vienen ya regulados.', 'Peacock PT5000'],
  ['MOV-ST2130', 'ST2130', 'Tianjin Seagull', 'China', 'automático', 28800, 25, 38, '', 'sí', 'sí', 'fecha', 'a las 3', '', 25.6, 4.60, 'espaciador', 'ETA 2824-2', 'intercambiables en buena parte con 2824', 'SÍ se repara. Misma arquitectura que el PT5000.', 'Seagull ST2130'],
  ['MOV-ST36', 'ST36 (ST3600)', 'Tianjin Seagull', 'China', 'cuerda manual', 18000, 17, 46, '', 'sí', 'sí', 'sin fecha', '', 'segundero pequeño a las 9', 36.6, 6.00, 'no entra', 'ETA 6497', '', 'Calibre grande y visible: pide fondo transparente. Necesita caja de 42-44 mm propia.', 'Seagull ST36'],
  ['MOV-ST1901', 'ST1901', 'Tianjin Seagull', 'China', 'cuerda manual', 21600, 21, 45, '', '', 'sí', 'cronógrafo', '', '2 registros', 27.4, '', 'no entra', 'rueda de columnas', '', 'Necesita caja de cronógrafo con pulsadores. Exige control al recibirlo.', 'Seagull ST1901'],
  ['MOV-9015', '9015', 'Miyota (Citizen)', 'Japón', 'automático', 28800, 24, 42, '-10/+30 s/día', 'sí', 'sí', 'fecha', 'a las 3', '', 26.0, 3.90, 'espaciador', 'Miyota 9', '', 'Muy plano: para relojes finos. Fama de rotor ruidoso. Ojo: la ventanilla de fecha no cae donde la del NH35, la esfera tiene que ser suya.', 'Miyota 9015'],
  ['MOV-9039', '9039', 'Miyota (Citizen)', 'Japón', 'automático', 28800, 24, 42, '-10/+30 s/día', 'sí', 'sí', 'sin fecha', '', '', 26.0, 3.90, 'espaciador', 'Miyota 9', 'escasos', 'El 9015 sin fecha: para esferas limpias sin ventanilla.', 'Miyota 9039'],
  ['MOV-8215', '8215', 'Miyota (Citizen)', 'Japón', 'automático', 21600, 21, 42, '', 'no', 'no', 'fecha', 'a las 3', '', 26.0, 5.67, 'espaciador', 'Miyota 8', 'abundantes', 'NO para el segundero y NO admite cuerda a mano.', 'Miyota 8215'],
  ['MOV-VH31', 'VH31', 'Seiko Time Module', 'Japón', 'cuarzo', '', '', '', '', '', '', 'sin fecha', '', '', '', '', 'espaciador', 'Seiko VH', '', 'Segundero a 4 pasos por segundo: de lejos parece automático.', 'Seiko VH31'],
  ['MOV-VK63', 'VK63', 'Seiko Time Module', 'Japón', 'mecacuarzo', '', '', '', '±15 s/mes', '', '', 'cronógrafo', '', '3 registros', '', '', '', 'Seiko VK', '', 'La aguja del cronógrafo arranca y vuelve a cero de golpe, como un mecánico. La hora la lleva un cuarzo.', 'Seiko VK63'],
  ['MOV-R715', '715', 'Ronda', 'Suiza', 'cuarzo', '', '', '', '', '', '', 'fecha', 'a las 3', '', '', '', '', 'Ronda 700', '', 'Segundero a saltos de segundo entero: cambias el barrido del VH31 por poder decir «suizo».', 'Ronda 715'],
  ['MOV-R5030', '5030.D', 'Ronda', 'Suiza', 'cuarzo', '', '', '', '', '', '', 'cronógrafo', '', '3 registros', '', '', '', 'Ronda 5030', '', '', 'Ronda 5030.D'],
  ['MOV-OS20', 'OS20', 'Miyota (Citizen)', 'Japón', 'cuarzo', '', '', '', '', '', '', 'cronógrafo', '', '', '', '', '', 'Miyota OS', '', '', 'Miyota OS20'],
  ['MOV-2035', '2035', 'Miyota (Citizen)', 'Japón', 'cuarzo', '', '', '', '', '', '', 'sin fecha', '', '', '', '', '', 'Miyota 20', 'abundantes', 'Un año de pila y segundero a saltos. Es lo que monta la gama de 60 €.', 'Miyota 2035'],
];


/* ============================================================
   Utilidades
   ============================================================ */

function col(clave, titulo) {
  const defs = COLUMNAS[clave];
  for (let i = 0; i < defs.length; i++) if (defs[i][0] === titulo) return i + 1;
  throw new Error('No existe la columna «' + titulo + '» en ' + clave);
}

function letra(n) {
  let s = '';
  while (n > 0) { const r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = (n - r - 1) / 26; }
  return s;
}

/** El cinturón: esto SOLO se ejecuta en un libro nuevo. */
function comprobarLibroVacio(ss) {
  const ocupadas = ss.getSheets().filter(function (h) {
    return HOJAS.indexOf(h.getName()) < 0 && h.getLastRow() > 0;
  }).map(function (h) { return h.getName(); });

  if (ocupadas.length) {
    throw new Error(
      'Este libro tiene pestañas con datos que no son de la biblioteca: ' +
      ocupadas.join(', ') + '. Este guion es para un LIBRO NUEVO y vacío.');
  }
}

function rehacer(ss, nombre) {
  const vieja = ss.getSheetByName(nombre);
  if (vieja) ss.deleteSheet(vieja);
  return ss.insertSheet(nombre);
}


/* ============================================================
   El montaje
   ============================================================ */

function montarBiblioteca() {
  const ss = SpreadsheetApp.getActive();
  comprobarLibroVacio(ss);

  montarParametros(ss);
  ['COMPONENTES', 'MOVIMIENTOS', 'CAJAS', 'ESFERAS', 'CORREAS', 'MODELOS',
   'REFERENCIAS', 'PRECIOS', 'COMPRAS', 'WEB'].forEach(function (c) { montarTabla(ss, c); });

  formulasPrecios(ss);
  formulasCompras(ss);
  formulasWeb(ss);
  sembrarMovimientos(ss);

  // fuera la pestaña vacía que trae todo libro nuevo
  ss.getSheets().forEach(function (h) {
    if (HOJAS.indexOf(h.getName()) < 0 && h.getLastRow() === 0) {
      Logger.log('  (quitada la pestaña vacía «' + h.getName() + '»)');
      ss.deleteSheet(h);
    }
  });

  ss.setActiveSheet(ss.getSheetByName('PARAMETROS'));

  Logger.log('');
  Logger.log('✔ Biblioteca montada: ' + HOJAS.join(' · '));
  Logger.log('  Los movimientos ya están dentro. Lo siguiente son las CAJAS:');
  Logger.log('  sin caja no hay reloj, y es la segunda pieza más cara.');
}


function montarParametros(ss) {
  const h = rehacer(ss, 'PARAMETROS');
  const cab = ['Parámetro', 'Valor', 'Unidad', 'Qué es', 'Nombre en fórmulas'];

  h.getRange(1, 1, 1, cab.length).setValues([cab])
    .setFontWeight('bold').setFontColor('#ffffff').setBackground(AZUL);

  h.getRange(2, 1, PARAMETROS.length, 5).setValues(
    PARAMETROS.map(function (p) { return [p[0], p[1], p[2], p[3], p[0]]; }));

  PARAMETROS.forEach(function (p, i) {
    const c = h.getRange(i + 2, 2);
    if (typeof p[1] === 'string')        c.setNumberFormat('@');
    else if (p[2] === '€' || p[2] === '€/mes') c.setNumberFormat(EUR);
    else if (p[2] === 'tanto por uno')   c.setNumberFormat('0.00%');
    else if (p[2] === 'veces')           c.setNumberFormat('0.00');
    else                                 c.setNumberFormat('#,##0');

    // ss_modo es una de dos palabras, no cualquier cosa
    if (p[0] === 'ss_modo') {
      c.setDataValidation(SpreadsheetApp.newDataValidation()
        .requireValueInList(['porcentaje', 'cuota'], true)
        .setAllowInvalid(false).build());
    }
  });

  h.getRange(2, 2, PARAMETROS.length, 1).setBackground(AMARILLO);
  h.setColumnWidth(1, 180); h.setColumnWidth(2, 100);
  h.setColumnWidth(3, 110); h.setColumnWidth(4, 620); h.setColumnWidth(5, 180);
  h.getRange(1, 4, PARAMETROS.length + 1, 1).setWrap(true);
  h.setFrozenRows(1);

  ss.getNamedRanges().forEach(function (r) {
    if (PARAMETROS.some(function (p) { return p[0] === r.getName(); })) r.remove();
  });
  PARAMETROS.forEach(function (p, i) { ss.setNamedRange(p[0], h.getRange(i + 2, 2)); });

  Logger.log('✔ PARAMETROS · ' + PARAMETROS.length + ' valores con nombre');
  Logger.log('  ⚠ impuesto_venta está a 0,21 provisionalmente. Hay que decidirlo:');
  Logger.log('    Canarias, IGIC y el REPEP del 01/07/2026.');
}


function montarTabla(ss, clave) {
  const h = rehacer(ss, clave);
  const defs = COLUMNAS[clave];
  const calculada = ['PRECIOS', 'COMPRAS', 'WEB'].indexOf(clave) >= 0;
  const filas = (clave === 'COMPONENTES' || clave === 'COMPRAS') ? FILAS_COMP : FILAS;

  h.getRange(1, 1, 1, defs.length)
    .setValues([defs.map(function (d) { return d[0]; })])
    .setFontWeight('bold').setFontColor('#ffffff')
    .setBackground(calculada ? GRIS : AZUL);

  defs.forEach(function (d, i) {
    h.setColumnWidth(i + 1, d[1]);
    if (d[2]) h.getRange(2, i + 1, filas, 1).setNumberFormat(d[2]);
    if (d[3]) h.getRange(1, i + 1).setNote(d[3]);
  });

  if (calculada) h.getRange(2, 1, filas, defs.length).setBackground(CALCULADA);

  const vals = VALIDACIONES[clave];
  if (vals) {
    Object.keys(vals).forEach(function (titulo) {
      const regla = SpreadsheetApp.newDataValidation()
        .requireValueInList(vals[titulo], true).setAllowInvalid(false).build();
      h.getRange(2, col(clave, titulo), filas, 1).setDataValidation(regla);
    });
  }

  h.setFrozenRows(1);
  h.setFrozenColumns(1);
  Logger.log('✔ ' + clave + ' · ' + defs.length + ' columnas');
}


/* ============================================================
   Las fórmulas
   ============================================================ */

function formulasPrecios(ss) {
  const h = ss.getSheetByName('PRECIOS');
  const COSTE = letra(col('COMPONENTES', 'coste_ud'));

  const desde = col('REFERENCIAS', 'id_movimiento');
  const hasta = col('REFERENCIAS', 'id_packaging');
  const sumas = [];
  for (let c = desde; c <= hasta; c++) {
    sumas.push('SUMIF(COMPONENTES!$A$2:$A$' + FILAS_COMP + ',REFERENCIAS!' + letra(c) +
               '2,COMPONENTES!$' + COSTE + '$2:$' + COSTE + '$' + FILAS_COMP + ')');
  }

  const f = {
    'ref':            '=IF(REFERENCIAS!A2="","",REFERENCIAS!A2)',
    'modelo':         '=IF($A2="","",IFERROR(VLOOKUP(REFERENCIAS!B2,MODELOS!$A$2:$B$100,2,FALSE),""))',
    'acabado':        '=IF($A2="","",REFERENCIAS!C2)',

    // lo que cuesta
    'coste_piezas':   '=IF($A2="","",' + sumas.join('+') + ')',
    'coste_ajustado': '=IF($A2="","",$D2*(1+colchon_inflacion))',
    'costes_directos':'=IF($A2="","",packaging+envio+montaje_y_control+provision_garantia)',

    // a cuánto se vende. Redondeado al x9,90 siguiente; se puede pisar a mano.
    'pvp_propuesto':  '=IF($A2="","",CEILING(multiplicador*($E2+$F2)-9.9,10)+9.9)',
    'techo_mercado':  '=IF($A2="","",IFERROR(VLOOKUP(REFERENCIAS!B2,MODELOS!$A$2:$I$100,9,FALSE),""))',

    // qué queda de esa venta
    'base_sin_iva':   '=IF($A2="","",$G2/(1+impuesto_venta))',
    'comision':       '=IF($A2="","",comision_pago_pct*$G2+comision_pago_fija)',
    'devoluciones':   '=IF($A2="","",devoluciones_pct*$G2)',
    'beneficio':      '=IF($A2="","",$I2-$J2-$K2-$E2-$F2)',

    // y qué se lleva Hacienda. El IRPF va sobre el beneficio, no sobre la venta.
    'irpf':           '=IF($A2="","",IF($L2>0,irpf*$L2,0))',
    // la Seguridad Social no es un porcentaje: es una cuota mensual repartida
    'seg_social':     '=IF($A2="","",IF(ss_modo="cuota",IFERROR(cuota_ss_mes/MAX(1,unidades_mes),0),IF($L2>0,ss_pct*$L2,0)))',

    'limpio':         '=IF($A2="","",$L2-$M2-$N2)',
    'limpio_pct':     '=IF(OR($A2="",$G2=0),"",$O2/$G2)',
    'multiplicador':  '=IF(OR($A2="",$D2=0),"",$G2/$D2)',

    'revision':       '=IF($A2="","",IF(AND($O2>=limpio_minimo,OR($H2="",$G2<=$H2)),"OK",' +
                      'TRIM(REGEXREPLACE(' +
                      'IF($O2<=0,"⚠ PIERDES DINERO · ",IF($O2<limpio_minimo,"no llega al limpio mínimo · ",""))&' +
                      'IF(AND($H2<>"",$G2>$H2),"por encima del mercado · ","")&' +
                      'IF(AND($Q2<>"",$Q2<2.5),"multiplicador por debajo de x2,5 · ",""),' +
                      '"\\s*·\\s*$",""))))',
  };
  aplicar(h, 'PRECIOS', f, FILAS);
  Logger.log('✔ PRECIOS · coste → PVP → impuesto → comisión → IRPF → SS → LIMPIO');
}


function formulasCompras(ss) {
  const h = ss.getSheetByName('COMPRAS');
  const d = letra(col('REFERENCIAS', 'id_movimiento'));
  const m = letra(col('REFERENCIAS', 'id_packaging'));
  function comp(titulo) { return 'COMPONENTES!' + letra(col('COMPONENTES', titulo)) + '2'; }

  const f = {
    'id_componente':   '=IF(COMPONENTES!A2="","",COMPONENTES!A2)',
    'desc_compra':     '=IF($A2="","",' + comp('desc_compra') + ')',
    'tipo':            '=IF($A2="","",' + comp('tipo') + ')',
    'coste_ud':        '=IF($A2="","",' + comp('coste_ud') + ')',
    'usado_en_refs':   '=IF($A2="","",COUNTIF(REFERENCIAS!$' + d + '$2:$' + m + '$' + FILAS + ',$A2))',
    // stock_actual se escribe a mano: no lleva fórmula
    'moq':             '=IF($A2="","",' + comp('moq') + ')',
    'coste_pedido_min':'=IF($A2="","",$D2*$G2)',
    'plazo_dias':      '=IF($A2="","",' + comp('plazo_dias') + ')',
    'inmovilizado':    '=IF($A2="","",$D2*N($F2))',
    'estado':          '=IF($A2="","",' + comp('estado') + ')',
  };
  aplicar(h, 'COMPRAS', f, FILAS_COMP);
  h.getRange(2, col('COMPRAS', 'stock_actual'), FILAS_COMP, 1).setBackground(AMARILLO);
  Logger.log('✔ COMPRAS · stock_actual se escribe a mano; lo demás sale solo');
}


function formulasWeb(ss) {
  const h = ss.getSheetByName('WEB');
  const RANGO_C = 'COMPONENTES!$A$2:$' + letra(COLUMNAS['COMPONENTES'].length) + '$' + FILAS_COMP;
  const DESC = col('COMPONENTES', 'desc_web');

  // la desc_web de la pieza a la que apunta la referencia
  function pieza(ranura) {
    return '=IF($A2="","",IFERROR(VLOOKUP(REFERENCIAS!' +
           letra(col('REFERENCIAS', ranura)) + '2,' + RANGO_C + ',' + DESC + ',FALSE),""))';
  }
  // una spec de la pestaña de familia (MOVIMIENTOS, CAJAS, ESFERAS, CORREAS)
  function spec(familia, ranura, titulo) {
    const ancho = COLUMNAS[familia].length;
    return '=IF($A2="","",IFERROR(VLOOKUP(REFERENCIAS!' +
           letra(col('REFERENCIAS', ranura)) + '2,' + familia + '!$A$2:$' +
           letra(ancho) + '$' + FILAS + ',' + col(familia, titulo) + ',FALSE),""))';
  }

  const f = {
    'ref':            '=IF(REFERENCIAS!A2="","",REFERENCIAS!A2)',
    'slug_modelo':    '=IF($A2="","",IFERROR(VLOOKUP(REFERENCIAS!B2,MODELOS!$A$2:$C$100,3,FALSE),""))',
    'modelo':         '=IF($A2="","",IFERROR(VLOOKUP(REFERENCIAS!B2,MODELOS!$A$2:$B$100,2,FALSE),""))',
    'acabado':        '=IF($A2="","",REFERENCIAS!C2)',
    'pvp':            '=IF($A2="","",PRECIOS!' + letra(col('PRECIOS', 'pvp_propuesto')) + '2)',

    'movimiento':     pieza('id_movimiento'),
    'calibre':        spec('MOVIMIENTOS', 'id_movimiento', 'calibre'),
    'tipo_movimiento':spec('MOVIMIENTOS', 'id_movimiento', 'tipo'),
    'frecuencia_ah':  spec('MOVIMIENTOS', 'id_movimiento', 'frecuencia_ah'),
    'joyas':          spec('MOVIMIENTOS', 'id_movimiento', 'joyas'),
    'reserva_h':      spec('MOVIMIENTOS', 'id_movimiento', 'reserva_h'),
    'calendario':     spec('MOVIMIENTOS', 'id_movimiento', 'calendario'),

    'caja':           pieza('id_caja'),
    'caja_material':  spec('CAJAS', 'id_caja', 'material'),
    'diametro_mm':    spec('CAJAS', 'id_caja', 'diametro_mm'),
    'grosor_mm':      spec('CAJAS', 'id_caja', 'grosor_mm'),
    'l2l_mm':         spec('CAJAS', 'id_caja', 'l2l_mm'),
    'ancho_asa_mm':   spec('CAJAS', 'id_caja', 'ancho_asa_mm'),
    'estanqueidad_m': spec('CAJAS', 'id_caja', 'estanqueidad_m'),
    'cristal':        pieza('id_cristal'),

    'esfera':         pieza('id_esfera'),
    'esfera_color':   spec('ESFERAS', 'id_esfera', 'color'),
    'indices':        spec('ESFERAS', 'id_esfera', 'indices'),
    'lume':           spec('ESFERAS', 'id_esfera', 'lume'),
    'agujas':         pieza('id_agujas'),

    'correa':         pieza('id_correa'),
    'correa_estilo':  spec('CORREAS', 'id_correa', 'estilo'),
    'cierre':         spec('CORREAS', 'id_correa', 'tipo_cierre'),

    'foto':           '=IF($A2="","",REFERENCIAS!' + letra(col('REFERENCIAS', 'foto')) + '2)',
    'publicar':       '=IF($A2="","",REFERENCIAS!' + letra(col('REFERENCIAS', 'estado')) + '2="activa")',
  };
  aplicar(h, 'WEB', f, FILAS);
  Logger.log('✔ WEB · ' + COLUMNAS['WEB'].length + ' columnas, todas públicas. Ni una de coste.');
}


function aplicar(destino, clave, formulas, filas) {
  Object.keys(formulas).forEach(function (titulo) {
    const c = col(clave, titulo);
    // Se escribe en la fila 2 y se copia hacia abajo: copiando, Sheets ajusta
    // las referencias fila a fila. (Va en notación con coma; la hoja la
    // traduce sola al «;» de España.)
    const primera = destino.getRange(2, c);
    primera.setFormula(formulas[titulo]);
    if (filas > 1) primera.copyTo(destino.getRange(3, c, filas - 1, 1));
  });
}


/* ============================================================
   La siembra
   ============================================================ */

function sembrarMovimientos(ss) {
  const comp = ss.getSheetByName('COMPONENTES');
  const movs = ss.getSheetByName('MOVIMIENTOS');
  const n = COLUMNAS['COMPONENTES'].length;

  const filas = MOV_COMPONENTE.map(function (m) {
    const fila = new Array(n).fill('');
    fila[col('COMPONENTES', 'id') - 1]             = m[0];
    fila[col('COMPONENTES', 'tipo') - 1]           = 'movimiento';
    fila[col('COMPONENTES', 'nombre_interno') - 1] = m[1];
    fila[col('COMPONENTES', 'desc_compra') - 1]    = m[2];
    fila[col('COMPONENTES', 'desc_web') - 1]       = m[3];
    fila[col('COMPONENTES', 'coste_ud') - 1]       = m[4];
    fila[col('COMPONENTES', 'moq') - 1]            = 1;
    fila[col('COMPONENTES', 'proveedor') - 1]      = 'AliExpress';
    fila[col('COMPONENTES', 'fecha_precio') - 1]   = HOY;
    fila[col('COMPONENTES', 'verificado') - 1]     = m[5];
    fila[col('COMPONENTES', 'estado') - 1]         = m[5] === 'sí' ? 'candidato' : 'buscando';
    fila[col('COMPONENTES', 'activo') - 1]         = 'sí';
    fila[col('COMPONENTES', 'notas_internas') - 1] = m[6];
    return fila;
  });
  comp.getRange(2, 1, filas.length, n).setValues(filas);

  movs.getRange(2, 1, MOV_SPECS.length, COLUMNAS['MOVIMIENTOS'].length)
      .setValues(MOV_SPECS);

  Logger.log('✔ Sembrados ' + MOV_COMPONENTE.length + ' movimientos con sus specs.');
  Logger.log('  Precios comprobados el ' + HOY + '. Los marcados «estimado» son rango,');
  Logger.log('  no precio: hay que confirmarlos antes de fiarse del margen.');
  Logger.log('  Una celda vacía es un dato que NO sabemos. No se rellena a ojo.');
}
