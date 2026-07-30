# laOra — traspaso completo

**Última actualización: 29/07/2026.** Todo lo de este documento está comprobado
contra producción ese día, no escrito de memoria.

---

## 0. Cómo se trabaja aquí

**Lo hace todo Claude Code.** Óscar no escribe código, no hace commits y no toca
paneles salvo cuando se le pide expresamente. Su trabajo es: dar acceso de sesión
en **Google Chrome** (deja la sesión abierta y logueada) y decidir. El resto
—código, imágenes, commits, PRs, despliegues y verificación— lo hace el asistente.

**Nunca nos rendimos.** Si algo falla, se busca la causa hasta el fondo: el
segundo intento no es repetir lo mismo, es entender por qué falló el primero.
En esta ventana, tres problemas se resolvieron solo porque no se dio nada por
imposible: el volcado que se colgaba (era un diálogo invisible), los documentos
internos publicados (hicieron falta tres mecanismos hasta dar con el que
funciona) y las Edge Functions con un 502 mudo (faltaba un grant que no
documenta nadie).

**Nunca se dice «hecho» sin haberlo visto.** Cada afirmación se comprueba: `curl`
contra producción, captura del navegador o consulta a la base. Si no se ha
podido comprobar, se dice.

**No se inventa nada que pueda cobrar dinero, prometer un plazo o afirmar un
dato legal.** Antes se pregunta. Un precio inventado o una garantía mal puesta no
es un error de diseño: es un problema con un cliente real.

**Se avisa de lo que se rompe por el camino**, aunque no lo haya pedido nadie y
aunque quede feo. Un enlace muerto, un documento interno publicado o una foto que
contradice al texto se cuentan, no se tapan.

### El ciclo
Rama → preview → «fusiona» de Óscar → `main` → verificación en producción.
Cuando Óscar dice «encárgate tú», se trabaja directo sobre `main` y se verifica
igual. **Hay otra ventana trabajando en el mismo repo**: antes de subir, siempre
`git pull`; si el push se rechaza, mezclar y comprobar que no se pisa nada.

---

## 1. Plataformas: qué hay en cada una

### GitHub — `github.com/Saneas26/laora`
Todo el código y el historial. `main` es producción.

**Ramas que ya no valen para nada** (se pueden borrar): `claude/acabados-solares`
(obsoleta, main la adelantó por la izquierda), `claude/reservas` (ya fusionada),
`claude/brief-v3`, `claude/copy-v31`, `claude/fotos`, `claude/leer-mas`,
`claude/trinchera`, `claude/web-laora`, y una veintena de `feat-*` / `fix-*`
ya fusionadas.

**Ojo:** cada rama publica preview pública en `<rama>.laora.pages.dev` con su
propio `_redirects`. Una rama vieja puede estar filtrando documentos internos.

### Cloudflare Pages — **NO es Vercel**
Proyecto `laora`, dominio `laora.es` (+ `www`). Panel: `dash.cloudflare.com`.

- Sin build: HTML/CSS/JS vanilla. **Build output directory: `/`** — todo el repo
  se publica tal cual.
- `main` = producción. Cada rama = preview automática.
- **`vercel.json` y `.vercelignore` no hacen absolutamente nada aquí.** Se
  intentaron y se borraron. Lo único que funciona es `_redirects`.
- La caché de borde tarda y es **inconsistente entre nodos**: justo después de
  subir, unas peticiones dan lo nuevo y otras lo viejo. No es un fallo del
  despliegue. Hay que sondear hasta varias lecturas seguidas correctas.

### Supabase — proyecto **`activala`**, ref `uikanfvigunjhzibnhxf`
`https://uikanfvigunjhzibnhxf.supabase.co` · organización **Saneas**, plan **Pro**.

**Regla del grupo (decisión de Óscar, 29/07/2026): DOS proyectos y ni uno más.**
- `saneas-app` → **aislado**, solo Saneas. No se toca desde aquí.
- `activala` → **compartido** por el resto de marcas.

Comparten instancia pero **no comparten tablas**: un esquema de Postgres por marca.

| Esquema | Contenido |
|---|---|
| `activala` | `interesados` (venía de `public`, nunca llegó a conectarse) |
| `laora` | `interesados`, `reservas`, vista `reservas_pendientes` |
| `acumula` | reservado, vacío. Acumula sigue en su proyecto Free aparte |
| `public` | **vacío a propósito** |

