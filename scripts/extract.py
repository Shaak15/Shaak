"""Extrae de los datos del juego (species.dat) los Pokémon de la caja del usuario.
Uso: python3 -I extract.py <ruta a infinitefusion-e18>"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rmarshal

ROOT = sys.argv[1]
BOX = [  # orden de la captura "Caja 2" (Chandelure aparece 2 veces)
 "PIDGEOT","SCOLIPEDE","SKARMORY","TORKOAL","CHANDELURE","KECLEON",
 "GOODRA","DUSKNOIR","GOLURK","TOXAPEX",
 "ALAKAZAM","MINIOR_M","GARBODOR","QWILFISH","TYRANTRUM","LURANTIS",
 "MAGCARGO","MEGANIUM","RAICHU","TOGETIC","NOIVERN","MAGNETON",
 "GRANBULL","TORTERRA","PORYGON","CHANDELURE","AEGISLASH","SLAKING",
]
EXTRA = ["MINIOR_C"]  # forma Núcleo (Escudo Limitado)
STATS = ["HP","ATTACK","DEFENSE","SPECIAL_ATTACK","SPECIAL_DEFENSE","SPEED"]

sp = rmarshal.load(os.path.join(ROOT, "Data/species.dat"))
ab = rmarshal.load(os.path.join(ROOT, "Data/abilities.dat"))
mv = rmarshal.load(os.path.join(ROOT, "Data/moves.dat"))

out = {"box": BOX, "species": {}, "abilities": {}, "moves": {}}
for key in dict.fromkeys(BOX + EXTRA):
    s = sp[key]
    bs = s.get("base_stats")
    moves = sorted({m for _, m in s.get("moves")} | set(s.get("tutor_moves") or []) | set(s.get("egg_moves") or []))
    out["species"][key] = {
        "id": key, "dex": s.get("id_number"), "name": s.get("real_name"),
        "type1": s.get("type1"), "type2": s.get("type2") or s.get("type1"),
        "stats": [bs[x] for x in STATS],
        "abilities": [a for a in s.get("abilities") if a],
        "hidden": [a for a in s.get("hidden_abilities") if a],
        "moves": moves,
    }
    for a in out["species"][key]["abilities"] + out["species"][key]["hidden"]:
        o = ab[a]; out["abilities"][a] = {"name": o.get("real_name"), "desc": o.get("real_description")}
    for m in moves:
        o = mv[m]
        out["moves"][m] = {"name": o.get("real_name"), "type": o.get("type"),
                           "power": o.get("base_damage"), "cat": o.get("category")}

os.makedirs("../data", exist_ok=True)
json.dump(out, open("../data/pokemon.json", "w"), indent=1, ensure_ascii=False)
print(len(out["species"]), "especies,", len(out["moves"]), "movimientos")
