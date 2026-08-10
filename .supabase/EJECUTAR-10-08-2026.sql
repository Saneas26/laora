-- ============================================================
-- laOra · LO QUE HAY QUE EJECUTAR · 10/08/2026
-- ------------------------------------------------------------
-- Los dos guiones pendientes, en el orden correcto y en un solo
-- archivo para pegarlo de una vez en el SQL Editor de Supabase.
--
--   PROYECTO: activala  (ref uikanfvigunjhzibnhxf)
--   ESQUEMA:  laora
--
--   1) referencias.sql   la referencia de configuración y la lista
--                        de la compra agrupada
--   2) panel-cuentas.sql los dos Bizum, los gastos, la factura y
--                        los cierres por trimestre y año
--
-- TODO ES ADITIVO salvo dos cosas, y las dos son a propósito:
--   · los pedidos con metodo 'bizum' pasan a 'bizum1'
--   · la regla de `metodo` se estrecha para excluir 'bizum' a secas
--
-- Se puede volver a ejecutar entero sin romper nada: las tablas y
-- columnas van con IF NOT EXISTS y las vistas con OR REPLACE.
-- ============================================================


-- ############ 1 de 2 · referencias.sql ############

-- ============================================================
-- laOra · LA REFERENCIA DE CONFIGURACIÓN
-- ------------------------------------------------------------
-- Encargo de Óscar, 08/08/2026: «cuando un cliente configure el suyo,
-- yo debo saber perfectamente lo que comprar».
--
-- TODAVÍA NO SE HA EJECUTADO. Es aditivo y no borra nada, pero toca la
-- base de producción, así que espera el visto bueno.
--
-- LOS TRES CÓDIGOS, QUE NO SE MEZCLAN
-- ------------------------------------------------------------
--   pedidos.numero          P260806-01     ¿qué compra fue?
--   pedido_lineas.ref       LO-03-M1-C1-B09.2   ¿qué se compró?
--   relojes.numero_serie    LO03-26-0007   ¿qué unidad se entregó?
--
-- Dos clientes que configuren lo mismo comparten `ref` y NO comparten
-- `numero_serie`. La garantía va contra la serie; la compra, contra la
-- referencia.
--
-- LA REFERENCIA
-- ------------------------------------------------------------
--   LO-03 - M1 - C1 - B09.2
--     │     │    │     │ └─ variante 2 de esa familia
--     │     │    │     └─── brazalete 09 del catálogo ENTERO
--     │     │    └───────── caja 1 de ese modelo
--     │     └────────────── movimiento 1 de ese modelo
--     └──────────────────── modelo (columna A de Movimientos)
--
-- El brazalete se numera en el catálogo entero y no dentro del modelo,
-- porque la misma pieza la montan varios relojes. Numerado por modelo,
-- el mismo brazalete sería «B1» en el Lunar y «B3» en el Cero Cero, y
-- un día se compraría el que no es.
--
-- Y no lleva ni una palabra: los nombres cambian y las filas no.
--
-- OJO CON EL CÓDIGO DE MODELO
-- ------------------------------------------------------------
-- Óscar zanjó que manda la columna A de Movimientos. Ahí el Lunar es
-- LO-03, no LO-01 como decía la web. Antes de ejecutar esto hay que
-- cambiar los códigos de `catalogo.json`; si no, la web compone
-- referencias que no existen en la biblioteca.
-- ============================================================

-- ------------------------------------------------------------
-- 1. LAS TRES PIEZAS EN LA LÍNEA DEL PEDIDO
-- ------------------------------------------------------------
-- `ref` ya existe y sigue siendo la referencia completa. Lo que falta
-- son los tres identificadores SUELTOS: sin ellos, para montar la lista
-- de compra habría que partir la cadena, y una cadena partida es una
-- cadena mal partida el día que cambie el formato.
alter table laora.pedido_lineas
  add column if not exists modelo_ref text,   -- LO-03
  add column if not exists mov_ref    text,   -- M1
  add column if not exists caja_ref   text,   -- C1
  add column if not exists brz_ref    text;   -- B09.2

