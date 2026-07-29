-- ============================================================
-- laOra · tabla de reservas (señal del 25 %)
-- Pegar-y-listo en el SQL Editor de Supabase. Idempotente.
--
-- OJO con el patrón: a diferencia de `interesados`, aquí anon NO
-- puede insertar. Las reservas las crea SOLO la Edge Function
-- `crear-reserva` con la service_role, porque es ella quien
-- calcula el importe. Si el navegador pudiera insertar, cualquiera
-- reservaría un reloj de 700 € por un céntimo.
-- ============================================================

create table if not exists public.reservas (
  id                 uuid primary key default gen_random_uuid(),
  codigo             text unique not null,          -- LAORA-XXXXXX, el que ve el cliente
  creado_en          timestamptz not null default now(),
  actualizado_en     timestamptz not null default now(),

  -- qué reserva
  ref                text not null,                 -- LO-01 … LO-09
  modelo             text not null,
  acabado            text not null,                 -- Alba · Levante · Cenit · Eclipse

  -- dinero (SIEMPRE calculado en el servidor, nunca lo que mande el cliente)
  precio_total       numeric(10,2) not null,        -- precio final con IVA
  senal              numeric(10,2) not null,        -- lo que se cobra ahora
  resto              numeric(10,2) not null,        -- lo que se cobra al enviar
  iva_porcentaje     numeric(4,1)  not null default 21,

  -- compromiso de entrega: obligatorio, va en el contrato
  entrega_prometida  text not null,

  -- quién
  nombre             text not null,
  email              text not null,
  telefono           text not null,
  direccion          text not null,
  cp                 text not null,
  poblacion          text not null,
  provincia          text not null,

  -- cómo va
  metodo             text not null
                     check (metodo in ('mollie','bizum','transferencia')),
  estado             text not null default 'pendiente'
                     check (estado in ('pendiente','pagada','cancelada','desistida','entregada')),
  mollie_id          text,
  pagada_en          timestamptz,
  notas              text
);

create index if not exists reservas_estado_idx on public.reservas (estado, creado_en desc);
create index if not exists reservas_mollie_idx on public.reservas (mollie_id);

alter table public.reservas enable row level security;

-- Deny-all para anon y authenticated: ni leer, ni insertar, ni tocar.
-- No se declara ninguna política, que en RLS significa denegar todo.
-- La service_role se salta RLS por definición: es la que usa la Edge Function.
drop policy if exists reservas_insert_anon on public.reservas;
drop policy if exists reservas_select_anon on public.reservas;

-- marca de tiempo de actualización
create or replace function public.tocar_reserva()
returns trigger language plpgsql as $$
begin
  new.actualizado_en := now();
  return new;
end;
$$;

drop trigger if exists trg_tocar_reserva on public.reservas;
create trigger trg_tocar_reserva
  before update on public.reservas
  for each row execute function public.tocar_reserva();

-- ============================================================
-- Aviso por correo al crear la reserva y al confirmarse el pago
-- → Edge Function `avisar-reserva`
-- ANTES de pegar: sustituir <PROYECTO> por la ref del proyecto.
-- ============================================================
create extension if not exists pg_net;

create or replace function public.notificar_reserva()
returns trigger
language plpgsql
security definer
as $$
begin
  -- avisa al crear, y al pasar a pagada (no en cada updatecillo)
  if (tg_op = 'INSERT') or (tg_op = 'UPDATE' and new.estado is distinct from old.estado) then
    perform net.http_post(
      url  := 'https://<PROYECTO>.supabase.co/functions/v1/avisar-reserva',
      body := jsonb_build_object('record', to_jsonb(new), 'evento', tg_op),
      headers := '{"Content-Type":"application/json"}'::jsonb
    );
  end if;
  return new;
end;
$$;

drop trigger if exists trg_notificar_reserva on public.reservas;
create trigger trg_notificar_reserva
  after insert or update on public.reservas
  for each row execute function public.notificar_reserva();

-- ============================================================
-- Vista cómoda para el Table Editor: lo que hay que atender hoy
-- ============================================================
create or replace view public.reservas_pendientes as
  select codigo, creado_en, ref, acabado, nombre, telefono, email,
         senal, metodo, estado
    from public.reservas
   where estado = 'pendiente'
   order by creado_en;
