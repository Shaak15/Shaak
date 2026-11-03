# Laboratorio de Fusiones · Pokémon Infinite Fusion

Herramienta para encontrar las fusiones más fuertes con los Pokémon de mi caja (Caja 2).

Abre **`site/index.html`** en el navegador (con `sprites.webp` en la misma carpeta).

## Secciones
- **Mejores fusiones**: destacadas por rol y por habilidad, más el ranking completo de las 703 fusiones, con filtros por rol.
- **Explorador 1 a 1**: eliges un Pokémon y ves sus mejores fusiones como cabeza y como cuerpo.
- **Mejor equipo**: busca equipos de 6 sin repetir Pokémon base.
- **Tu caja**: stats y habilidades de cada Pokémon. Marca quién tiene la habilidad oculta y todo se recalcula.
- **Cómo se calcula**: fórmulas y criterios.

## Datos
Todo se saca de los archivos del propio juego ([infinitefusion/infinitefusion-e18](https://github.com/infinitefusion/infinitefusion-e18)):

```bash
git clone --depth 1 https://github.com/infinitefusion/infinitefusion-e18 ../infinitefusion-e18
python3 -I scripts/extract.py ../infinitefusion-e18   # -> data/pokemon.json (stats, tipos, habilidades, movimientos)
python3 -I scripts/analyze.py                         # -> data/fusions.json (todas las fusiones puntuadas)
python3 -I scripts/sprites.py ../infinitefusion-e18   # -> site/sprites.webp + data/sprites.json
python3 -I scripts/build_site.py                      # -> site/index.html
```

`scripts/rmarshal.py` lee los `.dat` del juego (formato Ruby Marshal) sin ejecutar código.

Sprites: artistas de la comunidad de Pokémon Infinite Fusion (ver `Data/Sprite Credits.csv` del juego).
