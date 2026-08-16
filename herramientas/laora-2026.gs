/**
 * laOra 2026 · CONSTRUCTOR DEL LIBRO NUEVO
 * ============================================================
 * Generado el 16/08/2026 por Claude a partir del libro viejo, de
 * piezas.json y de los cuatro motores de precio EN PRODUCCIÓN
 * (los 258 PVP verificados al céntimo antes de generar esto).
 *
 * CÓMO USARLO
 *   1. script.google.com → Nuevo proyecto (no hace falta libro).
 *   2. Pega este archivo entero y ejecuta CREAR_LIBRO (autoriza).
 *   3. En «Registro de ejecución» sale la URL del libro nuevo.
 *      Pásasela a Claude para la verificación céntimo a céntimo.
 *
 * EL PRINCIPIO: cada dato UNA vez.
 *   Piezas       → coste y link de cada componente, una fila.
 *   Modelos      → reglas del reloj (logo, suplementos).
 *   Referencias  → el catálogo: solo IDs; coste/PVP/cuenta se
 *                  calculan con UNA fórmula por columna (MAP).
 *   Pedidos/Stock/Ventas/Resumen → logística y negocio.
 * Cambiar el precio de una correa = tocar UNA celda de Piezas.
 */

const HOY = new Date(2026, 7, 16);

const PARAMETROS = [
  ['Multiplicador del PVP', 'P_MULT', 2.7235, 'Coste de piezas × esto, redondeado al 9,90'],
  ['IVA', 'P_IVA', 0.21, ''],
  ['IRPF', 'P_IRPF', 0.20, 'Sobre el beneficio bruto'],
  ['Seguridad Social', 'P_SS', 0.05, 'Aprox. sobre el bruto'],
  ['Suelo de limpio por reloj (€)', 'P_SUELO', 50, 'Ningún reloj deja menos de esto'],
  ['Margen mínimo', 'P_MARGENMIN', 0.15, 'Del suelo porcentual'],
  ['Envío (€, IVA dentro)', 'P_ENVIO', 7, ''],
  ['Embalaje (€, IVA dentro)', 'P_EMBALAJE', 2, ''],
  ['Garantía: portes (€)', 'P_GPORTES', 14, ''],
  ['Garantía: piezas (€)', 'P_GPIEZAS', 5, ''],
  ['Garantía: tasa', 'P_GTASA', 0.05, '(movimiento + portes + piezas) × tasa'],
];

