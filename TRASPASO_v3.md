# 📋 TRASPASO — laOra v3

**Fecha:** 03/08/2026 · **Estado:** en producción · **Propietario:** Óscar Belloso

Este documento es para quien coja el trabajo después. Lee entero el
apartado 6 («Las quince trampas») antes de tocar nada: casi todas son
cosas que ya han roto algo una vez.

---

## 1 · RUTAS

### En producción

| Qué | Dónde |
|---|---|
| Web | **https://laora.es** |
| Repositorio | **github.com/Saneas26/laora**, rama `main` |
| Despliegue | **Cloudflare Pages**, automático al empujar a `main` (~40 s) |
| Build output | `/` — **todo lo que hay en el repo se publica**. Nunca metas una clave |
| Punto de retorno | etiqueta `web-v1-antes-del-rediseno` (la web anterior, entera) |

### En local

```
/Users/oscar/Sites/laora/
├── herramientas/generar.py      ← EL GENERADOR. Escribe las 13 páginas
├── assets/
│   ├── datos/catalogo.json      ← ÚNICA FUENTE DE VERDAD de los relojes
│   ├── css/
│   │   ├── laora.css            ← hoja única (768 líneas)
│   │   └── cabecera.css         ← la cabecera, compartida y anterior al rediseño
│   ├── js/
│   │   ├── home.js              ← pase de fotos del héroe + mapa del precio
│   │   ├── ficha.js             ← galería + configurador + curiosidades
│   │   ├── cabecera.js          ← inyecta la hamburguesa, fija la cabecera
│   │   └── telemetria.js        ← recuento anónimo del Grupo Saneas
│   └── img/relojes-2026/        ← 28 fotos .webp, 3 MB (las del material nuevo)
├── PRECIOS-ANTERIORES.md        ← copia de los precios de la web vieja
├── TRASPASO_v3.md               ← este documento
├── PROMPT_SIGUIENTE.md          ← qué pegarle a quien coja el trabajo
├── _redirects                   ← 48 reglas: las 17 URLs retiradas no dan 404,
│                                  y la documentación interna no se sirve
└── privacidad.html              ← LA ÚNICA página que se edita a mano
```

### Servidor local

**No hay Node en el Mac de Óscar.** Todo es Python 3. El servidor está en
`/Users/oscar/Sites/.claude/launch.json` con el nombre `laora` (puerto 8791,
`python3 -m http.server`). Se arranca con la herramienta de previsualización,
nunca desde una terminal.

### Fuentes de datos externas

| Qué | Dónde |
|---|---|
| Hoja de materiales | Google Sheet **`laora-biblioteca-materiales`**, id `1hOEjyzjzHewt-CThFyJWeIREw6J56Rj5gEmc2w5z0cc` |
| Pestaña que manda | **`Catalogo final`** — 68 columnas, una fila por combinación |
| Fotos de Óscar | Drive, carpeta `laOra_Material` (compartida con `saneacuerpoymente@gmail.com`) |

---

## 2 · CÓMO SE TRABAJA

### La regla de oro

> **Las páginas `.html` NO se editan a mano. Son salida del generador.**

Llevan un aviso en el `<head>`. Si editas una, el siguiente
`python3 herramientas/generar.py` te la pisa.

```bash
python3 herramientas/generar.py
```

Reescribe `index.html`, las cuatro de sección y las ocho fichas.
**No toca `privacidad.html`**, que se mantiene a mano.

### Dónde se cambia cada cosa

| Quiero cambiar… | Voy a… |
|---|---|
| Un dato de un reloj (precio, specs, fotos, historia) | `assets/datos/catalogo.json` |
| Un texto de una sección (home, taller, club…) | `herramientas/generar.py` |
| El aspecto | `assets/css/laora.css` |
| Las cifras del mapa del precio de la home | `assets/js/home.js` |
| La cabecera o el pie | `generar.py`, están una sola vez |

### Después de tocar el CSS

**Sube `V_CSS` en `generar.py`.** Cloudflare sirve el CSS con
`cache-control: max-age=14400`: sin subirlo, el navegador se queda **hasta
cuatro horas** con la hoja antigua. Esto ya costó una tarde entera.

