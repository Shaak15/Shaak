"""Sets recomendados de cada fusión, guiados por los sets reales de Pokémon Showdown.

La fusión aprende los movimientos de la cabeza y del cuerpo (nivel, MT/tutor y huevo).
Para cada habilidad se generan hasta tres sets, uno por arquetipo (como los roles de Showdown):
  * ataque  -> Fast Attacker / Wallbreaker / Setup Sweeper: 3-4 ataques + setup o protección
  * tanque  -> Bulky Attacker / Bulky Setup: 2-3 ataques + recuperación (+ estado o setup)
  * support -> Bulky/Fast Support: trampas, quemar/envenenar/paralizar, pivotar, recuperarse, 1-2 ataques
Los movimientos que casi nunca se usan en competitivo (según Showdown) pesan menos, y los que
usan de verdad la cabeza o el cuerpo pesan algo más.
"""
import itertools, json, os
import numpy as np
from typechart import TYPES, eff
from moves_es import MOVES_ES

HERE = os.path.dirname(os.path.abspath(__file__))
SD = json.load(open(os.path.join(HERE, "../data/showdown.json")))
POP = SD["pop"]

EFF = np.array([[eff(a, [d]) for d in TYPES] for a in TYPES])
TIDX = {t: i for i, t in enumerate(TYPES)}

BANNED = set("""HYPERBEAM GIGAIMPACT BLASTBURN FRENZYPLANT HYDROCANNON ROCKWRECKER ROAROFTIME SKYATTACK SKULLBASH
RAZORWIND FLY DIG DIVE BOUNCE PHANTOMFORCE SHADOWFORCE SKYDROP FOCUSPUNCH EXPLOSION SELFDESTRUCT MEMENTO FINALGAMBIT
FISSURE SHEERCOLD HORNDRILL GUILLOTINE DREAMEATER SNORE FUTURESIGHT DOOMDESIRE BIDE COUNTER MIRRORCOAT METALBURST
BELCH LASTRESORT SYNCHRONOISE NATURALGIFT FLING SPITUP TRUMPCARD HIDDENPOWER FRUSTRATION REVERSAL FLAIL ENDEAVOR
SUPERFANG NIGHTSHADE SEISMICTOSS DRAGONRAGE SONICBOOM PSYWAVE PRESENT ROLLOUT ICEBALL FURYCUTTER UPROAR STRUGGLE RAGE
ECHOEDVOICE ROUND STOREDPOWER PUNISHMENT ELECTROBALL GYROBALL MAGNITUDE FALSESWIPE FEINT FAKEOUT
BIND WRAP FIRESPIN INFESTATION WHIRLPOOL CLAMP SANDTOMB THRASH PETALDANCE OUTRAGE SOLARBEAM SOLARBLADE ERUPTION
WATERSPOUT RETALIATE REVENGE PAYBACK ASSURANCE COVET THIEF PURSUIT SECRETPOWER STRUGGLEBUG ACROBATICS
PRISMATICLASER METEORASSAULT ETERNABEAM GEOMANCY FREEZESHOCK ICEBURN METEORBEAM""".split())
SUN_OK = {"SOLARBEAM", "SOLARBLADE"}
MULTI = {"DOUBLEKICK": 2, "BONEMERANG": 2, "DUALCHOP": 2, "GEARGRIND": 2, "DOUBLEHIT": 2, "BULLETSEED": 3,
         "ROCKBLAST": 3, "ICICLESPEAR": 3, "PINMISSILE": 3, "TAILSLAP": 3, "ARMTHRUST": 3, "FURYSWIPES": 3,
         "FURYATTACK": 3, "DOUBLESLAP": 3, "COMETPUNCH": 3, "SPIKECANNON": 3, "BARRAGE": 3, "TRIPLEKICK": 4,
         "WATERSHURIKEN": 3, "TWINEEDLE": 2}
FIXED_POWER = {"RETURN": 102, "LOWKICK": 60, "GRASSKNOT": 60, "HEAVYSLAM": 60, "HEX": 65, "FACADE": 70,
               "BRINE": 70, "VENOSHOCK": 65, "SMACKDOWN": 50}
