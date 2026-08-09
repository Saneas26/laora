# Correcciones a la primera prueba · laOra
### Para el diseñador · 09/08/2026

---

Hemos montado tus dos archivos en la web y funciona. Antes de que dispares las 260 restantes, hay **dos cosas que corregir**. Las dos son medibles, así que no hay interpretación posible: o el número sale o no sale.

## Lo que está perfecto y no hay que tocar

- Lienzo de la cabeza: **1000 × 1000**. Correcto.
- Lienzo del brazalete: **1000 × 2400**. Correcto.
- **PNG con transparencia real** en los dos. Correcto, y es lo que más fallos suele dar.
- Nombres de archivo con la referencia: `LO-03-C1-E1.png` y `Brz-316-A01.png`. Correcto.
- **Las puntas de las asas caen exactamente en y = 200 y en y = 800.** Clavado.
- **El hueco del brazalete empieza en y = 898 y acaba en y = 1500.** Clavado.

El encaje vertical es perfecto. Eso era lo difícil y está resuelto: no cambies nada de eso.

---

## CORRECCIÓN 1 · El brazalete tiene que ser más ancho

El hueco entre las asas de la cabeza mide **266 píxeles**. El brazalete que has entregado mide **222**. Le faltan 44 px, un 16 %.

El resultado es que la correa flota dentro de las asas con 22 px de aire a cada lado, y se ve.

> **El ancho del brazalete a la altura del asa tiene que ser 266 px exactos: de x = 367 a x = 633.**

Es el mismo número que el hueco entre las asas de la cabeza. **Si esos dos números no son idénticos, el montaje canta.** En las plantillas está marcado con dos líneas verdes.

La causa probable es que la cabeza y el brazalete se fotografiaron a distancias distintas. Las dos piezas miden 20 mm de ancho de asa en la realidad: en la foto tienen que medir los mismos píxeles.

---

## CORRECCIÓN 2 · Centrar por las asas, no por el contorno

La cabeza está centrada por el rectángulo que la envuelve. Pero **la corona y los pulsadores sobresalen por la derecha**, así que ese rectángulo está descentrado respecto al reloj: el eje real de las asas cae en **x = 478** en vez de en 500.

Son 22 px, y hacen que el brazalete pegue con el asa derecha y deje hueco en la izquierda.

> **Lo que hay que centrar en x = 500 es el eje por donde entra la correa**, es decir, el punto medio entre las dos asas. La corona y los pulsadores quedan donde caigan.

Se comprueba fácil: mide el hueco entre las dos asas y comprueba que su punto medio está en x = 500.

---

## Lo que sigue igual

- **Trípode fijo**: misma altura, distancia y óptica en las 262 tomas.
- **Misma luz** en todas, sin tocar nada entre tomas.
- **Fondo transparente** de verdad, nunca blanco recortado.
- **Lienzos**: 1000 × 1000 la cabeza, 1000 × 2400 el brazalete. **No los cambies**: la geometría ya cuadra a este tamaño y cambiar de escala ahora rompería lo único que está bien. Guarda los originales de cámara por si algún día hiciera falta más resolución.
- **Nombre de archivo = referencia**, tal como viene en la columna `Referencia` del CSV. Sin acentos, sin espacios, sin cambiar mayúsculas.
- Las **cabezas** se fotografían con la esfera y las agujas ya montadas. Las esferas no se pueden añadir después.
- Los **brazaletes** se fotografían solos, extendidos en vertical y con el hueco del centro vacío.

---

## Cómo comprobarlo tú antes de mandarlo

Con la regla de Photoshop, sobre el PNG a tamaño real:

**En una cabeza**
1. Mide el hueco entre las dos asas por su parte más alta → tiene que dar **266 px**.
2. El punto medio de ese hueco → tiene que estar en **x = 500**.
3. La punta de las asas → **y = 200** arriba, **y = 800** abajo.

**En un brazalete**
1. Ancho a la altura del hueco → **266 px**, de x = 367 a x = 633.
2. El hueco vacío → de **y = 900** a **y = 1500**.
3. Centro del hueco → **x = 500**.

Si esos seis números salen, la foto encaja. Si alguno falla, no encaja, y se nota en pantalla.

---

## Qué mandar ahora

**Solo dos archivos otra vez**: la misma cabeza y el mismo brazalete, corregidos. Los montamos, los miramos y, si cuadran, ya vas a por las 260 restantes con la seguridad de que el sistema funciona.

No dispares el resto hasta que estos dos den el visto bueno.

---

## Archivos

| Qué | Ruta |
|---|---|
| Encargo completo | `.docs/marketing/ENCARGO-FOTOS.md` |
| Listado de las 262 fotos | `.docs/marketing/laora-fotos-encargo.csv` |
| Plantilla de cabeza | `.docs/marketing/plantilla-cabeza.svg` |
| Plantilla de brazalete | `.docs/marketing/plantilla-brazalete.svg` |
| Estas correcciones | `.docs/marketing/CORRECCIONES-PRUEBA-01.md` |

Las dos plantillas ya llevan dibujada la franja verde de 266 px con sus coordenadas. Cárgalas como capa encima de cada toma y cuadra el reloj dentro.
