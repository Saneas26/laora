/* ============================================================
   laOra · LA SESIÓN
   ------------------------------------------------------------
   Lo comparten la cuenta, el carrito y la app. Aquí no se pinta
   nada: solo se sabe quién eres y se consigue un token válido.

   Cómo entra la gente: se pide el correo y llega un correo con DOS
   caminos. Si pulsa el enlace, al volver Supabase deja los tokens en
   el fragmento de la dirección (`#access_token=…`) y se guardan aquí.
   Si escribe el código de seis cifras, se canjea con `entrarConCodigo`
   y se guarda igual.

   El código existe porque el enlace falla más de lo que parece: vale
   una sola vez —y hay gestores de correo que lo abren solos para
   comprobarlo, gastándolo— y solo deja la sesión en el navegador donde
   se abre, así que quien lee el correo en el móvil mientras compraba
   en el ordenador se queda fuera.

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

  /* ---------- ENTRAR CON EL CÓDIGO ----------
     El enlace del correo vale UNA vez y solo entra en el navegador
     donde se abre: si el gestor de correo lo previsualiza, se gasta; y
     si se lee en el móvil mientras se compraba en el ordenador, la
     sesión se queda en el móvil. El código no tiene ese problema: se
     escribe donde uno esté.

     Supabase pide que el `type` coincida con el motivo por el que se
     mandó el código, y desde fuera no se sabe si el correo era de alta
     o de entrada. Así que se prueban los tres, en orden. */
  function entrarConCodigo(correo, codigo) {
    var tipos = ['email', 'magiclink', 'signup'];

    function intento(i) {
      if (i >= tipos.length) throw new Error('codigo');
      return fetch(URL_SB + '/auth/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: ANONIMA },
        body: JSON.stringify({
          type: tipos[i],
          email: String(correo || '').trim(),
          token: String(codigo || '').replace(/\s/g, '')
        })
      }).then(function (r) {
        if (!r.ok) return intento(i + 1);
        return r.json().then(function (s) {
          if (!s || !s.access_token) return intento(i + 1);
          return guardar(s);
        });
      });
    }
    return intento(0);
  }

  /* ---------- ENTRAR CON LA LLAVE DEL CORREO ----------
     El botón del correo ya no lleva a la puerta de Supabase: lleva a
     `/entrar`, una página de la casa, y es la página quien canjea la
     llave cuando EL CLIENTE pulsa.

     POR QUÉ. El enlace directo se gasta al primer GET, y Outlook y
     Hotmail tienen un escáner que abre los enlaces de cada correo antes
     de entregarlo: la llave llegaba muerta, y con ella el código, que es
     la misma. Le pasó a Óscar el 29/08/2026 dándose de alta desde otro
     teléfono: «el botón no hace nada y el código tampoco». Un escáner
     carga una página pero no pulsa botones, así que la llave sobrevive.

     `tipo` es el motivo del correo (magiclink, signup…). Igual que en
     `entrarConCodigo`, desde fuera no se sabe seguro cuál era, así que
     si el que viene falla se prueban los demás. */
  function entrarConLlave(llave, tipo) {
    var tipos = [tipo, 'magiclink', 'signup', 'email'].filter(function (t, i, a) {
      return t && a.indexOf(t) === i;
    });

    function intento(i) {
      if (i >= tipos.length) throw new Error('llave');
      return fetch(URL_SB + '/auth/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: ANONIMA },
        body: JSON.stringify({ type: tipos[i], token_hash: String(llave || '').trim() })
      }).then(function (r) {
        if (!r.ok) return intento(i + 1);
        return r.json().then(function (s) {
          if (!s || !s.access_token) return intento(i + 1);
          return guardar(s);
        });
      });
    }
    return intento(0);
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

  /* ESCRIBIR es distinto de leer. `consultar` se traga los errores y
     devuelve null, que para leer vale —no hay datos y ya está— pero
     para escribir es peligroso: no se distingue «guardado» de «no se
     ha podido», y se le diría a alguien que sus datos están a salvo
     cuando no lo están. Esta revienta si algo va mal. */
  function escribir(tabla, opciones) {
    opciones = opciones || {};
    return token().then(function (t) {
      if (!t) throw new Error('sin sesión');
      var cab = {
        apikey: ANONIMA,
        Authorization: 'Bearer ' + t,
        'Accept-Profile': 'laora',
        'Content-Profile': 'laora',
        'Content-Type': 'application/json',
        Prefer: 'return=minimal'
      };
      Object.keys(opciones.headers || {}).forEach(function (k) { cab[k] = opciones.headers[k]; });
      return fetch(URL_SB + '/rest/v1/' + tabla, {
        method: opciones.method || 'POST',
        headers: cab,
        body: opciones.body
      });
    }).then(function (r) {
      if (!r.ok) {
        return r.text().then(function (t) {
          throw new Error('la base ha dicho que no (' + r.status + '): ' + t.slice(0, 120));
        });
      }
      return true;
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
    entrarConCodigo: entrarConCodigo,
    entrarConLlave: entrarConLlave,
    consultar: consultar,
    escribir: escribir,
    salir: salir
  };
})(window);
