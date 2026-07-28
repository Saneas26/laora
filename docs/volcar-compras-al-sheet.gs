/**
 * laOra · Volcado de la búsqueda de materiales al Sheet
 * ----------------------------------------------------
 * Crea (o rehace) la hoja «Compras — enlaces» del libro
 * «laora-biblioteca-materiales» con todos los proveedores localizados,
 * sus variantes, precios vistos, MOQ y enlace de compra.
 *
 * CÓMO SE USA
 *   1. Abre el Sheet → Extensiones → Apps Script.
 *   2. Pega este archivo entero (sustituye lo que haya).
 *   3. Ejecuta la función  volcarCompras  y acepta los permisos.
 *   4. Aparece la hoja «Compras — enlaces» al final del libro.
 *
 * Se puede volver a ejecutar las veces que haga falta: rehace la hoja
 * desde cero, así que NO escribas a mano en ella; las columnas para
 * rellenar (Estado y Notas de Óscar) están al final y se conservan por
 * clave si ya existían.
 *
 * IMPORTANTE sobre los precios: ninguno es una cotización. Son precios
 * publicados al detalle o estimaciones, y así se indican. Los fabricantes
 * serios no publican tarifa B2B: hay que pedirla.
 */

var HOJA = 'Compras — enlaces';

var CABECERA = [
  'Bloque', 'Componente', 'Para', 'Proveedor', 'Qué vende / ofrece',
  'Especificación', 'Precio visto', '¿Precio?', 'MOQ', 'País',
  'Fiabilidad', 'Enlace', 'Estado', 'Notas de Óscar'
];

