Estoy jugando a Pokémon Infinite Fusion y quiero que me ayudes a encontrar las mejores fusiones posibles con los Pokémon de mi caja. Te adjunto una captura de la caja.

## Paso 1 · Identificar mi caja (confírmalo conmigo antes de seguir)
- Usa **solo** los Pokémon de la captura y **en la fase evolutiva que tienen**: si no están evolucionados es porque no puedo evolucionarlos.
- Si hay Pokémon repetidos, cuéntalos (por ejemplo, con dos Chandelure se puede usar dos veces y fusionarlo consigo mismo).
- Dame la lista de lo que ves y marca con ❓ los sprites dudosos para que te los corrija. **No calcules nada hasta que te confirme la lista.**
- Ojo: Infinite Fusion no tiene todos los Pokémon (solo unos ~500). Si alguno no existe en el juego, dímelo y propón el más parecido.

## Paso 2 · Datos sacados del propio juego, no de wikis
- Clona el repositorio oficial del juego: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/infinitefusion/infinitefusion-e18` (es grande; dale tiempo).
- Saca stats base, tipos y habilidades (normales y oculta) de `Data/species.dat`, `Data/abilities.dat` y `Data/moves.dat`. Están en formato Ruby Marshal: léelos con un parser propio en Python que **solo lea datos** (no uses `Marshal.load` de Ruby sobre archivos descargados).
- Algunos Pokémon cambian respecto a los juegos oficiales (por ejemplo, Magneton es Acero/Eléctrico). Fíate del archivo del juego.
- Guarda un `data/pokemon.json` con mis Pokémon: stats, tipos, habilidades y movimientos (los movimientos los usaremos más adelante).

## Paso 3 · Reglas de fusión (comprobadas en `Data/Scripts/048_Fusion/FusedSpecies.rb`)
- **Stats:** `⌊2·dominante/3⌋ + ⌊otro/3⌋`, redondeando hacia abajo.
  - La **cabeza** domina PS, Ataque Especial y Defensa Especial.
  - El **cuerpo** domina Ataque, Defensa y Velocidad.
- **Tipos:**
  - Tipo 1 = tipo principal de la cabeza. Si la cabeza es Normal/Volador, aporta Volador.
  - Tipo 2 = segundo tipo del cuerpo, o su único tipo. Si coincide con el tipo 1, se usa el primer tipo del cuerpo.
- **Habilidad:** al fusionar se elige entre la habilidad que tenga *en ese momento* la cabeza y la del cuerpo.
  - La 1ª/2ª habilidad se puede cambiar antes con una Cápsula Habilidad.
  - La oculta tiene que tenerla ya el Pokémon base.
- **Trucos propios de Infinite Fusion:**
  - **Cambio Táctico** (Aegislash) funciona en cualquier fusión: al atacar intercambia Atq↔Def y AtqEsp↔DefEsp, y Escudo Real lo devuelve a modo defensa.
  - **Escudo Limitado** (Minior) cambia a la forma Núcleo con ≤50 % de PS.
  - **Ausente** (Slaking) se evita fusionando y eligiendo la habilidad del otro Pokémon.

## Paso 4 · Calcular TODAS las fusiones
- Calcula todas las combinaciones cabeza/cuerpo en ambas direcciones, y cada fusión con cada una de sus habilidades posibles.
- No escatimes: si un Pokémon combina genial con varios, quiero todas esas combinaciones, no solo la mejor.
- **Puntuación** (las stats y los tipos son lo que más pesa):
  - **60 % stats:** su mejor rol entre atacante físico, atacante especial, muro/tanque y rápido/sweeper.
    - Las habilidades que cambian las stats en combate (Cambio Táctico, Impulso, Entusiasmo) solo deben retocar un poco estas cifras.
  - **28 % combinación de tipos defensiva:**
    - Inmunidades y resistencias suman, debilidades restan, y las ×4 restan mucho.
    - Absorbe Fuego, Herbívoro y Pararrayos cuentan como inmunidad.
  - **6 % valor de la habilidad *para esa fusión*:** por ejemplo, Respondón solo vale mucho si aprende Fuerza Bruta, Sofoco o Cometa Draco, y Mandíbula Fuerte solo si tiene mordiscos.
  - **6 % cobertura ofensiva** de sus dos tipos.
- Saca rankings: uno general y otro por cada rol.
- Explica en lenguaje claro las claves de cada fusión: combos de habilidad con movimientos, avisos de debilidad ×4, etc.

## Paso 5 · Resultado: un HTML (y artefacto) con estas secciones
1. **Mejores fusiones** (apartado principal):
   - Destacadas: la mejor de cada rol y la mejor con cada habilidad fuerte.
   - Debajo, el ranking completo con filtros por rol, un buscador y la opción de mostrar solo la mejor dirección de cada pareja.
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

**Extras:**
- Pon el sprite de cada fusión: el personalizado del juego si existe (`Graphics/CustomBattlers/spritesheets/spritesheets_custom/<cabeza>/<cabeza>.png`, rejilla de 20 columnas de 96 px, índice = número del cuerpo) y, si no, el autogenerado (`Graphics/Battlers/spritesheets_autogen/<cabeza>.png`, 10 columnas). Junta todos los sprites en un solo atlas `.webp`.
- Todo en español, que funcione en el móvil y con tema claro/oscuro.

## Proyecto
- Hazlo en un repositorio de GitHub con scripts reproducibles: `extract.py` → `analyze.py` → `sprites.py` → `build_site.py`.
- Haz commit y push al terminar, y publica el HTML como artefacto.
- De los movimientos no te preocupes por ahora; los miraremos al final.

¿Qué te parece el plan? ¿Le añadirías algo? Empieza por el paso 1 y espera a que te confirme la lista.