Ahora mismo: `V_CSS = 25`, `V_CAB = 13`, `home.js?v=8`, `ficha.js?v=5`,
`cabecera.js?v=3`.

### Verificar en producción

El borde de Cloudflare tarda y **no es uniforme**: durante un minuto o dos
unas lecturas traen lo nuevo y otras lo viejo. Comprueba siempre con
**tres lecturas seguidas consistentes**, no con una.

---

## 3 · CÓMO QUEDA LA ESTRUCTURA

### Las 14 páginas

```
/                    home · 9 actos
/coleccion.html      los 8 modelos + los 4 acabados
/filosofia.html      «Nuestra forma de hacer»
/taller.html         taller y servicio
/club.html           Club laOra
/lunar.html          ┐
/cero-cero.html      │
/bauhaus.html        │
/precisa.html        ├ las 8 fichas de modelo
/trinchera.html      │
/bitacora.html       │
/tortuga.html        │
/coctel.html         ┘
/privacidad.html     legal, a mano
```

### Los códigos los manda la hoja

Hasta el 03/08/2026 la web y la hoja usaban el mismo código para relojes
distintos. **Ahora manda la hoja**, para que la referencia que ve el cliente
sirva para buscar en el almacén:

| Código | Modelo | URL |
|---|---|---|
| LO—01 | Lunar | `/lunar.html` |
| LO—02 | Cero Cero | `/cero-cero.html` |
| LO—03 | Bauhaus | `/bauhaus.html` |
| LO—04 | Precisa | `/precisa.html` |
| LO—05 | Trinchera | `/trinchera.html` |
| LO—07 | Bitácora | `/bitacora.html` |
| LO—08 | Tortuga | `/tortuga.html` |
| LO—09 | Cóctel | `/coctel.html` |

**El hueco en LO—06 es correcto**: la hoja tiene ahí un «Meridiano»
(homenaje al Rolex Explorer II) que no está en la web, y que la propia hoja
marca con **riesgo legal MUY ALTO**. No lo añadas sin hablarlo.

### Lo que NO existe

- **No hay carrito, ni checkout, ni pasarela.** Se retiró entero el
  03/08/2026 por decisión de Óscar. Lo que había —`precios.js`, `reservar`,
  `pagar`, `pagos.js`, la Edge Function `crear-reserva.ts` y las condiciones
  de venta— sigue recuperable en la etiqueta `web-v1-antes-del-rediseno`.
- **No hay ninguna dirección de correo**, salvo `taller@laora.es` en el
  cierre de `/taller.html`. `hola@laora.es` se retiró de toda la web.

---

## 4 · EL ESTILO

### De dónde sale

`assets/css/laora.css` es el `globals.css` del material de Codex del
03/08/2026 **copiado verbatim**, con el «preflight» de Tailwind replicado
delante (el original venía sobre Tailwind; sin eso se descuadran decenas de
medidas).

Óscar fue explícito: *«copia todo el diseño tal cual, con sus fuentes,
colores y todo exactamente igual»*.

### La paleta y las fuentes

```css
--ivory  #f4f0e8    fondo de página
--paper  #fbfaf6    fondo de secciones claras
--ink    #1c1d1b    texto
--muted  #6c6c64    párrafo secundario
--gold   #b48744    oro del material  (NO es el #D4A94B de la marca)
--green  #315347    bandas de servicio
--dark   #151715    secciones oscuras

--serif  Georgia          titulares y cursivas
--sans   Arial            todo lo demás
```

**Los titulares van en Arial peso 500**, y solo la cursiva (`<em>`) en
Georgia. No es una errata: es el diseño.

### Las excepciones deliberadas

Hay cuatro sitios donde el CSS **se sale del original a propósito**. Están
comentados en la hoja. No los «corrijas» de vuelta:

1. **Suelo de 12 px** en las notas del mapa del precio y en la ficha
   técnica. El original las traía a 9, 10 y 11.
