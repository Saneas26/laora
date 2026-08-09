/* ============================================================
   laOra · CONFIGURADOR DE TRES EJES  ·  MAQUETA
   ------------------------------------------------------------
   Todo el estado son tres índices —movimiento, caja, brazalete— más
   el color elegido dentro del brazalete. De ahí sale TODO lo demás:
   la foto, las características, la referencia y el precio.

   EL PRECIO NO ESTÁ ESCRITO EN NINGUNA PARTE. Se suma el coste de las
   tres piezas, se multiplica y se redondea al 9,90 más cercano. Por
   eso un brazalete nuevo no obliga a decidir un precio: entra con el
   suyo puesto.

   El redondeo va al 9,90 MÁS CERCANO, no al de arriba: 219,89 € tiene
   que caer en 219,90 y no en 229,90. Diez euros de diferencia por un
   céntimo de cálculo.
   ============================================================ */
(function () {
  'use strict';

  var datos = JSON.parse(document.querySelector('[data-piezas]').textContent);
  var $ = function (s) { return document.querySelector(s); };

  var estado = { mov: 0, caja: 0, brz: 0, color: 0 };

  function euros(v) {
    return v.toFixed(2).replace('.', ',') + ' €';
  }

  /* Al 9,90 más cercano: se buscan el 9,90 de abajo y el de arriba, y
     gana el que esté más cerca.

     OJO CON EL DE ABAJO. La cuenta evidente —`floor(p/10)*10 + 9,90`—
     está mal, y calla: para 264,56 € devuelve 269,90, que está POR
     ENCIMA. Solo acierta cuando los decimales ya pasan de 9,90. Hay que
     restar el 9,90 ANTES de truncar. Con la versión mala, cinco de las
     siete configuraciones del Lunar salían diez euros caras. */
  function redondea(p) {
    var bajo = Math.floor((p - 9.90) / 10) * 10 + 9.90;
    var alto = bajo + 10;
    return (p - bajo) <= (alto - p) ? bajo : alto;
  }

  /* ---------- el DIBUJO del brazalete ----------
     La muestra que trae cada color es un color plano —o dos, si el
     brazalete es bicolor—. Un rectángulo de color plano no parece un
     brazalete: parece una cinta. Aquí se le da el relieve del metal
     (una luz que cruza en diagonal) y la sombra entre eslabones.

     Cuando lleguen las fotos de brazalete, esta función desaparece y
     la banda pasa a ser un <img>. Nada más cambia. */
  function mezcla(hex, con, cuanto) {
    var a = parseInt(hex.slice(1), 16), b = parseInt(con.slice(1), 16);
    var out = 0, i;
    for (i = 16; i >= 0; i -= 8) {
      var v = Math.round((((a >> i) & 255) * (1 - cuanto)) + (((b >> i) & 255) * cuanto));
      out |= v << i;
    }
    return '#' + ('000000' + out.toString(16)).slice(-6);
  }

  var ESLABONES = 'repeating-linear-gradient(0deg,rgba(0,0,0,.16) 0 1.5px,rgba(255,255,255,.10) 1.5px 3px,rgba(0,0,0,0) 3px 15px)';

  function metal(c) {
    return mezcla(c, '#ffffff', .58) + ' 0%,' +
      mezcla(c, '#000000', .20) + ' 28%,' +
      mezcla(c, '#ffffff', .46) + ' 50%,' +
      mezcla(c, '#000000', .30) + ' 74%,' +
      mezcla(c, '#ffffff', .22) + ' 100%';
  }

  /* Un brazalete bicolor NO es medio plateado y medio dorado en
     diagonal: es plateado por fuera y dorado por el centro, que es por
     donde corren los eslabones del medio. Con dos tonos se dibujan
     tres franjas verticales; con uno, el metal a secas. */
  function dibujo(tonos) {
    if (tonos.length > 1) {
      return ESLABONES +
        ',linear-gradient(90deg,' +
        mezcla(tonos[0], '#ffffff', .40) + ' 0 30%,' +
        mezcla(tonos[1], '#ffffff', .34) + ' 30% 42%,' +
        mezcla(tonos[1], '#000000', .12) + ' 42% 58%,' +
        mezcla(tonos[1], '#ffffff', .34) + ' 58% 70%,' +
        mezcla(tonos[0], '#000000', .18) + ' 70% 100%)';
    }
    return ESLABONES + ',linear-gradient(100deg,' + metal(tonos[0]) + ')';
  }

  function piezas() {
    var brz = datos.brazaletes[estado.brz];
    return {
      mov: datos.movimientos[estado.mov],
      caja: datos.cajas[estado.caja],
      brz: brz,
      color: brz.colores[Math.min(estado.color, brz.colores.length - 1)]
    };
  }

  function coste() {
    var p = piezas();
    return p.mov.coste + p.caja.coste + p.color.coste;
  }

  /* ---------- LA REFERENCIA ----------
     Cuatro segmentos de largo fijo, uno por biblioteca:

         LO-03 - M1 - C1 - B09.2
           │     │    │     │ └─ variante 2 de esa familia
           │     │    │     └─── brazalete 09 del catálogo ENTERO
           │     │    └───────── caja 1 de este modelo
           │     └────────────── movimiento 1 de este modelo
           └──────────────────── modelo, columna A de Movimientos

     El brazalete se numera en el catálogo entero y no dentro del
     modelo, porque la misma pieza la montan varios relojes: si fuera
     «B1» en el Lunar y «B3» en el Cero Cero, un día se compraría la
     que no es.

     Y no lleva ni una palabra dentro. El día que un brazalete cambie
     de nombre, los pedidos viejos tienen que seguir cuadrando. */
  function referencia() {
    var p = piezas();
    return [datos.codigo, p.mov.ref, p.caja.ref, p.color.ref].join('-');
  }

  /* ---------- pintar ---------- */

  function pintaVisor() {
    var p = piezas();
    $('[data-foto]').src = p.caja.foto;
    $('[data-pendiente]').hidden = !p.caja.fotoPendiente;
    var fondo = dibujo(p.color.tonos);
    Array.prototype.forEach.call(document.querySelectorAll('[data-correa]'), function (el) {
      el.style.background = fondo;
    });
    $('[data-viendo]').innerHTML = '<b>' + p.caja.nombre + '</b> <span>· ' +
      p.brz.nombre + ' · ' + p.color.nombre + '</span>';
  }

  function pintaSpecs() {
    var p = piezas();
    var filas = p.mov.specs.concat(p.caja.specs);
    $('[data-specs]').innerHTML = filas.map(function (f) {
      return '<dt>' + f[0] + '</dt><dd>' + f[1] + '</dd>';
    }).join('');
  }

  function pintaColores() {
    var p = piezas();
    var caja = $('[data-colores]');
    caja.innerHTML = p.brz.colores.map(function (c, i) {
      return '<button class="cf-color" type="button" data-color="' + i + '"' +
        ' aria-pressed="' + (i === estado.color) + '"' +
        ' aria-label="' + c.nombre + '" title="' + c.nombre + '"' +
        ' style="background:' + c.muestra + '"></button>';
    }).join('') + '<span class="cf-color-nombre" data-color-nombre></span>';
    $('[data-color-nombre]').textContent = p.color.nombre;
    /* Con una sola variante no se pinta el grupo: la misma regla que
       con el movimiento. Y el rótulo lo pone la familia, porque no
       todas varían en COLOR —la de acero macizo varía en eslabonado—. */
    $('[data-grupo-color]').hidden = p.brz.colores.length < 2;
    $('[data-rotulo-variante]').textContent = p.brz.variante;
    $('[data-detalle]').textContent = p.brz.material + ' · ' + p.brz.detalle;
  }

  /* Los cuadraditos del brazalete los pinta el generador con el color
     plano del primer color de cada familia; aquí se les da el mismo
     dibujo que la banda para que el cuadro y el reloj coincidan. */
  function pintaMuestras() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-brz] i'), function (el, i) {
      el.style.background = dibujo(datos.brazaletes[i].colores[0].tonos);
    });
  }

  function pintaPrecio() {
    var p = piezas();
    var c = coste();
    var pvp = redondea(c * datos.multiplicador);
    $('[data-precio]').textContent = euros(pvp);
    $('[data-barra-nombre]').textContent = p.caja.nombre + ' · ' + p.brz.nombre;
    $('[data-barra-color]').textContent = p.color.nombre;

    /* La referencia NUNCA se enseña sola: al lado van siempre las
       palabras. Corta para la máquina, completa para la persona. */
    $('[data-ref]').textContent = referencia();

    $('[data-desglose]').innerHTML =
      '<b>Lo que hay que comprar</b><br>' +
      'Movimiento <i>' + p.mov.ref + '</i> ' + euros(p.mov.coste) + '<br>' +
      'Caja y esfera <i>' + p.caja.ref + '</i> ' + euros(p.caja.coste) + '<br>' +
      'Brazalete <i>' + p.color.ref + '</i> ' + euros(p.color.coste) + '<br>' +
      'Suma <i>' + euros(c) + '</i><br>' +
      '× ' + String(datos.multiplicador).replace('.', ',') + ' → <b>' + euros(pvp) + '</b>';
  }

  function pinta() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-caja]'), function (el) {
      el.setAttribute('aria-pressed', String(Number(el.dataset.caja) === estado.caja));
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-brz]'), function (el) {
      el.setAttribute('aria-pressed', String(Number(el.dataset.brz) === estado.brz));
    });
    pintaColores();
    pintaVisor();
    pintaSpecs();
    pintaPrecio();
  }

  /* ---------- escuchar ---------- */

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-caja],[data-brz],[data-color]');
    if (!b) return;
    if (b.dataset.caja !== undefined) estado.caja = Number(b.dataset.caja);
    else if (b.dataset.brz !== undefined) { estado.brz = Number(b.dataset.brz); estado.color = 0; }
    else estado.color = Number(b.dataset.color);
    pinta();
  });

  pintaMuestras();
  pinta();
})();
