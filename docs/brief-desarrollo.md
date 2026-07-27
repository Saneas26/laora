# laOra — Brief de desarrollo web (handoff completo para Dev)

Este documento reúne TODO lo definido para montar laora.es. Va acompañado de tres archivos:

- **`laora-copy-web.md`** — el texto exacto de cada sección y de las 9 fichas de modelo, palabra por palabra. Es la fuente de la verdad para el copy.
- **`laora-biblioteca-materiales.xlsx`** — specs técnicas, materiales, sistema de acabados, Línea Eclipse y estándar de calidad de cada modelo.
- **`laora-hero-mockup.html`** — maqueta animada del héroe (ábrela en el navegador). Es la referencia visual del objetivo.

---

## 1. Qué es laOra

Marca propia de relojería del **Grupo Saneas**. Importa componentes, los **monta y controla en Madrid**, y vende directo por web. No es tienda, ni reventa, ni réplica: es una manufactura de ensamblaje con marca y logo propios.

**La promesa:** sin intermediarios, sin peajes de marca, sin comerciales. Solo pagas el material y el trabajo de hacerlo bien. Garantía de 2 años con servicio técnico propio desde España.

## 2. Objetivo y tono de la web

El objetivo NO es transmitir lujo que deslumbra. Es transmitir **tranquilidad, confianza y transparencia**. La web resuelve el miedo de comprar un buen reloj (falsificaciones, sin garantía, sin postventa, sobreprecio) contándolo claro y respondiendo todas las objeciones cuanto antes.

- Voz: honesta, cercana, didáctica. Frases cortas, verbos, cero relleno, **cero urgencia falsa** (nada de contadores, escasez inventada ni "quedan 3").
- Doble lector: el que no sabe de relojería (que salga sabiendo algo y con ganas) y el que sabe (que respete el detalle técnico).
- Enseñar antes que vender: en laOra, enseñar ES vender.

## 3. Arquitectura de la información

**Páginas:**
1. **Home** (una sola página larga con las secciones de abajo).
2. **9 landings de modelo** (LO-01 … LO-09), una por reloj.
3. **El alma de un automático** (manifiesto editorial).
4. **El proceso de Madrid** (montaje, calibración, hermeticidad, garantía).
5. **Avísame / El estreno** (formulario de captación pre-lanzamiento).
6. **Privacidad** (legal).

**Orden de secciones de la Home (importante, hay que reordenar respecto a lo actual):**
1. **Héroe** (ver punto 4).
2. **Por qué existe laOra — El problema** (el bloque nuevo; hoy falta en la web). Es el gancho emocional: la historia de por qué no había forma honesta de comprar un reloj.
3. **Ni un euro de humo** + los tres pilares (sin peajes de marca / transparencia / para toda la vida).
4. **La colección** (rejilla de los 9 modelos).
5. **El manifiesto** — el alma de un mecánico (tres corazones: cuarzo / automático / cuerda manual).
6. **Cómo funcionan los acabados**.
7. **El proceso de Madrid**.
8. **Avísame** (formulario).
9. **Pie** con el Grupo Saneas.

## 4. El HÉROE (lo más importante — ver `laora-hero-mockup.html`)

Hoy el héroe es una foto quieta y no seduce. Nuevo héroe:

- **Fondo:** sereno y premium (slate/charcoal profundo, NO negro discoteca, NO blanco corporativo). Transmite fiabilidad, no opulencia.
- **Vídeo/animación en bucle:** un reloj laOra con el **logo grabado en la esfera**, el **segundero en movimiento** y la **luz recorriendo el zafiro**. En producción: vídeo macro en bucle (autoplay, silenciado, `playsinline`, `loop`) o el render 3D animado del modelo. La maqueta HTML muestra el efecto exacto buscado.
- **Titular (H1):** «El reloj que quieres. **Al precio honesto.**» — con "Al precio honesto" en color de acento (ámbar). (Sustituye al antiguo "Sin nadie en medio".)
- **Subtítulo:** «Ahora puedes tener lujo, sin pagarlo como lujo.»
- **Garantías / objeciones respondidas en el propio héroe** (con check verde suave):
  - Acero 316L, 904L o titanio
  - Zafiro con AR por las dos caras
  - Brazaletes de eslabones macizos, nunca huecos
  - Movimientos originales, nunca falsos
  - Control de calidad en Madrid: estanqueidad y ajuste
  - Taller de reparaciones en Madrid · 2 años de garantía
  - Atención personal y directa, desde Madrid
  - Sin intermediarios ni sorpresas en aduana
- **CTAs:** «Ver la colección» (primario, ámbar) y «Por qué laOra» (secundario).

## 5. La colección (9 modelos)

Numeración final LO-01 a LO-09, sin huecos. En la rejilla y en la UI **los modelos se nombran solo por su nombre laOra**; la marca homenajeada aparece únicamente dentro del bloque «La historia» de cada ficha.