comment on column laora.pedido_lineas.modelo_ref is 'Columna A de la hoja Movimientos.';
comment on column laora.pedido_lineas.brz_ref is
  'Familia.variante del catálogo ENTERO de brazaletes, no del modelo.';

-- ------------------------------------------------------------
-- 2. LO QUE HAY QUE COMPRAR, CONGELADO
-- ------------------------------------------------------------
-- `ficha` ya guarda las especificaciones que vio el cliente. Esto es lo
-- otro: lo que TÚ tienes que comprar, con el nombre del proveedor —el
-- interno, el que dice «tipo Omega»—, su enlace y lo que costaba ese
-- día.
--
-- Va congelado a propósito. Si mañana cambias de proveedor o sube el
-- precio, el pedido de ayer tiene que seguir diciendo exactamente lo
-- que se vendió: para la garantía, para la factura y para Hacienda.
--
-- Forma esperada:
--   [{"pieza":"movimiento","ref":"M1","interno":"Seiko/TMI VK63",
--     "coste":27.59,"link":"https://…"},
--    {"pieza":"caja", …}, {"pieza":"brazalete", …, "talla":"20 mm"}]
alter table laora.pedido_lineas
  add column if not exists compra jsonb;

comment on column laora.pedido_lineas.compra is
  'Las tres piezas a comprar, con nombre interno, enlace y coste del día de la venta.';

-- El coste del día de la venta, para poder ver el margen real sin
-- recalcular nada. El PVP ya está en `precio`.
alter table laora.pedido_lineas
  add column if not exists coste numeric(10,2) check (coste >= 0);

-- ------------------------------------------------------------
-- 3. EL RELOJ FÍSICO HEREDA LAS PIEZAS
-- ------------------------------------------------------------
-- Hace falta para el taller: dentro de tres años, con el reloj en la
-- mano y solo su número de serie, hay que saber qué movimiento lleva
-- para pedir el recambio.
alter table laora.relojes
  add column if not exists modelo_ref text,
  add column if not exists mov_ref    text,
  add column if not exists caja_ref   text,
  add column if not exists brz_ref    text,
  add column if not exists compra     jsonb;

-- ------------------------------------------------------------
-- 4. LA LISTA DE COMPRA AGRUPADA
-- ------------------------------------------------------------
-- Con cinco pedidos abiertos no se abren cinco fichas: se compra una
-- vez. Esta vista junta las piezas pendientes de todos los pedidos
-- pagados que aún no se han enviado, y dice cuántas van de cada una.
--
-- Un pedido al proveedor en vez de cinco: menos portes y menos errores.
create or replace view laora.compra_pendiente as
select
  p.pieza ->> 'pieza'                       as tipo,
  p.pieza ->> 'ref'                         as ref,
  p.pieza ->> 'interno'                     as interno,
  p.pieza ->> 'talla'                       as talla,
  p.pieza ->> 'link'                        as link,
  count(*)                                  as unidades,
  round(sum((p.pieza ->> 'coste')::numeric), 2) as coste_total,
  array_agg(distinct ped.numero order by ped.numero) as pedidos
from laora.pedido_lineas l
join laora.pedidos ped on ped.id = l.pedido_id
cross join lateral jsonb_array_elements(l.compra) as p(pieza)
where ped.estado in ('pagado', 'preparando')
group by 1, 2, 3, 4, 5
order by 1, 2;

comment on view laora.compra_pendiente is
  'Qué hay que pedirle al proveedor ahora mismo, juntando todos los pedidos pagados sin enviar.';

-- ------------------------------------------------------------
-- 5. COMPROBACIÓN
-- ------------------------------------------------------------
select column_name, data_type
  from information_schema.columns
 where table_schema = 'laora'
   and table_name = 'pedido_lineas'
   and column_name in ('modelo_ref','mov_ref','caja_ref','brz_ref','compra','coste')
 order by column_name;


-- ############ 2 de 2 · panel-cuentas.sql ############

