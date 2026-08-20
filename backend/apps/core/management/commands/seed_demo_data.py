from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed demo users, dosha profiles and sample guardrail data."

    def handle(self, *args, **options):
        import csv
        import hashlib

        from apps.guardrails.models import HerbAlias, InteractionRule, RuleVersion
        from apps.users.models import User

        alias_path = "apps/guardrails/data/herb_aliases_v1.csv"
        rules_path = "apps/guardrails/data/interactions_v1.csv"
        with open(alias_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                HerbAlias.objects.get_or_create(
                    canonical_herb=row["canonical_herb"], alias=row["alias"],
                    defaults={"language": row["language"], "confidence": float(row.get("confidence") or 1.0)},
                )

        version, _ = RuleVersion.objects.get_or_create(
            version="1.0.0",
            defaults={"sha256": hashlib.sha256(b"seed").hexdigest(), "steward": "clinical-steward@vedamind"},
        )
        with open(rules_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                InteractionRule.objects.get_or_create(
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

        demo = User.objects.filter(email="demo@vedamind.local").first()
        if demo is None:
            demo = User.objects.create_user(
                email="demo@vedamind.local", name="Demo User", password="demo-pass-123!"
            )
            demo.consent_accepted = True
            demo.save(update_fields=["consent_accepted"])
        self.stdout.write(self.style.SUCCESS("Seeded demo data."))
