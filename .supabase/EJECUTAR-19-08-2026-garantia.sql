-- ============================================================
-- laOra · LA GARANTÍA, UNA SOLA VERDAD (19/08/2026)
-- ------------------------------------------------------------
-- La casa decía tres cosas distintas sobre lo mismo:
--   · la portada, las fichas y la laOrateca:  5 años
--   · la cuenta y los correos:                3 años
--   · esta tabla:                             24 meses (2 años)
--
-- Óscar lo cierra: **3 años de garantía obligatoria para cualquiera
-- —que es la que manda la ley española— y 5 años para los socios del
-- Club**. Como el Club va incluido con el reloj, en la práctica el
-- comprador llega a los 5; pero la distinción importa y aquí queda
-- escrita, que es donde se calcula la fecha que luego se reclama.
--
-- Idempotente. Editor SQL de Supabase, proyecto uikanfvigunjhzibnhxf.
-- ============================================================

-- ---------- 1. la garantía de serie pasa a 3 años ----------
alter table laora.garantias alter column meses set default 36;

comment on column laora.garantias.meses is
  '36 = los 3 años que da la ley a cualquiera. 60 = los 5 del Club laOra.';

-- ---------- 2. las que ya estaban puestas a 24 ----------
-- Nadie ha comprado todavía con el sistema nuevo, así que esto es por
-- si quedara alguna de pruebas: se suben a 36 y se recalcula su fin.
update laora.garantias
   set meses = 36,
       hasta = desde + interval '36 months'
 where meses = 24;

-- ---------- 3. el Club, incluido con el reloj ----------
-- `club_desde` decide si a ese socio le tocan 5 años en vez de 3. Se
-- pone solo cuando paga su primer pedido, que es justo lo que promete
-- la página del Club: «incluido con tu reloj».
create or replace function laora.apuntar_al_club(p_socio uuid)
returns void
language sql
security definer
set search_path = laora, public
as $$
  update laora.socios
     set club_desde = current_date
   where id = p_socio and club_desde is null;
$$;

comment on function laora.apuntar_al_club is
  'Apunta al socio al Club si no lo estaba. La llama el webhook de Mollie al confirmarse el primer pago.';

-- ---------- 4. la garantía que le toca a un socio ----------
create or replace function laora.meses_garantia(p_socio uuid)
returns int
language sql
stable
set search_path = laora, public
as $$
  select case when exists (
    select 1 from laora.socios where id = p_socio and club_desde is not null
  ) then 60 else 36 end;
$$;

comment on function laora.meses_garantia is
  '60 meses para los socios del Club, 36 para el resto. Es la única fuente de esa cifra.';

-- ---------- 5. comprobación ----------
select
  (select column_default from information_schema.columns
    where table_schema='laora' and table_name='garantias' and column_name='meses') as default_meses,
  (select count(*) from laora.garantias where meses = 24) as quedan_a_24;
