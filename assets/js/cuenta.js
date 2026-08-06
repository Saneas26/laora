/* ============================================================
   laOra · CUENTA Y CLUB
   ------------------------------------------------------------
   Entrar sin contraseña: se pone el correo, llega un enlace y se
   entra. No se guarda ninguna contraseña, así que no hay ninguna que
   se pueda perder ni que haya que custodiar.

   Habla con Supabase Auth por HTTP, sin librerías. Las dos claves de
   abajo son PÚBLICAS por diseño —van en el navegador de cualquiera— y
   no dan acceso a nada por sí solas: quien manda es la política de
   filas de la base. La clave de servicio NUNCA aparece aquí.
   ============================================================ */
(function () {
  'use strict';

  /* ---------- lo único que hay que rellenar ----------
     Se sacan del panel de Supabase, en Project Settings → API:
       URL      → «Project URL»
       ANONIMA  → «anon public»
     Mientras estén vacías, la pantalla lo dice en vez de fallar. */
  var URL = '';
  var ANONIMA = '';

  var form = document.querySelector('[data-form]');
  var campo = document.querySelector('[data-correo]');
  var boton = document.querySelector('[data-enviar]');
  var aviso = document.querySelector('[data-aviso]');
  var hecho = document.querySelector('[data-hecho]');
  if (!form) return;

  function decir(texto, malo) {
    aviso.textContent = texto;
    aviso.hidden = !texto;
    aviso.classList.toggle('cu-error', !!malo);
  }

  /* Si vuelve del enlace del correo, Supabase deja la sesión en el
     fragmento de la dirección. Con eso ya está dentro. */
  (function volviendo() {
    if (!location.hash || location.hash.indexOf('access_token') < 0) return;
    var datos = {};
    location.hash.replace(/^#/, '').split('&').forEach(function (p) {
      var t = p.split('='); datos[t[0]] = decodeURIComponent(t[1] || '');
    });
    if (datos.access_token) {
      try { localStorage.setItem('laora.sesion', JSON.stringify(datos)); } catch (e) {}
      history.replaceState(null, '', location.pathname);
      form.hidden = true;
      hecho.hidden = false;
      hecho.querySelector('[data-hecho-texto]').textContent =
        'Ya estás dentro. Tu cuenta queda abierta en este navegador.';
    } else if (datos.error_description) {
      decir(datos.error_description, true);
    }
  })();

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var correo = (campo.value || '').trim();
    if (!correo || correo.indexOf('@') < 1) { decir('Escribe un correo válido.', true); return; }

    if (!URL || !ANONIMA) {
      decir('Falta configurar el acceso: las dos claves de Supabase todavía no están puestas en assets/js/cuenta.js.', true);
      return;
    }

    boton.disabled = true;
    decir('Enviando…');

    fetch(URL.replace(/\/$/, '') + '/auth/v1/otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'apikey': ANONIMA },
      body: JSON.stringify({
        email: correo,
        create_user: true,
        options: { email_redirect_to: location.origin + '/cuenta' }
      })
    }).then(function (r) {
      if (!r.ok) throw new Error('respuesta ' + r.status);
      form.hidden = true;
      hecho.hidden = false;
      hecho.querySelector('[data-hecho-texto]').textContent =
        'Te hemos enviado un enlace a ' + correo + '. Ábrelo desde este mismo aparato y entrarás sin contraseña.';
    }).catch(function () {
      boton.disabled = false;
      decir('No hemos podido enviar el enlace. Inténtalo dentro de un momento.', true);
    });
  });
})();