const PIEZAS = [
 [
  "P-001",
  "Movimiento",
  "LO-02",
  "ST2130 automático",
  "Calibre laOra LO_A4026 · arquitectura Suiza ETA 2824-2",
  "",
  50.09,
  "https://es.aliexpress.com/item/1005007137519976.html",
  "",
  0,
  ""
 ],
 [
  "P-002",
  "Movimiento",
  "LO-01, LO-02",
  "Ronda 715 cuarzo",
  "Calibre laOra LO_Q6026",
  "",
  15.05,
  "https://es.aliexpress.com/item/1005007185210188.html",
  "",
  0,
  "En el Precisa incluye el anillo espaciador (1,06)"
 ],
 [
  "P-003",
  "Movimiento",
  "LO-01",
  "PT5000 automático (25 joyas)",
  "Calibre laOra LO_A3826 · arquitectura Suiza ETA 2824-2",
  "",
  61.69,
  "https://es.aliexpress.com/item/1005011867804210.html",
  "",
  0,
  "Precio del 16/08 (subió)"
 ],
 [
  "P-004",
  "Movimiento",
  "LO-04",
  "PT5000 automático (Bitácora)",
  "Calibre laOra LO_A3826",
  "",
  59.01,
  "https://es.aliexpress.com/item/1005011867804210.html",
  "",
  0,
  "Coste con el que se calculó el Bitácora; unificar con P-003 cuando Óscar quiera repasar sus PVP"
 ],
 [
  "P-005",
  "Movimiento",
  "LO-03",
  "Seiko VK63 mecacuarzo",
  "Calibre laOra LO_MQ326 · fabricación japonesa",
  "",
  27.59,
  "https://es.aliexpress.com/item/1005008329410541.html",
  "",
  0,
  ""
 ],
 [
  "P-010",
  "Caja",
  "LO-02",
  "Acero 316 plata 36/39",
  "Acero 316 pulido",
  "36 o 39 mm",
  23.0,
  "https://es.aliexpress.com/item/1005008932757286.html",
  "",
  0,
  "5 ATM · tapa sólida o cristal"
 ],
 [
  "P-011",
  "Caja",
  "LO-02",
  "PVD negra 36/39",
  "Recubrimiento PVD negro",
  "36 o 39 mm",
  23.0,
  "https://es.aliexpress.com/item/1005008932757286.html",
  "",
  0,
  ""
 ],
 [
  "P-012",
  "Caja",
  "LO-02",
  "Bronce 36/39",
  "Bronce",
  "36 o 39 mm",
  23.0,
  "https://es.aliexpress.com/item/1005008932757286.html",
  "",
  0,
  ""
 ],
 [
  "P-013",
  "Caja",
  "LO-02",
  "Titanio 36/39",
  "Titanio hipoalergénico",
  "36 o 39 mm",
  54.39,
  "https://es.aliexpress.com/item/1005005301468458.html",
  "",
  0,
  "20 ATM · siempre tapa sólida"
 ],
 [
  "P-020",
  "Esfera",
  "LO-02",
  "Khaki segundero rojo Ø29",
  "Khaki negra mate, segundero rojo",
  "KR",
  17.29,
  "https://es.aliexpress.com/item/1005005292610859.html",
  "",
  0,
  "Pies para mecánicos; en cuarzo Ronda: pies cortados + adhesivo (decisión 15/08)"
 ],
 [
  "P-021",
  "Esfera",
  "LO-02",
  "Khaki segundero blanco Ø29",
  "Khaki negra mate, segundero blanco",
  "KB",
  17.29,
  "https://es.aliexpress.com/item/1005005292610859.html",
  "",
  0,
  "Ídem P-020"
 ],
 [
  "P-022",
  "Esfera",
  "LO-02",
  "Khaki agujas blancas/plata (bronce y titanio)",
  "Khaki negra mate, agujas blancas y plata",
  "BRZ",
  17.29,
  "",
  "",
  0,
  "LINK PENDIENTE de Óscar"
 ],
 [
  "P-023",
  "Esfera",
  "LO-02",
  "Murph numerales crema",
  "Murph, numerales crema",
  "MA",
  21.19,
  "https://es.aliexpress.com/item/1005012681807350.html",
  "",
  0,
  ""
 ],
 [
  "P-024",
  "Esfera",
  "LO-02",
  "Murph numerales blancos",
  "Murph, numerales blancos",
  "MB",
  21.19,
  "https://es.aliexpress.com/item/1005012681807350.html",
  "",
  0,
  ""
 ],
 [
  "P-030",
  "Correa",
  "LO-02",
  "Nato verde militar",
  "Nato Verde Militar",
  "",
  5.69,
  "https://es.aliexpress.com/item/1005010228796680.html",
  "",
  0,
  "Hebilla clásica plateada"
 ],
 [
  "P-031",
  "Correa",
  "LO-02",
  "Nato negro",
  "Nato Negro",
  "",
  5.69,
  "https://es.aliexpress.com/item/1005010228796680.html",
  "",
  0,
  ""
 ],
 [
  "P-032",
  "Correa",
  "LO-02",
  "Piel negra pespunte blanco",
  "Piel Genuina Negra",
  "",
  13.69,
  "https://es.aliexpress.com/item/1005005192599430.html",
  "",
  0,
  "Vaca italiana, encerada"
 ],
 [
  "P-033",
  "Correa",
  "LO-02",
  "Piel marrón claro",
  "Piel Genuina Marrón",
  "",
  13.69,
  "https://es.aliexpress.com/item/1005005192599430.html",
  "",
  0,
  ""
 ],
 [
  "P-034",
  "Correa",
  "LO-02",
  "Piel ante (bronce)",
  "Piel Ante Marrón Claro",
  "",
  4.3,
  "https://es.aliexpress.com/item/1005007894134908.html",
  "",
  0,
  ""
 ],
 [
  "P-035",
  "Correa",
  "LO-02",
  "Piel marrón oscuro (titanio)",
  "Piel Marrón Oscuro",
  "",
  4.69,
  "https://es.aliexpress.com/item/1005010813070667.html",
  "",
  0,
  "3 mm, pespunte claro"
 ],
 [
  "P-036",
  "Correa",
  "LO-02",
  "Brazalete acero 3 eslabones",
  "Brazalete Acero 316L",
  "",
  21.99,
  "https://es.aliexpress.com/item/1005006729305423.html",
  "",
  0,
  ""
 ],
 [
  "P-037",
  "Correa",
  "LO-02",
  "Pack piel negra + brazalete",
  "Pack Piel + Brazalete",
  "",
  35.68,
  "https://es.aliexpress.com/item/1005006729305423.html",
  "",
  0,
  "Composite: P-032 montada + P-036"
 ],
 [
  "P-038",
  "Correa",
  "LO-02",
  "Nato + piel genuina (7 colores)",
  "Nato + Piel",
  "Negro/Azul/Rojo/Caqui/Verde/Gris/Naranja",
  4.99,
  "https://es.aliexpress.com/item/1005010518516247.html",
  "P-030",
  10,
  "Se tarifa como el nato + 10 € (regla 16/08)"
 ],
 [
  "P-090",
  "Extra",
  "Todos",
  "Logo laOra",
  "",
  "",
  3.78,
  "",
  "",
  0,
  "Se suma solo en modelos con logo (columna de Modelos)"
 ],
 [
  "P-110",
  "Caja",
  "LO-01",
  "Caja 40 integrada, tapa sólida (cuarzo)",
  "Acero 316L 40 mm, brazalete integrado",
  "10 ATM",
  62.99,
  "https://es.aliexpress.com/item/1005011649275530.html",
  "",
  0,
  ""
 ],
 [
  "P-111",
  "Caja",
  "LO-01",
  "Caja 40 integrada, tapa cristal (automático)",
  "Acero 316L 40 mm, brazalete integrado",
  "20 ATM",
  59.4,
  "https://es.aliexpress.com/item/1005008684803503.html",
  "",
  0,
  ""
 ],
 [
  "P-120",
  "Esfera",
  "LO-01",
  "Esfera waffle Ø31,8 (6 colores)",
  "Esfera con guilloché waffle",
  "AZM/AZD/BLA/NEG/TIF/VER",
  10.39,
  "https://es.aliexpress.com/item/1005008683926798.html",
  "",
  0,
  ""
 ],
 [
  "P-130",
  "Extra",
  "LO-01",
  "Agujas para PT5000",
  "",
  "",
  4.89,
  "https://es.aliexpress.com/item/1005007796436504.html",
  "",
  0,
  "Solo el automático; la esfera trae agujas NH"
 ],
 [
  "P-210",
  "Caja",
  "LO-04",
  "Caja Plata (incluye agujas)",
  "Acero 316 pulido 40 mm",
  "C1",
  29.57,
  "https://es.aliexpress.com/item/1005009334813135.html",
  "",
  0,
  "25,79 caja + agujas; ver pestaña vieja"
 ],
 [
  "P-211",
  "Caja",
  "LO-04",
  "Caja Oro Rosa (incluye agujas)",
  "Acabado oro rosa",
  "C3",
  34.97,
  "https://es.aliexpress.com/item/1005009334813135.html",
  "",
  0,
  ""
 ],
 [
  "P-212",
  "Caja",
  "LO-04",
  "Caja Negra PVD (incluye agujas)",
  "PVD negro",
  "C4",
  34.97,
  "https://es.aliexpress.com/item/1005009334813135.html",
  "",
  0,
  ""
 ],
 [
  "P-220",
  "Esfera",
  "LO-04",
  "Esfera Bitácora (5 colores)",
  "Esfera con surcos horizontales",
  "Turquesa/Blanca/Negra/Azul/Gris",
  21.39,
  "https://es.aliexpress.com/item/1005012653959131.html",
  "",
  0,
  "17,00 esfera + agujas"
 ],
 [
  "P-221",
  "Esfera",
  "LO-04",
  "Esfera Bitácora Marrón",
  "Esfera marrón con surcos",
  "E6",
  25.99,
  "https://es.aliexpress.com/item/1005012653959131.html",
  "",
  0,
  ""
 ],
 [
  "P-230",
  "Correa",
  "LO-04",
  "Acero integrado plata",
  "Acero integrado, cierre plegable",
  "Bit-01",
  21.19,
  "https://es.aliexpress.com/item/1005009252680462.html",
  "",
  0,
  ""
 ],
 [
  "P-231",
  "Correa",
  "LO-04",
  "Acero integrado bicolor plata/oro rosa",
  "Acero integrado bicolor",
  "Bit-07",
  21.19,
  "https://es.aliexpress.com/item/1005009252680462.html",
  "",
  0,
  ""
 ],
 [
  "P-232",
  "Correa",
  "LO-04",
  "Acero integrado oro rosa",
  "Acero integrado oro rosa",
  "Bit-06",
  21.19,
  "https://es.aliexpress.com/item/1005009252680462.html",
  "",
  0,
  ""
 ],
 [
  "P-233",
  "Correa",
  "LO-04",
  "Acero integrado negro PVD",
  "Acero integrado negro",
  "Bit-02",
  21.19,
  "https://es.aliexpress.com/item/1005009252680462.html",
  "",
  0,
  ""
 ],
 [
  "P-234",
  "Correa",
  "LO-04",
  "Silicona negra",
  "Correa de silicona, hebilla mariposa",
  "G01",
  6.39,
  "https://es.aliexpress.com/item/1005008948854215.html",
  "",
  0,
  "OJO: la pestaña vieja Brazeletes la tenía a 9,89 — revisar precio real"
 ],
 [
  "P-235",
  "Correa",
  "LO-04",
  "Silicona azul",
  "Silicona azul",
  "G03",
  6.39,
  "https://es.aliexpress.com/item/1005008948854215.html",
  "",
  0,
  "Ídem 9,89"
 ],
 [
  "P-236",
  "Correa",
  "LO-04",
  "Silicona marrón",
  "Silicona marrón",
  "G04",
  6.39,
  "https://es.aliexpress.com/item/1005008948854215.html",
  "",
  0,
  "Ídem 9,89"
 ],
 [
  "P-310",
  "Caja",
  "LO-03",
  "Pack caja + esfera + agujas (3 versiones)",
  "Acero 316L 40 mm, bisel taquimétrico",
  "Negra/Blanca/Blanca-Azul",
  34.59,
  "https://es.aliexpress.com/item/1005007892634303.html",
  "",
  0,
  "Proveedor nuevo 16/08; sustituye a caja+esfera por separado"
 ],
 [
  "P-330",
  "Correa",
  "LO-03",
  "Caucho MoonSwatch pespunte blanco",
  "Caucho negro, extremo curvado",
  "MS01",
  6.39,
  "https://es.aliexpress.com/item/1005010706660703.html",
  "",
  0,
  ""
 ],
 [
  "P-331",
  "Correa",
  "LO-03",
  "Caucho MoonSwatch texturizado",
  "Caucho negro texturizado",
  "MS02",
  6.39,
  "https://es.aliexpress.com/item/1005010706660703.html",
  "",
  0,
  ""
 ],
 [
  "P-332",
  "Correa",
  "LO-03",
  "Piel perforada pespunte blanco",
  "Piel de vaca perforada",
  "PF01",
  6.79,
  "https://es.aliexpress.com/item/1005009640853583.html",
  "",
  0,
  ""
 ],
 [
  "P-333",
  "Correa",
  "LO-03",
  "Nato + piel beige",
  "Nato + Piel Beige",
  "NP08",
  4.99,
  "https://es.aliexpress.com/item/1005010518516247.html",
  "P-330",
  10,
  "Se tarifa como el caucho + 10 €"
 ],
 [
  "P-334",
  "Correa",
  "LO-03",
  "Acero 5 eslabones",
  "Brazalete de acero 316L, cinco eslabones",
  "A06",
  19.69,
  "https://es.aliexpress.com/item/1005006729305423.html",
  "",
  0,
  "Precio del 16/08"
 ],
 [
  "P-335",
  "Correa",
  "LO-03",
  "Piel negra pespunte blanco",
  "Piel genuina negra, pespunte blanco",
  "P02",
  30.79,
  "https://es.aliexpress.com/item/1005007805649477.html",
  "",
  0,
  "Hebilla clásica plateada"
 ],
 [
  "P-336",
  "Correa",
  "LO-03",
  "Piel negra pespunte negro",
  "Piel genuina negra, pespunte negro",
  "P06",
  31.59,
  "https://es.aliexpress.com/item/1005007805649477.html",
  "",
  0,
  ""
 ]
];