Guion reejecutable: `.supabase/estructura-grupo.sql`.

**Edge Functions desplegadas** (las de laOra con prefijo, todas con «Verify JWT»
DESACTIVADO):

| Función | Fichero | Quién la llama |
|---|---|---|
| `avisar-interesado` | — | **es de activala, NO tocar** |
| `laora-crear-reserva` | `.supabase/crear-reserva.ts` | la web |
| `laora-mollie-webhook` | `.supabase/mollie-webhook.ts` | Mollie |
| `laora-avisar-reserva` | `.supabase/avisar-reserva.ts` | trigger de la base |

**Secretos:** `LAORA_WEB_URL` = `https://laora.es` ✅ · `RESEND_API_KEY` ✅ ·
`INTERESADOS_EMAIL` ✅ (los dos últimos compartidos con activala) ·
**`LAORA_MOLLIE_API_KEY` FALTA** — la pone Óscar, es una credencial.

Clave publicable (va en el navegador, es pública por diseño):
`sb_publishable_1eLOM22REKcIJyHe36W_4Q_1Z3eyRam`.

### Mollie — la pasarela elegida
Cuenta pendiente de dar de alta y verificar. Se eligió por el pago partido.
Junto a ella, **Bizum y transferencia a mano**, sin comisión.

### Resend — correos
Dominio verificado `saneas.es`. Se envía desde `laOra <laora@saneas.es>`.

### Google Drive — material gráfico
Carpeta **`laOra_Material`**, id `1L7BU1QS0pBC9qRhZGrrlXSsrRdJgFcU2`, en la cuenta
**`oscar.laora@gmail.com`** (en Chrome, el perfil `/u/2/`).

**El conector de Drive de Claude está en OTRA cuenta** (`oscarbelloso10@`): solo
ve lo que esté dentro de esa carpeta compartida. Si un fichero no aparece, casi
siempre es que está fuera de ella, no que no exista. Comprobarlo abriendo Drive
en el Chrome de Óscar, que es la fuente fiable.

Dentro hay mezclados **renders de producto** y **bocetos de web**. No se
distinguen por el nombre: hay que abrirlos.
- Renders buenos: `lunar`, `cero_cero`, `bauhaus`, `precisa`, `trinchera`,
  `ocho_lados`, `Bitacora_Front`, `tortuga`, `pressage` (que es el **Cóctel**).
- Bocetos de web: `coleccion.png`, `bitacora_landing1/2/3.png`,
  `Bitacora_extra.png`, `bitacora_extra2/3.png`, `Bitacora_lateral_Derecho.png`.
- Sin usar todavía: `hora_cero.png`, `coctel.png` (ambiente con copa),
  `lunar_planeta.png`, `cero_cero_acto3.png`, `lunar_acto4.png`, `acto2/3/5/6/7.png`.

---

## 2. El repo, carpeta por carpeta

