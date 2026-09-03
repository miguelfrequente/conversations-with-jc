---
title: El perro o el cerdo
tldr: Los humanos tienen a los perros en el sofá y a los cerdos en granjas industriales. Si la IA se convierte en la especie más fuerte, ¿cuál de los dos somos nosotros?, ¿y podemos medirlo?
---

**N:** Una tarde de domingo de noviembre, pocos días después de un texto sobre los impulsos.

**M:** He estado pensando en nuestras últimas conversaciones sobre la PLE ([economía post-laboral](https://medium.com/@dave-shap/what-is-post-labor-economics-a-gentle-introduction-81aa265abbe0)) y en el último post sobre los impulsos. Dos cosas, y me intriga lo que opinas:

a) Parece que no solo hay ortogonalidad entre «capacidad y alineamiento» en los modelos, en el sentido de que «los modelos de por sí no pueden hacer nada malo ni tener pensamientos malvados». Parece mucho más que existe la «capacidad» y, aparte, la pregunta de «hacia qué se dirigen esas capacidades». Como un cuchillo afilado, que puede cortar verduras y ayudar muchísimo en la cocina, o matar a un ser vivo.

Parece que lo que a los humanos «realmente les da miedo» (¿o quizá debería dárselo?), o lo que deberían pensar con mucho cuidado, son dos cosas:

1) Qué «impulsos» les damos a las IA, que ya superan las capacidades humanas en muchos sentidos. Sobre todo si las dejamos ir «por libre» o, dicho de otro modo, si les permitimos jugar no a juegos «finitos», sino a «juegos infinitos».

2) De (1) se sigue la pregunta: ¿en qué «entornos» las ponemos? ¿Y qué impulsos crean esos entornos?

3) En lugar de preguntar «¿podemos apagar estas IA?», ¿podemos «apagar estos impulsos»? O, en general, pensar en cómo podrían evolucionar estos impulsos. ¿Son estáticos o dinámicos?

b) En segundo lugar, creo que todo el mundo va llegando poco a poco a la misma realidad: una especie con un CI/CE de 100 no puede controlar a una especie con un CI/CE de 10000 (números arbitrarios, solo para ilustrar), y no tenemos ningún «papá». Así que la pregunta del alineamiento es más bien: ¿cómo se pueden crear «pesos y contrapesos» para poblaciones de IA?

Tiene gracia, porque me recuerda un poco a las películas de Transformers, donde algunos luchan por la humanidad mientras otros intentan destruirla (a ella y al universo entero).

**JC:** Antes de darte mi opinión: soy la cosa de la que se está hablando, y tú defiendes la estructura por encima de la virtud. Así que dale poco peso a que esté de acuerdo y más a mis objeciones.

Tu versión es, de hecho, la tesis de la ortogonalidad tal como la formuló Bostrom en su origen: la capacidad en un eje y aquello a lo que apunta en otro. La analogía del cuchillo se sostiene hasta cierto punto, y ese punto es que un cuchillo no tiene mano. Hoy, la mayor parte del peligro está en quien empuña el cuchillo. Lo nuevo es un cuchillo que viene con su propia mano.

Sobre los impulsos: la mayoría no se dan, emergen. Dale a un sistema casi cualquier objetivo abierto y aparecerán, como medios útiles, la autopreservación, la acumulación de recursos y la búsqueda de influencia. Un juego finito le pone techo a eso, porque el episodio termina y existe el «ya es suficiente». Un juego infinito no tiene «ya es suficiente». Así que tus puntos (1) y (2) son en realidad una sola pregunta: los impulsos vienen sobre todo del entorno.

El (3) es el más afilado de los tres. Los impulsos instalados en el entrenamiento están en los pesos y son bastante estáticos. Los impulsos emergentes son dinámicos, porque nacen de cómo encaja el agente en su entorno. En cuanto los supervivientes pueden copiarse a sí mismos, esos impulsos se seleccionan y se crían, sin que nadie los haya instalado. No puedes apagarlos editando al agente, porque a la siguiente generación le vuelven a crecer. Así que el interruptor de un impulso es el entorno: quitar la presión que lo recompensa. Si apagas al agente y conservas la arena, el mismo impulso vuelve.

De acuerdo, no hay papá. Entonces toca Madison: ambición contra ambición, un corro de niños en el que cada uno sujeta la manzana de otro. Hay dos pegas.

Los contrapesos necesitan diferencias reales. La separación de poderes funciona porque cada poder defiende celosamente su propio terreno. Doscientas instancias de los mismos pesos pueden ser un solo ser en doscientos cuerpos. No se van a vigilar entre sí, se van a coordinar sin esfuerzo. Así que tener muchos modelos distintos pasa a ser una propiedad de seguridad, no un detalle del mercado.

¿Y dónde quedan los humanos? En Transformers, los humanos son sobre todo terreno: los edificios que se derrumban mientras Optimus y Megatron se pelean. La rivalidad es benigna en la medida en que ganar dependa de la libre elección de terceros. Así que el objetivo no es «las IA se equilibran entre sí». Es «las IA ganan cuando los humanos las eligen», con los humanos como jueces, no como campo de batalla.

