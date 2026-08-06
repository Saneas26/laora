# Embudos por modelo — plan de trabajo

Escrito el 06/08/2026, antes de empezar. Sirve para retomar el trabajo sin
depender de la conversación.

## La arquitectura que quiere Óscar

```
laora.es              pantalla principal, nada más
   ↓
/coleccion            se elige modelo   (Óscar trabaja en ella el 06/08)
   ↓
/<modelo>             EMBUDO INDIVIDUAL — el ejemplo es `lunarv2c.html`
```

`lunarv2c.html` es el patrón a replicar. Lleva:

- visor de la foto
- selector de **acabado** (con el «desde» de cada uno)
- selector de **brazalete o correa**
- resumen: acabado · correa · referencia · precio
- botón **Reservar**
- overlay de **ficha técnica completa**

## Material recibido

`laOra-fotos-aprobadas-para-Claude-2026-08-06.zip` (93 MB), descomprimido en
el escritorio de trabajo. Cuatro carpetas:

| Carpeta | Qué trae |
|---|---|
| `01-catalogo-final/` | **una foto por REFERENCIA exacta** del catálogo |
| `02-landing-lunar/` | las 8 fotos de los actos del Lunar (hero, muñeca, reflejo y las 5 de confianza) |
| `03-capturas-aprobadas/` | 14 capturas del diseño aprobado, a 1440×900 y 390×844 |
| `04-marca/` | logotipo y wordmarks |

Fotos de catálogo por modelo:

| Modelo | Fotos | Modelo | Fotos |
|---|---|---|---|
| Trinchera | 17 | Cero Cero | 6 |
| Lunar | 8 | Tortuga | 5 |
| Bitácora | 7 | Precisa | 4 |
| Cóctel | 3 | DIVER (LO-06) | 1 |

**El Buzo se llama DIVER y es LO-06**, confirmado por el nombre de sus
archivos. Del Bauhaus no hay ninguna: está aparcado.

Cada carpeta trae un `README.md` que empareja archivo ↔ referencia ↔ correa
↔ URL del proveedor.

## Lo que esto permite y hoy no se hace

El configurador enseña **siempre la misma foto**. Con este material puede
enseñar **la foto real de la combinación elegida**: al cambiar de correa,
cambia la foto. Es el salto más visible de todo el trabajo y sale gratis,
porque las fotos ya están hechas y nombradas por referencia.

## Orden de trabajo

1. **Meter las fotos en el repo**, convertidas a webp, con el nombre de su
   referencia: `assets/img/catalogo/LO-01_Lunar_A01.webp`.
2. **Generalizar `generar_v2c.py`** para que escriba un embudo por modelo en
   vez de solo el del Lunar. Un fichero, ocho páginas.
3. **Enganchar la foto por referencia** al configurador.
4. **Volcar los modelos que faltan** en `catalogo.json` desde la hoja
   «Catalogo laOra»: Tortuga, Cóctel y DIVER no tienen configurador.
5. Rutas y redirecciones: decidir si `/lunar` pasa a ser el embudo y la ficha
   vieja desaparece.

## Reglas del material aprobado que hay que respetar

Del `CLAUDE_HANDOFF.md` que venía en el zip:

- El texto lo decide Óscar. No reinterpretarlo sin preguntar.
- Nunca las palabras «réplica» ni «clon».
- `laOra` va siempre con el logotipo, nunca reconstruido con tipografía.
  El logotipo y la palabra de al lado comparten línea base y altura.
- **Precio mínimo del Lunar: 219,90 €.** No volver a enseñar 209,90 ni 189.
- Las variantes **Eclipse** van completamente negras, esfera incluida.
- Tipografía mínima: 14 px en ordenador, 12 px en móvil.
- Cada acto ocupa una pantalla. Los overlays técnicos sí pueden desplazarse.

## Los tres huecos

1. **Las fotos de los actos 2 y 3 solo existen del Lunar** (muñeca y reflejo).
   Los otros embudos no pueden tener esos dos actos hasta que las haya. Las
   cinco del carrusel de confianza sí son genéricas y sirven para todos.
2. **Tortuga, Cóctel y DIVER no tienen datos** en el catálogo: sus embudos no
   podrían enseñar precio hasta volcarlos de la hoja.
3. **Falta decidir qué pasa con las fichas viejas** (`/lunar`, `/cero-cero`…),
   que conviven con el diseño anterior.
