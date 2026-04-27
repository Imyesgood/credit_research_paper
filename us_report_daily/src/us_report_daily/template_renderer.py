import re

def render_template(template_html: str, placeholders: dict[str, str]) -> str:
    html = template_html
    for k, v in placeholders.items():
        html = html.replace("{{" + k + "}}", str(v))

    # leftover class placeholders -> fl
    html = re.sub(r"\{\{CLS\|[^}]+\}\}", "fl", html)
    # leftover placeholders -> —
    html = re.sub(r"\{\{[^}]+\}\}", "—", html)
    return html