| Ref | Nombre | Categoría | Homenaje (solo en «La historia») | Esfera / color | Movimientos | Acabados | Desde | Riesgo legal |
|---|---|---|---|---|---|---|---|---|
| LO-01 | «Lunar» | Cronógrafo | Omega Speedmaster Moonwatch | Negra, 3 subesferas | VK63 mecacuarzo · ST1901 cuerda manual | 4 | 190 € | Medio |
| LO-02 | «Hora Cero» | Buceador 300 m | Omega Seamaster Diver 300M (Bond) | Negra, acentos naranja, malla, sin fecha | VH31 mecacuarzo · NH35 automático | 4 | 190 € | Medio |
| LO-03 | «Bauhaus» | Vestir | Nomos Tangente | Blanca, agujas azules, segundero pequeño; correa arena | Ronda cuarzo subsegundos · Seagull ST17 cuerda manual | 3 | 170 € | Bajo |
| LO-04 | «Precisa» | Deportivo integrado | Tissot PRX | Azul marino, relieve de cuadraditos | Ronda cuarzo · NH35 · PT5000/Miyota 9015 | 3 | 190 € | Bajo |
| LO-05 | «Trinchera» | Militar de campo | Hamilton Khaki Field | Negra militar, cordura verde | Cuarzo · NH35 | 3 | 150 € | Bajo |
| LO-06 | «Ocho Lados» | Lujo deportivo acero | Audemars Piguet Royal Oak | Verde ahumado, gran tapisserie; integrado | Cuarzo · NH35 · Miyota 9015 | 3 | 250 € | **MUY ALTO** (verificar EUIPO) |
| LO-07 | «Bitácora» | Lujo deportivo acero | Patek Philippe Nautilus | Tiffany (turquesa), relieve horizontal; integrado | Cuarzo · NH35 · Miyota 9015 | 3 | 250 € | **MUY ALTO** (verificar EUIPO) |
| LO-08 | «Tortuga» | Buceador 200 m | Seiko Turtle | Negra | VH31/cuarzo · NH35/NH36 | 4 | 180 € | Bajo |
| LO-09 | «Cóctel» | Vestir | Seiko Presage Cocktail | Marrón sunburst, oro rosa (PVD) | Cuarzo · NH35 | 3 | 180 € | Bajo |

## 6. Sistema de acabados (el selector de cada modelo)

Cada modelo vive en **3 o 4 acabados** (cronógrafos y buceadores llegan a 4). Sube el precio, sube la calidad y la terminación. **El de entrada NO es "el barato": pasa el mismo control de calidad que el más alto** (filosofía Hardlex de Seiko: si es cristal mineral, es del mejor grado). La escalera genérica:

| Acabado | Movimiento | Cristal | Material | Brazalete/correa | Precio orient. |
|---|---|---|---|---|---|
| **T1 · Cuarzo** | Cuarzo Ronda/Seiko (VK63 en cronos; VS42 solar opcional) | Mineral K1 grado alto o zafiro | 316L cepillado | Correa de calidad o brazalete macizo | 150–260 € |
| **T2 · Automático** | Seiko NH35/NH36 | Zafiro plano AR | 316L, buen acabado | Brazalete 316L macizo (end-links macizos) | 230–380 € |
| **T3 · Signature** | Miyota 9015 o PT5000 | Zafiro doble domo AR | 316L alto pulido o 904L; opción titanio | Brazalete mecanizado + correa extra | 330–560 € |
| **T4 · Master** (héroes) | Sellita SW200 / ST1901 cuerda manual con QC / solar especial | Zafiro doble domo (o box) | 904L o titanio | Mejor brazalete + estuche | 500–800 € |

El detalle de qué acabado lleva cada modelo está en la hoja **«Gama y acabados»** del Excel.

**Requisito funcional del selector:** en cada landing, al cambiar de acabado deben cambiar **foto, especificaciones técnicas, desglose de coste y precio**. Enseñar los acabados juntos (el alto ancla, el T2 se vende como la compra sensata).

## 7. Línea Eclipse (edición especial negra)

Edición *blackout* transversal. Ver hoja **«Línea Eclipse»** del Excel.

- **Acabado:** todo negro (caja, bisel, esfera, brazalete) con revestimiento **DLC** (no PVD: el DLC no se raya, es el negro "para toda la vida").
- **Agujas:** plateadas con el **segundero en amarillo** (único punto de color). Variante audaz para divers: horaria en amarillo.
- **Modelos elegibles:** LO-01, LO-02, LO-04, LO-06, LO-07, LO-08. **No** en LO-03 «Bauhaus» ni LO-09 «Cóctel» (de vestir).
- **Precio:** prima de +50–100 € sobre el acabado base (a confirmar).
- **UI:** funciona como un interruptor de edición dentro de la ficha de los modelos elegibles.

