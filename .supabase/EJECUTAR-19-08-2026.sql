-- ============================================================
-- laOra · AJUSTES PARA COBRAR CON MOLLIE (19/08/2026)
-- ------------------------------------------------------------
-- Dos retoques en `laora.pedidos` para que la pasarela quepa:
--
--   1. Un estado nuevo: AUTORIZADO. Es el de Klarna entre que el
--      cliente compra y el reloj sale por la puerta. El dinero está
--      reservado pero todavía NO cobrado, y se captura al marcar el
--      pedido como enviado. Sin este estado habría que mentir y
--      llamarlo «pagado», que es justo lo que no es.
--
--   2. Dos formas de pago más: `klarna` y `mollie`. El método real
--      lo escribe el webhook cuando Mollie dice con qué se pagó.
--
-- Idempotente: se puede volver a ejecutar sin romper nada.
-- Se ejecuta en el editor SQL de Supabase, proyecto uikanfvigunjhzibnhxf.
-- ============================================================

-- ---------- 1. el estado ----------
alter table laora.pedidos drop constraint if exists pedidos_estado_check;
alter table laora.pedidos add  constraint pedidos_estado_check
  check (estado in ('solicitado','autorizado','pagado','preparando',
                    'enviado','entregado','cancelado','devuelto'));

comment on column laora.pedidos.estado is
  'autorizado = Klarna ha aprobado el pago pero el dinero NO está cobrado; se captura al enviar.';

-- ---------- 2. las formas de pago ----------
alter table laora.pedidos drop constraint if exists pedidos_metodo_check;
alter table laora.pedidos add  constraint pedidos_metodo_check
  check (metodo in ('tarjeta','klarna','bizum','paypal',
                    'transferencia','efectivo','mollie'));

comment on column laora.pedidos.referencia_pago is
  'El id del pago en Mollie (tr_…). Es por donde el webhook encuentra el pedido y por donde se captura Klarna.';

-- ---------- 3. comprobación ----------
-- Debe devolver las dos restricciones nuevas.
select conname, pg_get_constraintdef(oid)
  from pg_constraint
 where conrelid = 'laora.pedidos'::regclass
   and conname in ('pedidos_estado_check','pedidos_metodo_check');
