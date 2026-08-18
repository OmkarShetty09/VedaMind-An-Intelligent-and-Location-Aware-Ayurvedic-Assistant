from datetime import time


def build_activities(ctx):
    """Main meal at agni peak (midday), light dinner, seasonal diet notes."""
    if ctx.season == "varsha":
        dinner_note = "In the monsoon, digestion is weaker: prefer light, warm, well-spiced food."
    elif ctx.season == "grishma":
        dinner_note = "In peak summer, favor cool, light meals and hydration."
    else:
        dinner_note = "Prefer warm, freshly-cooked meals and a 3-hour gap before sleep."

    return [
        {
            "time_of_day": "midday",
            "start": time(12, 0),
            "end": time(13, 30),
            "title": "Main meal",
            "description": (
                "Eat your largest meal now, when digestive fire (agni) is strongest. "
                "Eat mindfully, until comfortably full."
            ),
            "reasons": ["Midday is the classical peak of agni."],
            "citations": [{"source": "Charaka Samhita", "ref": "Vimanasthana 1"}],
            "dosha_target": "pitta",
            "order": 10,
        },
        {
            "time_of_day": "evening",
            "start": time(19, 0),
            "end": time(20, 0),
            "title": "Light dinner",
            "description": dinner_note,
            "reasons": ["A light evening meal supports restful sleep."],
            "citations": [{"source": "Ashtanga Hridaya", "ref": "Sutrasthana 2, vv. 12-16"}],
            "dosha_target": "kapha",
            "order": 11,
        },
    ]