const MODELOS = [
 [
  "LO-01",
  "Precisa",
  "Tissot PRX",
  "SÍ",
  0,
  "Activo"
 ],
 [
  "LO-02",
  "Trinchera",
  "Hamilton Khaki Field (Mechanical y Murph)",
  "SÍ",
  10,
  "Activo"
 ],
 [
  "LO-03",
  "Lunar",
  "Omega Speedmaster Moonwatch",
  "NO",
  0,
  "Activo"
 ],
 [
  "LO-04",
  "Bitácora",
  "Patek Philippe Nautilus",
  "NO",
  0,
  "Activo"
 ]
];

const REFERENCIAS = [["LO-02-A-PL36C-KR-NATO", "LO-02", "P-001", "P-010", "P-020", "P-030", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KR-NATO", "LO-02", "P-001", "P-010", "P-020", "P-030", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KB-NATO", "LO-02", "P-001", "P-010", "P-021", "P-030", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KB-NATO", "LO-02", "P-001", "P-010", "P-021", "P-030", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KR-PIELN", "LO-02", "P-001", "P-010", "P-020", "P-032", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KR-PIELN", "LO-02", "P-001", "P-010", "P-020", "P-032", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KB-PIELN", "LO-02", "P-001", "P-010", "P-021", "P-032", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KB-PIELN", "LO-02", "P-001", "P-010", "P-021", "P-032", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KR-PIELM", "LO-02", "P-001", "P-010", "P-020", "P-033", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KR-PIELM", "LO-02", "P-001", "P-010", "P-020", "P-033", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KB-PIELM", "LO-02", "P-001", "P-010", "P-021", "P-033", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KB-PIELM", "LO-02", "P-001", "P-010", "P-021", "P-033", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KR-ACERO", "LO-02", "P-001", "P-010", "P-020", "P-036", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KR-ACERO", "LO-02", "P-001", "P-010", "P-020", "P-036", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-KB-ACERO", "LO-02", "P-001", "P-010", "P-021", "P-036", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-KB-ACERO", "LO-02", "P-001", "P-010", "P-021", "P-036", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-MA-PACK", "LO-02", "P-001", "P-010", "P-023", "P-037", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-MA-PACK", "LO-02", "P-001", "P-010", "P-023", "P-037", "", "39", "Cristal", "", "Activa"], ["LO-02-A-PL36C-MB-PACK", "LO-02", "P-001", "P-010", "P-024", "P-037", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-MB-PACK", "LO-02", "P-001", "P-010", "P-024", "P-037", "", "39", "Cristal", "", "Activa"], ["LO-02-A-NG36C-KB-NATON", "LO-02", "P-001", "P-011", "P-021", "P-031", "", "36", "Cristal", "", "Activa"], ["LO-02-A-NG39C-KB-NATON", "LO-02", "P-001", "P-011", "P-021", "P-031", "", "39", "Cristal", "", "Activa"], ["LO-02-A-NG36C-KB-PIELN", "LO-02", "P-001", "P-011", "P-021", "P-032", "", "36", "Cristal", "", "Activa"], ["LO-02-A-NG39C-KB-PIELN", "LO-02", "P-001", "P-011", "P-021", "P-032", "", "39", "Cristal", "", "Activa"], ["LO-02-A-BR36C-ANTE", "LO-02", "P-001", "P-012", "P-022", "P-034", "", "36", "Cristal", "", "Activa"], ["LO-02-A-BR39C-ANTE", "LO-02", "P-001", "P-012", "P-022", "P-034", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-PL36S-KR-NATO", "LO-02", "P-002", "P-010", "P-020", "P-030", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KR-NATO", "LO-02", "P-002", "P-010", "P-020", "P-030", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KB-NATO", "LO-02", "P-002", "P-010", "P-021", "P-030", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KB-NATO", "LO-02", "P-002", "P-010", "P-021", "P-030", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KR-PIELN", "LO-02", "P-002", "P-010", "P-020", "P-032", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KR-PIELN", "LO-02", "P-002", "P-010", "P-020", "P-032", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KB-PIELN", "LO-02", "P-002", "P-010", "P-021", "P-032", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KB-PIELN", "LO-02", "P-002", "P-010", "P-021", "P-032", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KR-PIELM", "LO-02", "P-002", "P-010", "P-020", "P-033", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KR-PIELM", "LO-02", "P-002", "P-010", "P-020", "P-033", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KB-PIELM", "LO-02", "P-002", "P-010", "P-021", "P-033", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KB-PIELM", "LO-02", "P-002", "P-010", "P-021", "P-033", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KR-ACERO", "LO-02", "P-002", "P-010", "P-020", "P-036", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KR-ACERO", "LO-02", "P-002", "P-010", "P-020", "P-036", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-KB-ACERO", "LO-02", "P-002", "P-010", "P-021", "P-036", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-KB-ACERO", "LO-02", "P-002", "P-010", "P-021", "P-036", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-MA-PACK", "LO-02", "P-002", "P-010", "P-023", "P-037", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-MA-PACK", "LO-02", "P-002", "P-010", "P-023", "P-037", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-PL36S-MB-PACK", "LO-02", "P-002", "P-010", "P-024", "P-037", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-MB-PACK", "LO-02", "P-002", "P-010", "P-024", "P-037", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-NG36S-KB-NATON", "LO-02", "P-002", "P-011", "P-021", "P-031", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-NG39S-KB-NATON", "LO-02", "P-002", "P-011", "P-021", "P-031", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-NG36S-KB-PIELN", "LO-02", "P-002", "P-011", "P-021", "P-032", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-NG39S-KB-PIELN", "LO-02", "P-002", "P-011", "P-021", "P-032", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-BR36S-ANTE", "LO-02", "P-002", "P-012", "P-022", "P-034", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-BR39S-ANTE", "LO-02", "P-002", "P-012", "P-022", "P-034", "", "39", "Sólida", "", "Activa"], ["LO-02-A-TI36S-BRZ-ANTE", "LO-02", "P-001", "P-013", "P-022", "P-034", "", "36", "Sólida", "", "Activa"], ["LO-02-A-TI39S-BRZ-ANTE", "LO-02", "P-001", "P-013", "P-022", "P-034", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-TI36S-BRZ-ANTE", "LO-02", "P-002", "P-013", "P-022", "P-034", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-TI39S-BRZ-ANTE", "LO-02", "P-002", "P-013", "P-022", "P-034", "", "39", "Sólida", "", "Activa"], ["LO-02-A-TI36S-BRZ-PIELO", "LO-02", "P-001", "P-013", "P-022", "P-035", "", "36", "Sólida", "", "Activa"], ["LO-02-A-TI39S-BRZ-PIELO", "LO-02", "P-001", "P-013", "P-022", "P-035", "", "39", "Sólida", "", "Activa"], ["LO-02-Q-TI36S-BRZ-PIELO", "LO-02", "P-002", "P-013", "P-022", "P-035", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-TI39S-BRZ-PIELO", "LO-02", "P-002", "P-013", "P-022", "P-035", "", "39", "Sólida", "", "Activa"], ["LO-02-A-PL36C-MA-PIELN", "LO-02", "P-001", "P-010", "P-023", "P-032", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-MA-PIELN", "LO-02", "P-001", "P-010", "P-023", "P-032", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-PL36S-MA-PIELN", "LO-02", "P-002", "P-010", "P-023", "P-032", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-MA-PIELN", "LO-02", "P-002", "P-010", "P-023", "P-032", "", "39", "Sólida", "", "Activa"], ["LO-02-A-PL36C-MA-ACERO", "LO-02", "P-001", "P-010", "P-023", "P-036", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-MA-ACERO", "LO-02", "P-001", "P-010", "P-023", "P-036", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-PL36S-MA-ACERO", "LO-02", "P-002", "P-010", "P-023", "P-036", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-MA-ACERO", "LO-02", "P-002", "P-010", "P-023", "P-036", "", "39", "Sólida", "", "Activa"], ["LO-02-A-PL36C-MB-PIELN", "LO-02", "P-001", "P-010", "P-024", "P-032", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-MB-PIELN", "LO-02", "P-001", "P-010", "P-024", "P-032", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-PL36S-MB-PIELN", "LO-02", "P-002", "P-010", "P-024", "P-032", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-MB-PIELN", "LO-02", "P-002", "P-010", "P-024", "P-032", "", "39", "Sólida", "", "Activa"], ["LO-02-A-PL36C-MB-ACERO", "LO-02", "P-001", "P-010", "P-024", "P-036", "", "36", "Cristal", "", "Activa"], ["LO-02-A-PL39C-MB-ACERO", "LO-02", "P-001", "P-010", "P-024", "P-036", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-PL36S-MB-ACERO", "LO-02", "P-002", "P-010", "P-024", "P-036", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-PL39S-MB-ACERO", "LO-02", "P-002", "P-010", "P-024", "P-036", "", "39", "Sólida", "", "Activa"], ["LO-02-A-PL36C-KR-NATOP-NEG", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "NEG", "Activa"], ["LO-02-A-PL39C-KR-NATOP-NEG", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "NEG", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-NEG", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "NEG", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-NEG", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "NEG", "Activa"], ["LO-02-A-PL36C-KR-NATOP-AZU", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "AZU", "Activa"], ["LO-02-A-PL39C-KR-NATOP-AZU", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "AZU", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-AZU", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "AZU", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-AZU", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "AZU", "Activa"], ["LO-02-A-PL36C-KR-NATOP-ROJ", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "ROJ", "Activa"], ["LO-02-A-PL39C-KR-NATOP-ROJ", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "ROJ", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-ROJ", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "ROJ", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-ROJ", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "ROJ", "Activa"], ["LO-02-A-PL36C-KR-NATOP-CAQ", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "CAQ", "Activa"], ["LO-02-A-PL39C-KR-NATOP-CAQ", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "CAQ", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-CAQ", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "CAQ", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-CAQ", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "CAQ", "Activa"], ["LO-02-A-PL36C-KR-NATOP-VER", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "VER", "Activa"], ["LO-02-A-PL39C-KR-NATOP-VER", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "VER", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-VER", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "VER", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-VER", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "VER", "Activa"], ["LO-02-A-PL36C-KR-NATOP-GRI", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "GRI", "Activa"], ["LO-02-A-PL39C-KR-NATOP-GRI", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "GRI", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-GRI", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "GRI", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-GRI", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "GRI", "Activa"], ["LO-02-A-PL36C-KR-NATOP-NAR", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "36", "Cristal", "NAR", "Activa"], ["LO-02-A-PL39C-KR-NATOP-NAR", "LO-02", "P-001", "P-010", "P-020", "P-038", "", "39", "Cristal", "NAR", "Activa"], ["LO-02-Q-PL36S-KR-NATOP-NAR", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "36", "Sólida", "NAR", "Activa"], ["LO-02-Q-PL39S-KR-NATOP-NAR", "LO-02", "P-002", "P-010", "P-020", "P-038", "", "39", "Sólida", "NAR", "Activa"], ["LO-02-A-PL36C-KB-NATOP-NEG", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "NEG", "Activa"], ["LO-02-A-PL39C-KB-NATOP-NEG", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "NEG", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-NEG", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "NEG", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-NEG", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "NEG", "Activa"], ["LO-02-A-PL36C-KB-NATOP-AZU", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "AZU", "Activa"], ["LO-02-A-PL39C-KB-NATOP-AZU", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "AZU", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-AZU", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "AZU", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-AZU", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "AZU", "Activa"], ["LO-02-A-PL36C-KB-NATOP-ROJ", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "ROJ", "Activa"], ["LO-02-A-PL39C-KB-NATOP-ROJ", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "ROJ", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-ROJ", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "ROJ", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-ROJ", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "ROJ", "Activa"], ["LO-02-A-PL36C-KB-NATOP-CAQ", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "CAQ", "Activa"], ["LO-02-A-PL39C-KB-NATOP-CAQ", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "CAQ", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-CAQ", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "CAQ", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-CAQ", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "CAQ", "Activa"], ["LO-02-A-PL36C-KB-NATOP-VER", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "VER", "Activa"], ["LO-02-A-PL39C-KB-NATOP-VER", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "VER", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-VER", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "VER", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-VER", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "VER", "Activa"], ["LO-02-A-PL36C-KB-NATOP-GRI", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "GRI", "Activa"], ["LO-02-A-PL39C-KB-NATOP-GRI", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "GRI", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-GRI", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "GRI", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-GRI", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "GRI", "Activa"], ["LO-02-A-PL36C-KB-NATOP-NAR", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "36", "Cristal", "NAR", "Activa"], ["LO-02-A-PL39C-KB-NATOP-NAR", "LO-02", "P-001", "P-010", "P-021", "P-038", "", "39", "Cristal", "NAR", "Activa"], ["LO-02-Q-PL36S-KB-NATOP-NAR", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "36", "Sólida", "NAR", "Activa"], ["LO-02-Q-PL39S-KB-NATOP-NAR", "LO-02", "P-002", "P-010", "P-021", "P-038", "", "39", "Sólida", "NAR", "Activa"], ["LO-02-A-NG36C-KR-NATON", "LO-02", "P-001", "P-011", "P-020", "P-031", "", "36", "Cristal", "", "Activa"], ["LO-02-A-NG39C-KR-NATON", "LO-02", "P-001", "P-011", "P-020", "P-031", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-NG36S-KR-NATON", "LO-02", "P-002", "P-011", "P-020", "P-031", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-NG39S-KR-NATON", "LO-02", "P-002", "P-011", "P-020", "P-031", "", "39", "Sólida", "", "Activa"], ["LO-02-A-NG36C-KR-PIELN", "LO-02", "P-001", "P-011", "P-020", "P-032", "", "36", "Cristal", "", "Activa"], ["LO-02-A-NG39C-KR-PIELN", "LO-02", "P-001", "P-011", "P-020", "P-032", "", "39", "Cristal", "", "Activa"], ["LO-02-Q-NG36S-KR-PIELN", "LO-02", "P-002", "P-011", "P-020", "P-032", "", "36", "Sólida", "", "Activa"], ["LO-02-Q-NG39S-KR-PIELN", "LO-02", "P-002", "P-011", "P-020", "P-032", "", "39", "Sólida", "", "Activa"], ["LO-02-A-NG36C-KR-NATOP-NEG", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "NEG", "Activa"], ["LO-02-A-NG39C-KR-NATOP-NEG", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "NEG", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-NEG", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "NEG", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-NEG", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "NEG", "Activa"], ["LO-02-A-NG36C-KR-NATOP-AZU", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "AZU", "Activa"], ["LO-02-A-NG39C-KR-NATOP-AZU", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "AZU", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-AZU", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "AZU", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-AZU", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "AZU", "Activa"], ["LO-02-A-NG36C-KR-NATOP-ROJ", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "ROJ", "Activa"], ["LO-02-A-NG39C-KR-NATOP-ROJ", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "ROJ", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-ROJ", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "ROJ", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-ROJ", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "ROJ", "Activa"], ["LO-02-A-NG36C-KR-NATOP-CAQ", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "CAQ", "Activa"], ["LO-02-A-NG39C-KR-NATOP-CAQ", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "CAQ", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-CAQ", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "CAQ", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-CAQ", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "CAQ", "Activa"], ["LO-02-A-NG36C-KR-NATOP-VER", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "VER", "Activa"], ["LO-02-A-NG39C-KR-NATOP-VER", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "VER", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-VER", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "VER", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-VER", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "VER", "Activa"], ["LO-02-A-NG36C-KR-NATOP-GRI", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "GRI", "Activa"], ["LO-02-A-NG39C-KR-NATOP-GRI", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "GRI", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-GRI", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "GRI", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-GRI", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "GRI", "Activa"], ["LO-02-A-NG36C-KR-NATOP-NAR", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "36", "Cristal", "NAR", "Activa"], ["LO-02-A-NG39C-KR-NATOP-NAR", "LO-02", "P-001", "P-011", "P-020", "P-038", "", "39", "Cristal", "NAR", "Activa"], ["LO-02-Q-NG36S-KR-NATOP-NAR", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "36", "Sólida", "NAR", "Activa"], ["LO-02-Q-NG39S-KR-NATOP-NAR", "LO-02", "P-002", "P-011", "P-020", "P-038", "", "39", "Sólida", "NAR", "Activa"], ["LO-02-A-NG36C-KB-NATOP-NEG", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "NEG", "Activa"], ["LO-02-A-NG39C-KB-NATOP-NEG", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "NEG", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-NEG", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "NEG", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-NEG", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "NEG", "Activa"], ["LO-02-A-NG36C-KB-NATOP-AZU", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "AZU", "Activa"], ["LO-02-A-NG39C-KB-NATOP-AZU", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "AZU", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-AZU", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "AZU", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-AZU", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "AZU", "Activa"], ["LO-02-A-NG36C-KB-NATOP-ROJ", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "ROJ", "Activa"], ["LO-02-A-NG39C-KB-NATOP-ROJ", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "ROJ", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-ROJ", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "ROJ", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-ROJ", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "ROJ", "Activa"], ["LO-02-A-NG36C-KB-NATOP-CAQ", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "CAQ", "Activa"], ["LO-02-A-NG39C-KB-NATOP-CAQ", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "CAQ", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-CAQ", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "CAQ", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-CAQ", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "CAQ", "Activa"], ["LO-02-A-NG36C-KB-NATOP-VER", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "VER", "Activa"], ["LO-02-A-NG39C-KB-NATOP-VER", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "VER", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-VER", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "VER", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-VER", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "VER", "Activa"], ["LO-02-A-NG36C-KB-NATOP-GRI", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "GRI", "Activa"], ["LO-02-A-NG39C-KB-NATOP-GRI", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "GRI", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-GRI", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "GRI", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-GRI", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "GRI", "Activa"], ["LO-02-A-NG36C-KB-NATOP-NAR", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "36", "Cristal", "NAR", "Activa"], ["LO-02-A-NG39C-KB-NATOP-NAR", "LO-02", "P-001", "P-011", "P-021", "P-038", "", "39", "Cristal", "NAR", "Activa"], ["LO-02-Q-NG36S-KB-NATOP-NAR", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "36", "Sólida", "NAR", "Activa"], ["LO-02-Q-NG39S-KB-NATOP-NAR", "LO-02", "P-002", "P-011", "P-021", "P-038", "", "39", "Sólida", "NAR", "Activa"], ["LO-01-Q-40S-AZM", "LO-01", "P-002", "P-110", "P-120", "", "", "40", "Sólida", "AZM", "Activa"], ["LO-01-Q-40S-AZD", "LO-01", "P-002", "P-110", "P-120", "", "", "40", "Sólida", "AZD", "Activa"], ["LO-01-Q-40S-BLA", "LO-01", "P-002", "P-110", "P-120", "", "", "40", "Sólida", "BLA", "Activa"], ["LO-01-Q-40S-NEG", "LO-01", "P-002", "P-110", "P-120", "", "", "40", "Sólida", "NEG", "Activa"], ["LO-01-Q-40S-TIF", "LO-01", "P-002", "P-110", "P-120", "", "", "40", "Sólida", "TIF", "Activa"], ["LO-01-Q-40S-VER", "LO-01", "P-002", "P-110", "P-120", "", "", "40", "Sólida", "VER", "Activa"], ["LO-01-A-40C-AZM", "LO-01", "P-003", "P-111", "P-120", "", "P-130", "40", "Cristal", "AZM", "Activa"], ["LO-01-A-40C-AZD", "LO-01", "P-003", "P-111", "P-120", "", "P-130", "40", "Cristal", "AZD", "Activa"], ["LO-01-A-40C-BLA", "LO-01", "P-003", "P-111", "P-120", "", "P-130", "40", "Cristal", "BLA", "Activa"], ["LO-01-A-40C-NEG", "LO-01", "P-003", "P-111", "P-120", "", "P-130", "40", "Cristal", "NEG", "Activa"], ["LO-01-A-40C-TIF", "LO-01", "P-003", "P-111", "P-120", "", "P-130", "40", "Cristal", "TIF", "Activa"], ["LO-01-A-40C-VER", "LO-01", "P-003", "P-111", "P-120", "", "P-130", "40", "Cristal", "VER", "Activa"], ["LO-04-C1-E1-Brz-Acero-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-230", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C1-E1-Brz-Acero-Bit-07", "LO-04", "P-004", "P-210", "P-220", "P-231", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C1-E1-Brz-Goma-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-234", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C1-E1-Brz-Goma-Bit-03", "LO-04", "P-004", "P-210", "P-220", "P-235", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C1-E2-Brz-Acero-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-230", "", "40", "—", "Blanca", "Activa"], ["LO-04-C1-E2-Brz-Acero-Bit-07", "LO-04", "P-004", "P-210", "P-220", "P-231", "", "40", "—", "Blanca", "Activa"], ["LO-04-C1-E2-Brz-Goma-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-234", "", "40", "—", "Blanca", "Activa"], ["LO-04-C1-E2-Brz-Goma-Bit-03", "LO-04", "P-004", "P-210", "P-220", "P-235", "", "40", "—", "Blanca", "Activa"], ["LO-04-C1-E3-Brz-Acero-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-230", "", "40", "—", "Negra", "Activa"], ["LO-04-C1-E3-Brz-Acero-Bit-07", "LO-04", "P-004", "P-210", "P-220", "P-231", "", "40", "—", "Negra", "Activa"], ["LO-04-C1-E3-Brz-Goma-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-234", "", "40", "—", "Negra", "Activa"], ["LO-04-C1-E4-Brz-Acero-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-230", "", "40", "—", "Azul", "Activa"], ["LO-04-C1-E4-Brz-Acero-Bit-07", "LO-04", "P-004", "P-210", "P-220", "P-231", "", "40", "—", "Azul", "Activa"], ["LO-04-C1-E4-Brz-Goma-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-234", "", "40", "—", "Azul", "Activa"], ["LO-04-C1-E4-Brz-Goma-Bit-03", "LO-04", "P-004", "P-210", "P-220", "P-235", "", "40", "—", "Azul", "Activa"], ["LO-04-C1-E5-Brz-Acero-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-230", "", "40", "—", "Gris", "Activa"], ["LO-04-C1-E5-Brz-Acero-Bit-07", "LO-04", "P-004", "P-210", "P-220", "P-231", "", "40", "—", "Gris", "Activa"], ["LO-04-C1-E5-Brz-Goma-Bit-01", "LO-04", "P-004", "P-210", "P-220", "P-234", "", "40", "—", "Gris", "Activa"], ["LO-04-C1-E5-Brz-Goma-Bit-03", "LO-04", "P-004", "P-210", "P-220", "P-235", "", "40", "—", "Gris", "Activa"], ["LO-04-C1-E6-Brz-Acero-Bit-01", "LO-04", "P-004", "P-210", "P-221", "P-230", "", "40", "—", "Marrón", "Activa"], ["LO-04-C3-E1-Brz-Acero-Bit-07", "LO-04", "P-004", "P-211", "P-220", "P-231", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C3-E1-Brz-Acero-Bit-06", "LO-04", "P-004", "P-211", "P-220", "P-232", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C3-E1-Brz-Goma-Bit-04", "LO-04", "P-004", "P-211", "P-220", "P-236", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C3-E2-Brz-Acero-Bit-06", "LO-04", "P-004", "P-211", "P-220", "P-232", "", "40", "—", "Blanca", "Activa"], ["LO-04-C3-E3-Brz-Acero-Bit-06", "LO-04", "P-004", "P-211", "P-220", "P-232", "", "40", "—", "Negra", "Activa"], ["LO-04-C3-E6-Brz-Acero-Bit-07", "LO-04", "P-004", "P-211", "P-221", "P-231", "", "40", "—", "Marrón", "Activa"], ["LO-04-C3-E6-Brz-Acero-Bit-06", "LO-04", "P-004", "P-211", "P-221", "P-232", "", "40", "—", "Marrón", "Activa"], ["LO-04-C3-E6-Brz-Goma-Bit-04", "LO-04", "P-004", "P-211", "P-221", "P-236", "", "40", "—", "Marrón", "Activa"], ["LO-04-C4-E1-Brz-Acero-Bit-02", "LO-04", "P-004", "P-212", "P-220", "P-233", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C4-E1-Brz-Goma-Bit-01", "LO-04", "P-004", "P-212", "P-220", "P-234", "", "40", "—", "Turquesa", "Activa"], ["LO-04-C4-E2-Brz-Acero-Bit-02", "LO-04", "P-004", "P-212", "P-220", "P-233", "", "40", "—", "Blanca", "Activa"], ["LO-04-C4-E2-Brz-Goma-Bit-01", "LO-04", "P-004", "P-212", "P-220", "P-234", "", "40", "—", "Blanca", "Activa"], ["LO-04-C4-E3-Brz-Acero-Bit-02", "LO-04", "P-004", "P-212", "P-220", "P-233", "", "40", "—", "Negra", "Activa"], ["LO-04-C4-E3-Brz-Goma-Bit-01", "LO-04", "P-004", "P-212", "P-220", "P-234", "", "40", "—", "Negra", "Activa"], ["LO-04-C4-E5-Brz-Acero-Bit-02", "LO-04", "P-004", "P-212", "P-220", "P-233", "", "40", "—", "Gris", "Activa"], ["LO-04-C4-E5-Brz-Goma-Bit-01", "LO-04", "P-004", "P-212", "P-220", "P-234", "", "40", "—", "Gris", "Activa"], ["LO-03-NEG-FKM", "LO-03", "P-005", "P-310", "", "P-330", "", "40", "—", "Negra", "Activa"], ["LO-03-NEG-TEX", "LO-03", "P-005", "P-310", "", "P-331", "", "40", "—", "Negra", "Activa"], ["LO-03-NEG-PERF", "LO-03", "P-005", "P-310", "", "P-332", "", "40", "—", "Negra", "Activa"], ["LO-03-NEG-ACERO", "LO-03", "P-005", "P-310", "", "P-334", "", "40", "—", "Negra", "Activa"], ["LO-03-NEG-PIELB", "LO-03", "P-005", "P-310", "", "P-335", "", "40", "—", "Negra", "Activa"], ["LO-03-NEG-PIELN", "LO-03", "P-005", "P-310", "", "P-336", "", "40", "—", "Negra", "Activa"], ["LO-03-BLA-FKM", "LO-03", "P-005", "P-310", "", "P-330", "", "40", "—", "Blanca", "Activa"], ["LO-03-BLA-TEX", "LO-03", "P-005", "P-310", "", "P-331", "", "40", "—", "Blanca", "Activa"], ["LO-03-BLA-PERF", "LO-03", "P-005", "P-310", "", "P-332", "", "40", "—", "Blanca", "Activa"], ["LO-03-BLA-ACERO", "LO-03", "P-005", "P-310", "", "P-334", "", "40", "—", "Blanca", "Activa"], ["LO-03-BLA-PIELB", "LO-03", "P-005", "P-310", "", "P-335", "", "40", "—", "Blanca", "Activa"], ["LO-03-BLA-PIELN", "LO-03", "P-005", "P-310", "", "P-336", "", "40", "—", "Blanca", "Activa"], ["LO-03-AZU-ACERO", "LO-03", "P-005", "P-310", "", "P-334", "", "40", "—", "Blanca y Azul", "Activa"], ["LO-03-AZU-NATOP", "LO-03", "P-005", "P-310", "", "P-333", "", "40", "—", "Blanca y Azul", "Activa"]];

