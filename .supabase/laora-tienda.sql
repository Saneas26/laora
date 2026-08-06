-- ============================================================
-- laOra · LA BASE DE LA VENTA
-- ------------------------------------------------------------
-- Socios, pedidos, relojes con su número de serie, garantías y
-- comentarios. Encima de esto van el panel de Óscar y la app de
-- los clientes; sin esto no hay ni lo uno ni lo otro.
--
-- DÓNDE VIVE
--   Proyecto `uikanfvigunjhzibnhxf` (el que se llama «activala» y
--   comparten las marcas), esquema **laora**, creado por
--   `estructura-grupo.sql`. Cada marca en su esquema: `public` se
--   queda vacío a propósito.
--
-- LO QUE YA HABÍA Y NO SE TOCA
--   `laora.interesados` (formulario de la web anterior) y
--   `laora.reservas` (el modelo de reserva con señal, nunca usado:
--   está vacía). Se dejan donde están. Lo de ahora es una venta
--   completa, no una reserva, así que va en tablas nuevas.
--
-- RLS: SÍ, Y AQUÍ SÍ SE PUEDE
--   En Saneas la regla es no activar RLS porque su app lee con la
--   clave anónima. laOra NO: entra con Auth de verdad (el enlace por
--   correo), así que cada socio tiene su `auth.uid()` y las políticas
--   pueden dejar que vea LO SUYO y nada más. Aquí hay direcciones,
--   NIF y números de serie: sin RLS, la clave pública de la web —que
--   está a la vista en el JavaScript— dejaría leerlo todo a cualquiera.
--   El panel no pasa por estas políticas: usa el service role desde su
--   Edge Function, como el de Saneas.
--
-- Idempotente: se puede volver a ejecutar sin romper nada.
-- ============================================================

create schema if not exists laora;

-- ============================================================
-- 1. SOCIOS
-- ------------------------------------------------------------
-- Uno por persona que entra. La fila se crea sola la primera vez
-- que alguien entra con su enlace (ver la función `laora.asegurar_socio`
-- al final), así que nunca hay que darla de alta a mano.
--
-- `id` es la misma que la de `auth.users`: no hay dos identidades.
-- ============================================================
create table if not exists laora.socios (
  id            uuid primary key references auth.users(id) on delete cascade,
  creado_en     timestamptz not null default now(),
  email         text not null,

  -- Se piden al comprar, no al entrar: entrar tiene que costar un clic.
  nombre        text,
  apellidos     text,
  telefono      text,
  nif           text,

  -- Dirección habitual. La del pedido se congela aparte: si alguien
  -- se muda, los pedidos viejos siguen diciendo a dónde se enviaron.
  direccion     text,
  cp            text,
  poblacion     text,
  provincia     text,
  pais          text not null default 'España',

  -- Club laOra. Nulo = no es socio del club, solo cliente.
  club_desde    date,
  notas         text,          -- privadas de Óscar; el socio no las ve
  actualizado_en timestamptz not null default now()
);

comment on table laora.socios is 'Clientes de laOra. La fila la crea la propia app al entrar.';
comment on column laora.socios.notas is 'Privadas de Óscar. Nunca se devuelven a la app.';

-- ============================================================
-- 2. PEDIDOS
-- ------------------------------------------------------------
-- Un pedido = una compra. Los datos de envío y de factura se
-- COPIAN aquí al hacerlo: son los que valen, aunque el socio
-- cambie luego los suyos.
-- ============================================================
create table if not exists laora.pedidos (
  id              uuid primary key default gen_random_uuid(),
  numero          text unique not null,        -- P260806-01
  socio_id        uuid not null references laora.socios(id) on delete restrict,
  creado_en       timestamptz not null default now(),
  actualizado_en  timestamptz not null default now(),

  -- El dinero lo calcula SIEMPRE el servidor desde el catálogo,
  -- nunca lo que diga el navegador.
  importe         numeric(10,2) not null check (importe >= 0),
  envio           numeric(10,2) not null default 0 check (envio >= 0),
  total           numeric(10,2) not null check (total >= 0),

  metodo          text check (metodo in ('paypal','tarjeta','transferencia','bizum','efectivo')),
  estado          text not null default 'solicitado'
                  check (estado in ('solicitado','pagado','preparando','enviado','entregado','cancelado','devuelto')),
  pagado_en       timestamptz,
  referencia_pago text,                        -- id de PayPal o de Mollie

  -- A dónde va, congelado
  env_nombre      text not null,
  env_telefono    text,
  env_direccion   text not null,
  env_cp          text not null,
  env_poblacion   text not null,
  env_provincia   text not null,
  env_pais        text not null default 'España',

  -- Factura: los datos fiscales, también congelados
  fac_nombre      text,
  fac_nif         text,
  fac_direccion   text,
  fac_cp          text,
  fac_poblacion   text,
  fac_provincia   text,
  factura_numero  text,
  factura_fecha   date,

  -- Envío
  transportista   text,
  seguimiento     text,
  enviado_en      timestamptz,
  entregado_en    timestamptz,

  notas           text          -- privadas de Óscar
);

