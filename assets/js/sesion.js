/* ============================================================
   laOra · LA SESIÓN
   ------------------------------------------------------------
   Lo comparten la cuenta, el carrito y la app. Aquí no se pinta
   nada: solo se sabe quién eres y se consigue un token válido.

   Cómo entra la gente: se pide el correo, llega un enlace, y al
   volver Supabase deja los tokens en el fragmento de la dirección
   (`#access_token=…`). Se guardan en este navegador y ya está.

   EL TOKEN CADUCA A LA HORA. Por eso está `token()`: mira si le
   queda vida y, si no, lo renueva con el `refresh_token` antes de
   devolverlo. Quien lo use no tiene que saber nada de esto.
   ============================================================ */
(function (global) {
  'use strict';

  var URL_SB = 'https://uikanfvigunjhzibnhxf.supabase.co';
  var ANONIMA = 'sb_publishable_1eLOM22REKcIJyHe36W_4Q_1Z3eyRam';
  var LLAVE = 'laora.sesion';

  function leer() {
    try { return JSON.parse(localStorage.getItem(LLAVE) || 'null'); }
    catch (e) { return null; }
  }

  function guardar(s) {
    if (!s || !s.access_token) return null;
    /* `expires_in` viene en segundos desde ahora; se convierte a una
       hora absoluta para poder comprobarla más tarde. */
    if (!s.expires_at && s.expires_in) {
      s.expires_at = Math.floor(Date.now() / 1000) + Number(s.expires_in);
    }
    try { localStorage.setItem(LLAVE, JSON.stringify(s)); } catch (e) {}
    return s;
  }

  function salir() {
    try { localStorage.removeItem(LLAVE); } catch (e) {}
  }

  /* Si venimos del enlace del correo, recoge los tokens y limpia la
     dirección para que no se queden a la vista ni en el historial.
     Devuelve true si acaba de entrar. */
  function recoger() {
    if (!global.location.hash || global.location.hash.indexOf('access_token') < 0) return false;
    var datos = {};
    global.location.hash.replace(/^#/, '').split('&').forEach(function (p) {
      var t = p.split('=');
      datos[t[0]] = decodeURIComponent(t[1] || '');
    });
    if (!datos.access_token) return false;
    guardar(datos);
    history.replaceState(null, '', global.location.pathname + global.location.search);
    return true;
  }

  function renovar(s) {
    return fetch(URL_SB + '/auth/v1/token?grant_type=refresh_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: ANONIMA },
      body: JSON.stringify({ refresh_token: s.refresh_token })
    }).then(function (r) {
      if (!r.ok) throw new Error('no se pudo renovar');
      return r.json();
    }).then(function (nueva) {
      return guardar(nueva);
    }).catch(function () {
      /* El refresh también caduca (o se ha usado en otro sitio). Se
         borra: es preferible pedir el correo otra vez a dejar una
         sesión que parece viva y no lo está. */
      salir();
      return null;
    });
  }

  /* El token listo para usar, o null si hay que volver a entrar.
     Renueva solo si le queda menos de un minuto. */
  function token() {
    var s = leer();
    if (!s || !s.access_token) return Promise.resolve(null);
    var caduca = Number(s.expires_at || 0);
    if (caduca && (caduca - 60) > Math.floor(Date.now() / 1000)) {
      return Promise.resolve(s.access_token);
    }
    if (!s.refresh_token) { salir(); return Promise.resolve(null); }
    return renovar(s).then(function (n) { return n ? n.access_token : null; });
  }

  /* Quién es, según Supabase. Null si el token ya no vale. */
  function quienSoy() {
    return token().then(function (t) {
      if (!t) return null;
      return fetch(URL_SB + '/auth/v1/user', {
        headers: { Authorization: 'Bearer ' + t, apikey: ANONIMA }
      }).then(function (r) { return r.ok ? r.json() : null; })
        .catch(function () { return null; });
    });
  }

  /* Manda el enlace de entrada. `vuelveA` es la página a la que
     volver: así quien está comprando vuelve al carrito y no a la
     cuenta, y no pierde lo que había elegido. */
  function pedirEnlace(correo, vuelveA) {
    return fetch(URL_SB + '/auth/v1/otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: ANONIMA },
      body: JSON.stringify({
        email: correo,
        create_user: true,
        options: { email_redirect_to: global.location.origin + (vuelveA || '/cuenta') }
      })
    }).then(function (r) {
      if (!r.ok) throw new Error('respuesta ' + r.status);
      return true;
    });
  }

  /* Una llamada a la base con la sesión puesta. `tabla` puede llevar
     el filtro de PostgREST: `socios?select=*`. */
  function consultar(tabla, opciones) {
    opciones = opciones || {};
    return token().then(function (t) {
      if (!t) return null;
      var cab = {
        apikey: ANONIMA,
        Authorization: 'Bearer ' + t,
        'Accept-Profile': 'laora',
        'Content-Profile': 'laora',
        'Content-Type': 'application/json'
      };
      Object.keys(opciones.headers || {}).forEach(function (k) { cab[k] = opciones.headers[k]; });
      return fetch(URL_SB + '/rest/v1/' + tabla, {
        method: opciones.method || 'GET',
        headers: cab,
        body: opciones.body
      }).then(function (r) { return r.ok ? r.json() : null; })
        .catch(function () { return null; });
    });
  }

  global.laoraSesion = {
    URL: URL_SB,
    ANONIMA: ANONIMA,
    recoger: recoger,
    hay: function () { return !!(leer() || {}).access_token; },
    token: token,
    quienSoy: quienSoy,
    pedirEnlace: pedirEnlace,
    consultar: consultar,
    salir: salir
  };
})(window);
