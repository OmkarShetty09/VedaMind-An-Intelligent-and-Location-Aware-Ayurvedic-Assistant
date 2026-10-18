"""'What not to take it with': cautions listed under every answer, from the seeded rule set."""

import pytest
from django.core.management import call_command

from apps.guardrails.cautions import GENERAL_NOTE, cautions_for, herbs_mentioned

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _seed():
    call_command("seed_demo_data")


def test_lists_modern_medicines_for_herbs_in_the_answer_without_declared_meds():
    result = cautions_for("Is haldi good for joints?\nTurmeric (haridra) is traditionally used [S1].")
    assert result["herbs"] == ["turmeric"]
    avoid = {i["avoid_with"]: i for i in result["items"]}
    assert {"Warfarin", "NSAIDs"} <= set(avoid)
    assert avoid["Warfarin"]["kind"] == "medicine"
    assert avoid["Warfarin"]["source_uri"].startswith("https://")
    assert avoid["NSAIDs"]["examples"]  # e.g. ibuprofen - a modern-medicine example for the class
    assert not any(i["applies_to_you"] for i in result["items"])
    assert result["general"] == GENERAL_NOTE and result["note"] == ""


def test_flags_the_users_own_medicine_and_conditions():
    result = cautions_for("Ashwagandha helps sleep.", medications=["Thyronorm 50 mcg"])
    by_target = {i["avoid_with"]: i for i in result["items"]}
    assert by_target["Pregnancy or breastfeeding"]["kind"] == "condition"
    assert result["items"][0]["applies_to_you"] is True  # the user's own interaction is listed first
    assert result["items"][0]["avoid_with"] == "Levothyroxine"


def test_no_herbs_or_no_rules_still_gives_the_general_warning():
    assert cautions_for("Wake before sunrise and walk.")["items"] == []
    assert cautions_for("Wake before sunrise and walk.")["general"] == GENERAL_NOTE
    assert herbs_mentioned("Sweetness and gingerly walking") == []