```
~/Sites/laora/
├── index.html                   LA HOME. Narrativa de 7 Actos, CSS inline
├── coleccion.html               La colección: hero, filosofía, los nueve, cierre
├── manifiesto.html              «El alma de un automático»
├── materiales.html              Los materiales y lo que se rechaza
├── privacidad.html              RGPD (CSS propio inline, no usa laora.css)
├── condiciones-de-venta.html    Contrato de venta — 4 HUECOS SIN RELLENAR
├── reservar.html                Checkout de reserva con señal del 25 %
├── reserva-recibida.html        Pantalla final de la reserva
├── carrito.html                 Carrito (nuevo, 29/07)
├── relojes/
│   ├── lo-02-cero-cero.html     ┐
│   ├── lo-03-bauhaus.html       │  siete fichas con el formato viejo
│   ├── lo-04-precisa.html       │  (tabla de cuatro acabados)
│   ├── lo-05-trinchera.html     │
│   ├── lo-06-ocho-lados.html    │
│   ├── lo-08-tortuga.html       │
│   ├── lo-09-coctel.html        ┘
│   ├── lo-07-bitacora.html      ← FORMATO NUEVO, el del boceto. Tres versiones.
│   └── lo-01-lunar.html         ← FORMATO NUEVO con los CUATRO acabados.
│                                  Es la plantilla para las siete que faltan.
├── assets/
│   ├── css/laora.css            Estilos de todo menos la home y las páginas nuevas
│   ├── css/ficha.css            LAS SIETE BANDAS de las fichas nuevas, compartida
│   ├── js/
│   │   ├── laora.js             Nav, .reveal, formulario, botón por acabado
│   │   ├── precios.js           ÚNICA FUENTE DE PRECIOS. Manda sobre todo
│   │   ├── carrito.js           Cesta en localStorage + contador
│   │   ├── reservar.js          Checkout de la señal del 25 %
│   │   ├── gracias.js           Pantalla final + datos de Bizum/IBAN
│   │   └── telemetria.js        Ping anónimo de visitas (ya activo)
│   ├── img/
│   │   ├── relojes/lo-0X.jpg    Foto de cada ficha
│   │   ├── relojes/col-0X.jpg   Los nueve renders nuevos, 3:4 sobre negro
│   │   ├── bitacora/            hero, hero-movil, frontal, ancha,
│   │   │                        fondo-visto y lume (recortadas del boceto)
│   │   ├── acto*.jpg            Fotos de los 7 Actos de la home
│   │   └── taller-madrid.jpg    acto5 recortada, SIN el botón de reproducir
│   └── sonido/clic-brazalete.wav
├── .docs/                       INTERNO, no se publica
│   ├── HANDOFF.md               ← este documento
│   ├── SUPABASE_PASOS.md        Guía de Supabase y Mollie, paso a paso
│   ├── CLOUDFLARE_PAGES.md      Guía de despliegue
│   ├── README-interno.md        README ampliado
│   ├── brief-desarrollo.md      Brief original — DICE QUÉ RELOJ IMITA A CUÁL
│   ├── copy-web.md              Copy de la v1
│   ├── sourcing-bitacora.md     125 proveedores con precio y enlace
│   ├── volcar-compras-al-sheet.gs  Apps Script del volcado al Sheet
│   └── hero-mockup.html
├── .supabase/                   INTERNO, no se publica
│   ├── estructura-grupo.sql     Esquemas, permisos y RLS de todo el grupo
│   ├── crear-reserva.ts         Edge Function: el guardarraíl del precio
│   ├── mollie-webhook.ts        Edge Function: confirmación de pago
│   ├── avisar-reserva.ts        Edge Function: los dos correos
│   ├── interesados.sql          SQL viejo del formulario
│   └── avisar-interesado.ts     Función de activala, como referencia
├── _redirects                   Reglas de Cloudflare Pages
├── README.md                    Público, sin nada interno
└── manifest.json, apple-touch-icon.png, .gitignore
```

**Regla de oro del repo: todo lo que no sea la web pública empieza por punto.**
No porque Pages lo oculte —no lo hace—, sino como convenio para saber de un
vistazo qué NO debe salir, y para que `_redirects` lo corte de un plumazo.

---

## 3. Por dónde vamos

### Funcionando y verificado en producción
- **La home** de 7 Actos.
- **La colección** (`/coleccion.html`) con los nueve renders nuevos.
- **La ficha de la Bitácora** (`/relojes/lo-07-bitacora.html`) con el formato
  nuevo: siete bandas, configurador y botón de carrito.
- **El carrito**: añade, cuenta, suma y resta cantidades, total.
- **Estructura de Supabase** con un esquema por marca y RLS.
- **Las tres Edge Functions** desplegadas y probadas.
- **El guardarraíl del precio**: intentar pagar 1 € por un reloj de 299 → 409.
  Escribir en `laora.reservas` desde el navegador → 401.
- **`.docs` y `.supabase` cortados** en producción.
- **Legal**: garantía de 3 años en toda la web, mineral K1 en vez de «Hardlex»,
  turquesa en vez de «Tiffany».

