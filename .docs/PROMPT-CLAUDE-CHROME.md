# Prompt para Claude in Chrome · ejecutar el SQL de laOra

Copia todo lo que hay **dentro del recuadro** y pégalo en Claude in Chrome.

---

```
Necesito que ejecutes un guion SQL en Supabase. Es la base de producción de
laOra, así que lee entero esto antes de tocar nada.

EL PROYECTO
  Nombre: activala
  Ref:    uikanfvigunjhzibnhxf
  Es el proyecto compartido del grupo. Dentro conviven varios esquemas
  (laora, activala, acumula). TODO lo que vas a ejecutar toca únicamente
  el esquema `laora`. Si algo intentara tocar otro esquema, para y avísame.

EL GUION
  Está en mi disco:
  file:///Users/oscar/Sites/laora/.supabase/EJECUTAR-10-08-2026.sql

  Ábrelo en una pestaña, selecciona todo el texto y cópialo.
  Si el navegador no te deja abrir archivos locales, dímelo y te lo pego yo.

QUÉ HACER, POR ORDEN
  1. Ve a https://supabase.com/dashboard/project/uikanfvigunjhzibnhxf/sql/new
  2. Comprueba ARRIBA A LA IZQUIERDA que el proyecto es «activala».
     Si pone otro, cámbialo antes de seguir.
  3. Pega el guion entero en el editor.
  4. Antes de ejecutar, dime cuántas líneas has pegado y qué dice la
     primera línea. Quiero confirmar que se ha pegado completo.
  5. Espera a que te diga que sí.
  6. Pulsa RUN.
  7. Cópiame el resultado tal cual, y cualquier error en rojo, entero.

QUÉ ESPERAR SI HA IDO BIEN
  La última consulta del guion es una comprobación y debe devolver tres
  filas parecidas a estas:
    metodos permitidos → CHECK (metodo = ANY (ARRAY['paypal', 'tarjeta',
                         'transferencia', 'bizum1', 'bizum2', 'efectivo']))
    vistas nuevas      → cobros_metodo, compra_pendiente, cuentas_anio,
                         cuentas_trimestre, pedido_cuentas
    tabla gastos       → 13 columnas

LO QUE NO DEBES HACER
  · No ejecutes ninguna otra consulta, ni de prueba.
  · No borres, vacíes ni modifiques ninguna tabla que no esté en el guion.
  · No toques los proyectos «saneas-app» ni «acumula».
  · No cambies ajustes del proyecto, ni claves, ni políticas RLS.
  · Si algo no cuadra —el proyecto no es el que digo, el guion se ha
    pegado a medias, sale un error— PARA y pregúntame. No improvises.

UNA COSA QUE VA A CAMBIAR DATOS, y es a propósito
  Hay una línea que convierte los pedidos con metodo 'bizum' en 'bizum1'.
  Es intencionado: ahora hay dos números de Bizum y hay que distinguirlos.
  Si me dices cuántas filas ha cambiado, mejor.
```

---

## Después, en el terminal (esto no lo hace el navegador)

La Edge Function se despliega desde aquí, que el CLI ya está autenticado:

```bash
supabase functions deploy panel-laora --project-ref uikanfvigunjhzibnhxf --no-verify-jwt
```

## Y para comprobar que todo está en pie

Entra en https://laora.es/panel.html y abre **Compras** y **Cuentas**. Si el
SQL está ejecutado y la función desplegada, las dos pintan sus tablas —vacías
mientras no haya pedidos, que es lo correcto—. Si sale un error en rojo, falta
uno de los dos pasos.
