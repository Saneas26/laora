# 🚀 PROMPT PARA EL SIGUIENTE — laOra

**Copia todo lo que hay entre las dos líneas y pégaselo al empezar.**

---

Trabajas en **laOra**, la marca de relojes de Óscar Belloso (Grupo Saneas).
Web en producción: **https://laora.es**

## Antes de tocar nada

Lee `/Users/oscar/Sites/laora/TRASPASO_v3.md`. Está completo: rutas,
generador, estructura, estilo, el modelo de ficha y quince trampas que ya
han roto algo alguna vez. **Con leerlo una vez basta.**

Presta atención especial al apartado 6. No son consejos: son cosas que ya
salieron mal.

## Qué es laOra

Relojes **homenaje** a los grandes iconos de la relojería. La distinción es
todo el negocio y no se difumina nunca:

> Un homenaje toma una arquitectura conocida como punto de partida. Una
> falsificación intenta hacerse pasar por otra marca.

Se nombra el original con todas sus letras, se cuenta su historia, y **jamás**
se pone en la esfera un nombre ajeno. El aviso legal del pie va en las 13
páginas, y las secciones que nombran una marca llevan **además el suyo
propio**.

## Cómo se trabaja aquí

**Las páginas `.html` no se editan a mano.** Son salida de un generador:

```bash
cd /Users/oscar/Sites/laora
python3 herramientas/generar.py
```

| Quiero cambiar… | Voy a… |
|---|---|
| un dato de un reloj | `assets/datos/catalogo.json` |
| un texto de sección | `herramientas/generar.py` |
| el aspecto | `assets/css/laora.css` **y subo `V_CSS`** |
| las cifras del mapa del precio | `assets/js/home.js` |

**No hay Node en este Mac.** Python 3 y nada más. El servidor de pruebas se
arranca con la herramienta de previsualización, nombre `laora`, nunca desde
una terminal.

## Las seis reglas que no se saltan

1. **Sube `V_CSS`** en `generar.py` con cada cambio de CSS. Si no, Cloudflare
   sirve la hoja vieja hasta cuatro horas y te vuelves loco.
2. **Nada inventado.** Ni precios, ni movimientos, ni fechas, ni
   estanqueidades. Si no está confirmado, `null`, y esa línea no se pinta.
   Nunca un «por confirmar» a la vista del cliente.
3. **Nada interno de la hoja de materiales llega al HTML.** Ahí hay enlaces
   de compra, coste por pieza, márgenes y beneficio.
4. **Traduce la jerga de proveedor.** La hoja dice «caja tipo Speedmaster»,
   «esfera tipo Nomos». Eso en la web contradice el aviso legal del pie.
5. **Cada reloj se decide solo.** Nada de plantillas: «movimiento suizo» es
   cierto en el Bauhaus y falso en el Lunar.
6. **El logotipo está blindado** y solo se le cambia el color y el cuerpo.
   Si lo deformas, míralo en el apartado 4 del traspaso.

## Verifica siempre

Mide en el navegador, no supongas. Y en producción comprueba con **tres
lecturas seguidas consistentes**: el borde de Cloudflare tarda y no es
uniforme.

Al terminar algo: **commit y push, sin esperar a que lo pidan.**

## Por dónde vas a seguir

**Crear las fichas de los cinco modelos que faltan**, con el modelo del
apartado 5 del traspaso: configurador + dos curiosidades en ventana
emergente + la historia del original como pieza de periódico. Ya están hechos
el **Lunar**, el **Bauhaus** y el **Cero Cero**: míralos antes de empezar.

**Ninguno de los cinco tiene datos** en la hoja: Precisa, Trinchera,
Bitácora, Tortuga y Cóctel no tienen ni una fila en «Catalogo final». Hay
que pedirle a Óscar que los vuelque antes de empezar.

Para leer la hoja entera **no vale la lectura normal**: se corta a la mitad
y te deja sin ver las filas del final, que es justo donde hay bloques
sueltos. Descárgala como `.xlsx` y ábrela con `zipfile` desde Python.
El Cero Cero tenía ocho filas escondidas ahí abajo.

## Cómo tratar con Óscar

- Va rápido y por mensajes cortos. Ejecuta, no le pidas permiso para lo
  obvio.
- **Pero avísale de lo que encuentres**, aunque no lo haya preguntado: un
  precio que no cuadra, un enlace roto, un dato que se contradice. Eso lo
  valora más que la velocidad.
- Cuando corrija un dato de palabra, **recuérdale si la hoja sigue diciendo
  lo contrario**: es la fuente de la que se vuelca todo.
- Si algo que pide tiene una consecuencia que no ha visto, díselo en dos
  líneas y sigue adelante. La decisión es suya.

---