create index if not exists pedidos_socio_idx  on laora.pedidos (socio_id, creado_en desc);
create index if not exists pedidos_estado_idx on laora.pedidos (estado, creado_en desc);

comment on column laora.pedidos.env_nombre is 'Copia congelada: a dónde se envió ESTE pedido, aunque el socio se mude después.';

-- ============================================================
-- 3. LÍNEAS DEL PEDIDO
-- ------------------------------------------------------------
-- Una por reloj comprado. La configuración elegida se copia aquí
-- en texto: si mañana cambia el catálogo, el pedido sigue diciendo
-- qué se vendió exactamente.
-- ============================================================
create table if not exists laora.pedido_lineas (
  id           uuid primary key default gen_random_uuid(),
  pedido_id    uuid not null references laora.pedidos(id) on delete cascade,
  ref          text not null,                  -- LO-01_Lunar_A01
  modelo       text not null,
  acabado      text not null,
  correa       text,
  precio       numeric(10,2) not null check (precio >= 0),
  cantidad     int not null default 1 check (cantidad > 0),
  ficha        jsonb,                          -- las especificaciones, tal como estaban al vender
  creado_en    timestamptz not null default now()
);

create index if not exists lineas_pedido_idx on laora.pedido_lineas (pedido_id);

comment on column laora.pedido_lineas.ficha is 'Especificaciones congeladas del catálogo en el momento de la venta.';

-- ============================================================
-- 4. RELOJES
-- ------------------------------------------------------------
-- El reloj FÍSICO, con su número de serie. No es lo mismo que la
-- línea del pedido: la línea dice qué se compró, esto dice CUÁL se
-- entregó. Un reloj puede existir en stock antes de venderse.
-- ============================================================
create table if not exists laora.relojes (
  id            uuid primary key default gen_random_uuid(),
  numero_serie  text unique not null,          -- LO01-26-0007
  ref           text not null,
  modelo        text not null,
  acabado       text not null,
  correa        text,
  ficha         jsonb,

  estado        text not null default 'stock'
                check (estado in ('stock','asignado','entregado','devuelto','baja')),
  linea_id      uuid unique references laora.pedido_lineas(id) on delete set null,
  socio_id      uuid references laora.socios(id) on delete set null,

  fabricado_en  date,
  entregado_en  date,
  notas         text,
  creado_en     timestamptz not null default now()
);

create index if not exists relojes_estado_idx on laora.relojes (estado, creado_en desc);
create index if not exists relojes_socio_idx  on laora.relojes (socio_id);

comment on table laora.relojes is 'La unidad física. `numero_serie` es único en toda la casa.';

-- ============================================================
-- 5. GARANTÍAS
-- ------------------------------------------------------------
-- Una por reloj entregado. Se abre al entregarlo y dice hasta
-- cuándo cubre. Las intervenciones del taller van aparte.
-- ============================================================
create table if not exists laora.garantias (
  id          uuid primary key default gen_random_uuid(),
  reloj_id    uuid not null unique references laora.relojes(id) on delete cascade,
  socio_id    uuid references laora.socios(id) on delete set null,
  desde       date not null,
  meses       int  not null default 24 check (meses > 0),
  hasta       date not null,
  estado      text not null default 'activa'
              check (estado in ('activa','caducada','anulada')),
  condiciones text,
  notas       text,
  creado_en   timestamptz not null default now()
);

create index if not exists garantias_socio_idx on laora.garantias (socio_id);

-- El taller: qué se le ha hecho a ese reloj y cuándo.
create table if not exists laora.intervenciones (
  id          uuid primary key default gen_random_uuid(),
  reloj_id    uuid not null references laora.relojes(id) on delete cascade,
  fecha       date not null default current_date,
  tipo        text not null default 'revision'
              check (tipo in ('revision','reparacion','ajuste','cambio_correa','pila','otro')),
  en_garantia boolean not null default true,
  descripcion text not null,
  coste       numeric(10,2) default 0,
  creado_en   timestamptz not null default now()
);

create index if not exists intervenciones_reloj_idx on laora.intervenciones (reloj_id, fecha desc);

