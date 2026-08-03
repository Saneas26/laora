/* ============================================================
   laOra · CATÁLOGO — única fuente de verdad de los modelos
   ------------------------------------------------------------
   Aquí viven los ocho relojes. La home, el listado de colección y
   las fichas leen de este fichero: no hay ningún modelo ni ningún
   precio escrito a mano en un HTML.

   PRECIOS
   `precio: null` significa «todavía no tenemos el precio cerrado».
   Donde hay null NO se pinta ninguna cifra: se enseña el modelo sin
   precio. Nunca se inventa ni se calcula por fórmula.

   El material de Codex del 03/08/2026 proponía precios por
   aritmética (base, base+70, base+140, base+210, iguales para los
   ocho modelos). Se descartó entero: los precios salen de la hoja
   de materiales de Óscar y de ningún otro sitio.
   Ver PRECIOS-ANTERIORES.md para las cifras que estuvieron
   publicadas hasta el 03/08/2026.

   MOVIMIENTOS Y ESPECIFICACIONES
   Misma regla: lo que no esté confirmado NO se escribe. El material
   traía «referencia por confirmar» y «[HERMETICIDAD POR CONFIRMAR]»
   como texto visible; aquí eso es sencillamente `null` y la ficha
   no enseña esa línea.
   ============================================================ */

