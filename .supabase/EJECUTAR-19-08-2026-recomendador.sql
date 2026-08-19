-- ============================================================
-- laOra · LAS TRES PREGUNTAS, ANOTADAS (19/08/2026)
-- ------------------------------------------------------------
-- El recomendador de la colección pregunta tres cosas: cómo tiene
-- la muñeca, para qué quiere el reloj y cuánto se quiere gastar.
-- A quien ha entrado con su cuenta se le anotan, y no se le vuelven
-- a preguntar cada vez que entra en la página.
--
-- A quien NO ha entrado no se le guarda nada, como hasta ahora: el
-- recomendador sigue respondiendo sin pedir un correo a cambio.
--
-- Los valores son los mismos que usa `recomendador.js`. Se dejan
-- atados con un CHECK para que un día no acabe ahí cualquier cosa.
--
-- Idempotente. Editor SQL de Supabase, proyecto uikanfvigunjhzibnhxf.
-- ============================================================

alter table laora.socios add column if not exists rec_muneca      text;
alter table laora.socios add column if not exists rec_uso         text;
alter table laora.socios add column if not exists rec_presupuesto text;
alter table laora.socios add column if not exists rec_fecha       timestamptz;

alter table laora.socios drop constraint if exists socios_rec_muneca_check;
alter table laora.socios add  constraint socios_rec_muneca_check
  check (rec_muneca is null or rec_muneca in ('fina','normal','ancha','nose'));

alter table laora.socios drop constraint if exists socios_rec_uso_check;
alter table laora.socios add  constraint socios_rec_uso_check
  check (rec_uso is null or rec_uso in ('dia','agua','vestir','hablar'));

alter table laora.socios drop constraint if exists socios_rec_presupuesto_check;
alter table laora.socios add  constraint socios_rec_presupuesto_check
  check (rec_presupuesto is null or rec_presupuesto in ('hasta200','200a300','mas300','da-igual'));

comment on column laora.socios.rec_muneca is
  'Respuesta a «¿cómo tienes la muñeca?». Si el socio dio su medida en cm, se deduce de ahí y no se le pregunta.';
comment on column laora.socios.rec_fecha is
  'Cuándo respondió. Sirve para volver a preguntar si un día se quedan viejas.';

-- ---------- el candado por columnas, otra vez ----------
-- El `grant update` de la cuenta enumera columnas, así que las nuevas
-- hay que sumarlas o el socio no podrá escribir sus propias respuestas.
grant update (rec_muneca, rec_uso, rec_presupuesto, rec_fecha)
  on laora.socios to authenticated;

-- ---------- comprobación ----------
select column_name
  from information_schema.column_privileges
 where table_schema = 'laora' and table_name = 'socios'
   and grantee = 'authenticated' and privilege_type = 'UPDATE'
   and column_name like 'rec_%'
 order by column_name;
