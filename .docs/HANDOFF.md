# laOra — traspaso de contexto (29/07/2026)

Documento de traspaso para quien continúe: humano o la siguiente sesión de
Claude. Resume qué existe, dónde vive cada pieza, qué falta y qué está roto.

## 0. Cómo se trabaja aquí

- **Repo**: `Saneas26/laora` en GitHub. Rama de trabajo de esta sesión:
  `main` directamente al final (cada cambio fue rama → PR → merge → verificado
  con `git show origin/main:<archivo>` antes de darlo por hecho).
- **Despliegue**: Cloudflare Pages, no Vercel. `main` = producción
  (`laora.es`), cada rama = preview en `<rama-normalizada>.laora.pages.dev`.
  Sin build: HTML/CSS/JS vanilla, build output = `/`.
- **El trabajo del humano (Óscar) de aquí en adelante**: dar acceso de sesión
  (Chrome logueado) a los paneles que hagan falta — Cloudflare, Supabase,
  Mollie, GitHub si algo no se puede por API. El resto (código, commits,
  PRs, verificación) lo hace el asistente. Antes de tocar un panel externo,
  pregunta cuál hace falta para la tarea concreta; no todos a la vez.

## 1. Accesos y rutas online

| Servicio | Ruta / identificador | Para qué |
|---|---|---|
| **GitHub** | `github.com/Saneas26/laora` | Código fuente, todo el historial |
| **Cloudflare Pages** | proyecto `laora`, dominio `laora.es` (+ `www`) | Hosting. Dashboard: `dash.cloudflare.com` |
| **Supabase** | proyecto **`activala`** (compartido por el grupo), ref `uikanfvigunjhzibnhxf` → `https://uikanfvigunjhzibnhxf.supabase.co` | Base de datos e Edge Functions de laOra (y de otras marcas del grupo, en esquemas separados) |
| **Supabase — esquema** | `laora` (dentro del proyecto `activala`; también existen `activala` y `acumula` como esquemas hermanos, y `public` se deja vacío a propósito) | Tablas `laora.interesados`, `laora.reservas`, vista `laora.reservas_pendientes` |
| **Mollie** | cuenta en `mollie.com` (alta pendiente de verificar del todo) | Pasarela de pago con tarjeta/Bizum automático |
| **Resend** | `resend.com`, dominio verificado `saneas.es` | Envío de los correos de aviso/confirmación |
| **Google Sheet** | `laora-biblioteca-materiales` (hoja "Compras — enlaces") | Solo sourcing de proveedores/materiales — no toca la web en producción |

No hay Vercel propio de laOra: la única URL `.vercel.app` que aparece en el
código es `pordondevoy-saneas.vercel.app`, la app hermana del grupo Saneas
(aparece en el pie como enlace, y es el endpoint que usa `telemetria.js`
para el ping anónimo de visitas).

## 2. Rutas locales del repo (lo importante)

```
/home/user/laora/
├── index.html                 ← LA HOME. Narrativa de 7 Actos + pie. Es "v2" ya publicada como v1.
├── manifiesto.html             "El alma de un automático"
├── materiales.html             Los materiales que se usan
├── privacidad.html             Política de privacidad (actualizada con el flujo de reserva)
├── condiciones-de-venta.html   Términos de venta — TIENE 4 HUECOS SIN RELLENAR (ver §4)
├── reservar.html               Checkout de una reserva (ref + acabado por query string)
├── reserva-recibida.html       Pantalla final tras reservar
├── relojes/
│   └── lo-0X-*.html            Una ficha por modelo (9). Cada una: 4 acabados + botón de reserva
├── assets/
│   ├── css/laora.css           Hoja de estilos de TODO menos los 7 Actos (que van inline en index.html)
│   ├── js/
│   │   ├── laora.js            Nav, animaciones .reveal, formulario interesados, botón de reserva
│   │   ├── precios.js          ÚNICA fuente de precios — ver §4, ahora mismo todo en null
│   │   ├── reservar.js         Checkout completo
│   │   ├── gracias.js          Pantalla final + instrucciones Bizum/transferencia — ver §4
│   │   └── telemetria.js       Ping anónimo de visitas (ya activo, ver §5)
│   └── img/, sonido/           Assets de los 7 Actos y del resto de la web
├── .supabase/                  SQL y Edge Functions (no se sube a laora.es — empieza por punto)
│   ├── estructura-grupo.sql    Esquemas + RLS + grants de todo el grupo (reejecutable)
│   ├── crear-reserva.ts        Edge Function laora-crear-reserva — recalcula precio, guardarraíl
│   ├── mollie-webhook.ts       Edge Function laora-mollie-webhook
│   └── avisar-reserva.ts       Edge Function laora-avisar-reserva
├── .docs/                      Documentación interna (tampoco se sube)
│   ├── HANDOFF.md              ← este documento
│   ├── SUPABASE_PASOS.md       Guía paso a paso de todo lo de Supabase/Mollie
│   ├── CLOUDFLARE_PAGES.md     Guía de despliegue
│   ├── brief-desarrollo.md     Brief de diseño original (a qué reloj homenajea cada modelo)
│   └── sourcing-bitacora.md    Investigación de proveedores
└── _redirects                  Reglas de Cloudflare Pages (bloquea /.docs, /.supabase, rutas viejas)
```

## 3. Qué se ha hecho en esta ventana de contexto (resumen cronológico)