-- ============================================================
-- 6. COMENTARIOS · los dos tipos
-- ------------------------------------------------------------
-- (a) `mensajes`: la conversación privada entre el socio y la casa.
--     La ve él y la ves tú, nadie más.
-- (b) `valoraciones`: lo que el socio quiere que se lea en la ficha
--     del modelo. No se publica solo: pasa por ti.
-- ============================================================
create table if not exists laora.mensajes (
  id         uuid primary key default gen_random_uuid(),
  socio_id   uuid not null references laora.socios(id) on delete cascade,
  pedido_id  uuid references laora.pedidos(id) on delete set null,
  reloj_id   uuid references laora.relojes(id) on delete set null,
  autor      text not null check (autor in ('socio','laora')),
  texto      text not null check (length(trim(texto)) > 0),
  creado_en  timestamptz not null default now(),
  leido_en   timestamptz
);

create index if not exists mensajes_socio_idx on laora.mensajes (socio_id, creado_en);
-- Para el aviso del panel: cuáles están sin leer por la casa.
create index if not exists mensajes_pendientes_idx on laora.mensajes (creado_en desc)
  where autor = 'socio' and leido_en is null;

create table if not exists laora.valoraciones (
  id           uuid primary key default gen_random_uuid(),
  socio_id     uuid not null references laora.socios(id) on delete cascade,
  modelo       text not null,                  -- el slug del catálogo: lunar, cero-cero…
  reloj_id     uuid references laora.relojes(id) on delete set null,
  estrellas    int  not null check (estrellas between 1 and 5),
  titulo       text,
  texto        text not null check (length(trim(texto)) > 0),
  firma        text,                           -- cómo quiere que salga firmada
  estado       text not null default 'pendiente'
               check (estado in ('pendiente','publicada','rechazada')),
  respuesta    text,                           -- la contestación de la casa, si la hay
  creado_en    timestamptz not null default now(),
  publicada_en timestamptz
);

-- Una valoración por socio y modelo: no se repite opinión.
create unique index if not exists valoraciones_unica_idx on laora.valoraciones (socio_id, modelo);
create index if not exists valoraciones_publicas_idx on laora.valoraciones (modelo, publicada_en desc)
  where estado = 'publicada';

-- ============================================================
-- 7. QUIÉN VE QUÉ
-- ------------------------------------------------------------
-- Sin políticas, activar RLS lo cierra TODO (menos para el service
-- role, que es lo que usa el panel). Así que cada tabla lleva las
-- suyas y son siempre la misma idea: `auth.uid()` = el socio.
-- ============================================================
alter table laora.socios         enable row level security;
alter table laora.pedidos        enable row level security;
alter table laora.pedido_lineas  enable row level security;
alter table laora.relojes        enable row level security;
alter table laora.garantias      enable row level security;
alter table laora.intervenciones enable row level security;
alter table laora.mensajes       enable row level security;
alter table laora.valoraciones   enable row level security;

do $$
begin
  -- --- lo suyo, solo lo suyo ---
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='socios' and policyname='socio_ve_lo_suyo') then
    create policy socio_ve_lo_suyo on laora.socios
      for select to authenticated using (id = auth.uid());
  end if;
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='socios' and policyname='socio_edita_lo_suyo') then
    create policy socio_edita_lo_suyo on laora.socios
      for update to authenticated using (id = auth.uid()) with check (id = auth.uid());
  end if;

  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='pedidos' and policyname='sus_pedidos') then
    create policy sus_pedidos on laora.pedidos
      for select to authenticated using (socio_id = auth.uid());
  end if;

  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='pedido_lineas' and policyname='sus_lineas') then
    create policy sus_lineas on laora.pedido_lineas
      for select to authenticated using (exists (
        select 1 from laora.pedidos p where p.id = pedido_id and p.socio_id = auth.uid()));
  end if;

  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='relojes' and policyname='sus_relojes') then
    create policy sus_relojes on laora.relojes
      for select to authenticated using (socio_id = auth.uid());
  end if;

  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='garantias' and policyname='sus_garantias') then
    create policy sus_garantias on laora.garantias
      for select to authenticated using (socio_id = auth.uid());
  end if;

  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='intervenciones' and policyname='sus_intervenciones') then
    create policy sus_intervenciones on laora.intervenciones
      for select to authenticated using (exists (
        select 1 from laora.relojes r where r.id = reloj_id and r.socio_id = auth.uid()));
  end if;

  -- --- la conversación: lee la suya y escribe solo como socio ---
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='mensajes' and policyname='su_conversacion') then
    create policy su_conversacion on laora.mensajes
      for select to authenticated using (socio_id = auth.uid());
  end if;
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='mensajes' and policyname='escribe_como_socio') then
    create policy escribe_como_socio on laora.mensajes
      for insert to authenticated with check (socio_id = auth.uid() and autor = 'socio');
  end if;

  -- --- valoraciones: las publicadas las lee cualquiera ---
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='valoraciones' and policyname='publicadas_a_la_vista') then
    create policy publicadas_a_la_vista on laora.valoraciones
      for select to anon, authenticated using (estado = 'publicada');
  end if;
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='valoraciones' and policyname='ve_la_suya') then
    create policy ve_la_suya on laora.valoraciones
      for select to authenticated using (socio_id = auth.uid());
  end if;
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='valoraciones' and policyname='escribe_la_suya') then
    create policy escribe_la_suya on laora.valoraciones
      for insert to authenticated with check (socio_id = auth.uid() and estado = 'pendiente');
  end if;
  -- Puede corregir la suya, pero NO publicarla: eso lo decide la casa.
  if not exists (select 1 from pg_policies where schemaname='laora' and tablename='valoraciones' and policyname='corrige_la_suya') then
    create policy corrige_la_suya on laora.valoraciones
      for update to authenticated
      using (socio_id = auth.uid() and estado = 'pendiente')
      with check (socio_id = auth.uid() and estado = 'pendiente');
  end if;