// Bloque | Componente | Para | Proveedor | Qué vende | Especificación | Precio | tipo | MOQ | País | Fiabilidad | URL
var FILAS = [

// ───────────────────────── CONJUNTO CAJA + BRAZALETE ─────────────────────────
['1 · Caja y brazalete','Conjunto caja + brazalete integrado','Todos','HK Watch Home','Caja NH35 40 mm 316L CNC + zafiro + brazalete integrado, estéril','Ø40 mm, 316L, integrado','27,54–35,53 €','Publicado (muestra)','10','Hong Kong','Media','https://www.alibaba.com/trade/search?SearchText=integrated+bracelet+watch+case+40mm+NH35'],
['1 · Caja y brazalete','Conjunto caja + brazalete integrado','Todos','Shenzhen Happy Time Technology','Caja 40 mm diseño integrado + zafiro plano + brazalete; declaran titanio','Ø40 mm, 316L/titanio, NH35/NH36','40,04–61,28 €','Publicado (muestra)','2','China','Media-alta','https://hp-times.en.alibaba.com/'],
['1 · Caja y brazalete','Conjunto caja + brazalete integrado','T3 Cenit (titanio)','Baoruihua / ODM Watch','Fábrica de brazaletes, cajas, cierres y coronas; especialistas en titanio','316L, titanio, oro K','Pedir cotización','No publicado','No publicado','China (Dongguan)','Alta como fábrica','https://www.odmwatch.com/application/titanium-bracelet'],
['1 · Caja y brazalete','Conjunto caja + brazalete integrado','T3 Cenit (titanio)','Shenzhen Gotop Watches','Cajas, esferas, brazaletes y cierres; CNC + sala limpia clase 100.000','316L, titanio, zafiro','Pedir cotización','No publicado','No publicado','China (Shenzhen)','Media-alta','https://www.gotopwatches.com/products/watch-case/'],
['1 · Caja y brazalete','Conjunto caja + brazalete integrado','Todos','Shenzhen Timebalife','ODM completo de reloj y componentes; declara Miyota/Seiko/ETA/Sellita','316L, titanio, cerámica','Pedir cotización','No publicado','~100','China (Shenzhen)','Media-alta','https://www.timebalife.com/oem'],
['1 · Caja y brazalete','Conjunto caja + brazalete integrado','Vía europea','Ickler GmbH (Pforzheim)','Cajas fresadas de bloque macizo para terceros; también brazaletes y cierres','Acero, titanio puro, bronce','Pedir cotización','No publicado','No publicado','Alemania','Alta','https://www.archimede-watches.com/us/MANUFAKTUR/ICKLER-MANUFAKTUR/'],
['1 · Caja y brazalete','Caja suelta (patrón de acabado)','Prototipo','namokiMODS','Caja NMK935 Mk2 estéril, línea Nautilus','316L, estéril','113,95 €','Publicado','1','Singapur','Alta (retail)','https://www.namokimods.com/en-eu/search?q=nautilus+case'],
['1 · Caja y brazalete','Brazalete suelto (patrón)','Prototipo','namokiMODS','Brazalete Nautilus estéril','316L','70,95–86,95 €','Publicado','1','Singapur','Alta (retail)','https://www.namokimods.com/en-eu/search?q=nautilus+case'],
['1 · Caja y brazalete','End-link macizo (referencia)','Prototipo','namokiMODS','Solid End Link suelto — prueba de que los huecos existen en el mercado','316L macizo','16,95 €','Publicado','1','Singapur','Alta (retail)','https://www.namokimods.com/en-eu/search?q=nautilus+case'],
['1 · Caja y brazalete','Conjunto integrado 36 mm','Descartado (tamaño)','Lucius Atelier «Seikonaut»','Caja octogonal redondeada con brazalete integrado, zafiro AR doble, 200 m','36 mm — NO hay 40 mm','239 SGD (~165 €)','Publicado','1','Singapur','Alta','https://luciusatelier.com/products/seikonaut-watch-case-36mm'],
['1 · Caja y brazalete','Conjunto integrado 40 mm','Solo automático','iModLab IC011','Set de caja 40 mm, brazalete integrado 20 mm, zafiro, 5 ATM, «NO LOGO»','Solo NH35A/NH36A/7S26/4R36','159 USD','Publicado','10 (500 para logo propio)','China','Media','https://www.imodlab.com/products/ic011-40mm-nh35-nh36-case-set-watch-factory-wholesale'],
['1 · Caja y brazalete','Conjunto 40 mm estilo integrado','Referencia','Tandorio','Caja + brazalete 316L, 11,5 mm de grosor, zafiro, 100 m','Ø40 mm, esfera 28,5–29,4 mm','No verificado','No fiable','1','China','Media','https://tandoriowatch.com/products/40mm-rose-gold-watch-case-nautilus'],

// ───────────────────────────── MOVIMIENTOS ─────────────────────────────
['2 · Movimientos','Ronda 715 (cuarzo suizo)','T1 Alba','Kirman (Sevilla)','Distribuidor español de Ronda, Miyota y Hattori/Seiko. Factura española','11½‴, fecha, pila 60 meses','Pedir cotización','No publicado','No publicado','España','Alta — PRIMERA LLAMADA','https://www.kirman.com/noticias/destacados/movimientos-para-relojes-de-pulsera/'],
['2 · Movimientos','Ronda 715 (cuarzo suizo)','T1 Alba','Ronda AG (fábrica)','Fabricante. Pedir versión Swiss Made 5 rubíes (no Swiss Parts)','11½‴, Ø26 mm, 2,5 mm','Pedir cotización','No publicado','No publicado','Suiza','Máxima','https://www.ronda.ch/en/about-ronda-group/ronda/contact'],
['2 · Movimientos','Ronda 715 (cuarzo suizo)','T1 Alba','watch-tools.de','Venta unitaria, suministro directo desde Suiza','715','18,84 € (IVA incl.)','Publicado','1','Alemania','Alta','https://www.watch-tools.de/movements-133/ronda-quarzuhrwerke.php'],
['2 · Movimientos','Ronda 715 (cuarzo suizo)','T1 Alba','Selfor Paris','Venta por packs completos','715','15,48 € (IVA incl.)','Publicado','Pack','Francia','Alta','https://www.selforparis.com/en/watchmaking-supplies/watch-movements/watch-movements-ronda-715-125954.html'],
['2 · Movimientos','Ronda 515 (cuarzo suizo)','T1 alternativa','H.S. Walsh','72 referencias Ronda en stock, entrega 24 h en UK','515','10,95 £','Publicado','1','Reino Unido (fuera UE)','Alta','https://www.hswalsh.com/manufacturers/ronda'],
['2 · Movimientos','Ronda (varios)','T1 Alba','Bullnheimer & Co.','Mayorista B2B, precios netos tras registro','Catálogo Ronda','Pedir cotización','No publicado','No publicado','Alemania','Alta','https://bullnheimer.de/en/Movements-watch-spare-parts/Watch-movements/RONDA-watch-movements/'],
['2 · Movimientos','Seiko NH35A (automático)','T2 Meridiano','Time Module Inc. (TMI)','Fabricante/comercializador oficial. Pedir agente para España','24 rubíes, 21.600 A/h, ~41 h','Pedir cotización','No publicado','No publicado','Hong Kong','Máxima','https://www.timemodule.com/en/'],
['2 · Movimientos','Seiko NH35A (automático)','T2 Meridiano','namokiMODS','Venta unitaria; tiene sección mayorista','NH35A estándar','120 SGD (~80 €)','Publicado','1','Singapur','Alta','https://www.namokimods.com/products/seiko-sii-nh35a-automatic-movement'],
['2 · Movimientos','Seiko NH35A (automático)','T2 Meridiano','Lucius Atelier','Regulado o sin regular, envío exprés 2-4 días','NH35A','135–185 SGD (~95–130 €)','Publicado','1','Singapur','Alta','https://luciusatelier.com/products/seiko-tmi-nh35-automatic-movement-date-black'],
['2 · Movimientos','Seiko NH35A (automático)','T2 Meridiano','Watch&Style','Venta unitaria','NH35A','~5.100 PHP (~78 €)','Publicado','1','Filipinas','Media-alta','https://watchandstyle.net/collections/movements'],
['2 · Movimientos','Miyota 9015 (automático fino)','T3 Cenit','Miyota / Citizen (fábrica)','Formulario oficial: asignan agente por país. Exponen en Inhorgenta','24 rubíes, 28.800 A/h, ~42 h','No publican por política','No publicado','No publicado','Japón','Máxima','https://miyotamovement.com/faq/'],
['2 · Movimientos','Miyota 9015 (automático fino)','T3 Cenit','Perrin Supply','Venta unitaria, descuento con registro mayorista','9015','117,08 USD','Publicado','1','Canadá (fuera UE)','Alta','https://perrinwatchparts.com/en-us/products/automatic_watch_movement_miyota_9015'],
['2 · Movimientos','Miyota GM10-D3 (cuarzo)','T1 plan B','Perrin Supply','Cuarzo con fecha a las 3 — lo encasillan de serie las fábricas chinas','Ø23,30 mm, 2,71 mm, pila 364','Ver ficha','Publicado','1','Canadá','Alta','https://perrinwatchparts.com/en-us/products/quartz_watch_movement_miyota_gm10_date_6'],
['2 · Movimientos','Portamovimiento Ronda → caja NH3x','T1 Alba','Thingiverse (KenVersus)','STL gratuito ya diseñado: Ronda 515 en caja NH34/35/36/38','Imprimible 3D — prototipo','Gratuito','Publicado','1','—','Alta (prototipo)','https://www.thingiverse.com/thing:6798210'],
['2 · Movimientos','Portamovimiento VH31/Miyota → NH3x','T1 alternativa','Printables','STL gratuito, variantes para esferas 28,5 y 31 mm','Imprimible 3D','Gratuito','Publicado','1','—','Alta (prototipo)','https://www.printables.com/model/1182656-seiko-vh31-miyota-2115-movement-holder-for-seiko-n'],
['2 · Movimientos','Portamovimiento a medida','T1 Alba','Watch Complications','Diseño CAD + impresión a medida de portamovimientos y espaciadores','PLA (resina en estudio)','Pedir presupuesto','No publicado','1','—','Media-alta','https://watchcomplications.com/2021/05/20/custom-movement-holders-and-spacers/'],

// ───────────────────────────── ESFERA Y AGUJAS ─────────────────────────────
['3 · Esfera y agujas','Esfera turquesa con relieve','Todos','Shenzhen Timebalife','Fábrica de esferas: catálogo con soleil turquesa y relieves; imprime logo','Estéril + tampografía propia','Pedir cotización','No publicado','No publicado','China','Media-alta','https://www.timebalife.com/watch-dial/'],
['3 · Esfera y agujas','Esfera turquesa con relieve','Todos','Shenzhen Shijin Watch','Línea de producto específica «Embossed Dial»','Relieve estampado','Pedir cotización','No publicado','No publicado','China','Media','https://www.shijinwatch.com/products/embossed-dial.html'],
['3 · Esfera y agujas','Esfera turquesa con relieve','Vía europea','Fraporlux Swiss SA','Independiente: estampación del relieve + tampografía + apliques bajo un techo','26 oficios en casa','Pedir cotización','No publicado','No publicado','Suiza','Alta','https://www.fraporlux.com/'],
['3 · Esfera y agujas','Esfera a medida','Vía europea','Cador GmbH','Todas las tecnologías de esfera bajo un techo, del utillaje al montaje','—','Pedir cotización','No publicado','No publicado','Alemania','Alta','https://www.cador.de/en'],
['3 · Esfera y agujas','Esfera — muestra maestra','Prototipo','The Dialmaker (Andalucía)','Taller de 2 personas: grabado láser, texturas, pintado a mano. 1 unidad','Sin mínimo, 1-2 semanas','Pedir presupuesto','No publicado','1','España','Alta como taller','https://thedialmaker.com/'],
['3 · Esfera y agujas','Esfera — solo logo','Prototipo','dialmaker.shop','Añadir logo a esfera de stock, o esfera 100% a medida','Logo: 8-10 días','70 USD (solo logo)','Publicado','1 (logo) / 20 (a medida)','No identificado','Media-baja','https://www.dialmaker.shop/products/dial-maker-custom-dial-service-4'],
['3 · Esfera y agujas','Esfera turquesa de stock','Prototipo','Lucius Atelier','Esfera turquesa estéril con fecha, 28,5 mm, compatible NH35','Con licencia Super-LumiNova','Ver ficha','Publicado','1','Singapur','Media-alta','https://luciusatelier.com/pages/bespoke-designs'],
['3 · Esfera y agujas','Agujas bastón con lume','Todos','Perfect / Dongguan Perfect Watch Parts','Fabricante real de agujas, coronas, pulsadores y fondos. ISO 9001, desde 1998','OEM/ODM','~1,00 USD/ud (a 200)','Publicado (orientativo)','20–200','China (Dongguan)','Alta','https://perfectwatchpart.en.made-in-china.com'],
['3 · Esfera y agujas','Agujas a medida','Vía europea','Aiguilla SA','Fabricante suizo desde 1890, ~170 empleados, 15-20 operaciones por aguja','A medida','Pedir cotización','No publicado','No publicado','Suiza','Alta','http://aiguilla.ch/en/accueil.8.html'],
['3 · Esfera y agujas','Agujas (muestras)','Prototipo','Quanzhou Beike Laien','Trading company: útil para muestras, no para producción','OEM/ODM','2,63–4,20 USD','Publicado','10','China','Media-baja','https://watch118.en.made-in-china.com'],
['3 · Esfera y agujas','ATENCIÓN — agujas por calibre','Todos','—','NH35A: 1,50/0,89/0,21 · Miyota 9015: 1,50/1,00/0,17 · Ronda 715: 1,20/0,70/0,20','Tres juegos distintos: NO hay aguja universal','—','—','—','—','Dato verificado','https://calibercorner.com/seiko-caliber-nh35a/'],

// ───────────────────────────── CRISTALES ─────────────────────────────
['4 · Cristales','Zafiro plano y doble domo','T2/T3','Watch Parts Platform','Catálogo de medidas fijas, chaflán 0,3×45° pulido','Ø19–32 mm, 0,75–4,0 mm','No verificado (fallo SSL)','—','2','Hong Kong','Media','https://watchpartsplatform.net/collections/sapphire-glass-crystals'],
['4 · Cristales','Zafiro (plano, domo, box) con AR','T2/T3','Crystaltimes','Zafiro para modding, AR azul/verde/clear','Ø31 y 32 mm','Ver web','—','1','—','Media-alta','https://crystaltimes.net/shop/shop-all/'],
['4 · Cristales','Zafiro doble domo con AR','T3 Cenit','WR Watches','Doble domo con chaflán ancho, AR azul','32 mm','42,90 USD','Publicado','1','—','Media (retail)','https://wrwatches.com/products/32mm-double-domed-sapphire-ultra-wide-chamfer-crystal-blue-ar-coating'],
['4 · Cristales','Zafiro de recambio','Postventa','Perrin Supply','25 referencias, canto superior pulido','Ø13–44 mm; 0,80/1,00/1,50/2,00 mm','No verificado','—','1','Canadá','Alta','https://perrinwatchparts.com/en-us/collections/sapphire-crystals'],
['4 · Cristales','Zafiro y mineral (Sternkreuz)','Postventa','Cousins UK','El distribuidor de referencia en Europa. Requiere cuenta trade','Gama completa','No verificado (403)','—','1','Reino Unido','Alta','https://www.cousinsuk.com/category/sapphire-watch-glasses'],
['4 · Cristales','Zafiro a medida con AR','Producción','Shenzhen Shen Xun Lens Technology','Fabricante de zafiro a medida, recubrimientos AR y AF','Espesores 0,33–6 mm','Pedir cotización','No publicado','Industrial','China','Media','https://www.made-in-china.com/products-search/hot-china-products/Sapphire_Crystal_Watch.html'],
['4 · Cristales','Zafiro a medida (plano/domo)','Producción','Chengdu Optic-Well','Fabricante con línea específica de watch glass','Plano, mono y doble domo','Pedir cotización','No publicado','No publicado','China','Media','https://www.opticwell.com/china-manufacture-sapphire-watch-glass-watch-crystal-in-stock-product/'],
['4 · Cristales','Mineral K1 (NO decir «Hardlex»)','T1 Alba','SXET Glass','Fabricante de watch glass: zafiro, mineral y K1','K1 ≥600 HV — pedir certificado','Pedir cotización','No publicado','No publicado','China','Media-baja','https://www.sxetglass.com/watch-glass/'],
['4 · Cristales','Cristales de zafiro (reposición)','Postventa','Suministros Revuelto','Catálogo español, algunas referencias con junta incluida','Medidas fijas','Ver web','—','1','España','Media-alta','https://suministrosrevuelto.com/951-cristales-zafiro'],

// ───────────────────────── JUNTAS, CORONA Y CIERRE ─────────────────────────
['5 · Juntas y cierre','O-ring de fondo (NBR 70)','Todos','Esslinger','O-rings de fondo y juntas de cristal tipo I (Hytrel)','Espesores 0,30–1,00 mm','3,49 USD/ud · surtido 19,95 USD','Publicado','1','EE. UU.','Alta','https://www.esslinger.com/watch-gaskets/'],
['5 · Juntas y cierre','Juntas de fondo, cristal y corona','Todos','Otto Frei','Juntas de corona y tubo 5,3/6,0/7,0 mm','—','Fondo 5,50 USD/3 · corona 1,00–1,80 USD','Publicado','1','EE. UU.','Alta','https://www.ofrei.com/page_153.html'],
['5 · Juntas y cierre','Tóricas NBR / Viton','Producción','O-Ring Stocks','Catálogo métrico completo, NBR y FKM 70/75/90 Sh A','NBR 70 Sh A es lo correcto aquí','Publicado por referencia','Publicado','Baja','UE','Alta','https://www.o-ring-stocks.eu/'],
['5 · Juntas y cierre','Juntas a medida','Producción','KLINGER Besma','Fabricante español de juntas y tóricas: NBR, FKM, VMQ, EPDM','A medida','Pedir cotización','No publicado','Industrial','España','Alta','https://www.juntasbesma.com/'],
['5 · Juntas y cierre','Tóricas NBR de catálogo','Producción','Disumtec','Tóricas métricas estándar','NBR','Publicado','Publicado','Baja','España','Alta','https://www.disumtec.com/en/o-rings/3800000136-nbr-o-ring.html'],
['5 · Juntas y cierre','Corona estanca con tubo','Todos','Esslinger','Coronas estancas y roscadas con tubo; surtidos','Tap 10 (0,90 mm), Ø3,5–10 mm','5,95–7,00 USD · surtido 100 uds 30,95 USD','Publicado','1','EE. UU.','Alta','https://www.esslinger.com/waterproof-watch-crowns/'],
['5 · Juntas y cierre','Corona + tija para NH35','Prototipo','DIY Watch Club','Kit corona-tija listo para NH35','NH35','Ver ficha','Publicado','1','Hong Kong','Media-alta','https://shop.diywatch.club/products/diver-crown-and-stem-seiko-nh35'],
['5 · Juntas y cierre','Cierre desplegable macizo','Referencia','Strapcode','Cierre mariposa con pulsadores, 316L macizo','16 y 18 mm — no hay titanio','41,99 USD','Publicado','1','—','Alta (retail)','https://www.strapcode.com/products/strapcode-watch-bands-deployant-buckle-025b'],
['5 · Juntas y cierre','Cierre desplegable mecanizado','Referencia','Uncle Straps','Cierre de doble pulsador mecanizado, Flip-Lock','16/18/20 mm','Publicado por producto','Publicado','1','EE. UU.','Alta (retail)','https://unclestraps.com/products/replacement-clasps'],
['5 · Juntas y cierre','AVISO — cierre en integrado','Todos','—','El cierre NO se compra suelto: sale del mismo molde y pulido que el brazalete','Mismo proveedor y mismo plano','—','—','—','—','Criterio de compras','https://www.odmwatch.com/application/folding-buckle'],

// ───────────────────────── DLC (EDICIÓN ECLIPSE) ─────────────────────────
['6 · DLC Eclipse','Recubrimiento DLC negro','T4 Eclipse','Oerlikon Balzers Coating Spain','Centro de recubrimiento a terceros; tiene división propia de relojería','Gama BALINIT — pedir ficha técnica','Pedir cotización','No publicado','No publicado','España (Antzuola)','Alta','https://www.oerlikon.com/balzers/global/en/markets/high-end-deco-watches/'],
['6 · DLC Eclipse','Recubrimiento DLC negro','T4 Eclipse','Flubetech','Recubrimientos cerámicos duros; producto DLC MOLT. PVD, HiPIMS y HT-CVD','Perfil automoción/matricería','Pedir cotización','No publicado','No publicado','España (Barcelona/Gipuzkoa)','Alta','https://flubetech.com/en/producto/dlc-molt/'],
['6 · DLC Eclipse','Recubrimiento DLC negro','T4 Eclipse','Hirucoat','PVD y tratamiento superficial sobre inox, titanio, Inconel','Opciones biocompatibles','Pedir cotización','No publicado','No publicado','España (Galdakao)','Media-alta','https://hirucoat.com/'],
['6 · DLC Eclipse','Recubrimiento PVD/DLC','T4 Eclipse','Grup TTC','PVD, CVD, TD y PECVD sobre piezas acabadas','PVD 0,5–2 µm','Pedir cotización','No publicado','No publicado','España','Media','https://grupttc.es/recubrimientos-pvd/'],
['6 · DLC Eclipse','DLC decorativo relojero','T4 Eclipse','Blösch AG','LA referencia de la industria relojera suiza. Blaktop y Anthratop','~1 µm; trata inox, latón, cerámica y zafiro','Pedir cotización','No publicado','No publicado','Suiza','Alta','https://onlinemagazin.bloesch.ch/en/dlc-coating-decorative-and-functional'],
['6 · DLC Eclipse','DLC sobre caja OEM','T4 Eclipse','Pardwin','Cajas con DLC negro sobre 316L y titanio; ISO 9001','2 µm, 120–160 °C, ciclo 6-8 h','Pedir cotización','No publicado','2 / 20 / 300 según personalización','China','Media','https://pardwincn.com/black-dlc-stainless-steel-dlc-watch-case-scratch-resistance/'],
['6 · DLC Eclipse','DLC pieza a pieza (techo de coste)','Referencia','Black Dog Horology','Servicio DLC unitario sobre relojes montados','—','750 CAD caja + 250 CAD brazalete','Publicado','Piezas sueltas','Canadá','Alta (dato de precio)','https://www.blackdoghorology.com/product/DLC/6'],

// ───────────────────── CONTROL DE CALIDAD (TALLER MADRID) ─────────────────────
['7 · Taller Madrid','Prueba de estanqueidad en seco','Todos','Roxer Diablo (vía H.S. Walsh)','Detector de fugas por vacío — el ensayo del 100 % de las unidades','Seco','£1.225','Publicado','1','Reino Unido','Alta','https://www.hswalsh.com/horological-tools-equipment/waterproof-testing/waterproof-testing-machines'],
['7 · Taller Madrid','Prueba de estanqueidad en seco','Todos','Witschi ProofMaster CP','Presión + vacío con compresor integrado; mide deformación de caja','Seco — el recomendado','£4.695','Publicado','1','Suiza','Alta','https://www.witschi.com/en/products/proofmaster-2/'],
['7 · Taller Madrid','Prueba de estanqueidad económica','Todos','Elma Leak Controller 2000','Detector de fugas por vacío','Seco','£990','Publicado','1','—','Alta','https://www.hswalsh.com/horological-tools-equipment/waterproof-testing/waterproof-testing-machines'],
['7 · Taller Madrid','Confirmación por inmersión','Muestreo','Calypso / Calypso Plus','Solo por muestreo y SIEMPRE sobre caja vacía, nunca reloj montado','Húmedo, 10 bar','£439,95 / £495','Publicado','1','—','Alta','https://www.hswalsh.com/horological-tools-equipment/waterproof-testing/waterproof-testing-machines'],
['7 · Taller Madrid','Prueba de presión de aficionado','Prototipo','DIY Watch Club','Cámara 7×14 cm, 2 relojes','6 bar','120 USD','Publicado','1','Hong Kong','Media','https://shop.diywatch.club/products/water-pressure-tester-6-bar-6-atm'],
// ───────────────────────────── PACKAGING ─────────────────────────────
['8 · Packaging','Estuche de cartoncillo impreso','Caja de producto','Exaprint ES','Estuche cartoncillo 380 g troquelado y hendido, CMYK. 10 formatos','La partida principal de la propuesta','0,73 €/ud a 100 (sin IVA)','Publicado — CONFIRMAR IVA','25','España','Alta','https://www.exaprint.es/packagings/producto/estuche-carton/'],
['8 · Packaging','Caja troquelada a medida','Caja de producto','Packly (IT, envía a ES)','Troqueladas de cartoncillo y ondulado, digital HD, FSC','«You never pay for the die»: TROQUEL GRATIS','Pedir presupuesto','No publicado','1','Italia','Alta','https://pack.ly/en/short-runs'],
['8 · Packaging','Caja + cuna a medida','Caja y sujeción','ProPrintweb (Barcelona)','Cartoncillo a medida libre: tapa+base, funda deslizante, nidos interiores','Troquelado incluido, sin coste aparte','Pedir presupuesto','No publicado','15','España','Alta','https://proprintweb.com/impresion/cajas-personalizadas'],
['8 · Packaging','Caja forrada con interior troquelado','Caja de producto','Cajas Arteca (Cádiz)','Cartonaje rígido forrado + interior de cartón con huecos. Producto de joyería','Puede sustituir a dos partidas','1,79 €/ud orientativo','Publicado','100','España','Alta','https://cajasarteca.es/cajas-interior-carton-troquelado.html'],
['8 · Packaging','Caja rígida y mailer','Caja de producto','Packhelp','Product box y caja rígida con tapa, medida libre','Product box 150 ud 1,09 € · rígida 120 ud 5,33 €','Publicado','Publicado','30 plegable / 120 rígida','Polonia/ES','Alta','https://packhelp.es/embalaje/cajas/cajas-para-productos/cajas-rigidas/'],
['8 · Packaging','Caja digital sin clichés','Prototipo','Cajadecarton.es','Impresión digital sobre troqueladas, sin planchas ni clichés','7-10 días','Pedir presupuesto','No publicado','10–25','España','Alta','https://www.cajadecarton.es/impresion-digital'],
['8 · Packaging','Caja a medida (Madrid)','Caja de producto','Be Your Packer (Madrid)','Editor 3D, ondulado, cartoncillo y rígidas forradas','10-15 días','Pedir presupuesto','No publicado','1','España','Alta','https://beyourpacker.com/10-cajas-personalizadas'],
['8 · Packaging','Cartonaje rígido artesanal','Caja de producto','Cartonajes Sánchez (Madrid)','Cartón rígido contracolado, telas, imanes','MOQ 500 si hay troquelado','Pedir presupuesto','No publicado','25 (500 con troquel)','España','Alta','https://cartonajessanchez.com/productos'],
['8 · Packaging','Prototipo 1 unidad','Prototipo','Pixartprinting ES','Caja Deluxe de cartón rígido, soft touch, barniz 3D','Para iterar barato antes de la serie','Configurador','No publicado','1','España','Alta','https://www.pixartprinting.es/packaging/packaging-estandar/caja-deluxe/'],
['8 · Packaging','Manga honeycomb de papel','Protección','Packhelp','Rollo de papel nido de abeja 40 cm × 100 m, sin máquina','≈0,08 €/reloj','40,41 €/rollo','Publicado','1 rollo','Polonia/ES','Alta','https://packhelp.com/p/honeycomb-paper/plain/'],
['8 · Packaging','Papel de seda impreso','Presentación','Packhelp ES','Papel de seda personalizado 20/35 g','100 ud 0,90 € · 500 ud 0,30 € (sin IVA)','0,90 €/ud a 100','Publicado','30','Polonia/ES','Alta','https://packhelp.es/p/papel-de-seda/personalizable/'],
['8 · Packaging','Etiqueta kraft EN BLANCO','Presentación','Etinova','Etiqueta kraft Ø50 mm en blanco, rollo de 500','Se estampa a mano con el sello: más barata y más artesana','0,061 €/ud','Publicado','500','España','Alta','https://www.etinova.com/'],
['8 · Packaging','Sello de caucho + tampón','Presentación','sellosdecaucho.com','Sello cuadrado 50×50 mm de haya + tampón','Pago único; sirve para cajas, seda y tarjetas','15,95 € + 3,10 €','Publicado','1','España','Alta','https://www.sellosdecaucho.com/'],
['8 · Packaging','Sello de lacre','Presentación (opcional)','stampa.es','Sello de lacre de latón Ø15-30 + barras (2,19 €/barra)','Pago único','38,50 €','Publicado','1','España','Alta','https://stampa.es/'],
['8 · Packaging','Tarjeta de garantía 650 g','Presentación','Vistaprint ES','Tarjeta extragruesa 650 g/m²','100 ud 0,32 € · 500 ud 0,11 € (IVA incl.)','0,32 €/ud a 100','Publicado','100','España','Alta','https://www.vistaprint.es/tarjetas-de-visita/extragruesas'],
['8 · Packaging','Tarjeta premium 600 g','Presentación','MOO','Luxe 600 g Mohawk, 4 capas, borde de color. Entrega al día siguiente','100 ud 0,74 € sin IVA','0,74 €/ud','Publicado','50','Reino Unido','Alta','https://www.moo.com/es/business-cards/luxe'],
['8 · Packaging','Cinta de papel engomado','Cierre','Sticker Mule','Cinta kraft engomada 71 mm personalizada, envío gratis','≈0,29 €/caja (0,5 m)','0,57 €/m','Publicado','30 m','—','Alta','https://www.stickermule.com/es/products/cinta-de-embalaje'],
['8 · Packaging','Caja de envío corrugado','Envío','Kartox','Cajas a medida de ondulado; catálogo desde 0,46 €','Canal B/C, 200 lb / 32 ECT — el grado que exige ISTA 3A','~0,60 €/ud','ESTIMADO','1','España','Media','https://www.kartox.com/cajas-a-medida'],
['8 · Packaging','AVISO — pulpa moldeada a medida','—','—','INVIABLE a esta escala: molde desde 3.000 $ y arranque de 1.000-2.000 uds','Umbral de viabilidad: 5.000-10.000 uds','—','—','—','—','Dato verificado','https://www.innaturepack.com/'],
['8 · Packaging','AVISO — protección mínima','Envío','Norma ISTA 3A / FedEx','5 cm de relleno en las SEIS caras entre caja de producto y caja de envío','Doble caja obligatoria. Objetivo: 760 mm de caída y ~17 impactos','—','—','—','—','Dato verificado','https://ista.org/'],
['8 · Packaging','Ensayo de caída (validación)','Control','ITENE (Paterna, Valencia)','Laboratorio español de ensayo de embalaje. Tel. 961 820 000','Caída 760 mm en 10 orientaciones','No publican tarifa','No publicado','—','España','Alta','https://www.itene.com/'],

// ───────────────────────────── ENVÍOS ─────────────────────────────
['9 · Envíos','Envío nacional asegurado','Península','Correos Paq Premium + Valor Declarado','1-2 días. VD 1,5 %, mínimo 1,67 €, máximo 6.000 €','NO excluye relojes. Toda la cadena publicada','15,35 € + 7,50 € (para 500 €)','Publicado','1','España','Alta — RECOMENDADO','https://www.correos.es/'],
['9 · Envíos','Envío nacional económico','Península','Correos Paq Estándar + VD','2-4 días','Misma cobertura','13,65 € + VD','Publicado','1','España','Alta','https://www.correos.es/'],
['9 · Envíos','Seguro «Joyería o Valores»','Península','MRW','ÚNICO operador cuyo clausulado admite relojes POR ESCRITO (cl. 2.3)','0,80 % + 1 €/envío, mínimo 3,75 € + IVA, máx 50.000 €','~5 € para 500 €','Publicado','1','España','Alta — RECOMENDADO','https://www.mrw.es/uso_MRW_mensajeria/condiciones_venta/'],
['9 · Envíos','Valor declarado','Península','SEUR','Zona gris: exige tasación oficial para asegurar objetos de valor','1,40 %, mínimo 4 €, máx 6.000 €','Pedir tarifa','No publicado','1','España','Media-alta','https://www.seur.com/es/condiciones-de-transporte/'],
['9 · Envíos','NO USAR — excluye relojes','—','GLS Spain','Condiciones generales cl. 2: excluye joyas, RELOJES, perlas y obras de arte','Enviar por aquí = sin derecho a reclamación','—','—','—','España','Alta (literal)','https://gls-group.com/ES/downloads/glsspain_condicionesgenerales.pdf'],
['9 · Envíos','NO USAR — excluye relojes','—','Correos Express','Excluye joyas y metales preciosos','—','—','—','—','España','Alta (literal)','https://www.correosexpress.com/'],
['9 · Envíos','RIESGO — zona gris','—','UPS','Prohíbe «artículos de valor inusual» y advierte que la lista NO es exhaustiva','Además no cubre relojes de más de 500 USD','—','—','—','—','Alta','https://www.ups.com/assets/resources/webcontent/en_GB/service-guide-base-ES.pdf'],
['9 · Envíos','Envío a la UE','UE','Correos Paq Standard Internacional','Seguro 1 %, mínimo 2,04 €, máximo 3.000 €','Confirmar en oficina que el país de destino admite seguro','33,07 € (EU1)','Publicado','1','España','Alta','https://www.correos.es/'],
['9 · Envíos','Envío a Canarias','Canarias','Correos Paq Premium + DUA','Es EXPORTACIÓN: se factura sin IVA','25,45 € + DUA 14,42 € + VD','≈47,37 € para un reloj de 500 €','Publicado','1','España','Alta','https://www.correos.es/'],
['9 · Envíos','AVISO — IGIC en Canarias','Canarias','Agencia Tributaria Canaria','El tipo incrementado se aplica a joyería: confirmar si un reloj tributa al 7 % o al 13,5-15 %','Diferencia de ~32 € por unidad. Avisar en el checkout','—','A CONFIRMAR','—','España','Media-alta','https://www3.gobiernodecanarias.org/tributos/atc/'],
['9 · Envíos','AVISO — reglas de póliza','Todos','—','Siempre con FIRMA y tracking. Etiquetado NEUTRO: nada de marca ni la palabra «reloj» fuera','Varias pólizas rechazan el siniestro solo por esto','—','—','—','—','Dato verificado','https://www.mrw.es/uso_MRW_mensajeria/condiciones_venta/'],

// ───────────────────── HERRAMIENTA DEL TALLER (MADRID) ─────────────────────
['10 · Herramienta','Prensa de cristales y fondos','Montaje','Bergeon 5500 — Suministros Revuelto (Madrid)','La imprescindible. Versión completa 5500-A: 599,90 €','Tel. 915 216 149','252,00 € sin IVA','Publicado','1','España','Alta','https://suministrosrevuelto.com/839-prensas-bergeon'],
['10 · Herramienta','Potencia de encajar agujas','Montaje','Horotec MSA 05.055 — Sum. Revuelto','Con 8 tases. Lo que de verdad quieres para serie','Alternativa: Bergeon 5378 a 72 €','120,00 € sin IVA','Publicado','1','España','Alta','https://suministrosrevuelto.com/863-utiles-poner-agujas-y-potencias'],
['10 · Herramienta','Útil manual de agujas','Montaje','Bergeon 7404-S03 — Sum. Revuelto','Juego de 3','—','67,40 € sin IVA','Publicado','1','España','Alta','https://suministrosrevuelto.com/863-utiles-poner-agujas-y-potencias'],
['10 · Herramienta','Extractor de agujas (Presto)','Montaje','Bergeon 4344-9 — Sum. Revuelto','Rebajado de 27 €','—','20,00 € sin IVA','Publicado','1','España','Alta','https://suministrosrevuelto.com/prestos-varios/1579-presto-sacar-agujar-tipo-n-1.html'],
['10 · Herramienta','Vacuómetro de hermeticidad 3 atm','Control','Suministros Revuelto','Imprescindible si el reloj declara estanqueidad. Capacidad 2 relojes','Rebajado de 300 €','199,90 € sin IVA','Publicado','1','España','Alta','https://suministrosrevuelto.com/es/vacuometros/33034-vacuometro-agua-3-atmosferas.html'],
['10 · Herramienta','Abrefondos roscados','Montaje','Bergeon 5700-Z — Sum. Revuelto','Por encargo. Pedir precio profesional a Kirman antes de comprar','—','890,00 € sin IVA','Publicado','1','España','Alta','https://suministrosrevuelto.com/potencias-de-volante/32596-util-abrir-fondos-rosca-bergeon-5700-z.html'],
['10 · Herramienta','Timegrapher','Control','Weishi No.1000','Comprobador de marcha. El 1900 solo añade pantalla en color','~95-196 € según fuente','~150 €','ESTIMADO','1','—','Media','https://www.javiergutierrezchamorro.com/weishi-timegrapher-no-1000-mtg1000/'],
['10 · Herramienta','Lupa frontal Optivisor','Montaje','Suministros Revuelto','1,75×. Rebajada de 44 €','—','29,90 €','Publicado','1','España','Alta','https://suministrosrevuelto.com/564-lupa-binocular'],
['10 · Herramienta','Lupa estereoscópica','Control','Euromex NOVEX AP-4 — Amaina','20×','—','196,95 € con IVA','Publicado','1','España','Alta','https://www.amaina.com/18-microscopios-lupas-binoculares'],
['10 · Herramienta','Mesa de relojero','Taller','ComraShop','Mesa Relojero Extra, 10 cajones','Web profesional, IVA no incluido','1.180,00 € sin IVA','Publicado','1','España','Alta','https://comrashop.es/84-mesas-de-trabajo'],
['10 · Herramienta','Acceso profesional Bergeon','Todos','Kirman (Sevilla)','Distribuidor oficial de Bergeon, Witschi, Elma y Horotec. Precios tras registro','PEDIR ACCESO: probablemente mejore los 890 € del 5700-Z','Registro profesional','No publicado','—','España','Alta','https://tienda.kirman.com/bergeon2'],
['10 · Herramienta','Formación — hermeticidad y peritaje','Taller','Escuela de Relojería Kirman','Masterclass de 8 h. Exactamente la formación de quien monta series con garantía propia','También cristales (8 h) y módulos de mecánico','No publicado','No publicado','—','España','Alta','https://www.kirman.com/escuela-de-relojeria-kirman/'],
['10 · Herramienta','Formación reglada','Taller','Institut Mare de Déu de la Mercè (Barcelona)','ÚNICO centro de FP de relojería de España. ~2.000 h, vinculado a WOSTEP','Público','No publicado','No publicado','—','España','Alta','https://www.educaweb.com/curso/ciclo-formativo-grado-medio-mantenimiento-reparacion-relojeria-barcelona-44962/'],

// ───────────────────────────── LUME ─────────────────────────────
['11 · Lume','Pigmento Super-LumiNova','Esfera y agujas','RC Tritec AG (Teufen, Suiza)','EL fabricante con licencia. Asesoran grado, color y granulometría','Grados: Standard, A, X1, X2. Colores: C3, BGW9, C1, Old Radium','No publican precio','No publicado','No publicado','Suiza','Alta','https://www.rctritec.com/en/superluminova'],
['11 · Lume','Pigmento al detalle','Prototipo','Dial Maker Shop','SLN C3 y BGW9, 1 g Standard Grade','—','40,00 USD/g','Publicado','1','—','Media-alta','https://www.dialmaker.shop/collections/swiss-super-luminova'],
['11 · Lume','Kits de aplicación','Prototipo','DIY Watch Club','Kits de SLN suizo y de Nemoto. Distinguen ambos: señal de honestidad','—','20-145 USD','Publicado','1','Hong Kong','Media-alta','https://shop.diywatch.club/collections/lume-powder-and-kit'],
['11 · Lume','AVISO — el lume va en el pedido de esfera','Esfera y agujas','—','El lume se aplica EN FÁBRICA, no después. Exigir que esfera y agujas se luman con el MISMO LOTE','Si no, salen dos tonos distintos en el mismo reloj','—','—','—','—','Dato verificado','https://www.rctritec.com/en/superluminova/qualities-1'],
['11 · Lume','AVISO — cómo verificar que es suizo','Esfera y agujas','—','La química es la misma familia: un análisis básico NO distingue. Lo que distingue: ensayo DIN 67510-1','Exigir albarán de RC Tritec con nº de lote + muestra de retención precintada','—','—','—','—','Dato verificado','https://www.rctritec.com/en/superluminova'],

// ─────────────────── CUMPLIMIENTO LEGAL (NO ES OPCIONAL) ───────────────────
['12 · Legal','Garantía legal en España','Todos','RDL 7/2021','TRES años de garantía legal, no dos. Y repuestos obligatorios 10 años','Anunciar 2 años puede leerse como limitar un derecho: sancionable. YA CORREGIDO EN LA WEB','—','—','—','España','Verificado','https://portal-cec.consumo.gob.es/en/comunicacion/noticias/2022/espana-amplia-la-garantia-legal-minima-de-dos-tres-anos'],
['12 · Legal','RAEE — solo si lleva CUARZO','T1 Alba','RD 993/2022','Si el reloj lleva cuarzo eres FABRICANTE DE AEE: alta en RII-AEE, marcado CE, RoHS, SCRAP y pilas','Si es puramente mecánico, NADA de esto aplica. Decisión de negocio antes que ninguna otra','—','—','—','España','Verificado','https://industria.gob.es/registros-industriales/RAEE/Documents/07.2024%20Guia%20alta%20de%20productores%20en%20el%20RII-AEE_rev%20MINTUR_def.pdf'],
['12 · Legal','Níquel — REACH Anexo XVII','Todos','EN 1811:2023','Caja, fondo, corona, hebilla y brazalete van en contacto con la piel. Límite 0,5 µg/cm²/semana','PEDIR EL ENSAYO EN 1811 al fabricante de la caja y guardarlo','—','—','—','UE','Verificado','https://www.sgs.com/en-us/news/2024/01/safeguards-0224-eu-harmonizes-en-1811-2023-for-nickel-release-reach-annex-xvii-restriction'],
['12 · Legal','Marcas registradas ajenas','Todos','—','«Hardlex» es de Seiko (usar mineral K1) y «Tiffany Blue» es de Tiffany & Co. (usar solo Pantone)','La BOM dice «esfera TIFFANY»: CAMBIARLO','—','—','—','—','Verificado','https://www.rctritec.com/'],
['12 · Legal','Riesgo de diseño LO-06 y LO-07','Ocho Lados y Bitácora','EUIPO','Ser estéril protege de la marca, NO del diseño. Verificar ANTES de pagar utillaje','El propio Excel lo marca en rojo','—','—','—','UE','Verificado','https://www.euipo.europa.eu/es']
];

