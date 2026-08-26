# Encargo para el chat de la web · Precios del Trinchera y norma del suelo

Preparado el **26/08/2026**. Los números están verificados ejecutando el motor
de la ficha fuera del navegador. **No hay que recalcular nada: solo aplicar.**

---

## A · SEIS COSTES NUEVOS en `trinchera.html`

Óscar confirmó estos costes de proveedor el 26/08. Cambiar **solo el número**,
sin tocar nombres ni fichas técnicas.

| Línea | Pieza | Ahora | **Poner** |
|--:|---|--:|--:|
| 499 | `CAJAS.PL` Acero Plata | `coste: 23.00` | **`coste: 18.50`** |
| 500 | `CAJAS.NG` Negra PVD | `coste: 23.00` | **`coste: 18.50`** |
| 501 | `CAJAS.BR` Bronce | `coste: 23.00` | **`coste: 22.60`** |
| 502 | `CAJAS.TI` Titanio | `coste: 54.39` | **`coste: 45.16`** |
| 511 | `ESFERAS.KR` | `coste: 17.29` | **`coste: 16.25`** |
| 512 | `ESFERAS.KB` | `coste: 17.29` | **`coste: 16.25`** |
| 515 | `ESFERAS.BRZ` | `coste: 17.29` | **`coste: 16.25`** |
| 513 | `ESFERAS.MA` | `coste: 21.19` | **`coste: 18.63`** |
| 514 | `ESFERAS.MB` | `coste: 21.19` | **`coste: 18.63`** |
| 543 | `CORREAS.ACERO` | `coste: 19.69` | **`coste: 19.59`** |
| 546 | `CORREAS.ACERONG` | `coste: 26.50` | **`coste: 26.19`** |
| 553 | `CORREAS.DUON` | `coste: 49.68` | **`coste: 49.58`** |
| 554 | `CORREAS.DUOM` | `coste: 49.68` | **`coste: 49.58`** |
| 555 | `CORREAS.DUOV` | `coste: 49.68` | **`coste: 49.58`** |
| 556 | `CORREAS.DUOA` | `coste: 23.99` | **`coste: 23.89`** |

Los cuatro dúos son suma de piezas (piel 29,99 + brazalete 19,59 = 49,58;
ante 4,30 + brazalete 19,59 = 23,89). Si algún día cambia el brazalete, hay que
rehacer los cuatro a mano: el motor no los deriva solo.

**Las esferas de color (blanca, azul, gris) cuestan lo mismo que la negra.**
Óscar: «las esferas del khaki valen todas lo mismo y en el murph también». No
hay que añadir nada.

---

## B · LA NORMA DEL SUELO · las CUATRO fichas, no solo el Trinchera

**Óscar, 26/08/2026: «Ninguna referencia puede bajar bajo ningún concepto de
50 € o del 15 % de beneficio SE VENDA POR EL CANAL QUE SE VENDA.»**

Hasta hoy el suelo se calculaba con una comisión **media** del 2,5 % —la mitad
del 5 % de Klarna, asumiendo que la mitad de las ventas van por ahí—. Pero un
cliente concreto no paga la media: paga el 5 % o paga el 0 %. El suelo se
cumplía en promedio, no en cada venta.

**Cambiar `COMISION` de `0.025` a `0.05` en:**

| Fichero | Línea |
|---|--:|
| `trinchera.html` | 1246 |
| `lunar.html` | 589 |
| `bitacora.html` | 454 |
| `precisa.html` | 245 |
| `assets/js/configurador-v2.js` (`COMISION_2026`) | 896 |

⚠️ **NO tocar `KLARNA = 1.025`.** Es otra cosa: sube el PVP de tarifa un 2,5 %.
El cambio es **solo del suelo**.

Actualizar también el comentario de la línea, que hoy dice «5 % de Klarna en la
mitad de las ventas» y pasa a ser «5 % de Klarna: el suelo se exige con el peor
canal, no con la media».

---

## C · EL «DESDE» DEL TRINCHERA baja a 179,90 €

| Fichero | Qué |
|---|---|
| `assets/datos/desde.json` | `"trinchera": 189.9` → **`179.9`** |
| `coleccion.html:166` | `<li class="cv2-precio-lista">189,90 €</li>` → **`179,90 €`** |

⚠️ Ojo: en `coleccion.html` hay **otro** `189,90 €` en la línea 320 que es del
**Lunar**. Ese NO se toca.

---

## D · AL TERMINAR, OBLIGATORIO

```
node herramientas/volcar_catalogo_2026.js
```

Sin eso, la web enseña los precios nuevos y **el servidor sigue cobrando los
viejos**: rechazará las referencias con «ya no está a la venta». El volcador
avisa por consola de que el Lunar se copia del catálogo anterior (le falta el
manifiesto de fotos); eso es normal y esperado.

---

## Qué va a pasar con los precios · verificado

**Trinchera, 368 referencias:**

| | Hoy | Después |
|---|--:|--:|
| Desde | 189,90 € | **179,90 €** |
| Hasta | 429,90 € | **399,90 €** |
| Precio medio | 330,17 € | **309,90 €** |
| Neto mínimo pagando por Klarna | 50,97 € | **50,50 €** |
| **Referencias que rompen la norma** | 0 | **0** |

**354 bajan · 14 se quedan igual · ninguna sube.** Variación media −20,27 €.

Los tres de portada: Militar 189,90 → **179,90** · Acero 229,90 → **219,90** ·
Murph 349,90 → **339,90**.

**El efecto en Precisa, Lunar y Bitácora está sin medir.** El cambio del suelo
les afecta también, y solo puede SUBIR precios (nunca bajarlos), en las
referencias donde hoy manda el suelo. Conviene revisar sus «desde» después de
volcar.

---

## Lo que NO entra en este encargo

Queda pendiente y sin decidir:

1. **El coste de la tapa de cristal.** Entra en la referencia (`PL36S` sólida /
   `PL36C` de cristal) pero **no suma nada al precio**, en 184 referencias. O
   viene incluida en la caja, o se está regalando.
2. **Faltan los enlaces** del brazalete de acero y del brazalete PVD. Los
   costes valen (los dio Óscar); los anuncios no están.