2. **`--gris-galeria #4e4943` y `--oro-galeria #836026`**, solo para la
   noticia y las curiosidades. Van sobre el gris de la galería (`#e9e5dc`),
   más oscuro que la página, y ahí los colores del material se quedan en
   4,2:1 y 2,6:1.
3. **La cabecera es una barra maciza de 76 px** pegada arriba, como la del
   material. La nuestra iba flotando y el menú caía sobre la foto del héroe.
4. **`.aire`** en la palabra «termina» del Club: a −.065em de tracking la
   `r` se pega a la `m` y se leía «temmina».

### El logotipo está blindado

`«laOra» no se escribe: se dibuja.` Es el logotipo canónico en Nunito Sans,
todo en minúsculas salvo la O, que es el círculo con el triángulo invertido
a las 12. **Solo se le puede cambiar el color y el cuerpo.**

En `laora.css`:

```css
.cb-marca { text-transform: none !important; display: inline-flex !important;
  gap: 0 !important; white-space: nowrap; }
.cb-marca .o { font-size: inherit !important; }
```

Esos `!important` no son pereza: el logotipo se deformó **dos veces** porque
reglas de página alcanzaban a sus `span` (una le metió 9 px al círculo, otra
lo abrió con un `gap`). En el generador va por la constante `MARCA`.

Si lo metes dentro de un `.button` (que es `inline-flex` con `gap:22px`),
envuélvelo con el rótulo en `<span class="etiqueta">` o el hueco los separa.

---

## 5 · EL MODELO DE FICHA INSTAURADO HOY

Esta es la parte nueva y **es la plantilla para los seis modelos que faltan**.
Está hecha en el **Lunar** y en el **Bauhaus**. Míralos antes de seguir.

### La ficha tiene dos columnas

```
┌─ IZQUIERDA (.pdp-gallery) ────────┬─ DERECHA (.pdp-buy) ──────┐
│  foto grande + miniaturas         │  código · familia          │
│                                   │  NOMBRE                    │
│  ┌ CURIOSIDADES ────────────┐     │  homenaje                  │
│  │ 2 botones → <dialog>     │     │  descripción               │
│  └──────────────────────────┘     │  PRECIO (cambia)           │
│                                   │  ── configurador ──        │
│  ┌ LA HISTORIA DEL ORIGINAL ┐     │  acabado  [botones]        │
│  │ noticia de periódico     │     │  correa   [botones]        │
│  │ + aviso legal            │     │  ficha técnica (cambia)    │
│  └──────────────────────────┘     │  referencia LO-01_..._A01  │
└───────────────────────────────────┴────────────────────────────┘
```

La izquierda se llenó hoy: antes se quedaba corta y el blanco cantaba.

### 5.1 · El configurador

Datos en `catalogo.json` → `configurador`:

```json
"configurador": {
  "acabados": [ { "id", "nombre", "descriptor", "resumen",
                  "movimiento", "movimientoTipo", "frecuencia",
                  "autonomia", "cristal", "caja", "bisel", "peso" } ],
  "correas":  [ { "id", "nombre", "detalle" } ],
  "precios":  { "alba": [229.90, ...], ... },
  "comunes":  { "Diámetro": "40 mm", ... }
}
```

- **`precios[acabado][índice de correa]`** — la matriz completa.
- **`correas` vacío** → no se pinta el grupo. Un desplegable de una sola
  opción es un estorbo (es el caso del Bauhaus).
- Las claves de `acabados` que existan se pintan como líneas de ficha
  técnica que **cambian al elegir**; las que no, se omiten. El Bauhaus no
  distingue `fondo`, el Lunar sí distingue `cristal`.
- **`descriptor` es la mejor característica del acabado**, y tiene que ser
  cierta en ese reloj. Ver la trampa 8.
- La **referencia** se compone igual que en la hoja
  (`LO-01_Lunar_A01`): código + inicial del acabado + número de correa.

### 5.2 · Las curiosidades

Dos por ficha, en `catalogo.json` → `curiosidades`:

```json
{ "id", "titulo", "gancho", "cuerpo": ["párrafo", "párrafo", ...] }
```

