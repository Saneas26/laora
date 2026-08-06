# La hoja «Catalogo laOra» manda

Última pasada: 06/08/2026, con la hoja actualizada. Óscar:

> «la hoja del sheet pasa a ser lo que manda por encima de cualquier dato
> que tengas historico»

Fuente: hoja «Catalogo laOra» del libro
`1hOEjyzjzHewt-CThFyJWeIREw6J56Rj5gEmc2w5z0cc`, leída entera.
**52 referencias · 8 modelos.**

El volcado lo hace `herramientas/volcar_hoja.py` y es repetible: cuando
la hoja cambie, se vuelve a pasar y se regenera.

## Estado: 45 de 52 referencias publicadas

**Las 45 coinciden con la hoja en referencia Y precio**, comprobadas una
a una contra la fila de la que salen. Cada una enseña además su propia
foto de catálogo.

| Modelo | Acabados | Opciones | Refs | Desde |
|---|---:|---:|---:|---:|
| LO-01 Lunar | 3 | 8 | 8 | 219,90 € |
| LO-02 Cero Cero | 6 | 4 | 6 | 209,90 € |
| LO-04 Precisa | 4 | 1 | 4 | 229,90 € |
| LO-05 Trinchera | 6 | 8 | 13 | 189,90 € |
| LO-07 Bitácora | 6 | 4 | 7 | 219,90 € |
| LO-08 Tortuga | 4 | 2 | 4 | 219,90 € |
| LO-09 Cóctel | 3 | 1 | 3 | 209,90 € |

Comprobado también, en las siete pantallas: cero apariciones de marcas
ajenas, de «clon», de «⚠», de «no declarado», de notas de taller o de
cifras de coste. Cero textos rotos. Cero fotos que falten.

## Los precios de esta pasada

La hoja subió 23 precios. Todos están ya publicados. Los que más
cambian respecto a lo que había en la web antes de auditar:

| Modelo · acabado | Publicaba | Hoja |
|---|---:|---:|
| Precisa Eclipse | 169,90 | **379,90** |
| Precisa Cenit | 219,90 | 379,90 |
| Bitácora Cenit | 239,90 | 349,90 |
| Cero Cero Cenit | 249,90 | 359,90 |
| Trinchera Cenit | 209,90 | 289,90 |
| Precisa Alba | 169,90 | 229,90 |
| Bitácora Alba | 199,90 | 219,90 |

Con los precios nuevos, **ninguna referencia queda por debajo del coste
ni del mínimo de 50 € y 15 %** que fija la propia hoja. Antes de esta
auditoría, el Eclipse del Precisa se vendía a 169,90 € cuando cuesta
195,37 € con IVA.

## Lo que sigue fuera, y por qué

| Referencia | PVP | Motivo |
|---|---:|---|
| `LO-05_Trinchera_A01` | 189,90 | la hoja se contradice (ver abajo) |
| `LO-05_Trinchera_L01` | 249,90 | la hoja se contradice (ver abajo) |
| `LO-08_Tortuga_C01` | 449,90 | movimiento «por confirmar/proveedor pendiente» |
| `LO-06_Diver_A01` | 229,90 | el DIVER no existe en la web |
| `LO-06_Diver_L01` | 289,90 | ídem |
| `LO-06_Diver_C01` | 279,90 | ídem |
| `LO-06_Diver_E01` | 279,90 | ídem |

El **Bauhaus** tampoco está: no aparece en la hoja. Se le han quitado el
configurador y el precio, y en el listado enseña el diámetro.

## Los cuatro errores que quedan en la hoja

### 1. El Trinchera: dos celdas que se contradicen

| Fila | Celda | Qué dice | El problema |
|---|---|---|---|
| `LO-05_Trinchera_A01` | Caja — Material | «Acero inoxidable 316L, PVD negro» | Es un **Alba**, y su «Caja/conjunto» dice «39mm **plata** solido». Su foto de catálogo es plateada. Parece copiada de la fila Eclipse. |
| `LO-05_Trinchera_L01` | Caja/conjunto | «G30» | Es un código, no una descripción. Las otras tres Levante describen la caja entera. |

Las otras 13 referencias del Trinchera **ya están publicadas**: con esas
dos celdas puestas, entran solas al volver a pasar el volcado.

### 2. El Cenit del Tortuga sigue sin cerrar

`LO-08_Tortuga_C01`, 449,90 €, el reloj más caro de la casa. La hoja
dice «Seiko NH36A automático» y a la vez «por confirmar/proveedor
pendiente». No se pone a la venta un reloj cuyo movimiento no está
cerrado.

### 3. Un Eclipse en oro rosa

`LO-07_Bitacora_E01-OR`, 219,90 €, **Eclipse con caja PVD oro rosa**.
Choca de frente con tu regla: «las variantes Eclipse van completamente
negras, esfera incluida».

Está publicado como dice la hoja, porque la hoja manda. Pero es una
excepción a una regla tuya: o la referencia deja de llamarse Eclipse, o
la regla cambia.

### 4. El DIVER tiene la escalera al revés

Su **Cenit cuesta menos que su Levante**: 279,90 frente a 289,90 €. Por
la escalera que fijaste, el Cenit es el máximo del modelo y va por
encima de todo. Es el único de los ocho modelos donde pasa.

| Referencia | Acabado | Movimiento | PVP |
|---|---|---|---:|
| LO-06_Diver_A01 | Alba | VH31 cuarzo de barrido | 229,90 € |
| LO-06_Diver_L01 | Levante | Seiko NH35A | 289,90 € |
| LO-06_Diver_C01 | Cenit | PT5000 | **279,90 €** |
| LO-06_Diver_E01 | Eclipse | PT5000 | 279,90 € |

Dar de alta el DIVER es sacar un modelo nuevo a la calle, y eso lo
decides tú.

## Textos que hay que volver a escribir

El `resumen` de cada acabado —la frase que lo explica— lo escribió el
equipo, no la hoja. Se conserva solo donde el calibre no ha cambiado.
Donde el movimiento es otro, la frase describía un calibre que ya no es
y se ha caído: antes sin texto que con un texto que miente.

Sin frase se han quedado los Cenit del Cero Cero, el Precisa y el
Bitácora, y los Eclipse que han cambiado de calibre.

## Lo que el volcado no deja pasar

- **Coste, margen, subtotales y enlaces de proveedor**: no se copian.
- **Avisos internos**: «No declarado por el vendedor ⚠», «según ficha
  del vendedor». La celda se queda vacía y la línea no se pinta.
- **Notas de taller**: «requiere anillo espaciador para el VH31»,
  «asiento NH3x», «ajuste directo PT5000».
- **Marcas de otras casas**: la hoja describe las cajas por el reloj al
  que se parecen —«tonneau estilo PRX», «para Rolex SUBMARINER»— porque
  así se le piden al proveedor. En la web no se nombra a otra marca ni
  se dice a qué se parece.
- **«Clon» y «réplica»**, y de qué calibre ajeno es copia cada
  movimiento: la hoja pone «Seagull ST2130 (Tianjin, clon ETA 2824-2)»;
  la web, «Seagull ST2130».