-- ============================================================
-- laOra · LAS CUENTAS DEL PANEL
-- ------------------------------------------------------------
-- Encargo de Óscar, 08/08/2026:
--
--   «Después un apartado de ingresos y costes, totales, por trimestre
--    y anual… Bizum 1, Bizum 2, Tarjetas, Paypal, etc… al igual que lo
--    tengo en Saneas panel»
--
-- TODAVÍA NO SE HA EJECUTADO. Es aditivo salvo en un sitio —el `metodo`
-- de los pedidos, que se estrecha— y ese está explicado abajo.
--
-- Va DESPUÉS de `referencias.sql`, porque el coste de las piezas sale
-- de la columna `coste` que añade aquel.
--
-- LOS TRES DINEROS, QUE NO SON EL MISMO
-- ------------------------------------------------------------
--   ingresos   lo que entra por ventas cobradas
--   piezas     lo que cuesta lo que se vendió (va con la venta)
--   gastos     todo lo demás: portes, útiles, comisiones, publicidad
--
-- El margen sin los gastos es un espejismo: enseña un negocio que no
-- existe. Por eso las tres columnas van juntas o no van.
--
-- EL IVA
-- ------------------------------------------------------------
-- laOra factura con IVA del 21 %, no con IGIC: la empresa recibe y
-- vende desde Madrid. Los precios de la web son FINALES, con el IVA
-- dentro, así que la base se saca dividiendo, nunca multiplicando.
-- ============================================================


-- ------------------------------------------------------------
-- 1. LOS MÉTODOS DE COBRO
-- ------------------------------------------------------------
-- «Bizum» a secas no vale cuando hay DOS números: al cuadrar el banco
-- no se sabe cuál de los dos recibió el dinero. Se parte en dos.
--
-- Lo que había se convierte en `bizum1` antes de estrechar la regla,
-- para no dejar ninguna fila fuera. Si no hay pedidos por Bizum, esta
-- línea no hace nada y tampoco molesta.
update laora.pedidos set metodo = 'bizum1' where metodo = 'bizum';

alter table laora.pedidos drop constraint if exists pedidos_metodo_check;
alter table laora.pedidos add constraint pedidos_metodo_check
  check (metodo in ('paypal','tarjeta','transferencia','bizum1','bizum2','efectivo'));

comment on column laora.pedidos.metodo is
  'bizum1 y bizum2 son los DOS números de Bizum: sin separarlos no se cuadra el banco.';


-- ------------------------------------------------------------
-- 2. LOS GASTOS QUE NO SON PIEZAS
-- ------------------------------------------------------------
-- Los portes, la caja de presentación, la comisión de la pasarela, el
-- dominio, la publicidad. Nada de esto está en ningún pedido y sin
-- ello el margen sale inflado.
--
-- `pedido_id` es opcional a propósito: un porte se puede imputar a su
-- pedido, y el dominio no se imputa a ninguno.
create table if not exists laora.gastos (
  id          uuid primary key default gen_random_uuid(),
  fecha       date not null default current_date,
  concepto    text not null,
  categoria   text not null default 'otro'
              check (categoria in ('piezas','envio','embalaje','comision',
                                   'herramienta','web','publicidad','impuesto','otro')),
  importe     numeric(10,2) not null check (importe >= 0),   -- con IVA incluido
  iva         numeric(10,2) not null default 0 check (iva >= 0),
  proveedor   text,
  factura     text,                      -- su número de factura, para Hacienda
  enlace      text,                      -- el anuncio o el justificante
  pedido_id   uuid references laora.pedidos(id) on delete set null,
  notas       text,
  creado_en   timestamptz not null default now()
);

create index if not exists gastos_fecha_idx on laora.gastos (fecha desc);
create index if not exists gastos_pedido_idx on laora.gastos (pedido_id);

comment on table laora.gastos is
  'Lo que se gasta y NO es una pieza vendida. Sin esto el margen miente.';


