# 📸 TRASPASO — laOra, las fotos de colección y configurador

Estado a **23/08/2026, 21:00**. Este documento existe para que un Claude nuevo
sea operativo a la primera orden, sin preguntar nada.
Complementa a `TRASPASO_v3.md` (estructura, estilo, fichas); **no lo repite**.

---

## 0 · LO PRIMERO: LAS NORMAS DE ÓSCAR

Son órdenes suyas, no preferencias. Romper una cuesta días de trabajo.

| Norma | Qué significa |
|---|---|
| **Un reloj cada vez** | Cuando nombra un modelo, los demás **ni se tocan, ni se miran, ni se mencionan**. |
| **Nada viejo** | Cero componentes, precios o fotos del catálogo anterior sin su «sí» pieza a pieza. «Antiguo» = hace cinco minutos para atrás. |
| **Anotarlo TODO** | Cada dato que dé (un link, un precio, una medida) se registra **en el mismo turno**. Jamás volver a preguntarle un dato ya dado. |
| **Preguntar con botones** | Todo siguiente paso se propone con `AskUserQuestion`, nunca en prosa. Responde con un clic. |
| **Verificar en producción** | No se dice «hecho» ni «desplegado» sin `curl` real a laora.es. Ver la trampa del `?v=` más abajo. |
| **Commit + push al terminar** | Sin esperar a que lo pida. |
| **El prompt, de copia y pega** | Si pide «el prompt» para un tercero: bloque de texto **en el chat**, autosuficiente. No un archivo del repo. |
| **Entrada por el original** | Cada configurador abre con la configuración del reloj homenajeado. |
| **El movimiento nunca se nombra** | En la web: «Calibre laOra LO_xxxx» + arquitectura suiza / fabricación japonesa. Jamás China ni la marca real. |
| **Legibilidad por encima de todo** | Contraste alto, texto grande, legible para alguien de 60 años. Manda sobre bocetos e identidad. |
| **La API key de Mollie no se pega en el chat** | Vive en el secreto `LAORA_MOLLIE_API_KEY`. |

### 🚫 Vías CERRADAS — no volver a proponerlas

Óscar las descartó **por experiencia propia**, cada una tras probarla:

1. **Composición por capas** (Claude monta piezas separadas). Falló días. Su
   frase: *«tú dices que colocas bien la esfera cuando no estaba bien colocada»*.
2. **Render 3D con Blender.** Se instaló, se modeló la caja, se renderizó, y lo
   cortó el 23/08: *«no se parece la forma de la caja… es tontería continuar»*.
   Desinstalado sin rastro el mismo día.
3. **Pagar un 3D a un freelance.** *«hay que hacerlo de manera gratuita… ya no
   pago más»*.

**Claude NO genera imágenes.** Eso se dice claro en vez de ofrecer sucedáneos.

---

## 1 · DÓNDE ESTÁ TODO

### Producción
| | |
|---|---|
| Web | **https://laora.es** |
| Alojamiento | **Cloudflare Pages** (no Vercel) |
| Repo | **https://github.com/Saneas26/laora** · rama `main` |
| Despliegue | automático con `git push origin main`. Tarda ~1 min. |
| Backend | Supabase `https://uikanfvigunjhzibnhxf.supabase.co` |
| Edge Functions | `functions/v1/pagar-pedido` · `functions/v1/panel-laora` |
| Cobro | **Mollie**, real. El carrito cobra de verdad. |

### Local
| | |
|---|---|
| Repo | `/Users/oscar/Sites/laora` |
| Servidor de pruebas | `python3 -m http.server 4173 --directory /Users/oscar/Sites/laora` (ya definido en `.claude/launch.json`, nombre `laora`) |
| Másteres de foto | **NO existen.** Se borraron el 23/08. Óscar los entrega uno a uno por ruta. |

### Firma de los commits — obligatoria
```
git -c user.email="215491276+Saneas26@users.noreply.github.com" \
    -c user.name="Saneas26" commit -m "..."
```

