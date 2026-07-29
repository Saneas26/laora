# laOra · Supabase (formulario de interesados) — pasos numerados

El patrón es el mismo que en Activala: tabla insert-only + trigger pg_net →
Edge Function → Resend, con tu correo SOLO en un secreto. Mientras Supabase no
esté conectado, el formulario de la web deriva a WhatsApp (no se pierde nadie).

## 1. Crear el proyecto
1. supabase.com → **New project** → organización de siempre.
2. Nombre: `laora` · Región: **Europe (West)** · contraseña de base la que quieras (guárdala).
3. Apunta la **ref del proyecto** (lo que va en `https://<ref>.supabase.co`).

## 2. La tabla y el trigger
1. SQL Editor → pega `supabase/interesados.sql` **cambiando antes `<PROYECTO>`
   por la ref del paso 1.3** → Run. Es idempotente: se puede repetir sin miedo.

## 3. La Edge Function
1. Edge Functions → **Deploy a new function** → nombre exacto: `avisar-interesado`.
2. Pega el contenido de `supabase/avisar-interesado.ts`.
3. En los ajustes de la función, **desactiva «Enforce JWT verification»**
   (la llama el trigger interno, no un cliente).

## 4. Los secretos (tu correo JAMÁS en el código)
1. Edge Functions → **Secrets**:
   - `INTERESADOS_EMAIL` = tu correo (donde quieres recibir los avisos).
   - `RESEND_API_KEY` = tu API key de resend.com (vale la de siempre).
2. No hace falta verificar laora.es en Resend: el plan Free solo admite 1 dominio,
   así que el aviso sale como `laOra <laora@saneas.es>` (dominio ya verificado)
   con `reply_to` al email del interesado.

## 5. Conectar la web
1. Project Settings → **API**: copia la **URL** y la clave **publishable** (anon).
2. En el repo, edita `assets/js/laora.js` (líneas de arriba):
   - `LAORA_SUPABASE_URL = 'https://<ref>.supabase.co'`
   - `LAORA_SUPABASE_KEY = '<clave publishable>'`
   (es pública por diseño; la seguridad la pone RLS, no la ocultación).
3. Commit y push: guardar es desplegar.

## 6. Probar
1. Envía el formulario desde la web con datos de prueba.
2. Table Editor → `interesados`: debe aparecer la fila (y borrarla desde ahí si quieres).
3. Debe llegarte el correo de aviso. Si no llega, revisa los dos secretos del paso 4.

## Ver los interesados
Table Editor → tabla `interesados`. Desde el cliente nadie puede leer, editar
ni borrar: solo insertar (RLS deny-all con política única de INSERT para anon).
