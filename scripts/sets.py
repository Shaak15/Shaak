"""Generador del set recomendado (4 movimientos) de cada fusión y su valor.

Idea: la fusión aprende los movimientos de la cabeza y del cuerpo (nivel, MT/tutor y huevo).
Para cada combinación de habilidad:
  1. Se valora cada ataque contra los 18 tipos: potencia x precisión x STAB x habilidad x eficacia x stat.
  2. Se valora cada movimiento de estado según el rol y la habilidad (Danza Espada, Recuperación, Escudo Real…).
  3. Se prueban todas las combinaciones de 2-4 ataques + 0-2 de estado y se queda la de más valor.
"""
import itertools
import numpy as np
from typechart import TYPES, eff
from moves_es import MOVES_ES

EFF = np.array([[eff(a, [d]) for d in TYPES] for a in TYPES])  # [tipo ataque][tipo defensor]
TIDX = {t: i for i, t in enumerate(TYPES)}

# Movimientos que no se recomiendan (carga, recarga, se debilitan, OHKO, daño fijo, tipo variable…)
BANNED = set("""HYPERBEAM GIGAIMPACT BLASTBURN FRENZYPLANT HYDROCANNON ROCKWRECKER ROAROFTIME SKYATTACK SKULLBASH
RAZORWIND FLY DIG DIVE BOUNCE PHANTOMFORCE SHADOWFORCE SKYDROP FOCUSPUNCH EXPLOSION SELFDESTRUCT MEMENTO FINALGAMBIT
FISSURE SHEERCOLD HORNDRILL GUILLOTINE DREAMEATER SNORE FUTURESIGHT DOOMDESIRE BIDE COUNTER MIRRORCOAT METALBURST
BELCH LASTRESORT SYNCHRONOISE NATURALGIFT FLING SPITUP TRUMPCARD HIDDENPOWER FRUSTRATION REVERSAL FLAIL ENDEAVOR
SUPERFANG NIGHTSHADE SEISMICTOSS DRAGONRAGE SONICBOOM PSYWAVE PRESENT ROLLOUT ICEBALL FURYCUTTER UPROAR STRUGGLE RAGE
ECHOEDVOICE ROUND SPITUP STOREDPOWER PUNISHMENT ELECTROBALL GYROBALL MAGNITUDE FALSESWIPE FEINT FAKEOUT SNORE
BIND WRAP FIRESPIN INFESTATION WHIRLPOOL CLAMP SANDTOMB THRASH PETALDANCE OUTRAGE SOLARBEAM SOLARBLADE ERUPTION
WATERSPOUT RETALIATE REVENGE PAYBACK ASSURANCE COVET THIEF PURSUIT SECRETPOWER STRUGGLEBUG""".split())
SUN_OK = {"SOLARBEAM", "SOLARBLADE"}  # sin carga con Sequía
MULTI = {"DOUBLEKICK": 2, "BONEMERANG": 2, "DUALCHOP": 2, "GEARGRIND": 2, "DOUBLEHIT": 2, "BULLETSEED": 3,
         "ROCKBLAST": 3, "ICICLESPEAR": 3, "PINMISSILE": 3, "TAILSLAP": 3, "ARMTHRUST": 3, "FURYSWIPES": 3,
         "FURYATTACK": 3, "DOUBLESLAP": 3, "COMETPUNCH": 3, "SPIKECANNON": 3, "BARRAGE": 3, "TRIPLEKICK": 4,
         "WATERSHURIKEN": 3, "TWINEEDLE": 2}
FIXED_POWER = {"RETURN": 102, "LOWKICK": 60, "GRASSKNOT": 60, "HEAVYSLAM": 60, "HEX": 65, "ACROBATICS": 70,
               "FACADE": 70, "BRINE": 70, "VENOSHOCK": 65, "SMACKDOWN": 50}
# bajan stats del usuario: con Respondón las suben
SELF_DROP = {"SUPERPOWER": 0.85, "CLOSECOMBAT": 0.95, "OVERHEAT": 0.8, "LEAFSTORM": 0.8, "DRACOMETEOR": 0.8,
             "PSYCHOBOOST": 0.8, "FLEURCANNON": 0.8, "HAMMERARM": 0.95, "ICEHAMMER": 0.95, "VCREATE": 0.9}
RECOIL = {"BRAVEBIRD", "DOUBLEEDGE", "FLAREBLITZ", "WOODHAMMER", "WILDCHARGE", "HEADSMASH", "TAKEDOWN",
          "SUBMISSION", "VOLTTACKLE", "HEADCHARGE"}