function volcarCompras() {
  var libro = SpreadsheetApp.getActiveSpreadsheet();

  // Conserva lo que Óscar hubiera escrito en Estado / Notas
  var previas = {};
  var vieja = libro.getSheetByName(HOJA);
  if (vieja) {
    var datos = vieja.getDataRange().getValues();
    for (var i = 1; i < datos.length; i++) {
      var clave = datos[i][1] + '|' + datos[i][3];   // Componente + Proveedor
      if (datos[i][12] || datos[i][13]) previas[clave] = [datos[i][12], datos[i][13]];
    }
    libro.deleteSheet(vieja);
  }

  var h = libro.insertSheet(HOJA);

  // Título
  h.getRange(1, 1).setValue('laOra · LO-07 «Bitácora» — proveedores y enlaces de compra');
  h.getRange(1, 1, 1, CABECERA.length).merge()
   .setFontSize(14).setFontWeight('bold')
   .setBackground('#14181B').setFontColor('#F5D34D')
   .setVerticalAlignment('middle');
  h.setRowHeight(1, 38);

  h.getRange(2, 1).setValue(
    'Ningún precio es una cotización: son precios publicados al detalle o estimaciones, marcados en la columna «¿Precio?». ' +
    'Los fabricantes serios no publican tarifa B2B — hay que pedirla. Rellena Estado y Notas; el resto se rehace al reejecutar el script.');
  h.getRange(2, 1, 1, CABECERA.length).merge()
   .setFontSize(10).setFontStyle('italic').setFontColor('#6E7679')
   .setWrap(true).setVerticalAlignment('middle');
  h.setRowHeight(2, 32);

  // Cabecera
  h.getRange(3, 1, 1, CABECERA.length).setValues([CABECERA])
   .setFontWeight('bold').setBackground('#14181B').setFontColor('#FFFFFF')
   .setVerticalAlignment('middle');
  h.setRowHeight(3, 26);

  // Datos
  var filas = FILAS.map(function (f) {
    var clave = f[1] + '|' + f[3];
    var guardado = previas[clave] || ['', ''];
    return f.concat(guardado);
  });
  h.getRange(4, 1, filas.length, CABECERA.length).setValues(filas);

  // Enlaces clicables en la columna 12
  for (var i = 0; i < filas.length; i++) {
    var url = filas[i][11];
    if (url && url.indexOf('http') === 0) {
      h.getRange(4 + i, 12).setFormula('=HYPERLINK("' + url + '";"Abrir ↗")');
    }
  }

  // Colores por bloque
  var tonos = {
    '1 · Caja y brazalete': '#FFF6D6', '2 · Movimientos': '#EFEDE8',
    '3 · Esfera y agujas': '#FFF6D6', '4 · Cristales': '#EFEDE8',
    '5 · Juntas y cierre': '#FFF6D6', '6 · DLC Eclipse': '#EFEDE8',
    '7 · Taller Madrid': '#FFF6D6', '8 · Packaging': '#EFEDE8',
    '9 · Envíos': '#FFF6D6', '10 · Herramienta': '#EFEDE8',
    '11 · Lume': '#FFF6D6', '12 · Legal': '#FBE3E0'
  };
  for (var j = 0; j < filas.length; j++) {
    var tono = tonos[filas[j][0]];
    if (tono) h.getRange(4 + j, 1, 1, CABECERA.length).setBackground(tono);
    // Avisos en rojo suave
    if (filas[j][1].indexOf('ATENCIÓN') === 0 || filas[j][1].indexOf('AVISO') === 0 ||
        filas[j][1].indexOf('NO USAR') === 0 || filas[j][1].indexOf('RIESGO') === 0) {
      h.getRange(4 + j, 1, 1, CABECERA.length).setBackground('#FBE3E0').setFontWeight('bold');
    }
  }

  // Formato general
  var anchos = [150, 210, 120, 190, 300, 230, 150, 120, 90, 120, 120, 90, 120, 240];
  for (var c = 0; c < anchos.length; c++) h.setColumnWidth(c + 1, anchos[c]);
  h.getRange(4, 1, filas.length, CABECERA.length).setWrap(true).setVerticalAlignment('top');
  // Solo filas: no se pueden inmovilizar columnas si las filas de título
  // están combinadas a lo ancho (Sheets lo rechaza).
  h.setFrozenRows(3);

  // Validación de la columna Estado
  var estados = SpreadsheetApp.newDataValidation()
    .requireValueInList(['', 'Pendiente', 'Correo enviado', 'Cotización recibida',
                         'Muestra pedida', 'Muestra recibida', 'Validado', 'Descartado'], true)
    .build();
  h.getRange(4, 13, filas.length, 1).setDataValidation(estados);

  h.getRange(3, 1, filas.length + 1, CABECERA.length)
   .setBorder(true, true, true, true, true, true, '#C6C3BB', SpreadsheetApp.BorderStyle.SOLID);

  libro.setActiveSheet(h);
  SpreadsheetApp.getUi().alert(
    'Listo: ' + filas.length + ' proveedores volcados en «' + HOJA + '».\n\n' +
    'Rellena las columnas Estado y Notas conforme vayas pidiendo cotizaciones. ' +
    'Si vuelves a ejecutar el script, esas dos columnas se conservan.');
}
