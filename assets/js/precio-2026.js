/* ============================================================
   laOra · EL MOTOR DE PRECIO, 2026
   ============================================================
   Cómo se convierte el COSTE de compra de un reloj en su PVP: el coste
   completo, el multiplicador, el redondeo al 9,90, el 2,5 % de la
   pasarela y el suelo de la REGLA Nº1.

   POR QUÉ ESTÁ AQUÍ Y NO EN CADA FICHA. Hasta el 29/08/2026 estas mismas
   46 líneas estaban COPIADAS, palabra por palabra, dentro de `lunar.html`
   y de `trinchera.html`. Dos relojes vendiendo con dos copias de la regla
   que decide cuánto cobran: el día que Óscar cambie el multiplicador o el
   suelo y solo se toque una, el otro sigue cobrando con la regla vieja y
   nadie se entera hasta que alguien cuadre las cuentas.

   LO QUE NO ESTÁ AQUÍ es de qué se compone el coste de cada reloj —qué
   paquete monta el proveedor, qué correa se paga aparte, qué añade el
   dúo—. Eso es de cada modelo y se queda en su ficha. Aquí solo entra un
   número, el coste, y sale otro, el precio.

   Uso:
       var P = window.laoraPrecio;
       function precio() {
         return Math.max(P.redondea(P.pvpBase(costes()) * P.KLARNA),
                         P.sueloPvp(P.costeCompleto(costes())));
       }
   ============================================================ */
(function () {
  var IVA = 0.21, IRPF = 0.20, SS = 0.05, MULT = 2.28;

  /* EL COSTE COMPLETO (Óscar, 22/08/2026).
     «Todos los costes tienen que incluir packing + envío + 5 % de SS,
     todos. Y a partir de ahí se aplica el multiplicador.»

     · Las piezas de AliExpress se anuncian SIN IVA. Para el margen valen
       lo anunciado: el IVA soportado de la compra se descuenta del
       repercutido en la liquidación, así que no se pierde.
     · Packing y envío: 9 € CON IVA, como siempre — su parte sin IVA es
       la que cuesta de verdad.
     · Fondo de garantía: 4 € por reloj (antes era un 5 % del movimiento,
       que se quedaba corto).
     · Seguridad Social: un 5 % del coste. Es un gasto, no un impuesto
       sobre lo que ganas.

     LA COMISIÓN, AL 5 % DESDE EL 30/08/2026. Estaba al 2,5 % —la mitad,
     porque solo la mitad de las ventas van por Klarna— y eso vale para el
     margen MEDIO, pero no para el SUELO: la REGLA Nº1 se mide con Klarna
     al 5 % ([[laora-suelo-por-canal]]), porque al cliente concreto que
     paga por Klarna no se le puede vender por debajo de 50 € limpios. Con
     el 2,5 % el suelo daba por buenas referencias que, pagadas por
     Klarna, dejaban 49 y pico: el auditor cazó 192 en el filo. Solo mueve
     el suelo: la tarifa no cambia, y únicamente suben las referencias que
     estaban en el borde. */
  var PACKING_ENVIO = 9;                   // con IVA, como siempre
  var GARANTIA = 4;                        // fondo de garantía por reloj
  var COMISION = 0.05;                     // el 5 % entero: el suelo protege al que paga por Klarna

  /* LOS DOS GASTOS QUE FALTABAN (Óscar, 31/08/2026). Su regla es que
     «con todos los gastos posibles, absolutamente todos», tienen que
     quedarle 50 € y el 15 %. Y había dos fuera de la cuenta:

     · EL ENVÍO DEL PROVEEDOR. Los 9 € de arriba son el packing y el
       envío AL CLIENTE. Lo que cobra AliExpress por traer las piezas no
       estaba en ningún sitio: hay proveedores que lo dan gratis y otros
       que cobran 4,52 € por pedido, que se reparten entre las piezas de
       ese pedido. 1,00 € por reloj es una estimación prudente hasta que
       haya pedidos de verdad con los que medirlo.
     · LAS DEVOLUCIONES. La casa promete 30 días. Un reloj que vuelve se
       lleva el envío de ida, el de vuelta y el tiempo en que no se
       vende. Va como porcentaje del PVP, igual que la comisión, porque
       es una merma sobre lo vendido y no un coste de la pieza.

     Los dos son ESTIMACIONES de Óscar, no datos de factura: cuando haya
     pedidos y devoluciones reales se ajustan aquí y todo el catálogo se
     recalcula solo. */
  var ENVIO_PROVEEDOR = 1.00;              // lo que cuesta traer las piezas, por reloj
  var DEVOLUCIONES = 0.10;                // 1,5 % del PVP: la merma de los 30 días

  function costeCompleto(c) {
    return (c + PACKING_ENVIO / (1 + IVA) + GARANTIA + ENVIO_PROVEEDOR) * (1 + SS);
  }
  function redondea(p) {
    var bajo = Math.floor((p - 9.90) / 10) * 10 + 9.90;
    return (p - bajo) <= (bajo + 10 - p) ? bajo : bajo + 10;
  }
  function sube990(p) {
    var bajo = Math.floor((p - 9.90) / 10) * 10 + 9.90;
    return bajo >= p - 1e-9 ? bajo : bajo + 10;
  }
  /* EL SUELO, CON LA COMISIÓN DENTRO (Óscar, 22/08/2026).
     Antes el suelo se calculaba sobre el precio de tarifa y DESPUÉS se
     le sumaba el 2,5 % de Klarna, así que la comisión se comía el
     suelo: el Lunar más barato prometía 50 € limpios y dejaba 46,69.
     Ahora se calcula sobre lo que queda de cada euro DESPUÉS de pagar
     la comisión, y ningún reloj sale a la venta por debajo de 50 €
     limpios o del 15 % de beneficio neto. */
  function sueloPvp(cn) {
    var queda = 1 - IRPF;                  // la SS ya va dentro del coste
    var euro = 1 / (1 + IVA) - COMISION - DEVOLUCIONES;  // lo que llega de cada euro de PVP
    var porEuros = (50 / queda + cn) / euro;
    var margen = euro * queda - 0.15;
    var porciento = margen > 0 ? queda * cn / margen : 0;
    return sube990(Math.max(porEuros, porciento));
  }
  function pvpBase(c) { return redondea(costeCompleto(c) * MULT); }

  /* EL 2,5 % DE KLARNA (Óscar, 19/08/2026, confirmado el 22/08): el PVP
     de tarifa sube un 2,5 % y se vuelve a redondear al 9,90. Después, el
     suelo: si no llega a 50 € limpios o al 15 %, sube de escalón. */
  var KLARNA = 1.025;

  window.laoraPrecio = {
    IVA: IVA, IRPF: IRPF, SS: SS, MULT: MULT,
    PACKING_ENVIO: PACKING_ENVIO, GARANTIA: GARANTIA, COMISION: COMISION,
    ENVIO_PROVEEDOR: ENVIO_PROVEEDOR, DEVOLUCIONES: DEVOLUCIONES,
    KLARNA: KLARNA,
    costeCompleto: costeCompleto, redondea: redondea, sube990: sube990,
    sueloPvp: sueloPvp, pvpBase: pvpBase
  };
})();