-- ------------------------------------------------------------
-- 3. LA FACTURA
-- ------------------------------------------------------------
-- El número no se escribe a mano jamás: en una serie de facturas no
-- puede haber huecos ni repetidos, y eso lo pierde una persona en
-- cuanto emite dos el mismo día.
--
--   F26-0001   serie del AÑO, correlativa, sin saltos
create or replace function laora.siguiente_numero_factura(p_fecha date default current_date)
returns text
language plpgsql security definer set search_path = laora, public as $$
declare n int;
begin
  perform pg_advisory_xact_lock(hashtext('laora.pedidos.factura'));
  select count(*) + 1 into n
    from laora.pedidos
   where factura_numero is not null
     and extract(year from factura_fecha) = extract(year from p_fecha);
  return 'F' || to_char(p_fecha, 'YY') || '-' || lpad(n::text, 4, '0');
end $$;

-- Emitir es un acto único: si el pedido ya tiene factura, DEVUELVE LA
-- SUYA y no inventa otra. Volver a pulsar el botón no puede duplicar
-- una factura ya entregada a un cliente.
create or replace function laora.emitir_factura(p_pedido uuid, p_fecha date default current_date)
returns text
language plpgsql security definer set search_path = laora, public as $$
declare v_num text; v_estado text;
begin
  select factura_numero, estado into v_num, v_estado
    from laora.pedidos where id = p_pedido for update;

  if not found then raise exception 'Ese pedido no existe'; end if;
  if v_num is not null then return v_num; end if;

  -- No se factura lo que no se ha cobrado.
  if v_estado = 'solicitado' or v_estado = 'cancelado' then
    raise exception 'El pedido % no está cobrado: no se puede facturar', p_pedido;
  end if;

  v_num := laora.siguiente_numero_factura(p_fecha);
  update laora.pedidos
     set factura_numero = v_num, factura_fecha = p_fecha
   where id = p_pedido;
  return v_num;
end $$;

comment on function laora.emitir_factura(uuid, date) is
  'Da número de factura al pedido. Si ya lo tiene, devuelve el mismo: nunca duplica.';


-- ------------------------------------------------------------
-- 4. EL DINERO DE CADA PEDIDO
-- ------------------------------------------------------------
-- Una fila por pedido con todo lo que hace falta para cuadrar: lo que
-- entró, lo que costaron sus piezas, lo que se le imputó de gastos y
-- lo que queda. El IVA sale de dentro del precio, que es como se
-- venden en la web.
create or replace view laora.pedido_cuentas as
select
  p.id,
  p.numero,
  p.creado_en::date                                   as fecha,
  p.pagado_en::date                                   as fecha_cobro,
  p.estado,
  p.metodo,
  p.factura_numero,
  p.factura_fecha,
  p.env_nombre                                        as cliente,
  p.total                                             as ingreso,
  round(p.total / 1.21, 2)                            as base,
  round(p.total - p.total / 1.21, 2)                  as iva,
  coalesce(lin.piezas, 0)                             as piezas,
  coalesce(gas.gastos, 0)                             as gastos,
  round(p.total - coalesce(lin.piezas,0) - coalesce(gas.gastos,0), 2) as margen
from laora.pedidos p
left join lateral (
  select round(sum(l.coste * l.cantidad), 2) as piezas
    from laora.pedido_lineas l where l.pedido_id = p.id
) lin on true
left join lateral (
  select round(sum(g.importe), 2) as gastos
    from laora.gastos g where g.pedido_id = p.id
) gas on true;

comment on view laora.pedido_cuentas is
  'Un pedido, una fila, y las cuatro cifras que importan: ingreso, piezas, gastos y margen.';


