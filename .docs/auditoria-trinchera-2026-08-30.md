# Auditoría del Trinchera · 30/08/2026

Proveedores, piezas, costes y PVP. Todo medido ejecutando el motor real con
`herramientas/volcar_catalogo_2026.js` y `herramientas/auditar_regla1.js`.

---

## 1 · Lo primero: la regla nº1 está limpia

**14.728 referencias, ninguna por debajo de 50 € limpios ni del 15 % neto**,
midiendo con Klarna al 5 %.

Se arregló hoy. Mi auditor llevaba desde el 29/08 diciendo verde **sin medir
nada**: el motor de precio se había ido de las fichas a
`assets/js/precio-2026.js` y el parche del suelo ya no llegaba. Arreglado el
auditor, salieron **192 referencias rotas**, y el chat de la web subió el suelo
al 5 % en el commit `5bef947`. Esas 192 subieron 10 €.

El auditor ahora **aborta** si no encuentra la constante, en vez de callar.

---

## 2 · El Trinchera ya no es el de ayer

| | Ayer 29/08 | **Hoy 30/08** |
|---|--:|--:|
| Referencias | 1.506 | **10.240** |
| PVP | 189,90 – 429,90 € | **189,90 – 449,90 €** |

Se rehízo de cero: la ficha se genera desde
`assets/datos/fichas/trinchera.json` y el configurador es el de la casa. Y
viste **las correas oficiales del Lunar** —ocho familias, treinta y seis
colores—, no las suyas de antes.

**Consecuencia:** `.docs/encargo-precios-trinchera.md` **está muerto**. Sus
claves (`CAJAS.PL`, `ESFERAS.KR`, `CORREAS.ACERO`) y sus números de línea ya no
existen. No lo aplique nadie.

---

## 3 · Seis costes de la ficha no son los que confirmó Óscar

Todos **por encima** de lo real, así que el precio de venta es más alto de lo
que tocaría. No se pierde dinero; se cobra de más.

| Pieza | Ficha hoy | **Confirmado por Óscar** | Δ | Proveedor |
|---|--:|--:|--:|---|
| Caja acero plata | 23,00 € | **18,50 €** | −4,50 | `1005009937589354` |
| Caja negra PVD | 23,00 € | **18,50 €** | −4,50 | mismo anuncio |
| Caja bronce | 23,00 € | **22,60 €** | −0,40 | mismo anuncio |
| Caja titanio | 54,39 € | **45,16 €** | −9,23 | `1005010605313493` · tandorio |
| Esfera Khaki | 17,29 € | **16,25 €** | −1,04 | `1005007043976717` |
| Esfera Murph | 21,19 € | **18,63 €** | −2,56 | `1005005589112497` |
| Piel perforada | 6,69 € | **6,79 €** | **+0,10** | `1005009640853583` |

Los seis primeros son del 26/08 y llevan cuatro días sin aplicar. La perforada
subió el 29/08.

### Lo que cuadra

| Pieza | Ficha | Confirmado |
|---|--:|--:|
| Cuarzo LO_Q6026 **+ anillo** | 18,65 € | 15,05 + 3,60 ✅ |
| Automático LO_A4026 | 50,09 € | 50,09 ✅ |
| Piel con costura | 7,69 € | 7,69 ✅ |
| Tela vaquera | 5,99 € | 5,99 ✅ |
| Grabado del logotipo | 3,78 € | — *(sin proveedor)* |

El anillo espaciador del cuarzo va **dentro** del coste del calibre, no aparte.
Está bien resuelto y documentado en la ficha.

---

## 4 · Qué pasa si se aplican los costes confirmados

Medido con el volcador, con el suelo al 5 %:

| | |
|---|--:|
| Referencias que **bajan** de precio | **8.608** de 10.240 |
| Referencias que suben | **0** |
| Bajada media | **17,63 €** |
| Bajada máxima | **30,00 €** |
| «Desde» del Trinchera | 189,90 € → **179,90 €** |
| Techo | 449,90 € → **419,90 €** |

Es la corrección más grande que queda pendiente en toda la casa.

---

## 5 · Costes sin proveedor confirmado por Óscar

Vienen del chat de la web o de la hoja de materiales vieja. **No están mal por
definición: es que no hay constancia de que Óscar los haya dado.**

| Concepto | Coste | Refs afectadas | Nota |
|---|--:|--:|---|
| Caucho curvado | 5,79 € | **4.928** | ⚠️ ver abajo |
| Piel vintage | 16,89 € | 1.600 | sin origen |
| Nato | 3,99 € | 320 | Óscar dio 11,29 (39) y 5,59 (36) para el nato viejo |
| Acero 316L satinado | 20,19 € | 64 | Óscar dio 19,59 (Trinchera) y 19,79 (Lunar) |
| Piel italiana | 37,39 € | *(sin refs vivas)* | Óscar dio 29,99 para la italiana vieja |
| Hebilla negra / oro / mariposa | 1,20 / 1,00 / 0,20 € | — | de la hoja vieja |
| Grabado del logotipo | 3,78 € | todas | de la hoja vieja, sin anuncio |

### ⚠️ El caucho no cuadra, y son 4.928 referencias

Óscar dio hoy **12,99 €** para el caucho del Lunar, cinco colores. La ficha
—del Trinchera y del Lunar— tiene **5,79 €** para nueve colores de «caucho
curvado». **Son más del doble de diferencia y afectan a casi la mitad del
Trinchera.**

O son dos productos distintos —el curvado de la entrega x20 contra el que
Óscar coteó— o uno de los dos números está mal. **Hay que resolverlo antes de
pedir nada.**

---

## 6 · El libro está desfasado

Las piezas **P-019 a P-049** describen el Trinchera **viejo**: los cuatro dúos,
la esfera de segundero rojo, los natos de 11,29 y 5,59, las pieles italianas de
29,99, la piel del Khaki… Nada de eso existe en la ficha de hoy.

Hay que rehacer ese bloque contra `assets/datos/fichas/trinchera.json`, que es
la fuente de verdad. Las piezas nuevas y compartidas (P-050 a P-058) sí están
al día.

---

## 7 · Qué hacer, por orden

1. **Resolver el caucho**: 5,79 o 12,99. Bloquea 4.928 referencias.
2. **Aplicar los seis costes confirmados** en `assets/datos/fichas/trinchera.json`
   y regenerar la ficha. Bajan 8.608 precios.
3. **Poner al día P-019…P-049 del libro** contra el JSON de la ficha.
4. **Confirmar o sustituir** los costes sin origen: vintage, nato, acero
   satinado, hebillas y el grabado del logotipo.
5. **Borrar `.docs/encargo-precios-trinchera.md`**, que ya no apunta a nada.
