# -*- coding: utf-8 -*-
# Genera las 9 landings de laOra (relojes/lo-0X-*.html) desde el copy v3.
# Se ejecuta UNA vez en local; el repo guarda los HTML estáticos (sin build).
import html, os

DEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'relojes')

WA_SVG = '<svg width="19" height="19" viewBox="0 0 24 24" fill="#0A2E1C" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.78-1.47-1.75-1.64-2.05-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.6-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.01-1.04 2.47s1.06 2.86 1.21 3.06c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.75-.72 2-1.41.25-.69.25-1.28.17-1.41-.07-.13-.27-.2-.57-.35M12.04 21.5h-.01a9.4 9.4 0 0 1-4.8-1.32l-.34-.2-3.57.93.96-3.48-.22-.36a9.38 9.38 0 0 1-1.44-5.01c0-5.18 4.22-9.4 9.42-9.4a9.36 9.36 0 0 1 9.41 9.41c0 5.18-4.22 9.4-9.41 9.4M20.52 3.49A11.82 11.82 0 0 0 12.04 0C5.46 0 .1 5.35.1 11.93c0 2.1.55 4.15 1.6 5.96L0 24l6.26-1.64a11.9 11.9 0 0 0 5.78 1.47h.01c6.58 0 11.93-5.35 11.94-11.93a11.86 11.86 0 0 0-3.47-8.41"/></svg>'

