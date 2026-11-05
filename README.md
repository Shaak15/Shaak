# Laboratorio de Fusiones · Pokémon Infinite Fusion

Herramienta para encontrar las fusiones más fuertes con los Pokémon de mi caja (Caja 2).

Abre **`site/index.html`** en el navegador (con `sprites.webp` en la misma carpeta).

## Secciones
- **Mejores fusiones**: destacadas por rol y por habilidad, más el ranking completo de todas las fusiones, con filtros por rol.
- **Explorador 1 a 1**: eliges un Pokémon y ves sus mejores fusiones como cabeza y como cuerpo.
- **Mejor equipo**: busca equipos de 6 sin repetir Pokémon base.
- **Mi equipo**: eliges tus fusiones y te dice los huecos de tipos y roles y quién los rellena mejor.
- **Tu caja**: stats y habilidades de cada Pokémon. Quita Pokémon de la caja o marca quién tiene la habilidad oculta y todo se recalcula.

Cada fusión trae un **set recomendado** de 4 movimientos (`scripts/sets.py`) que cuenta un 20% en la puntuación.
- **Cómo se calcula**: fórmulas y criterios.

## Datos
Todo se saca de los archivos del propio juego ([infinitefusion/infinitefusion-e18](https://github.com/infinitefusion/infinitefusion-e18)):

```bash
# Datos (versión 6.6, que incluye Camerupt): PBS de texto de la rama develop-6.6
B=https://raw.githubusercontent.com/infinitefusion/infinitefusion-e18/develop-6.6/PBS
mkdir -p pbs66 && for f in pokemon abilities moves; do curl -sSLo pbs66/$f.txt $B/$f.txt; done
python3 -I scripts/extract.py pbs66        # -> data/pokemon.json (stats, tipos, habilidades, movimientos)
python3 -I scripts/analyze.py              # -> data/fusions.json (todas las fusiones puntuadas)
# Sprites: custom de la rama main + autogenerados de develop-6.6 (Graphics/Battlers/spritesheets_autogen)
python3 -I scripts/sprites.py ../infinitefusion-e18 ../autogen66   # -> site/sprites.webp + data/sprites.json
python3 -I scripts/build_site.py           # -> site/index.html
```

`scripts/pbs.py` lee los PBS de texto del juego. `scripts/rmarshal.py` lee los `.dat` antiguos (Ruby Marshal) sin ejecutar código.

Sprites: artistas de la comunidad de Pokémon Infinite Fusion (ver `Data/Sprite Credits.csv` del juego).
