# Precios publicados hasta el 03/08/2026

Copia de seguridad de `assets/js/precios.js` antes de retirarlo en el rediseño.
**No es la hoja de materiales** — son las cifras que estaban publicadas, y casi
todas eran horquillas orientativas, no precios cerrados.

De 35 acabados, solo **5 tenían precio cerrado**. Los otros 30 estaban a `null`,
que en aquel sistema significaba «este acabado todavía no está a la venta».

| Modelo | Alba | Levante | Cenit | Eclipse |
|---|---|---|---|---|
| Lunar | **239,90 €** | — | **379,90 €** | 550–750 € |
| Bitácora | **250 €** | **320 €** | **420 €** | — |
| Trinchera | desde 150 € | 230–320 € | 330–450 € | +50–100 € sobre Cenit |
| Precisa | desde 190 € | 280–380 € | 400–560 € | +50–100 € sobre Cenit |
| Bauhaus | desde 170 € | 260–360 € | 360–480 € | +50–100 € sobre Cenit |
| Cero Cero | desde 190 € | 280–380 € | 400–560 € | 560–750 € |
| Cóctel | desde 180 € | 270–370 € | 380–500 € | +50–100 € sobre Cenit |
| Tortuga | desde 180 € | 260–350 € | 360–500 € | 500–650 € |
| Ocho Lados | desde 250 € | 350–480 € | 500–700 € | +50–100 € sobre Cenit |

**En negrita, los cinco precios cerrados.** El resto eran horquillas.

## Lo que enseñaba el listado de colección

Estas eran las cifras visibles en `coleccion.html`, y no siempre coincidían con
las de arriba:

Lunar 269,90 € · Bitácora 259 € · Trinchera 289,90 € · Precisa 299,90 €
· Bauhaus 269,90 € · Cero Cero 329,90 € · Cóctel 299,90 € · Tortuga 399,90 €

## Desajustes conocidos, para no repetirlos

- **Lunar**: 269,90 € en el listado y 239,90 € en su ficha.
- La descripción de la home para Google anunciaba «desde 249,90 €», un precio
  que no existía en ningún sitio.
- **Ocho Lados** tenía precios y ficha (`relojes/lo-06-ocho-lados.html`) pero no
  estaba en el listado de la colección.

## Qué manda a partir de ahora

La **hoja de materiales** de Óscar (Google Sheet con acabados, precios y specs
reales de los modelos). Nada de precios calculados por fórmula: el material de
Codex del 03/08 proponía base / +70 € / +140 € / +210 € iguales para los ocho
modelos, y eso se descartó.
