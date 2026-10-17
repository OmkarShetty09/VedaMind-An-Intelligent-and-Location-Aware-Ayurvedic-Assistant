from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load the guardrail data (herb/drug aliases, interaction rules) and the optional demo user."

    def handle(self, *args, **options):
        import csv
        import hashlib
        from pathlib import Path

        from apps.guardrails.alias_graph import reset_graph_cache
        from apps.guardrails.models import DrugAlias, HerbAlias, InteractionRule, RuleVersion
        from apps.users.models import User

        # Resolve from the app package, so the command works from any working directory.
        data_dir = Path(__file__).resolve().parents[3] / "guardrails" / "data"
        alias_path = data_dir / "herb_aliases_v1.csv"
        drug_path = data_dir / "drug_aliases_v1.csv"
        rules_path = data_dir / "interactions_v1.csv"

        with open(alias_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                HerbAlias.objects.update_or_create(
                    canonical_herb=row["canonical_herb"], alias=row["alias"],
                    defaults={"language": row["language"], "confidence": float(row.get("confidence") or 1.0)},
                )

        with open(drug_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                DrugAlias.objects.update_or_create(
                    alias=row["alias"].strip().lower(),
                    defaults={
                        "canonical": row["canonical"].strip().lower(),
                        "classes": [c.strip().lower() for c in row["classes"].split("|") if c.strip()],
                    },
                )

        # The rule-set version is pinned to the exact CSV content it was loaded from.
        digest = hashlib.sha256(rules_path.read_bytes()).hexdigest()
        version, _ = RuleVersion.objects.get_or_create(
            sha256=digest,
            defaults={"version": f"csv-{digest[:12]}", "steward": settings.GUARDRAIL_RULE_STEWARD},
        )
        with open(rules_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                InteractionRule.objects.update_or_create(
                    herb_a=row["herb_a"], herb_b_or_drug=row["herb_b_or_drug"],
                    context_tag=row["context_tag"] or "",
                    defaults={
                        "direction": row["direction"],
                        "interaction_type": row["interaction_type"],
                        "mechanism": row["mechanism"],
                        "recommendation": row["recommendation"],
                        "severity": row["severity"].upper(),
                        "evidence": row["evidence"].upper(),
                        "dose_threshold": row["dose_threshold"],
                        "source_uri": row["source_uri"],
                        "rule_version": version,
                    },
                )
        reset_graph_cache()

        email = settings.DEMO_USER_EMAIL.strip().lower()
        if email and settings.DEMO_USER_PASSWORD:
            if not User.objects.filter(email__iexact=email).exists():
                demo = User.objects.create_user(email=email, name="Demo User", password=settings.DEMO_USER_PASSWORD)
                demo.consent_accepted = True
                demo.save(update_fields=["consent_accepted"])
                self.stdout.write(f"Created demo user {email}")
        else:
            self.stdout.write("DEMO_USER_EMAIL / DEMO_USER_PASSWORD not set; no demo user created.")
        self.stdout.write(self.style.SUCCESS("Seeded guardrail data."))