PIVOT = {"UTURN", "VOLTSWITCH", "FLIPTURN"}
DRAIN = {"DRAINPUNCH", "GIGADRAIN", "HORNLEECH", "LEECHLIFE", "DRAININGKISS", "OBLIVIONWING", "PARABOLICCHARGE"}
SERENE_GOOD = {"AIRSLASH", "IRONHEAD", "ROCKSLIDE", "HEADBUTT", "ZENHEADBUTT", "BODYSLAM", "SCALD", "DARKPULSE",
               "EXTRASENSORY", "DISCHARGE", "BITE", "STOMP", "ICICLECRASH", "WATERFALL", "NEEDLEARM", "ZINGZAP"}

# Movimientos de estado útiles: (tipo, valor base)
SETUP = {"SWORDSDANCE": ("fis", .35), "DRAGONDANCE": ("fis", .45), "BULKUP": ("fis", .25), "CURSE": ("fis", .2),
         "HONECLAWS": ("fis", .2), "COIL": ("fis", .3), "SHIFTGEAR": ("fis", .45), "HOWL": ("fis", .15),
         "NASTYPLOT": ("esp", .35), "CALMMIND": ("esp", .28), "QUIVERDANCE": ("esp", .5), "TAILGLOW": ("esp", .45),
         "GROWTH": ("ambos", .2), "WORKUP": ("ambos", .15), "SHELLSMASH": ("ambos", .55),
         "ROCKPOLISH": ("ambos", .2), "AGILITY": ("ambos", .2), "AUTOTOMIZE": ("ambos", .18)}
RECOVERY = {"RECOVER": .5, "ROOST": .5, "SLACKOFF": .5, "SOFTBOILED": .5, "MILKDRINK": .5, "MOONLIGHT": .42,
            "MORNINGSUN": .42, "SYNTHESIS": .42, "SHOREUP": .5, "WISH": .35, "REST": .2, "STRENGTHSAP": .55}
UTILITY = {"WILLOWISP": .25, "TOXIC": .2, "THUNDERWAVE": .16, "STEALTHROCK": .2, "SPIKES": .15, "TOXICSPIKES": .12,
           "TAUNT": .1, "LEECHSEED": .15, "SUBSTITUTE": .08, "ROAR": .08, "WHIRLWIND": .08, "HAZE": .08,
           "DEFOG": .08, "PROTECT": .06, "DETECT": .06, "KINGSSHIELD": .1, "BANEFULBUNKER": .2,
           "SPORE": .35, "SLEEPPOWDER": .25, "HYPNOSIS": .18, "SING": .15, "GRASSWHISTLE": .15, "LOVELYKISS": .2,
           "YAWN": .15, "GLARE": .2, "STUNSPORE": .15, "NUZZLE": 0, "PAINSPLIT": .2, "TRICKROOM": .1,
           "LIGHTSCREEN": .08, "REFLECT": .08, "ENCORE": .12, "DESTINYBOND": .1}
SLEEP_ACC = {"SPORE": 100, "SLEEPPOWDER": 75, "HYPNOSIS": 60, "SING": 55, "GRASSWHISTLE": 55, "LOVELYKISS": 75, "YAWN": 100}


def offense_stats(f, ab, est):
    hp, at, de, sa, sd, sp = f["stats"]
    if ab == "STANCECHANGE":
        return max(at, de), max(sa, sd)
    if ab == "SHIELDSDOWN":
        return est[1], est[3]
    return at, sa