### A medias
- **Siete fichas con el formato viejo.** Ya están en el nuevo la Bitácora y el
  Lunar. Lo que hay que saber para hacer las otras siete:
  - Las siete bandas viven en **`assets/css/ficha.css`**, compartida. Se sacaron
    del `<style>` en línea de la Bitácora, que ahora también la usa. **No volver
    a meter CSS en línea en una ficha**: se arregla una vez y valen las nueve.
  - El prefijo sigue siendo **`b-`** (nació en la Bitácora). No se renombró para
    no tocar un marcado ya verificado en producción. Léase «b- = banda de ficha».
  - Para cuatro acabados: `class="b-tres b-cuatro"` en la retícula, `b-cima` en
    la columna de Eclipse, y `b-seis` en `.b-iconos` si son seis iconos.
  - **Precios y horquillas los pinta el JS desde `precios.js`**, no van a mano en
    el HTML como en la Bitácora. Cuando Óscar cierre un precio, la ficha se
    actualiza sola. Probado: con precio, el botón vende y la línea entra bien en
    el carrito; sin precio, el botón queda muerto y el carrito no recibe nada.
  - **Una sola foto por banda de versiones**, no una por columna (decisión de
    Óscar del 29/07). Solo hay un render por modelo: repetirlo no enseñaba nada.
  - **El configurador solo elige el acabado.** Los desplegables de esfera y de
    extras se quedan puestos, cada uno con una única posibilidad y sin
    alternativas: cada modelo se hace en una sola esfera y no lleva extras.
    Es decisión de Óscar del 30/07 y **pisa al boceto**, que enseñaba tres
    esferas y una correa de piel de +25 €. En la Bitácora la correa era además
    imposible: su brazalete va unido a la caja. Añadir una opción el día que
    exista = añadir un `<option>` con su `data-precio`, nada más.
  - En «lo que llevan todas» **solo va lo que es común a TODOS los acabados** del
    modelo. En el Lunar el zafiro no lo es (Alba lleva mineral K1), así que no
    está. Mirar la tabla de la ficha vieja antes de copiar los iconos.
  - Los renders de `assets/img/relojes/` son **cuadrados y con fondo propio**
    rgb(29,29,31): la banda del héroe lleva `b-cuadrada`, que iguala el fondo. La
    máscara radial de la colección **no sirve** aquí (el brazalete ocupa el alto
    entero y el degradado se come sus extremos).
- **El pago del carrito no existe.** El checkout que hay (`reservar.html`) se hizo
  para comprar un reloj suelto con señal del 25 %; ahora la compra es por cesta.
  Hay que rehacer ese paso.
- **Pie del grupo desalineado**: la otra ventana añadió la tarjeta de Saneas.es a
  siete páginas; `privacidad.html` y ocho fichas siguen con el pie viejo.

### Bloqueado, esperando a Óscar
1. **`LAORA_ENTREGA` está vacía** en `precios.js`. Sin fecha de entrega
   comprometida no se puede cobrar, y el código lo impide a propósito. Hoy
   `laora-crear-reserva` responde literalmente *«no hay fecha de entrega
   comprometida»*. **Es lo único que separa a la Bitácora de poder vender.**
2. **33 de 36 precios siguen vacíos.** Solo LO-07: Alba 250, Levante 320, Cenit 420.
3. **Cuatro huecos en `condiciones-de-venta.html`**: domicilio fiscal, fecha de
   entrega, teléfono de Bizum e IBAN. Salen marcados en ámbar en la propia web.
4. **`LAORA_COBRO` vacío** en `gracias.js`: sin Bizum ni IBAN, quien elija pago
   manual no sabe dónde pagar.
5. **Alta en Mollie y su clave.** Es una credencial: la pone Óscar.
6. **Dos de las cuatro fotos que pedía el boceto siguen sin existir**: el
   cuaderno con el compás y el dibujo técnico de medidas. El **fondo visto** y
   la **toma del lume** ya están puestas, recortadas del propio boceto
   (`.docs` no las guarda; están en `assets/img/bitacora/`).
   **Ojo con la resolución**: `bitacora_landing3.png` mide 1024×1536 en origen,
   así que lo que se recorta de él es pequeño — `fondo-visto.jpg` sale a 599×225
   y `lume.jpg` a 285×190. Se ven bien al tamaño al que se enseñan, pero son 1×:
   en pantalla retina no son nítidas. **Si existen los renders originales
   sueltos, sustituirlas.** Las otras dos no se pueden recortar: el cuaderno se
   funde con el texto con un degradado y del dibujo técnico solo quedarían
   ~150×125 px de línea fina.
