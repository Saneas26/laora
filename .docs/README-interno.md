# laOra — web de marketing

Web estática de **laOra** (relojería de homenaje, montaje y control en Madrid),
marca del grupo Saneas. Dominio: **laora.es** (Cloudflare Pages).

- Sin frameworks y sin build: HTML/CSS/JS vanilla. Guardar es desplegar.
- `index.html` — portada con la colección completa (LO-01…LO-09).
- `manifiesto.html` — «El alma de un automático».
- `relojes/lo-0X-*.html` — una landing por modelo.
- `supabase/` — SQL pegar-y-listo y Edge Function del formulario de interesados.
- Chuletas: `SUPABASE_PASOS.md` · `CLOUDFLARE_PAGES.md`.

Regla editorial: las marcas homenajeadas se nombran UNA vez y solo dentro del
bloque «La historia» de cada ficha. Nunca en títulos, metas, alts ni URLs.

Ciclo de trabajo del grupo: rama → preview → «fusiona» de Óscar → main.