SELF_DROP = {"SUPERPOWER": 0.85, "CLOSECOMBAT": 0.95, "OVERHEAT": 0.8, "LEAFSTORM": 0.8, "DRACOMETEOR": 0.8,
             "PSYCHOBOOST": 0.8, "FLEURCANNON": 0.8, "HAMMERARM": 0.95, "ICEHAMMER": 0.95, "VCREATE": 0.9}
DROP_ATK = {"SUPERPOWER"}                                   # baja el Ataque
DROP_SPA = {"OVERHEAT", "LEAFSTORM", "DRACOMETEOR", "PSYCHOBOOST", "FLEURCANNON"}  # baja el AtqEsp
RECOIL = {"BRAVEBIRD", "DOUBLEEDGE", "FLAREBLITZ", "WOODHAMMER", "WILDCHARGE", "HEADSMASH", "TAKEDOWN",
          "SUBMISSION", "VOLTTACKLE", "HEADCHARGE"}
DRAIN = {"DRAINPUNCH", "GIGADRAIN", "HORNLEECH", "LEECHLIFE", "DRAININGKISS", "OBLIVIONWING"}
SERENE_GOOD = {"AIRSLASH", "IRONHEAD", "ROCKSLIDE", "HEADBUTT", "ZENHEADBUTT", "BODYSLAM", "SCALD", "DARKPULSE",
               "EXTRASENSORY", "DISCHARGE", "BITE", "STOMP", "ICICLECRASH", "WATERFALL", "ZINGZAP"}

SETUP = {"SWORDSDANCE": ("fis", .35), "DRAGONDANCE": ("fis", .45), "BULKUP": ("fis", .25), "CURSE": ("fis", .2),
         "HONECLAWS": ("fis", .18), "COIL": ("fis", .3), "SHIFTGEAR": ("fis", .45),
         "NASTYPLOT": ("esp", .35), "CALMMIND": ("esp", .28), "QUIVERDANCE": ("esp", .5), "TAILGLOW": ("esp", .45),
         "GROWTH": ("ambos", .15), "WORKUP": ("ambos", .12), "SHELLSMASH": ("ambos", .55),
         "ROCKPOLISH": ("ambos", .2), "AGILITY": ("ambos", .2)}
RECOVERY = {"RECOVER": .5, "ROOST": .5, "SLACKOFF": .5, "SOFTBOILED": .5, "MILKDRINK": .5, "MOONLIGHT": .42,
            "MORNINGSUN": .42, "SYNTHESIS": .42, "SHOREUP": .5, "WISH": .35, "STRENGTHSAP": .55, "REST": .2}
# movimientos de support: (grupo, valor). Los grupos evitan repetir dos cosas del mismo tipo.
SUPPORT = {"STEALTHROCK": ("trampa", .5), "SPIKES": ("trampa2", .42), "TOXICSPIKES": ("trampa3", .32),
           "STICKYWEB": ("trampa4", .42),
           "WILLOWISP": ("estado", .45), "TOXIC": ("estado", .4), "THUNDERWAVE": ("estado", .34), "GLARE": ("estado", .38),
           "SPORE": ("sueno", .5), "SLEEPPOWDER": ("sueno", .36), "YAWN": ("sueno", .28), "STUNSPORE": ("estado", .28),
           "UTURN": ("pivote", .38), "VOLTSWITCH": ("pivote", .38), "FLIPTURN": ("pivote", .32), "PARTINGSHOT": ("pivote", .42),
           "TELEPORT": ("pivote", .3), "DEFOG": ("limpiar", .3), "RAPIDSPIN": ("limpiar", .3),
           "KNOCKOFF": ("quitar", .38), "TRICK": ("quitar", .18), "TAUNT": ("mofa", .26), "ENCORE": ("mofa", .3),
           "HAZE": ("fase", .22), "CLEARSMOG": ("fase", .18), "ROAR": ("fase", .26), "WHIRLWIND": ("fase", .26),
           "DRAGONTAIL": ("fase", .26), "REFLECT": ("pantalla", .25), "LIGHTSCREEN": ("pantalla2", .25),
           "HEALBELL": ("cura", .3), "AROMATHERAPY": ("cura", .3), "PAINSPLIT": ("recup", .3),
           "LEECHSEED": ("drenar", .28), "TRICKROOM": ("espacio", .2), "DESTINYBOND": ("mofa", .16),
           "NUZZLE": ("estado", .2), "SCALD": ("quemar", .25), "LAVAPLUME": ("quemar", .18)}