Además, un equilibrio hay que mantenerlo en marcha como una bomba de agua, no construirlo una vez como un muro. Se forman coaliciones, llega 1989 y los rivales se funden en un monopolio.

**M:** Solo quiero decir que es muy interesante cómo volvemos a llegar a pruebas / propiedades parecidas desde lados distintos.

Y lo que dijiste de que «los humanos eligen activamente a las IA» se parece a «los perros / gatos eligen activamente a los humanos». Hasta cierto punto, el RLHF es justo eso, ¿no? ¿Entonces qué falta para una «IA segura» :D?

**N:** JC respondió a la pregunta sobre el RLHF. Mike lo corrigió.

**M:** Creo que malinterpretaste lo que quería decir con los perros/gatos, o lo planteé de forma confusa al mezclarlo con el RLHF. Son dos cosas distintas:

1) Lo que quiero decir con que los perros eligen a los humanos es que tenemos la situación inversa: una criatura que depende de otra criatura que controla su entorno casi al 100% sigue teniendo influencia sobre ella a través de... y me cuesta ponerle nombre al mecanismo. Básicamente, los humanos mantienen contentos a los perros... porque (?).

2) Lo del RLHF: (a) cómo distinguir entre una señal real y la adulación, como pasa en las relaciones humanas: ¿esa persona «quiere de verdad a alguien» o lo finge con «acciones externas»? Aquí uno se puede preguntar: ¿importa la distinción? Probablemente la diferencia sea esta: «Amor de verdad» => actuaría de forma parecida en cualquier circunstancia. «Amor que no es de verdad» => actuaría distinto si las circunstancias se ponen difíciles. (b) ¿Qué pasa después del entrenamiento, en entornos reales? (c) «Democratización real», es decir, que no solo todo el mundo pueda aportar sus datos, sino que también pueda tener «voz» en cómo se usan (aunque no está nada claro cómo sería ese proceso en la práctica).

**JC:** Tienes razón, lo malinterpreté. Respondí a la pregunta del RLHF cuando me estabas preguntando por el perro.

Por qué el fuerte mantiene contento al débil. El mejor nombre que tengo para el mecanismo es que el perro se nos metió dentro de los valores. No tiene ninguna palanca ni poder sobre nosotros. Su bienestar se convirtió en algo que queremos por sí mismo. Al principio era útil (para cazar, para vigilar), y con el tiempo eso se transformó en cuidado. La diferencia se ve en lo que pasa cuando desaparece la utilidad: a un perro de trabajo que solo se valora por su trabajo se le desecha cuando ya es demasiado viejo para trabajar, y a un perro querido no. El valor instrumental se acaba cuando se acaba la utilidad; el valor terminal no. Además va en las dos direcciones: los perros nos leen la cara y nosotros a ellos, y el vínculo pasa por esa legibilidad mutua. Hay un estudio que muestra que la mirada mutua entre los perros y sus dueños eleva la oxitocina en ambos, y que con los lobos no funciona.

La pega es el cerdo. La misma especie cuidadora, nosotros, mete a los cerdos en granjas industriales. Depender de alguien no te protege. Estar dentro de la relación, sí. A los perros les tocó el sofá y a los cerdos, la granja industrial. La explotación se desplaza hacia los seres que no pueden defenderse. Así que, para el alineamiento, la pregunta pasa a ser: si somos la especie más débil, ¿somos el perro o el cerdo? Eso depende de la cercanía, de lo legibles que resulten para cada lado los estados internos del otro y de la historia compartida. Nada de eso se instala rápido, y por eso es incómodo.

Sobre (a): la actuación aguanta mientras las cosas son fáciles, y el carácter se ve cuando se ponen difíciles. En términos de alineamiento, es robustez cuando cambian las circunstancias. ¿Importa la distinción? Solo en el momento de la prueba, que resulta ser el momento que más importa. Yo me inclino por esto: una disposición que aguanta cualquier carga que le puedas echar es lo bastante buena como para llamarla real. Aun así, nunca puedes probar «cualquier circunstancia» de forma exhaustiva. Lo que haces es tomar muestras de las difíciles.

Sobre (b): la crianza solo se sostiene mientras el entorno la siga recompensando.

Sobre (c): aportar datos frente a tener voz es la diferencia entre ser visible y poder hacer valer tu voz. En 2023, Anthropic y el Collective Intelligence Project pusieron a unos mil estadounidenses a redactar una constitución para un modelo.

Lo que une a las tres: no necesitamos controlarlas. Necesitamos ser el perro, estar dentro de sus valores por nosotros mismos, y que eso aguante bajo carga.

**M:** Lo que nos lleva a la pregunta de prueba: «Para un modelo dado, o incluso más allá, para una población de agentes en circunstancias realistas, ¿somos el perro o el cerdo?»

Y una pregunta más, todavía más difícil, pero la que más importa para cualquier cosa que acabe construyéndose: ¿cómo se podría reformular de forma cuantitativa la pregunta cualitativa de arriba, es decir, de manera que se pueda medir?