Abren una **ventana emergente de verdad** con `<dialog>` y `showModal()`.
El fondo oscurecido, el cierre con Escape, el foco atrapado dentro y su
devolución al botón los pone el navegador. En `ficha.js` solo van abrir,
cerrar y el clic en el fondo.

**No repitas lo que ya cuenta la noticia.** Las cuatro que hay son buenas
referencias de tono: la hesalita, el taquímetro, el azul de las agujas y la
denominación de origen de Glashütte.

### 5.3 · La historia del original

En `catalogo.json` → `historiaOriginal`. Compuesta como pieza de periódico:
filete doble, antetítulo, titular a dos líneas, entradilla en cursiva,
capitular, **cuerpo a dos columnas justificadas con guionado** y cuatro
hitos fechados.

```json
{ "original", "antetitulo", "titular", "entradilla",
  "cuerpo": [...], "datos": [["1969","..."], ...], "cierre", "aviso" }
```

**Nombra la marca y el modelo con todas sus letras** — decisión de Óscar. Y
justo por eso **`aviso` no es opcional**: dice que son marcas de sus
titulares, que laOra no está afiliada, y que aquello es divulgación. Va a
12 px, no escondido. El del pie no basta: hace falta aquí.

---

## 6 · LAS QUINCE TRAMPAS

1. **No edites los `.html`.** Son salida del generador.
2. **Sube `V_CSS`** en cada cambio de CSS, o el navegador se queda 4 h con
   la hoja vieja.
3. **No hay Node.** Python 3 y punto. El generador se escribió primero en
   JavaScript y hubo que rehacerlo.
4. **Nada interno de la hoja llega al HTML.** Ahí hay enlaces de AliExpress,
   precio de compra por pieza, coste, margen y beneficio. Al JSON que se
   sirve solo van acabado, correa, PVP, movimiento y specs visibles.
5. **Traduce la jerga del proveedor.** La hoja dice «caja tipo Speedmaster»,
   «esfera tipo Nomos», «brazalete presidencial», «caja tipo DJ». Eso en la
   web **choca de frente con el aviso legal del pie**. Descríbelo por lo que
   es.
6. **No inventes precios ni specs.** `null` significa «no lo sabemos» y esa
   línea sencillamente no se pinta. Nunca un «por confirmar» a la vista.
   El material de Codex traía precios calculados por fórmula: se descartaron
   enteros.
7. **La hoja se contradice a sí misma.** Su pestaña «Modelos» y su
   «Catalogo final» discrepan en diámetro y estanqueidad del Lunar (42/50 m
   contra 40/100 m). **Manda «Catalogo final».**
8. **Cada reloj es distinto. No hagas plantilla.** «Movimiento suizo» vale
   en el Bauhaus (Ronda 1069) y sería **falso** en el Lunar (VK63, japonés).
   «Movimiento automático» vale en el Bauhaus (ST1701) y es **falso** en el
   Cenit del Lunar (ST19, cuerda manual). Mira el calibre antes de titular.
9. **Si Óscar corrige la hoja de palabra, avísale de que la hoja sigue
   diciendo lo contrario.** Pasó con el fondo del Bauhaus: la hoja lo da
   como «exhibición de cristal» y va macizo. Es la fuente de la que se
   vuelca todo.
10. **El logotipo está blindado.** Ver apartado 4.
11. **El oro del material no vale sobre fondos oscuros.** Sobre `#e9e5dc`
    se queda en 2,6:1. Usa `--oro-galeria`.
12. **El `preflight` mata cosas del navegador.** Pone `margin:0` a todo, y
    eso descentró la ventana emergente (un `<dialog>` modal se centra con
    `margin:auto`). Si algo nativo se comporta raro, mira ahí primero.
13. **La captura del panel del navegador no es fiable** con la página
    desplazada o el panel oculto: devuelve blanco o contenido viejo. Mide
    con `getBoundingClientRect` y `getComputedStyle`, y para ver un bloque
    de más abajo, quita por JS los hermanos anteriores.
14. **Las transiciones no avanzan con el panel oculto**, así que
    `getComputedStyle` devuelve el valor de partida. Para leer el valor
    real, desactiva las transiciones antes de medir.