function CREAR_LIBRO() {
  const ss = SpreadsheetApp.create('laOra 2026');
  construirParametros(ss);
  construirPiezas(ss);
  construirModelos(ss);
  construirReferencias(ss);
  construirPedidos(ss);
  construirVentas(ss);
  construirStock(ss);
  construirResumen(ss);
  const primera = ss.getSheets()[0];
  if (primera.getName().indexOf('Hoja') === 0 || primera.getName().indexOf('Sheet') === 0) {
    ss.deleteSheet(primera);
  }
  Logger.log('LIBRO CREADO → ' + ss.getUrl());
  return ss.getUrl();
}

function cabecera(sh, columnas) {
  sh.getRange(1, 1, 1, columnas.length).setValues([columnas])
    .setFontWeight('bold').setBackground('#121414').setFontColor('#f5efe6');
  sh.setFrozenRows(1);
}

function construirParametros(ss) {
  const sh = ss.insertSheet('Parametros');
  cabecera(sh, ['Parámetro', 'Nombre', 'Valor', 'Nota']);
  sh.getRange(2, 1, PARAMETROS.length, 4).setValues(PARAMETROS);
  PARAMETROS.forEach(function (p, i) {
    ss.setNamedRange(p[1], sh.getRange(i + 2, 3));
  });
  sh.setColumnWidths(1, 1, 220); sh.setColumnWidths(4, 1, 340);
  protegeAviso(sh.getRange('A1:D30'), 'Los parámetros mandan sobre todo el libro');
}

