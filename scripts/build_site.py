"""Genera site/index.html metiendo los datos dentro de la plantilla."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "../data/fusions.json")))
D["sprites"] = json.load(open(os.path.join(HERE, "../data/sprites.json")))
tpl = open(os.path.join(HERE, "../site/template.html")).read()
blob = json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
open(os.path.join(HERE, "../site/index.html"), "w").write(tpl.replace("/*__DATA__*/", blob))
print(os.path.getsize(os.path.join(HERE, "../site/index.html")))
