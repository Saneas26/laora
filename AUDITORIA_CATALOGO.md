# La hoja «Catalogo laOra» manda

Última pasada: 06/08/2026, después de las correcciones de Óscar.

> «la hoja del sheet pasa a ser lo que manda por encima de cualquier dato
> que tengas historico»

Fuente: hoja «Catalogo laOra» del libro
`1hOEjyzjzHewt-CThFyJWeIREw6J56Rj5gEmc2w5z0cc`, leída entera.
**51 referencias · 8 modelos.**

El volcado lo hace `herramientas/volcar_hoja.py` y es repetible: cuando
la hoja cambie, se vuelve a pasar y se regenera.

## Estado: 48 de 51 referencias publicadas

**Las 48 coinciden con su fila de la hoja en referencia Y precio**, una
a una, y cada una enseña su propia foto de catálogo.

| Modelo | Acabados | Opciones | Refs | Desde |
|---|---:|---:|---:|---:|
| LO-01 Lunar | 3 | 8 | 8 | 219,90 € |
| LO-02 Cero Cero | 6 | 4 | 6 | 209,90 € |
| LO-04 Precisa | 4 | 1 | 4 | 229,90 € |
| LO-05 Trinchera | 6 | 9 | 15 | 189,90 € |
| LO-07 Bitácora | 6 | 4 | 7 | 219,90 € |
| LO-08 Tortuga | 5 | 2 | 5 | 219,90 € |
| LO-09 Cóctel | 3 | 1 | 3 | 209,90 € |

Comprobado además en las siete pantallas: cero marcas ajenas, cero
«clon», cero «⚠», cero «no declarado», cero notas de taller, cero
códigos de proveedor, cero textos rotos, cero fotos que falten. Y las
siete caben en una pantalla de teléfono de 375 × 812.

## Las decisiones de Óscar del 06/08/2026, aplicadas

**El Trinchera en Alba es plata o bronce; el PVD negro es solo del
Eclipse.** Aplicado y comprobado: ninguna combinación de Alba, Levante
o Cenit lleva caja negra, y ninguna Eclipse lleva otra cosa. Sus 15
referencias están publicadas.

**El Cenit del Tortuga se pone a la venta.** 449,90 € con el Seiko NE15.
Era la única fila que quedaba fuera por llevar «por confirmar» dentro de
la celda del calibre.

**El Eclipse en oro rosa del Bitácora se queda.** Excepción aceptada a
la regla de que los Eclipse van completamente negros: brazalete y todo
lo demás en negro, la caja en oro rosa. `LO-07_Bitacora_E01-OR`,
219,90 €.

**El DIVER ya no tiene la escalera al revés.** La hoja quitó el
`LO-06_Diver_L01` y pasó el `C01` a Levante.

## Lo que sigue fuera

Solo el **DIVER (LO-06)**: tres referencias que no existen en
`catalogo.json` ni en la colección.

| Referencia | Acabado | Movimiento | PVP |
|---|---|---|---:|
| LO-06_Diver_A01 | Alba | VH31 cuarzo de barrido | 229,90 € |
| LO-06_Diver_C01 | **Levante** | Seiko NH35A | 289,90 € |
| LO-06_Diver_E01 | Eclipse | PT5000 | 279,90 € |

Dos cosas antes de darlo de alta:

1. **Solo hay una foto de catálogo del DIVER**, la del Alba. Su Eclipse
   saldría con un reloj plateado, y un Eclipse es negro entero.
2. **La referencia del Levante empieza por C**, de Cenit:
   `LO-06_Diver_C01`. Conviene renombrarla a `L01` antes de publicarla,
   porque la referencia es lo que va en el pedido.

## Lo que la hoja todavía dice mal

`herramientas/arreglar_hoja.gs` deja las cuatro celdas bien de una
pasada: se abre el libro, Extensiones → Apps Script, se pega y se
ejecuta. Mientras tanto la web las corrige al vuelo con la tabla
`CORRECCIONES` de `volcar_hoja.py`, que se borra en cuanto la hoja esté
al día.

| Fila | Celda | Dice | Debería decir |
|---|---|---|---|
| `LO-05_Trinchera_A01` | Caja — Material | Acero 316L, **PVD negro** | Acero 316L, plata |
| `LO-05_Trinchera_A01` | Caja — Acabado | **PVD negro** mate/cepillado | Acero pulido/cepillado (plata) |
| `LO-05_Trinchera_A01` | Brazalete — Tipo de cierre | **BK25** | Hebilla de acero |
| `LO-05_Trinchera_A01` | Y (correa) | …bal**í**stico… | igual que las otras: sin tilde partía la opción en dos |
| `LO-05_Trinchera_L01` | Caja — Material y Acabado | **PVD negro** | plata |
| `LO-08_Tortuga_C01` | Movimiento — Calibre | Seiko NE15 — **por confirmar/proveedor pendiente** | Seiko NE15 (equiv. 6R15) |

### Y una que no puedo decidir yo

`LO-08_Tortuga_C01` **nombra dos movimientos distintos**:

- columna «Movimiento»: Seiko **NH36A** automático (con fecha larga)
- columna «Movimiento — Calibre»: Seiko **NE15** (equiv. 6R15)

Los demás datos de esa fila —23 rubíes, 21.600 vph, ~50 h de reserva—
son los del NE15, no los del NH36A, así que la web publica **NE15**. Es
también lo coherente con que sea el reloj más caro de la casa. Pero hay
que decidirlo y dejar las dos columnas iguales.

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
- **Notas de compras dentro del dato**: «— por confirmar/proveedor
  pendiente». Se borran del texto y se listan al final del volcado para
  que se limpien en la hoja.
- **Códigos de proveedor** donde debería haber una descripción: «BK25»,
  «G30».
- **Marcas de otras casas**: la hoja describe las cajas por el reloj al
  que se parecen —«tonneau estilo PRX», «para Rolex SUBMARINER»— porque
  así se le piden al proveedor. En la web no se nombra a otra marca ni
  se dice a qué se parece.
- **«Clon» y «réplica»**, y de qué calibre ajeno es copia cada
  movimiento: la hoja pone «Seagull ST2130 (Tianjin, clon ETA 2824-2)»;
  la web, «Seagull ST2130».