---

## 2 · EL ESTADO REAL: LAS FOTOS ESTÁN A CERO

El 23/08 Óscar ordenó borrarlas todas: *«no quiero ninguna imagen de ningún
reloj, todos fuera… las miniaturas también. Solo hablo de la hoja colección y
configurador, **la landing inicial no la toques**»*.

**Se borraron 1.381 ficheros.** `assets/img` pasó de 151 MB a 32 MB.
Commits `768ffb8` y `fb22fb8`, verificados en producción.

### Cuántas referencias están rotas ahora mismo

| Fichero | Rotas | Total |
|---|---:|---:|
| `bitacora.html` | **74** | 85 |
| `coleccion.html` | **65** | 73 |
| `cero-cero.html` | **50** | 51 |
| `assets/datos/recomendador.json` | **20** | 20 |
| `lunar.html` | **10** | 19 |
| `trinchera.html` | **9** | 18 |
| `precisa.html` | **3** | 12 |
| `assets/datos/piezas-lunar.json` | **1** | 1 |
| **TOTAL** | **232** | |

`index.html`, `filosofia.html`, `club.html`, `taller.html`, `laorateca.html`,
`carrito.html`, `cuenta.html`, `panel.html`, `404.html`, `coctel.html`,
`diver.html`, `tortuga.html` → **0 rotas. Están intactas y NO se tocan.**

### Lo que SÍ sigue vivo en `assets/img` (67 ficheros, 32 MB)
`heroes-2026/` (7, los usa index) · `filosofia/` (15) · `filosofia-2026/` (4) ·
los `acto*.jpg` sueltos · `taller-madrid.jpg` · `compra-directa.jpg` ·
`marca/` (3 logotipos de esfera) · `pago/klarna.svg` · iconos PWA ·
capturas `app-*` del Grupo Saneas · y **15 supervivientes** dentro de las
carpetas purgadas porque los usa la landing: los `trust-*`, `lunar-hero-steel`,
`lunar-wrist`, `coctel-bar-logo-alto`, `laora-wordmark-dark`,
`bitacora-hero-full`, `tortuga-detail`, `workshop-hero`, `lunar-acero`,
`trinchera-acto1`.

### ⚠️ DOS AVISOS ABIERTOS

1. **El volcador del catálogo está roto.** `herramientas/volcar_catalogo_2026.js`
   falla con `ENOENT … assets/img/lunar-config/manifest.json` desde la purga, así
   que `assets/datos/catalogo-2026.json` **se ha quedado con las referencias y
   fotos viejas**. El servidor valida los pedidos contra ese fichero.
2. **La venta sigue ABIERTA.** Decisión expresa de Óscar el 23/08: se le ofreció
   cerrar el paso a pago y dijo que no. **No volver a proponerlo.**

---

## 3 · CÓMO SE PUBLICA UNA FOTO (el trabajo pendiente)

### El formato de la casa
- **AVIF**, en **tres tamaños: 480 / 1200 / 1600**, servidos con `srcset`.
- **El máster (4096) NO se publica nunca** y no se guarda en el repo.
- Calidades ya calibradas: 480→62, 1200→66, 1600→68.

### La herramienta
```bash
python3 herramientas/foto_a_web.py <master.png> <carpeta_destino> <nombre>
```
Crea `<carpeta>/480|1200|1600/<nombre>.avif`. Imprime el peso de cada uno.

### Dónde van, por página

| Página | Carpeta | Patrón del nombre |
|---|---|---|
| `trinchera.html` | `assets/img/componentes/<grupo>/` | por PIEZA, no por reloj — ver abajo |
| `lunar.html` | `assets/img/lunar-config/{heads,straps,buckles,casebacks}/` | por pieza, más `manifest.json` |
| `precisa.html` | `assets/img/precisa-2026/` | |
| `bitacora.html` | `assets/img/bitacora/` y `assets/img/piezas/completas/` | |
| `cero-cero.html` | `assets/img/cero-cero/` | |
| `coleccion.html` | reutiliza las de las fichas | |

