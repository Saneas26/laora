# Encargo para el chat de la web · Costes del Trinchera y REGLA Nº1

Reescrito el **29/08/2026** (la versión del 26/08 tenía números de línea
viejos y cuatro dúos que ya no existen). Todo verificado ejecutando el motor
de las fichas fuera del navegador. **No hay que recalcular nada: solo aplicar.**

> ## ⚖️ La regla que manda
>
> **Óscar, 29/08/2026:** «Nunca puede haber ninguna referencia por debajo de
> 50 € o un 15 % de beneficio neto, **jamás**. Si eso ocurre, **que cambia
> todo**. Esa es la regla número 1.»
>
> **Hoy el catálogo la cumple: las 3.498 referencias están por encima.**
> Este encargo baja los costes, y por tanto los precios. Aplicado a medias
> —los costes sí, el suelo no— **rompe 53 referencias**, la peor a 47,05 €
> limpios. Las partes **A** y **B** van en el mismo commit o no van ninguna.

---

## A · ONCE COSTES NUEVOS en `trinchera.html`

Costes de proveedor confirmados por Óscar el 26/08. Cambiar **solo el número**,
sin tocar nombres ni fichas técnicas. Números de línea comprobados a 27/08 sobre
el commit `c6cd8c8`; si no cuadran, buscar por el nombre de la clave.

| Línea | Pieza | Ahora | **Poner** |
|--:|---|--:|--:|
| 543 | `CAJAS.PL` Acero Plata | `coste: 23.00` | **`coste: 18.50`** |
| 544 | `CAJAS.NG` Negra PVD | `coste: 23.00` | **`coste: 18.50`** |
| 545 | `CAJAS.BR` Bronce | `coste: 23.00` | **`coste: 22.60`** |
| 546 | `CAJAS.TI` Titanio | `coste: 54.39` | **`coste: 45.16`** |
| 555 | `ESFERAS.KR` | `coste: 17.29` | **`coste: 16.25`** |
| 556 | `ESFERAS.KB` | `coste: 17.29` | **`coste: 16.25`** |
| 557 | `ESFERAS.MA` | `coste: 21.19` | **`coste: 18.63`** |
| 558 | `ESFERAS.MB` | `coste: 21.19` | **`coste: 18.63`** |
| 559 | `ESFERAS.BRZ` | `coste: 17.29` | **`coste: 16.25`** |
| 587 | `CORREAS.ACERO` | `coste: 19.69` | **`coste: 19.59`** |
| 590 | `CORREAS.ACERONG` | `coste: 26.50` | **`coste: 26.19`** |

**Los cuatro dúos (`DUON`, `DUOM`, `DUOV`, `DUOA`) ya no están** en la tabla de
correas —los quitasteis en `4b37e17`— así que no hay nada que tocar ahí. Si
algún día vuelven, su coste es la suma de las piezas: piel 29,99 + brazalete
19,59 = **49,58**; ante 4,30 + brazalete 19,59 = **23,89**.

**Las esferas de color (blanca, azul, gris) cuestan lo mismo que la negra.**
Óscar: «las esferas del khaki valen todas lo mismo y en el murph también». No
hay que añadir nada.

---

## B · EL SUELO, AL 5 % · **obligatorio y en el mismo commit**

La constante que usa `sueloPvp()` pasa de **`0.025` a `0.05`** en cinco sitios:

| Fichero | Línea | Ahora |
|---|--:|---|
| `precisa.html` | 245 | `var COMISION = 0.025;` |
| `bitacora.html` | 454 | `var COMISION = 0.025;` |
| `lunar.html` | 589 | `var COMISION = 0.025;` |
| `trinchera.html` | 1369 | `var COMISION = 0.025;` |
| `assets/js/configurador-v2.js` | 896 | `var GARANTIA_2026 = 4.00, COMISION_2026 = 0.025, KLARNA_2026 = 1.025;` |

Y el comentario de al lado («5 % de Klarna en la mitad de las ventas») ya no
describe lo que hace: ahora es el 5 % de Klarna **en todas**, porque el cliente
que paga por Klarna no paga la media.

**`KLARNA = 1.025` NO se toca.** Es otra cosa: sube el PVP de tarifa. Lo que
cambia es solo el suelo.

