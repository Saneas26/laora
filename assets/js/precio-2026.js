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

     LA COMISIÓN DE LA PASARELA se calcula al 2,5 %: Klarna se lleva el
     5 %, pero solo la mitad de las ventas van por Klarna (Óscar, 22/08). */
  var PACKING_ENVIO = 9;                   // con IVA, como siempre
  var GARANTIA = 4;                        // fondo de garantía por reloj
  var COMISION = 0.025;                    // 5 % de Klarna en la mitad de las ventas
  function costeCompleto(c) {
    return (c + PACKING_ENVIO / (1 + IVA) + GARANTIA) * (1 + SS);
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
    var euro = 1 / (1 + IVA) - COMISION;   // lo que llega de cada euro de PVP
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
    KLARNA: KLARNA,
    costeCompleto: costeCompleto, redondea: redondea, sube990: sube990,
    sueloPvp: sueloPvp, pvpBase: pvpBase
  };
})();
