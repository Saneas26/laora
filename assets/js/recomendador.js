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
   · Aquí no se pide un correo ni se guarda nada. No hay embudo
     que capture: hay una respuesta.
   ============================================================ */
(function () {
  'use strict';

  var caja = document.querySelector('[data-recomendador]');
  if (!caja) return;

  var PREGUNTAS = [
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

  var MM = { fina: [36, 39], normal: [36, 39, 40], ancha: [40, 41] };
  var TRAMO = {
    hasta200: function (p) { return p <= 200; },
    '200a300': function (p) { return p > 200 && p <= 300; },
    mas300:   function (p) { return p > 300; }
  };

  var fichas = null, paso = 0, respuestas = {};

  /* ---------- pintar ---------- */

  function pinta() {
    if (paso < PREGUNTAS.length) return pintaPregunta(PREGUNTAS[paso]);
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
        respuestas[PREGUNTAS[paso].clave] = this.dataset.valor;
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
    var html = '<p class="rec-paso">Lo que yo me llevaría</p>';

    if (r.aviso === 'nada') {
      html += '<h2 class="rec-titulo">Hoy no tengo el reloj que buscas.</h2>' +
              '<p class="rec-pie">Y prefiero decírtelo a colocarte otro. Los que faltan están en el taller de diseño; cuando estén, estarán aquí.</p>';
    } else {
      if (r.aviso === 'precio') html += '<p class="rec-aviso">Con ese presupuesto exacto no tengo nada para ese uso. Esto es lo más cerca que estoy, y te digo el precio de verdad.</p>';
      if (r.aviso === 'muneca') html += '<p class="rec-aviso">Para tu muñeca no tengo la medida ideal en ese uso. Estos te valen, pero mírales el diámetro.</p>';
      if (r.aviso === 'ambos')  html += '<p class="rec-aviso">Ni la medida ni el precio me cuadran del todo con lo que buscas. Te enseño lo que hay, sin adornos.</p>';

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

    html += '<button type="button" class="rec-atras" data-otra>← Empezar otra vez</button>';
    caja.innerHTML = html;
    caja.querySelector('[data-otra]').addEventListener('click', function () {
      paso = 0; respuestas = {}; pinta();
    });
  }

  /* ---------- arranque ---------- */

  fetch('/assets/datos/recomendador.json')
    .then(function (r) { return r.json(); })
    .then(function (d) { fichas = d.fichas; pinta(); })
    .catch(function () {
      /* Sin datos no se enseña un cacharro roto: se quita de en medio
         y la colección de abajo sigue estando entera. */
      var seccion = caja.closest('.rec');
      if (seccion) seccion.hidden = true;
    });
})();
