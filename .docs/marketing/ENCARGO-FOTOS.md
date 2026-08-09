# Encargo de fotografía · laOra
### Piezas para el configurador · 262 tomas

---

## Qué estamos haciendo y por qué importa

laOra vende relojes **configurables**: el cliente elige movimiento, caja, esfera y brazalete, y la web le enseña **su** reloj mientras lo elige. Con las piezas que hay hoy salen **11.230 combinaciones distintas**.

Once mil fotos no existen. Así que la página **monta la imagen en el momento, con dos capas**:

```
      ┌──────────────┐
      │  BRAZALETE   │   ← capa de atrás, una foto
      │   ╔══════╗   │
      │   ║CABEZA║   │   ← capa de delante, otra foto
      │   ╚══════╝   │
      │              │
      └──────────────┘
```

**262 fotos cubren las 11.230 combinaciones.** Por eso todo lo que viene a continuación sobre encuadre y posición no es manía: si las dos capas no coinciden al milímetro, el montaje se ve y el reloj parece falso.

---

## Los dos tipos de toma

### 1 · CABEZA — 137 fotos
La caja **con su esfera y sus agujas ya montadas**, sin brazalete.

La esfera no se puede montar por capas: va bajo el cristal, con las agujas encima y los reflejos del zafiro por delante. Por eso cada pareja de caja y esfera es una foto.

| Especificación | Valor |
|---|---|
| Lienzo | **1000 × 1000 px**, cuadrado |
| Fondo | **Transparente**. Nunca blanco |
| Centro | El **eje de las asas** en **x = 500**. La corona y los pulsadores NO cuentan |
| Puntas de las asas | Arriba en **y = 200**, abajo en **y = 800** |
| Ancho máximo | 640 px, corona y pulsadores incluidos |
| **Hueco entre asas** | **266 px exactos**, de x = 367 a x = 633 |
| Plantilla | `plantilla-cabeza.svg` |

### 2 · BRAZALETE — 125 fotos
El brazalete **entero, extendido en vertical, con el hueco de la caja vacío** en el centro. Sin reloj.

| Especificación | Valor |
|---|---|
| Lienzo | **1000 × 2400 px**, vertical |
| Fondo | **Transparente** |
| Centro del hueco | **x = 500, y = 1200** |
| Bordes del hueco | Arriba **y = 900**, abajo **y = 1500** |
| **Ancho en el asa** | **266 px exactos**, de x = 367 a x = 633 |
| Plantilla | `plantilla-brazalete.svg` |

Los dos lienzos comparten el mismo eje vertical y la misma escala. Con los centros alineados, **las asas de la cabeza caen justo en los bordes del hueco**. Ahí está todo el truco.

---

## Las cinco reglas que no se pueden saltar

0. **Las dos capas comparten escala.** El hueco entre las asas de la cabeza y el ancho del brazalete son **el mismo número: 266 px**. Si no coinciden, la correa se ve estrecha dentro de las asas y el montaje canta.
1. **Trípode fijo.** Misma altura, misma distancia y misma óptica en las 262 tomas. Si se mueve la cámara, hay que rehacer el bloque entero.
2. **Misma luz.** No se cambia nada entre tomas: ni potencia, ni difusor, ni posición. Dos brazaletes con luces distintas no se pueden mezclar con la misma cabeza.
3. **Fondo recortado de verdad.** PNG con transparencia. Un fondo blanco recortado a mano deja un halo que se ve en cuanto la capa va encima de otra.
4. **Centrar por el eje de las asas.** No por el contorno de la foto: la corona sobresale por la derecha y desplaza el centro más de 20 px. Se centra por donde entra la correa.
5. **Las asas siempre en el mismo punto.** Es la única coordenada que importa. Cargar la plantilla como capa y cuadrar cada toma encima.
6. **El nombre del archivo es la referencia.** Viene en el CSV, columna `Referencia`. Sin inventar, sin espacios, sin acentos, sin mayúsculas distintas.

---

## Nombres y entrega

```
cabezas/     LO-02-C1-E1.png      ← modelo · caja · esfera
brazaletes/  Brz-Lona-L01.png     ← la referencia tal cual
```

La página construye el nombre con lo que el cliente elige y va a buscarlo. **No hay ninguna lista de correspondencia**: si el archivo se llama distinto, la foto no aparece.

**Maestro:** PNG a 2000 px de ancho con transparencia, capas planas.
**Nosotros generamos** el WebP a 1000 px que sube a la web. No hace falta que lo entregue comprimido.

---

## En qué orden

No por relojes: **por reparto**. Una foto de brazalete sirve a todos los relojes que lo admiten; una cabeza sirve a uno solo.

| Bloque | Fotos | Qué desbloquea |
|---|---:|---|
| **1 · Brazaletes** | 125 | Sirven a los ocho relojes |
| **2 · Cabezas de Lunar, Cóctel, Diver y Precisa** | 15 | Cuatro modelos completos en la web |
| **3 · Bitácora y Tortuga** | 43 | Seis modelos |
| **4 · Trinchera** | 70 | El catálogo entero |

Con los bloques 1 y 2 —**140 fotos**— ya hay cuatro relojes funcionando de verdad.

---

## Lo que NO hay que hacer

- **No** fotografiar combinaciones completas (caja + esfera + brazalete montados). Serían 11.230.
- **No** retocar el color de una foto para «crear» otra variante. Si el brazalete azul no se ha comprado, no se inventa.
- **No** recortar con fondo blanco y llamarlo transparencia.
- **No** cambiar el encuadre «porque este reloj se ve mejor así». Se ve mejor suelto y peor montado.

---

## Archivos de este encargo

| Qué | Ruta |
|---|---|
| Listado completo, 262 filas | `.docs/marketing/laora-fotos-encargo.csv` |
| Plantilla de cabeza | `.docs/marketing/plantilla-cabeza.svg` |
| Plantilla de brazalete | `.docs/marketing/plantilla-brazalete.svg` |
| Este documento | `.docs/marketing/ENCARGO-FOTOS.md` |

El CSV trae, por cada foto: **Tipo · Referencia · Modelo · Nombre · Detalle · Se usa en · URL de la pieza**. Las URL son las del proveedor, para que se vea qué es cada cosa antes de tenerla en la mano.

Las cabezas llevan **dos URL**: la de la caja y la de la esfera, porque hay que montarlas antes de fotografiar.

---

## Resultado de la primera prueba (09/08/2026)

Se probaron `LO-03-C1-E1.png` y `Brz-316-A01.png`. **Los lienzos, la transparencia, los nombres y el encaje vertical: perfectos.** Dos cosas a corregir:

| | Debería | Estaba |
|---|---|---|
| Ancho del brazalete | 266 px | **222 px** — 16 % estrecho |
| Eje de la cabeza | Asas en x = 500 | Contorno en x = 500 → asas en **x = 478** |

Las dos están ya reflejadas en las plantillas.

## Antes de empezar

Las fotos **no se pueden hacer hasta tener las piezas físicamente**. Son **17 pedidos de brazalete** y **10 de caja** — cada anuncio trae varios colores. Ese es el camino crítico.

Sugerencia: que el diseñador haga **una cabeza y un brazalete de prueba** y los montemos en la web antes de disparar las 260 restantes. Si el encaje falla, falla en dos fotos y no en doscientas.