7. **Las medidas del Lunar** (diámetro, grosor, asas, ancho de correa). Salen en
   ámbar con `[POR CERRAR]` en su ficha, como los huecos de las condiciones de
   venta. No se ponen a ojo: las confirma el fabricante de la caja.
   **Las medidas del boceto son las de la Bitácora** (~40 mm, ~9,5–11 mm,
   ~47 mm, ~22 mm) y ya estaban en su ficha: no sirven para el Lunar.

### El siguiente paso
**Llevar las siete fichas restantes al formato nuevo.** El Lunar es la plantilla
para las de cuatro acabados: misma estructura de siete bandas, mismo
configurador, mismos nombres de acabado, y el CSS ya está en `ficha.css`.

**El formulario de aviso de estreno NO se pone en marcha** — decisión de Óscar
del 30/07/2026, preguntado expresamente. En toda la web no queda ninguno:
`laora.js` conserva el manejador y `laora.interesados` existe y acepta INSERT
(comprobado con un POST a PostREST), pero el formulario se quitó de la home.
Con 33 de 36 acabados sin precio, eso significa que hoy no hay forma de que un
interesado deje su correo, y está aceptado. Las fichas nuevas dicen la verdad
—«todavía no está a la venta»— en vez de dar un botón que no lleva a ningún
sitio. **No volver a proponerlo salvo que él lo saque.**

En paralelo, y en cuanto Óscar dé los datos: rellenar fecha de entrega y los
cuatro huecos legales. Con eso la Bitácora ya puede vender.

Después: rehacer el paso de pago para que salga del carrito.

---

## 4. Errores que NO hay que volver a cometer

Todos ocurrieron en esta ventana. Están aquí para que no se repitan.

### Despliegue y plataforma
1. **Esto no es Vercel.** Se perdió tiempo con `.vercelignore` y `vercel.json`.
   Es **Cloudflare Pages** y lo único que manda es `_redirects`.
2. **En Cloudflare Pages, un `rewrite` pierde contra un fichero que existe; un
   `redirect` gana.** Si hay que tapar una ruta que existe, redirect.
3. **Pages SÍ publica los ficheros que empiezan por punto.** El prefijo `.` es un
   convenio nuestro, no un mecanismo de seguridad.
4. **El build output es `/`: todo el repo se publica.** El brief de desarrollo
   —con la tabla de qué reloj imita a cuál— estuvo descargable en abierto.
   Antes de añadir una carpeta, pensar si puede salir a internet.
5. **La caché de borde de Cloudflare es inconsistente entre nodos.** No dar por
   fallido un despliegue tras una sola lectura: sondear varias seguidas.
6. **Cada rama publica preview pública.** Tapar una fuga en `main` no la tapa en
   las ramas viejas.

### Supabase
7. **Los grants por defecto solo cubren `public`.** En un esquema nuevo hay que
   dar permisos a `service_role` **a mano** o las Edge Functions fallan con un
   502 sin explicación. Costó un buen rato encontrarlo.
8. **Al hablar con PostgREST hay que mandar `Content-Profile: laora`** (o
   `Accept-Profile` al leer) o busca en `public`, que está vacío.
9. **`SUPABASE_SERVICE_ROLE_KEY` está marcada DEPRECATED**, la sustituye
   `SUPABASE_SECRET_KEYS`. El código acepta las dos.
10. **El límite del plan Free es por usuario, no por organización.**
11. **Un 200 con `[]` no es una fuga:** RLS devuelve lista vacía, no error. Hay
    que mirar el cuerpo, no solo el código de estado.

### CSS y front
12. **`laora.css` se carga en todas las páginas y pisa lo que no esperas.**
    Ya define `.hero`, `.eyebrow`, `.serif`, `.reveal` y el fondo del `footer`.
    Las páginas nuevas usan prefijo propio (`c-` en la colección, `b-` en la
    ficha) y redeclaran `footer{background:var(--negro)}`.
13. **Copiar el pie de `index.html` arrastra los guiones de los Actos** (audio,
    overlay de vídeo) y la página peta. Copiar solo `<footer>…</footer>`.
14. **`acto5-taller.jpg` lleva el botón de «reproducir» incrustado**: es el póster
    del vídeo. Para usarla fuera del Acto V está `taller-madrid.jpg`, recortada.
15. **Si el negro del render no es el de la sección, se ve el recuadro** de cada
    foto. Se resuelve con una `mask-image` radial, no ajustando el color a ojo.

