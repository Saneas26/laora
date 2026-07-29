-- ============================================================
-- laOra · tabla de interesados (formulario público de la web)
-- Pegar-y-listo en el SQL Editor de Supabase. Idempotente.
-- Patrón del grupo: tabla INSERT-ONLY para anon. Nadie puede leer,
-- editar ni borrar desde el cliente. Los datos se ven en Table Editor.
-- ============================================================

create table if not exists public.interesados (
  id          uuid primary key default gen_random_uuid(),
  creado_en   timestamptz not null default now(),
  nombre      text not null,
  email       text not null,
  whatsapp    text,
  modelo      text,      -- LO-01 «Lunar» … LO-09 «Cóctel», o vacío = toda la colección
  mensaje     text
);

alter table public.interesados enable row level security;

-- Solo INSERT para anon. Sin políticas de select/update/delete: deny-all.
drop policy if exists interesados_insert_anon on public.interesados;
create policy interesados_insert_anon
  on public.interesados for insert to anon
  with check (true);

-- ============================================================
-- Aviso por correo: trigger con pg_net → Edge Function avisar-interesado
-- (equivalente por SQL del Database Webhook, por si el panel no los muestra).
-- ANTES de pegar: sustituir <PROYECTO> por la ref del proyecto Supabase de laOra.
-- ============================================================

create extension if not exists pg_net;

create or replace function public.notificar_interesado()
returns trigger
language plpgsql
security definer
as $$
begin
  perform net.http_post(
    url  := 'https://<PROYECTO>.supabase.co/functions/v1/avisar-interesado',
    body := jsonb_build_object('record', to_jsonb(new)),
    headers := '{"Content-Type":"application/json"}'::jsonb
  );
  return new;
end;
$$;

drop trigger if exists trg_notificar_interesado on public.interesados;
create trigger trg_notificar_interesado
  after insert on public.interesados
  for each row execute function public.notificar_interesado();
