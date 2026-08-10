# Tercer encargo · laOra · EL LUNAR ENTERO
### 57 fotos y su página deja de tener nada dibujado · 10/08/2026

---

## Para qué es esto

La página del Lunar funciona ya con **dos** fotos tuyas: `LO-03-C1-E1` y `Brz-316-A01`.
Las demás combinaciones se enseñan hoy con un **brazalete dibujado por ordenador**, que
es un apaño mientras no hay foto. Con este encargo terminado, el Lunar pasa a ser el
primer reloj **real de arriba abajo**: cualquiera de sus 220 configuraciones se ve con
su metal y su esfera de verdad.

**Son 57 fotos.** No 220: la página monta la cabeza sobre el brazalete, así que con
4 cabezas y 55 brazaletes salen las 220 combinaciones.

La lista completa, con el nombre exacto de cada archivo y el enlace al proveedor de
cada pieza, está en **`laora-lunar-fotos.csv`**, al lado de este documento.

---

## Lo que ya está aprobado no se toca

`LO-03-C1-E1.webp` y `Brz-316-A01.webp` llevan días montadas en la web y encajan al
píxel. **Esas dos son la referencia.** Todo lo que dispares tiene que poder
intercambiarse con ellas sin que se note.

Sigue valiendo, palabra por palabra, lo de `ENCARGO-FOTOS.md` y
`CORRECCIONES-PRUEBA-01.md`. Este documento no los sustituye: los continúa y añade las
medidas exactas, sacadas de las dos fotos buenas.

---

## LA REGLA QUE MANDA SOBRE TODAS

> **Las 59 fotos se montan unas encima de otras. Cualquier cosa que cambie entre dos
> tomas se ve como una costura.**

Eso quiere decir, y no es negociable:

- **Trípode o columna de reproducción bloqueada.** No se mueve entre tomas. Ni un
  milímetro, ni para cambiar la pieza.
- **Misma cámara, mismo objetivo, misma distancia, misma altura.** Nada de acercarse
  «un poco» a una pieza pequeña: se recorta después, no se reencuadra.
- **Misma luz.** Mismas fuentes, misma potencia, mismas posiciones. Si hay que parar y
  seguir mañana, se fotografía de nuevo una pieza ya hecha y se compara antes de
  continuar.
- **Cámara perpendicular al reloj**, a su altura. Sin picado ni contrapicado. El reloj
  se ve de frente, plano, sin fuga.
- **Fondo transparente de verdad**, recortado limpio. Nada de blanco «que ya se
  quitará», y sin halo claro en el borde.
- **Sin sombra proyectada dentro del archivo.** La sombra la pone la web.

---

## LAS MEDIDAS, SACADAS DE LAS FOTOS BUENAS

No son estimaciones: están medidas píxel a píxel sobre `LO-03-C1-E1.webp` y
`Brz-316-A01.webp`.

### La cabeza · lienzo 1000 × 1000

```
      x=240                x=500                    x=802
        │                    │                        │
  y=200 ┼───── punta de las asas ──────┼               ← arriba del todo
        │   x=363 ┤          │        ├ x=635         │
        │            hueco entre asas                 │
        │            de x=367 a x=633 = 266 px        │
  y=272 │      ╭─────── la caja empieza ───────╮      │
        │      │                               │      │
  y=500 ┼──────┤   CENTRO DE LA CAJA en x=500  ├──────┼ corona y pulsadores
        │      │   caja de x=240 a x=760       │      │  hasta x=802
  y=728 │      ╰──────── la caja acaba ────────╯      │
        │            hueco entre asas                 │
        │            de x=369 a x=633 = 264 px        │
  y=799 ┼───── punta de las asas ──────┼               ← abajo del todo
```

- **El reloj ocupa de `y=200` a `y=799`.** Exactamente 600 px de alto, con 200 px de
  aire arriba y 200 abajo. Esos márgenes no son decorativos: la web los usa para
  colocar la pieza.
- **La caja va centrada en `x=500`.** Se centra por el **eje de las asas**, no por el
  contorno: la corona sobresale por la derecha y descentraría la foto si te guías por
  el bulto.
- **Corona y pulsadores a la DERECHA.** Siempre.
- El punto más ancho, con corona incluida, llega a `x=802`.

### El brazalete · lienzo 1000 × 2400

```
  y=48    ┌──────┐   el cierre, arriba del todo (189 px de ancho)
          │      │
          │ ████ │   la mitad de arriba
          │ ████ │
  y=897   └─╮  ╭─┘   el extremo curvo que abraza la caja
             ╲╱      de x=366 a x=633 = 267 px de ancho

  ...      HUECO de y=898 a y=1500 (603 px) — aquí va la cabeza, no hay nada

  y=1501     ╱╲      el otro extremo curvo, mismo ancho
          ┌─╯  ╰─┐
          │ ████ │   la mitad de abajo
          │ ████ │
  y=2389  └──────┘   la punta, 136 px de ancho
```

