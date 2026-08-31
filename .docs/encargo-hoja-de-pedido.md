# Encargo · La hoja de pedido del panel

**Óscar, 30/08/2026:**

> «Cuando yo tenga que hacer un pedido, en mi panel aparece la foto captura de
> pantalla del carrito de compra y las referencias de todos los componentes,
> más las URL de dónde comprar cada componente de esa elección, más los precios
> asignados de compra.»

---

## Qué es

Un cliente compra un Trinchera con caja de acero de 36, esfera Khaki negra,
cuarzo y caucho negro con hebilla mariposa. Eso, para Óscar, no es un reloj:
son **siete compras en cuatro tiendas distintas**. Hoy tiene que reconstruirlas
a mano desde la referencia.

La hoja de pedido lo hace por él: **de la referencia vendida a la lista de la
compra**, con el enlace de cada pieza y lo que se paga por ella.

## Qué tiene que salir

Para **cada línea del pedido**:

1. **La captura del carrito** — la foto de lo que el cliente eligió, tal cual.
2. **La referencia completa** y su desglose en piezas.
3. **Una fila por componente**, y en cada fila:
   - qué pieza es (nombre interno y nombre web),
   - **la URL del anuncio donde se compra**,
   - **la variante exacta que hay que elegir** en ese anuncio,
   - **el precio de compra asignado**,
4. **El total de compra** de ese reloj, y el **margen** contra lo que pagó el
   cliente.
5. **Agrupado por proveedor**, porque se pide por tienda, no por reloj: si dos
   piezas salen del mismo anuncio van juntas y el envío se paga una vez.

Ejemplo de lo que tendría que salir para un Trinchera de cuarzo, acero 36,
Khaki negra, caucho negro y mariposa:

| Componente | Anuncio | Variante | Coste |
|---|---|---|--:|
| Movimiento cuarzo LO_Q6026 | `1005007185210188` | — | 15,05 € |
| Anillo espaciador | `1005007976335088` | — | 3,60 € |
| Caja acero 316, 36 mm | `1005009937589354` | acero · 36 · tapa sólida | 18,50 € |
| Esfera Khaki negra + agujas | `1005007043976717` | negra | 16,25 € |
| Correa de caucho negra | `1005008055142978` | negro | 5,89 € |
| Hebilla mariposa | `1005008996913269` | plata | 2,69 € |
| Grabado del logotipo | **falta** | — | 3,78 € |
| | | **total** | **65,76 €** |

## De dónde salen los datos

**Ya existen casi todos**, y están en dos sitios:

- **`assets/datos/fichas/*.json`** — cada opción con su `coste`. Es la fuente
  de verdad del configurador y del precio.
- **El libro `laOra 2026`, pestaña Piezas** — cada pieza con su **enlace de
  anuncio**, su **variante** y su **coste**.

Lo que falta para poder montarlo es **el puente entre los dos**: hoy el JSON de
la ficha no dice de qué pieza del libro sale cada opción. Hace falta un `pieza`
—el `P-0xx`— en cada opción del JSON, o una tabla aparte que los case.

## 🔴 Sin esto no se puede montar

**Cinco conceptos del Trinchera no tienen anuncio**, así que su fila saldría
vacía:

| Concepto | Coste | Anuncio |
|---|--:|---|
| Grabado del logotipo | 3,78 € | **no hay** |
| Piel vintage | 16,89 € | **no hay** |
| Nato *(el nuevo, de la biblioteca)* | 3,99 € | **no hay** |
| Acero 316L satinado | 20,19 € | **no hay** |
| Piel italiana *(el nuevo)* | 37,39 € | **no hay** |

Y de los que sí tienen anuncio, **falta la variante exacta de pedido** en casi
todos: qué hay que elegir en el desplegable de AliExpress para que llegue la
pieza correcta. Eso está pedido desde el 26/08 y sigue sin darse.

## Por dónde empezar

1. **Cerrar los cinco anuncios que faltan** y las variantes de pedido. Es lo
   que bloquea.
2. **Añadir el `P-0xx` a cada opción** de los JSON de ficha.
3. **Guardar la captura del carrito** con el pedido, que hoy no se guarda.
4. Y ya con eso, la pantalla: es la parte fácil.

Los pasos 1 y 2 son de gestión. El 3 y el 4, del chat de la web.