15. **Cloudflare ofusca los `mailto:`** automáticamente. Si buscas una
    dirección en el HTML servido y no aparece, mira si hay un
    `/cdn-cgi/l/email-protection`.

---

## 7 · POR DÓNDE SE SIGUE

**Crear las fichas de los seis modelos que faltan**, con el mismo modelo del
apartado 5: configurador + dos curiosidades + la historia del original.

### Estado real de los datos

| Modelo | En «Catalogo final» | Se puede hacer |
|---|---|---|
| **Cero Cero** LO—02 | **24 combinaciones**, los 4 acabados | **Sí, es el siguiente** |
| Precisa LO—04 | — | No, falta volcarlo |
| Trinchera LO—05 | — | No |
| Bitácora LO—07 | — | No |
| Tortuga LO—08 | — | No |
| Cóctel LO—09 | — | No |

**Solo el Cero Cero tiene datos.** Los otros cinco no tienen ni una fila:
hay que pedirle a Óscar que los vuelque antes.

### Antes de hacer el Cero Cero, dos cosas que mirar con Óscar

- Sus **correas 03 y 06 son la misma** —«NATO nailon negro/naranja», mismo
  precio— en los cuatro acabados. Saldrían dos botones idénticos.
- **Alba y Levante son idénticos**: mismo movimiento (VH31) y exactamente
  los mismos seis precios. Hoy el cliente no vería diferencia entre pagar
  uno u otro.

### Los originales de cada modelo, para escribir su historia

| Modelo | Original que se nombra |
|---|---|
| Cero Cero | Omega Seamaster Diver 300M |
| Precisa | Tissot PRX |
| Trinchera | Hamilton Khaki Field |
| Bitácora | Patek Philippe Nautilus |
| Tortuga | Seiko Prospex «Turtle» |
| Cóctel | Seiko Presage Cocktail Time |

---

## 8 · LO QUE QUEDA ABIERTO

| Asunto | Estado |
|---|---|
| **Botón de reserva** | Óscar eligió recuperar la reserva con señal. `reservar.html`, `pagar.html` y `reserva-recibida.html` están en la etiqueta pero **con el diseño viejo**: hay que rehacerlas. El botón está escrito y **comentado** en la ficha, listo para descomentar; `ficha.js` ya le pasa referencia, acabado y correa por la URL. La lógica que se salva: `precios.js`, `pagos.js`, `crear-reserva.ts` y las condiciones de venta. Transferencia y Bizum **ya funcionaban** con el IBAN puesto; solo tarjeta y PayPal esperaban la clave de Mollie |
| **Fichas sin llamada a la acción** | Las seis sin configurador no tienen nada que pulsar |
| **Precios de la home** | El «desde 209,90 €» del mapa del precio es del Lunar. Cuando entren más modelos, comprobar que sigue siendo el mínimo de la colección |
| **Cifras del mapa del precio** | Orientativas y fechadas en agosto de 2026. Si se actualizan en `home.js`, **actualizar también la fecha de la nota legal** |
| **Detalle en negro de la home** | La sección «Calidad demostrable» usa `lunar-detail.webp`, que es el acabado Eclipse. Haría falta una foto de detalle del de acero |
| **Sin Node** | Si algún día hace falta, hoy no está instalado |

---

## 9 · FILOSOFÍA — lo que Óscar no negocia

- **Homenaje no es falsificación.** Se nombra el original, se explica de
  dónde viene y **nunca** se pone en la esfera un nombre ajeno. El aviso del
  pie va en las 13 páginas.
- **Legibilidad.** Manda sobre la estética… **salvo en laOra**, donde Óscar
  levantó la regla para copiar el diseño tal cual. Aun así puso un suelo de
  **12 px** para el texto que hay que leer. Ver la memoria
  `legibilidad-por-encima-de-todo`.
- **Nada inventado.** Ni precios, ni specs, ni movimientos, ni fechas. Si no
  está confirmado, no se publica.
- **Al terminar, fusionar.** Commit y push sin esperar a que lo pida.