PROT = {"PROTECT": .06, "DETECT": .06, "KINGSSHIELD": .1, "BANEFULBUNKER": .25}
SLEEP_ACC = {"SPORE": 100, "SLEEPPOWDER": 75, "HYPNOSIS": 60, "YAWN": 100}


def popf(mid):
    """Peso según lo que se usa en competitivo: los movimientos raros pesan menos."""
    n = POP.get(mid, 0)
    return 1.0 if n >= 20 else 0.95 if n >= 5 else 0.88 if n >= 1 else 0.72


def offense_stats(f, ab, est):
    hp, at, de, sa, sd, sp = f["stats"]
    if ab == "STANCECHANGE":          # al atacar se intercambian: ataca con Def y DefEsp
        return de, sd
    if ab == "SHIELDSDOWN":
        return est[1], est[3]
    return at, sa


def attack_vector(mid, m, ab, atk, spa, types, speed, parents):
    if m["cat"] == 2:
        return None
    if mid in BANNED and not (mid in SUN_OK and ab == "DROUGHT"):
        return None
    p = FIXED_POWER.get(mid, m["power"])
    if p <= 1:
        return None
    p *= MULTI.get(mid, 1)
    acc = 1.0 if (m["acc"] == 0 or ab == "NOGUARD") else m["acc"] / 100
    t = m["type"]
    stab = 1.0
    if ab == "PROTEAN" or t in types:
        stab = 2.0 if ab == "ADAPTABILITY" else 1.5
    mod = popf(mid) * (1.06 if mid in parents else 1.0)
    phys = m["cat"] == 0
    fl = m.get("flags", "")
    if ab == "HUSTLE" and phys: mod *= 1.5; acc *= 0.8
    if ab == "IRONFIST" and "j" in fl: mod *= 1.2
    if ab == "STRONGJAW" and "i" in fl: mod *= 1.5
    if ab == "GUTS" and phys: mod *= 1.3
    if ab == "GUTS" and mid == "FACADE": p = 140
    if ab == "DROUGHT":
        if t == "FIRE": mod *= 1.5
        if t == "WATER": mod *= 0.5
    if ab == "ANALYTIC" and speed < 70: mod *= 1.15
    if ab == "SERENEGRACE" and mid in SERENE_GOOD: mod *= 1.12
    if mid in SELF_DROP:
        mod *= 1.6 if ab == "CONTRARY" else SELF_DROP[mid]
    if mid in RECOIL and ab != "ROCKHEAD": mod *= 0.92
    if mid in DRAIN: mod *= 1.08
    if m["prio"] > 0: mod *= 1.05
    stat = atk if phys else spa
    return EFF[TIDX[t]] * (p * acc * stab * mod * stat / 10000.0)


_COMBOS = {}
def combos(n, k):
    if (n, k) not in _COMBOS:
        _COMBOS[(n, k)] = np.array(list(itertools.combinations(range(n), k)), dtype=int) if n >= k else np.zeros((0, k), int)
    return _COMBOS[(n, k)]


def best_attacks(V, ids, k, must=None):
    """Mejor combinación de k ataques (máximo daño medio contra los 18 tipos)."""
    n = len(ids)
    if n == 0 or k <= 0:
        return 0.0, []
    k = min(k, n)
    C = combos(n, k)
    if must is not None:
        C = C[(C == must).any(axis=1)]
        if len(C) == 0: return 0.0, []
    sc = V[C].max(axis=1).mean(axis=1)
    j = int(np.argmax(sc))
    return float(sc[j]), [ids[i] for i in C[j]]