1. **Los 7 Actos** (`v2/index.html`, ahora fusionado en `index.html`): landing
   narrativa completa — Acto I (hero), II (revelación), III (peajes, con foto
   de fondo estilo espía), IV (cierre "lo que no negociamos"), V (proceso de
   preparación + vídeo en overlay, **pendiente el archivo de vídeo real**,
   ver §4), VI (embalaje + Club laOra + botón de descarga de app, **pendiente
   el link real de la app**), VII (cierre "no compras un reloj").
2. **Publicada como home real** (`feat-publica-v2-como-home`): quitado el
   `noindex`, recuperado el SEO, fusionada con partes de la web anterior.
3. **Recortada de nuevo** a petición de Óscar: se quitó la cuadrícula de
   colección y el formulario "avísame", y **todo el WhatsApp de toda la
   web** (nav, CTA de cabecera y pie en las 9 fichas + home + páginas legales;
   se dejó el texto legal de privacidad/condiciones que lo cita como canal de
   contacto).
4. **Traído el flujo de reservas** desde la rama `claude/reservas` (existía
   desde antes, no fusionada): botón "Reservar" por cada uno de los 4
   acabados de cada modelo → checkout → Mollie o Bizum/transferencia manual
   → Edge Functions en Supabase. Guardarraíl de precio verificado: el
   servidor recalcula desde `precios.js` y devuelve 409 si no coincide;
   `laora.reservas` no tiene ningún grant para `anon`.

## 4. Lo que falta / lo que está roto (con ubicación exacta)

**Bloqueantes para poder cobrar de verdad** (ninguno es un bug — el código
los exige a propósito, ver `.docs/SUPABASE_PASOS.md`):
- `assets/js/precios.js` — los 36 precios (9 modelos × 4 acabados) están en
  `precio: null`. Sin precio, el botón de cada acabado cae a "Avísame del
  estreno" en vez de dejar reservar.
- `assets/js/precios.js:117` — `LAORA_ENTREGA = ''`. Sin fecha de entrega
  comprometida tampoco se puede cobrar (por ley, sin fecha pactada hay 30
  días desde el cobro para entregar).
- `condiciones-de-venta.html` — 4 huecos marcados en ámbar sin rellenar:
  domicilio fiscal (línea 44), fecha de entrega (línea 75), teléfono Bizum
  (línea 114), IBAN (línea 115).
- `assets/js/gracias.js:14` — `LAORA_COBRO.bizum` e `.iban` vacíos: sin
  esto el cliente que paga por Bizum/transferencia no ve dónde pagar.
- **Falta la API key de Mollie** (`LAORA_MOLLIE_API_KEY`, secreto en la
  Edge Function) — la pone Óscar, es una credencial.

**Urgente, esto sí es un cabo suelto real ahora que se fusionó a `main`**:
- El secreto `LAORA_WEB_URL` de las Edge Functions de Supabase todavía
  apunta a `https://claude-reservas.laora.pages.dev` (la preview de la rama
  vieja). Con `main` ya fusionado, los enlaces que generen los correos de
  confirmación de reserva van a esa preview, no a `laora.es`. **Hay que
  cambiarlo en Supabase → Edge Functions → Secrets a `https://laora.es`.**
  Necesito sesión de Supabase para esto.

**Anclas muertas** (no rompen nada, simplemente no desplazan a ningún
sitio — quedaron así al quitar secciones de la home a petición de Óscar):
- `/?modelo=X#interesados` — usado por los botones "Avísame del estreno"
  de los 36 acabados sin precio, y por varios `href` sueltos.
- `/#coleccion`, `/#porque`, `/#madrid` — en los `nav` de `materiales.html`,
  `manifiesto.html` y las 9 fichas de reloj.
- Los CTA "Descubre/Ver la colección" del Acto I, IV y VII de la home
  (`/index.html#coleccion`).

Pendiente de decisión de Óscar: si esto se resuelve trayendo de vuelta una
página de colección, o rehaciendo esos enlaces a otro destino.

**Pendiente, mencionado por Óscar pero no entregado todavía**:
- Vídeo real para el overlay del Acto V (`/assets/video/acto5-taller.mp4`
  no existe — el `<video>` usa la foto como poster mientras tanto).
- Enlace real de la app laOra para el botón del Acto VI (ahora mismo
  `href="#"`).

## 5. Analítica — decisión pendiente, no empezada

Óscar pidió trackear: tiempo en página, cuánto se hace scroll, qué reloj se
ve, qué acabado se elige, quién reserva y quién compra. Ya existe algo
mínimo (`telemetria.js`, ping anónimo diario de visitas — no toca esto),
pero el sistema de eventos completo no se ha construido. Quedó en dos
preguntas sin responder:

1. **Herramienta**: ¿Google Analytics 4 (gratis, paneles ya hechos, trae de
   serie tiempo/scroll/esquema de ecommerce, pero cookies → aviso de
   consentimiento en la UE) o ampliar el sistema propio con Supabase (más
   privado, pero hay que construir también los paneles para consultarlo)?
2. Con el carrito ya resuelto (era "compra directa", sin carrito, decisión
   tomada aparte — ver rama `claude/reservas`), ya hay eventos reales que
   trackear: ver acabado, reservar, pagar.

## 6. Cosas que YA no hay que volver a preguntar

- No hay carrito de la compra — es una decisión de diseño, no un olvido
  (comprar un reloj, un acabado, ya está resuelto con la reserva directa).
- No se usa Vercel para el hosting de laOra — es Cloudflare Pages.
- El sitio no usa cookies de terceros ni analítica externa todavía (lo dice
  la propia política de privacidad).
