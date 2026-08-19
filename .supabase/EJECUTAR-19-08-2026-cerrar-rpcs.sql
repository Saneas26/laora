-- ============================================================
-- laOra · CERRAR LAS FUNCIONES (19/08/2026) · URGENTE
-- ------------------------------------------------------------
-- LO QUE PASA AHORA MISMO
--   Postgres, al crear una función, le da permiso de ejecución a
--   TODO EL MUNDO por defecto. Y la clave pública de laOra está —como
--   debe— a la vista en el JavaScript de la web. Resultado: cualquiera
--   puede llamar a estas funciones desde una consola.
--
--   La peor es `siguiente_numero_pedido`: cada llamada CONSUME un
--   número de pedido. Comprobado el 19/08/2026 desde fuera, sin
--   sesión: devolvió «P260819-01». Nadie roba datos con esto, pero
--   cualquiera puede dispararla en bucle y dejar la numeración de la
--   facturación llena de huecos y de saltos.
--
--   Y `apuntar_al_club` deja apuntar a cualquiera al Club —es decir,
--   regalarle dos años de garantía— si se sabe su id.
--
-- LO QUE HACE ESTO
--   Le quita el permiso a todo el mundo y se lo devuelve SOLO al
--   `service_role`, que es la llave que usan las Edge Functions y que
--   nunca sale del servidor. La web no llama a ninguna función
--   directamente: habla con las tablas, y ahí manda RLS.
--
-- Idempotente. Editor SQL de Supabase, proyecto uikanfvigunjhzibnhxf.
-- ============================================================

do $$
declare f record;
begin
  for f in
    select p.oid::regprocedure as firma
      from pg_proc p
      join pg_namespace n on n.oid = p.pronamespace
     where n.nspname = 'laora'
  loop
    execute format('revoke execute on function %s from public, anon, authenticated', f.firma);
    execute format('grant  execute on function %s to service_role', f.firma);
    raise notice 'cerrada: %', f.firma;
  end loop;
end $$;

-- Y que las que se creen a partir de ahora nazcan cerradas.
alter default privileges in schema laora revoke execute on functions from public;

-- ---------- comprobación ----------
-- No debe quedar ninguna fila: son las funciones que anon o
-- authenticated todavía podrían ejecutar.
select p.proname, r.rolname
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  cross join lateral (values ('anon'), ('authenticated')) as r(rolname)
 where n.nspname = 'laora'
   and has_function_privilege(r.rolname, p.oid, 'execute');