def generate(f, ab, est, moves_db, movepool):
    """Devuelve {'ataque': {...}, 'tanque': {...}, 'support': {...}} con moves y value."""
    hp, at, de, sa, sd, sp = est
    atk, spa = offense_stats(f, ab, est)
    bulk = (np.sqrt(hp * de) + np.sqrt(hp * sd)) / 200.0
    parents = set()
    for k in (f["head"], f["body"]):
        parents |= set(SD["species"].get(k, {}).get("moves", {}))
    vecs, ids = [], []
    for mid in movepool:
        m = moves_db.get(mid)
        if not m: continue
        v = attack_vector(mid, m, ab, atk, spa, f["types"], sp, parents)
        if v is not None:
            vecs.append(v); ids.append(mid)
    out = {}
    if not vecs:
        return out
    V = np.array(vecs)
    order = np.argsort(-V.mean(axis=1))
    keep, per_type = [], {}
    for i in order:
        t = moves_db[ids[i]]["type"]
        if per_type.get(t, 0) >= 2: continue
        per_type[t] = per_type.get(t, 0) + 1
        keep.append(i)
        if len(keep) >= 12: break
    V = V[keep]; ids = [ids[i] for i in keep]
    cat = {i: moves_db[i]["cat"] for i in ids}
    pool = set(movepool)

    def setup_ok(s, atts):
        kind = SETUP[s][0]
        nphys = sum(1 for a in atts if cat[a] == 0); nspec = len(atts) - nphys
        if kind == "fis" and (nphys < 2 or any(a in DROP_ATK for a in atts) and ab != "CONTRARY"): return False
        if kind == "esp" and (nspec < 2 or any(a in DROP_SPA for a in atts) and ab != "CONTRARY"): return False
        if kind == "ambos" and len(atts) < 2: return False
        return True

    setups = [s for s in SETUP if s in pool and POP.get(s, 0) >= 5]
    recs = sorted([r for r in RECOVERY if r in pool], key=lambda r: -RECOVERY[r])
    rec = recs[0] if recs else None
    prot = None
    if ab == "STANCECHANGE" and "KINGSSHIELD" in pool: prot = ("KINGSSHIELD", 0.85)
    elif ab == "SPEEDBOOST" and ({"PROTECT", "DETECT"} & pool): prot = ("PROTECT" if "PROTECT" in pool else "DETECT", 0.5)
    elif ab == "MERCILESS" and "BANEFULBUNKER" in pool: prot = ("BANEFULBUNKER", 0.35)

    # --- ataque: 4 ataques / setup + 3 / protección (+ setup) + ataques
    best = None
    fixed = [prot[0]] if prot else []
    extra = prot[1] if prot else 0
    for s in [None] + setups:
        k = 4 - len(fixed) - (1 if s else 0)
        o, atts = best_attacks(V, ids, k)
        if not atts: continue
        if s and not setup_ok(s, atts): continue
        val = o * (1 + (SETUP[s][1] if s else 0)) + extra
        if ab == "CONTRARY" and any(a in SELF_DROP for a in atts): val += 0.1 * o
        if best is None or val > best["value"]:
            best = {"moves": atts + fixed + ([s] if s else []), "value": val, "off": o}
    if best: out["ataque"] = best

    # --- tanque: recuperación obligatoria + 2-3 ataques (+ setup o estado)
    if rec:
        best = None
        bulky_extra = [s for s in setups if SETUP[s][0] != "ambos"] + [u for u in ("WILLOWISP", "TOXIC", "THUNDERWAVE", "STEALTHROCK", "LEECHSEED") if u in pool]
        for x in [None] + bulky_extra:
            k = 4 - 1 - len(fixed) - (1 if x else 0)
            if k < 2: k = 2
            o, atts = best_attacks(V, ids, k)
            if not atts: continue
            if x in SETUP and not setup_ok(x, atts): continue
            xv = (SETUP[x][1] * o if x in SETUP else SUPPORT[x][1] * bulk) if x else 0
            val = 0.65 * o + RECOVERY[rec] * bulk + xv + extra
            if ab == "REGENERATOR": val -= 0.1
            mv = atts + [rec] + fixed + ([x] if x else [])
            mv = mv[:4]
            if best is None or val > best["value"]:
                best = {"moves": mv, "value": val, "off": o}
        if best: out["tanque"] = best

    # --- support: 2-3 movimientos de apoyo + 1-2 ataques (los de apoyo que atacan también cuentan)
    sup = []
    for mid, (g, v) in SUPPORT.items():
        if mid not in pool: continue
        if mid in SLEEP_ACC and ab != "NOGUARD": v *= SLEEP_ACC[mid] / 100
        if ab == "MERCILESS" and mid in ("TOXIC", "TOXICSPIKES"): v += 0.15
        if ab == "REGENERATOR" and g == "pivote": v += 0.15
        if ab == "PRANKSTER": v += 0.1
        sup.append((mid, g, v))
    if rec: sup.append((rec, "recup", RECOVERY[rec] * 0.9))
    sup.sort(key=lambda x: -x[2]); sup = sup[:8]
    if len(sup) >= 2:
        best = None
        for ns in (2, 3):
            for combo in itertools.combinations(sup, ns):
                gs = [g for _, g, _ in combo]
                if len(set(gs)) < len(gs): continue
                sv = sum(v for _, _, v in combo)
                chosen = [m for m, _, _ in combo]
                atk_in = [m for m in chosen if moves_db[m]["cat"] < 2]
                k = 4 - ns - (1 if prot and prot[0] == "KINGSSHIELD" else 0)
                o, atts = best_attacks(V, [i for i in ids if i not in chosen], max(k, 1))
                val = sv * (0.6 + 0.4 * bulk) + 0.35 * o
                mv = atts + chosen + ([prot[0]] if prot and prot[0] == "KINGSSHIELD" else [])
                if best is None or val > best["value"]:
                    best = {"moves": mv[:4], "value": val, "off": o, "sup": sv}
        if best: out["support"] = best
    return out


