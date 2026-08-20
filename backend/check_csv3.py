import csv

rules = list(csv.DictReader(open("apps/guardrails/data/interactions_v1.csv", encoding="utf-8")))
for i, r in enumerate(rules):
    for k, v in r.items():
        if k is None:
            print("ROW", i, "EXTRA PHANTOM COLUMN:", repr(v))
    for field, limit in [("context_tag", 32), ("severity", 16), ("evidence", 16), ("interaction_type", 64), ("dose_threshold", 64), ("direction", 16)]:
        v = r.get(field, "")
        if len(v or "") > limit:
            print("ROW", i, field, "LEN", len(v or ""), repr(v))