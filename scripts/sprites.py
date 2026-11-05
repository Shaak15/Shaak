"""Construye un atlas con el sprite de cada fusión (custom si existe, si no el autogenerado)
y el sprite base de cada Pokémon.
Uso: python3 -I sprites.py <ruta infinitefusion-e18 (main)> <carpeta con los autogen de develop-6.6>
Los sprites custom salen de la rama main (Pokémon hasta el nº 501); los autogenerados, de develop-6.6."""
import json, os, sys
from PIL import Image
ROOT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "../data/fusions.json")))
SP = D["meta"]["species"]
S = 96
CUSTOM = os.path.join(ROOT, "Graphics/CustomBattlers/spritesheets/spritesheets_custom")
AUTO = sys.argv[2]
OLDMAX = 501
BASE = os.path.join(ROOT, "Graphics/CustomBattlers/spritesheets/spritesheets_base")
cache = {}
def sheet(p):
    if p not in cache:
        cache[p] = Image.open(p).convert("RGBA") if os.path.exists(p) else None
    return cache[p]
def cell(img, idx, cols):
    if img is None: return None
    x, y = (idx % cols) * S, (idx // cols) * S
    if y + S > img.height: return None
    c = img.crop((x, y, x + S, y + S))
    return c if c.getbbox() else None

keys, tiles, kinds = [], [], {}
for k, s in SP.items():
    d = s['dex']
    t = cell(sheet(f"{BASE}/{d}.png"), 0, 10) if d <= OLDMAX else cell(sheet(f"{AUTO}/{d}.png"), d, 10)
    keys.append(k); tiles.append(t)
for f in D["fusions"]:
    h, b = SP[f["head"]]["dex"], SP[f["body"]]["dex"]
    t = cell(sheet(f"{CUSTOM}/{h}/{h}.png"), b, 20) if (h <= OLDMAX and b <= OLDMAX) else None; kind = "custom"
    if t is None:
        t = cell(sheet(f"{AUTO}/{h}.png"), b, 10); kind = "auto"
    if t is None: kind = "none"
    keys.append(f["head"] + "|" + f["body"]); tiles.append(t); kinds[keys[-1]] = kind

COLS = 30
rows = (len(tiles) + COLS - 1) // COLS
atlas = Image.new("RGBA", (COLS * S, rows * S), (0, 0, 0, 0))
index = {}
for i, (k, t) in enumerate(zip(keys, tiles)):
    if t is None: continue
    atlas.paste(t, ((i % COLS) * S, (i // COLS) * S))
    index[k] = i
out = os.path.join(HERE, "../site/sprites.webp")
atlas.save(out, "WEBP", lossless=True, method=6)
json.dump({"cols": COLS, "size": S, "index": index, "kind": kinds}, open(os.path.join(HERE, "../data/sprites.json"), "w"))
from collections import Counter
print(atlas.size, os.path.getsize(out), Counter(kinds.values()))