function construirPiezas(ss) {
  const sh = ss.insertSheet('Piezas');
  const cols = ['ID', 'Tipo', 'Modelos', 'Nombre interno', 'Nombre web', 'Variantes', 'Coste €', 'Fecha coste', 'Link anuncio', 'Tarifa como', 'Recargo PVP €', 'Estado', 'Notas'];
  cabecera(sh, cols);
  const filas = PIEZAS.map(function (p) {
    return [p[0], p[1], p[2], p[3], p[4], p[5], p[6], HOY, p[7], p[8], p[9], 'Activa', p[10]];
  });
  sh.getRange(2, 1, filas.length, cols.length).setValues(filas);
  sh.getRange(2, 7, filas.length, 1).setNumberFormat('#,##0.00 €');
  sh.getRange(2, 8, filas.length, 1).setNumberFormat('dd/mm/yyyy');
  // Un link vacío en pieza activa CHILLA en rojo
  const regla = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=AND($A2<>"", $I2="", $L2="Activa")')
    .setBackground('#f4c7c3')
    .setRanges([sh.getRange('A2:M400')]).build();
  sh.setConditionalFormatRules([regla]);
  sh.setColumnWidths(4, 3, 240); sh.setColumnWidths(9, 1, 300); sh.setColumnWidths(13, 1, 340);
}

