"""Calcula TODAS las fusiones posibles de la caja y las puntúa.

Reglas sacadas del código del juego (Data/Scripts/048_Fusion/FusedSpecies.rb):
  * Stats: floor(2*dominante/3) + floor(otro/3)
      - Cabeza domina: PS, AtqEsp, DefEsp      - Cuerpo domina: Atq, Def, Vel
  * Tipo 1 = tipo 1 de la cabeza (si la cabeza es Normal/Volador -> Volador)
    Tipo 2 = tipo 2 del cuerpo (o su único tipo); si coincide con el tipo 1 -> tipo 1 del cuerpo
  * Habilidad: al fusionar eliges entre la habilidad ACTUAL de la cabeza y la del cuerpo.
  * Cambio Táctico (Stance Change) en IF: al atacar intercambia Atq<->Def y AtqEsp<->DefEsp.
  * Escudo Limitado (Shields Down): con PS <= 50% pasa a la forma Núcleo de Minior.

Uso: python3 -I analyze.py   (lee ../data/pokemon.json, escribe ../data/fusions.json)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typechart import TYPES, eff

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "../data/pokemon.json")))
SP = DATA["species"]
BOX = DATA["box"]
UNIQUE = list(dict.fromkeys(BOX))
COUNT = {k: BOX.count(k) for k in UNIQUE}

# ---------------------------------------------------------------- reglas del juego
def fstat(dom, other):
    return (2 * dom) // 3 + other // 3

def fuse_stats(h, b):
    hs, bs = h["stats"], b["stats"]
    return [fstat(hs[0], bs[0]),  # PS      cabeza
            fstat(bs[1], hs[1]),  # Atq     cuerpo
            fstat(bs[2], hs[2]),  # Def     cuerpo
            fstat(hs[3], bs[3]),  # AtqEsp  cabeza
            fstat(hs[4], bs[4]),  # DefEsp  cabeza
            fstat(bs[5], hs[5])]  # Vel     cuerpo

def fuse_types(h, b):
    t1 = h["type2"] if (h["type1"] == "NORMAL" and h["type2"] == "FLYING") else h["type1"]
    t2 = b["type2"]
    if t2 == t1:
        t2 = b["type1"]
    return [t1] if t2 == t1 else [t1, t2]

def ability_options(h, b):
    """Todas las habilidades que puede llevar la fusión.
    kind: 'normal' (slot 1/2 del Pokémon base; con Cápsula Habilidad se cambia antes de fusionar)
          'oculta' (el Pokémon base tiene que tenerla ya)."""
    opts = []
    for who, s in (("cuerpo", b), ("cabeza", h)):
        for a in s["abilities"]:
            opts.append((a, who, "normal"))
        for a in s["hidden"]:
            opts.append((a, who, "oculta"))
    seen, out = set(), []
    for a, who, kind in opts:
        if a in seen:
            continue
        seen.add(a); out.append({"id": a, "from": who, "kind": kind})
    return out

# ---------------------------------------------------------------- movimientos clave
BITE = {"BITE","CRUNCH","FIREFANG","ICEFANG","THUNDERFANG","POISONFANG","PSYCHICFANGS","HYPERFANG","JAWLOCK"}
PUNCH = {"FIREPUNCH","ICEPUNCH","THUNDERPUNCH","DRAINPUNCH","MACHPUNCH","SHADOWPUNCH","DYNAMICPUNCH",
         "FOCUSPUNCH","HAMMERARM","BULLETPUNCH","METEORMASH","MEGAPUNCH","COMETPUNCH","DIZZYPUNCH",
         "SKYUPPERCUT","POWERUPPUNCH","ICEHAMMER"}
CONTRARY_MOVES = ["LEAFSTORM","OVERHEAT","DRACOMETEOR","SUPERPOWER","CLOSECOMBAT","PSYCHOBOOST",
                  "FLEURCANNON","HAMMERARM","VCREATE","DRAGONASCENT","ICEHAMMER","ARMORCANNON","MAKEITRAIN"]
SERENE = ["AIRSLASH","IRONHEAD","ROCKSLIDE","FAKEOUT","HEADBUTT","ZINGZAP","BODYSLAM","SCALD","NUZZLE",
          "ICICLECRASH","WATERFALL","BITE","DARKPULSE","EXTRASENSORY","ZENHEADBUTT","DISCHARGE",
          "THUNDERBOLT","FLAMETHROWER","ICEBEAM","PSYCHIC","SHADOWBALL","SLUDGEBOMB","LAVAPLUME","FLAMECHARGE"]
NOGUARD = ["DYNAMICPUNCH","FOCUSBLAST","STONEEDGE","ZAPCANNON","HYPNOSIS","INFERNO","FIREBLAST","THUNDER",
           "HURRICANE","BLIZZARD","HYDROPUMP","GUNKSHOT","CROSSCHOP","MEGAHORN","IRONTAIL","SING","SLEEPPOWDER","WILLOWISP"]
RECOIL = ["HEADSMASH","DOUBLEEDGE","BRAVEBIRD","FLAREBLITZ","WOODHAMMER","WILDCHARGE","HEADCHARGE","TAKEDOWN","SUBMISSION","VOLTTACKLE"]
PIVOT = ["UTURN","VOLTSWITCH","FLIPTURN","PARTINGSHOT","TELEPORT"]
SETUP_PHYS = ["SWORDSDANCE","DRAGONDANCE","SHELLSMASH","BULKUP","CURSE","HONECLAWS","SHIFTGEAR","COIL","HOWL"]
SETUP_SPEC = ["NASTYPLOT","CALMMIND","QUIVERDANCE","SHELLSMASH","TAILGLOW","GEOMANCY","GROWTH","WORKUP"]

def mname(m):
    return DATA["moves"].get(m, {}).get("name", m)

def has(moves, lst):
    return [m for m in lst if m in moves]

# ---------------------------------------------------------------- puntuación
TYPE_PTS = {0: 3.0, 0.25: 2.0, 0.5: 1.0, 1: 0.0, 2: -2.0, 4: -5.0}
IMMUNITY_AB = {"FLASHFIRE": "FIRE", "SAPSIPPER": "GRASS", "LIGHTNINGROD": "ELECTRIC", "LEVITATE": "GROUND"}

def defense_profile(types, ability):
    prof = {}
    for t in TYPES:
        m = eff(t, types)
        if IMMUNITY_AB.get(ability) == t:
            m = 0
        prof[t] = m
    return prof

def typing_score(prof):
    return sum(TYPE_PTS[m] for m in prof.values())

def offense_coverage(types, ability):
    atk_types = TYPES if ability == "PROTEAN" else types
    return sum(1 for t in TYPES if max(eff(a, [t]) for a in atk_types) >= 2)

def bulk(hp, d):
    return math.sqrt(hp * d)

def role_scores(st):
    hp, at, de, sa, sd, sp = st
    bp, bs = bulk(hp, de), bulk(hp, sd)
    return {
        "fisico":   at * 1.0 + sp * 0.55 + 0.35 * (bp + bs),
        "especial": sa * 1.0 + sp * 0.55 + 0.35 * (bp + bs),
        "muro":     (bp + bs) * 0.85 + 0.3 * max(at, sa),
        "rapido":   sp * 1.0 + max(at, sa) * 0.8 + 0.15 * (bp + bs),
    }

def effective_stats(st, ability, core_st=None):
    """Stats 'reales' teniendo en cuenta la habilidad."""
    hp, at, de, sa, sd, sp = st
    if ability == "STANCECHANGE":
        # Ataca en forma Espada (Atq=Def, AtqEsp=DefEsp); Escudo Real devuelve las defensas.
        at2, sa2 = (at + max(at, de)) / 2, (sa + max(sa, sd)) / 2
        de2 = 0.65 * de + 0.35 * min(at, de) if de > at else de
        sd2 = 0.65 * sd + 0.35 * min(sa, sd) if sd > sa else sd
        return [hp, at2, de2, sa2, sd2, sp]
    if ability == "HUSTLE":
        return [hp, at * 1.15, de, sa, sd, sp]   # x1.5 Atq con 80% precisión ~ x1.3 neto
    if ability == "SHIELDSDOWN" and core_st:
        return [(a + b) / 2 for a, b in zip(st, core_st)]
    if ability == "SPEEDBOOST":
        return [hp, at, de, sa, sd, sp * 1.1]
    return list(st)

def ability_value(a, ctx):
    """0-100: lo buena que es la habilidad PARA ESTA fusión concreta."""
    mv, role, st, types = ctx["moves"], ctx["role"], ctx["stats"], ctx["types"]
    phys = role in ("fisico",) or (role == "rapido" and st[1] >= st[3])
    v = {
        "SPEEDBOOST": 84, "PROTEAN": 85, "MAGICGUARD": 72, "REGENERATOR": 66, "INTIMIDATE": 70,
        "SHADOWTAG": 66, "SHIELDSDOWN": 62, "STURDY": 38, "FLASHFIRE": 45, "SAPSIPPER": 45,
        "LIGHTNINGROD": 45, "DOWNLOAD": 45, "TRACE": 35, "GOOEY": 35, "WEAKARMOR": 22,
        "INFILTRATOR": 28, "QUICKFEET": 35, "SUPERLUCK": 30, "PRESSURE": 25, "WHITESMOKE": 25,
        "POISONPOINT": 30, "STATIC": 30, "FLAMEBODY": 32, "SHELLARMOR": 25, "BIGPECKS": 12,
        "KEENEYE": 10, "INNERFOCUS": 20, "LIMBER": 15, "MAGMAARMOR": 10, "SYNCHRONIZE": 18,
        "MAGNETPULL": 15, "LEAFGUARD": 8, "OVERGROW": 20, "SWARM": 20, "SWIFTSWIM": 8,
        "STENCH": 22, "AFTERMATH": 15, "FRISK": 10, "HYDRATION": 5, "TELEPATHY": 3,
        "TANGLEDFEET": 3, "RATTLED": 8, "COLORCHANGE": 8, "KLUTZ": 0, "TRUANT": -100,
        "SNIPER": 25, "DANCER": 25, "SOLIDROCK": 40, "ANGERPOINT": 15,
        "LEVITATE": 55, "ADAPTABILITY": 70, "GUTS": 45, "NATURALCURE": 35, "HARVEST": 18,
        "HYPERCUTTER": 10, "UNNERVE": 10, "VITALSPIRIT": 12,
    }.get(a)
    if v is not None:
        if a == "REGENERATOR" and role == "muro": v += 12
        if a == "INTIMIDATE" and role == "muro": v += 6
        if a == "STURDY" and st[0] + st[2] + st[4] < 230: v += 10
        if a == "MAGICGUARD" and role in ("especial", "rapido"): v += 5
        if a == "SHADOWTAG" and role == "muro": v -= 6
        return v
    if a == "STANCECHANGE":
        gain = max(0, st[2] - st[1]) + max(0, st[4] - st[3])
        return min(95, 40 + gain * 0.5)
    if a == "CONTRARY":
        return 88 if has(mv, CONTRARY_MOVES) else 25
    if a == "DROUGHT":
        return 78 if ("FIRE" in types or has(mv, ["SOLARBEAM", "SOLARBLADE"])) else 50
    if a == "HUSTLE":
        return 60 if phys else 5
    if a == "SERENEGRACE":
        return 65 if len(has(mv, SERENE)) >= 2 else 35
    if a == "MERCILESS":
        return 50 if has(mv, ["TOXIC", "TOXICSPIKES", "BANEFULBUNKER"]) else 30
    if a == "NOGUARD":
        return 52 if len(has(mv, NOGUARD)) >= 2 else 30
    if a == "STRONGJAW":
        return 58 if (has(mv, BITE) and phys) else 12
    if a == "IRONFIST":
        return 55 if (len(has(mv, PUNCH)) >= 2 and phys) else 12
    if a == "ANALYTIC":
        return 42 if st[5] < 70 else 20
    if a == "ROCKHEAD":
        return 50 if (has(mv, RECOIL) and phys) else 10
    return 15

def norm(vals):
    lo, hi = min(vals), max(vals)
    return lambda x: 100 * (x - lo) / (hi - lo) if hi > lo else 50

# ---------------------------------------------------------------- notas en español
T_ES = {"NORMAL":"Normal","FIRE":"Fuego","WATER":"Agua","ELECTRIC":"Eléctrico","GRASS":"Planta","ICE":"Hielo",
        "FIGHTING":"Lucha","POISON":"Veneno","GROUND":"Tierra","FLYING":"Volador","PSYCHIC":"Psíquico","BUG":"Bicho",
        "ROCK":"Roca","GHOST":"Fantasma","DRAGON":"Dragón","DARK":"Siniestro","STEEL":"Acero","FAIRY":"Hada"}
from abilities_es import AB_ES

def notes_for(f, ab, ctx):
    mv, st, raw = ctx["moves"], ctx["stats"], f["stats"]
    n = []
    if ab == "STANCECHANGE":
        n.append(f"Cambio Táctico: al atacar se intercambian Atq↔Def y AtqEsp↔DefEsp → ataca con {raw[2]} Atq / {raw[4]} AtqEsp. "
                 + ("Escudo Real (King's Shield) lo devuelve a modo defensa." if "KINGSSHIELD" in mv else ""))
    if ab == "SPEEDBOOST":
        p = has(mv, ["PROTECT", "DETECT", "SUBSTITUTE"]) + has(mv, SETUP_PHYS + SETUP_SPEC)
        n.append("Impulso: +1 Vel cada turno." + (f" Combo: {', '.join(mname(x) for x in p[:4])}." if p else ""))
    if ab == "CONTRARY":
        c = has(mv, CONTRARY_MOVES)
        if c: n.append(f"Respondón: {', '.join(mname(x) for x in c)} te SUBEN las stats en vez de bajarlas.")
    if ab == "PROTEAN":
        n.append("Mutatipo: cada ataque tiene STAB (x1.5) y cambias de tipo al atacar.")
    if ab == "DROUGHT":
        s = has(mv, ["SOLARBEAM", "SOLARBLADE"])
        n.append("Sequía: sol al entrar (Fuego x1.5, Agua x0.5)." + (f" {', '.join(mname(x) for x in s)} sin carga." if s else ""))
    if ab == "MAGICGUARD":
        n.append("Muro Mágico: sin daño por veneno, quemadura, trampas ni Vidasfera → lleva Vidasfera.")
    if ab == "REGENERATOR":
        p = has(mv, PIVOT)
        n.append("Regeneración: recupera 1/3 de PS al cambiar." + (f" Con {', '.join(mname(x) for x in p)} pivota gratis." if p else ""))
    if ab == "MERCILESS":
        n.append("Ensañamiento: críticos seguros contra rivales envenenados (Tóxico/Púas Tóxicas primero).")
    if ab == "HUSTLE":
        n.append("Entusiasmo: Atq x1.5 pero 80% de precisión en físicos.")
    if ab == "SHIELDSDOWN":
        n.append("Escudo Limitado: inmune a estados en forma Meteoro; con ≤50% PS pasa a Núcleo (más Atq/AtqEsp/Vel).")
    if ab == "SERENEGRACE":
        s = has(mv, SERENE)
        if s: n.append(f"Dicha: efectos secundarios x2 ({', '.join(mname(x) for x in s[:4])}).")
    if ab == "STRONGJAW":
        n.append(f"Mandíbula Fuerte: mordiscos x1.5 ({', '.join(mname(x) for x in has(mv, BITE)[:4])}).")
    if ab == "IRONFIST":
        n.append(f"Puño Férreo: puños x1.2 ({', '.join(mname(x) for x in has(mv, PUNCH)[:4])}).")
    if ab == "NOGUARD":
        n.append(f"Indefenso: todo acierta ({', '.join(mname(x) for x in has(mv, NOGUARD)[:4])}).")
    if ab == "SHADOWTAG":
        n.append("Sombra Trampa: el rival no puede huir ni cambiar.")
    if ab == "ADAPTABILITY":
        n.append("Adaptable: los ataques de su tipo pegan x2 en vez de x1.5.")
    if ab == "LEVITATE":
        n.append("Levitación: inmune a los ataques de tipo Tierra.")
    if ab == "GUTS":
        n.append("Agallas: Atq x1.5 si tiene un estado; con Llamasfera (Flame Orb) siempre activo.")
    if ab == "INTIMIDATE":
        n.append("Intimidación: -1 Atq al rival al entrar.")
    if "SHELLSMASH" in mv and ab not in ("CONTRARY",):
        n.append("Tiene Rompecoraza (de Minior): +2 Atq/AtqEsp/Vel de golpe.")
    if ab == "CONTRARY" and "SHELLSMASH" in mv:
        n.append("¡Ojo! Rompecoraza con Respondón es al revés (baja ataques).")
    if any(s.startswith("SLAKING") for s in (f["head"], f["body"])) and ab != "TRUANT":
        n.append("Esquiva Ausente de Slaking: fusiona con Slaking llevando la habilidad del otro.")
    q = [T_ES[t] for t, m in ctx["prof"].items() if m == 4]
    if q: n.append("⚠ Debilidad x4 a " + ", ".join(q) + ".")
    return n

def ab_entry(x, i):
    prof = i["prof"]
    f = {"head": x["head"], "body": x["body"], "stats": x["stats"]}
    return {"id": i["ab"]["id"], "from": i["ab"]["from"], "kind": i["ab"]["kind"],
            "score": i["score"], "role": i["role"], "roles": i["roles"], "est": i["est"],
            "mult": [prof[t] for t in TYPES], "typ": i["typ"],
            "cov": i["cov"], "notes": notes_for(f, i["ab"]["id"], i["ctx"])}

# ---------------------------------------------------------------- bucle principal
def build():
    pairs = []
    for h in UNIQUE:
        for b in UNIQUE:
            if h == b and COUNT[h] < 2:
                continue
            pairs.append((h, b))

    rows = []
    for h, b in pairs:
        H, B = SP[h], SP[b]
        st = fuse_stats(H, B)
        types = fuse_types(H, B)
        moves = set(H["moves"]) | set(B["moves"])
        core = None
        if "MINIOR_M" in (h, b):
            core = fuse_stats(SP["MINIOR_C"] if h == "MINIOR_M" else H, SP["MINIOR_C"] if b == "MINIOR_M" else B)
        opts = ability_options(H, B)
        per = []
        for o in opts:
            a = o["id"]
            est = effective_stats(st, a, core)
            rs = role_scores(est)
            if a == "TRUANT":
                rs = {k: v * 0.5 for k, v in rs.items()}
            prof = defense_profile(types, a)
            per.append({"ab": o, "est": est, "rs": rs, "prof": prof,
                        "typ": typing_score(prof), "cov": offense_coverage(types, a)})
        rows.append({"head": h, "body": b, "stats": st, "core": core, "types": types,
                     "moves": moves, "per": per})

    # normalizar por rol / tipos / cobertura sobre todo el conjunto
    allrs = {r: [p["rs"][r] for x in rows for p in x["per"]] for r in ("fisico", "especial", "muro", "rapido")}
    nr = {r: norm(v) for r, v in allrs.items()}
    nt = norm([p["typ"] for x in rows for p in x["per"]])
    nc = norm([p["cov"] for x in rows for p in x["per"]])

    out = []
    for x in rows:
        best = None
        abil_list = []
        for p in x["per"]:
            rsn = {r: nr[r](v) for r, v in p["rs"].items()}
            role = max(rsn, key=rsn.get)
            ctx = {"moves": x["moves"], "role": role, "stats": p["est"], "types": x["types"], "prof": p["prof"]}
            av = ability_value(p["ab"]["id"], ctx)
            score = 0.60 * rsn[role] + 0.28 * nt(p["typ"]) + 0.06 * max(-40, av) + 0.06 * nc(p["cov"])
            # puntuación por rol (para los rankings por rol)
            role_total = {r: 0.66 * rsn[r] + 0.24 * nt(p["typ"]) + 0.05 * max(-40, av) + 0.05 * nc(p["cov"]) for r in rsn}
            item = {"ab": p["ab"], "score": round(score, 2), "role": role, "roles": {k: round(v, 1) for k, v in role_total.items()},
                    "est": [round(s) for s in p["est"]], "abv": av, "typ": p["typ"], "cov": p["cov"],
                    "prof": p["prof"], "ctx": ctx}
            abil_list.append(item)
            if best is None or score > best["score"]:
                best = item
        abil_list.sort(key=lambda i: -i["score"])
        prof = best["prof"]
        f = {"head": x["head"], "body": x["body"], "stats": x["stats"], "bst": sum(x["stats"]),
             "core": x["core"], "types": x["types"],
             "best": best["ab"]["id"], "score": best["score"], "role": best["role"],
             "abilities": [ab_entry(x, i) for i in abil_list],
             }
        out.append(f)

    out.sort(key=lambda f: -f["score"])
    for i, f in enumerate(out):
        f["rank"] = i + 1
    return out

if __name__ == "__main__":
    fus = build()
    meta = {
        "box": BOX, "count": COUNT,
        "species": {k: {kk: v[kk] for kk in ("id", "name", "dex", "type1", "type2", "stats", "abilities", "hidden")}
                    for k, v in SP.items()},
        "abilities": {k: {"en": v["name"], "es": AB_ES.get(k, v["name"]), "desc": v["desc"]} for k, v in DATA["abilities"].items()},
        "types_es": T_ES, "types": TYPES, "chart": [[eff(x, [y]) for y in TYPES] for x in TYPES],
    }
    json.dump({"meta": meta, "fusions": fus}, open(os.path.join(HERE, "../data/fusions.json"), "w"), ensure_ascii=False)
    print(len(fus), "fusiones")
    for f in fus[:40]:
        print(f'{f["rank"]:3} {f["score"]:6.1f} {f["head"]:>10}/{f["body"]:<10} {"/".join(f["types"]):16} {f["best"]:13} {f["role"]:8} {f["stats"]} {f["bst"]}')
