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
