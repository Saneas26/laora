# La hoja «Catalogo laOra» manda

06/08/2026. Óscar:

> «la hoja del sheet pasa a ser lo que manda por encima de cualquier dato
> que tengas historico»

Fuente: hoja «Catalogo laOra» del libro
`1hOEjyzjzHewt-CThFyJWeIREw6J56Rj5gEmc2w5z0cc`, leída entera.
**52 referencias · 8 modelos.**

El volcado lo hace `herramientas/volcar_hoja.py` y es repetible: cuando
la hoja cambie, se vuelve a pasar.

## Lo que se ha volcado

| Modelo | Acabados | Opciones | Referencias | Desde |
|---|---:|---:|---:|---:|
| LO-02 Cero Cero | 6 | 4 | 6 | 189,90 € |
| LO-04 Precisa | 4 | 1 | 4 | 199,90 € |
| LO-07 Bitácora | 6 | 4 | 7 | 189,90 € |
| LO-08 Tortuga | 4 | 2 | 4 | 219,90 € |
| LO-09 Cóctel | 3 | 1 | 3 | 189,90 € |

Las 24 referencias publicadas existen en la hoja, una por una, con su
precio y su movimiento. El Tortuga y el Cóctel estrenan pantalla de
comprar: antes solo tenían la ficha antigua, sin precio ni configurador.

## Lo que se ha corregido

Estaba publicado y no salía de la hoja:

| Modelo · acabado | Estaba | Ahora | |
|---|---:|---:|---|
| Precisa Eclipse | 169,90 | **379,90** | se vendía por debajo del coste |
| Precisa Cenit | 219,90 | 379,90 | |
| Precisa Alba | 169,90 | 199,90 | |
| Precisa Levante | 219,90 | 229,90 | |
| Cero Cero Cenit | 249,90 | 339,90 | |
| Cero Cero Levante | 239,90 | 249,90 | |
| Cero Cero Alba | 209,90 | 189,90 | |
| Bitácora Cenit | 239,90 | 319,90 | |
| Bitácora Alba | 199,90 | 189,90 | |

Y los movimientos. La web repartía cada acabado en dos o tres calibres
que la hoja no tiene; la hoja da **un solo Cenit por modelo**:

| Modelo | Cenit |
|---|---|
| Cero Cero | Miyota 9015 |
| Precisa | Miyota 9015 |
| Bitácora | Miyota 9015 |

## Lo que se ha quitado

- **El Bauhaus.** No está en la hoja. Se le quitan el configurador y el
  precio: publicaba 169,90 y 199,90 € que no salían de ninguna parte. Su
  ficha sigue en pie, y en el listado enseña el diámetro, como hace
  siempre que no hay precio cerrado.
- **El Cenit del Tortuga** (`LO-08_Tortuga_C01`, 449,90 €). La hoja lo
  marca «por confirmar/proveedor pendiente». No se pone a la venta un
  reloj cuyo movimiento no está cerrado. En cuanto se confirme, entra
  solo con volver a pasar el volcado.

## Lo que la hoja trae y no sale a la web

El volcado filtra lo que es de casa: enlaces a proveedores, coste,
subtotales, margen, y los avisos internos —«No declarado por el
vendedor ⚠», «según ficha del vendedor», «requiere anillo espaciador
para el VH31»—. Una celda que solo diga eso se queda vacía, y una línea
vacía no se pinta: no hay ningún «por confirmar» a la vista.

También se quitan **las marcas de otras casas**. La hoja describe las
cajas por el reloj al que se parecen —«tonneau estilo PRX», «textura
Grenade (estilo Aquanaut)», «para Rolex SUBMARINER»— porque así se le
piden al proveedor. En la web no se nombra a otra marca ni se dice a qué
se parece: es lo que separa un homenaje de una copia.

## Lo que queda pendiente, y depende de Óscar

### 1. El Trinchera: dos celdas que se contradicen

Es el único modelo que no se ha podido volcar, y no por poco: sus 15
referencias son las que más dinero mueven mal (su Cenit está publicado a
209,90 € cuando la hoja dice **289,90 € con PT5000**, un movimiento que
en la web no aparece por ningún sitio; y le falta entero el **Levante,
249,90 € con Seagull ST2130**, cuatro referencias).

Lo que hay que arreglar en la hoja:

| Fila | Celda | Qué dice | El problema |
|---|---|---|---|
| `LO-05_Trinchera_A01` | Caja — Material | «Acero inoxidable 316L, PVD negro» | Es un **Alba**, y su «Caja/conjunto» dice «39mm **plata** solido». Su foto de catálogo es plateada. Parece copiada de la fila Eclipse. |
| `LO-05_Trinchera_L01` | Caja/conjunto | «G30» | Es un código, no una descripción. Las otras tres Levante dicen la caja entera. |

Con esas dos celdas puestas, el Trinchera se vuelca solo.

### 2. El Eclipse en oro rosa del Bitácora

`LO-07_Bitacora_E01-OR` está en la hoja como **Eclipse con caja PVD oro
rosa**, 189,90 €. Choca de frente con la regla que fijaste: «las
variantes Eclipse van completamente negras, esfera incluida».

**Se ha volcado tal como dice la hoja**, porque la hoja manda. Pero es
una excepción a una regla tuya y conviene que la mires: o la referencia
deja de llamarse Eclipse, o la regla cambia.

### 3. El DIVER (LO-06) no tiene sitio en la web

Cuatro referencias en la hoja, de 219,90 a 289,90 €, y una foto de
catálogo. No existe en `catalogo.json` ni en la colección: darle de alta
es sacar un modelo nuevo a la calle, y eso lo decides tú.

| Referencia | Acabado | Movimiento | PVP |
|---|---|---|---:|
| LO-06_Diver_A01 | Alba | VH31 cuarzo de barrido | 219,90 € |
| LO-06_Diver_L01 | Levante | Seiko NH35A | 289,90 € |
| LO-06_Diver_C01 | Cenit | PT5000 | 279,90 € |
| LO-06_Diver_E01 | Eclipse | PT5000 | 279,90 € |

Ojo a una cosa: su **Cenit cuesta menos que su Levante** (279,90 frente
a 289,90). Por la escalera que fijaste, el Cenit es el máximo del modelo
y debería ir por encima.

### 4. Textos que se han quedado sin frase

El `resumen` de cada acabado —la línea que lo explica en una frase— lo
escribió el equipo, no la hoja. Se ha conservado solo donde el calibre
no ha cambiado. Donde el movimiento es otro, la frase describía un
movimiento que ya no es y se ha caído: antes sin texto que con un texto
que miente. Los que hay que volver a escribir son los Cenit del Cero
Cero, el Precisa y el Bitácora, y los Eclipse que han cambiado de
calibre.