MODELOS = [
dict(
  slug='lo-01-lunar', ref='LO-01', nombre='Lunar', cat='Cronógrafo', desde='190',
  desc='Cronógrafo de homenaje al reloj que fue a la Luna. Mecacuarzo o cuerda manual de rueda de columnas, montado y calibrado en Madrid. Desde 190 €.',
  historia=[
    ('lead', '21 de julio de 1969. Buzz Aldrin baja la escalerilla del módulo lunar y pisa un mundo que no es el nuestro. En su muñeca, por fuera del traje, un cronógrafo. No un ordenador, no un prototipo de la NASA: <b>un reloj mecánico de cuerda que cualquiera podía comprar en una tienda.</b>'),
    ('p', 'Cuatro años antes, la NASA había hecho algo poco romántico pero decisivo: metió los cronógrafos candidatos en una cámara de tortura. Calor extremo, frío extremo, vacío, vibración, golpes que habrían destrozado a casi cualquier máquina. Solo uno salió funcionando, y por eso el Speedmaster de Omega fue certificado como el único reloj apto para las misiones tripuladas. Se ganó el apodo que ya no se le quita: <b>Moonwatch</b>.'),
    ('p', 'Y en 1970, cuando el Apolo 13 sufrió la explosión que estuvo a punto de matar a su tripulación, fue un cronógrafo como este el que midió a mano los <b>14 segundos exactos</b> de encendido de motor que enderezaron la nave y trajeron a tres hombres de vuelta a casa. Un reloj mecánico ayudó a salvar tres vidas a 300.000 kilómetros de la Tierra.'),
  ],
  icono='Porque no es un reloj de lujo que se hizo el interesante: es una herramienta que se ganó su leyenda en el sitio más hostil imaginable. La esfera negra, las subesferas, el bisel taquimétrico: cada detalle nació para leerse de un vistazo con guantes de astronauta. Es, probablemente, el reloj más contado de la historia.',
  tributo=[
    'La historia es de todos. El viaje a la Luna no tiene dueño. Lo único que no te puedes permitir es el logo, y resulta que el logo es la mitad del precio.',
    'El «Lunar» recoge ese lenguaje —la esfera panda, las subesferas, la escala taquimétrica— con materiales de verdad, montado y calibrado en Madrid, y con el desglose de cada pieza a la vista. Tú decides si lo quieres con el pulso preciso del mecacuarzo o con lo que llevaba el original: cuerda manual, el gesto de cada mañana, sin rotor, como los relojes que subieron allí arriba.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cronógrafo mecacuarzo Seiko VK63: la sensación de un cronógrafo de verdad con la fiabilidad del cuarzo. Cristal mineral endurecido de máxima calidad, acero 316L cepillado.', 'Desde ~190 €', False),
    ('T2', 'Meridiano', 'Mismo VK63, ahora con zafiro y brazalete de acero macizo. El equilibrio perfecto.', '~250–330 €', False),
    ('T3', 'Cenit', 'Cronógrafo de cuerda manual Seagull ST1901, de rueda de columnas, revisado y regulado en Madrid en su mejor versión. Le das cuerda tú cada mañana, igual que el que fue a la Luna. Cristal de zafiro tipo «box», acero superior, brazalete premium y estuche. Aquí empieza el alma.', '~400–750 €', True),
  ],
  nota='<b>Nota de honestidad (se cuenta, no se esconde):</b> la disposición y el número de subesferas no es idéntica a la del original en todos los acabados, porque cada calibre tiene la suya. En la ficha técnica de cada acabado te decimos exactamente qué calibre llevas, de dónde viene y qué hace cada subesfera. Preferimos que lo sepas antes de comprarlo y no al abrir la caja.',
  agua=None,
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-02-hora-cero', ref='LO-02', nombre='Hora Cero', cat='Buceador 300 m', desde='190',
  desc='Buceador de 300 m reales con malla milanesa, agujas espada y acentos naranja. Cada unidad pasa prueba de presión en Madrid. Desde 190 €.',
  historia=[
    ('lead', 'Antes de cada operación, alguien dice una hora. Todos ponen su reloj en la misma cifra y, a partir de ese instante, ya nada se cuenta en horas: <b>se cuenta en minutos desde el cero.</b>'),
    ('p', '1995. Después de seis años sin estrenos, el agente más famoso del cine vuelve en GoldenEye con la muñeca renovada. La responsable de vestuario decidió que el emblema de siempre ya no decía lo que tenía que decir, y le puso un buceador de acero con esfera azul, bisel de escala y una válvula de helio en el flanco: el Seamaster Diver 300M de Omega. Desde entonces, ese buceador es <b>el reloj del espía</b>. Lo ha llevado en cada misión durante casi tres décadas, y en su última película apareció en la versión que más se recuerda: esfera oscura, acentos naranja y malla milanesa.'),
  ],
  icono='Porque reúne dos mundos que casi nunca conviven: la herramienta y el traje. Es un instrumento de buceo profesional —300 metros de estanqueidad, bisel para cronometrar el aire que te queda, lume para la oscuridad del fondo— y sin embargo desaparece bajo el puño de una camisa. Esa doble vida, más la malla milanesa y el toque de naranja, lo convirtieron en una de las siluetas más reconocibles del mundo.',
  tributo=[
    'El favorito de mucha gente, y se entiende. El «Hora Cero» recoge lo que lo hace grande: esfera negra con acentos naranja, agujas espada, bisel cerámico y esa malla milanesa que es media personalidad del reloj.',
    'Y recoge también su idea. En este reloj el bisel no es un adorno: es el aro con el que marcas tu minuto cero y ves cuánto llevas. Por eso lo cuidamos donde se nota — clic firme, sin holgura, unidireccional como debe ser.',
    'Lo demás no se ve en la foto y sí en el agua: cada unidad pasa la prueba de presión en Madrid antes de salir. Y en la malla no aceptamos el cierre magnético barato: va con cierre desplegable de calidad. Un detalle así es donde se nota si alguien te ha respetado o te ha ahorrado.',
  ],
  acabados=[
    ('T1', 'Alba', 'Mecacuarzo Seiko VH31 de segundero de barrido suave. Cristal mineral endurecido de máxima calidad, acero 316L.', 'Desde ~190 €', False),
    ('T2', 'Meridiano', 'Seiko NH35, zafiro con AR, malla milanesa maciza. El corazón mecánico bajo el agua.', '~280–380 €', True),
    ('T3', 'Cenit', 'Automático superior con zafiro abombado y bisel cerámico, en titanio o acero 904L, malla milanesa mecanizada y correa de caucho. El buceador definitivo.', '~400–750 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>300 m (30 bar)</b>. Cada unidad pasa prueba de presión en seco en Madrid antes de salir. No está certificado bajo la norma ISO 6425, así que no lo llamamos reloj de buceo profesional.',
        'Y ahora en cristiano: <b>dúchate con él, nádate un kilómetro, bucea a pulmón, métete en el mar sin pensarlo.</b> Si buceas con botella, ese es un mundo con su propia norma y sus propios relojes: este no la tiene. Preferimos decírtelo aquí que dejarte descubrirlo a doce metros.'),
  proceso='Montaje, calibración y control de hermeticidad, uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-03-bauhaus', ref='LO-03', nombre='Bauhaus', cat='Reloj de vestir', desde='170',
  desc='Reloj de vestir de líneas esenciales: esfera blanca, agujas azuladas, segundero pequeño a las seis. Cuarzo o cuerda manual. Desde 170 €.',
  historia=[
    ('lead', '1919, Alemania. Una escuela de diseño llamada Bauhaus lanza una idea que cambiará el siglo: <b>la forma sigue a la función.</b> Nada sobra, nada se pone por adorno; la belleza nace de la utilidad.'),
    ('p', 'Décadas después, en el pequeño pueblo relojero de Glashütte, esa filosofía se convirtió en reloj: el Tangente de Nomos, una esfera blanca y limpia, números finos, agujas azuladas como acero templado, y un pequeño segundero girando discreto a las seis.'),
  ],
  icono='Porque demuestra que quitar es más difícil que poner. En un mundo de relojes que gritan, este susurra. Es la elegancia de lo esencial: el reloj que un arquitecto, un diseñador o cualquiera con buen gusto reconoce al instante. No busca impresionar; busca durar en el gusto.',
  tributo=[
    'Respetar este diseño obliga a ser fiel donde importa: el perfil finísimo y el segundero pequeño a las seis son su alma, así que elegimos el movimiento a su medida, no al revés. Esfera blanca, agujas azul aciano, correa color arena.',
    'En cuarzo con segundero pequeño, o en el gesto más puro de todos: cuerda manual, el que le das tú cada mañana, sin rotor, como los relojes de siempre.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cuarzo de segundero pequeño (respeta el diseño original), cristal mineral endurecido de máxima calidad o zafiro, piel color arena.', 'Desde ~170 €', False),
    ('T2', 'Meridiano', 'Calibre Seagull ST17 de cuerda con segundero pequeño: el ritual de darle cuerda cada día. Zafiro fino, piel premium.', '~260–360 €', True),
    ('T3', 'Cenit', 'Acabado superior, zafiro abombado y fondo de cristal para ver la maquinaria, acero de alto pulido o 904L.', '~360–480 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>30 m (3 bar)</b>.',
        'En cristiano: <b>aguanta la lluvia y que te laves las manos.</b> No te duches con él ni te lo lleves a la piscina. Es un reloj de vestir y trabaja en seco.'),
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-04-precisa', ref='LO-04', nombre='Precisa', cat='Deportivo de brazalete integrado', desde='190',
  desc='Deportivo de brazalete integrado en azul marino con esfera de relieve. Cuarzo o automático, eslabones macizos. Desde 190 €.',
  historia=[
    ('lead', 'Años 70. Una idea revolucionaria recorre la relojería: <b>fundir el reloj y su brazalete en una sola pieza continua</b>, sin asas, sin costuras, como si el metal fluyera de la caja al brazo. Nace el reloj deportivo de brazalete integrado.'),
    ('p', 'En 1978 esta receta se democratiza en un reloj de caja plana y facetada cuyo nombre lo dice todo: el PRX de Tissot. Preciso, Robusto y X, el número diez en romano, por sus diez atmósferas de estanqueidad.'),
  ],
  icono='Porque llevó una idea de lujo al alcance de la gente. El brazalete integrado era territorio de relojes carísimos; este lo puso en la muñeca de cualquiera con un diseño que, cuatro décadas después, volvió y arrasó. Es versátil como pocos: sirve para la oficina, para una cena y para el fin de semana sin cambiar de correa, porque no hay correa que cambiar.',
  tributo=[
    'El «Precisa» va en azul marino con la esfera de relieve de cuadraditos, ese detalle textil que atrapa la luz.',
    'En un integrado, la calidad se juega en un sitio muy concreto: el ajuste del brazalete a la caja y el pulido de los eslabones. Ahí no ahorramos. Cuarzo o automático, siempre con eslabones macizos y el brazalete cayendo como debe caer el buen acero.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cuarzo suizo, cristal mineral endurecido de máxima calidad o zafiro, brazalete integrado macizo.', 'Desde ~190 €', False),
    ('T2', 'Meridiano', 'Seiko NH35, zafiro con AR, brazalete integrado macizo.', '~280–380 €', True),
    ('T3', 'Cenit', 'Aquí entra el PT5000, el primo del legendario calibre suizo ETA 2824. Cuando la patente de aquel movimiento expiró, su arquitectura pasó a ser patrimonio de la relojería: hoy el PT5000 se fabrica con fidelidad milimétrica —mismas medidas, piezas intercambiables, mismos estándares— y lo revisa y regula cualquier relojero del mundo. Pagas la ingeniería suiza, no la etiqueta suiza. Con zafiro abombado y acero de alto pulido o titanio.', '~400–560 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>100 m (10 bar)</b>.',
        'En cristiano: <b>dúchate con él, nada, métete en la piscina.</b> No es un reloj de buceo y no lo llamamos así.'),
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-05-trinchera', ref='LO-05', nombre='Trinchera', cat='Reloj militar de campo', desde='150',
  desc='Reloj militar de campo: esfera negra mate, doble escala horaria, lume potente y cordura verde. El automático para empezar. Desde 150 €.',
  historia=[
    ('lead', 'Antes del smartphone, antes del GPS, un soldado en el frente tenía una sola herramienta para coordinar un ataque al segundo: <b>el reloj de su muñeca.</b>'),
    ('p', 'Los trench watches de las guerras mundiales pusieron por primera vez el reloj en la muñeca de millones de hombres —hasta entonces era cosa de bolsillo— y definieron una estética que nunca ha pasado de moda: esfera negra mate, números grandes y limpios, lume para la noche, y una legibilidad tan brutal que se entiende en una décima de segundo bajo presión. El Khaki Field de Hamilton es su heredero más conocido.'),
  ],
  icono='Porque es honestidad hecha reloj. Sin adornos, sin subesferas que no sirven, sin lujo. Solo lo necesario para leer la hora en cualquier condición. El reloj de campo es el «vaqueros y camiseta blanca» de la relojería: nunca falla, siempre queda bien, no le debe nada a nadie.',
  tributo=[
    'El «Trinchera» es el más puro de la colección, y a propósito. Esfera negra militar con su doble escala de 12 y 24 horas, lume potente, correa de cordura verde militar. El automático NH35 dentro y el zafiro delante.',
    'Es el reloj para empezar en el mundo del automático sin gastar de más y sin renunciar a nada.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cuarzo suizo/japonés, cristal mineral endurecido de máxima calidad, cordura verde o NATO.', 'Desde ~150 €', False),
    ('T2', 'Meridiano', 'Seiko NH35, zafiro con AR, cordura o piel premium.', '~230–320 €', True),
    ('T3', 'Cenit', 'NH35 o Miyota 9015, zafiro abombado, acero de alto pulido (opción bronce o titanio), piel + brazalete.', '~330–450 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>100 m (10 bar)</b>.',
        'En cristiano: <b>lluvia, barro, sudor, ducha y piscina sin pensarlo.</b> Con la correa de tela, sécala después: el reloj aguanta más que ella.'),
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-06-ocho-lados', ref='LO-06', nombre='Ocho Lados', cat='Lujo deportivo de acero', desde='250',
  desc='Lujo deportivo de acero: bisel octogonal con tornillos a la vista y esfera verde ahumada de relieve. Desde 250 €.',
  historia=[
    ('lead', '1972. La relojería suiza estaba en crisis y una manufactura se jugó el todo por el todo. Audemars Piguet le encargó a un joven diseñador, Gérald Genta, algo que nunca se había hecho, y se lo pidió la víspera de la feria de Basilea. Genta lo dibujó en una sola noche: <b>un reloj de acero con un bisel octogonal sujeto por ocho tornillos a la vista</b>, inspirado en la escafandra de los antiguos buzos de alta mar.'),
    ('p', 'Lo llamaron Royal Oak, por los barcos de la Marina británica que a su vez debían su nombre al roble donde un rey de Inglaterra se escondió de sus enemigos.'),
    ('p', 'Lo escandaloso fue el precio: un reloj de acero que costaba más que uno de oro de la competencia. Nadie lo entendió. Y se convirtió en el reloj que inventó una categoría entera: <b>el lujo deportivo de acero.</b>'),
  ],
  icono='Porque rompió la regla de que el valor está en el material. Cobró por diseño, por audacia, por identidad. Ese bisel octogonal con tornillos y la esfera de relieve tapisserie son hoy tan reconocibles que no necesitan firma. Cambió para siempre lo que un reloj de acero podía significar.',
  tributo=[
    'Ocho lados. Ocho tornillos. Y una hora que todo el mundo reconoce.',
    'El «Ocho Lados» va en verde ahumado con relieve tapisserie, el color que convirtió a este diseño en objeto de deseo de la última década.',
    'En un integrado de este nivel, el brazalete y su acabado lo son todo: por eso lo tratamos como la pieza más exigente de la colección. Automático fino dentro, para respetar el perfil.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cuarzo suizo, cristal mineral endurecido de máxima calidad o zafiro, brazalete integrado macizo.', 'Desde ~250 €', False),
    ('T2', 'Meridiano', 'Seiko NH35, zafiro con AR, brazalete integrado macizo.', '~350–480 €', True),
    ('T3', 'Cenit', 'Miyota 9015 (fino y suave), zafiro abombado, acero de alto pulido o titanio, brazalete integrado mecanizado.', '~500–700 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>50 m (5 bar)</b>.',
        'En cristiano: <b>lluvia, manos, un chapuzón corto.</b> No lo lleves a la piscina todos los días ni al mar. Es un reloj deportivo de vestir, no un buceador.'),
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-07-bitacora', ref='LO-07', nombre='Bitácora', cat='Lujo deportivo de acero', desde='250',
  desc='Lujo deportivo de acero en turquesa con relieve horizontal y brazalete integrado macizo. Desde 250 €.',
  historia=[
    ('lead', 'El mismo diseñador que había revolucionado el sector, Gérald Genta, cuenta la leyenda que dibujó este reloj <b>en cinco minutos, durante una cena</b>, mirando a una mesa de directivos al otro lado del restaurante.'),
    ('p', 'Se inspiró en la portilla de un transatlántico: esa ventana redondeada de los barcos con sus bisagras herméticas a los lados. Patek Philippe lo bautizó Nautilus, como el submarino de Julio Verne en 20.000 leguas de viaje submarino. Corría 1976.'),
  ],
  icono='Porque llevó el lujo más serio del mundo a un reloj que podías mojar. Su forma —el octágono redondeado, las «orejas» laterales como bisagras, la esfera de líneas horizontales— es de las poquísimas siluetas que se reconocen en la oscuridad. Y una versión suya, en un turquesa concreto, se convirtió hace pocos años en el reloj más deseado y más imposible de conseguir del planeta.',
  tributo=[
    'Por eso la «Bitácora» va precisamente en ese turquesa. Es el color que puso a este diseño en boca de todo el mundo, y el que mejor cuenta lo que somos: el mismo deseo, sin la lista de espera imposible ni el peaje del apellido.',
    'Esfera de relieve horizontal, brazalete integrado macizo, automático fino. La portilla de un transatlántico en tu muñeca.',
    'Y el nombre: en un barco, la bitácora es el cuaderno donde se anota la hora de cada cosa que pasa a bordo. El rumbo, el viento, la avería, la calma. Nada existe hasta que alguien apunta a qué hora ocurrió.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cuarzo suizo, cristal mineral endurecido de máxima calidad o zafiro, brazalete integrado macizo.', 'Desde ~250 €', False),
    ('T2', 'Meridiano', 'Seiko NH35, zafiro con AR, brazalete integrado macizo.', '~350–480 €', True),
    ('T3', 'Cenit', 'Miyota 9015 (fino), zafiro abombado, acero de alto pulido o titanio, brazalete integrado mecanizado.', '~500–700 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>50 m (5 bar)</b>.',
        'En cristiano: <b>lluvia, manos, un chapuzón corto.</b> No es un reloj para nadar a diario ni para el mar.'),
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-08-tortuga', ref='LO-08', nombre='Tortuga', cat='Buceador 200 m', desde='180',
  desc='Buceador de 200 m reales con caja cojín y corona a las cuatro. Cada unidad pasa prueba de presión en Madrid. Desde 180 €.',
  historia=[
    ('lead', '1976. Mientras Suiza discutía sobre relojes de vestir, Japón fabricaba herramientas. Ese año Seiko sacó un buceador con una caja en forma de cojín, tan característica que el mundo entero acabó llamándolo por su apodo: <b>Turtle, la tortuga.</b> No era caro. No pretendía ser elegante. Era casi indestructible.'),
    ('p', 'Y por eso se lo llevaron quienes de verdad se jugaban la vida: buceadores, militares, gente que necesitaba que un reloj funcionara cuando todo lo demás fallaba. Su hermano mayor había aparecido en la muñeca de un capitán en plena selva, en una de las grandes películas bélicas del cine. Esta estirpe de relojes se ganó su fama en el barro y en el agua, no en una vitrina.'),
  ],
  icono='Porque democratizó la fiabilidad. Demostró que un reloj no necesita un apellido suizo para aguantar 200 metros bajo el agua, resistir golpes y seguir marcando la hora treinta años después. La caja cojín, la corona a las cuatro, el bisel de buceo: puro diseño funcional que se volvió bello sin proponérselo.',
  tributo=[
    'El «Tortuga» es nuestra declaración de principios. Es el reloj con el que estrenamos el control de estanqueidad, porque aquí no hay lugar para el marketing: o aguanta la prueba, o no sale.',
    'Caja cojín en 316L, esfera negra clásica, bisel de buceo, zafiro (una mejora sobre el cristal mineral del original) y el fiable automático japonés dentro. Un reloj para el mar, para el trabajo y para toda la vida.',
  ],
  acabados=[
    ('T1', 'Alba', 'Mecacuarzo de barrido o cuarzo suizo, cristal mineral endurecido de máxima calidad, caucho o NATO.', 'Desde ~180 €', False),
    ('T2', 'Meridiano', 'Seiko NH35/NH36 día-fecha, zafiro, brazalete macizo + caucho.', '~260–350 €', True),
    ('T3', 'Cenit', 'NH36 día-fecha con zafiro abombado y bisel cerámico, en titanio o acero 904L, brazalete mecanizado premium.', '~360–650 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>200 m (20 bar)</b>. Cada unidad pasa prueba de presión en seco en Madrid antes de salir. No está certificado bajo la norma ISO 6425, así que no lo llamamos reloj de buceo profesional.',
        'Y ahora en cristiano: <b>dúchate con él, nada, bucea a pulmón, métete en el mar sin pensarlo dos veces.</b> Si buceas con botella, ese es un mundo con su propia norma y sus propios relojes: este no la tiene. Preferimos decírtelo aquí que dejarte descubrirlo a doce metros.'),
  proceso='Montaje, calibración y control de hermeticidad, uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
dict(
  slug='lo-09-coctel', ref='LO-09', nombre='Cóctel', cat='Reloj de vestir', desde='180',
  desc='Reloj de vestir con esfera sunburst marrón, caja en oro rosa y cristal muy abombado. Desde 180 €.',
  historia=[
    ('lead', 'En el barrio de Ginza, en Tokio, hay un bar donde preparar un combinado es una ceremonia. Su barman, uno de los mejores del mundo, hace de cada copa un pequeño ritual de hospitalidad —lo que en Japón llaman <b>omotenashi</b>, atender al otro sin esperar nada a cambio—.'),
    ('p', 'De esa cultura nació el Presage Cocktail Time de Seiko, un reloj cuyas esferas imitan el color de un cóctel: un degradado que se enciende con la luz, cubierto por un cristal muy abombado que hace de copa, para que la mirada resbale como el licor por el cristal.'),
  ],
  icono='Porque convirtió un reloj de vestir asequible en una pequeña obra de artesanía. Esa esfera sunburst que cambia de tono según cómo le da la luz, ese cristal en forma de cúpula: detalles que normalmente solo verías muy por encima de su precio. Es la prueba de que la elegancia no es cara, es cuidada.',
  tributo=[
    'El «Cóctel» va en marrón —el tono dulce de la carta— con caja en oro rosa y ese cristal abombado que es media magia del reloj.',
    'Es nuestro reloj de vestir: el que te pones cuando la ocasión importa. Automático dentro, sunburst delante, y el domo alto que hace bailar la luz sobre la esfera.',
  ],
  acabados=[
    ('T1', 'Alba', 'Cuarzo suizo/japonés, cristal mineral endurecido abombado de máxima calidad, caja PVD oro rosa, piel marrón.', 'Desde ~180 €', False),
    ('T2', 'Meridiano', 'Seiko NH35, zafiro abombado con AR, PVD oro rosa, piel premium o brazalete.', '~270–370 €', True),
    ('T3', 'Cenit', 'NH35 o Miyota 9015, zafiro de domo alto, acabado superior, brazalete + piel.', '~380–500 €', False),
  ],
  nota=None,
  agua=('Estanqueidad: <b>30 m (3 bar)</b>.',
        'En cristiano: <b>lluvia y lavarte las manos.</b> Ni ducha ni piscina. Y si lleva PVD oro rosa, trátalo como lo que es: un acabado precioso que agradece que no lo restriegues.'),
  proceso='Montaje, calibración y control uno a uno. 3 años de garantía legal en España, con servicio técnico propio. Fabricamos en series pequeñas: pide el aviso y te escribimos cuando tu modelo esté disponible.',
),
]

NAV = '''<nav class="nav" id="nav">
  <div class="container nav-inner">
    <a class="brand" href="/">la<span class="o"></span>ra<sup>®</sup></a>
    <div class="nav-links">
      <a href="/#coleccion">La colección</a>
      <a href="/#porque">Por qué laOra</a>
      <a href="/materiales.html">Materiales</a>
      <a href="/manifiesto.html">El alma de un automático</a>
      <a href="/#madrid">El proceso de Madrid</a>
    </div>
    <a class="wa-mini" href="https://api.whatsapp.com/send?phone=34689806987">{wa} WhatsApp</a>
  </div>
</nav>'''

FOOTER = '''<footer>
  <div class="brand"><span style="color:var(--tinta)">la</span><span class="o"></span><span style="color:var(--tinta)">ra</span><sup>®</sup></div>
  <div class="footer-links">
    <a href="https://api.whatsapp.com/send?phone=34689806987">WhatsApp</a>
    <a href="/materiales.html">Materiales</a>
    <a href="/manifiesto.html">El alma de un automático</a>
    <a href="/privacidad.html">Privacidad</a>
  </div>
  <div class="fg-title">Grupo <span class="saneas">Saneas</span></div>
  <div class="gp-grid">
    <a class="gp-item" href="https://saneas.es" target="_blank" rel="noopener">
      <img src="/assets/img/app-saneas.png" alt="APP Saneas" loading="lazy"><b>APP Saneas</b>
    </a>
    <a class="gp-item" href="https://saneas.es/asesorias" target="_blank" rel="noopener">
      <span class="gp-ico"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span><b>Asesorías</b>
    </a>
    <a class="gp-item" href="https://pordondevoy-saneas.vercel.app" target="_blank" rel="noopener">
      <img src="/assets/img/app-pordondevoy.png" alt="APP Pordondevoy" loading="lazy"><b>Pordondevoy</b>
    </a>
    <a class="gp-item" href="https://activala.es" target="_blank" rel="noopener">
      <img src="/assets/img/app-activala.png" alt="Activala" loading="lazy"><b>Activala</b>
    </a>
    <a class="gp-item" href="https://acumula.es" target="_blank" rel="noopener">
      <img src="/assets/img/app-acumula.png?v=2" alt="APP Acumula" loading="lazy"><b>Acumula</b>
    </a>
  </div>
  <p class="copy">© 2026 laOra® · Reloj · Calidad · Precio honesto · Todos los derechos reservados</p>
</footer>'''

def acabado_html(a):
    tier, nombre, texto, precio, senal = a
    clase = 'acabado senal' if senal else 'acabado'
    sello = ' <small>· el favorito del taller</small>' if senal else ''
    return f'''      <div class="{clase} reveal">
        <div class="tier"><b>{tier}</b><h3>«{nombre}»</h3></div>
        <p>{texto}</p>
        <p class="precio">{precio}{sello}</p>
      </div>'''


# ---------------------------------------------------------------------------
# FICHAS TÉCNICAS por acabado. Clave: (ref, tier). Se pintan bajo el selector.
# Solo se rellenan a medida que Producto las cierra; si no hay ficha, no se pinta.
# ---------------------------------------------------------------------------
FICHAS = {
 ('LO-07','T1'): [
   ('Movimiento','Cuarzo suizo Ronda 715 (11½\'\'\'), 5 rubíes, versión Swiss Made. Tres agujas y fecha, parada de segundero, autonomía de pila de 60 meses.'),
   ('Cristal','Mineral endurecido K1 de máxima calidad (~600 HV) con antirreflejos interior. Menos duro que el zafiro y por tanto más fácil de rayar, pero más tenaz frente a los golpes: es el cristal que aguanta el impacto que astillaría un zafiro.'),
   ('Caja','Acero inoxidable 316L, Ø 40 mm, octágono redondeado con orejas laterales. Cepillado y pulido a mano en las transiciones.'),
   ('Brazalete','Integrado, eslabones y terminales macizos. Cierre desplegable mecanizado con seguridad. Eslabones desmontables para ajuste.'),
   ('Esfera','Turquesa con relieve de líneas horizontales, índices aplicados con lume Super-LumiNova, fecha a las 3.'),
   ('Medidas','Ø 40 mm · grosor aprox. 11,5 mm · asa a asa integrada (~46 mm) · brazalete de 22 mm en la caja.'),
   ('Estanqueidad','50 m (5 bar), verificada unidad a unidad en Madrid con prueba de presión en seco.'),
   ('Garantía','3 años de garantía legal en España — la que manda la ley, no una promesa nuestra — con servicio técnico propio en Madrid. Y guardamos repuestos 10 años.'),
 ],
 ('LO-07','T2'): [
   ('Movimiento','Automático Seiko NH35A (Time Module), 24 rubíes, 21.600 alt/h, ~41 h de reserva de marcha, parada de segundero y cuerda manual. Variante Type L, la que respeta el grosor de nuestra esfera.'),
   ('Cristal','Zafiro con antirreflejos interior. Dureza 9 en la escala de Mohs: en el día a día, prácticamente imposible de rayar.'),
   ('Caja','Acero inoxidable 316L verificado por ensayo, Ø 40 mm, octágono redondeado. Cepillado y pulido de alto contraste.'),
   ('Brazalete','Integrado, eslabones y terminales macizos. Cierre desplegable mecanizado con seguridad y microajuste.'),
   ('Esfera','Turquesa con relieve de líneas horizontales, índices aplicados con lume Super-LumiNova, fecha a las 3.'),
   ('Medidas','Ø 40 mm · grosor aprox. 11,5 mm · asa a asa integrada (~46 mm) · brazalete de 22 mm en la caja.'),
   ('Estanqueidad','50 m (5 bar), verificada unidad a unidad en Madrid con prueba de presión en seco.'),
   ('Garantía','3 años de garantía legal en España — la que manda la ley, no una promesa nuestra — con servicio técnico propio en Madrid. Y guardamos repuestos 10 años.'),
 ],
 ('LO-07','T3'): [
   ('Movimiento','Automático Miyota 9015 (Citizen), 24 rubíes, 28.800 alt/h, ~42 h de reserva. De alta frecuencia y perfil fino: el segundero barre con más suavidad y el reloj se mantiene delgado.'),
   ('Cristal','Zafiro abombado con antirreflejos por las dos caras. El cristal desaparece y solo queda la esfera; a cambio, la cara exterior pide más cuidado.'),
   ('Caja','Acero 316L de alto pulido o titanio grado 2 (ligero e hipoalergénico), Ø 40 mm.'),
   ('Brazalete','Integrado mecanizado, eslabones y terminales macizos, cierre desplegable con microajuste, en el mismo material que la caja.'),
   ('Esfera','Turquesa con relieve de líneas horizontales, índices aplicados con lume Super-LumiNova, fecha a las 3.'),
   ('Medidas','Ø 40 mm · grosor aprox. 11,5 mm · asa a asa integrada (~46 mm) · brazalete de 22 mm en la caja.'),
   ('Estanqueidad','50 m (5 bar), verificada unidad a unidad en Madrid con prueba de presión en seco.'),
   ('Garantía','3 años de garantía legal en España — la que manda la ley, no una promesa nuestra — con servicio técnico propio en Madrid. Y guardamos repuestos 10 años.'),
 ],
 ('LO-07','T4'): [
   ('Acabado','Revestimiento DLC negro (carbono tipo diamante) en caja, bisel, brazalete y cierre. No es pintura ni un baño: es una capa de carbono que roza la dureza del diamante — no se raya, no se descascarilla, no envejece mal.'),
   ('Esfera y agujas','Esfera negra, agujas plateadas y segundero amarillo: el único punto de color, el filo de luz que asoma cuando la luna tapa el sol.'),
   ('Base','Se monta sobre el Meridiano o sobre el Cenit: eliges el corazón y el Eclipse le pone el traje.'),
   ('Cristal','El del acabado elegido: zafiro con AR interior en Meridiano, zafiro abombado con AR doble en Cenit.'),
   ('Medidas','Ø 40 mm · grosor aprox. 11,5 mm · asa a asa integrada (~46 mm) · brazalete de 22 mm en la caja.'),
   ('Estanqueidad','50 m (5 bar), verificada unidad a unidad en Madrid con prueba de presión en seco.'),
   ('Garantía','3 años de garantía legal en España — la que manda la ley, no una promesa nuestra — con servicio técnico propio en Madrid. Y guardamos repuestos 10 años.'),
 ],
}

ECLIPSE = {'LO-01','LO-02','LO-04','LO-06','LO-07','LO-08'}

def pagina(m):
    num = m['ref'].split('-')[1]
    art = 'la' if m['ref'] == 'LO-07' else 'el'
    gama = 'Alba · Meridiano · Cenit' + (' · Eclipse' if m['ref'] in ECLIPSE else '')
    import json
    datos = [{'tier': a[0], 'nombre': a[1], 'texto': a[2], 'precio': a[3],
              'ficha': FICHAS.get((m['ref'], a[0]), [])} for a in m['acabados']]
    inicial = next((i for i, a in enumerate(m['acabados']) if a[4]), 0)
    if m['ref'] in ECLIPSE:
        nota_diver = ' En los buceadores puede pedirse también la horaria en amarillo, para un look más marcado.' if m['ref'] in {'LO-02', 'LO-08'} else ''
        datos.append({'tier': 'T4', 'nombre': 'Eclipse',
            'texto': 'Negro sobre negro sobre negro: caja, bisel, esfera y brazalete en DLC, un revestimiento de carbono que roza la dureza del diamante — no se raya, no se descascarilla, no envejece mal. Un único destello: el segundero en amarillo, girando como el filo de luz que asoma cuando la luna tapa el sol. Disponible sobre los acabados medios y altos.' + nota_diver,
            'precio': 'Prima de +50–100 € sobre el acabado elegido (a confirmar)', 'eclipse': True,
            'ficha': FICHAS.get((m['ref'], 'T4'), [])})
    datos_js = ('window.LAORA_ACABADOS = ' + json.dumps(datos, ensure_ascii=False) +
                ';\nwindow.LAORA_ACABADO_INICIAL = ' + str(inicial) + ';')
    historia = '\n'.join(
        f'      <p class="{"lead" if t=="lead" else ""}">{txt}</p>' for t, txt in m['historia'])
    tributo = '\n'.join(f'      <p>{p}</p>' for p in m['tributo'])
    acabados = '\n'.join(acabado_html(a) for a in m['acabados'])
    nota = f'''    <div class="nota reveal">{m['nota']}</div>\n''' if m['nota'] else ''
    if m['agua']:
        titulo_agua = 'Ficha técnica — Estanqueidad' if 'presión' in m['agua'][0] else 'Ficha técnica — Agua'
        agua = f'''
<!-- FICHA TÉCNICA · AGUA -->
<section class="block gris">
  <div class="container">
    <div class="block-head reveal">
      <span class="eyebrow">{titulo_agua}</span>
      <h2>Lo que puedes hacer con él. Y lo que no.</h2>
    </div>
    <div class="agua reveal">
      <div class="dato">{m['agua'][0]}</div>
      <div class="llano">{m['agua'][1]}</div>
    </div>
  </div>
</section>
'''
    else:
        agua = ''
    proceso_fondo = '' if m['agua'] else ' gris'
    html_pagina = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{m['desc']}">
<meta property="og:title" content="{m['ref']} «{m['nombre']}» — {m['cat']} laOra">
<meta property="og:description" content="{m['desc']}">
<meta property="og:url" content="https://laora.es/relojes/{m['slug']}.html">
<meta property="og:image" content="https://laora.es/assets/img/relojes/lo-{num}.jpg">
<title>{m['ref']} «{m['nombre']}» — {m['cat']} laOra · desde {m['desde']} €</title>
<link rel="icon" type="image/png" href="/assets/img/app-laora.png?v=2">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/manifest.json">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700;800&family=Quicksand:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/laora.css?v=14">
</head>
<body>

{NAV.format(wa=WA_SVG)}

<!-- HÉROE -->
<header class="hero">
  <div class="container hero-grid">
    <div class="stage reveal">
      <span class="stage-badge"><span class="laora">laOra</span> · {m['ref']}</span>
      <img src="/assets/img/relojes/lo-{num}.jpg" alt="Reloj laOra {m['nombre']}, {m['cat'].lower()}" onerror="this.remove()">
    </div>
    <div>
      <span class="eyebrow">{m['ref']} · {m['cat']}</span>
      <h1>«{m['nombre']}»</h1>
      <p class="hero-sub" style="margin-top:14px">{m['cat']} · desde <b>{m['desde']} €</b></p>
      <div class="hero-cta">
        <a href="/?modelo={m['ref']}#interesados" class="btn btn-carbon">Avísame del estreno</a>
        <a class="btn btn-wa" href="https://api.whatsapp.com/send?phone=34689806987">{WA_SVG} WhatsApp</a>
      </div>
      <div class="hero-mini">
        <div><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#B8843F" stroke-width="2.2"><path d="M20 6 9 17l-5-5"/></svg> {gama}</div>
        <div><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#B8843F" stroke-width="2.2"><path d="M20 6 9 17l-5-5"/></svg> Montado y controlado en Madrid</div>
        <div><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#B8843F" stroke-width="2.2"><path d="M20 6 9 17l-5-5"/></svg> Garantía de 3 años</div>
      </div>
    </div>
  </div>
</header>

<!-- LA HISTORIA -->
<section class="block dark-sec">
  <div class="container">
    <div class="block-head reveal">
      <span class="eyebrow">La historia</span>
      <h2>La historia que llevas en la muñeca.</h2>
    </div>
    <div class="story reveal">
{historia}
    </div>
  </div>
</section>

<!-- POR QUÉ ES UN ICONO -->
<section class="block">
  <div class="container block-head reveal">
    <span class="eyebrow">Por qué es un icono</span>
    <h2>Un diseño que no necesita firma.</h2>
    <p>{m['icono']}</p>
  </div>
</section>

<!-- NUESTRO TRIBUTO -->
<section class="block gris claro">
  <div class="container">
    <div class="block-head reveal">
      <span class="eyebrow">Nuestro tributo</span>
      <h2>Lo mismo que amas. Sin el peaje.</h2>
    </div>
    <div class="story reveal">
{tributo}
    </div>
  </div>
</section>

<!-- LOS ACABADOS -->
<section class="block" id="acabados">
  <div class="container">
    <div class="block-head reveal">
      <span class="eyebrow">Los acabados</span>
      <h2>Tú eliges hasta dónde quieres llegar.</h2>
      <p>Cada reloj de laOra vive en varios acabados. No cambia el diseño: cambian los materiales y la mecánica. El de entrada nunca es «el barato»: pasa exactamente el mismo control de calidad que el más alto.</p>
    </div>
    <div class="selector-chips reveal" id="selectorChips"></div>
    <div class="panel-acabado reveal" id="panelAcabado"></div>
    <div class="acabados-grid" style="margin-top:34px">
{acabados}
    </div>
{nota}    <div class="nota reveal"><b>El desglose, a la vista:</b> junto a cada acabado publicaremos el desglose de coste por componente —qué añade cada escalón y por qué cuesta más— en la puesta a la venta. La transparencia no es un adorno: es el producto.</div>
  </div>
</section>
{agua}
<!-- EL PROCESO DE MADRID -->
<section class="block{proceso_fondo}" id="madrid">
  <div class="container block-head reveal">
    <span class="eyebrow">El proceso de Madrid</span>
    <h2>Uno a uno. O no sale.</h2>
    <p>{m['proceso']}</p>
    <p style="margin-top:26px">¿Cuarzo, automático o cuerda manual? Léelo aquí: <a href="/manifiesto.html" style="color:var(--dorado);font-weight:700">«El alma de un automático»</a>.</p>
  </div>
</section>

<!-- CTA FINAL -->
<section class="block dark-sec" style="background:radial-gradient(120% 120% at 50% 0%,#1b1e24,#0b0d12)">
  <div class="container block-head reveal">
    <span class="eyebrow">El estreno</span>
    <h2>Que te avisemos cuando salga {art} «{m['nombre']}».</h2>
    <p>Sin pago por adelantado. Te escribimos en cuanto se abra la reserva, por orden de llegada.</p>
    <div class="hero-cta" style="justify-content:center;margin-top:30px">
      <a href="/?modelo={m['ref']}#interesados" class="btn btn-ambar">Avísame del estreno</a>
      <a class="btn btn-claro" href="/#coleccion">Ver los otros ocho</a>
    </div>
  </div>
</section>

{FOOTER}

<script>
{datos_js}
</script>
<script src="/assets/js/laora.js?v=14"></script>
</body>
</html>
'''
    return html_pagina

os.makedirs(DEST, exist_ok=True)
for m in MODELOS:
    ruta = os.path.join(DEST, m['slug'] + '.html')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(pagina(m))
    print('OK', ruta)
print('Total:', len(MODELOS))
