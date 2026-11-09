"""Extrae los Pokémon de la caja desde los PBS de texto del juego (rama develop-6.6).
Uso: python3 -I extract.py <carpeta con pokemon.txt, abilities.txt y moves.txt>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pbs

SRC = sys.argv[1]
BOX = [  # caja actual (Chandelure aparece 2 veces)
 "FEAROW","SCOLIPEDE","SKARMORY","CAMERUPT","CHANDELURE","KECLEON",
 "GOODRA","DUSCLOPS","GOLURK","TOXAPEX",
 "ALAKAZAM","MINIOR_M","GARBODOR","QWILFISH","TYRANTRUM","LURANTIS",
 "MAGCARGO","MEGANIUM","RAICHU","TOGETIC","NOIVERN","MAGNETON",
 "PORYGON","CHANDELURE","AEGISLASH","SLAKING",
 "ORICORIO_4",
 # nuevos: Corphish -> Crawdaunt (nivel 30), Magby -> Magmar (21) -> Magmortar (nivel 50 o Magmarizador)
 "TREVENANT","CHIMECHO","CRAWDAUNT","URSARING","MAGMORTAR",
 "DELPHOX",
 "FERROTHORN","MACHAMP","SUICUNE","ZAPDOS","NECROZMA","MISMAGIUS","SHARPEDO","CARBINK",
]
EXTRA = ["MINIOR_C"]  # forma Núcleo (Escudo Limitado)

sp = pbs.read_pokemon(os.path.join(SRC, "pokemon.txt"))
ab = pbs.read_abilities(os.path.join(SRC, "abilities.txt"))
mv = pbs.read_moves(os.path.join(SRC, "moves.txt"))

out = {"box": BOX, "species": {}, "abilities": {}, "moves": {}}
for key in dict.fromkeys(BOX + EXTRA):
    s = dict(sp[key])
    if key == "ORICORIO_4": s["name"] = "Oricorio (Fantasma)"
    out["species"][key] = s
    for a in s["abilities"] + s["hidden"]:
        out["abilities"][a] = ab[a]
    for m in s["moves"]:
        if m in mv: out["moves"][m] = mv[m]

os.makedirs("../data", exist_ok=True)
json.dump(out, open("../data/pokemon.json", "w"), indent=1, ensure_ascii=False)
print(len(out["species"]), "especies,", len(out["moves"]), "movimientos")
