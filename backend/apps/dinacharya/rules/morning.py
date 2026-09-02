from datetime import date, datetime, time, timedelta


def build_activities(ctx):
    """Wake, hydration, oil massage (season-adapted), tongue, movement."""
    sunrise = ctx.sunrise or time(6, 0)
    sunrise_dt = datetime.combine(date.today(), sunrise)
    wake = (sunrise_dt - timedelta(minutes=30)).time()
    muhurta_start = (sunrise_dt - timedelta(minutes=96)).time()

    oil = "sesame" if ctx.season in ("shishir", "hemant", "vasant") else "coconut"

    return [
        {
            "time_of_day": "brahma_muhurta",
            "start": muhurta_start,
            "end": wake,
            "title": "Rise with the day",
            "description": "Wake before sunrise; sit quietly for a few minutes.",
            "reasons": ["Brahma muhurta is associated with a calm mind (classical timing)."],
            "citations": [{"source": "Ashtanga Hridaya", "ref": "Sutrasthana 2, vv. 1-3"}],
            "dosha_target": "vata",
            "order": 0,
        },
        {
            "time_of_day": "sunrise",
            "start": wake,
            "end": None,
            "title": "Warm water + tongue cleaning",
            "description": "Drink warm water; clean the tongue gently.",
            "reasons": ["Warm water supports digestion and hydration."],
            "citations": [{"source": "Charaka Samhita", "ref": "Sutrasthana 5"}],
            "dosha_target": "kapha",
            "order": 1,
        },
        {
            "time_of_day": "sunrise",
            "start": (sunrise_dt + timedelta(minutes=15)).time(),
            "end": (sunrise_dt + timedelta(minutes=45)).time(),
            "title": f"Self-massage ({oil} oil)",
            "description": f"A short abhyanga with {oil} oil before bathing.",
            "reasons": [f"{oil.title()} oil is seasonally balancing for your climate."],
            "citations": [{"source": "Ashtanga Hridaya", "ref": "Sutrasthana 2, vv. 8-11"}],
            "dosha_target": "vata",
            "order": 2,
        },
        {
            "time_of_day": "mid_morning",
            "start": (sunrise_dt + timedelta(hours=2)).time(),
            "end": (sunrise_dt + timedelta(hours=3)).time(),
            "title": "Movement / exercise",
            "description": "Moderate exercise until mild perspiration; stop before exhaustion.",
            "reasons": ["Exercise supports kapha balance and digestion."],
            "citations": [{"source": "Charaka Samhita", "ref": "Sutrasthana 7"}],
            "dosha_target": "kapha",
            "order": 3,
        },
    ]
