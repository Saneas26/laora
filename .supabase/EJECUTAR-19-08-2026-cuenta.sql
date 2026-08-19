-- ============================================================
-- laOra · LA CUENTA DEL CLIENTE (19/08/2026)
-- ------------------------------------------------------------
-- Dos cosas:
--
--   1. Lo que el socio quiera contarnos, todo VOLUNTARIO: su talla
--      de muñeca, su cumpleaños y cómo nos conoció. Y si quiere que
--      le avisemos de las novedades, que va aparte y sin marcar por
--      defecto, como manda la ley.
--
--   2. UN CANDADO QUE FALTABA. La política `socio_edita_lo_suyo`
--      deja que cada socio actualice SU fila… entera. Eso incluye
--      `notas`, que son las privadas de Óscar, y `club_desde`, que
--      no lo decide el cliente. Las políticas de Postgres van por
--      FILA, no por columna; lo que va por columna son los permisos.
--      Así que aquí se le quita el permiso de escribir en toda la
--      tabla y se le devuelve solo sobre las columnas que son suyas.
--
-- Idempotente: se puede volver a ejecutar sin romper nada.
-- Editor SQL de Supabase, proyecto uikanfvigunjhzibnhxf.
-- ============================================================

-- ---------- 1. lo voluntario ----------
alter table laora.socios add column if not exists muneca_cm     numeric(4,1);
alter table laora.socios add column if not exists cumple_dia    smallint;
alter table laora.socios add column if not exists cumple_mes    smallint;
alter table laora.socios add column if not exists nos_conocio   text;
alter table laora.socios add column if not exists quiere_avisos boolean not null default false;
alter table laora.socios add column if not exists avisos_desde  timestamptz;

-- Que no entren disparates, ni por error ni a mano.
alter table laora.socios drop constraint if exists socios_muneca_check;
alter table laora.socios add  constraint socios_muneca_check
  check (muneca_cm is null or (muneca_cm >= 10 and muneca_cm <= 30));

alter table laora.socios drop constraint if exists socios_cumple_check;
alter table laora.socios add  constraint socios_cumple_check
  check ((cumple_dia is null and cumple_mes is null)
      or (cumple_dia between 1 and 31 and cumple_mes between 1 and 12));

comment on column laora.socios.muneca_cm is
  'Contorno de muñeca en cm. Voluntario: sirve para recomendar correa y diámetro.';
comment on column laora.socios.cumple_dia is
  'Día del cumpleaños. Sin año: no hace falta la edad para felicitar.';
comment on column laora.socios.quiere_avisos is
  'Consentimiento EXPRESO para avisos de novedades. Falso por defecto y solo lo enciende el socio.';

-- ---------- 2. el candado por columnas ----------
-- Se le quita el permiso de escritura sobre la tabla…
revoke update on laora.socios from authenticated;

-- …y se le devuelve solo sobre lo que es suyo. `notas` (privadas de
-- Óscar), `club_desde`, `email` y `id` quedan fuera a propósito.
grant update (
  nombre, apellidos, telefono, nif,
  direccion, cp, poblacion, provincia, pais,
  muneca_cm, cumple_dia, cumple_mes, nos_conocio,
  quiere_avisos, avisos_desde, actualizado_en
) on laora.socios to authenticated;

-- ---------- 3. comprobación ----------
-- Debe salir la lista de columnas que el socio puede escribir, y NO
-- deben estar ni `notas` ni `club_desde`.
select column_name
  from information_schema.column_privileges
 where table_schema = 'laora' and table_name = 'socios'
   and grantee = 'authenticated' and privilege_type = 'UPDATE'
 order by column_name;
