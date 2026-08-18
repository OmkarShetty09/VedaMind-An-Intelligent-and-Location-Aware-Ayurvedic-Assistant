from datetime import time


def build_activities(ctx):
    activities = [
        {
            "time_of_day": "sunset",
            "start": ctx.sunset or time(18, 30),
            "end": None,
            "title": "Sunset walk",
            "description": "A short evening walk; reduce stimulation as light fades.",
            "reasons": ["Matching activity to the light cycle steadies the mind."],
            "citations": [{"source": "Ashtanga Hridaya", "ref": "Sutrasthana 2"}],
            "dosha_target": "vata",
            "order": 20,
        }
    ]
    if ctx.temperature_c is not None and ctx.temperature_c > 35:
        activities.append(
            {
                "time_of_day": "afternoon",
                "start": time(14, 30),
                "end": time(15, 30),
                "title": "Afternoon rest",
                "description": "Very hot weather: rest in a cool, shaded room; hydrate.",
                "reasons": ["Heat stress is managed by scheduling rest during peak heat."],
                "citations": [{"source": "Ritucharya (heat management)"}],
                "dosha_target": "pitta",
                "order": 21,
            }
        )
    return activities
