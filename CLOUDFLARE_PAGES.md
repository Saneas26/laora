# laOra · Conectar el repo a Cloudflare Pages con laora.es

Igual que saneas.es y activala.es: `main` = producción, cada rama = preview automática.

## 1. Crear el proyecto en Pages
1. dash.cloudflare.com → **Workers & Pages → Create → Pages → Connect to Git**.
2. Autoriza GitHub si lo pide y elige el repo **`Saneas26/laora`**.
3. Configuración del build (es una web estática, no hay build):
   - **Project name**: `laora`
   - **Production branch**: `main`
   - **Framework preset**: `None`
   - **Build command**: *(vacío)*
   - **Build output directory**: `/`
4. **Save and Deploy**. Primera URL: `laora.pages.dev`.

## 2. Dominio propio (laora.es está en DonDominio)
1. Si `laora.es` aún no está en Cloudflare: **Add a domain** → seguir el asistente
   → en DonDominio, cambia los **nameservers** del dominio al par que te dé
   Cloudflare (Panel DonDominio → dominio → DNS/Nameservers → personalizado).
   La propagación tarda de minutos a unas horas.
2. En el proyecto Pages → **Custom domains → Set up a custom domain** → `laora.es`.
3. Añade también `www.laora.es` y Cloudflare lo redirige solo.
4. El certificado HTTPS se emite automáticamente en unos minutos.

## 3. Previews por rama (el ciclo de siempre)
- Cada push a una rama publica preview en `<rama-normalizada>.laora.pages.dev`.
- La rama de estreno de esta web es `claude/web-laora` → preview
  `claude-web-laora.laora.pages.dev` en cuanto conectes el proyecto.
- Nada se fusiona a `main` sin tu «fusiona»; al fusionar, producción se actualiza sola.

## 4. Después de estrenar
1. Rellenar Supabase (ver `SUPABASE_PASOS.md`) para que el formulario guarde y avise.
2. Actualizar el pie de **todas** las webs del grupo: la tarjeta laOra deja el
   «Muy pronto» y enlaza a https://laora.es (la rama para saneas.es ya queda
   preparada aparte; en activala.es se hace igual).
3. Encargar a la ventana de Saneas añadir laOra al desplegable y pie de la app.
