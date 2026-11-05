Estoy jugando a Pokémon Infinite Fusion y quiero que me ayudes a encontrar las mejores fusiones posibles con los Pokémon de mi caja. Te adjunto una captura de la caja.

Uso la versión gratuita de Claude: **no busques ni descargues nada de GitHub ni de internet**. Trabaja con lo que ya sabes y hazlo todo dentro de un único artefacto HTML.

## Paso 1 · Identificar mi caja (confírmalo conmigo antes de seguir)
- Usa **solo** los Pokémon de la captura y **en la fase evolutiva que tienen**: si no están evolucionados es porque no puedo evolucionarlos.
- Si hay Pokémon repetidos, cuéntalos (con dos iguales se puede usar dos veces y fusionarlo consigo mismo).
- Dame la lista numerada de lo que ves y marca con ❓ los sprites dudosos para que te los corrija. **No hagas nada más hasta que te confirme la lista.**
- Infinite Fusion no tiene todos los Pokémon (solo unos ~500, sobre todo de 1ª-4ª gen más una selección de las demás; por ejemplo, Camerupt no está). Si alguno no existe en el juego, dímelo.

## Paso 2 · Tabla de mi caja
Cuando confirme la lista, dame una tabla con cada Pokémon:
- Tipos.
- Stats base (PS, Atq, Def, AtqEsp, DefEsp, Vel).
- Habilidades normales y oculta.

Notas para los datos:
- Infinite Fusion usa **mayoritariamente los stats de 5ª generación**, sin los aumentos de 6ª+ (por ejemplo, Pidgeot tiene 91 de Vel, Alakazam 85 de DefEsp y Raichu 100 de Vel). Los Pokémon posteriores usan sus stats oficiales.
- Algunos tipos cambian. Por ejemplo, Magneton es **Acero/Eléctrico** (Acero primero) y Togetic es Hada/Volador.
- Si no estás seguro de un dato, márcalo para que lo revise en el juego.

## Paso 3 · Reglas de fusión del juego
- **Stats:** `⌊2·dominante/3⌋ + ⌊otro/3⌋`, redondeando hacia abajo cada parte.
  - La **cabeza** domina PS, AtqEsp y DefEsp.
  - El **cuerpo** domina Atq, Def y Vel.
- **Tipos:**
  - Tipo 1 = tipo principal de la cabeza. Si la cabeza es Normal/Volador (Pidgeot, Togekiss…), aporta Volador.
  - Tipo 2 = segundo tipo del cuerpo, o su único tipo. Si coincide con el tipo 1, se usa el primer tipo del cuerpo. Si todo coincide, la fusión tiene un solo tipo.
- **Habilidad:** al fusionar se elige entre la habilidad que tenga *en ese momento* la cabeza y la del cuerpo.
  - La 1ª/2ª habilidad se puede cambiar antes con una Cápsula Habilidad.
  - La oculta tiene que tenerla ya el Pokémon base.
- **Trucos propios de Infinite Fusion:**
  - **Cambio Táctico** (Aegislash) funciona en cualquier fusión: al atacar intercambia Atq↔Def y AtqEsp↔DefEsp, y Escudo Real lo devuelve a modo defensa.
  - **Escudo Limitado** (Minior) pasa a la forma Núcleo con ≤50 % de PS.
  - **Ausente** (Slaking) se evita fusionando y eligiendo la habilidad del otro Pokémon.

## Paso 4 · El artefacto HTML (que el JavaScript haga los cálculos)
**No escribas a mano la lista de fusiones.** Mete en el HTML solo los datos de mi caja (paso 2) y la tabla de tipos, y que el **JavaScript calcule todas las fusiones** al abrir la página: todas las combinaciones cabeza/cuerpo en ambas direcciones, y cada fusión con cada habilidad posible.

**Puntuación de cada fusión** (las stats y los tipos son lo que más pesa):
- **60 % stats:** su mejor rol entre atacante físico, atacante especial, muro/tanque y rápido/sweeper.
- **28 % combinación de tipos defensiva:**
  - Inmunidades y resistencias suman, debilidades restan, y las ×4 restan mucho.
  - Absorbe Fuego, Herbívoro, Pararrayos, Levitación, etc. cuentan como inmunidad.
- **6 % valor de la habilidad** para esa fusión (Impulso, Mutatipo, Regeneración, Intimidación, Muro Mágico… valen más; Ausente resta muchísimo).
- **6 % cobertura ofensiva** de sus dos tipos.

**Secciones de la página:**
1. **Mejores fusiones** (apartado principal):
   - Destacadas: la mejor de cada rol y la mejor con cada habilidad fuerte.
   - Debajo, el ranking completo con filtros por rol, un buscador y la opción de mostrar solo la mejor dirección de cada pareja.
   - No escatimes: si un Pokémon combina genial con varios, que salgan todas esas fusiones.
2. **Explorador 1 a 1:**
   - Elijo un Pokémon de mi caja y veo todas sus fusiones, como cabeza y como cuerpo, ordenadas por puntuación.
   - Cada fila muestra a qué es débil.
3. **Mejor equipo de 6:**
   - Sin repetir Pokémon base, salvo los que tengo repetidos.
   - Que castigue que 3 o más compartan debilidad y premie mezclar roles.
   - Que me deje excluir Pokémon.
4. **Mi caja:** tabla con stats, tipos y habilidades, y una casilla por Pokémon de "tiene la habilidad oculta". Al desmarcarla, todo se recalcula.
5. **Cómo se calcula:** fórmulas, reglas y pesos.

Al pulsar una fusión quiero ver un **detalle**:
- Stats de la fusión comparadas con las de los dos Pokémon base.
- Todas las habilidades posibles con su puntuación.
- Una sección de **debilidades y resistencias explicada en texto**:
  - A qué es débil y por qué tipo. Por ejemplo: "débil a Siniestro ×2 (por Fantasma)".
  - Aviso especial para las ×4.
  - Inmunidades, indicando si vienen del tipo o de la habilidad.
  - Resistencias.
  - Una valoración del tipo defensivo.
- Una o dos claves de uso.

Todo en español, que funcione en el móvil y con tema claro/oscuro. Sin imágenes externas: usa colores por tipo en vez de sprites.

Si el artefacto es demasiado largo para una sola respuesta, hazlo por partes: primero los datos y el cálculo, luego el resto de secciones.

¿Qué te parece el plan? ¿Le añadirías algo? Empieza por el paso 1 y espera a que te confirme la lista.