⚠️ **Aviso sobre `configurador-v2.js:1007`.** Ahí `COMISION_2026` no calcula el
suelo, sino el neto que se enseña en el panel de cuentas. Al ponerlo al 5 % ese
panel pasa a mostrar el **peor caso** en vez del promedio. Es más honrado y
Óscar lo prefiere así, pero conviene que lo sepáis antes de que os extrañe la
cifra. Si preferís separar las dos cosas, haced dos constantes; el suelo tiene
que quedar al 5 % igualmente.

---

## C · TRES BOTONES DE COMPRA MUERTOS en `coleccion.html`

Esto **no depende de los precios y está roto en producción ahora mismo.** Tres
tarjetas de la colección llevan referencias con `KR` (segundero rojo), que se
retiró el 24/08. En el catálogo del servidor **hay cero referencias con `KR`**,
así que quien pulse «Añadir al carrito» ahí se lleva un «ya no está a la venta».

- `LO-02-Q-PL39S-KR-NATO-VER` (219,90 €)
- `LO-02-A-PL36C-KR-ACERO` (309,90 €)
- `LO-02-A-PL39C-KR-NATO-VER` (299,90 €)

Sustituir `KR` por `KB` (segundero blanco) es lo natural —misma esfera, mismo
coste, misma foto salvo la aguja—, pero eso es decisión vuestra: lo que no
puede quedarse es la referencia muerta.

---

## D · LOS PRECIOS ESCRITOS A MANO en `coleccion.html`

Hay quince `"precio":` a pelo dentro de los `data-anadir` y `data-var` del
Trinchera. Al aplicar A + B, **nueve cambian**:

| Referencia | Ahora | **Poner** |
|---|--:|--:|
| `LO-02-Q-PL36S-KB-PIELO-NEG-plata` | 219,90 € | **199,90 €** |
| `LO-02-Q-PL36S-KB-ACERO` | 229,90 € | **219,90 €** |
| `LO-02-Q-TI36S-KB-ANTE-CAM` | 269,90 € | **249,90 €** |
| `LO-02-A-PL36C-MA-ANTE-CAM` | 279,90 € | **269,90 €** |
| `LO-02-A-PL36C-KB-PIELO-NEG-plata` | 299,90 € | **289,90 €** |
| `LO-02-Q-TI39S-KB-PIELO-MOS-plata` | 309,90 € | **279,90 €** |
| `LO-02-A-PL36C-MB-PIELN-PB-plata` | 339,90 € | **329,90 €** |
| `LO-02-A-PL36C-MA-PIELM-PB-plata` | 339,90 € | **329,90 €** |
| `LO-02-A-PL39C-MA-PIELN-PB-plata` | 349,90 € | **339,90 €** |
| `LO-02-A-TI39S-KB-ANTE-CAM` (×2) | 359,90 € | **329,90 €** |

`LO-02-Q-PL36S-KB-NATO-VER` se queda en **189,90 €**: baja por el coste y vuelve
a subir por el suelo. Las tres de la sección C no tienen precio nuevo porque no
existen.

---

## E · EL «DESDE» DEL TRINCHERA: 189,90 → **179,90 €**

Tras aplicar A y B, el Trinchera más barato son **179,90 €**, y son
**60 referencias** las que se venden a ese precio. Hay que cambiarlo en dos
sitios:

- `assets/datos/desde.json` → `"trinchera": 179.9`
- `coleccion.html`, **línea 173** → `<li class="cv2-precio-lista">179,90 €</li>`

🚨 **El 189,90 € de la línea 326 es del LUNAR y NO se toca.** Los dos modelos
tienen hoy el mismo «desde», así que un buscar-y-reemplazar se lleva el que no
es. Ir por número de línea.

---

## F · AL TERMINAR, DOS COMPROBACIONES

```bash
node herramientas/auditar_regla1.js
```

Tiene que decir **✅ REGLA Nº1 CUMPLIDA** y salir con código 0. Si sale rojo,
el suelo no se ha aplicado en algún sitio: **no desplegar**.

```bash
node herramientas/volcar_catalogo_2026.js
```

Obligatorio: el servidor cobra por su propia lista, y si no se vuelca, la web
enseñará los precios nuevos y el servidor rechazará las referencias.

---

## Lo que este encargo NO arregla

Datos de compra que no existen todavía en ninguna parte y que Óscar tiene que
dar: la variante exacta de pedido de cada caja, el coste de envío del
proveedor, plazos, mínimos y descuentos por volumen. Y el **grabado del
logotipo (3,78 €)**, que viene de la hoja de materiales vieja y no tiene ni
proveedor ni anuncio detrás.
