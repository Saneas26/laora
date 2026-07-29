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

---

# Reservas con señal del 25 % (Mollie + Bizum/transferencia)

Esto va DESPUÉS de tener el proyecto Supabase del formulario funcionando.

## 0. Antes de nada: lo que no es técnico
Sin estas tres cosas la web no cobra, y es a propósito — el propio código lo impide:

1. **Los 36 precios** en `assets/js/precios.js`. Precio final con IVA incluido.
   Un acabado con `precio: null` enseña «Avísame del estreno» y no deja reservar.
2. **La fecha de entrega** en `LAORA_ENTREGA`, en el mismo fichero. Vacía = no se cobra.
   Sin fecha pactada la ley te da 30 días desde el cobro, y no hay reloj en 30 días.
3. **Rellenar los tres huecos amarillos de `condiciones-de-venta.html`**: domicilio
   fiscal, fecha de entrega, teléfono de Bizum e IBAN. Salen marcados en la web
   para que no se olviden.

También hay que poner el Bizum y el IBAN en `LAORA_COBRO`, arriba de
`assets/js/gracias.js`, o el cliente no sabe dónde pagar.

## 1. Estructura — YA HECHA (29/07/2026)
Dos proyectos y no más:
- **`saneas-app`** — aislado, solo Saneas.
- **`activala`** (ref `uikanfvigunjhzibnhxf`) — compartido por el resto.

Comparten instancia pero **no tablas**: cada marca en su esquema
(`activala`, `laora`, `acumula`). `public` se queda vacío a propósito.
El guion está en `.supabase/estructura-grupo.sql` y es reejecutable.

Comprobado el 29/07/2026 contra la API real:
- alta en `laora.interesados` → 201
- leer `laora.interesados` o `activala.interesados` → `[]` (RLS corta las filas)
- insertar en `laora.reservas` desde el navegador → `42501 permission denied`

Al hablar con PostgREST hay que mandar **`Content-Profile: laora`** (o
`Accept-Profile` al leer) o busca en `public`, que está vacío.

## 2. Cuenta de Mollie
1. Alta en mollie.com y verificación de la cuenta (piden datos fiscales).
2. Activar los métodos que quieras: tarjeta y Bizum.
3. Developers → **API keys**: copia la `test_…` para probar y la `live_…` para
   cuando vaya en serio.

## 3. Las tres Edge Functions — YA DESPLEGADAS (29/07/2026)
Van con prefijo `laora-` porque el proyecto es compartido, y las tres
con **«Verify JWT» DESACTIVADO**:

| Función | Fichero | Quién la llama |
|---|---|---|
| `laora-crear-reserva` | `.supabase/crear-reserva.ts` | la web |
| `laora-mollie-webhook` | `.supabase/mollie-webhook.ts` | Mollie |
| `laora-avisar-reserva` | `.supabase/avisar-reserva.ts` | el trigger de la base |

No tocar `avisar-interesado`: es de activala.

Secretos (Edge Functions → Secrets):
- `LAORA_WEB_URL` — puesto. **Ahora apunta a la preview de la rama**
  (`https://claude-reservas.laora.pages.dev`) para poder probar. **Al
  fusionar hay que cambiarlo a `https://laora.es`.**
- `RESEND_API_KEY` e `INTERESADOS_EMAIL` — ya existían, compartidos con activala.
- **`LAORA_MOLLIE_API_KEY` — FALTA.** La pone Óscar: es una credencial.

Ojo con la clave de servicio: `SUPABASE_SERVICE_ROLE_KEY` está marcada
DEPRECATED y la sustituye `SUPABASE_SECRET_KEYS`. El código acepta las dos.

## 4. Enchufar la web
En `assets/js/laora.js`, arriba: `LAORA_SUPABASE_URL` y `LAORA_SUPABASE_KEY`
(la clave **publishable/anon**, nunca la service_role). Son las mismas que usa
el formulario de interesados.

## 5. Probar antes de cobrar de verdad
Con la clave `test_` de Mollie:
1. Pon un precio y una fecha de entrega de prueba en `precios.js`.
2. Reserva con tarjeta: Mollie te deja elegir el resultado (pagado, fallido…).
3. Comprueba que la fila de `reservas` pasa a `pagada` sola. Si se queda en
   `pendiente`, el webhook no llega: revisa que la función esté sin JWT.
4. Reserva por Bizum: la fila debe quedar en `pendiente` y llegarte el correo
   con el aviso de cobro manual.
5. Cambia la clave a `live_` cuando todo lo anterior salga bien.

## 6. El día a día
- Las reservas pendientes de cobro manual: vista `reservas_pendientes` en el
  Table Editor.
- Cuando veas el Bizum o la transferencia, pon `estado` = `pagada`. El correo
  de confirmación al cliente sale solo.
- Al enviar el reloj, cobras el 75 % restante y pones `estado` = `entregada`.
