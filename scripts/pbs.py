"""Lector de los PBS de texto de Infinite Fusion (pokemon.txt, abilities.txt, moves.txt)."""
import csv, io

def read_pokemon(path):
    out, cur = {}, None
    for line in open(path, encoding="utf-8-sig"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.startswith("[") and line.endswith("]"):
            cur = {"id_number": int(line[1:-1])}; continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        cur[k] = v
        if k == "InternalName": out[v] = cur
    res = {}
    for name, s in out.items():
        hp, atk, de, spe, spa, spd = [int(x) for x in s["BaseStats"].split(",")]
        mv = s.get("Moves", "").split(",")
        moves = set(mv[1::2]) | set(filter(None, s.get("TutorMoves", "").split(","))) | set(filter(None, s.get("EggMoves", "").split(",")))
        res[name] = {
            "id": name, "dex": s["id_number"], "name": s["Name"],
            "type1": s["Type1"], "type2": s.get("Type2") or s["Type1"],
            "stats": [hp, atk, de, spa, spd, spe],
            "abilities": [a for a in s.get("Abilities", "").split(",") if a],
            "hidden": [a for a in s.get("HiddenAbility", "").split(",") if a],
            "moves": sorted(m for m in moves if m),
        }
    return res

def read_csvish(path):
    rows = []
    for line in open(path, encoding="utf-8-sig"):
        if not line.strip() or line.startswith("#"): continue
        rows.append(next(csv.reader(io.StringIO(line.strip()))))
    return rows

def read_abilities(path):
    return {r[1]: {"name": r[2], "desc": r[3] if len(r) > 3 else ""} for r in read_csvish(path)}

CAT = {"Physical": 0, "Special": 1, "Status": 2}
def read_moves(path):
    return {r[1]: {"name": r[2], "type": r[5], "power": int(r[4]), "cat": CAT.get(r[6], 2)} for r in read_csvish(path)}