function construirModelos(ss) {
  const sh = ss.insertSheet('Modelos');
  cabecera(sh, ['ID', 'Nombre', 'Homenaje', 'Con logo', 'Supl. Ø39 €', 'Estado', 'Desde €']);
  sh.getRange(2, 1, MODELOS.length, 6).setValues(MODELOS.map(function (m) { return m.slice(0, 6); }));
  // MINIFS se atraganta con la columna del derrame («el argumento debe
  // ser un intervalo»): FILTER+MIN por fila, que sí funciona.
  for (var i = 0; i < MODELOS.length; i++) {
    var fila = i + 2;
    sh.getRange(fila, 7).setFormula(
      '=IF(A' + fila + '="",,MIN(FILTER(Referencias!$M$2:$M, (Referencias!$B$2:$B=A' + fila + ')*(Referencias!$K$2:$K="Activa"))))');
  }
  sh.getRange(2, 7, MODELOS.length, 1).setNumberFormat('#,##0.00 €');
  sh.setColumnWidths(3, 1, 320);
  protegeAviso(sh.getRange('G2:G20'), 'Columna calculada');
}

function construirReferencias(ss) {
  const sh = ss.insertSheet('Referencias');
  const cols = ['REF', 'Modelo', 'Movimiento', 'Caja', 'Esfera', 'Correa', 'Extra', 'Ø', 'Tapa', 'Variante', 'Estado',
                'Coste piezas €', 'PVP €', 'Coste neto €', 'Base imp. €', 'IVA €', 'Bruto €', 'IRPF €', 'SS €', 'Limpio €', 'Margen %'];
  cabecera(sh, cols);
  sh.getRange(2, 1, REFERENCIAS.length, 11).setValues(REFERENCIAS);
  // LAS TRES FÓRMULAS DE COLUMNA (una para todo el libro, se estiran solas)
  sh.getRange('L2').setFormula("=MAP($A$2:$A,$B$2:$B,$C$2:$C,$D$2:$D,$E$2:$E,$F$2:$F,$G$2:$G, LAMBDA(ref,mod,mv,cj,es,co,ex, IF(ref=\"\",,\n LET(pid, Piezas!$A$2:$A, pco, Piezas!$G$2:$G,\n  cost, LAMBDA(x, IF(x=\"\",0, XLOOKUP(x,pid,pco,0))),\n  logo, IF(XLOOKUP(mod,Modelos!$A$2:$A,Modelos!$D$2:$D,\"NO\")=\"S\u00cd\", XLOOKUP(\"P-090\",pid,pco,0), 0),\n  cost(mv)+cost(cj)+cost(es)+cost(co)+cost(ex)+logo))))");
  sh.getRange('M2').setFormula("=MAP($A$2:$A,$B$2:$B,$C$2:$C,$D$2:$D,$E$2:$E,$F$2:$F,$G$2:$G,$H$2:$H, LAMBDA(ref,mod,mv,cj,es,co,ex,dia, IF(ref=\"\",,\n LET(pid, Piezas!$A$2:$A, pco, Piezas!$G$2:$G, pta, Piezas!$J$2:$J, pre, Piezas!$K$2:$K,\n  cost, LAMBDA(x, IF(x=\"\",0, XLOOKUP(x,pid,pco,0))),\n  tar, LAMBDA(x, IF(x=\"\",0, LET(t, XLOOKUP(x,pid,pta,\"\"), IF(t=\"\", XLOOKUP(x,pid,pco,0), XLOOKUP(t,pid,pco,0))))),\n  rec, LAMBDA(x, IF(x=\"\",0, XLOOKUP(x,pid,pre,0))),\n  logo, IF(XLOOKUP(mod,Modelos!$A$2:$A,Modelos!$D$2:$D,\"NO\")=\"S\u00cd\", XLOOKUP(\"P-090\",pid,pco,0), 0),\n  ct, tar(mv)+tar(cj)+tar(es)+tar(co)+tar(ex)+logo,\n  neto, ct + (P_ENVIO+P_EMBALAJE)/(1+P_IVA) + (cost(mv)+P_GPORTES+P_GPIEZAS)*P_GTASA,\n  red, LAMBDA(p, LET(b, FLOOR(p-9.9,10)+9.9, IF(p-b<=b+10-p, b, b+10))),\n  sube, LAMBDA(p, LET(b, FLOOR(p-9.9,10)+9.9, IF(b>=p-0.000000001, b, b+10))),\n  queda, 1-P_IRPF-P_SS,\n  suelo, sube(MAX((P_SUELO/queda+neto)*(1+P_IVA), IF(queda/(1+P_IVA)-P_MARGENMIN>0, queda*neto/(queda/(1+P_IVA)-P_MARGENMIN), 0))),\n  supl, IF(dia&\"\"=\"39\", XLOOKUP(mod,Modelos!$A$2:$A,Modelos!$E$2:$E,0), 0),\n  MAX(red(ct*P_MULT), suelo) + rec(mv)+rec(cj)+rec(es)+rec(co)+rec(ex) + supl))))");
  sh.getRange('N2').setFormula("=MAP($A$2:$A,$C$2:$C,$L$2:$L, LAMBDA(ref,mv,creal, IF(ref=\"\",,\n creal + (P_ENVIO+P_EMBALAJE)/(1+P_IVA) + (IF(mv=\"\",0,XLOOKUP(mv,Piezas!$A$2:$A,Piezas!$G$2:$G,0))+P_GPORTES+P_GPIEZAS)*P_GTASA)))");
  // y la cuenta, columna a columna sobre las anteriores
  sh.getRange('O2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$M$2:$M/(1+P_IVA)))');
  sh.getRange('P2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$M$2:$M-$O$2:$O))');
  sh.getRange('Q2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$O$2:$O-$N$2:$N))');
  sh.getRange('R2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$Q$2:$Q*P_IRPF))');
  sh.getRange('S2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$Q$2:$Q*P_SS))');
  sh.getRange('T2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$Q$2:$Q-$R$2:$R-$S$2:$S))');
  sh.getRange('U2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$T$2:$T/$M$2:$M))');
  sh.getRange(2, 12, 900, 9).setNumberFormat('#,##0.00 €');
  sh.getRange(2, 21, 900, 1).setNumberFormat('0.0%');
  // Desplegables: modelo y piezas solo de la lista
  validaDe(sh.getRange('B2:B900'), ss, 'Modelos', 'A2:A50');
  validaDe(sh.getRange('C2:G900'), ss, 'Piezas', 'A2:A400');
  protegeAviso(sh.getRange('L1:U900'), 'Columnas calculadas: se tocan en Piezas/Parametros, no aquí');
  sh.setColumnWidths(1, 1, 250);
}