def attack_vector(mid, m, f, ab, atk, spa, types, speed):
    """Valor de un ataque contra cada uno de los 18 tipos (o None si no se recomienda)."""
    if m["cat"] == 2:
        return None, 1.0
    if mid in BANNED and not (mid in SUN_OK and ab == "DROUGHT"):
        return None, 1.0
    p = FIXED_POWER.get(mid, m["power"])
    if p <= 1:
        return None, 1.0
    p *= MULTI.get(mid, 1)
    acc = 1.0 if (m["acc"] == 0 or ab == "NOGUARD") else m["acc"] / 100
    t = m["type"]
    stab = 1.0
    if ab == "PROTEAN" or t in types:
        stab = 2.0 if ab == "ADAPTABILITY" else 1.5
    mod = 1.0
    phys = m["cat"] == 0
    flags = m.get("flags", "")
    if ab == "HUSTLE" and phys: mod *= 1.5; acc *= 0.8
    if ab == "IRONFIST" and "j" in flags: mod *= 1.2
    if ab == "STRONGJAW" and "i" in flags: mod *= 1.5
    if ab == "GUTS" and phys: mod *= 1.3   # con Llamasfera; la quemadura resta PS cada turno
    if ab == "GUTS" and mid == "FACADE": p = 140
    if ab == "DROUGHT":
        if t == "FIRE": mod *= 1.5
        if t == "WATER": mod *= 0.5
    if ab == "ANALYTIC" and speed < 70: mod *= 1.15
    if ab == "DOWNLOAD": mod *= 1.1
    if ab == "SERENEGRACE" and mid in SERENE_GOOD: mod *= 1.12
    if ab in ("SNIPER", "SUPERLUCK") and "h" in flags: mod *= 1.08
    if mid in SELF_DROP:
        mod *= 1.6 if ab == "CONTRARY" else SELF_DROP[mid]
    if mid in RECOIL and ab != "ROCKHEAD": mod *= 0.92
    if mid in DRAIN: mod *= 1.08
    if m["prio"] > 0: mod *= 1.05
    stat = atk if phys else spa
    base = p * acc * stab * mod * stat / 10000.0
    return EFF[TIDX[t]] * base, base


def status_value(mid, ab, role, bulk, est, has_phys, has_spec, speed):
    """(grupo, valor) de un movimiento de estado para esta fusión. El valor de setup es una fracción del daño."""
    if mid in SETUP:
        kind, v = SETUP[mid]
        if kind == "fis" and not has_phys: return None
        if kind == "esp" and not has_spec: return None
        if mid == "CURSE" and speed > 60: v *= 0.5
        if mid in ("ROCKPOLISH", "AGILITY", "AUTOTOMIZE") and not (55 <= speed <= 100): return None
        if mid == "GROWTH" and ab == "DROUGHT": v = .35
        if mid == "CALMMIND" and role == "muro": v += .08
        if ab == "SPEEDBOOST" and mid in ("DRAGONDANCE", "ROCKPOLISH", "AGILITY"): v *= 0.7
        return ("setup", v)
    if mid in RECOVERY:
        v = RECOVERY[mid] * bulk * (1.4 if role == "muro" else 0.8)
        if ab == "REGENERATOR": v *= 0.8
        return ("recup", v)
    if mid in UTILITY:
        v = UTILITY[mid]
        if mid == "KINGSSHIELD" and ab == "STANCECHANGE": v = 0.85
        if mid in ("PROTECT", "DETECT") and ab == "SPEEDBOOST": v = 0.5
        if mid in ("PROTECT", "DETECT", "BANEFULBUNKER") and ab == "MERCILESS": v += 0.1
        if mid in ("TOXIC", "TOXICSPIKES") and ab == "MERCILESS": v += 0.2
        if mid in SLEEP_ACC: v *= (1.0 if ab == "NOGUARD" else SLEEP_ACC[mid] / 100)
        if mid in ("THUNDERWAVE", "TOXIC", "HYPNOSIS", "WILLOWISP") and ab == "NOGUARD": v += 0.05
        if role == "muro" and mid in ("WILLOWISP", "TOXIC", "STEALTHROCK", "LEECHSEED", "PAINSPLIT"): v *= 1.3
        if mid == "TRICKROOM" and speed < 50: v = .25
        return ("prot" if mid in ("PROTECT", "DETECT", "KINGSSHIELD", "BANEFULBUNKER") else "util", v)
    return None


_COMBOS = {}
def combos(n, k):
    key = (n, k)
    if key not in _COMBOS:
        _COMBOS[key] = np.array(list(itertools.combinations(range(n), k)), dtype=int) if n >= k else np.zeros((0, k), int)
    return _COMBOS[key]


