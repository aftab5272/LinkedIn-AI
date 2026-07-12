from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable

from scheduler.schedule import ensure_directory


def _find_chromium_or_chrome() -> str | None:
    """Locate a browser executable that can render pages to PNG."""
    candidates = [
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
        "msedge",
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            result = subprocess.run([candidate, "--version"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


def render_html_to_png(html_file: str | Path, output_png: str | Path, width: int = 1080, height: int = 1350) -> Path:
    """Render a single HTML slide into a PNG using a headless browser when available."""
    browser = _find_chromium_or_chrome()
    if not browser:
        raise RuntimeError("No headless browser found. Install Chrome, Chromium, or Edge to render PNG images.")

    html_path = Path(html_file).resolve()
    output_path = Path(output_png).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={output_path}",
        str(html_path),
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)
    return output_path


def render_html_slides_to_png(html_dir: str | Path, output_dir: str | Path = "Output/carousel/png", width: int = 1080, height: int = 1350) -> list[Path]:
    """Convert every HTML slide in a directory into a PNG image at the requested resolution."""
    source_dir = Path(html_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"HTML slides directory not found: {source_dir}")

    output_directory = ensure_directory(output_dir)
    rendered_paths: list[Path] = []

    for html_file in sorted(source_dir.glob("slide-*.html")):
        output_png = output_directory / f"{html_file.stem}.png"
        rendered_paths.append(render_html_to_png(html_file, output_png, width=width, height=height))

    return rendered_paths