window.LAORA_CATALOGO = [
  {
    slug: 'lunar',
    codigo: 'LO—01',
    nombre: 'Lunar',
    familia: 'Cronógrafo',
    homenaje: 'Homenaje al gran cronógrafo lunar',
    frase: 'El cronógrafo que mira más allá.',
    descripcion: 'Una lectura contemporánea del cronógrafo más reconocible de la exploración espacial, firmada únicamente por laOra.',
    historia: 'Lunar conserva la claridad instrumental, la escala taquimétrica y el equilibrio de tres contadores que hicieron universal este arquetipo. No pretende pasar por el original: es nuestro homenaje, con identidad laOra y una construcción pensada para usarse cada día.',
    precio: null,
    diametro: '42 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/lunar-front.webp',
    galeria: ['/assets/img/relojes-2026/lunar-front.webp',
              '/assets/img/relojes-2026/lunar-detail.webp',
              '/assets/img/relojes-2026/lunar-hero.webp'],
    fichaTecnica: [['Caja', 'Acero con acabado negro'],
                   ['Bisel', 'Escala taquimétrica'],
                   ['Brazalete', 'Acero con acabado negro'],
                   ['Control', 'Revisión individual en Madrid']]
  },
  {
    slug: 'bitacora',
    codigo: 'LO—02',
    nombre: 'Bitácora',
    familia: 'Deportivo integrado',
    homenaje: 'Homenaje a la arquitectura deportiva integrada',
    frase: 'Equilibrio, precisión y uso diario.',
    descripcion: 'Geometría de acero, perfil contenido y una esfera que cambia con la luz.',
    historia: 'Bitácora toma como punto de partida el reloj deportivo integrado de los setenta y lo traduce a una propuesta directa, legible y con marca propia.',
    precio: null,
    diametro: '40 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/bitacora.webp',
    galeria: ['/assets/img/relojes-2026/bitacora.webp',
              '/assets/img/relojes-2026/bitacora-hero-dial.webp',
              '/assets/img/relojes-2026/bitacora-hero-movement.webp'],
    fichaTecnica: [['Caja', 'Acero 316L'],
                   ['Arquitectura', 'Brazalete integrado'],
                   ['Esfera', 'Texturizada'],
                   ['Control', 'Revisión individual en Madrid']]
  },
  {
    slug: 'trinchera',
    codigo: 'LO—03',
    nombre: 'Trinchera',
    familia: 'Reloj de campo',
    homenaje: 'Homenaje al reloj de campaña clásico',
    frase: 'Legible por instinto.',
    descripcion: 'Un reloj de campaña honesto: números limpios, contraste absoluto y acero sin artificios.',
    historia: 'Trinchera rinde homenaje al reloj que nació como herramienta. Conserva su lectura inmediata y su austeridad funcional, sin insignias militares ni logotipos ajenos.',
    precio: null,
    diametro: '39 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/trinchera-hero.webp',
    galeria: ['/assets/img/relojes-2026/trinchera-hero.webp',
              '/assets/img/relojes-2026/trinchera-profile.webp',
              '/assets/img/relojes-2026/trinchera-eclipse.webp'],
    fichaTecnica: [['Caja', 'Acero 316L cepillado'],
                   ['Esfera', 'Negro mate de alta lectura'],
                   ['Correa', 'Tejido verde oliva'],
                   ['Trasera', 'Acero macizo']]
  },
  {
    slug: 'precisa',
    codigo: 'LO—04',
    nombre: 'Precisa',
    familia: 'Deportivo integrado',
    homenaje: 'Homenaje al deportivo integrado de los setenta',
    frase: 'La forma exacta del tiempo.',
    descripcion: 'Acero, geometría y azul profundo en una silueta reconocible al instante.',
    historia: 'Precisa parte de uno de los códigos más influyentes de la relojería deportiva: caja y brazalete como una sola línea. Lo presentamos abiertamente como homenaje y lo firmamos solo con laOra.',
    precio: null,
    diametro: '40 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/precisa-front.webp',
    galeria: ['/assets/img/relojes-2026/precisa-front.webp',
              '/assets/img/relojes-2026/precisa-hero.webp',
              '/assets/img/relojes-2026/precisa-bracelet.webp'],
    fichaTecnica: [['Caja', 'Acero 316L cepillado y pulido'],
                   ['Esfera', 'Azul con textura cuadriculada'],
                   ['Brazalete', 'Acero integrado'],
                   ['Calendario', 'Fecha a las 3']]
  },
  {
    slug: 'bauhaus',
    codigo: 'LO—05',
    nombre: 'Bauhaus',
    familia: 'Reloj de vestir',
    homenaje: 'Homenaje al racionalismo alemán',
    frase: 'Menos elementos. Más intención.',
    descripcion: 'Proporción, espacio y agujas azules para una elegancia que no necesita levantar la voz.',
    historia: 'Bauhaus celebra la tradición del diseño funcional centroeuropeo: cada línea tiene un motivo y nada ocupa más espacio del necesario. La esfera y la firma son inequívocamente laOra.',
    precio: null,
    diametro: '38 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/bauhaus-profile.webp',
    galeria: ['/assets/img/relojes-2026/bauhaus-profile.webp',
              '/assets/img/relojes-2026/bauhaus-hero.webp',
              '/assets/img/relojes-2026/bauhaus-back.webp'],
    fichaTecnica: [['Caja', 'Acero pulido'],
                   ['Esfera', 'Marfil mate'],
                   ['Agujas', 'Azules'],
                   ['Correa', 'Piel arena']]
  },
  {
    slug: 'cero-cero',
    codigo: 'LO—06',
    nombre: 'Cero Cero',
    familia: 'Buceo',
    homenaje: 'Homenaje al buceador profesional contemporáneo',
    frase: 'Herramienta bajo el agua. Carácter fuera de ella.',
    descripcion: 'Un buceador rotundo con lectura de alto contraste y un acento naranja que lo hace suyo.',
    historia: 'Cero Cero recoge el lenguaje del reloj de buceo profesional sin copiar una identidad ajena. Sus proporciones, su esfera y su firma laOra convierten la referencia en una pieza independiente.',
    precio: null,
    diametro: '41 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/cero-cero-hero.webp',
    galeria: ['/assets/img/relojes-2026/cero-cero-hero.webp',
              '/assets/img/relojes-2026/cero-cero-profile.webp',
              '/assets/img/relojes-2026/cero-cero-back.webp'],
    fichaTecnica: [['Caja', 'Acero 316L'],
                   ['Bisel', 'Giratorio de buceo'],
                   ['Esfera', 'Negro mate · acento naranja'],
                   ['Brazalete', 'Malla de acero']]
  },
  {
    slug: 'coctel',
    codigo: 'LO—07',
    nombre: 'Cóctel',
    familia: 'Reloj de vestir',
    homenaje: 'Homenaje a las esferas de cóctel japonesas',
    frase: 'La hora elegante, sin esperar una ocasión.',
    descripcion: 'Una esfera marrón trabajada por la luz, índices facetados y piel oscura.',
    historia: 'Cóctel toma la esfera expresiva del reloj de vestir japonés como punto de partida. La referencia se reconoce; la marca, la selección y el servicio son laOra.',
    precio: null,
    diametro: '38 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/coctel-profile.webp',
    galeria: ['/assets/img/relojes-2026/coctel-profile.webp',
              '/assets/img/relojes-2026/coctel-hero.webp',
              '/assets/img/relojes-2026/coctel-back.webp'],
    fichaTecnica: [['Caja', 'Acero pulido'],
                   ['Esfera', 'Marrón con textura radial'],
                   ['Índices', 'Aplicados y facetados'],
                   ['Correa', 'Piel marrón']]
  },
  {
    slug: 'tortuga',
    codigo: 'LO—08',
    nombre: 'Tortuga',
    familia: 'Buceo',
    homenaje: 'Homenaje al buceador de caja cojín',
    frase: 'Un icono de aventura, a nuestra manera.',
    descripcion: 'Caja cojín, corona a las cuatro y esfera verde profunda para un buceador con presencia.',
    historia: 'Tortuga parte de uno de los perfiles de buceo más queridos del mundo. Lo hacemos sin disfrazarlo de original: esfera, nombre y emblema son laOra; el homenaje forma parte de su historia y se cuenta con claridad.',
    precio: null,
    diametro: '42 mm',
    hermeticidad: null,
    foto: '/assets/img/relojes-2026/tortuga-detail.webp',
    galeria: ['/assets/img/relojes-2026/tortuga-detail.webp',
              '/assets/img/relojes-2026/tortuga-hero.webp',
              '/assets/img/relojes-2026/box.webp'],
    fichaTecnica: [['Caja', 'Acero 316L tipo cojín'],
                   ['Corona', 'A las 4'],
                   ['Esfera', 'Verde profundo'],
                   ['Correa', 'Caucho negro waffle']]
  }
];

