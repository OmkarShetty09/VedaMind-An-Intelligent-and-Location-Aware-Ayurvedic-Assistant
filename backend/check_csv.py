import csv

path = "apps/guardrails/data/herb_aliases_v1.csv"
rows = list(csv.DictReader(open(path, encoding="utf-8")))
print("rows", len(rows))
bad = [r for r in rows if len(r.get("language", "") or "") > 16]
for b in bad[:10]:
    print("BAD lang", repr(b.get("language")), len(b.get("language") or ""))
print("headers", list(rows[0].keys()) if rows else "none")

rules = list(csv.DictReader(open("apps/guardrails/data/interactions_v1.csv", encoding="utf-8")))
print("rules rows", len(rules))
print("rules headers", list(rules[0].keys()) if rules else "none")
badsev = [r for r in rules if len(r.get("severity", "") or "") > 16]
badev = [r for r in rules if len(r.get("evidence", "") or "") > 16]
badint = [r for r in rules if len(r.get("interaction_type", "") or "") > 64]
baddir = [r for r in rules if r.get("direction", "") not in ("herb_drug", "herb_herb")]
print("bad severity", len(badsev), [b.get("severity") for b in badsev[:5]])
print("bad evidence", len(badev), [b.get("evidence") for b in badev[:5]])
print("bad interaction_type>64", len(badint), [b.get("interaction_type") for b in badint[:5]])
print("bad direction", len(baddir), [b.get("direction") for b in baddir[:5]])