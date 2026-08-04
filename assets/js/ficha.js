/* ============================================================
   laOra · FICHA DE RELOJ
   ------------------------------------------------------------
   Dos cosas: la galería y el configurador.

   Todo lo que pinta el configurador viene del <script
   type="application/json" data-configurador> que escribe el
   generador desde assets/datos/catalogo.json. Ahí NO hay nada
   interno: ni proveedores, ni enlaces de compra, ni coste, ni
   margen. Solo lo que ve el cliente.

   Si este fichero no llega a cargarse, la ficha se sigue leyendo
   entera: sale la primera foto, el precio de entrada y las
   especificaciones del primer acabado, que van escritas en el
   HTML. Lo único que se pierde es poder cambiar de opción.
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 1 · la galería ---------- */
  (function galeria() {
    var grande = document.querySelector('[data-foto-grande]');
    var minis = document.querySelectorAll('[data-mini]');
    if (!grande || minis.length < 2) return;

    function elegir(boton) {
      grande.src = boton.dataset.mini;
      for (var i = 0; i < minis.length; i++) {
        minis[i].classList.toggle('active', minis[i] === boton);
      }
    }
    for (var i = 0; i < minis.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () { elegir(boton); });
      })(minis[i]);
    }
  })();


  /* ---------- 2 · el configurador ---------- */
  (function configurador() {
    var caja = document.querySelector('[data-configurador]');
    if (!caja) return;

    var d;
    try { d = JSON.parse(caja.textContent); } catch (e) { return; }
    if (!d || !d.acabados || !d.correas) return;

    var elPrecio = document.querySelector('[data-precio]');
    var elResumen = document.querySelector('[data-resumen-acabado]');
    var elRef = document.querySelector('[data-ref]');
    var elReservar = document.querySelector('[data-reservar]');

    /* Hay modelos con una sola opción de brazalete y sin grupo que elegir
       (el Bauhaus). Ahí `correas` viene vacío y el índice de correa es
       siempre 0: sin esto, `indexOf` devolvía -1 y se quedaban sin precio
       y con la referencia acabada en 00. */
    var correas = (d.correas && d.correas.length) ? d.correas : [{ nombre: '' }];

    /* La ficha abre por la combinación MÁS BARATA que se pueda pedir, no por
       la primera de la lista: es la cifra con la que Óscar quiere que empiece
       a mirar quien llega. Se recorre la tabla de precios entera y se busca el
       mínimo; si hay empate gana el primero, que es el orden de la hoja.
       El generador escribe en el HTML esa misma combinación, así que la página
       ya carga bien antes de que este fichero llegue a ejecutarse. */
    function masBarata() {
      var mejor = null;
      for (var i = 0; i < d.acabados.length; i++) {
        var lista = d.precios[d.acabados[i].id] || [];
        for (var j = 0; j < lista.length; j++) {
          if (lista[j] == null) continue;
          if (!mejor || lista[j] < mejor.precio) {
            mejor = { acabado: d.acabados[i], correa: correas[j] || correas[0],
                      precio: lista[j] };
          }
        }
      }
      return mejor || { acabado: d.acabados[0], correa: correas[0] };
    }

    var arranque = masBarata();
    var acabado = arranque.acabado;
    var correa = arranque.correa;

    /* La referencia se compone igual que en la hoja de materiales:
       LO-01_Lunar_A01 → modelo + inicial del acabado + número de correa.
       Así lo que el cliente ve en la web y lo que Óscar busca en la hoja
       es la misma cadena.

       `refSufijo` es para cuando dos acabados comparten inicial y la hoja
       los separa por el calibre: el Cero Cero tiene dos Cenit y en la hoja
       son LO-02_CeroCero_C01-ST2130 y LO-02_CeroCero_C01-NH38. Sin esto,
       los dos darían la misma referencia y llevarían al cajón equivocado.

       `refNum` fuerza el número cuando la hoja no lo saca de la correa.
       En el Precisa no hay correa que elegir y aun así los dos Cenit son
       C01-ST2130 y C02-NH35: el número lo puso Óscar a mano en la hoja,
       así que aquí se copia, no se calcula.

       Puede ser una cadena —vale para todas las correas— o una lista
       paralela a `correas`. El Trinchera la necesita en lista: numera
       correlativo dentro del acabado, no por correa, así que su segundo
       Cenit es C03 con la NATO verde y C04 con la negra. */
    /* `refLetra` es para cuando el acabado se renombra y la hoja no.
       El segundo Cenit del Precisa pasó a llamarse Eclipse, pero en la
       hoja sigue siendo LO-04_Precisa_C02-NH35: manda la hoja, porque esa
       cadena es la que Óscar busca cuando prepara el pedido. */
    function referencia() {
      var j = Math.max(0, correas.indexOf(correa));
      var letra = acabado.refLetra || acabado.nombre.charAt(0).toUpperCase();
      var codigo = d.codigo.replace(/[—–-]/g, '-').replace(/\s/g, '');
      /* La hoja escribe los modelos sin tildes y sin espacios: «Bitacora»,
         «CeroCero». El nombre bonito lleva las dos cosas, así que hay que
         desnudarlo o la referencia no casaría con la del almacén. */
      var modelo = d.modelo.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                           .replace(/\s/g, '');
      var num = acabado.refNum;
      if (Array.isArray(num)) num = num[j];
      if (!num) num = ('0' + (j + 1)).slice(-2);
      return codigo + '_' + modelo + '_' + letra +
             num + (acabado.refSufijo || '');
    }

    function euros(v) {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency', currency: 'EUR',
        minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 2
      }).format(v);
    }

    function pintar() {
      var j = Math.max(0, correas.indexOf(correa));
      var lista = d.precios[acabado.id] || [];
      var precio = lista[j];

      if (elPrecio) elPrecio.textContent = precio === undefined ? '' : euros(precio);
      if (elResumen) elResumen.textContent = acabado.resumen || '';
      if (elRef) elRef.textContent = referencia();

      /* La ficha técnica que depende del acabado. Una línea que este acabado
         no tenga se esconde entera —etiqueta incluida—: la hoja declara la
         estanqueidad del Lunar solo para el Cenit, y dejar ahí un «Estanqueidad»
         en blanco es peor que no ponerlo. */
      var campos = document.querySelectorAll('[data-spec]');
      for (var i = 0; i < campos.length; i++) {
        var clave = campos[i].dataset.spec;
        var valor = acabado[clave];
        campos[i].textContent = valor || '';
        if (campos[i].parentElement) campos[i].parentElement.hidden = !valor;
      }

      /* La foto grande sigue al acabado: el Eclipse tiene la suya, en negro,
         y no la del acero. Se hace pulsando su miniatura, que ya cambia la
         imagen y marca cuál está activa. */
      if (acabado.foto) {
        var mini = document.querySelector('[data-mini="' + acabado.foto + '"]');
        if (mini && !mini.classList.contains('active')) mini.click();
      }

      /* el botón se lleva la combinación elegida a la reserva */
      if (elReservar) {
        elReservar.setAttribute('href',
          '/reservar.html?ref=' + encodeURIComponent(referencia()) +
          '&acabado=' + encodeURIComponent(acabado.nombre) +
          (correa.nombre ? '&correa=' + encodeURIComponent(correa.nombre) : ''));
      }
    }

    function grupo(nombre, lista, alElegir) {
      var cont = document.querySelector('[data-grupo="' + nombre + '"]');
      if (!cont) return;
      var botones = cont.querySelectorAll('[data-' + nombre + ']');
      for (var i = 0; i < botones.length; i++) {
        (function (boton, indice) {
          boton.addEventListener('click', function () {
            for (var k = 0; k < botones.length; k++) {
              var esta = botones[k] === boton;
              botones[k].setAttribute('aria-selected', String(esta));
              if (esta) botones[k].removeAttribute('tabindex');
              else botones[k].setAttribute('tabindex', '-1');
            }
            alElegir(lista[indice]);
            pintar();
          });
        })(botones[i], i);
      }
    }

    /* No todos los acabados admiten las mismas correas. En el Cero Cero la
       hoja solo da malla milanesa y NATO para el Levante; los demás van con
       el brazalete Oyster y nada más. Con `acabado.correas` —una lista de
       ids— se ocultan las que ese acabado no tiene, y si se queda con una
       sola desaparece el grupo entero: un botón que no elige nada estorba.

       El acabado que no declare `correas` las admite todas, que es como se
       comportaban las fichas hasta ahora. */
    var NO_DISPONIBLE = 'No disponible con este acabado';

    function ajustarCorreas() {
      var cont = document.querySelector('[data-grupo="correa"]');
      if (!cont) return;
      var botones = cont.querySelectorAll('[data-correa]');
      var vivos = [];

      for (var i = 0; i < botones.length; i++) {
        var b = botones[i];
        var vale = !acabado.correas ||
                   acabado.correas.indexOf(b.dataset.correa) !== -1;
        if (vale) vivos.push(b);

        /* Se quedan A LA VISTA y apagados, no escondidos: así se ve de un
           vistazo con qué acabado sí las tendrías. Lo que no puede pasar es
           que se pulsen, porque esa combinación no existe en la hoja, no
           tiene precio, y dejaría un pedido sin importe. */
        b.disabled = !vale;
        var pie = b.querySelector('small');
        if (pie) {
          if (!pie.dataset.detalle) pie.dataset.detalle = pie.textContent;
          pie.textContent = vale ? pie.dataset.detalle : NO_DISPONIBLE;
        }
      }

      /* si la que estaba elegida ya no vale, se cae a la primera que sí */
      if (vivos.length && vivos.indexOf(
            cont.querySelector('[aria-selected="true"]')) === -1) {
        for (var k = 0; k < correas.length; k++) {
          if (correas[k].id === vivos[0].dataset.correa) correa = correas[k];
        }
        for (var m = 0; m < botones.length; m++) {
          var esta = botones[m] === vivos[0];
          botones[m].setAttribute('aria-selected', String(esta));
          if (esta) botones[m].removeAttribute('tabindex');
          else botones[m].setAttribute('tabindex', '-1');
        }
      }
    }

    /* Deja marcado el botón que toca. Lo normal es que el generador ya lo
       haya escrito así, pero si algún día los datos y el HTML se desalinean
       manda el dato, no el marcado. */
    function marcar(nombre, id) {
      var cont = document.querySelector('[data-grupo="' + nombre + '"]');
      if (!cont) return;
      var botones = cont.querySelectorAll('[data-' + nombre + ']');
      for (var i = 0; i < botones.length; i++) {
        var esta = botones[i].dataset[nombre] === id;
        botones[i].setAttribute('aria-selected', String(esta));
        if (esta) botones[i].removeAttribute('tabindex');
        else botones[i].setAttribute('tabindex', '-1');
      }
    }

    grupo('acabado', d.acabados, function (v) { acabado = v; ajustarCorreas(); });
    grupo('correa', correas, function (v) { correa = v; });

    marcar('acabado', acabado.id);
    if (correa.id) marcar('correa', correa.id);
    ajustarCorreas();
    pintar();
  })();

  /* ---------- 3 · las curiosidades ----------
     Ventana emergente de verdad, con <dialog> y showModal(). El fondo
     oscurecido, cerrar con Escape, atrapar el foco dentro y devolverlo al
     boton al salir lo hace el navegador solo: aqui unicamente se abre, se
     cierra y se anade el clic en el fondo, que eso si no viene de serie.

     `showModal` esta en todos los navegadores desde 2022. En uno mas viejo
     el boton no haria nada; por eso el texto va escrito en la pagina y no
     se pierde para quien lo lea con un buscador. */
  (function curiosidades() {
    var abridores = document.querySelectorAll('[data-abre]');
    if (!abridores.length) return;

    function abrir(v) {
      if (typeof v.showModal === 'function') v.showModal();
      else v.setAttribute('open', '');       /* reserva para navegadores viejos */
    }

    for (var i = 0; i < abridores.length; i++) {
      (function (boton) {
        boton.addEventListener('click', function () {
          var v = document.getElementById(boton.dataset.abre);
          if (v) abrir(v);
        });
      })(abridores[i]);
    }

    var ventanas = document.querySelectorAll('.cur-ventana');
    for (var j = 0; j < ventanas.length; j++) {
      (function (v) {
        var equis = v.querySelector('[data-cierra]');
        if (equis) equis.addEventListener('click', function () { v.close(); });

        /* clic en el fondo oscurecido. El backdrop no es un elemento al que
           se le pueda escuchar, asi que se mira si el clic cayo fuera de la
           caja: si el <dialog> ocupa toda la pantalla, lo de fuera del
           rectangulo del contenido es el fondo. */
        v.addEventListener('click', function (e) {
          if (e.target !== v) return;
          var c = v.getBoundingClientRect();
          var dentro = e.clientX >= c.left && e.clientX <= c.right &&
                       e.clientY >= c.top && e.clientY <= c.bottom;
          if (!dentro) v.close();
        });
      })(ventanas[j]);
    }
  })();

})();
