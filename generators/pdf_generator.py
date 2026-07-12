from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image

from scheduler.schedule import ensure_directory


def merge_pngs_to_pdf(png_dir: str | Path, output_pdf: str | Path = "Output/carousel/pdf/linkedin_carousel.pdf") -> Path:
    """Merge PNG slide images into a single PDF file."""
    source_dir = Path(png_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"PNG slides directory not found: {source_dir}")

    png_files = sorted(source_dir.glob("slide-*.png"))
    if not png_files:
        raise FileNotFoundError(f"No PNG slide files found in {source_dir}")

    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    images = [Image.open(path).convert("RGB") for path in png_files]
    first_image = images[0]
    first_image.save(output_path, save_all=True, append_images=images[1:], resolution=100.0)

    for image in images:
        image.close()

    return output_path