end $$;

-- La web anónima solo puede leer las valoraciones publicadas: para eso
-- necesita el permiso de tabla, además de la política de arriba.
grant usage on schema laora to anon, authenticated;
grant select on laora.valoraciones to anon;
grant select, update on laora.socios to authenticated;
grant select on laora.pedidos, laora.pedido_lineas, laora.relojes,
                laora.garantias, laora.intervenciones to authenticated;
grant select, insert on laora.mensajes to authenticated;
grant select, insert, update on laora.valoraciones to authenticated;

-- ============================================================
-- 8. LO QUE SE HACE SOLO
-- ============================================================

-- `actualizado_en` al día, sin acordarse de ponerlo en cada update.
create or replace function laora.sellar_actualizado() returns trigger
language plpgsql as $$
begin
  new.actualizado_en = now();
  return new;
end $$;

drop trigger if exists socios_sellar  on laora.socios;
create trigger socios_sellar  before update on laora.socios
  for each row execute function laora.sellar_actualizado();

drop trigger if exists pedidos_sellar on laora.pedidos;
create trigger pedidos_sellar before update on laora.pedidos
  for each row execute function laora.sellar_actualizado();

-- La garantía sabe sola hasta cuándo llega.
create or replace function laora.calcular_hasta() returns trigger
language plpgsql as $$
begin
  new.hasta = (new.desde + (new.meses || ' months')::interval)::date;
  if new.hasta < current_date and new.estado = 'activa' then
    new.estado = 'caducada';
  end if;
  return new;
end $$;

drop trigger if exists garantias_hasta on laora.garantias;
create trigger garantias_hasta before insert or update of desde, meses on laora.garantias
  for each row execute function laora.calcular_hasta();

-- Entrar crea el socio. La app llama a esto justo después del enlace
-- del correo, y así nadie tiene que darse de alta dos veces.
create or replace function laora.asegurar_socio()
returns laora.socios
language plpgsql security definer set search_path = laora, public as $$
declare fila laora.socios;
begin
  if auth.uid() is null then
    raise exception 'hay que haber entrado';
  end if;

  insert into laora.socios (id, email)
  values (auth.uid(), coalesce(auth.jwt() ->> 'email', ''))
  on conflict (id) do nothing;

  select * into fila from laora.socios where id = auth.uid();
  return fila;
end $$;

grant execute on function laora.asegurar_socio() to authenticated;

-- El número de pedido: P + AAMMDD + correlativo del día.
-- El candado evita que dos compras a la vez saquen el mismo número.
create or replace function laora.siguiente_numero_pedido(p_fecha date default current_date)
returns text
language plpgsql security definer set search_path = laora, public as $$
declare n int;
begin
  perform pg_advisory_xact_lock(hashtext('laora.pedidos.numero'));
  select count(*) + 1 into n from laora.pedidos
   where creado_en::date = p_fecha;
  return 'P' || to_char(p_fecha, 'YYMMDD') || '-' || lpad(n::text, 2, '0');
end $$;

-- ============================================================
-- 9. COMPROBACIÓN
-- ============================================================
select table_name,
       (select count(*) from information_schema.columns c
         where c.table_schema = 'laora' and c.table_name = t.table_name) as columnas
  from information_schema.tables t
 where t.table_schema = 'laora'
 order by table_name;
