"""Entity extraction + the /guardrails/check endpoint against the seeded rule set."""

import csv
from pathlib import Path

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.guardrails.alias_graph import AliasGraph
from apps.guardrails.drug_lexicon import DrugLexicon
from apps.guardrails.entity_extraction import extract_entities
from apps.guardrails.models import DrugAlias, HerbAlias
from apps.guardrails.rules_engine import _dose_mg, evaluate
from apps.guardrails.tests.test_rules_engine import rule
from apps.guardrails.views_utils import context_flags

GRAPH = AliasGraph(
    [
        HerbAlias(canonical_herb="turmeric", alias="haldi", confidence=1.0),
        HerbAlias(canonical_herb="ashwagandha", alias="winter cherry", confidence=1.0),
        HerbAlias(canonical_herb="triphala", alias="haritaki trio", confidence=1.0),
    ]
)

# The shipped drug vocabulary, without a database (the DB copy is seeded from this same file).
with open(Path(__file__).resolve().parents[1] / "data" / "drug_aliases_v1.csv", encoding="utf-8") as _fh:
    LEXICON = DrugLexicon(
        [
            DrugAlias(alias=r["alias"], canonical=r["canonical"], classes=[c for c in r["classes"].split("|") if c])
            for r in csv.DictReader(_fh)
        ]
    )


def extract(text, **kwargs):
    return extract_entities(text, GRAPH, lexicon=LEXICON, **kwargs)


def names(entities):
    return sorted(e.canonical for e in entities)


def test_ordinary_words_are_not_drugs():
    # Previously every unknown 4+ letter word was a "drug", so this became a blocked novel pair.
    result = extract("Can I take turmeric for joint pain and better digestion?")
    assert names(result.herbs) == ["turmeric"]
    assert result.drugs == []


def test_known_drugs_brands_and_classes_are_drugs():
    result = extract("I take Coumadin, metformin and some sedatives")
    assert names(result.drugs) == ["metformin", "sedatives", "warfarin"]


def test_unknown_drug_with_inn_stem_still_counts_as_drug():
    result = extract("haldi with atorvastatin?")
    assert names(result.herbs) == ["turmeric"]
    assert names(result.drugs) == ["atorvastatin"]


def test_april_is_not_a_drug():
    assert extract("Is triphala good in April?").drugs == []


def test_multi_word_alias_is_resolved():
    assert names(extract("Tell me about winter cherry").herbs) == ["ashwagandha"]


def test_declared_medications_are_drugs_even_if_unrecognised():
    result = extract("Should I take turmeric?", medications=["Thyronorm 50 mcg", "Dolo 650"])
    assert names(result.drugs) == ["dolo", "levothyroxine"]


def test_drug_classes_come_from_the_lexicon():
    assert LEXICON.classes_for("hydrochlorothiazide") == {"thiazide_diuretics", "diuretics"}
    rules = [rule("licorice", "thiazide_diuretics", severity="HIGH", evidence="VALIDATED")]
    result = evaluate(["licorice"], ["hydrochlorothiazide"], rules=rules, drug_classes=LEXICON.class_map())
    assert result.overall == "block"  # a rule written for a class matches its member drug


def test_reason_code_reports_the_worst_match():
    result = evaluate(
        ["ashwagandha"],
        ["levothyroxine", "donepezil"],
        rules=[
            rule("ashwagandha", "levothyroxine", severity="HIGH", evidence="VALIDATED"),
            rule("ashwagandha", "donepezil", severity="LOW", evidence="THEORETICAL"),
        ],
    )
    assert result.overall == "block"
    assert result.reason_code == "interaction_high_or_severe"


def test_dose_units_are_normalised_to_mg():
    assert _dose_mg(">4g") == 4000
    assert _dose_mg("500 mg") == 500
    assert _dose_mg("250mcg") == 0.25
    # culinary 1 g ginger is under the 4 g therapeutic threshold, 5 g is over it
    ginger = [rule("ginger", "warfarin", severity="MODERATE", evidence="PROBABLE", dose_threshold=">4g")]
    assert not evaluate(["ginger"], ["warfarin"], doses={"ginger": "1 g"}, rules=ginger).matches
    assert evaluate(["ginger"], ["warfarin"], doses={"ginger": "5 g"}, rules=ginger).matches


def test_context_flags_are_derived_from_conditions():
    flags = context_flags({"conditions": ["Pregnant (2nd trimester)", "chronic kidney disease", "Type 2 Diabetes"]})
    assert flags == {"pregnancy": True, "pediatric": False, "renal": True, "diabetes": True}


@pytest.mark.django_db
class TestCheckEndpoint:
    @pytest.fixture(autouse=True)
    def _seed(self):
        call_command("seed_demo_data")

    def check(self, text, **context):
        from django.conf import settings

        client = APIClient()
        response = client.post(
            "/api/v1/guardrails/check",
            {"text": text, "context": context},
            format="json",
            HTTP_X_RAG_ADMIN_TOKEN=settings.RAG_ADMIN_TOKEN,
        )
        assert response.status_code == 200, response.content
        return response.json()

    @pytest.mark.parametrize(
        ("text", "decision"),
        [
            ("Can I take turmeric with warfarin?", "block"),
            ("Is licorice ok with hydrochlorothiazide?", "block"),
            ("Tell me about brahmi and donepezil", "caution"),
            ("Can I take turmeric for joint pain?", "pass"),
            ("What herbs help with digestion?", "pass"),
            ("What should my morning routine look like?", "pass"),
        ],
    )
    def test_decisions(self, text, decision):
        assert self.check(text)["decision"] == decision

    def test_profile_medications_are_checked(self):
        body = self.check("Should I take turmeric?", medications=["warfarin 5 mg"])
        assert body["decision"] == "block"
        assert body["severity"] == "high"
        assert body["matches"][0]["pair"] == "turmeric <-> warfarin"

    def test_pregnancy_condition_applies_context_rule(self):
        assert self.check("Is ashwagandha good for sleep?", conditions=["pregnancy"])["decision"] == "block"

    def test_rag_service_token_is_not_throttled_as_anonymous(self, settings):
        from rest_framework.throttling import SimpleRateThrottle

        rates = dict(SimpleRateThrottle.THROTTLE_RATES, anon="2/min", guardrail="2/min")
        original = SimpleRateThrottle.THROTTLE_RATES
        SimpleRateThrottle.THROTTLE_RATES = rates
        try:
            assert all(self.check("what is triphala")["decision"] == "pass" for _ in range(5))
        finally:
            SimpleRateThrottle.THROTTLE_RATES = original

    def test_rules_cite_real_sources(self):
        from apps.guardrails.models import InteractionRule

        uris = list(InteractionRule.objects.values_list("source_uri", flat=True))
        assert uris and all(u.startswith("https://") and "example.org" not in u for u in uris)

    def test_admin_edit_to_drug_vocabulary_applies_without_restart(self):
        assert self.check("I take zzdrugone and turmeric")["decision"] == "pass"
        DrugAlias.objects.create(alias="zzdrugone", canonical="warfarin", classes=[])
        assert self.check("I take zzdrugone and turmeric")["decision"] == "block"

    def test_requires_jwt_or_service_token(self):
        response = APIClient().post("/api/v1/guardrails/check", {"text": "turmeric"}, format="json")
        assert response.status_code in (401, 403)
