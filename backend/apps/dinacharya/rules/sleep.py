from datetime import time


def build_activities(ctx):
    dosha = ctx.dominant_dosha
    bedtime = {"kapha": time(21, 30), "vata": time(22, 0), "pitta": time(22, 30)}.get(dosha, time(22, 0))

    return [
        {
            "time_of_day": "evening",
            "start": time(21, 0),
            "end": None,
            "title": "Wind down",
            "description": "Dim lights, avoid screens, light reading or quiet reflection.",
            "reasons": ["Reduced stimulation before sleep improves nidra (restorative sleep)."],
            "citations": [{"source": "Charaka Samhita", "ref": "Sutrasthana 21 (nidra)"}],
            "dosha_target": "vata",
            "order": 30,
        },
        {
            "time_of_day": "night",
            "start": bedtime,
            "end": None,
            "title": "Sleep",
            "description": f"Aim for 7-8 hours of sleep. Your routine is tuned to a {dosha} constitution.",
            "reasons": ["Kapha-predominant people often need earlier sleep; pitta later."],
            "citations": [{"source": "Charaka Samhita", "ref": "Sutrasthana 21"}],
            "dosha_target": dosha,
            "order": 31,
        },
    ]