def support_power(f, est, pool, ab):
    """Lo bien que puede hacer de support: movimientos de apoyo disponibles x aguante."""
    hp, at, de, sa, sd, sp = est
    bulk = (np.sqrt(hp * de) + np.sqrt(hp * sd)) / 200.0
    vals, groups = [], set()
    for mid, (g, v) in sorted(SUPPORT.items(), key=lambda x: -x[1][1]):
        if mid in pool and g not in groups:
            groups.add(g); vals.append(v)
    if any(r in pool for r in RECOVERY): vals.append(0.45)
    vals.sort(reverse=True)
    return sum(vals[:4]) * (0.5 + 0.5 * bulk)


def set_notes(moves, ab, moves_db):
    nm = lambda m: MOVES_ES.get(m, moves_db[m]["name"])
    n = []
    drops = [m for m in moves if m in SELF_DROP]
    if ab == "CONTRARY" and drops:
        n.append("Respondón + " + ", ".join(nm(m) for m in drops) + ": cada uso te SUBE las stats (Fuerza Bruta: +1 Atq y +1 Def; Sofoco y Cometa Draco: +2 AtqEsp).")
    if ab == "STANCECHANGE" and "KINGSSHIELD" in moves:
        n.append("Escudo Real: vuelve a forma Escudo y protege; el rival que te toque pierde 2 de Ataque.")
    if ab == "SPEEDBOOST" and any(m in moves for m in ("PROTECT", "DETECT")):
        n.append("Protección el primer turno = +1 Velocidad gratis con Impulso.")
    if ab == "DROUGHT" and any(m in moves for m in SUN_OK):
        n.append("Rayo Solar sin turno de carga gracias al sol de Sequía.")
    if ab == "REGENERATOR" and any(m in ("UTURN", "VOLTSWITCH", "FLIPTURN", "TELEPORT") for m in moves):
        n.append("Pivotar + Regeneración: atacas, cambias y recuperas 1/3 de PS.")
    if ab == "GUTS" and "FACADE" in moves:
        n.append("Agallas + Imagen con Llamasfera: Imagen pega 140 de potencia con Atq x1.5.")
    if "SHELLSMASH" in moves:
        n.append("Rompecoraza: +2 Atq, AtqEsp y Vel a cambio de -1 Def y DefEsp.")
    if ab == "NOGUARD" and any(moves_db[m]["acc"] and moves_db[m]["acc"] < 90 for m in moves):
        n.append("Indefenso: los ataques imprecisos del set aciertan siempre.")
    return n
