from __future__ import annotations

import re
from typing import Iterable


def normalize_hashtag(tag: str) -> str:
    """Return a normalized hashtag string."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "", tag).strip()
    if not cleaned:
        return ""
    return f"#{cleaned.lower()}"


def build_hashtags(text: str, max_hashtags: int = 5) -> list[str]:
    """Extract topic-relevant hashtags from a headline or post text."""
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    seen: set[str] = set()
    hashtags: list[str] = []

    for word in words:
        if len(word) < 3:
            continue
        if word in {"the", "and", "for", "with", "your", "that", "this", "from", "into", "have", "about"}:
            continue
        tag = normalize_hashtag(word)
        if tag and tag not in seen:
            seen.add(tag)
            hashtags.append(tag)
        if len(hashtags) >= max_hashtags:
            break

    if not hashtags:
        hashtags = ["#AI", "#Productivity", "#Automation"]

    return hashtags


def append_hashtags_to_post(post_text: str, hashtags: Iterable[str] | None = None) -> str:
    """Append a hashtag block to the post body while preserving the original content."""
    selected = list(hashtags or [])
    if not selected:
        selected = build_hashtags(post_text)

    cleaned = post_text.rstrip()
    if not cleaned.endswith("\n"):
        cleaned += "\n"
    cleaned += "\n"
    cleaned += " ".join(selected)
    return cleaned
