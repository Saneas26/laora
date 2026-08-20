/* ============================================================
   laOra · LAS TRES PREGUNTAS
   ------------------------------------------------------------
   Óscar, 18/08/2026: la entrada del que llega sin saber nada de
   relojes. Tres preguntas —muñeca, para qué y cuánto— y como
   mucho TRES relojes con el motivo escrito. Nunca veinte de golpe.

   Reglas de la casa que van dentro del código, no del texto:
   · La muñeca se pregunta LA PRIMERA. Es el miedo número uno del
     que compra su primer reloj bueno y nadie del sector lo
     pregunta antes que el modelo.
   · Si no hay nada que encaje, se dice. Antes que empujar un
     reloj que no le sirve, se le enseña lo más cercano y se le
     avisa de en qué falla.
   · Cada recomendación lleva su «pero»: lo que ese reloj NO hace.
     Es lo que hace creíble todo lo demás.
   · Aquí NO se pide un correo. Al que llega de la calle no se le
     guarda nada: hay una respuesta, no un embudo que capture.
   · Al que YA ha entrado con su cuenta sí se le anotan las tres
     respuestas en su ficha (19/08/2026), y entonces no se le
     vuelven a preguntar cada vez que abre la colección. Y si ya
     nos dijo su muñeca en centímetros, la primera pregunta se
     deduce de ahí: preguntar dos veces lo mismo es de no escuchar.
   ============================================================ */
