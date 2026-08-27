from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_ENV = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def load_template(name: str):
    return _ENV.get_template(name)


def render_system_grounded(
    passages: list[dict],
    user_message: str,
    dosha: dict | None = None,
    season: str | None = None,
    medications: list[str] | None = None,
    conditions: list[str] | None = None,
    location_context: str | None = None,
) -> list[dict]:
    template = load_template("system_grounded.j2")
    dosha_data = None
    if dosha:
        primary = dosha.get("dominant_dosha", "")
        if primary:
            scores = dosha.get("scores", {})
            sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            secondary = sorted_doshas[1][0] if len(sorted_doshas) > 1 and sorted_doshas[1][1] > 20 else None
            dosha_data = {"primary": primary, "secondary": secondary}

    system = template.render(
        passages=passages,
        user_message=user_message,
        dosha=dosha_data,
        season=season,
        medications=medications or [],
        conditions=conditions or [],
        location_context=location_context,
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"<user>\n{user_message}\n</user>"},
    ]


def refusal_text() -> str:
    return load_template("refusal.j2").render().strip()
