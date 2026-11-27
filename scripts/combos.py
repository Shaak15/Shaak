"""Combos que usa la comunidad de Infinite Fusion, buscados en la caja.

Cada combo dice qué habilidad y qué movimientos hacen falta. Para cada fusión que lo cumple
se guarda la habilidad que hay que llevar y una nota; la página filtra por lo que tengas en la caja.
"""
from typechart import TYPES

COMBOS = [
 {"id": "parafinch", "title": "Parafinch: Dicha + Tajo Aéreo + Onda Trueno",
  "desc": "Con Dicha, Tajo Aéreo hace retroceder el 60% de las veces. Si antes paralizas al rival con Onda Trueno, casi nunca llega a atacar. Mejor si la fusión es de tipo Volador (Tajo Aéreo con STAB) y rápida.",
  "ab": ["SERENEGRACE"], "all": ["AIRSLASH"], "any": ["THUNDERWAVE", "NUZZLE", "GLARE"]},
 {"id": "veleta", "title": "Veleta + Protección + Sustituto",
  "desc": "Prohibido en competitivo. Cada turno sube +2 un stat al azar (también la Evasión) y baja otro -1. Protección y Sustituto dan turnos gratis para acumular. Cuanto más aguante, mejor.",
  "ab": ["MOODY"], "all": ["PROTECT", "SUBSTITUTE"], "sort": "bulk"},
 {"id": "tactico", "title": "Cambio Táctico con mucha Defensa",
  "desc": "En Infinite Fusion, al atacar se intercambian Atq↔Def y AtqEsp↔DefEsp. Una fusión con Def y DefEsp enormes ataca con esos números, y Escudo Real la devuelve a modo defensa.",
  "ab": ["STANCECHANGE"], "all": ["KINGSSHIELD"], "cond": "tactico"},
 {"id": "respondon", "title": "Respondón + ataques que bajan stats",
  "desc": "Con Respondón, Fuerza Bruta sube Ataque y Defensa, Machada sube Velocidad, y Sofoco o Cometa Draco suben +2 el AtqEsp. Cada golpe te hace más fuerte.",
  "ab": ["CONTRARY"], "any": ["SUPERPOWER", "HAMMERARM", "OVERHEAT", "DRACOMETEOR", "LEAFSTORM", "CLOSECOMBAT"]},
 {"id": "impulso", "title": "Impulso + Protección",
  "desc": "Protección el primer turno = +1 Velocidad gratis. Con Danza Espada o Danza Dragón detrás, barre equipos enteros.",
  "ab": ["SPEEDBOOST"], "all": ["PROTECT"]},
 {"id": "rompecoraza", "title": "Rompecoraza",
  "desc": "+2 Ataque, AtqEsp y Velocidad de golpe a cambio de -1 Def y DefEsp. Con Robustez o Escudo Limitado aguanta el turno de preparación.",
  "ab": None, "all": ["SHELLSMASH"]},
 {"id": "agallas", "title": "Agallas + Imagen + Llamasfera",
  "desc": "La Llamasfera te quema a propósito: Agallas sube el Ataque x1.5 e Imagen pasa a 140 de potencia. La quemadura no te baja el Ataque con Agallas.",
  "ab": ["GUTS"], "all": ["FACADE"]},
 {"id": "experto", "title": "Experto + Sorpresa / ataques débiles",
  "desc": "Experto multiplica x1.5 los ataques de 60 o menos. Sorpresa (siempre hace retroceder el primer turno) pasa a 60 de potencia efectiva y Doble Golpe a 105.",
  "ab": ["TECHNICIAN"], "any": ["FAKEOUT", "DOUBLEHIT", "BULLETPUNCH", "AERIALACE", "ROCKBLAST"]},
 {"id": "espacio", "title": "Espacio Raro: lentos que pegan fuerte",
  "desc": "Con Espacio Raro, los más lentos atacan primero durante 5 turnos. Estas fusiones son lentas (Vel ≤ 55) pero pegan mucho. Te hace falta un setter: Chandelure, Dusclops, Necrozma, Carbink, Trevenant, Mismagius, Alakazam, Kecleon, Porygon o Delphox aprenden Espacio Raro.",
  "ab": None, "cond": "espacio"},
 {"id": "sindebil", "title": "Sin ninguna debilidad",
  "desc": "Fusiones a las que ningún tipo les hace daño súper eficaz, normalmente por una habilidad (Levitación, Absorbe…) que tapa la única debilidad de sus tipos.",
  "ab": None, "cond": "sindebil"},
]


def find(fusions, species):
    out = []
    for c in COMBOS:
        hits = []
        for f in fusions:
            pool = set(species[f["head"]]["moves"]) | set(species[f["body"]]["moves"])
            if any(m not in pool for m in c.get("all", [])): continue
            if c.get("any") and not any(m in pool for m in c["any"]): continue
            entries = [a for a in f["abilities"] if (c["ab"] is None or a["id"] in c["ab"]) and a["id"] != "TRUANT"]
            if not entries: continue
            e = entries[0]                      # la mejor habilidad que cumple
            hp, at, de, sa, sd, sp = f["stats"]
            if c.get("cond") == "tactico" and max(de - at, sd - sa) < 30: continue
            if c.get("cond") == "espacio" and not (sp <= 55 and max(at, sa) >= 110): continue
            if c.get("cond") == "sindebil":
                e = next((a for a in entries if max(a["mult"]) < 2), None)
                if e is None: continue
            key = (hp * (de + sd)) ** 0.5 if c.get("sort") == "bulk" else e["score"]
            if c["id"] == "parafinch":   # Tajo Aéreo con STAB y ser rápido es lo que hace funcionar el combo
                key += (12 if "FLYING" in f["types"] else 0) + sp / 8
            used = [m for m in c.get("all", []) + c.get("any", []) if m in pool]
            hits.append({"k": f["head"] + "|" + f["body"], "ab": e["id"], "uses": used, "key": round(key, 2)})
        hits.sort(key=lambda h: -h["key"])
        out.append({k: c[k] for k in ("id", "title", "desc")} | {"hits": hits[:40]})
    return out