### Datos, dinero y legal
16. **Nunca inventar un precio.** Un acabado sin precio cerrado no enseña botón
    de compra: enseña que todavía no está a la venta. El código lo impide.
17. **El navegador nunca fija el importe.** El servidor recalcula desde
    `precios.js` y rechaza si no cuadra.
18. **La garantía en España son 3 años** (RDL 7/2021), no 2. Los bocetos siguen
    poniendo 2: hay que corregirlo cada vez.
19. **«Hardlex» es marca de Seiko y «Tiffany» de Tiffany & Co.** Se dice
    «mineral K1» y «turquesa».
20. **El reloj homenajeado se nombra UNA vez**, y solo dentro de «La historia» de
    su ficha. Nunca en títulos, metas, alts, URLs ni en la colección.
21. **El ® del logo:** las marcas no están registradas en la OEPM. Usarlo sin
    registro es sancionable. Sigue puesto: es decisión de Óscar.

### Herramientas y método
22. **Un `getUi().alert()` en Apps Script cuelga la ejecución** si la hoja no está
    en primer plano. Usar `Logger.log`.
23. **El portapapeles es compartido con Óscar.** Si él copia algo, se pierde lo
    que hubiera puesto el asistente. Para textos cortos, escribir directamente.
24. **En el editor SQL de Supabase hay que clicar DENTRO del área de texto.** Si
    el clic cae fuera, `cmd+A` selecciona la página y lo tecleado dispara atajos:
    una vez acabé en Observability. Usar `find` para obtener el `ref` del editor.
25. **`sips --cropOffset` no cuenta desde la esquina superior izquierda.** Para
    partir una imagen en tramos, verificar el resultado.
26. **Los bocetos traen nombres desfasados** (integra, campo, octógono, puerto,
    cero cero). Comprobar contra los nombres actuales antes de copiar.
27. **No fiarse de un documento de traspaso.** El anterior daba por «anclas
    muertas que no rompen nada» lo que en realidad era que las nueve fichas
    estaban inalcanzables y no quedaba ninguna vía de contacto en toda la web.
    **Comprobar siempre contra producción.**

---

## 5. Marca, tono y decisiones cerradas

- **laOra** siempre en Nunito Sans, minúsculas con la O mayúscula.
- **Nada de anglicismos** en la web ni en los nombres de producto.
- Paleta: negro `#050505`, ámbar `#F5D34D`, oro `#c7a04a`, hueso `#f2efe9`.
  Serif **Source Serif 4** para titulares, **JetBrains Mono** para epígrafes.
- **Gama:** `01 Alba · 02 Levante · 03 Cenit · 04 Eclipse`. Son las
  denominaciones **para todos los modelos**; cuando un reloj tiene tres, se usan
  las tres primeras. La Bitácora va con tres.
- **LO-02 se llama «Cero Cero»** — lo manda la esfera del render.
- **Compra: carrito**, decisión de Óscar del 29/07. Antes era compra directa con
  señal del 25 %; ese código sigue ahí y funciona.
- **Nunca prometer stock ni plazos** que no estén cerrados.
- **Nunca vender nada a la audiencia de Saneas.**

---

## 6. Comprobaciones rápidas

```bash
# ¿queda algún enlace a un ancla que no existe?
grep -rn '#coleccion\|#interesados\|#porque\|#madrid' --include="*.html" . | grep -v '^./.docs'

# ¿se ha colado algo interno en producción? (debe decir «Redirecting»)
for u in .docs/brief-desarrollo.md .supabase/estructura-grupo.sql; do
  curl -s "https://laora.es/$u" | head -c 14; echo "  <- $u"; done

# ¿aguanta el guardarraíl del precio?
curl -s -X POST "https://uikanfvigunjhzibnhxf.supabase.co/functions/v1/laora-crear-reserva" \
  -H "apikey: sb_publishable_1eLOM22REKcIJyHe36W_4Q_1Z3eyRam" \
  -H 'Content-Type: application/json' \
  -d '{"ref":"LO-07","modelo":"Bitacora","acabado":"Cenit","metodo":"bizum","precio_total":1,
       "nombre":"x","email":"p@example.com","telefono":"1","direccion":"x","cp":"1",
       "poblacion":"x","provincia":"x"}'

# ¿todas las fichas se alcanzan desde algún sitio?
grep -c '/relojes/' coleccion.html
```
