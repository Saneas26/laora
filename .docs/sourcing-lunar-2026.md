# laOra · Lunar 2026 · hoja de compra

Abierto el **27/08/2026**, con los datos que dio Óscar ese día. El Lunar se
trabaja ahora porque es el turno del modelo — ver `laora-modelo-a-modelo`.

> **Estado: el Lunar NO está a la venta.** `lunar.html` tiene
> `COSTES_PUESTOS = false` y todos sus `coste: 0`, así que el volcador lo deja
> fuera del catálogo del servidor: **0 referencias**. Hasta que estos costes
> entren en la ficha, no se puede vender ni un Lunar.

---

## 1 · Lo que dijo Óscar, tal cual

### Caja con ZAFIRO — 48,99 € · 100 metros
[1005012226039294](https://es.aliexpress.com/item/1005012226039294.html)

Viene montada, con esfera y agujas dentro. **Sólo dos combinaciones:**

| Caja | Bisel | Esfera | Agujas |
|---|---|---|---|
| Acero | Negro | Negra | Blancas |
| Acero | Azul | Blanca | Azules |

### Caja con MINERAL — 34,59 € · «como ya teníamos»
[1005007892634303](https://es.aliexpress.com/item/1005007892634303.html) ·
FJ wrist watch store · captura del 16/08 en
`herramientas/capturas/2026-08-16-1005007892634303.json`

Viene montada, con esfera y agujas dentro. **Siete combinaciones:**

| # | Caja | Bisel | Esfera | Agujas |
|--:|---|---|---|---|
| 1 | Acero | Negro | Negra | Blancas |
| 2 | Acero | Negro | Naranja | Naranjas |
| 3 | Acero | Negro | Dorada | Doradas |
| 4 | Acero | Azul | Blanca | Azules |
| 5 | Acero | Negro | Oro rosa | Oro rosa |
| 6 | Acero | **Blanco** | Oro rosa | Oro rosa |
| 7 | Acero | **Blanco** | Panda | Blancas |

De la **nº 6** dio además el desglose por piezas: **esfera 8,99 · agujas 4,79 ·
caja + bisel 23,79**.

### Brazalete de acero — 19,79 €, aparte
No va dentro de ninguna de las cajas de arriba.

### Caja PVD — 48,99 €
Caja PVD + bisel negro + **brazalete PVD** incluido. **Esfera y agujas aparte.**

---

## 2 · Qué cuesta cada cosa, y qué ha subido

Comparado con la captura del 16/08 del mismo proveedor:

| Pieza | SKU | 16/08 | **27/08** | |
|---|---|--:|--:|---|
| Caja montada acero (mineral) | NO.23…NO.44 | 34,59 € | **34,59 €** | igual |
| Caja vacía acero, bisel negro | NO.1 | 23,79 € | **23,79 €** | igual |
| Brazalete de acero | NO.10 | 19,69 € | **19,79 €** | +0,10 |
| Esfera suelta | NO.30 | 7,69 € | **8,99 €** | **+1,30** |
| Juego de agujas | NO.38…NO.42 | 4,09 € | **4,79 €** | **+0,70** |
| Caja vacía acero, bisel azul | NO.8 | 26,39 € | sin dato | |
| Caja vacía PVD, bisel negro | NO.13 | 29,59 € | *(dentro del pack de 48,99)* | |
| Brazalete PVD | NO.20 | 26,39 € | *(dentro del pack de 48,99)* | |
| **Caja montada acero con ZAFIRO** | — | no existía | **48,99 €** | anuncio nuevo |

**El pack de PVD sale a cuenta:** por piezas serían 29,59 + 26,39 = 55,98 €, y
el pack son **48,99 €** — casi 7 € menos.

### ⚠️ Montar a piezas cuesta MÁS que comprarla montada

23,79 + 8,99 + 4,79 = **37,57 €**, frente a los **34,59 €** de la caja montada.
Son **2,98 € más**. Ya pasaba en agosto (35,57 frente a 34,59) y la diferencia
ha crecido porque han subido la esfera y las agujas, no la caja.

**Consecuencia para el precio:** montar a piezas sólo se hace cuando el
proveedor NO vende esa combinación ya montada. La nº 6 —bisel blanco con esfera
oro rosa— es de ésas, así que **no cuesta 34,59 sino 37,57**, y hay que costearla
aparte en vez de meterla en el saco de las montadas.

---

## 3 · Lo que hace falta para poner precio

**Falta un solo dato y sin él no hay precio: el coste del movimiento.**

`lunar.html` tiene `MOVS.MQ.coste = 0`. El Lunar monta el **LO_MQ326**,
mecacuarzo japonés de arquitectura **VK63**, y el anuncio de las cajas dice
expresamente *«movimiento NO incluido»*. En todo el repo no hay ni un precio de
VK63: ni en las capturas, ni en el sourcing, ni en el libro.

Lo demás del motor ya está: logo 3,78 · packing y envío 9 (con IVA) · garantía
4 · SS 5 % · multiplicador 2,28 · IVA 21 % · IRPF 20 %, y el suelo de la
**regla nº1** (50 € limpios o 15 % neto medido con Klarna al 5 %).

### Lo que costaría cada versión, sin el movimiento

Piezas, ya sumado el logo de 3,78 €:

| Versión | Caja | Correa | Piezas sin movimiento |
|---|--:|--:|--:|
| Acero · mineral · montada | 34,59 | 19,79 | **58,16 €** |
| Acero · mineral · a piezas (bisel blanco + oro rosa) | 37,57 | 19,79 | **61,14 €** |
| Acero · **zafiro** · montada | 48,99 | 19,79 | **72,56 €** |
| **PVD** · mineral · pack con brazalete | 48,99 | incl. | **53,77 €** + esfera y agujas |

El PVD sale **más barato que el acero con zafiro** aun llevando el brazalete
dentro, pero le faltan esfera y agujas: si son las sueltas (8,99 + 4,79), se
queda en **67,55 €**, todavía por debajo del zafiro.

---

## 4 · Lo que falta por confirmar

1. **El coste del movimiento VK63 / LO_MQ326.** Bloquea todo.
2. **El zafiro de 48,99, ¿lleva brazalete?** Por cómo funciona el otro anuncio
   diría que no, y así está contado arriba. Si lo lleva, esa versión baja
   19,79 €.
3. **La esfera y las agujas del PVD, ¿son las sueltas de 8,99 y 4,79?** Y con
   qué colores se ofrece.
4. **«Dorada» y «oro rosa», ¿son dos acabados distintos o el mismo?** Óscar
   nombró los dos en la misma lista, y en la captura de agosto sólo hay un
   juego de agujas doradas (NO.42). En la ficha hay una sola entrada, `ORO`.
5. **«Bisel blanco», ¿es el «bisel plateado» de la captura de agosto?** Los
   montajes nº 6 y nº 7 encajan con las piezas P-001 y P-007, que la captura
   describe como *bisel taquimétrico plateado*.
6. **El enlace de las cajas con zafiro** llega sin captura. Hay que hacerla
   antes de comprar: variantes, envío, mínimos y descuento por volumen.
7. **Envío y descuentos.** Del proveedor de mineral se sabe: envío **4,52 €**,
   **−5 % desde 5 unidades**, mínimo 1, devoluciones gratis 90 días, y los
   precios de agosto llevaban un **−50 %** de promoción que hay que
   reverificar en sesión limpia antes de pedir.

---

## 5 · El configurador no está montado para esto

`lunar.html` calcula el coste sumando dimensiones sueltas:

```js
MOVS[mov].coste + CAJAS[caja].coste + CRISTALES[cristal].coste +
ESFERAS[esf].coste + BISELES[bisel].coste + AGUJAS[agujas].coste +
CORREAS[correa].coste + LOGO
```

Pero el proveedor **no vende dimensiones sueltas: vende paquetes.** La caja
montada de 34,59 € ya trae bisel, esfera y agujas dentro, y sólo existe en siete
combinaciones. El zafiro, en dos. Repartir esos 34,59 € entre cuatro casillas
haría que cualquier combinación que el proveedor no venda saliera con un precio
inventado.

**Hace falta que el coste salga de una tabla de paquetes**, no de una suma de
casillas: la combinación completa decide qué se compra y a cuánto. Es un cambio
del motor de la ficha, y lo lleva el chat de la web. Aquí queda el dato.

---

## 6 · Qué PVP saldría, según lo que cueste el movimiento

Con el motor de siempre y el suelo de la regla nº1. Entre paréntesis, lo que
queda **limpio pagando por Klarna**.

| Movimiento | Acero · mineral · montada | Acero · mineral · a piezas | Acero · **zafiro** | **PVD** · pack + esfera y agujas |
|--:|---|---|---|---|
| 10,00 € | 189,90 € (51,10) | 199,90 € (54,80) | 229,90 € (63,85) | 209,90 € (56,47) |
| 15,00 € | 199,90 € (53,11) | 209,90 € (56,82) | 239,90 € (65,86) | 219,90 € (58,48) |
| 20,00 € | 209,90 € (55,12) | 219,90 € (58,83) | 249,90 € (67,87) | 229,90 € (60,49) |
| 25,00 € | 229,90 € (63,34) | 229,90 € (60,84) | 259,90 € (69,88) | 249,90 € (68,72) |
| 30,00 € | 239,90 € (65,35) | 249,90 € (69,06) | 269,90 € (71,89) | 259,90 € (70,73) |
| 35,00 € | 249,90 € (67,36) | 259,90 € (71,07) | 279,90 € (73,90) | 269,90 € (72,74) |
| 40,00 € | 259,90 € (69,38) | 269,90 € (73,08) | 299,90 € (82,13) | 279,90 € (74,75) |

Todas las filas cumplen la regla nº1: en el peor caso —movimiento a 10 € y
caja montada— quedan 51,10 € limpios. **Ninguna versión del Lunar se cae por
abajo, cueste lo que cueste el movimiento.**

La portada anuncia hoy el Lunar a **219,90 €**. Eso encaja con un movimiento
de entre 20 y 25 € en la versión de acero, mineral y montada.
