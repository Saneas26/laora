-- ============================================================
-- Grupo Saneas · estructura del proyecto Supabase compartido
-- ------------------------------------------------------------
-- Regla del grupo (29/07/2026):
--   · saneas-app  → proyecto AISLADO, solo Saneas. No se toca desde aquí.
--   · activala    → proyecto COMPARTIDO por el resto de marcas.
--
-- Comparten instancia, NO comparten tablas: cada marca vive en su
-- propio esquema de Postgres, con sus permisos. `public` se queda
-- vacío a propósito, para que nadie deje ahí una tabla por pereza.
--
-- Idempotente: se puede volver a ejecutar sin romper nada.
-- ============================================================

-- ---------- 1. Un esquema por marca ----------
create schema if not exists activala;
create schema if not exists laora;
create schema if not exists acumula;   -- reservado; su migración va aparte

comment on schema activala is 'Marca Activala — activala.es';
comment on schema laora    is 'Marca laOra — laora.es';
comment on schema acumula  is 'App Acumula — reservado, aún sin migrar';

-- ---------- 2. Activala: su tabla sale de public ----------
-- La creó el guion original en `public` y nunca llegó a conectarse
-- (activala.es no llama a Supabase). Se mueve a su sitio.
do $$
begin
  if exists (select 1 from information_schema.tables
              where table_schema = 'public' and table_name = 'interesados') then
    alter table public.interesados set schema activala;
  end if;
end $$;

-- ---------- 3. laOra ----------
create table if not exists laora.interesados (
  id          uuid primary key default gen_random_uuid(),
  creado_en   timestamptz not null default now(),
  nombre      text not null,
  email       text not null,
  whatsapp    text,
  modelo      text,      -- LO-01 … LO-09, o vacío = toda la colección
  mensaje     text
);

create table if not exists laora.reservas (
  id                 uuid primary key default gen_random_uuid(),
  codigo             text unique not null,
  creado_en          timestamptz not null default now(),
  actualizado_en     timestamptz not null default now(),

  ref                text not null,
  modelo             text not null,
  acabado            text not null,

  -- dinero: SIEMPRE lo calcula el servidor, nunca el navegador
  precio_total       numeric(10,2) not null,
  senal              numeric(10,2) not null,
  resto              numeric(10,2) not null,
  iva_porcentaje     numeric(4,1)  not null default 21,

  entrega_prometida  text not null,   -- obligatorio: va en el contrato

  nombre             text not null,
  email              text not null,
  telefono           text not null,
  direccion          text not null,
  cp                 text not null,
  poblacion          text not null,
  provincia          text not null,

  metodo             text not null check (metodo in ('mollie','bizum','transferencia')),
  estado             text not null default 'pendiente'
                     check (estado in ('pendiente','pagada','cancelada','desistida','entregada')),
  mollie_id          text,
  pagada_en          timestamptz,
  notas              text
);

create index if not exists reservas_estado_idx on laora.reservas (estado, creado_en desc);
create index if not exists reservas_mollie_idx on laora.reservas (mollie_id);

create or replace function laora.tocar_reserva()
returns trigger language plpgsql as $$
begin
  new.actualizado_en := now();
  return new;
end;
$$;

drop trigger if exists trg_tocar_reserva on laora.reservas;
create trigger trg_tocar_reserva
  before update on laora.reservas
  for each row execute function laora.tocar_reserva();

-- ---------- 4. Permisos: cada esquema, lo justo ----------
-- Sin esto PostgREST no ve nada: los grants por defecto de Supabase
-- solo cubren `public`.

-- Activala: insertar y nada más (formulario público).
grant usage on schema activala to anon, authenticated;
grant insert on activala.interesados to anon;

-- laOra · interesados: insertar y nada más.
grant usage on schema laora to anon, authenticated;
grant insert on laora.interesados to anon;

-- laOra · reservas: NADA para anon. Solo la Edge Function con
-- service_role, que se salta RLS. Es lo que impide que alguien
-- reserve un reloj de 700 € por un céntimo desde el navegador.
revoke all on laora.reservas from anon, authenticated;

-- ---------- 5. RLS en todo ----------
alter table activala.interesados enable row level security;
alter table laora.interesados    enable row level security;
alter table laora.reservas       enable row level security;

drop policy if exists interesados_insert_anon on activala.interesados;
create policy interesados_insert_anon
  on activala.interesados for insert to anon with check (true);

drop policy if exists interesados_insert_anon on laora.interesados;
create policy interesados_insert_anon
  on laora.interesados for insert to anon with check (true);

-- laora.reservas: sin una sola política = denegado a todo el mundo
-- salvo service_role. Es deliberado, no un olvido.

-- ---------- 6. Vista de trabajo ----------
create or replace view laora.reservas_pendientes as
  select codigo, creado_en, ref, acabado, nombre, telefono, email,
         senal, metodo, estado
    from laora.reservas
   where estado = 'pendiente'
   order by creado_en;

revoke all on laora.reservas_pendientes from anon, authenticated;

-- ---------- 7. Comprobación ----------
select table_schema, table_name
  from information_schema.tables
 where table_schema in ('public','activala','laora','acumula')
 order by table_schema, table_name;
