/* ============================================================
   laOra · EL MOTOR DEL CONFIGURADOR, 2026
   ============================================================
   Óscar, 29/08/2026: «el estilo del Lunar pasa a ser el único estilo a
   utilizar en el resto de modelos, por tanto Trinchera y todos los demás
   ya deberían tener instalado el configurador con el estilo Lunar».

   Esto SALE DE `lunar.html`, donde eran 1.858 líneas dentro de la propia
   página. Mientras estuvieron ahí, el configurador era de un modelo. Aquí
   es de la casa: los diez lo cargan y cada uno le pasa SUS piezas.

   CÓMO SE USA. La ficha define sus tablas y, al final, deja el modelo en
   `window.LAORA_MODELO`; este fichero se carga después y arranca solo.

       <script>
         var MOVS = {...}, ESFERAS = {...};      // lo del modelo
         window.LAORA_MODELO = { slug: 'lunar', MOVS: MOVS, … };
       </script>
       <script src="/assets/js/configurador-2026.js"></script>

   QUÉ PONE EL MODELO Y QUÉ PONE EL MOTOR. El modelo pone las PIEZAS
   —movimientos, cajas, biseles, esferas, agujas, correas, cierres,
   cristales—, los PAQUETES del proveedor con sus costes, las CAPAS con
   las que se dibuja, su `slug` y su `nombre`, y cuatro frases suyas: la
   referencia, la descripción, la resistencia al agua y el dicho completo.

   El motor pone TODO LO DEMÁS y es igual en los diez: los pasos que se
   abren de uno en uno, el montaje por capas, la foto de presentación
   hasta la primera elección, el precio desde el coste con su suelo, la
   barra de precio, las miniaturas de la correa, la criba y el carrito.

   ⚠️ UN SOLO ENVOLTORIO, y esto costó una tarde. Todo vive dentro del
   `(function () {` que ya traía el configurador, y los alias del modelo se
   declaran DENTRO de él. Al sacarlo de la ficha se probó a envolverlo en
   otro IIFE con los alias fuera: las funciones quedaban en un ámbito y los
   alias en otro, y el volcador veía `MOVS` pero no `precio`. Si hay que
   añadir algo, va aquí dentro.
   ============================================================ */
