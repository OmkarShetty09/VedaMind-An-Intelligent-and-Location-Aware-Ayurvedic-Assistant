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


def render_system_grounded(passages: list[dict], user_message: str) -> list[dict]:
    template = load_template("system_grounded.j2")
    system = template.render(passages=passages, user_message=user_message)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"<user>\n{user_message}\n</user>"},
    ]


def render_dinacharya_weave(schedule_json: str) -> list[dict]:
    template = load_template("dinacharya_weave.j2")
    return [
        {"role": "system", "content": template.render(schedule_json=schedule_json)},
        {"role": "user", "content": "Write my routine for today."},
    ]


def refusal_text() -> str:
    return load_template("refusal.j2").render().strip()