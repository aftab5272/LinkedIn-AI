from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scheduler.schedule import ensure_directory, resolve_path


def read_post_text(post_file: str | Path) -> str:
    """Read the LinkedIn post content from a markdown file."""
    path = Path(post_file)
    if not path.exists():
        raise FileNotFoundError(f"Post file not found: {path}")

    return path.read_text(encoding="utf-8")


def clean_markdown_text(text: str) -> str:
    """Remove markdown syntax and normalize whitespace for slide content."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text)
    text = text.replace("#", "")
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def split_into_paragraphs(text: str) -> list[str]:
    """Split post content into meaningful paragraphs."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return [clean_markdown_text(p) for p in paragraphs]


def summarize_paragraph(paragraph: str, max_words: int = 24) -> str:
    """Create a concise summary from a paragraph."""
    cleaned = clean_markdown_text(paragraph)
    words = cleaned.split()
    if len(words) <= max_words:
        return cleaned
    return " ".join(words[:max_words]).rstrip(".,;:") + "..."


def build_carousel_structure(post_file: str | Path) -> dict[str, Any]:
    """Transform a LinkedIn post into an 8-slide carousel structure."""
    post_path = Path(post_file)
    post_text = read_post_text(post_path)
    paragraphs = split_into_paragraphs(post_text)

    if not paragraphs:
        raise ValueError("The LinkedIn post does not contain any content to convert.")

    hook_text = summarize_paragraph(paragraphs[0], max_words=24)
    body_paragraphs = paragraphs[1:]

    slides: list[dict[str, Any]] = []
    slides.append({
        "slide": 1,
        "type": "hook",
        "title": hook_text,
        "content": hook_text,
    })

    for index, paragraph in enumerate(body_paragraphs[:6], start=2):
        slides.append({
            "slide": index,
            "type": "idea",
            "title": f"Key idea {index - 1}",
            "content": summarize_paragraph(paragraph, max_words=24),
        })

    while len(slides) < 7:
        slides.append({
            "slide": len(slides) + 1,
            "type": "idea",
            "title": f"Key idea {len(slides)}",
            "content": "Add a practical takeaway for your audience.",
        })

    slides.append({
        "slide": 8,
        "type": "cta",
        "title": "Let’s continue the conversation",
        "content": "Share your perspective in the comments and tell us how you would apply this idea.",
    })

    return {
        "source_post": str(post_path),
        "slides": slides,
    }


def save_carousel_json(carousel_data: dict[str, Any], output_dir: str | Path = "Output/carousel", filename: str = "carousel.json") -> Path:
    """Save the carousel structure as JSON in the requested output folder."""
    output_directory = ensure_directory(output_dir)
    output_path = output_directory / filename
    output_path.write_text(json.dumps(carousel_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def generate_and_save_carousel(post_file: str | Path, output_dir: str | Path = "Output/carousel", filename: str = "carousel.json") -> Path:
    """Create a carousel JSON file from a LinkedIn markdown post."""
    carousel_data = build_carousel_structure(post_file)
    output_path = save_carousel_json(carousel_data, output_dir=output_dir, filename=filename)
    return output_path