## 8. Estructura de cada landing de modelo

1. **Héroe:** foto/render + nombre laOra + categoría + «desde XX €».
2. **La historia** (bloque editorial con foto de contexto; aquí, y solo aquí, se nombra el icono homenajeado una vez).
3. **Por qué es un icono.**
4. **Nuestro tributo.**
5. **Selector de acabados** (tarjetas T1–T4 con foto, specs completas, desglose de coste y precio).
6. **Ficha técnica completa** del acabado elegido: acero, cristal, calibre y origen, estanqueidad en dos registros, medidas, entrecuernos, brazalete.
7. **El proceso de Madrid** + garantía 2 años.
8. **Enlace** al manifiesto «El alma de un automático».

El texto exacto de los 8 modelos está en `laora-copy-web.md`.

## 9. Reglas de marca y legales (imprescindibles)

- **Nombrar iconos solo en «La historia».** Fuera de ese bloque, ninguna marca ajena: ni en H1, ni en `<title>`, ni en `meta description`, ni en `alt` de imágenes, ni en URLs, ni en anuncios. En rejillas y navegación, solo el nombre laOra.
- **Nunca** reproducir logos ni tipografías ajenas. Componentes y esferas **estériles** con marca laOra.
- **Nunca** afirmar "es igual que un [marca] por la décima parte". Se habla de homenaje/tributo y se vende lo nuestro por lo que es.
- **Estanqueidad en dos registros** en toda ficha: dato técnico primero (p. ej. "200 m / 20 bar"), traducción llana después ("en cristiano: …"). Los buceadores no están certificados ISO 6425: no llamarlos "de buceo profesional".
- **Desglose de coste por componente** junto a las tarjetas de acabado: es el argumento central. La transparencia es el producto.
- **PT5000:** se presenta como "el primo del calibre suizo ETA 2824, cuya patente expiró; hoy se fabrica con fidelidad milimétrica cumpliendo los estándares. Pagas la ingeniería suiza, no la etiqueta." (Texto exacto en la ficha del LO-04.)
- **LO-06 y LO-07** (integrados de forma protegida): verificar EUIPO antes de producir. Marcados en rojo en el Excel.

## 10. Requisitos funcionales y técnicos

- **Móvil primero de verdad:** el tráfico vendrá de TikTok/Instagram, en vertical. Recorrido vídeo → ficha → compra con mínima fricción.
- **Rendimiento:** el héroe (vídeo) optimizado (peso, `preload`, poster, lazy del resto), Core Web Vitals cuidados. Una web lenta se percibe como barata.
- **Selector de acabados** que actualiza foto/specs/desglose/precio sin recargar.
- **Formulario Avísame:** nombre, email, WhatsApp (opcional), modelo de interés (desplegable LO-01…LO-09), mensaje opcional, honeypot antispam. Sin pago por adelantado, sin listas de espera falsas. Integración WhatsApp.
- **Cumplimiento:** RGPD, banner de cookies (opción más privada por defecto), condiciones de venta, desistimiento, y términos de garantía. Ojo: la garantía comercial de 2 años **no** sustituye a la garantía legal de conformidad española (más larga) — no redactar nada que lo sugiera.
- **Analítica:** medir recorrido hasta la compra y dónde se cae, no vanidad de visitas.
- **Cero humo técnico:** sin contadores falsos, sin "X personas viendo esto", sin reseñas plantadas.

## 11. Correcciones sobre la web actual (revisión en vivo)

- Cambiar el titular del héroe al nuevo (punto 4) y convertir el héroe en vídeo/animado.
- **Añadir el bloque «Por qué existe laOra — El problema»** debajo del héroe (hoy falta).
- **LO-04 aparece como «Integra»: renombrar a «Precisa»** en toda la web.
- Retirar los carteles **«FOTO EN CAMINO» / «FOTOS EN CAMINO»** donde ya hay render (dan sensación de obra).
- Sincronizar todos los textos con `laora-copy-web.md` (es la versión buena).
- Añadir microinteracciones al hacer scroll (aparición suave de secciones; en las tarjetas, girar el reloj o encender el lume al pasar el ratón).

## 12. Estado y pendientes (no bloquean el maquetado)

- **Fotografía real de producto:** pendiente (hay renders; el vídeo del héroe puede partir de ellos).
- **Sourcing del DLC de la Línea Eclipse** y prima exacta: pendiente de Compras + CFO.
- **Desglose de coste real por modelo/acabado:** pendiente de que el CFO lo cierre; la UI debe dejar el hueco preparado.
- Verificación EUIPO de LO-06 y LO-07 antes de producir.

---

*Fuente única de copy: `laora-copy-web.md`. Fuente única de specs/materiales: `laora-biblioteca-materiales.xlsx`. Referencia visual del héroe: `laora-hero-mockup.html`.*