(function () {
  var M = window.LAORA_MODELO;
  if (!M) return;

  /* Las piezas del modelo, con el nombre corto de siempre para que el
     motor se lea igual que cuando vivía dentro de la ficha. */
  /* ⚠️ TODO LO QUE NO TRAIGA EL MODELO VIENE VACÍO, NO `undefined`. Un
     modelo recién nacido no tiene capas, ni miniaturas, ni cierres, ni
     paquetes: es el caso normal desde que los diez tienen configurador sin
     tener fotos (Óscar, 29/08/2026). Sin estos «o vacío» el motor se paraba
     con «Cannot read properties of undefined» a la primera, y la ficha se
     quedaba con las tarjetas puestas y los pasos escondidos. */
  var MOVS = M.MOVS || {}, TAMANOS = M.TAMANOS || {}, MM = M.MM,
      CAJAS = M.CAJAS || {}, ESFERAS = M.ESFERAS || {}, BISELES = M.BISELES || {},
      AGUJAS = M.AGUJAS || {}, CORREAS = M.CORREAS || {},
      CORREA_MAT = M.CORREA_MAT || {}, MATERIALES = M.MATERIALES || {},
      CRISTALES = M.CRISTALES || {}, FECHA = M.FECHA || '', LOGO = M.LOGO || 0,
      SERIE_V = M.SERIE_V || '', CAPA = M.CAPA || {}, CAPA_IMG = M.CAPA_IMG || '',
      PILA = M.PILA || [],
      CIERRES = M.CIERRES || {}, CIERRE_IMG = M.CIERRE_IMG || '',
      MINI = M.MINI || {}, MINI_IMG = M.MINI_IMG || '', MINI_ALT = M.MINI_ALT || {},
      PAQUETES = M.PAQUETES || [], AGUJAS_LIBRES = M.AGUJAS_LIBRES,
      COSTES_PUESTOS = !!M.COSTES_PUESTOS, CADENA = M.CADENA || [];
  var e = M.e;

  /* ⚠️ LO QUE SE GUARDA EN EL NAVEGADOR VA CON EL NOMBRE DEL MODELO
     DELANTE. Eran tres llaves escritas a mano con «lunar» dentro: con el
     motor compartido, el segundo modelo habría leído y pisado la criba y
     las combinaciones del primero. */
  var LLAVE = 'laora.' + (M.slug || 'modelo') + '.';

  /* ---------- EL CONTRATO DE PASOS ----------
     El orden que llevan los diez modelos, con sus dos reglas: una sola
     opción sale señalada y explicada, y sin opciones el paso no aparece.
     Manda `assets/datos/pasos-2026.json`; esto es una copia literal que
     mete `herramientas/sincronizar_pasos.py`, porque el motor pinta antes
     de que el cliente vea nada y además corre fuera del navegador cuando
     el volcador calcula el catálogo: un `fetch` estorbaría en los dos
     sitios. El gancho de pre-commit avisa si las dos se separan. */
  /* >>> pasos-2026.json · lo copia herramientas/sincronizar_pasos.py */
  var PASOS = [
    {
      "id": "tamano",
      "rotulo": "Tamaño de la caja",
      "de": "caja.tamanos",
      "tarjeta": "caja"
    },
    {
      "id": "caja",
      "rotulo": "Material",
      "de": "caja.materiales",
      "nota": "Acero, PVD, bronce o titanio.",
      "tarjeta": "caja"
    },
    {
      "id": "bisel",
      "rotulo": "Bisel",
      "de": "bisel.colores",
      "salta_si": "caja.integrada",
      "tarjeta": "caja"
    },
    {
      "id": "biselmat",
      "rotulo": "Material y acabado del bisel",
      "de": "bisel.materiales",
      "salta_si": "caja.integrada",
      "tarjeta": "caja"
    },
    {
      "id": "esftipo",
      "rotulo": "Tipo de esfera",
      "de": "esfera.tipos",
      "tarjeta": "caja"
    },
    {
      "id": "esf",
      "rotulo": "Esfera",
      "de": "esfera.colores",
      "tarjeta": "caja"
    },
    {
      "id": "agujas",
      "rotulo": "Agujas",
      "de": "agujas.colores",
      "tarjeta": "caja"
    },
    {
      "id": "cristal",
      "rotulo": "Cristal",
      "de": "cristal",
      "tarjeta": "caja"
    },
    {
      "id": "mov",
      "rotulo": "Calibre",
      "de": "movimiento",
      "tarjeta": "mov"
    },
    {
      "id": "correamat",
      "rotulo": "Material",
      "de": "correa.familias",
      "tarjeta": "correa"
    },
    {
      "id": "correa",
      "rotulo": "Color",
      "de": "correa.colores",
      "tarjeta": "correa"
    },
    {
      "id": "pespunte",
      "rotulo": "Pespunte",
      "de": "correa.pespuntes",
      "tarjeta": "correa"
    },
    {
      "id": "cierre",
      "rotulo": "Cierre",
      "de": "correa.cierres",
      "tarjeta": "correa"
    },
    {
      "id": "cierrecolor",
      "rotulo": "Color del cierre",
      "de": "correa.colores_cierre",
      "tarjeta": "correa"
    }
  ];
  var TARJETAS = [
    {
      "id": "caja",
      "titulo": "La caja"
    },
    {
      "id": "mov",
      "titulo": "El movimiento"
    },
    {
      "id": "correa",
      "titulo": "El brazalete o la correa",
      "marca": "correa"
    }
  ];
  /* <<< fin del contrato de pasos */

  /* ---------- LOS PASOS SE PINTAN, NO SE ESCRIBEN ----------
     Hasta el 29/08/2026 las once cajas de opciones estaban escritas a mano
     en el HTML de la ficha, con su rótulo y su orden. Con diez modelos eso
     son diez copias que se separan en cuanto alguien cambia una: el orden
     lo manda el contrato, así que el motor las monta desde él.

     QUÉ TABLA LLENA CADA PASO sigue decidiéndolo `pinta()`, que es donde
     vive lo que un paso puede depender de otro. Aquí sólo se pone el
     armazón: la tarjeta, el rótulo, el hueco de los botones y el de la
     explicación. Un paso al que `pinta()` no le eche opciones se queda
     vacío y `pinta()` lo esconde, que es la segunda regla del contrato. */
  function montaPasos() {
    var caja = $('[data-pv-pasos]');
    if (!caja || !PASOS.length) return;
    var html = '';
    TARJETAS.forEach(function (t) {
      var suyos = PASOS.filter(function (p) { return p.tarjeta === t.id; });
      if (!suyos.length) return;
      html += '<section class="pv-tarjeta"' +
              (t.marca ? ' data-pv-tarjeta="' + t.marca + '"' : '') + '>' +
              '<h2 class="pv-tarjeta-tit">' + t.titulo + '</h2>';
      suyos.forEach(function (p) {
        html += '<div class="pv-g" data-g="' + p.id + '" hidden>' +
                '<p class="pv-g-cab"><span>' + p.rotulo + '</span>' +
                '<span class="pv-g-valor" data-valor="' + p.id + '"></span></p>' +
                '<div class="pv-opciones" data-pv="' + p.id + '"></div>' +
                /* La foto del cierre vive dentro de su paso: es lo único que
                   un paso enseña además de sus botones. */
                (p.id === 'cierre'
                  ? '<img class="pv-cierre-foto" data-pv-cierre-foto alt="" hidden>' : '') +
                '<p class="pv-g-explica" data-explica="' + p.id + '"></p>' +
                '</div>';
      });
      html += '</section>';
    });
    caja.innerHTML = html;
  }

  /* UN PASO SIN OPCIONES NO SE VE. Es la segunda regla del contrato, y se
     aplica después de que `pinta()` haya repartido los botones: el paso
     nace escondido y sólo aparece si le ha caído alguno. */
  function escondeVacios() {
    PASOS.forEach(function (p) {
      var g = $('[data-g="' + p.id + '"]');
      if (!g) return;
      var ops = g.querySelector('[data-pv="' + p.id + '"]');
      g.hidden = !ops || !ops.children.length;
    });
  }

  /* Las cuatro frases que solo sabe decir el modelo. */
  function referencia() { return M.referencia(e); }
  function agua() { return M.agua(e); }
  function descripcion() { return M.descripcion(e); }
  function dichoCompleto() { return M.dichoCompleto(e); }

  /* LO QUE EL MOTOR LE PRESTA AL MODELO para que pinte sus pasos. Se pasa
     explícito y no por variables sueltas: así se ve de un vistazo con qué
     cuenta una ficha, y añadir algo aquí es una decisión, no un descuido. */
  var HERRAMIENTAS = {
    botones: botones, rotula: rotula, deTabla: deTabla, valores: valores,
    combos: combos, cribado: cribado, marcado: marcado,
    /* ⚠️ `$` y `todos` van ENVUELTOS. Son `var`, no `function`, así que
       cuando este objeto se arma —lo primero de todo, para que el modelo
       tenga sus herramientas antes del primer coste— todavía valen
       `undefined`. Envueltas se resuelven al llamarlas, que es cuando ya
       existen. */
    $: function (sel) { return $(sel); },
    todos: function (sel) { return todos(sel); },
    matDe: matDe, primeraDe: primeraDe, paqueteDe: paqueteDe,
    /* Cada paso enseña sólo lo que sigue teniendo salida con lo ya elegido
       por encima. `o[2]` es «no lo dibujes» y `o[3]` es «dibújalo apagado». */
    soloDe: function (tabla, campo, fij, apagaSobrantes) {
      var ok = valores(campo, fij);
      return deTabla(tabla).map(function (o) {
        var fuera = ok.indexOf(o[0]) < 0;
        if (apagaSobrantes) o[3] = fuera; else o[2] = fuera;
        return o;
      });
    }
  };

  /* ⚠️ Y SE LE ENTREGAN AL MODELO AQUÍ, ANTES DE NADA. Se probó a pasarlas
     solo al pintar los pasos, y no vale: `costes()` se llama antes que el
     primer pintado —el precio se calcula al principio de `pinta()`— y el
     modelo se quedaba sin herramientas justo cuando las necesitaba. */
  if (M.tomaHerramientas) M.tomaHerramientas(HERRAMIENTAS);

  /* El coste de la caja NO está aquí: va en PAQUETES, porque el proveedor
     la vende montada con bisel, esfera y agujas dentro. Aquí sólo viven el
     nombre y el material. */
  /* EL DIÁMETRO (Óscar, 28/08/2026: «el tamaño de la caja es de 40 mm»).
     Hoy sólo hay uno, así que NO entra en la referencia: meterlo movería las
     54 que ya se venden sin que cambie el reloj. El día que haya una segunda
     medida hay que meterlo, porque entonces sí serán dos productos. */
  /* Las azules son horaria y minutero AZULADOS; el segundero del
     cronógrafo y los índices siguen siendo de acero. De momento sólo hay
     foto con la esfera blanca y el bisel azul: el resto sale con el cartel
     hasta que se fotografíe. */
  /* LAS CORREAS DE CAUCHO SON LAS DE LAS FOTOS (Óscar, 28/08/2026).
     Sustituyen a la lista de un solo color del 27/08 —negro, azul marino,
     marrón, gris, naranja y negro/azul celeste—, que se quedó sin ninguna
     foto: ahora son las cinco de dos tonos que él fotografió.

     EL CAUCHO BAJA A 9,89 (Óscar, 28/08/2026, con el enlace del proveedor:
     https://es.aliexpress.com/item/1005008055142978.html). Venía de 12,99.
     Sigue siendo MÁS BARATO que el brazalete de 19,79, así que con correa
     el Lunar baja un escalón, y ahora dos. */

  /* LA CORREA, EN DOS PASOS: material y color, como Tesla parte el
     exterior en color y llantas. El estado sigue siendo uno solo —`e.correa`—
     y el material se deduce de él; elegir material salta a la primera correa
     de ese material. */
  /* DE QUÉ FAMILIA ES UNA CORREA, y cuál es la primera de cada familia.
     Con `CORREA_MAT` puesto, el motor lo sabe solo; sin él —un modelo que
     todavía no reparte sus correas por familias— cada correa es su propia
     familia y el paso del material no estorba. */
  function matDe(c) {
    return (CORREA_MAT && CORREA_MAT[c]) || c;
  }
  function primeraDe(mat) {
    var k = Object.keys(CORREAS || {}).filter(function (c) { return matDe(c) === mat; });
    return k[0];
  }

  /* ⚠️ LAS FOTOS DEL LUNAR VAN CON SU FONDO PINTADO (Óscar, 27/08/2026:
     «vamos a poner el fondo como viene… en el azul y en el oro rosa, y
     además en todos los del lunar»). Azul marino la de agujas azules, oro
     rosa la de agujas de oro rosa. Ya no se piden transparentes.

     Las dos primeras —la esfera negra y la blanca con agujas plata— siguen
     recortadas y sin fecha: son las viejas, y hay que rehacerlas con las dos
     cosas.

     LAS FOTOS QUE EXISTEN, y nada más. Una línea por foto publicada, y se
     añade EN EL MISMO COMMIT que el AVIF. Lo que no esté aquí sale con el
     cartel de «Fotografía en preparación», que es la verdad.

     La primera entró el 27/08/2026: la madre del Lunar, 4096² con alfa de
     verdad. La anterior se rechazó —fondo de damero PINTADO en los píxeles
     y 1.254 px— y Óscar la rehizo. */
  /* ⛔ AQUÍ VIVÍA `SERIE`: una foto por combinación entera, con la clave
     hecha de caja+esfera+bisel+agujas+correa. Se ha ido el 29/08/2026 por
     orden de Óscar —«no quiero que se guarde nada de fotos y combinaciones
     anteriores de ningún modelo, todo desde cero»—, y porque es justo lo
     contrario de montar por piezas: una foto por combinación son miles de
     imágenes para enseñar las mismas cinco piezas barajadas. */


  /* ============================================================
     EL MECANISMO, el mismo que el del Trinchera (Óscar, 26/08/2026:
     «crea el configurador igual que el del trinchera, con el mismo
     mecanismo»). Los nombres son los de allí a propósito: el día que se
     arregle algo en uno, se sabe dónde está en el otro.
     ============================================================ */

  var $ = function (s) { return document.querySelector(s); };
  /* DESDE QUE HAY BARRA, EL PRECIO SALE EN DOS SITIOS. `$` devuelve el
     primero que encuentra, así que lo que se pinta por duplicado —el
     precio, la cuota de Klarna y el botón de comprar— se pinta con esto
     en TODOS. Si se dejara `$`, la barra se quedaría con el precio de
     ejemplo del HTML puesto para siempre. */
  var todos = function (s) {
    return [].slice.call(document.querySelectorAll(s));
  };
  function eu(v) { return v.toFixed(2).replace('.', ',') + ' €'; }

  /* ---------- LA FIRMA DE UNA COMBINACIÓN ----------
     Todo lo que el cliente elige, en orden. Sirve para marcar y para vetar,
     igual que en el Trinchera. */
  function firma() {
    return [e.mov, e.esf, e.bisel, e.agujas, e.caja, e.cristal, e.correa].join('|');
  }
  /* En limpio: aquí todavía no hay nada que quitar, pero la función existe
     desde el principio para que el día que el Lunar tenga dos medidas o dos
     movimientos no haya que reescribir la lista de vetadas. */
  function canon(f) { return String(f); }

  /* Las combinaciones que Óscar da por muertas. Valen para todo el mundo:
     ni se dibujan ni entran en el catálogo del servidor. */
  var VETADAS = {};
  function vetada(f) { return !!VETADAS[canon(f)]; }
  /* El volcador tiene que ver el árbol ENTERO y descartar al final, hoja por
     hoja: leyendo los botones que la ficha esconde se caen ramas buenas.
     Es el fallo que costó cuarenta referencias sanas en el Trinchera. */
  var SIN_VETO = false;
  function sinVeto(v) { SIN_VETO = !!v; }

  /* ---------- EL MODO CURAR, sólo con `?curar` ---------- */
  /* La criba y el panel de curar son herramientas de casa: se piden por
     la barra de direcciones y no salen solas. */
  var CRIBA_VISIBLE = false;
  try { CRIBA_VISIBLE = /[?&](criba|capas)(=|&|$)/.test(location.search); } catch (x) {}
  var CURAR = false;
  try { CURAR = /[?&]curar(=|&|$)/.test(location.search); } catch (x) {}
  var COMBIS = {};
  try {
    if (window.localStorage)
      COMBIS = JSON.parse(window.localStorage.getItem(LLAVE + 'combis') || '{}') || {};
  } catch (x) { COMBIS = {}; }
  function guardaCombis() {
    recanon();
    try {
      if (window.localStorage)
        window.localStorage.setItem(LLAVE + 'combis', JSON.stringify(COMBIS));
    } catch (x) {}
  }
  /* Lo que ya está vetado deja de estar pendiente y se cae de la lista solo */
  (function () {
    var toco = false, k;
    for (k in COMBIS) if (VETADAS[canon(k)]) { delete COMBIS[k]; toco = true; }
    if (toco) {
      try {
        if (window.localStorage)
          window.localStorage.setItem(LLAVE + 'combis', JSON.stringify(COMBIS));
      } catch (x) {}
    }
  })();
  var COMBIS_CANON = {};
  function recanon() {
    COMBIS_CANON = {};
    for (var k in COMBIS) COMBIS_CANON[canon(k)] = 1;
  }
  recanon();
  function marcada(f) { return !!COMBIS_CANON[canon(f)]; }
  function desmarca(f) {
    var c = canon(f), k;
    for (k in COMBIS) if (canon(k) === c) delete COMBIS[k];
  }
  var APLICADAS = false;
  try {
    if (window.localStorage)
      APLICADAS = window.localStorage.getItem(LLAVE + 'aplicadas') === '1';
  } catch (x) {}
  function guardaAplicadas() {
    try {
      if (window.localStorage)
        window.localStorage.setItem(LLAVE + 'aplicadas', APLICADAS ? '1' : '0');
    } catch (x) {}
  }

  /* ---------- LOS BOTONES ----------
     Lo que no se puede elegir NO se dibuja (Óscar, 26/08/2026). */
  /* ⚠️ EL MATERIAL DE LA CORREA SE GUARDA, además de arrastrar el color.
     Esta función se escribió para el Lunar, donde el material NO es un paso
     del estado: se deduce de la correa elegida, y por eso aquí ponía la
     primera correa de la familia y se iba sin guardar nada.

     En los modelos generados el material SÍ es un paso —tiene su tabla y su
     valor—, y sin guardarlo pasaba esto: pulsabas «Piel italiana», la correa
     se iba a la primera de la familia... y `normaliza` la devolvía al brazalete
     de acero, porque el material seguía diciendo acero. El botón no respondía.
     (29/08/2026, la primera prueba del Trinchera nuevo.) */
  function aplicaOpcion(g, v) {
    e[g] = v;
    if (g === 'correamat') {
      var c = primeraDe(v);
      if (c) e.correa = c;
    }
  }

  function llevaAMarcada(grupo, valor) {
    var copia = {}, k;
    for (k in e) copia[k] = e[k];
    aplicaOpcion(grupo, valor);
    normaliza();
    var esta = (!SIN_VETO && vetada(firma())) || (APLICADAS && marcada(firma()));
    for (k in copia) e[k] = copia[k];
    return esta;
  }

  /* ---------- NADA SALE SEÑALADO HASTA QUE SE PULSA ----------
     Óscar, 28/08/2026: «la caja sale vacía pero con Bisel negro señalado, no
     puede haber ninguno señalado porque no lo están. Hay que esperar a que se
     señale un botón para que quede señalado».

     SÓLO EN EL MONTAJE POR CAPAS, y sólo en los pasos que dibujan una pieza.
     Ahí el reloj se construye poco a poco y la pieza no está puesta todavía:
     marcarle el botón es decir que se ha elegido algo que no se ve. La caja
     sí sale marcada —«en la primera opción damos por defecto señalada Acero,
     ok»— porque su capa se dibuja desde el principio, y el cristal también,
     porque no se ve en el dibujo y no hay nada que contradecir.

     En la tienda (sin `?capas`) NO cambia nada: allí la foto enseña el reloj
     entero desde el primer momento, así que lo marcado es lo que se ve. */
  var ESPERA_PULSACION = { bisel: 'bisel', esf: 'esf', agujas: 'agujas',
                           correamat: 'correa', correa: 'correa' };
  function marcado(g) {
    if (!CAPAS) return true;
    var q = ESPERA_PULSACION[g];
    return !q || !!tocado[q];
  }

  function botones(grupo, opciones, activo) {
    var caja = $('[data-pv="' + grupo + '"]');
    if (!caja) return;
    var marca = marcado(grupo);
    caja.innerHTML = opciones.filter(function (o) {
      return !o[2] && (o[3] || !llevaAMarcada(grupo, o[0]));
    }).map(function (o) {
      /* `o[3]` es «dibújalo pero apagado»: sirve para enseñar a dónde va el
         configurador sin dejar comprar lo que todavía no existe. */
      return '<button type="button" data-v="' + o[0] + '"' + (o[3] ? ' disabled' : '') +
             ' aria-pressed="' + (marca && !o[3] && o[0] === activo) + '">' + o[1] + '</button>';
    }).join('');
  }
  function deTabla(tabla) {
    return Object.keys(tabla).map(function (k) { return [k, tabla[k].nombre]; });
  }

  /* ============================================================
     EL MONTAJE POR CAPAS  ·  `?capas`
     ------------------------------------------------------------
     Óscar, 28/08/2026: «prefiero que se vayan sobreponiendo las capas sin
     ocultarse unas a otras. Y así nos evitamos crear 1500 imágenes, y sirve
     como juego interactivo para el cliente».

     Y SE CONSTRUYE POCO A POCO: al abrir sólo está la caja; según se va
     eligiendo, cada pieza se posa encima. Lo que todavía no se ha tocado no
     se enseña, porque enseñarlo sería decidir por el cliente.

     VA CON `?capas` Y NO EN LA TIENDA. Desde el 28/08 por la noche están
     TODAS: seis esferas, tres biseles, cinco juegos de agujas, el brazalete
     y las cinco correas de caucho. Lo que falta ya no son capas, es
     cuadrarlas: las agujas pequeñas van dentro de su capa y cada esfera
     tiene los contadores en otro sitio, así que cada pareja que sobreviva a
     la criba de Óscar necesita su copia cuadrada. Cambiar el visor entero dejaría a la mayoría de las
     combinaciones sin nada que enseñar, y eso hoy se vende. Cuando estén
     todas, se quita la condición y se acabaron los AVIF por combinación.
     ============================================================ */
  /* EL MONTAJE POR CAPAS YA NO ES UNA PRUEBA: ES LA FICHA (Óscar,
     29/08/2026). Se acabó `?capas`. El reloj se arma con las piezas que el
     cliente elige —caja, bisel, esfera, agujas, correa—, cada una su
     imagen, y ninguna foto pertenece a una combinación entera. */
  var CAPAS = true;

  /* SE PRECARGAN TODAS DE GOLPE. Cambiar el `src` de un <img> lo deja en
     blanco mientras baja el fichero nuevo, y en un carrusel eso es un
     parpadeo en cada pulsación. Las siete pesan 252 KB juntas —menos que
     tres fotos—, así que se piden una vez al abrir y a partir de ahí los
     cambios son instantáneos. */
  /* El fichero de una opción: o es un nombre, o es una tabla con una copia
     por esfera y `'*'` de comodín. */
  function ficheroCapa(grupo, valor, esf) {
    /* LA CORREA SALE DE LA BIBLIOTECA, no de la tabla del modelo: es una
       pieza compartida y se llama por lo que es. */
    if (grupo === 'correa') {
      /* Y el nombre de la pieza puede depender de más de un paso —el
         pespunte de la piel va en el mismo fichero que el color—, así que
         si el modelo sabe armarlo, se le pregunta. */
      if (M.piezaDe) return M.piezaDe(e);
      var c = CORREAS[valor];
      return c && c.pieza ? c.pieza : null;
    }
    var v = CAPA[grupo] && CAPA[grupo][valor];
    if (!v) return null;
    if (typeof v === 'string') return v;
    /* `esf` se pasa a mano desde la pantalla de criba, que dibuja parejas
       que no son la que está puesta. */
    return v[esf || e.esf] || v['*'] || null;
  }
  /* De qué carpeta sale cada pieza. Las correas ya están en la biblioteca
     de componentes; las demás siguen en la carpeta del modelo hasta que lleguen
     rehechas, que es lo que Óscar dijo el 29/08: se rehace todo. */
  var COMPONENTE_IMG = '/assets/img/componentes/';
  function baseCapa(grupo) {
    return grupo === 'correa' ? COMPONENTE_IMG + 'correas/1200/' : CAPA_IMG;
  }
  function urlCapa(grupo, valor, esf) {
    var f = ficheroCapa(grupo, valor, esf);
    return f ? baseCapa(grupo) + f + '.avif' + SERIE_V : null;
  }
  /* El bisel con el que el proveedor monta cada esfera: el del primer
     paquete que la lleve. Lo usa la criba para que cada miniatura salga con
     su bisel y no con uno cualquiera. */
  function biselDe(esf) {
    for (var i = 0; i < PAQUETES.length; i++)
      if (PAQUETES[i].esf === esf) return PAQUETES[i].bisel;
    return 'NEG';
  }
  function cadaFicheroCapa(hazlo) {
    for (var g in CAPA) {
      if (!CAPA[g]) continue;
      for (var k in CAPA[g]) {
        var v = CAPA[g][k];
        if (typeof v === 'string') hazlo(v, g);
        else for (var d in v) hazlo(v[d], g);
      }
    }
    /* Las correas van aparte porque ya no están en CAPA: son piezas de la
       biblioteca y cada una dice su nombre en `CORREAS[x].pieza`. */
    for (var c in CORREAS) {
      /* Y una correa puede tener MÁS DE UN nombre: la piel viene con el
         pespunte dentro del fichero, así que son dos. El modelo los da. */
      var piezas = M.piezasDe ? M.piezasDe(c)
                 : (CORREAS[c].pieza ? [CORREAS[c].pieza] : []);
      for (var q = 0; q < piezas.length; q++) hazlo(piezas[q], 'correa');
    }
  }

  /* ---------- LA PRECARGA, POR ESFERA ----------
     Cambiar el `src` de un <img> lo deja en blanco mientras baja el fichero
     nuevo, y en un configurador eso es un parpadeo en cada pulsación, así
     que las capas se piden por delante.

     PERO LAS AGUJAS YA NO SE PIDEN TODAS. Con una copia por esfera son 30
     capas: pedirlas de golpe son 400 KB que el cliente se baja para usar
     cinco. Se piden LAS CINCO DE LA ESFERA PUESTA, y cuando se cambia de
     esfera se piden las cinco de la nueva. Así el peso de la precarga se
     queda donde estaba antes de las copias. */
  var PRECARGADAS = false, PRECARGADA_ESF = null;
  function pideCapa(f, grupo) {
    if (!f) return;
    var i = new Image();
    i.src = baseCapa(grupo) + f + '.avif' + SERIE_V;
  }
  function precargaCapas() {
    if (!CAPAS) return;
    if (!PRECARGADAS) {
      PRECARGADAS = true;
      cadaFicheroCapa(function (f, g) { if (g !== 'agujas') pideCapa(f, g); });
    }
    if (PRECARGADA_ESF !== e.esf) {
      PRECARGADA_ESF = e.esf;
      for (var k in CAPA.agujas) pideCapa(ficheroCapa('agujas', k), 'agujas');
    }
  }

  /* ---------- MIENTRAS NADIE HA ELEGIDO NADA ----------
     Óscar, 29/08/2026: «la página del modelo arranca con la primera
     imagen así hasta que el cliente escoja su primera elección de
     componentes».

     Es la misma regla del 28/08 —ningún botón sale señalado hasta que se
     pulsa— llevada a la foto: si el cliente no ha decidido nada, la ficha
     no tiene ningún reloj concreto que enseñar, así que enseña EL reloj, el
     de la foto de presentación, y no una caja desnuda ni el cartel de
     «fotografía en preparación».

     `mov` no cuenta: viene puesto de fábrica —hay un solo movimiento— y no
     es una elección de nadie. */
  function sinElegirNada() {
    for (var k in tocado) if (k !== 'mov' && tocado[k]) return false;
    return true;
  }
  function pintaPresentacion() {
    var im = $('[data-pv-presenta]');
    var puesta = sinElegirNada();
    if (im) im.hidden = !puesta;
    return puesta;
  }

  function pintaCapas() {
    precargaCapas();
    var caja = $('[data-pv-capas]');
    if (!caja) return;
    caja.hidden = !CAPAS;
    /* ⚠️ EL BOTÓN DE CRIBA ES PARA ÓSCAR, NO PARA EL CLIENTE. Salía con
       `?capas`, y desde que el montaje por piezas ES la ficha, `CAPAS`
       está siempre puesto: sin esto, la criba se le aparecería a
       cualquiera. Ahora pide `?criba` a mano. */
    var abre = $('[data-pv-criba-abre]');
    if (abre) abre.hidden = !CRIBA_VISIBLE;
    if (!CAPAS) return;
    var puestas = {};
    PILA.forEach(function (p) {
      var img = caja.querySelector('[data-capa="' + p.capa + '"]');
      if (!img) return;
      var f = ficheroCapa(p.grupo, e[p.grupo]);
      var toca = !p.espera || !!tocado[p.espera];
      var apoyo = !p.necesita || !!puestas[p.necesita];
      if (!f || !toca || !apoyo) { img.hidden = true; img.removeAttribute('src'); return; }
      var src = baseCapa(p.grupo) + f + '.avif' + SERIE_V;
      if (img.getAttribute('src') !== src) img.setAttribute('src', src);
      img.hidden = false;
      puestas[p.capa] = true;
    });
    /* El carrusel mueve el paso que se está tocando ahora mismo. Con la
       foto de presentación puesta no hay paso que mover, y además quedaría
       flotando encima de la foto. */
    var c = $('[data-pv-carrusel]');
    if (c) {
      var g = sinElegirNada() ? null : pasoEnJuego();
      c.hidden = !g;
      if (g) c.querySelector('[data-carrusel-paso]').textContent = ROTULO[g];
    }
  }

  var ROTULO = { esf: 'Esfera', bisel: 'Bisel', agujas: 'Agujas',
                 caja: 'Material', correamat: 'Correa', correa: 'Color' };
  /* ---------- QUÉ PASO MANDA EL CARRUSEL ----------
     Óscar, 28/08/2026: «cuando el scroll baja a esfera, el cursor pasa de
     poner Bisel a poner Esfera y por tanto el selector sería para la esfera,
     después para las agujas».

     Manda el desplazamiento: de los pasos que cambian el dibujo, gana el que
     esté más cerca de la línea imaginaria del 40 % de la pantalla. Se eligió
     el 40 % y no el centro porque la columna es larga y con el centro el paso
     cambiaba demasiado tarde, cuando el grupo ya se había pasado de largo.

     Pulsar un botón también manda, porque para pulsarlo hay que estar
     mirándolo; el desplazamiento lo confirma en el mismo sitio. */
  var SEGUIBLES = ['caja', 'bisel', 'esf', 'agujas', 'correamat', 'correa'];
  /* Un paso con una sola opción no entra en la rueda: las flechas no
     tendrían a dónde ir y el rótulo se quedaría quieto engañando. Hoy le
     pasa al material de la caja, que sólo es acero. */
  function giraSolo(g) {
    var c = document.querySelector('[data-pv="' + g + '"]');
    return !!c && c.querySelectorAll('button:not([disabled])').length > 1;
  }
  var ULTIMO = null;
  function pasoPorScroll() {
    var linea = window.innerHeight * 0.40, mejor = null, cerca = 1e9;
    SEGUIBLES.forEach(function (g) {
      var caja = document.querySelector('[data-g="' + g + '"]');
      if (!caja || caja.hidden || !giraSolo(g)) return;
      var r = caja.getBoundingClientRect();
      if (!r.height) return;
      var d = Math.abs((r.top + r.bottom) / 2 - linea);
      if (d < cerca) { cerca = d; mejor = g; }
    });
    return mejor;
  }
  function pasoEnJuego() {
    var g = pasoPorScroll();
    if (g) return g;
    if (ULTIMO && ROTULO[ULTIMO]) return ULTIMO;
    return tocado.bisel ? (tocado.esf ? 'agujas' : 'esf') : 'bisel';
  }
  /* Pasar a la opción de al lado del paso en juego, dando la vuelta al
     llegar al final. Sólo cuenta lo que de verdad se puede elegir: los
     botones apagados no entran en la rueda. */
  function gira(paso) {
    var caja = $('[data-pv="' + (pasoEnJuego() || 'esf') + '"]');
    if (!caja) return;
    var bs = [].slice.call(caja.querySelectorAll('button:not([disabled])'));
    if (bs.length < 2) return;
    var i = 0, hay = false;
    bs.forEach(function (b, k) {
      if (b.getAttribute('aria-pressed') === 'true') { i = k; hay = true; }
    });
    /* Si el paso aún no se ha tocado no hay nada marcado: la primera vuelta
       de rueda pone la PRIMERA opción, no la segunda. */
    if (!hay) { bs[0].click(); return; }
    bs[(i + paso + bs.length) % bs.length].click();
  }

  /* ---------- LA FOTO ----------
     La clave es lo que se VE en la foto: caja, esfera, bisel, agujas y
     correa. El movimiento no entra: por delante no se distingue.

     CADA PIEZA TIENE SU NOMBRE DE FOTO, en su tabla. La primera versión
     armaba la clave con los nombres que se le enseñan al cliente
     —«Brazalete de acero» a minúsculas y sin espacios—, y eso ata el
     nombre de un fichero a un texto de pantalla: el día que ese texto se
     retoque, la ficha pide una foto que no existe y sale el cartel sin que
     nadie haya tocado una imagen. Así lo hace el Trinchera. */

  /* ---------- LAS CUATRO COMBINACIONES QUE EXISTEN ----------
     Óscar, 27/08/2026. Esfera, bisel y agujas no se combinan libres: hay
     CUATRO ternas y ninguna más. Se escriben tal cual él las dictó, y de
     esta tabla salen los botones, las reparaciones y lo que el volcador
     mete en el catálogo. Antes esto era una regla suelta —«con esfera negra
     no hay bisel azul»—; con cuatro ternas cerradas, una regla por pareja se
     quedaba corta.

     EL ORDEN MANDA: bisel → esfera → agujas. Cada paso enseña sólo lo que
     sigue teniendo salida con lo ya elegido, y al cambiar hacia atrás lo de
     abajo se recoloca solo. Comprobar en los dos sentidos dejaría al cliente
     encerrado: con las agujas naranjas puestas desaparecería el botón de la
     esfera blanca.

     EL BISEL VA PRIMERO desde el 28/08/2026, cuando Óscar ordenó el montaje
     por capas: «2- se elige el bisel… 3- se elige la esfera». Antes mandaba
     la esfera. Da igual para el catálogo —las siete ternas son las mismas—
     pero así el orden de las tarjetas, el del carrusel y el de la regla
     dicen todos lo mismo. Con bisel negro quedan cuatro esferas; con azul,
     una; con blanco, dos. */
  /* El paquete de una combinación, o null si el proveedor no la monta. */
  function paqueteDe(s) {
    s = s || e;
    var i, p;
    for (i = 0; i < PAQUETES.length; i++) {
      p = PAQUETES[i];
      if (p.caja === s.caja && p.cristal === s.cristal && p.esf === s.esf &&
          p.bisel === s.bisel && p.agujas === s.agujas) return p;
    }
    if (!AGUJAS_LIBRES) return null;
    for (i = 0; i < PAQUETES.length; i++) {
      p = PAQUETES[i];
      if (p.caja === s.caja && p.cristal === s.cristal && p.esf === s.esf &&
          p.bisel === s.bisel) return p;
    }
    return null;
  }
  /* Un filtro parcial: se le pasa lo que ya está decidido y devuelve las
     ternas que todavía encajan. Con `{}` devuelve las cuatro. */
  function combos(fij) {
    return PAQUETES.filter(function (c) {
      for (var k in fij) if (fij[k] && c[k] !== fij[k]) return false;
      return true;
    });
  }
  function valores(campo, fij) {
    var v = [];
    combos(fij).forEach(function (x) {
      if (v.indexOf(x[campo]) < 0) v.push(x[campo]);
    });
    return v;
  }

  /* ---------- REPARAR LO ELEGIDO ----------
     Igual que el pintado: las dependencias entre pasos son del MODELO
     —qué bisel admite esta esfera, qué caja queda con las dos— y el Lunar
     escribe las suyas en su ficha.

     El que no tenga ninguna se repara solo: si lo elegido en un paso ya no
     está entre sus opciones, se coge la primera. Es lo mínimo para que un
     configurador sin reglas nunca enseñe algo que no existe. */
  function normaliza() {
    if (M.normaliza) return M.normaliza(e, HERRAMIENTAS);
    /* Primero, que lo elegido exista en su paso... */
    PASOS.forEach(function (p) {
      var t = M.OPCIONES && M.OPCIONES[p.id];
      if (!t) return;
      if (!t[e[p.id]]) e[p.id] = Object.keys(t)[0];
      /* ...y que siga valiendo con lo elegido arriba: al pasar de piel a
         acero, el color de la piel ya no existe en el brazalete, y sin esto
         la referencia y el coste se quedan con el color de la correa que
         acabas de dejar. */
      if (M.valeEn && !M.valeEn(p.id, e[p.id], e)) {
        var vale = Object.keys(t).filter(function (k) {
          return M.valeEn(p.id, k, e);
        });
        if (vale.length) e[p.id] = vale[0];
      }
    });
    /* Y si el modelo dice qué combinaciones EXISTEN —no todos los relojes
       admiten todas: la Bitácora monta 36 de las 126 que salen de
       multiplicar—, se repara la cadena hacia abajo, igual que el Lunar.
       Así cambiar la caja nunca deja al cliente delante de algo que no se
       fabrica. */
    if (!PAQUETES.length || !CADENA.length) return;
    var fij = {};
    CADENA.forEach(function (k) {
      var ok = valores(k, fij);
      if (!ok.length) return;
      if (ok.indexOf(e[k]) < 0) e[k] = ok[0];
      fij[k] = e[k];
    });
  }

  /* Los pasos, uno detrás de otro, con lo que diga `OPCIONES`. Sin reglas
     entre ellos: el que las tenga, las escribe. */
  /* ---------- LAS PUERTAS ----------
     Un paso que solo aparece si otro lo abre: el pespunte es de la piel, y
     con un brazalete de acero no hay nada que coser. El modelo las declara
     y trae su propia `abierta`; el que no traiga ninguna tiene todos los
     pasos abiertos, que es como estaba esto hasta hoy.

     Cerrado quiere decir tres cosas a la vez: no se pinta —y `escondeVacios`
     lo esconde por la regla de siempre—, no se cobra, y no entra en la
     referencia. Si faltara la tercera, el mismo reloj tendría dos
     referencias según un pespunte que no lleva. */
  function abierta(id) { return M.abierta ? M.abierta(id, e) : true; }

  /* Y LOS FILTROS: un paso cuyas opciones dependen de lo elegido en otro.
     El color de la correa es del material —con acero no se enseña el azul
     celeste del caucho—. El modelo dice cuál vale; el que no traiga
     ninguno enseña todos, que es como estaba esto hasta hoy. */
  function valeEn(id, v) { return M.valeEn ? M.valeEn(id, v, e) : true; }
  function filtra(id, ops) {
    if (!M.valeEn) return ops;
    return ops.filter(function (o) { return valeEn(id, o[0]); });
  }

  function pintaPasosGenerico() {
    var fij = {};
    PASOS.forEach(function (p) {
      var t = M.OPCIONES && M.OPCIONES[p.id];
      if (!t) return;
      if (!abierta(p.id)) { botones(p.id, [], null); return; }
      var op = t[e[p.id]];
      /* Con lista de combinaciones, cada paso enseña sólo lo que sigue
         teniendo salida con lo ya elegido por encima; sin ella, todo. */
      var ops = filtra(p.id, (PAQUETES.length && CADENA.indexOf(p.id) >= 0)
        ? HERRAMIENTAS.soloDe(t, p.id, fij)
        : deTabla(t));
      if (PAQUETES.length && CADENA.indexOf(p.id) >= 0) fij[p.id] = e[p.id];
      botones(p.id, ops, e[p.id]);
      if (op) rotula(p.id, op.nombre, op.expl || op.tec || '');
    });
  }



  /* ---------- EL PRECIO, DEL COSTE AL PVP ----------
     El multiplicador, el redondeo al 9,90, el 2,5 % de la pasarela y el
     suelo de la REGLA Nº1 viven en `/assets/js/precio-2026.js`, que
     comparten todos los modelos. Estaban COPIADOS aquí y en la otra ficha,
     palabra por palabra: dos relojes vendiendo con dos copias de la regla
     que decide cuánto cobran. */
  var P = window.laoraPrecio;
  var IVA = P.IVA, IRPF = P.IRPF, SS = P.SS, MULT = P.MULT;
  var PACKING_ENVIO = P.PACKING_ENVIO, GARANTIA = P.GARANTIA, COMISION = P.COMISION;
  var KLARNA = P.KLARNA;
  var costeCompleto = P.costeCompleto, redondea = P.redondea,
      sube990 = P.sube990, sueloPvp = P.sueloPvp, pvpBase = P.pvpBase;
  /* EL COSTE, DEL PAQUETE MÁS LO QUE SE LE AÑADE. Devuelve `null` cuando no
     se sabe —una combinación que el proveedor no monta, o una correa sin
     coste—, y entonces la ficha no enseña precio ni deja comprar. */
  /* ---------- EL COSTE DE COMPRA ----------
     De qué se compone el coste de un reloj es del MODELO: el Lunar lo saca
     de los paquetes que monta su proveedor, la Precisa lo suma por piezas
     y cada uno tiene sus reglas —qué correa va dentro del paquete, qué
     cambia con el movimiento—. El motor no se mete: pide el número.

     Y el que no diga nada se suma solo: el coste de cada opción elegida
     más lo que el modelo ponga de fijo —el logo—. Si a alguna le falta el
     coste, no hay coste: se dibuja, pero no se pone precio ni se vende.
     Vale para cualquier modelo que compre por piezas. */
  function costes() {
    if (M.costes) return M.costes(e);
    var total = M.EXTRA || 0;
    for (var i = 0; i < PASOS.length; i++) {
      /* UN PASO CERRADO NO SE COBRA. La hebilla es de la correa de piel;
         con un brazalete de acero el cierre viene con él, y sumar además
         el de la hebilla sería cobrar dos veces una pieza que no lleva. */
      if (!abierta(PASOS[i].id)) continue;
      var t = M.OPCIONES && M.OPCIONES[PASOS[i].id];
      if (!t) continue;
      var o = t[e[PASOS[i].id]];
      if (!o) continue;
      if (o.coste === null || o.coste === undefined) return null;
      total += o.coste;
    }
    return total;
  }
  function precioTarifa() { return pvpBase(costes()); }

  /* ---------- LA COMISIÓN DE LA PASARELA ----------
     Hasta el 22/08/2026 se repercutía subiendo el PVP un 2,5 % —la mitad
     del 5 % de Klarna— por fuera del motor. Ahora entra por donde debe:
     el SUELO se calcula sobre lo que queda de cada euro DESPUÉS de
     pagarla, así que subir además un 2,5 % sería cobrarla dos veces.
     El PVP es el coste completo por el multiplicador y, si con él no se
     llega al suelo, sube de escalón hasta cumplirlo. */
  /* El redondeo al 9,90 puede dejar el precio por debajo del suelo, así
     que el suelo se vuelve a exigir DESPUÉS de redondear: manda él. */
  function netoDeCoste() { return costeCompleto(costes()); }
  /* EL 2,5 % DE KLARNA (Óscar, 19/08/2026, confirmado el 22/08): el PVP
     de tarifa sube un 2,5 % y se vuelve a redondear al 9,90. Después, el
     suelo: si no llega a 50 € limpios o al 15 %, sube de escalón. */
  /* ⚠️ SIN COSTE NO HAY PRECIO, Y DEVUELVE `null`. Antes esto no lo
     comprobaba: `costes()` devolvía `null`, JavaScript lo trataba como cero
     al sumarlo, y salía un precio de 99,90 € para un reloj cuyo coste no se
     sabe. Lo enseñó el volcador el 29/08/2026 con la Precisa recién
     generada —doce referencias a 99,90 que ningún proveedor puede
     cubrir—. Un precio calculado sobre un coste desconocido es peor que no
     tener precio. */
  function precio() {
    var c = costes();
    if (c === null || c === undefined) return null;
    return Math.max(redondea(precioTarifa() * KLARNA), sueloPvp(netoDeCoste()));
  }
  /* EL MOVIMIENTO YA VIENE SEÑALADO (Óscar, 27/08/2026). El Lunar sólo
     tiene el LO_MQ326: pedirle al cliente que pulse el único botón que hay
     es hacerle perder un paso. Se deja marcado de entrada, con su calibre
     escrito debajo, y el primer paso abierto es la esfera. */
  var tocado = { mov: true };
  function sinNadaQueElegir(g) {
    var op = g.querySelector('.pv-opciones');
    return !op || op.hidden || !op.querySelector('button');
  }
  /* SE ACABÓ ABRIR LOS PASOS DE UNO EN UNO (Óscar, 28/08/2026). En Tesla la
     configuración entera se ve desde el primer momento y el cliente va y
     viene; es lo que se ha pedido copiar. La función se queda vacía para no
     tener que perseguir sus llamadas. */
  function abrirPasos() {}

  /* ---------- LA CABECERA DE CADA GRUPO ----------
     Lo elegido a la derecha y su explicación debajo, en letra pequeña. Es el
     patrón de Tesla y es lo que sostiene la tarjeta. */
  function rotula(g, valor, expl) {
    var v = document.querySelector('[data-valor="' + g + '"]');
    var x = document.querySelector('[data-explica="' + g + '"]');
    /* Si el paso todavía no se ha pulsado, la cabecera tampoco puede cantar
       un valor: diría por escrito lo mismo que el botón marcado tenía
       prohibido decir. Se pone en gris con «Sin elegir» y sin explicación,
       que es lo que ya hacen los pasos pendientes. */
    if (!marcado(g)) { valor = 'Sin elegir'; expl = ''; }
    var caja = document.querySelector('[data-g="' + g + '"]');
    if (caja && ESPERA_PULSACION[g])
      caja.classList.toggle('pv-g-vacio', !marcado(g));
    if (v) v.textContent = valor;
    if (x) x.textContent = expl || '';
  }

  /* ---------- LA ENTREGA ----------
     Treinta días desde HOY, recalculado en cada carga: una fecha escrita a
     mano envejece sola y acaba prometiendo una entrega que ya pasó. */
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function entrega() {
    var el = $('[data-pv-entrega]');
    if (!el) return;
    var d = new Date();
    d.setDate(d.getDate() + 30);
    el.textContent = 'Entrega estimada: ' + d.getDate() + ' de ' +
                     MESES[d.getMonth()] + ' de ' + d.getFullYear();
  }

  /* ---------- LA FORMA DE COMPRA ----------
     ⚠️ DE MOMENTO SÓLO EXPLICA, NO COBRA. El botón sigue metiendo el reloj
     entero en el carrito: partir el cobro en una señal y un resto es cosa de
     la pasarela, no de esta ficha. Lo que sí hace ya es decir la verdad de
     cuánto se pide al reservar. */
  /* ---------- LA SEÑAL DE LA RESERVA ----------
     EL 40 % DEL PRECIO, SIEMPRE (Óscar, 28/08/2026: «para que no varíe tanto,
     se va a pedir el 40 % del importe siempre como fijo, es decir el valor
     más alto de los calculados»).

     Antes salía del coste de compra redondeado al 9,90 de arriba y bailaba
     entre el 36 % y el 40 % según la configuración. Un porcentaje fijo se
     explica en una línea, se entiende sin mirar la tabla, y —lo que importa—
     **sigue sin publicar lo que nos cuesta el reloj**, que es lo que hacía la
     primera versión. Cubre el coste en las seis configuraciones: la más
     ajustada, la de oro rosa con caucho, cuesta 81,01 y adelanta 91,96.

     No se redondea al 9,90: entonces ya no sería el 40 % y habría que volver
     a decir un porcentaje distinto en cada reloj. */
  var SENAL = 0.40;
  /* LA CUENTA, PARA CUANDO LA HAGA LA PASARELA. La ficha ya no enseña los
     importes —sólo el porcentaje—, pero la regla tiene que vivir en un solo
     sitio: el día que el carrito cobre la señal de verdad, saca de aquí lo
     que cobra ahora y lo que queda. */
  function senal() {
    if (costes() === null) return null;
    var total = precio(), ahora = Math.round(total * SENAL * 100) / 100;
    return { ahora: ahora, luego: Math.round((total - ahora) * 100) / 100,
             pct: Math.round(SENAL * 100) };
  }

  /* La cuota de los tres plazos, redondeada HACIA ARRIBA al céntimo: tres
     cuotas tienen que sumar el precio o más, nunca menos. */
  function cuota() { return Math.ceil(precio() / 3 * 100) / 100; }
  function modoEnTresPagos() {
    var sel = $('[data-pv-modo]');
    return !!sel && (sel.value === 'P-3' || sel.value === 'E-3');
  }

  function modoDeCompra() {
    var sel = $('[data-pv-modo]'), nota = $('[data-pv-modo-nota]');
    if (!sel || !nota) return;
    var v = sel.value;
    if (v === 'P-RES' || v === 'E-RES') {
      nota.hidden = false;
      /* SIN IMPORTES AQUÍ (Óscar, 28/08/2026): «no mostramos el importe, solo
         al final de la compra». El porcentaje sale de `SENAL`, que es donde
         vive la regla, para que no haya un 40 escrito a mano que se quede
         viejo el día que cambie. */
      nota.innerHTML = 'Para la reserva solo tendrás que abonar el <b>' +
        Math.round(SENAL * 100) + '&nbsp;%</b> del total hoy.<br>' +
        'El resto una semana antes de la entrega, te avisamos nosotros.';
    } else if (v === 'P-3' || v === 'E-3') {
      nota.hidden = false;
      nota.innerHTML = 'Tres plazos sin intereses (0&nbsp;% TAE) con Klarna. El ' +
                       'primero al comprar y los otros dos, cada treinta días.';
    } else if (v === 'E-DIR') {
      nota.hidden = false;
      nota.textContent = 'Se factura con tus datos fiscales. El IVA va desglosado ' +
                         'en la factura.';
    } else {
      nota.hidden = true;
    }
  }

  function pinta() {
    normaliza();

    /* EL PRECIO, SÓLO SI HAY COSTES. Sin ellos no se enseña un número ni se
       deja comprar: una cifra inventada en una tienda es peor que ninguna. */
    var hayPrecio = COSTES_PUESTOS && costes() !== null;
    var pie = $('[data-pv-pie]');
    /* EN «3 PAGOS» EL PRECIO GRANDE ES LA CUOTA (Óscar, 28/08/2026: «no
       pone 239,90, pone 79,97 € y más pequeño ×3 pagos»). Es lo que el
       cliente va a pagar hoy, así que es el número que manda; el total
       sigue estando en la ficha técnica y en el carrito.
       ⚠️ LO QUE SE METE EN EL CARRITO NO CAMBIA: allí va `precio()`, el
       total. Partir el cobro es cosa de la pasarela, no de la ficha. */
    var tres = modoEnTresPagos();
    todos('[data-pv-precio]').forEach(function (n) {
      if (!hayPrecio) { n.textContent = 'Precio por definir'; return; }
      n.innerHTML = tres
        ? eu(cuota()) + ' <span class="pv-precio-x">×&nbsp;3 pagos</span>'
        : eu(precio());
    });
    /* SIN PRECIO NO HAY PLAZOS NI «DISPONIBLE». La caja de Klarna venía con
       un número de ejemplo dentro y el punto verde diciendo que está a la
       venta: las dos cosas serían mentira hasta que haya costes. */
    todos('.pv-klarna, .pv-barra-klarna').forEach(function (n) { n.hidden = !hayPrecio; });
    if (hayPrecio) {
      var c = eu(cuota());
      todos('[data-pv-klarna]').forEach(function (n) { n.textContent = c; });
    }
    var stock = document.querySelector('.pv-stock');
    if (stock) stock.hidden = !hayPrecio;
    if (pie) pie.classList.toggle('pv-sin-precio', !hayPrecio);
    todos('[data-pv-comprar]').forEach(function (b) {
      b.disabled = !hayPrecio;
      b.textContent = hayPrecio ? 'Añadir al carrito' : 'Todavía no está a la venta';
    });

    /* ---------- QUÉ TABLA LLENA CADA PASO ----------
       Esto ya no lo decide el motor: lo decide el MODELO, porque es donde
       viven las dependencias entre pasos —qué esferas admite este bisel,
       qué cajas quedan con esa esfera, qué correa trae el paquete—. El
       Lunar tiene las suyas y las escribe en su ficha.

       Y EL QUE NO TENGA NINGUNA se pinta solo: paso por paso, del contrato,
       con la tabla que el modelo haya puesto en `OPCIONES`. Es lo que
       permite que los diez modelos tengan configurador desde el primer día
       —con sus pasos, su estado y su referencia— aunque todavía no tengan
       ni una foto ni un coste (Óscar, 29/08/2026: «quiero todos ya aunque
       no estén las imágenes»). */
    if (M.pintaPasos) M.pintaPasos(e, HERRAMIENTAS);
    else pintaPasosGenerico();

    entrega();
    modoDeCompra();
    pintaCapas();
    repasaBarra();
    repasaVisor();

    /* LA FOTO: la de la serie si esta combinación ya está hecha, y si no, el
       cartel. Nunca una imagen que no sea la elegida. */
    /* EL VISOR SOLO TIENE DOS ESTADOS: la foto de presentación mientras
       nadie ha elegido nada, y el reloj armado con sus piezas en cuanto se
       elige la primera. Ni foto de combinación ni cartel de «en
       preparación»: eso era del mundo de una foto por reloj. */
    pintaPresentacion();
    var lupa = $('[data-pv-ampliar]');
    if (lupa) lupa.hidden = true;

    /* LA FICHA TÉCNICA LA ESCRIBE EL MODELO. Estaba aquí con las tablas del
       Lunar —caja, cristal, movimiento, esfera, bisel, agujas—, y en un
       modelo que aún no tenga esas tablas reventaba al leer `.mat`. Cada
       ficha sabe decir su reloj; el motor solo reparte lo que le den. */
    var tec = M.tecnica ? M.tecnica(e) : {};
    ['caja', 'mov', 'esf', 'agua'].forEach(function (k) {
      var n = $('[data-pv-tec="' + k + '"]');
      if (n) n.textContent = tec[k] || '';
    });

    escondeVacios();
    abrirPasos();
    if (CURAR) panelCurar();

    /* Y TODO SEÑALADO DESDE EL PRINCIPIO: en Tesla el coche entra
       configurado y el resumen de arriba dice lo que llevas puesto. Esconder
       la elección de partida dejaría la tarjeta diciendo un nombre que
       ningún botón confirma. */
  }

  /* ============================================================
     LA PANTALLA DE CRIBA  ·  botón en `?capas`
     ------------------------------------------------------------
     Óscar, 28/08/2026: «monta la pantalla curar sobre lunar?capas para que
     yo te diga cuáles combinaciones no pueden ser».

     QUÉ SE CRIBA. Sólo lo que se dejó libre y nadie ha revisado:

       · ESFERA × AGUJAS, treinta parejas. Las agujas se liberaron el 28/08
         y salen las cinco con cualquier esfera.
       · CAJA DE PVD × ESFERA, seis. La hoja de compra dice que con el PVD
         la esfera está «por decidir», así que están las seis puestas.

     Lo demás no se criba porque no es libre: el bisel de cada esfera lo
     manda la tabla de paquetes, y las correas van con todo.

     LO MARCADO NO SE BORRA, SE APAGA. Las parejas cribadas salen en el
     configurador dibujadas pero sin poder pulsarse, igual que el PVD antes
     de tener precio: así se ve el efecto sin perder de vista lo que se
     quitó. Y vive en este navegador —localStorage—; para que desaparezca
     para todo el mundo hay que pasarme la lista y escribirla en la ficha.
     ============================================================ */
  var CRIBA = {};
  try {
    if (window.localStorage)
      CRIBA = JSON.parse(window.localStorage.getItem(LLAVE + 'criba') || '{}') || {};
  } catch (x) { CRIBA = {}; }
  function guardaCriba() {
    try {
      if (window.localStorage)
        window.localStorage.setItem(LLAVE + 'criba', JSON.stringify(CRIBA));
    } catch (x) {}
  }
  function clave(tipo, a, b) { return tipo + ':' + a + '|' + b; }
  function cribado(tipo, a, b) { return !!CRIBA[clave(tipo, a, b)]; }

  var CRIBA_ABIERTA = false;
  function dibujaCriba() {
    var caja = $('[data-pv-criba]');
    if (!caja) return;
    caja.hidden = !CRIBA_ABIERTA;
    if (!CRIBA_ABIERTA) return;

    function celda(tipo, a, b, capas, rotulo) {
      return '<button type="button" class="pv-criba-celda" data-criba="' +
             clave(tipo, a, b) + '" aria-pressed="' + cribado(tipo, a, b) + '">' +
             '<span class="pv-criba-foto">' +
               capas.map(function (u) {
                 return u ? '<img src="' + u + '" alt="" loading="lazy">' : '';
               }).join('') +
             '</span><span>' + rotulo + '</span></button>';
    }

    var esferas = Object.keys(ESFERAS), agujas = Object.keys(AGUJAS);
    var html =
      '<button type="button" class="pv-criba-cierra" data-criba-cierra>Cerrar</button>' +
      '<h2>Criba del ' + M.nombre + '</h2>' +
      '<p>Marca lo que <b>no puede ser</b>. Lo marcado se queda a la vista, ' +
      'apagado en el configurador, y sigue aquí hasta que lo desmarques. ' +
      'Cuando termines, cópiame la lista de abajo.</p>';

    html += '<h3>Esfera y agujas · ' + (esferas.length * agujas.length) + ' parejas</h3>' +
            '<p>Las agujas salen libres con cualquier esfera desde que lo pediste. ' +
            'Cada miniatura va con el bisel que el proveedor le monta a esa esfera.</p>' +
            '<div class="pv-criba-rejilla" style="grid-template-columns:repeat(' +
            agujas.length + ',minmax(96px,1fr))">';
    esferas.forEach(function (ek) {
      var bi = biselDe(ek);
      agujas.forEach(function (ak) {
        html += celda('EA', ek, ak, [
          urlCapa('caja', 'PL'), urlCapa('bisel', bi),
          urlCapa('esf', ek), urlCapa('agujas', ak, ek)
        ], ESFERAS[ek].nombre + ' · ' + AGUJAS[ak].nombre);
      });
    });
    html += '</div>';

    html += '<h3>Caja de PVD y esfera · ' + esferas.length + '</h3>' +
            '<p>La hoja de compra deja la esfera del PVD «por decidir», así que ' +
            'están las seis puestas.</p>' +
            '<div class="pv-criba-rejilla" style="grid-template-columns:repeat(' +
            esferas.length + ',minmax(96px,1fr))">';
    esferas.forEach(function (ek) {
      html += celda('CE', 'NG', ek, [
        urlCapa('caja', 'NG'), urlCapa('bisel', 'NEG'),
        urlCapa('esf', ek), urlCapa('agujas', 'BLA', ek)
      ], 'PVD · ' + ESFERAS[ek].nombre);
    });
    html += '</div>';

    var lista = listaCriba();
    html += '<h3>Para pasármelo</h3>' +
            '<textarea class="pv-criba-texto" readonly rows="6" ' +
            'onclick="this.select()">' + (lista || 'Nada marcado todavía.') + '</textarea>';
    caja.innerHTML = html;

    var pie = $('[data-pv-criba-pie]');
    if (pie) {
      pie.hidden = false;
      pie.innerHTML =
        '<b>' + Object.keys(CRIBA).length + ' marcadas</b>' +
        '<button type="button" data-criba-copia>Copiar la lista</button>' +
        '<button type="button" data-criba-vacia>Desmarcar todas</button>' +
        '<button type="button" data-criba-cierra>Cerrar</button>' +
        '<span class="pv-curar-ok" data-criba-ok hidden>copiado</span>';
    }
  }
  function listaCriba() {
    return Object.keys(CRIBA).sort().map(function (k) {
      var t = k.slice(0, 2), p = k.slice(3).split('|');
      if (t === 'EA') return 'esfera ' + ESFERAS[p[0]].nombre + ' + agujas ' +
                             AGUJAS[p[1]].nombre + '   (' + k + ')';
      return 'caja PVD + esfera ' + ESFERAS[p[1]].nombre + '   (' + k + ')';
    }).join('\n');
  }

  /* ---------- EL PANEL DE CURAR ---------- */
  function paraMi() {
    return Object.keys(COMBIS).map(function (k) {
      return canon(k) + '   · ' + COMBIS[k].dicho;
    }).join('\n');
  }
  function panelCurar() {
    if (!CURAR) return;
    var p = document.getElementById('pv-curar');
    if (!p) {
      p = document.createElement('div');
      p.id = 'pv-curar'; p.className = 'pv-curar';
      document.body.appendChild(p);
    }
    var combis = Object.keys(COMBIS);
    var yaEsta = marcada(firma());
    p.innerHTML =
      '<b>Esta combinación</b>' +
      '<p class="pv-curar-dicho">' + dichoCompleto() + '</p>' +
      '<p><code>' + referencia() + '</code></p>' +
      '<button type="button" data-curar-combi>' +
        (yaEsta ? '☑  Marcada para quitar' : '☐  Quitar esta combinación') +
      '</button>' +
      '<hr>' +
      '<b>Combinaciones marcadas (' + combis.length + ')</b>' +
      (combis.length
        ? '<ul>' + combis.map(function (k) {
            return '<li><span>' + COMBIS[k].dicho + '</span>' +
                   '<button type="button" data-descombi="' + k + '">quitar de la lista</button></li>';
          }).join('') + '</ul>' +
          '<button type="button" data-curar-aplica>' +
            (APLICADAS ? 'Volver a ponerlas todas' : 'Quitarlas ya (' + combis.length + ')') +
          '</button>' +
          '<p class="pv-curar-dicho">' +
            (APLICADAS
              ? 'Quitadas <b>en este navegador</b>. Para que desaparezcan para todo el mundo, cópiame la lista y las escribo en la ficha.'
              : 'Marcadas, pero todavía en pie. Púlsalo y desaparecen del configurador para que veas cómo queda.') +
          '</p>' +
          '<b>Para pasármelo</b>' +
          '<textarea class="pv-curar-texto" readonly rows="4" onclick="this.select()">' + paraMi() + '</textarea>'
        : '<p>Ninguna. Combina, y cuando algo no te guste márcalo aquí: sigue todo en pie hasta que lo confirmes.</p>') +
      '<hr>' +
      '<button type="button" data-curar-copia>Copiar la lista</button> ' +
      '<button type="button" data-curar-vacia>Vaciar</button>' +
      '<span class="pv-curar-ok" data-curar-ok hidden>copiado</span>';
  }
  function escapaDeMarcada() {
    if (!vetada(firma()) && !(APLICADAS && marcada(firma()))) return;
    var grupos = ['correa', 'cristal', 'agujas', 'bisel', 'esf', 'caja', 'mov'];
    for (var i = 0; i < grupos.length; i++) {
      var caja = $('[data-pv="' + grupos[i] + '"]');
      if (!caja) continue;
      var bs = caja.querySelectorAll('button');
      for (var j = 0; j < bs.length; j++) {
        if (bs[j].dataset.v === e[grupos[i]]) continue;
        if (!llevaAMarcada(grupos[i], bs[j].dataset.v)) { bs[j].click(); return; }
      }
    }
  }

  /* ---------- LA BARRA SE APAGA CUANDO SALE EL PIE ----------
     Óscar, 28/08/2026: la barra «permanece visible sólo hasta que el scroll
     llega a la tarjeta donde ya se ve la otra tarjeta de precio con el
     botón añadir al carrito».

     LA REGLA, EN UNA LÍNEA: el pie asoma por abajo. `ASOMO` son los píxeles
     que tiene que haber entrado para que cuente, y evitan que la barra
     parpadee cuando el pie roza el filo de la pantalla.

     SE MIRA A MANO Y NO CON UN IntersectionObserver, que era la primera
     versión: el observador es más fino, pero no hay forma de comprobarlo
     desde aquí —en el panel del navegador no llega a dispararse ni una
     vez—, y una regla que no se puede probar no se publica. Ésta se mide
     con `getBoundingClientRect`, que sí responde, y se puede recorrer
     entera sobre la página de verdad.

     SE VUELVE A MIRAR EN TRES SITIOS, no sólo al desplazarse: al elegir
     —cambiar de correa hace crecer la columna y el pie se mueve sin que
     nadie toque el scroll—, al cambiar el tamaño de la ventana y al
     arrancar. */
  /* CUÁNDO SE CONSIDERA QUE «EL SCROLL HA LLEGADO» AL PIE: cuando su borde
     de arriba ha subido por encima del 60 % de la pantalla, o sea cuando el
     precio y el botón del pie se ven de verdad, no cuando el pie asoma por
     el filo.

     ANTES BASTABA CON QUE ASOMARA 24 px, y eso rompía las pantallas altas:
     en un monitor de más de 1.800 px el pie ya entra en cuadro sin
     desplazar nada, así que la barra nacía apagada y no se veía nunca. */
  var LLEGADA = 0.60;

  /* ---------- LA CÁMARA SE ALEJA EN LA CORREA ----------
     Manda la TARJETA entera, no el paso: los dos pasos de la correa —el
     material y el color— viven en ella, y el color se esconde con el
     brazalete puesto, así que mirar la tarjeta es lo único que vale para
     los dos casos. Se considera que se ha llegado cuando ocupa la franja
     de en medio de la pantalla. */
  function repasaVisor() {
    var t = document.querySelector('[data-pv-tarjeta="correa"]');
    if (!t) return;
    var r = t.getBoundingClientRect();
    var enJuego = r.top < window.innerHeight * 0.60 &&
                  r.bottom > window.innerHeight * 0.15;
    var capas = $('[data-pv-capas]');
    if (capas) capas.classList.toggle('pv-capas-lejos', enJuego && CAPAS);
    pintaMinis(enJuego);
  }

  /* LAS MINIATURAS DE LA CORREA. Se rehacen sólo cuando cambia la lista:
     tocar el `src` de una imagen que ya está puesta la deja en blanco
     mientras vuelve a bajar, y aquí eso sería un parpadeo por cada
     pulsación en el paso del color. */
  var MINIS_PUESTAS = '';
  function pintaMinis(enJuego) {
    var caja = $('[data-pv-pila-correa]');
    if (!caja) return;
    var lista = MINI[e.correa] || [];
    caja.hidden = !lista.length;
    var firma = lista.join('|');
    if (firma !== MINIS_PUESTAS) {
      MINIS_PUESTAS = firma;
      caja.innerHTML = '';
      lista.forEach(function (f) {
        var im = new Image();
        im.className = 'pv-mini-correa';
        im.src = MINI_IMG + f + '.avif' + SERIE_V;
        im.alt = (MINI_ALT[f] ||
                  'Correa ' + CORREAS[e.correa].nombre.toLowerCase()) +
                 ', foto del fabricante';
        caja.appendChild(im);
      });
    }
    caja.classList.toggle('pv-pila-dentro', enJuego && !!lista.length);
    apartaDeLoQueEstorbe(caja);
  }

  /* ⚠️ ESA ESQUINA ESTÁ OCUPADA POR DOS COSAS.

     LA BARRA DE PRECIO, en escritorio: el marco es más alto que la
     pantalla, así que su parte de abajo cae por debajo del filo y ahí es
     donde la barra se queda pegada. La miniatura de abajo —la del color
     elegido, la que más importa— desaparecía detrás del precio. Ya pasaba
     con la miniatura suelta y no se vio porque una sola cabía por encima;
     con tres se vio a la primera.

     EL CARRUSEL, en el móvil: los botones ‹ › y el nombre del paso viven
     abajo en medio del marco, y la fila de miniaturas les pasaba por
     encima. No estorban a la pulsación —la pila lleva `pointer-events:
     none`—, pero tapar un botón ya es motivo.

     Ninguna de las dos se arregla con un número fijo: la barra mide
     distinto según la pantalla y se apaga al llegar al pie, y el carrusel
     va y viene. Se miden las dos y se aparta de la que más suba. */
  function apartaDeLoQueEstorbe(caja) {
    var hero = caja.closest('.pv-hero');
    if (!hero) return;
    var suelo = hero.getBoundingClientRect().bottom, hueco = 16;

    function esquiva(el, margen) {
      if (!el || el.hidden) return;
      var r = el.getBoundingClientRect();
      if (!r.height) return;
      var solape = suelo - r.top;
      if (solape > 0) hueco = Math.max(hueco, Math.round(solape) + margen);
    }
    var barra = $('[data-pv-barra]');
    if (barra && !barra.classList.contains('pv-barra-fuera')) esquiva(barra, 12);
    esquiva($('[data-pv-carrusel]'), 10);

    caja.style.bottom = hueco + 'px';
  }

  /* NO SE DECIDE NADA HASTA QUE LA PÁGINA ESTÁ CUADRADA. Mientras las fotos
     no han cargado, la columna mide bastante menos y el pie cae dentro de la
     pantalla: la barra se apagaba, la página terminaba de cuadrar y volvía a
     encenderse. Un parpadeo en cada carga, que se ve —así salió en la
     primera foto de producción, con la tarjeta transparentándose a través
     de la barra a medio desvanecer—. */
  var PAGINA_LISTA = document.readyState === 'complete';
  window.addEventListener('load', function () {
    PAGINA_LISTA = true;
    repasaBarra();
    repasaVisor();
  });
  function repasaBarra() {
    var barra = $('[data-pv-barra]'), pie = $('[data-pv-pie]');
    if (!barra || !pie || !PAGINA_LISTA) return;
    var r = pie.getBoundingClientRect();
    /* Sólo el borde de arriba: «permanece visible SÓLO HASTA QUE el scroll
       llega» a la tarjeta del pie. Una vez llegado, se queda apagada el
       resto de la página en vez de reaparecer por debajo del pie encima de
       la ficha técnica y del pie de página. */
    barra.classList.toggle('pv-barra-fuera',
      r.top < window.innerHeight * LLEGADA);
  }

  /* ---------- LOS CLICS ---------- */
  /* La barra y el carrusel se repasan al desplazarse, una vez por
     fotograma: mirar el `getBoundingClientRect` de seis cajas en cada píxel
     de scroll es tirar trabajo, y con `requestAnimationFrame` basta. */
  (function () {
    var pedido = false;
    function apunta() {
      if (pedido) return;
      pedido = true;
      requestAnimationFrame(function () {
        pedido = false;
        repasaBarra();
        repasaVisor();
        if (!CAPAS) return;
        var c = $('[data-pv-carrusel]');
        if (!c || c.hidden) return;
        var g = pasoEnJuego();
        if (g) c.querySelector('[data-carrusel-paso]').textContent = ROTULO[g];
      });
    }
    window.addEventListener('scroll', apunta, { passive: true });
    window.addEventListener('resize', apunta);
  })();

  document.addEventListener('click', function (ev) {
    var fl = ev.target.closest('[data-carrusel]');
    if (fl) { gira(Number(fl.dataset.carrusel)); }

    if (ev.target.closest('[data-pv-criba-abre]')) {
      CRIBA_ABIERTA = true; dibujaCriba(); return;
    }
    if (ev.target.closest('[data-criba-cierra]')) {
      CRIBA_ABIERTA = false; dibujaCriba();
      var pie = $('[data-pv-criba-pie]'); if (pie) pie.hidden = true;
      pinta(); return;
    }
    var c = ev.target.closest('[data-criba]');
    if (c) {
      var k = c.dataset.criba;
      if (CRIBA[k]) delete CRIBA[k]; else CRIBA[k] = 1;
      guardaCriba(); dibujaCriba(); return;
    }
    if (ev.target.closest('[data-criba-vacia]')) {
      CRIBA = {}; guardaCriba(); dibujaCriba(); return;
    }
    if (ev.target.closest('[data-criba-copia]')) {
      var ta = $('.pv-criba-texto'), ok = $('[data-criba-ok]'), hecho = false;
      if (ta) { ta.select(); try { hecho = document.execCommand('copy'); } catch (err) {} }
      if (!hecho) { try { navigator.clipboard.writeText(listaCriba()); hecho = true; } catch (err) {} }
      if (ok) { ok.textContent = hecho ? 'copiado' : 'no he podido: selecciónalo tú'; ok.hidden = false; }
      return;
    }
  });
  document.addEventListener('change', function (ev) {
    /* `pinta()` y no sólo `modoDeCompra()`: desde que el precio grande
       cambia con la forma de pago, cambiar el desplegable tiene que repintar
       el precio de la tarjeta y el de la barra. */
    if (ev.target.closest('[data-pv-modo]')) pinta();
  });
  document.addEventListener('click', function (ev) {
    if (ev.target.closest('[data-curar-combi]')) {
      var f = firma();
      if (marcada(f)) desmarca(f);
      else COMBIS[f] = { ref: referencia(), dicho: dichoCompleto() };
      guardaCombis(); pinta(); escapaDeMarcada(); panelCurar();
      return;
    }
    var dc = ev.target.closest('[data-descombi]');
    if (dc) { delete COMBIS[dc.dataset.descombi]; guardaCombis(); pinta(); panelCurar(); return; }
    if (ev.target.closest('[data-curar-aplica]')) {
      APLICADAS = !APLICADAS; guardaAplicadas();
      pinta(); escapaDeMarcada(); panelCurar();
      return;
    }
    if (ev.target.closest('[data-curar-vacia]')) {
      COMBIS = {}; APLICADAS = false; guardaCombis(); guardaAplicadas();
      pinta(); panelCurar();
      return;
    }
    if (ev.target.closest('[data-curar-copia]')) {
      var ok = $('[data-curar-ok]');
      var caja = document.querySelector('.pv-curar-texto');
      var hecho = false;
      if (caja) { caja.select(); try { hecho = document.execCommand('copy'); } catch (err) {} }
      if (!hecho) { try { navigator.clipboard.writeText(paraMi()); hecho = true; } catch (err) {} }
      if (ok) { ok.textContent = hecho ? 'copiado' : 'no he podido: selecciónalo tú'; ok.hidden = false; }
      return;
    }

    var b = ev.target.closest('[data-pv] button');
    if (b && b.disabled) return;
    if (b) {
      var g = b.closest('[data-pv]').dataset.pv;
      aplicaOpcion(g, b.dataset.v);
      tocado[g] = true;
      /* Elegir el material ya deja puesta una correa concreta —salta a la
         primera de ese material—, así que cuenta como haber elegido correa:
         si no, la capa no se dibujaría hasta tocar además el color, y con
         brazalete no hay color que tocar. */
      if (g === 'correamat') tocado.correa = true;
      ULTIMO = g;
      pinta();
      return;
    }

    if (ev.target.closest('[data-pv-comprar]')) {
      if (!COSTES_PUESTOS) return;
      if (typeof laoraCarritoAnadir !== 'function') return;
      laoraCarritoAnadir({
        ref: referencia(),
        nombre: M.nombre,
        /* EL DETALLE LO ESCRIBE EL MODELO. Aquí estaba escrito a mano con
           las tablas del Lunar —caja, esfera, bisel, cierre, movimiento—,
           y en un modelo que no tenga bisel eso revienta. Cada ficha sabe
           cómo se dice su reloj; el motor solo pregunta.

           EL CIERRE VA EN EL DETALLE aunque todavía no esté en la
           referencia: si no, el pedido no diría cuál lleva. */
        detalle: M.detalle ? M.detalle(e) : dichoCompleto(),
        correa: (CORREAS && CORREAS[e.correa] && CORREAS[e.correa].nombre) || '',
        precio: precio(),
        /* ⚠️ LA LÍNEA DEL CARRITO VA SIN FOTO, y es a propósito. Ya no
           existe una foto del reloj entero: el reloj se arma con sus piezas.
           Lo que se manda son LAS PIEZAS, en orden de montaje, para que el
           carrito pueda apilarlas igual que la ficha el día que se toque.
           Hasta entonces la línea sale con su texto, que dice exactamente
           lo mismo. */
        foto: '',
        capas: (PILA || []).map(function (p) { return urlCapa(p.grupo, e[p.grupo]); })
                   .filter(Boolean)
      });
      window.location.href = '/carrito.html';
    }
  });

  montaPasos();
  pinta();
  panelCurar();
  /* ---------- LA PUERTA DE SERVICIO ----------
     `herramientas/volcar_catalogo_2026.js` ejecuta este motor FUERA del
     navegador para calcular las tres mil referencias del catálogo, y
     necesita alcanzar sus tripas. Antes se las apañaba inyectándole un
     exportador y confiando en el hoisting; adivinar dónde empieza el
     ámbito de un fichero ajeno es frágil por definición, así que ahora el
     motor dice él lo que expone, con nombre y apellidos y a la vista en
     el diff.

     No es una API pública: es una puerta de servicio para la casa. */
  /* `__LAORA_ULTIMO` guarda lo mismo bajo otro nombre para el volcador,
     que lo lee después de ejecutar la ficha. */
  window.__LAORA_MOTOR = window.__LAORA_ULTIMO = {
    e: e, precio: precio, costes: costes, referencia: referencia,
    normaliza: normaliza, pinta: pinta, agua: agua, firma: firma,
    vetada: vetada, sinVeto: sinVeto,
    /* El contrato de pasos y las opciones del modelo: con los dos, el
       volcador puede recorrer todas las combinaciones sin tener una copia
       de las listas, que es lo que se quedaba viejo. */
    PASOS: PASOS, OPCIONES: M.OPCIONES || null, M: M,
    MOVS: MOVS, CAJAS: CAJAS, ESFERAS: ESFERAS, BISELES: BISELES,
    AGUJAS: AGUJAS, CORREAS: CORREAS, CRISTALES: CRISTALES,
    PAQUETES: PAQUETES, COSTES_PUESTOS: COSTES_PUESTOS, MM: MM,
    AGUJAS_LIBRES: AGUJAS_LIBRES
  };

})();
