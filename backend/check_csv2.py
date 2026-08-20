import csv

rules = list(csv.DictReader(open("apps/guardrails/data/interactions_v1.csv", encoding="utf-8")))
for i, r in enumerate(rules):
    if len(r.get("severity", "") or "") > 16:
        print("ROW INDEX", i)
        for k, v in r.items():
            print(f"  {k} = {v!r}")
    if (r.get("severity", "") or "") not in ("NONE", "LOW", "MODERATE", "HIGH", "SEVERE"):
        print("ROW", i, "severity not in choices:", repr(r.get("severity")))