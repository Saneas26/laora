# La pantalla de comprar, una por modelo

Escrito el 06/08/2026. Hecho el 06/08/2026.

## Lo que pidió Óscar

> «yo solo quiero montar laora.es/lunar, laora.es/bitacora,
> laora.es/precisa… y que sean exactamente igual que el laora.es/lunarv2c,
> no quiero montar una landing para cada uno. Solo hay una, es la
> principal y no es solo del lunar, se habla de la empresa y las
> emociones de comprar un reloj nuestro»

O sea:

```
laora.es              LA landing. Una sola. La empresa y lo que se
                      siente al comprar un reloj nuestro.
   ↓
/coleccion            se elige modelo
   ↓
/<modelo>             LA PANTALLA DE COMPRAR. Igual para todos.
```

## Lo que hay publicado

`herramientas/generar_configuradores.py` escribe cinco páginas, todas
iguales, todas con los datos de `assets/datos/catalogo.json`:

| Página | Acabados | Correas | Combinaciones |
|---|---:|---:|---:|
| `/lunar` | 3 | 8 | 8 |
| `/cero-cero` | 8 | 3 | 10 |
| `/precisa` | 7 | integrado | 7 |
| `/trinchera` | 6 | 2 | 12 |
| `/bitacora` | 6 | integrado | 6 |

`lunarv2c.html` ya no existe: `/lunarv2c` y `/lunarv2C` van con un 301
a `/lunar`. La hoja y el script se llaman ya `configurador.css` y
`configurador.js`, no `lunarv2c.*`.

`generar.py` —el generador de las fichas anteriores— SALTA esos cinco
slugs. Si no lo hiciera, ejecutarlo devolvería `/lunar` a la ficha vieja
sin que nadie se enterara.

## Lo que se decidió por el camino

**La referencia se compone en Python, no en el navegador.** Había dos
copias de las reglas de la hoja de materiales y se habían desviado: el
segundo Cenit del Precisa salía `C01` donde la hoja dice `C02`. Ahora
viaja ya hecha dentro del JSON de cada página.

**El calibre se escribe cuando el nombre se repite.** El Bitácora tiene
tres Eclipse y el Cero Cero, cuatro: salían botones idénticos, dos al
mismo precio. Ahora ponen «Eclipse / ST2130». Solo donde hace falta: el
Lunar, con tres acabados distintos, se queda como Óscar lo aprobó.

**Cuando no hay nada que elegir, no se pinta un botón.** El Precisa y el
Bitácora llevan brazalete integrado. Como botón, esa única muestra se
estiraba a todo el ancho y salía un azulejo de 690 px que echaba el
precio fuera de la pantalla. Ahora es una línea que dice lo que lleva.

**El visor pasó de negro a marfil.** Las fotos del paquete traen fondo
marfil incrustado (#f6f0eb, medido en el archivo). Sobre el visor negro
se veía el recuadro de la foto recortado y, peor, el rótulo blanco caía
encima del marfil: ilegible.

## Las fotos

`assets/img/catalogo/` — 51 fotos, una por referencia, del paquete
aprobado del 06/08/2026. Las 43 combinaciones que se pueden pedir tienen
foto de catálogo.

- **Lunar: foto por COMBINACIÓN.** Su README empareja una a una las ocho
  referencias con las ocho correas y coincide con el catálogo.
- **El resto: foto por ACABADO.** Sus paquetes numeran por caja o por
  movimiento, no por correa: el `A02` del Trinchera es la caja de
  bronce, no la NATO negra. Emparejar por número pondría una foto que no
  es la que se está eligiendo.

Cuando el paquete de un modelo confirme la correspondencia por correa,
se añade su slug a `FOTO_POR_COMBINACION` y esa pantalla pasa sola a
enseñar la foto exacta.

## Lo que falta

1. **Tortuga, Cóctel y DIVER (LO-06) no tienen configurador** en el
   catálogo: sin acabados ni matriz de precios no hay nada que elegir.
   Conservan su ficha anterior. Tienen fotos (5, 3 y 1).
2. **El Bauhaus sigue aparcado.** No se le abre pantalla de comprar a un
   reloj que hoy no se puede montar. Tampoco tiene fotos.
3. **Solo el Lunar está auditado contra la hoja definitiva.** En los
   demás, `catalogo.json` y el paquete de fotos no coinciden en los
   movimientos: el catálogo da el Cenit del Bitácora como ST2130 y el
   README de las fotos, como Miyota 9015. Manda la hoja «Catalogo laOra»
   y hay que volcarla modelo a modelo.
4. **Lo que se perdió de las fichas anteriores**: las curiosidades, la
   historia del original y la comparativa de precios. Están en el
   historial y `generar.py` sabe rehacerlas, pero hoy no se ven en
   ninguna parte. Decidir dónde van.