def best_set(f, ab, est, role, moves_db, movepool):
    hp, at, de, sa, sd, sp = est
    atk, spa = offense_stats(f, ab, est)
    speed = est[5]
    bulk = (np.sqrt(hp * de) + np.sqrt(hp * sd)) / 200.0
    vecs, ids = [], []
    for mid in movepool:
        m = moves_db.get(mid)
        if not m: continue
        v, base = attack_vector(mid, m, f, ab, atk, spa, f["types"], speed)
        if v is not None:
            vecs.append(v); ids.append(mid)
    if not vecs:
        return {"moves": [], "value": 0.0, "off": 0.0}
    V = np.array(vecs)
    # podar: los 2 mejores por tipo y los 12 mejores en total (por valor medio)
    meanv = V.mean(axis=1)
    keep, per_type = [], {}
    for i in np.argsort(-meanv):
        t = moves_db[ids[i]]["type"]
        if per_type.get(t, 0) >= 2: continue
        per_type[t] = per_type.get(t, 0) + 1
        keep.append(i)
        if len(keep) >= 12: break
    V = V[keep]; ids = [ids[i] for i in keep]
    has_phys = any(moves_db[i]["cat"] == 0 for i in ids[:6])
    has_spec = any(moves_db[i]["cat"] == 1 for i in ids[:6])
    # estado
    st = []
    for mid in movepool:
        r = status_value(mid, ab, role, bulk, est, has_phys, has_spec, speed)
        if r: st.append((mid, r[0], r[1]))
    st.sort(key=lambda x: -x[2]); st = st[:6]
    # mejor conjunto de ataques para k = 2..4
    best_att = {}
    for k in (2, 3, 4):
        C = combos(len(ids), min(k, len(ids)))
        if len(C) == 0: continue
        scores = V[C].max(axis=1).mean(axis=1)
        j = int(np.argmax(scores))
        best_att[k] = (float(scores[j]), [ids[i] for i in C[j]])
    if not best_att:
        return {"moves": [], "value": 0.0, "off": 0.0}
    kmax = max(best_att)
    best = None
    for ns in (0, 1, 2):
        k = 4 - ns
        if k not in best_att:
            k = kmax
        off, atts = best_att[k]
        for sts in itertools.combinations(st, ns):
            groups = [g for _, g, _ in sts]
            if groups.count("setup") > 1 or groups.count("recup") > 1 or groups.count("prot") > 1: continue
            nphys = sum(1 for a in atts if moves_db[a]["cat"] == 0)
            nspec = len(atts) - nphys
            bad = False
            for mid, g, v in sts:
                if g == "setup":
                    kind = SETUP[mid][0]
                    if (kind == "fis" and nphys < 2) or (kind == "esp" and nspec < 2): bad = True
            if bad: continue
            val = off
            for mid, g, v in sts:
                val += v * off if g == "setup" else v
            if ab == "REGENERATOR" and any(a in PIVOT for a in atts): val += 0.15
            if ab == "CONTRARY" and any(a in SELF_DROP for a in atts): val += 0.1 * off
            if best is None or val > best["value"]:
                best = {"moves": list(atts) + [m for m, _, _ in sts], "value": val, "off": off}
    return best


def set_notes(moves, ab, moves_db):
    n = []
    drops = [m for m in moves if m in SELF_DROP]
    if ab == "CONTRARY" and drops:
        n.append("Respondón + " + ", ".join(MOVES_ES.get(m, moves_db[m]["name"]) for m in drops) + ": cada uso te SUBE las stats (Fuerza Bruta: +1 Atq y +1 Def; Sofoco y Cometa Draco: +2 AtqEsp).")
    if ab == "STANCECHANGE" and "KINGSSHIELD" in moves:
        n.append("Escudo Real: vuelve a forma Escudo y protege; el rival que te toque pierde 2 de Ataque.")
    if ab == "SPEEDBOOST" and any(m in moves for m in ("PROTECT", "DETECT")):
        n.append("Protección el primer turno = +1 Velocidad gratis con Impulso.")
    if ab == "DROUGHT" and any(m in moves for m in SUN_OK):
        n.append("Rayo Solar sin turno de carga gracias al sol de Sequía.")
    if ab == "REGENERATOR" and any(m in PIVOT for m in moves):
        n.append("Ida y Vuelta / Voltiocambio + Regeneración: atacas, cambias y recuperas 1/3 de PS.")
    if ab == "GUTS" and "FACADE" in moves:
        n.append("Agallas + Imagen con Llamasfera: Imagen pega 140 de potencia con Atq x1.5.")
    if "SHELLSMASH" in moves:
        n.append("Rompecoraza: +2 Atq, AtqEsp y Vel a cambio de -1 Def y DefEsp. Úsalo cuando el rival no pueda tumbarte.")
    if ab == "NOGUARD" and any(moves_db[m]["acc"] and moves_db[m]["acc"] < 90 for m in moves):
        n.append("Indefenso: los ataques imprecisos del set aciertan siempre.")
    return n
