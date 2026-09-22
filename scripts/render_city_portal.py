"""Render the progressive-enhancement portal from its editable collection manifest.

Run: python scripts/render_city_portal.py
No network requests or non-standard dependencies are required.
"""
from collections import Counter
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "website/data/city-portal.json"
TEMPLATE = ROOT / "scripts/templates/city-portal.html"
DESTINATION = ROOT / "website/interfaces/city-live/index.html"


def render():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    apps = data["apps"]
    counts = Counter(app["category"] for app in apps)
    filters = []
    for category in data["categories"]:
        key = category["id"]
        count = len(apps) if key == "all" else counts[key]
        filters.append(f'<button type="button" data-category="{escape(key)}" aria-pressed="{str(key == "all").lower()}">{escape(category["label"])} <span>{count}</span></button>')
    cards = []
    for app in apps:
        text = {k: escape(str(v), quote=True) for k, v in app.items()}
        search = escape(" ".join(str(app[k]) for k in ["name", "edition", "description", "role", "url", "category"]).casefold(), quote=True)
        cards.append(f'''<a class="app-card" id="app-{text['id']}" href="{text['url']}" target="_blank" rel="noopener noreferrer" data-category="{text['category']}" data-name="{text['name']}" data-search="{search}" data-order="{text['number']}" aria-label="Open {text['name']} — {text['edition']} (new tab)">
  <div class="card-art"><img src="{text['image']}" alt="" width="900" height="473" loading="lazy" decoding="async"><span class="card-number">{app['number']:02}</span><span class="card-arrow" aria-hidden="true">↗</span></div>
  <div class="card-copy"><p class="card-role">{text['role']}</p><h3>{text['name']}</h3><p class="card-edition">{text['edition']}</p><p class="card-description">{text['description']}</p><div class="card-footer"><span>OPEN INSTRUMENT</span><span aria-hidden="true">↗</span></div></div>
</a>''')
    sources = [f'<li><a href="{escape(s["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(s["provider"])} · {escape(s["title"])}</a></li>' for s in data["sources"]]
    html = TEMPLATE.read_text(encoding="utf-8")
    for key, value in {"HERO_IMAGE": escape(data["hero"]["image"], quote=True), "FILTERS": "\n".join(filters), "APP_CARDS": "\n".join(cards), "SOURCE_LINKS": "\n".join(sources)}.items():
        html = html.replace(f"@@{key}@@", value)
    return html


if __name__ == "__main__":
    DESTINATION.write_text(render(), encoding="utf-8")
    print(f"Rendered {DESTINATION.relative_to(ROOT)}")