### Los contadores de versión hay que subirlos a mano
Cada ficha tiene su constante y **Cloudflare cachea 4 h**:
- ~~`trinchera.html` → `var SERIE_V`~~ · **se fue el 29/08/2026**: el Trinchera se genera desde `assets/datos/fichas/trinchera.json` y ya no lleva fotos propias dentro.
- `lunar.html` → `?v=12` en las rutas de `lunar-config`
- Al regenerar con `generar_configurador_v2.py`, **comprobar que no BAJA** las
  versiones (`V_CARRITO`, `V_JS`): es una trampa conocida.

### Después de tocar cualquier configurador
```bash
node herramientas/volcar_catalogo_2026.js
```
Si no se pasa, la web enseña el precio nuevo y el servidor rechaza la
referencia con «ya no está a la venta».

### ⚠️ La trampa del `?v=` — verificar SIEMPRE así
En Cloudflare, `?v=25` **no** revienta la caché: sirve el archivo viejo hasta 4 h.
Para comprobar de verdad:
```bash
curl -sL -o /tmp/x "https://laora.es/assets/img/.../foto.avif?x=$RANDOM" && md5 -q /tmp/x
```
y comparar con el `md5` del fichero local. Ojo también al 308 de `/lunar.html` →
`/lunar`, que obliga a `curl -sL`.

---

## 4 · DE DÓNDE SALEN LAS FOTOS

**Las genera Óscar, no Claude.** Se las pide a **Gemini** (gratis, y le funciona
mejor que ChatGPT de pago: le dio en 30 s algo mejor que tres semanas). Se las
pasa a Claude por ruta local, normalmente en `~/Documents/Codex/<fecha>/…`.

### El límite real, y no es de prompt
Un logotipo de 8 mm en una esfera de 38 es **texto diminuto**, y los modelos de
imagen fallan ahí de forma sistemática. Sale «LUNAB», «TRINCHER», tipografías
inventadas. **Ningún prompt lo arregla de forma fiable.** No prometer que sí.

### El protocolo que sí reduce fallos
1. **Nunca «genera un reloj».** Siempre «en esta imagen, cambia solo…».
2. **Un fallo por mensaje.** Dos, y redibuja el reloj entero.
3. **El logotipo se adjunta, no se describe.** El PNG está en
   `assets/img/marca/logo-esfera-{modelo}.png`.
4. **En inglés.**
5. **La resolución NO se le pide al generador**: se escala después con Upscayl
   (libre y local).
6. **Congelar lo bueno.** Una imagen aprobada no se vuelve a tocar; los cambios
   parten de ella, nunca encadenados.

### El generador del logotipo de esfera
```bash
python3 herramientas/logotipo_esfera.py TRINCHERA
python3 herramientas/logotipo_esfera.py TRINCHERA --sep 54 --dx 12
```
`--sep` = aire entre «laOra» y el modelo · `--dx` = ajuste **óptico** a la
derecha. Van a `assets/img/marca/`. Se construye desde el wordmark oficial, así
que las letras son las de verdad; el triángulo de la O va **relleno en plata**.

---

## 5 · EL TRABAJO DE CLAUDE: VERIFICAR ANTES DE PUBLICAR

Óscar pide expresamente que se le revise cada foto. Comprobar y decir **sí o no
con el motivo**, en un minuto:

| Qué | Cómo |
|---|---|
| **Formato** | PNG con canal alfa. Si es JPEG, el fondo «transparente» está **pintado** (ya pasó: un damero de 19,3 px en dos grises, 116 y 75). |
| **Resolución** | 4096 deseable. Medir el **diámetro de la caja en px**, no el lienzo. |
| **Encuadre** | bbox del objeto, centrado, y si la correa va a sangre. |
| **Texto** | logotipo completo, sin cortar, sin errata, con nuestra tipografía. |
| **Parches** | rectángulos de grano distinto alrededor del logo: injertos sin fundir. Se ven subiendo el brillo ×3. |
| **Restos fantasma** | formas blancas sueltas que no son piezas del reloj. |
| **Contaminación de color** | franjas verdes en el filo de las agujas al recortar. |
| **Detalles de modelo** | ¿está la escala de 24 h? ¿las agujas del color pedido? |

---

## 6 · LOS MODELOS

`LO-01 Precisa · 02 Trinchera · 03 Lunar · 04 Bitácora · 05 Cero Cero ·
06 Cóctel · 07 Tortuga · 08 Diver · 09 Medusa` (sin producir).

Precios de arranque, en `assets/datos/desde.json`:
`bitacora 319,90 · cero-cero 329,90 · coctel 159,90 · diver 219,90 ·
lunar 189,90 · precisa 249,90 · tortuga 189,90 · trinchera 189,90`.

⚠️ **La Precisa dice tres precios distintos**: portada 229,90, `desde.json`
249,90 y catálogo 259,90. Avisado, sin arreglar.

### El motor de precios 2026
Vive en cada ficha y en `assets/js/configurador-v2.js` (`D.motor === '2026'`):
```js
var IVA = 0.21, IRPF = 0.20, SS = 0.05, MULT = 2.28;
var PACKING_ENVIO = 9, GARANTIA = 4, COMISION = 0.025, KLARNA = 1.025;
costeCompleto(c) = (c + 9/1.21 + 4) * 1.05
precio = max(redondea(costeCompleto * 2.28 * 1.025), sueloPvp)
```
Suelo: **50 € limpios o 15 % de margen neto**, lo que sea mayor. El neto se
calcula asumiendo **50 % de las ventas por Klarna**.
Los costes de AliExpress **no llevan IVA**: hay que añadírselo.

---

## 7 · FICHEROS QUE IMPORTAN

```
/Users/oscar/Sites/laora/
├── coleccion.html            ← la hoja de colección (65 fotos rotas)
├── trinchera.html  lunar.html  precisa.html  bitacora.html  cero-cero.html
├── index.html                ← LANDING: no se toca
├── assets/
│   ├── datos/
│   │   ├── catalogo-2026.json    ← lo genera volcar_catalogo_2026.js (ROTO)
│   │   ├── piezas.json           ← costes y piezas de los 7 modelos
│   │   ├── desde.json            ← precios «desde»
│   │   └── recomendador.json     ← 20 fotos rotas
│   ├── img/marca/            ← los 3 logotipos de esfera
│   └── js/configurador-v2.js ← el motor común
└── herramientas/
    ├── foto_a_web.py             ← AVIF 480/1200/1600
    ├── logotipo_esfera.py        ← el logo impreso en la esfera
    ├── volcar_catalogo_2026.js   ← ARREGLAR
    └── generar_configurador_v2.py
```

⚠️ **Trampa de `generar_configurador_v2.py`**: al regenerar, rompe
Cóctel/Diver/Tortuga (pierden title, description, favicon, viewport-fit) y pisa
`desde.json` con precios viejos. Hay que restaurarlos con `git checkout`.

⚠️ **Puede haber otra sesión de Claude en el mismo repo** haciendo `git add -A`.
Comprobar `git status` antes de commitear.

---

## 8 · POR DÓNDE SE SIGUE

1. Óscar pasa **una foto**, por ruta local.
2. Claude la **verifica** (sección 5) y dice sí o no con el motivo.
3. Si es «sí»: **AVIF en tres tamaños**, se enchufa en su ficha y en colección,
   **se sube el contador de versión**, commit + push, y **se verifica en
   producción con `?x=$RANDOM`**.
4. Se repasan **coste, cuenta de explotación, links y especificaciones** de ese
   reloj.
5. Solo entonces se pasa al siguiente. **De una en una.**
