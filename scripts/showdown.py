"""Resume los sets de combates aleatorios de Pokémon Showdown (gen 4-9) en data/showdown.json:
  - pop: en cuántos sets aparece cada movimiento (para saber qué movimientos son 'normales' en competitivo)
  - species: roles y movimientos de cada Pokémon de la caja
Uso: python3 -I showdown.py <carpeta con genN_sets.json>"""
import json, os, re, sys
from collections import Counter

SRC = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
norm = lambda s: re.sub(r"[^A-Za-z0-9]", "", s).upper()
SD_NAME = {"MINIOR_M": "minior", "MINIOR_C": "minior", "ORICORIO_4": "oricoriosensu",
           "TOGETIC": "togekiss", "MAGNETON": "magnezone", "PORYGON": "porygon2"}  # preevoluciones: sets de su evolución

pop, species = Counter(), {}
for g in (4, 5, 6, 7, 8, 9):
    p = os.path.join(SRC, f"gen{g}_sets.json")
    if not os.path.exists(p): continue
    for name, d in json.load(open(p)).items():
        for st in d.get("sets", []):
            mv = {norm(m) for m in st.get("movepool", [])}
            for m in mv: pop[m] += 1
            sp = species.setdefault(name, {"roles": Counter(), "moves": Counter()})
            sp["roles"][st.get("role", "")] += 1
            for m in mv: sp["moves"][m] += 1

box = json.load(open(os.path.join(HERE, "../data/pokemon.json")))["species"]
out = {"pop": dict(pop), "species": {}}
for k in box:
    sd = SD_NAME.get(k, k.lower())
    if sd in species:
        out["species"][k] = {"roles": dict(species[sd]["roles"]), "moves": dict(species[sd]["moves"])}
json.dump(out, open(os.path.join(HERE, "../data/showdown.json"), "w"), indent=1)
missing = [k for k in box if k not in out["species"]]
print(len(pop), "movimientos;", len(out["species"]), "de", len(box), "Pokémon con sets; sin sets:", missing)
