from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from scheduler.schedule import ensure_directory


def load_carousel_data(json_path: str | Path) -> dict[str, Any]:
    """Load the carousel JSON structure from disk."""
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Carousel JSON not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def render_slide_html(slide: dict[str, Any], slide_number: int, total_slides: int) -> str:
    """Render a single slide as a polished, mobile-friendly HTML document."""
    title = html.escape(str(slide.get("title", ""))).strip()
    content = html.escape(str(slide.get("content", ""))).strip()
    slide_type = str(slide.get("type", "idea")).lower()

    if slide_type == "hook":
        badge_text = "Hook"
    elif slide_type == "cta":
        badge_text = "Call to Action"
    else:
        badge_text = "Key Insight"

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Slide {slide_number}</title>
  <style>
    :root {{
      --accent: #2563eb;
      --text: #0f172a;
      --muted: #475569;
      --surface: #ffffff;
      --border: #dbeafe;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f8fbff;
      color: var(--text);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 24px;
    }}
    .card {{
      width: min(100%, 860px);
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 10px 30px rgba(37, 99, 235, 0.10);
      padding: 32px;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .badge {{
      display: inline-block;
      padding: 8px 12px;
      border-radius: 999px;
      background: #eff6ff;
      color: var(--accent);
      font-weight: 700;
      font-size: 0.9rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .counter {{
      color: var(--muted);
      font-weight: 600;
      font-size: 0.95rem;
    }}
    h1 {{
      font-size: clamp(1.8rem, 2.5vw, 2.6rem);
      line-height: 1.15;
      margin: 0 0 16px;
      font-weight: 800;
      color: var(--text);
    }}
    p {{
      font-size: clamp(1rem, 1.5vw, 1.2rem);
      line-height: 1.7;
      color: var(--muted);
      margin: 0;
    }}
    .accent {{ color: var(--accent); }}
    @media (max-width: 640px) {{
      body {{ padding: 12px; }}
      .card {{ padding: 20px; border-radius: 16px; }}
      h1 {{ font-size: 1.6rem; }}
      p {{ font-size: 1rem; }}
    }}
  </style>
</head>
<body>
  <main class=\"card\">
    <div class=\"topbar\">
      <span class=\"badge\">{badge_text}</span>
      <span class=\"counter\">Slide {slide_number} of {total_slides}</span>
    </div>
    <h1>{title}</h1>
    <p>{content}</p>
  </main>
</body>
</html>
"""


def render_carousel_html(json_path: str | Path, output_dir: str | Path = "Output/carousel/html") -> list[Path]:
    """Render each slide from the carousel JSON into a standalone HTML file."""
    carousel_data = load_carousel_data(json_path)
    slides = carousel_data.get("slides", [])

    output_directory = ensure_directory(output_dir)
    rendered_paths: list[Path] = []

    for index, slide in enumerate(slides, start=1):
        html_path = output_directory / f"slide-{index}.html"
        html_path.write_text(render_slide_html(slide, index, len(slides)), encoding="utf-8")
        rendered_paths.append(html_path)

    return rendered_paths