function construirPedidos(ss) {
  const sh = ss.insertSheet('Pedidos');
  cabecera(sh, ['Fecha', 'Pieza', 'Cantidad', 'Coste ud. €', 'Total €', 'Nº pedido AliExpress', 'Estado', 'Notas']);
  sh.getRange('E2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$C$2:$C*$D$2:$D))');
  sh.getRange(2, 4, 900, 2).setNumberFormat('#,##0.00 €');
  sh.getRange(2, 1, 900, 1).setNumberFormat('dd/mm/yyyy');
  validaDe(sh.getRange('B2:B900'), ss, 'Piezas', 'A2:A400');
  validaLista(sh.getRange('G2:G900'), ['Pedido', 'En camino', 'Recibido', 'Incidencia']);
}

function construirVentas(ss) {
  const sh = ss.insertSheet('Ventas');
  cabecera(sh, ['Fecha', 'REF', 'Canal', 'PVP cobrado €', 'Envío real €', 'Coste piezas €', 'Margen real €', 'Modelo', 'Notas']);
  sh.getRange('F2').setFormula('=ARRAYFORMULA(IF($B$2:$B="",,XLOOKUP($B$2:$B, Referencias!$A$2:$A, Referencias!$L$2:$L, 0)))');
  sh.getRange('G2').setFormula('=ARRAYFORMULA(IF($B$2:$B="",,$D$2:$D/(1+P_IVA)-$F$2:$F-$E$2:$E))');
  sh.getRange('H2').setFormula('=ARRAYFORMULA(IF($B$2:$B="",,LEFT($B$2:$B,5)))');
  sh.getRange(2, 4, 900, 4).setNumberFormat('#,##0.00 €');
  sh.getRange(2, 1, 900, 1).setNumberFormat('dd/mm/yyyy');
  validaDe(sh.getRange('B2:B900'), ss, 'Referencias', 'A2:A900');
  validaLista(sh.getRange('C2:C900'), ['Web', 'Instagram', 'Directo', 'Otro']);
  protegeAviso(sh.getRange('F1:H900'), 'Calculadas');
}