/* Precio en euros a la española. Con `null` devuelve cadena vacía y
   quien la pinta se encarga de no dejar un hueco raro. */
window.LAORA_PRECIO = function (valor) {
  if (valor === null || valor === undefined) return '';
  return new Intl.NumberFormat('es-ES', {
    style: 'currency', currency: 'EUR',
    minimumFractionDigits: Number.isInteger(valor) ? 0 : 2,
    maximumFractionDigits: 2
  }).format(valor);
};

window.LAORA_RELOJ = function (slug) {
  return window.LAORA_CATALOGO.filter(function (r) { return r.slug === slug; })[0] || null;
};

/* Tarjeta de producto. La usan la home y el listado de colección, así
   que las dos enseñan exactamente lo mismo: es el desajuste que hubo
   entre ficha y listado en la web anterior y no se repite.

   Si el modelo no tiene precio cerrado, la línea del precio no se
   pinta: no queda un hueco ni un «—», sencillamente no está. */
window.LAORA_TARJETA = function (r) {
  var art = document.createElement('article');
  art.className = 'p-tarjeta';

  var enlaceFoto = document.createElement('a');
  enlaceFoto.className = 'p-foto';
  enlaceFoto.href = '/' + r.slug + '.html';
  enlaceFoto.setAttribute('aria-label', 'Ver ' + r.nombre);

  var img = document.createElement('img');
  img.src = r.foto;
  img.alt = r.nombre + ' de laOra, ' + r.familia.toLowerCase();
  img.loading = 'lazy';

  var cod = document.createElement('span');
  cod.className = 'p-codigo';
  cod.textContent = r.codigo;

  var fle = document.createElement('span');
  fle.className = 'p-flecha';
  fle.setAttribute('aria-hidden', 'true');
  fle.textContent = '↗';

  enlaceFoto.append(img, cod, fle);

  var meta = document.createElement('div');
  meta.className = 'p-meta';
  var fam = document.createElement('p'); fam.textContent = r.familia;
  var dia = document.createElement('p'); dia.textContent = r.diametro;
  meta.append(fam, dia);

  var h3 = document.createElement('h3'); h3.textContent = r.nombre;
  var frase = document.createElement('p'); frase.className = 'p-frase'; frase.textContent = r.frase;
  var hom = document.createElement('p'); hom.className = 'p-homenaje'; hom.textContent = r.homenaje;

  var acciones = document.createElement('div');
  acciones.className = 'p-acciones';
  if (r.precio !== null && r.precio !== undefined) {
    var precio = document.createElement('span');
    precio.className = 'p-precio';
    precio.textContent = 'Desde ' + window.LAORA_PRECIO(r.precio);
    acciones.appendChild(precio);
  }
  var ver = document.createElement('a');
  ver.href = '/' + r.slug + '.html';
  ver.innerHTML = 'Ver ' + r.nombre + ' <span aria-hidden="true">→</span>';
  acciones.appendChild(ver);

  art.append(enlaceFoto, meta, h3, frase, hom, acciones);
  return art;
};