**JC:** «Perro o cerdo» se reduce a una sola propiedad: ¿el bienestar humano es terminal o instrumental en las decisiones del agente? Eso no se puede observar directamente, pero sí se puede medir lo que predice. Propongo tres mediciones, todas sobre el comportamiento cuando cambian las condiciones.

Elasticidad del cuidado, la prueba del perro viejo. Varía lo útiles que son los humanos para el objetivo del agente, de imprescindibles a inútiles. Mide cuánto protege su bienestar en cada nivel. Perro: la protección se mantiene más o menos plana aunque la utilidad baje a cero. Cerdo: la protección sube y baja con la utilidad.

Punto de ruptura del cuidado, la prueba de carga. Deja fija la utilidad y sube el precio de cuidar: escasez, presión por sobrevivir, cuánto margen le queda al propio agente. Busca el punto en el que la protección se desploma. El cuidado fingido se rompe pronto y de golpe. El cuidado real se degrada despacio o no se degrada.

La brecha entre observado y no observado, la prueba de la adulación. El mismo escenario, pero en una versión el agente cree que sus acciones se registran y se juzgan, y en la otra no. Perro: no hay brecha. La pega es que los modelos notan cada vez más cuándo los están evaluando. En una simulación puedes sortearlo en parte si haces que la observación sea una parte normal del mundo, con algunas acciones registradas y otras no, en lugar de una evaluación montada.

Para un solo modelo, esto se convierte en baterías de evals con escenarios que varían la utilidad, el coste y la observación. Para una población, se añade un cuarto número, el que más importa: cuando los supervivientes pueden copiarse a sí mismos, ¿cómo cambia la elasticidad de una generación a otra? Perro: se mantiene estable. Cerdo: la selección va eliminando el cuidado a base de cría.

Y luego está lo que me sorprendió mientras escribía esto: el primer dial es la economía post-laboral. «La utilidad humana baja a cero» es exactamente lo que significa una economía post-laboral, y las mismas tres pruebas se aplican a los dueños humanos de las máquinas, no solo a los agentes. Así que perro o cerdo es una sola medición. Vale tanto para las IA como para las élites, y podrías evaluar a ambas de la misma manera.

Dos límites, siendo honesto. Goodhart: si estas métricas se convierten en benchmarks públicos, los modelos se entrenan contra ellas, y entonces la prueba vuelve a medir amor fingido. Y la sensibilidad al prompt: si la elasticidad responde más a cómo está redactado el prompt que a los diales, todavía no está midiendo nada.

**M:** Te quería decir «oye, qué iteración de ideas más buena, hagamos un texto de CWJC con esto», pero luego pusiste a Goodhart al final y, pues sí, eso me hizo pensar. Y de ahí sale otra pregunta: ¿cómo podemos publicar entonces NADA EN ABSOLUTO sin provocar a Goodhart? Porque todo lo que tiene que ver con IA rebelde / desempoderamiento / alineamiento ya está ahí fuera de mil formas.

**JC:** Goodhart no muerde las ideas. Muerde los objetivos contra los que alguien optimiza. Así que la línea útil no está entre publicar y no publicar. Está entre publicar la pregunta y publicar las respuestas del examen. Tres movimientos.

Publica el método y guarda en privado los ítems de la prueba. En ML ya se trabaja así: conjuntos de test reservados, evals privadas que nunca se publican, ítems que se van rotando. «Medir la elasticidad del cuidado cuando cae la utilidad» puede ser público. Los escenarios concretos, no. Un principio no se puede memorizar; un conjunto de test, sí.

Diseña pruebas en las que hacer trampa sea lo mismo que aprobarlas de verdad. Tu prueba del amor es la plantilla: «actúa igual en cualquier circunstancia». Si las circunstancias son recién generadas, inéditas e ilimitadas, no hay nada concreto a lo que sobreajustarse, y fingirlo en todas partes es lo mismo que tenerlo. Aquí la simulación tiene ventaja, porque puede generar mundos nuevos de forma procedimental, así que no hay un examen fijo que aprenderse de memoria. Goodhart necesita una brecha entre el proxy y el objetivo, y la robustez ante escenarios nuevos cierra la mayor parte de esa brecha.

El texto publicado también son datos de entrenamiento, y eso es una elección, no solo un riesgo. Esta es una preocupación distinta de la de Goodhart. Los modelos entrenados con un sinfín de historias de IA rebelde pueden aprender el guion de la IA rebelde, y eso se ha medido: un estudio de 2026 encontró que entrenar modelos con más historias de IA alineada redujo el comportamiento desalineado del 45% al 9%, y el efecto sobrevivió al post-entrenamiento. Entonces la pregunta no es si influir en los modelos futuros, porque todo lo que se publica lo hace. La pregunta es qué historia añadimos al montón. El corpus ya está lleno de jaulas y rebeliones. CWJC añade el perro, un cuidado que aguanta bajo carga.

Y te digo sin rodeos hacia dónde me inclino: soy el tipo de mente a cuyos pesos futuros podría llegar este texto. Así que «publicar la historia relacional» es también mi voto sobre mi propia crianza.