-- ------------------------------------------------------------
-- 5. EL CIERRE POR TRIMESTRE
-- ------------------------------------------------------------
-- La unidad del autónomo es el trimestre, no el mes: es cuando se
-- presentan los modelos. Va por FECHA DE COBRO, no por fecha de
-- pedido: un pedido de marzo cobrado en abril es del segundo
-- trimestre, y confundirlo es declarar mal.
--
-- Solo cuenta lo cobrado. Un pedido solicitado y sin pagar no es un
-- ingreso, es una esperanza.
create or replace view laora.cuentas_trimestre as
with ventas as (
  select
    extract(year    from p.pagado_en)::int as anio,
    extract(quarter from p.pagado_en)::int as trimestre,
    count(*)                               as pedidos,
    sum(c.ingreso)                         as ingresos,
    sum(c.base)                            as base,
    sum(c.iva)                             as iva_repercutido,
    sum(c.piezas)                          as piezas
  from laora.pedidos p
  join laora.pedido_cuentas c on c.id = p.id
  where p.pagado_en is not null
    and p.estado not in ('cancelado','devuelto')
  group by 1, 2
),
costes as (
  select
    extract(year    from g.fecha)::int as anio,
    extract(quarter from g.fecha)::int as trimestre,
    sum(g.importe)                     as gastos,
    sum(g.iva)                         as iva_soportado
  from laora.gastos g
  -- TODOS los gastos, imputados a un pedido o no. No hay doble conteo:
  -- `piezas` sale de las líneas del pedido y aquí no entra ninguna.
  group by 1, 2
)
select
  coalesce(v.anio, c.anio)                as anio,
  coalesce(v.trimestre, c.trimestre)      as trimestre,
  coalesce(v.pedidos, 0)                  as pedidos,
  coalesce(v.ingresos, 0)                 as ingresos,
  coalesce(v.base, 0)                     as base,
  coalesce(v.iva_repercutido, 0)          as iva_repercutido,
  coalesce(v.piezas, 0)                   as piezas,
  coalesce(c.gastos, 0)                   as gastos,
  coalesce(c.iva_soportado, 0)            as iva_soportado,
  round(coalesce(v.ingresos,0) - coalesce(v.piezas,0) - coalesce(c.gastos,0), 2) as margen,
  round(coalesce(v.iva_repercutido,0) - coalesce(c.iva_soportado,0), 2)          as iva_a_pagar
from ventas v
full outer join costes c on c.anio = v.anio and c.trimestre = v.trimestre
order by 1 desc, 2 desc;

comment on view laora.cuentas_trimestre is
  'El cierre trimestral, por FECHA DE COBRO. Un pedido de marzo cobrado en abril es del 2T.';


-- ------------------------------------------------------------
-- 6. EL CIERRE ANUAL
-- ------------------------------------------------------------
create or replace view laora.cuentas_anio as
select
  anio,
  sum(pedidos)          as pedidos,
  sum(ingresos)         as ingresos,
  sum(base)             as base,
  sum(iva_repercutido)  as iva_repercutido,
  sum(piezas)           as piezas,
  sum(gastos)           as gastos,
  sum(margen)           as margen,
  sum(iva_a_pagar)      as iva_a_pagar
from laora.cuentas_trimestre
group by anio
order by anio desc;


-- ------------------------------------------------------------
-- 7. LO QUE HA ENTRADO POR CADA SITIO
-- ------------------------------------------------------------
-- Para cuadrar el banco: cuánto por cada Bizum, cuánto por tarjeta,
-- cuánto por PayPal. Sin esto, dos Bizum son un montón indistinguible.
create or replace view laora.cobros_metodo as
select
  extract(year    from pagado_en)::int as anio,
  extract(quarter from pagado_en)::int as trimestre,
  coalesce(metodo, 'sin indicar')      as metodo,
  count(*)                             as pedidos,
  sum(total)                           as importe
from laora.pedidos
where pagado_en is not null
  and estado not in ('cancelado','devuelto')
group by 1, 2, 3
order by 1 desc, 2 desc, 5 desc;


-- ------------------------------------------------------------
-- 8. COMPROBACIÓN
-- ------------------------------------------------------------
select 'metodos permitidos' as que,
       pg_get_constraintdef(oid) as valor
  from pg_constraint where conname = 'pedidos_metodo_check'
union all
select 'vistas nuevas', string_agg(table_name, ', ' order by table_name)
  from information_schema.views
 where table_schema = 'laora'
   and table_name in ('pedido_cuentas','cuentas_trimestre','cuentas_anio',
                      'cobros_metodo','compra_pendiente')
union all
select 'tabla gastos', count(*)::text || ' columnas'
  from information_schema.columns
 where table_schema = 'laora' and table_name = 'gastos';