function construirStock(ss) {
  const sh = ss.insertSheet('Stock');
  cabecera(sh, ['Pieza', 'Nombre', 'Recibidas', 'Usadas en ventas', 'Disponibles', 'Valor €']);
  sh.getRange('A2').setFormula('=ARRAYFORMULA(Piezas!A2:A)');
  sh.getRange('B2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,XLOOKUP($A$2:$A, Piezas!$A$2:$A, Piezas!$D$2:$D, "")))');
  sh.getRange('C2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,SUMIFS(Pedidos!$C$2:$C, Pedidos!$B$2:$B, $A$2:$A, Pedidos!$G$2:$G, "Recibido")))');
  sh.getRange('D2').setFormula(
    '=MAP($A$2:$A, LAMBDA(p, IF(p="",, LET(refs, Ventas!$B$2:$B, fila, LAMBDA(col, IFERROR(XLOOKUP(refs, Referencias!$A$2:$A, col, ""), "")), ' +
    'SUMPRODUCT((fila(Referencias!$C$2:$C)=p)+(fila(Referencias!$D$2:$D)=p)+(fila(Referencias!$E$2:$E)=p)+(fila(Referencias!$F$2:$F)=p)+(fila(Referencias!$G$2:$G)=p))))))');
  sh.getRange('E2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$C$2:$C-$D$2:$D))');
  sh.getRange('F2').setFormula('=ARRAYFORMULA(IF($A$2:$A="",,$E$2:$E*XLOOKUP($A$2:$A, Piezas!$A$2:$A, Piezas!$G$2:$G, 0)))');
  sh.getRange(2, 6, 400, 1).setNumberFormat('#,##0.00 €');
  protegeAviso(sh.getRange('A1:F400'), 'Hoja entera calculada: el stock se mueve desde Pedidos y Ventas');
}

function construirResumen(ss) {
  const sh = ss.insertSheet('Resumen');
  sh.getRange('A1').setValue('laOra · Resumen del negocio').setFontWeight('bold').setFontSize(14);
  sh.getRange('A3').setValue('Ventas por mes y modelo');
  sh.getRange('A4').setFormula(
    '=IFERROR(QUERY(Ventas!A2:H, "select year(A), month(A)+1, H, count(B), sum(D), sum(G) where A is not null group by year(A), month(A)+1, H order by year(A) desc, month(A)+1 desc label year(A) \'Año\', month(A)+1 \'Mes\', H \'Modelo\', count(B) \'Uds.\', sum(D) \'Ingresos\', sum(G) \'Margen\'", 0), "Sin ventas todavía")');
  sh.getRange('A12').setValue('Referencias más vendidas');
  sh.getRange('A13').setFormula(
    '=IFERROR(QUERY(Ventas!A2:H, "select B, count(B), sum(D) where B is not null group by B order by count(B) desc limit 10 label B \'REF\', count(B) \'Uds.\', sum(D) \'Ingresos\'", 0), "Sin ventas todavía")');
  sh.getRange('E3').setValue('Dinero en stock (€)');
  sh.getRange('F3').setFormula('=SUM(Stock!F2:F)');
  sh.getRange('E4').setValue('Piezas activas sin link');
  sh.getRange('F4').setFormula('=COUNTIFS(Piezas!I2:I, "", Piezas!A2:A, "<>", Piezas!L2:L, "Activa")');
  sh.getRange('E5').setValue('Referencias activas');
  sh.getRange('F5').setFormula('=COUNTIFS(Referencias!K2:K, "Activa")');
  sh.getRange('F3').setNumberFormat('#,##0.00 €');
}

function validaDe(rango, ss, hoja, celdas) {
  const regla = SpreadsheetApp.newDataValidation()
    .requireValueInRange(ss.getSheetByName(hoja).getRange(celdas), true)
    .setAllowInvalid(false).build();
  rango.setDataValidation(regla);
}

function validaLista(rango, valores) {
  const regla = SpreadsheetApp.newDataValidation()
    .requireValueInList(valores, true).setAllowInvalid(false).build();
  rango.setDataValidation(regla);
}

function protegeAviso(rango, descripcion) {
  rango.protect().setDescription(descripcion).setWarningOnly(true);
}
