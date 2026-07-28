/* ============================================================
   laOra · JS común: nav, aparición, y formulario de interesados.
   Patrón del grupo: la tabla es INSERT-ONLY en Supabase y el aviso
   por correo sale de una Edge Function con el destino en secreto.
   La clave publishable es pública por diseño; la seguridad la pone RLS.
   ============================================================ */

/* Rellenar al crear el proyecto Supabase de laOra (SUPABASE_PASOS.md).
   Mientras estén vacíos, el formulario deriva a WhatsApp. */
var LAORA_SUPABASE_URL = '';
var LAORA_SUPABASE_KEY = '';
var LAORA_WHATSAPP = '34689806987';

/* Borde de la barra al hacer scroll */
(function () {
  var nav = document.getElementById('nav');
  if (!nav) return;
  addEventListener('scroll', function () {
    nav.classList.toggle('scrolled', scrollY > 10);
  }, { passive: true });
})();

/* Aparición de secciones */
(function () {
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: .14, rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
})();

/* Preselección de modelo si se llega con /?modelo=LO-01#interesados */
(function () {
  var sel = document.getElementById('modelo');
  if (!sel) return;
  var m = ((location.search + location.hash).split('modelo=')[1] || '').slice(0, 5);
  if (!m) return;
  for (var i = 0; i < sel.options.length; i++) {
    if (sel.options[i].value.indexOf(m) === 0) { sel.selectedIndex = i; break; }
  }
})();

/* Selector de acabados (brief §6): chips T1…T4 + Eclipse que pintan el panel.
   Cada landing define window.LAORA_ACABADOS antes de cargar este módulo.
   El desglose de coste por componente queda con su hueco preparado hasta
   que Compras y el CFO lo cierren. */
(function () {
  var datos = window.LAORA_ACABADOS;
  var chips = document.getElementById('selectorChips');
  var panel = document.getElementById('panelAcabado');
  if (!datos || !chips || !panel) return;

  function pinta(i) {
    var a = datos[i];
    panel.className = 'panel-acabado' + (a.eclipse ? ' panel-eclipse' : '');
    panel.innerHTML =
      '<span class="pa-tier">' + a.tier + '</span>' +
      '<h3>«' + a.nombre + '»</h3>' +
      '<p>' + a.texto + '</p>' +
      '<p class="pa-precio">' + a.precio + '</p>' +
      '<p class="pa-hueco">Desglose de coste por componente: se publica aquí, pieza a pieza, ' +
      'en cuanto Compras y el CFO lo cierren. La transparencia no es un adorno: es el producto.</p>';
    Array.prototype.forEach.call(chips.children, function (c, j) {
      c.classList.toggle('activo', j === i);
    });
  }

  datos.forEach(function (a, i) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'chip' + (a.eclipse ? ' eclipse' : '');
    b.textContent = a.tier + ' · ' + a.nombre;
    b.addEventListener('click', function () { pinta(i); });
    chips.appendChild(b);
  });
  pinta(window.LAORA_ACABADO_INICIAL || 0);
})();

/* «La versión larga» plegada bajo el cabreo: Leer más despliega y
   el botón Ocultar del final vuelve a plegar. */
(function () {
  var btn = document.getElementById('largaBtn');
  var resto = document.getElementById('largaResto');
  var ocultar = document.getElementById('ocultarBtn');
  if (!btn || !resto) return;
  function pliega(estado) {
    resto.hidden = estado;
    btn.textContent = estado ? 'Leer más +' : 'Leer menos −';
    if (estado) btn.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
  btn.addEventListener('click', function () { pliega(!resto.hidden); });
  if (ocultar) ocultar.addEventListener('click', function () { pliega(true); });
})();

/* Formulario de interesados */
(function () {
  var form = document.getElementById('formInteresados');
  if (!form) return;

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();

    /* honeypot: si el campo oculto viene relleno, es un bot y se descarta */
    if (form.c_web && form.c_web.value) return;

    var datos = {
      nombre:   form.nombre.value.trim(),
      email:    form.email.value.trim(),
      whatsapp: form.whatsapp.value.trim(),
      modelo:   form.modelo ? form.modelo.value : '',
      mensaje:  form.mensaje ? form.mensaje.value.trim() : ''
    };
    if (!datos.nombre) { form.nombre.focus(); return; }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(datos.email)) { form.email.focus(); return; }

    var boton = form.querySelector('button[type="submit"]');
    boton.disabled = true;

    function hecho() {
      form.style.display = 'none';
      var ok = document.getElementById('formOk');
      ok.style.display = 'block';
      var nombreOk = document.getElementById('okName');
      if (nombreOk) nombreOk.textContent = datos.nombre.split(' ')[0];
    }
    function porWhatsApp() {
      var texto = 'Hola laOra, quiero que me aviséis del estreno.' +
        (datos.modelo ? ' Me interesa el ' + datos.modelo + '.' : '') +
        ' Soy ' + datos.nombre + ' (' + datos.email + ').';
      location.href = 'https://api.whatsapp.com/send?phone=' + LAORA_WHATSAPP +
        '&text=' + encodeURIComponent(texto);
      boton.disabled = false;
    }

    if (!LAORA_SUPABASE_URL || !LAORA_SUPABASE_KEY) { porWhatsApp(); return; }

    fetch(LAORA_SUPABASE_URL + '/rest/v1/interesados', {
      method: 'POST',
      headers: {
        apikey: LAORA_SUPABASE_KEY,
        Authorization: 'Bearer ' + LAORA_SUPABASE_KEY,
        'Content-Type': 'application/json',
        Prefer: 'return=minimal'
      },
      body: JSON.stringify(datos)
    }).then(function (r) {
      if (r.status === 201) hecho(); else porWhatsApp();
    }).catch(porWhatsApp);
  });
})();