(function () {
  'use strict';

  var caja = document.querySelector('[data-recomendador]');
  if (!caja) return;

  /* DOS PUERTAS (Óscar, 20/08/2026). Las mismas tres preguntas, pero
     preguntadas de otra manera cuando el reloj es para otro:
     · La muñeca cambia de persona Y de respuestas. Nadie mide la
       muñeca de otro a escondidas, así que «No lo sé» pasa a ser la
       PRIMERA opción, que es la verdad en casi todos los regalos, y
       las pistas dejan de ser centímetros para ser lo que se ve.
     · El uso cambia de persona: «para mojarse», no «para mojarme».
     · El presupuesto NO cambia. El dinero es de quien regala, así que
       esa pregunta sigue siendo suya y en primera persona. */
  var PREGUNTAS_MI = [
    { clave: 'muneca', titulo: '¿Cómo tienes la muñeca?',
      pie: 'Es lo primero, porque un reloj que baila o que sobresale no te lo vas a poner.',
      opciones: [
        { v: 'fina',   r: 'Fina',    d: 'Menos de 16 cm de contorno' },
        { v: 'normal', r: 'Normal',  d: 'Entre 16 y 18 cm' },
        { v: 'ancha',  r: 'Ancha',   d: 'Más de 18 cm' },
        { v: 'nose',   r: 'Ni idea', d: 'Te enseño de todo y ya lo afinamos' }
      ] },
    { clave: 'uso', titulo: '¿Para qué lo quieres?',
      pie: 'Si solo vas a tener uno, el de todos los días casi siempre es la respuesta.',
      opciones: [
        { v: 'dia',    r: 'Para todos los días', d: 'Trabajo, calle y cena, el mismo' },
        { v: 'agua',   r: 'Para mojarme',        d: 'Ducha, piscina o mar' },
        { v: 'vestir', r: 'Para arreglarme',     d: 'Traje, bodas, cenas de las buenas' },
        { v: 'hablar', r: 'Que dé que hablar',   d: 'De los que te preguntan qué llevas' }
      ] },
    { clave: 'presupuesto', titulo: '¿Cuánto te quieres gastar?',
      pie: 'Sin rodeos: aquí el precio es uno y no hay descuentos que valgan.',
      opciones: [
        { v: 'hasta200', r: 'Hasta 200 €',   d: '' },
        { v: '200a300',  r: 'De 200 a 300 €', d: '' },
        { v: 'mas300',   r: 'Más de 300 €',   d: '' },
        { v: 'da-igual', r: 'Enséñamelo todo', d: 'Ya decidiré yo' }
      ] }
  ];

  var PREGUNTAS_REGALO = [
    { clave: 'muneca', titulo: '¿Cómo tiene él o ella la muñeca?',
      pie: 'Nadie mide la muñeca de otro a escondidas. Si no lo sabes, dilo sin más: es la respuesta normal en un regalo y te enseño lo que le queda bien a casi cualquiera.',
      opciones: [
        { v: 'nose',   r: 'No lo sé',  d: 'Lo normal en un regalo. Te enseño lo que vale para casi cualquier muñeca' },
        { v: 'fina',   r: 'Fina',      d: 'Se le ve la muñeca delgada' },
        { v: 'normal', r: 'Normal',    d: 'Ni delgada ni fuerte' },
        { v: 'ancha',  r: 'Ancha',     d: 'Muñeca fuerte, de las que llenan la correa' }
      ] },
    { clave: 'uso', titulo: '¿Para qué lo va a usar?',
      pie: 'Si va a tener uno solo, el de todos los días casi siempre es la respuesta.',
      opciones: [
        { v: 'dia',    r: 'Para todos los días', d: 'Trabajo, calle y cena, el mismo' },
        { v: 'agua',   r: 'Para mojarse',        d: 'Ducha, piscina o mar' },
        { v: 'vestir', r: 'Para arreglarse',     d: 'Traje, bodas, cenas de las buenas' },
        { v: 'hablar', r: 'Que dé que hablar',   d: 'De los que le preguntan qué lleva' }
      ] },
    { clave: 'presupuesto', titulo: '¿Cuánto te quieres gastar?',
      pie: 'Esta sigue siendo tuya: aquí el precio es uno y no hay descuentos que valgan.',
      opciones: [
        { v: 'hasta200', r: 'Hasta 200 €',   d: '' },
        { v: '200a300',  r: 'De 200 a 300 €', d: '' },
        { v: 'mas300',   r: 'Más de 300 €',   d: '' },
        { v: 'da-igual', r: 'Enséñamelo todo', d: 'Ya decidiré yo' }
      ] }
  ];

  var TEXTOS = {
    mi: {
      cabecera: 'Lo que yo me llevaría',
      muneca: 'Para tu muñeca no tengo la medida ideal en ese uso. Estos te valen, pero mírales el diámetro.',
      red: ''
    },
    regalo: {
      cabecera: 'Lo que yo le regalaría',
      muneca: 'Para esa muñeca no tengo la medida ideal en ese uso. Estos valen, pero mírales el diámetro.',
      red: 'Y si la medida no acierta, hay 30 días para devolverlo, con el envío pagado.'
    }
  };

  var MODO = 'mi';
  function PREGS() { return MODO === 'regalo' ? PREGUNTAS_REGALO : PREGUNTAS_MI; }

  var MM = { fina: [36, 39], normal: [36, 39, 40], ancha: [40, 41] };
  var TRAMO = {
    hasta200: function (p) { return p <= 200; },
    '200a300': function (p) { return p > 200 && p <= 300; },
    mas300:   function (p) { return p > 300; }
  };

  var fichas = null, paso = 0, respuestas = {};
  var SOCIO = null;       // {id, …} solo si ha entrado con su cuenta
  var recordado = false;  // true si las tres salieron de su ficha

  /* Su medida en centímetros vale por la primera pregunta: los tramos
     son los mismos que se le enseñan en los botones. */
  function deCentimetros(cm) {
    cm = Number(cm);
    if (!cm) return null;
    if (cm < 16) return 'fina';
    if (cm <= 18) return 'normal';
    return 'ancha';
  }

  /* Se anota lo que responde, si es de casa. Si falla, no se le dice
     nada: no ha venido a guardar un perfil, ha venido a que le
     recomienden un reloj. */
  function anota(clave, valor) {
    /* En modo regalo NO se anota: esas respuestas son de otra persona
       y meterlas en su ficha sería ensuciarla. */
    if (MODO === 'regalo') return;
    if (!SOCIO || !SOCIO.id || !window.laoraSesion || !laoraSesion.escribir) return;
    var cambios = { rec_fecha: new Date().toISOString() };
    cambios['rec_' + clave] = valor;
    laoraSesion.escribir('socios?id=eq.' + SOCIO.id, {
      method: 'PATCH', body: JSON.stringify(cambios)
    }).catch(function () {});
  }

  /* ---------- pintar ---------- */

  function pinta() {
    if (paso < PREGS().length) return pintaPregunta(PREGS()[paso]);
    pintaRespuesta();
  }

  function pintaPregunta(p) {
    var html = '<p class="rec-paso">Pregunta ' + (paso + 1) + ' de 3</p>' +
               '<h2 class="rec-titulo">' + p.titulo + '</h2>' +
               '<div class="rec-opciones">';
    for (var i = 0; i < p.opciones.length; i++) {
      var o = p.opciones[i];
      html += '<button type="button" class="rec-opcion" data-valor="' + o.v + '">' +
              '<b>' + o.r + '</b>' + (o.d ? '<span>' + o.d + '</span>' : '') + '</button>';
    }
    html += '</div><p class="rec-pie">' + p.pie + '</p>';
    if (paso > 0) html += '<button type="button" class="rec-atras" data-atras>← Volver</button>';
    caja.innerHTML = html;

    var botones = caja.querySelectorAll('.rec-opcion');
    for (var j = 0; j < botones.length; j++) {
      botones[j].addEventListener('click', function () {
        var clave = PREGS()[paso].clave;
        respuestas[clave] = this.dataset.valor;
        anota(clave, this.dataset.valor);
        paso++;
        pinta();
      });
    }
    var atras = caja.querySelector('[data-atras]');
    if (atras) atras.addEventListener('click', function () { paso--; pinta(); });
  }

  /* ---------- elegir ---------- */

  function encajaMuneca(f) {
    if (respuestas.muneca === 'nose') return true;
    return MM[respuestas.muneca].indexOf(f.mm) !== -1;
  }
  function encajaPrecio(f) {
    if (respuestas.presupuesto === 'da-igual') return true;
    return TRAMO[respuestas.presupuesto](f.precio);
  }
  function encajaUso(f) { return f.usos.indexOf(respuestas.uso) !== -1; }

  /* Se busca lo que cumple las tres. Si no hay nada, se afloja UNA
     condición cada vez y se dice cuál se ha aflojado: primero el
     precio —que es lo que el cliente sabe negociar consigo mismo—,
     luego la muñeca, y solo al final el uso, que es lo único que no
     se puede traicionar sin venderle un reloj que no le sirve. */
  function elige() {
    var todas = fichas.filter(encajaUso);
    var exacto = todas.filter(encajaMuneca).filter(encajaPrecio);
    if (exacto.length) return { lista: orden(exacto), aviso: null };

    var sinPrecio = todas.filter(encajaMuneca);
    if (sinPrecio.length) return { lista: orden(sinPrecio), aviso: 'precio' };

    var sinMuneca = todas.filter(encajaPrecio);
    if (sinMuneca.length) return { lista: orden(sinMuneca), aviso: 'muneca' };

    if (todas.length) return { lista: orden(todas), aviso: 'ambos' };
    return { lista: [], aviso: 'nada' };
  }

  function orden(lista) {
    return lista.slice().sort(function (a, b) { return a.precio - b.precio; }).slice(0, 3);
  }

  /* El motivo se escribe con los datos de la propia ficha: nada de
     frases genéricas que valen para cualquier reloj. */
  function motivo(f) {
    var trozos = [f.mm + ' mm'];
    if (respuestas.muneca === 'fina' && f.mm <= 39) trozos[0] += ', que en muñeca fina queda clavado';
    if (respuestas.muneca === 'ancha' && f.mm >= 40) trozos[0] += ', que es lo que pide una muñeca ancha';
    trozos.push(f.agua);
    trozos.push(f.movimiento);
    return trozos;
  }

  function euros(n) { return n.toFixed(2).replace('.', ',') + ' €'; }

  function pintaRespuesta() {
    var r = elige();
    var T = TEXTOS[MODO];
    var html = '<p class="rec-paso">' + T.cabecera + '</p>';

    if (r.aviso === 'nada') {
      html += '<h2 class="rec-titulo">Hoy no tengo el reloj que buscas.</h2>' +
              '<p class="rec-pie">Y prefiero decírtelo a colocarte otro. Los que faltan están en el taller de diseño; cuando estén, estarán aquí.</p>';
    } else {
      if (r.aviso === 'precio') html += '<p class="rec-aviso">Con ese presupuesto exacto no tengo nada para ese uso. Esto es lo más cerca que estoy, y te digo el precio de verdad.</p>';
      if (r.aviso === 'muneca') html += '<p class="rec-aviso">' + T.muneca + '</p>';
      if (r.aviso === 'ambos')  html += '<p class="rec-aviso">Ni la medida ni el precio me cuadran del todo con lo que buscas. Te enseño lo que hay, sin adornos.</p>';

      if (T.red) html += '<p class="rec-red">' + T.red + '</p>';
      html += '<div class="rec-fichas">';
      for (var i = 0; i < r.lista.length; i++) {
        var f = r.lista[i];
        html += '<article class="rec-ficha">' +
                  '<img src="' + f.foto + '" alt="' + f.alt + '" loading="lazy" decoding="async">' +
                  '<div class="rec-ficha-cuerpo">' +
                    '<p class="rec-ficha-nombre"><b>' + f.modelo + '</b> <span>' + f.acabado + '</span></p>' +
                    '<p class="rec-ficha-precio">' + euros(f.precio) + '</p>' +
                    '<ul class="rec-porque">' +
                      '<li>' + motivo(f).join('</li><li>') + '</li>' +
                    '</ul>' +
                    '<p class="rec-pero"><b>Pero:</b> ' + f.noEs + '</p>' +
                    '<a class="rec-ir" href="' + f.enlace + '">Verlo entero</a>' +
                  '</div>' +
                '</article>';
      }
      html += '</div>';
    }

    /* Si las respuestas salen de su ficha, se dice. Que la página
       acierte sin preguntar está bien; que no se sepa por qué, no. */
    if (recordado) {
      var dicho = [];
      for (var q = 0; q < PREGS().length; q++) {
        var pr = PREGS()[q];
        for (var o = 0; o < pr.opciones.length; o++) {
          if (pr.opciones[o].v === respuestas[pr.clave]) dicho.push(pr.opciones[o].r.toLowerCase());
        }
      }
      html = '<p class="rec-recordado">Esto va por lo que ya nos contaste: <b>' +
             dicho.join('</b>, <b>') + '</b>. Si ha cambiado, vuelve a empezar aquí abajo.</p>' + html;
    }

    html += '<button type="button" class="rec-atras" data-otra>← Empezar otra vez</button>';
    caja.innerHTML = html;
    caja.querySelector('[data-otra]').addEventListener('click', function () {
      paso = 0; respuestas = {}; recordado = false; pinta();
    });
  }

  /* ---------- arranque ---------- */

  /* Lo que ya nos contó, si es de casa. Se pregunta solo lo que
     falte; si están las tres, se le enseña directamente su
     recomendación, con el «empezar otra vez» de siempre debajo. */
  function loQueYaSabemos() {
    if (!window.laoraSesion || !laoraSesion.hay()) return Promise.resolve();
    return laoraSesion.quienSoy().then(function (u) {
      if (!u) return;
      SOCIO = { id: u.id };
      return laoraSesion.consultar(
        'socios?select=muneca_cm,rec_muneca,rec_uso,rec_presupuesto&limit=1');
    }).then(function (filas) {
      var s = filas && filas[0];
      if (!s) return;
      var muneca = s.rec_muneca || deCentimetros(s.muneca_cm);
      if (muneca) respuestas.muneca = muneca;
      if (s.rec_uso) respuestas.uso = s.rec_uso;
      if (s.rec_presupuesto) respuestas.presupuesto = s.rec_presupuesto;
      /* El paso es la primera pregunta sin contestar. */
      while (paso < PREGS().length && respuestas[PREGS()[paso].clave]) paso++;
      recordado = paso >= PREGS().length;
    }).catch(function () {});
  }

  /* ---------- las dos puertas ---------- */

  /* Hasta que no se pulsa un botón no se pregunta nada: quien ya sabe
     lo que busca baja directo a la colección y no se encuentra un
     cuestionario delante. */
  var seccion = caja.closest('.rec');
  var puertas = document.querySelectorAll('[data-rec-abre]');

  function abre(modo, boton) {
    MODO = modo;
    paso = 0; respuestas = {}; recordado = false;
    for (var i = 0; i < puertas.length; i++) {
      puertas[i].setAttribute('aria-expanded', puertas[i] === boton ? 'true' : 'false');
    }
    if (seccion) seccion.hidden = false;
    /* Lo que ya nos contó vale para ÉL, no para a quien regala. */
    var listo = modo === 'mi' ? loQueYaSabemos() : Promise.resolve();
    listo.then(function () {
      pinta();
      if (seccion) seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  fetch('/assets/datos/recomendador.json')
    .then(function (r) { return r.json(); })
    .then(function (d) {
      fichas = d.fichas;
      for (var i = 0; i < puertas.length; i++) {
        puertas[i].addEventListener('click', function () {
          abre(this.dataset.recAbre, this);
        });
      }
    })
    .catch(function () {
      /* Sin datos no se enseña un cacharro roto ni un botón que no
         hace nada: se quitan los dos y la colección sigue entera. */
      if (seccion) seccion.hidden = true;
      var cajaBotones = document.querySelector('[data-puertas]');
      if (cajaBotones) cajaBotones.hidden = true;
    });
})();
