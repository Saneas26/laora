# Integración del configurador Lunar

Usa `manifest.json` como fuente de verdad. No cambies la escala, posición,
relación de aspecto ni encuadre de ninguna imagen.

## Render

Crear un contenedor cuadrado y superponer, en este orden:

1. Fondo CSS `#EAE8E8`.
2. Imagen de `strap`.
3. Imagen de `head`.

Las dos imágenes tienen un lienzo transparente idéntico de 1254 × 1254 px:

```css
.lunar-preview {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #EAE8E8;
}

.lunar-preview > img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
}
```

No usar `object-fit: cover`, offsets distintos, recortes, zoom, rotación ni
transformaciones específicas por variante. Cambiar una opción consiste
únicamente en sustituir el `src` de la capa correspondiente.

## Alcance actual

- 13 cabezas registradas y transparentes.
- 1 correa registrada: piel negra perforada con pespunte blanco.
- Una composición de control en `previews/`.

No inventar nombres de activos ni combinaciones: leerlos de `manifest.json`.
