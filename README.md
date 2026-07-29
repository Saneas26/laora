# laOra — web de laora.es

Web estática, sin frameworks y sin build: HTML/CSS/JS vanilla.
Cloudflare Pages, `main` = producción, cada rama = preview.

## Importante antes de añadir nada

El **build output directory es `/`**: todo lo que esté en el repo se publica en
laora.es tal cual. Cloudflare Pages no sube nada que empiece por punto, así que
todo lo interno vive en carpetas ocultas:

| Carpeta | Qué hay |
|---|---|
| `.docs/` | Brief de desarrollo, copy, informe de sourcing, chuletas de Supabase y de Cloudflare Pages, y este README ampliado |
| `.supabase/` | SQL del formulario y Edge Function de aviso |

**Cualquier carpeta o fichero que no sea la web pública empieza por punto.**
No sirve `.gitignore` (haría falta no versionarlo) ni `.vercelignore`/`vercel.json`
(esto no es Vercel). `_redirects` corta además las rutas antiguas.

La documentación completa está en `.docs/README-interno.md`.