- **El hueco del centro va de `y=898` a `y=1500`.** Ahí no puede haber ni un píxel.
- **Los dos extremos que tocan la caja miden 267 px de ancho**, de `x=366` a `x=633`.
  Ese número tiene que cuadrar con el hueco entre asas de la cabeza —266 px— porque el
  brazalete se mete 80 px por detrás de las asas. Si el brazalete sale más ancho, asoma
  por los lados; si sale más estrecho, se ve la rendija de luz.
- **El extremo es cóncavo**, curvado hacia dentro, para que abrace la caja redonda. No
  lo cortes recto.
- Centrado en `x=500`, igual que la cabeza.

### El archivo

- **WebP con canal alfa.** Si trabajas en PNG, entrega PNG y ya lo convierto yo — pero
  entonces que el PNG lleve la transparencia de verdad, no un fondo blanco.
- **El nombre del archivo ES la referencia.** `Brz-904-A15.webp`, tal cual, con sus
  guiones y sus mayúsculas. Un nombre mal escrito es una foto que la web no encuentra.

---

## QUÉ HAY QUE DISPARAR

### 1 · Las cabezas — 4 en total, **3 pendientes**

Son dos biseles por sus esferas compatibles. La esfera negra solo entra en el bisel
negro y la azul solo en el azul; la blanca entra en los dos.

| Archivo | Bisel | Esfera | Estado |
|---|---|---|---|
| `LO-03-C1-E1.webp` | Negro | Negra | ✅ **entregada** |
| `LO-03-C1-E2.webp` | Negro | **Blanca** | pendiente |
| `LO-03-C2-E2.webp` | **Azul** | Blanca | pendiente |
| `LO-03-C2-E3.webp` | **Azul** | Azul | pendiente |

Las agujas, en las cuatro, **en la misma posición exacta** que en la que ya está
entregada. Es la misma foto cambiando dos piezas, no cuatro fotos distintas.

### 2 · Los brazaletes y correas — 55 en total, **54 pendientes**

Diez familias. La lista completa con enlace al proveedor está en el CSV; aquí va el
resumen para que sepas lo que tienes que tener encima de la mesa:

| Familia | Cuántas | Referencias |
|---|---:|---|
| Acero 316L, cinco eslabones | 1 | `A01` ✅ |
| Acero 316L, cierre desplegable | 3 | `A02`–`A04` |
| Acero 316L macizo | 3 | `A05`–`A07` |
| Acero 316L macizo, eslabón ancho | 1 | `A10` |
| Acero 316L macizo, eslabón fino | 1 | `A11` |
| Acero 904L macizo | 2 | `A12`, `A13` |
| Acero 904L, eslabones planos | 7 | `A14`–`A20` |
| Caucho con hebilla de acero | 7 | `G01`–`G07` |
| Caucho fluorado, cierre desplegable | **30** | `C01`–`C30` |

**Las 30 de caucho fluorado son media tanda ellas solas.** Muchas se diferencian solo
en el color de la costura o del cierre: cuidado con el orden, y comprueba la referencia
contra el CSV antes de guardar cada una.

### 3 · Lo que NO hay que fotografiar

Los cuadritos que en la web enseñan cada familia de brazalete **se recortan del archivo
de 1000 × 2400**. No hace falta ni una foto más para eso. Yo los saco.

---

## Y DESPUÉS, LA FOTO CON ALMA

Lo de arriba deja el configurador real. Pero la portada y la ficha del Lunar siguen
enseñando **imágenes generadas por ordenador**, y eso es lo siguiente que hay que
sustituir. No corre tanta prisa —el configurador manda—, pero hay que decirlo ahora
para que lo tengas en la cabeza cuando montes el set:

| Qué | Medida | Para qué | Hoy |
|---|---|---|---|
| Reloj sobre negro, tres cuartos | 1200 × 1200 | la tarjeta de la colección | render |
| Escena horizontal | 1672 × 941 (16:9) | la portada | render |
| En la muñeca | 1600 × 1200 | dar la escala real | render |
| Macro del bisel y la esfera | 1600 × 1600 | el detalle que vende | no hay |
| La caja abierta, el envío | 1600 × 1200 | lo que recibe el cliente | no hay |

Estas cinco **sí llevan luz de autor**: sombra, ambiente y carácter. Son lo contrario
de las 57 de arriba, que son fotos de catálogo, planas y clínicas a propósito.

---

## En qué orden

1. **Las 3 cabezas primero.** Son las que menos cuestan y desbloquean las 4 esquinas
   del configurador.
2. **Los 17 de acero después** (`A02`–`A20`). Con eso, las combinaciones caras del
   Lunar ya son reales.
3. **Los 7 de caucho con hebilla** (`G01`–`G07`).
4. **Las 30 de caucho fluorado** (`C01`–`C30`), que es el bloque largo.

Manda un **primer envío de tres** —una cabeza y dos brazaletes— antes de disparar el
resto. Los monto, los mido y te digo si cuadran. Si algo se ha movido en el set, mejor
descubrirlo con tres fotos que con cincuenta y siete.
