import yaml, re
from pathlib import Path

def load_rules(path=Path(__file__).with_name("rules.yml")):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    cats = data["categories"]
    compiled = []
    for cat, spec in cats.items():
        for t in spec["terms"]:
            phrase = t["phrase"]
            # word-boundary regex, case-insensitive; tweak per term as needed
            rx = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
            compiled.append({
                "category": cat,
                "weight": spec.get("weight", 1.0),
                "rx": rx,
                "phrase": phrase,
                "suggest": t.get("suggest"),
                "note": t.get("note","")
            })
    return compiled
