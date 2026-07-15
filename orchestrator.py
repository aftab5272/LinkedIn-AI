from __future__ import annotations

import logging
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Research.engine import run_daily_research
from Research.topic_selection import read_best_topic_metadata
from generators.carousel import generate_and_save_carousel
from generators.carousel_renderer import render_carousel_html
from generators.hashtags import append_hashtags_to_post, build_hashtags
from generators.image_renderer import render_html_slides_to_png
from generators.linkedin import generate_and_save_linkedin_post
from generators.pdf_generator import merge_pngs_to_pdf
from publishers.linkedin_publisher import publish_to_linkedin
from scheduler.schedule import ensure_directory, resolve_path


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("linkedin_automation")


class PipelineResult(dict):
    """Container for pipeline outputs."""


def run_pipeline() -> PipelineResult:
    """Run the full LinkedIn automation pipeline from research to export."""
    logger.info("Starting LinkedIn automation pipeline")

    project_root = resolve_path(".")
    today_topics_path = project_root / "Research" / date.today().strftime("%Y-%m-%d") / "topics.json"
    if not today_topics_path.exists():
        try:
            run_daily_research()
        except Exception as exc:
            logger.warning("Research step failed: %s", exc)
    else:
        logger.info("Using existing research topic bundle: %s", today_topics_path)
    best_topic_file = project_root / "Research" / "best_topic.md"
    topic_details = read_best_topic_metadata(best_topic_file)

    topic_title = topic_details.get("title") if topic_details else None
    topic_source = topic_details.get("source") if topic_details else None
    topic_link = topic_details.get("link") if topic_details else None

    logger.info("Generating LinkedIn post")
    generated_post = generate_and_save_linkedin_post(
        prompt_name="linkedin",
        output_dir="Posts",
        topic=topic_title,
        topic_source=topic_source,
        topic_link=topic_link,
        topic_file=best_topic_file,
    )

    post_path = project_root / "Posts" / Path(generated_post).name
    if not post_path.exists():
        raise FileNotFoundError(f"Generated post file not found: {post_path}")

    post_text = post_path.read_text(encoding="utf-8")
    hashtags = build_hashtags(post_text)
    updated_post_text = append_hashtags_to_post(post_text, hashtags=hashtags)
    post_path.write_text(updated_post_text, encoding="utf-8")

    logger.info("Generating carousel")
    carousel_path = generate_and_save_carousel(post_path, output_dir="Output/carousel")

    logger.info("Rendering HTML slides")
    html_files = render_carousel_html(carousel_path, output_dir="Output/carousel/html")

    logger.info("Rendering PNG slides")
    png_files = render_html_slides_to_png(project_root / "Output" / "carousel" / "html", output_dir="Output/carousel/png")

    logger.info("Generating PDF")
    pdf_path = merge_pngs_to_pdf(project_root / "Output" / "carousel" / "png", output_pdf="Output/carousel/pdf/linkedin_carousel.pdf")

    payload = None
    if os.getenv("ENABLE_LINKEDIN_PUBLISH", "false").lower() in {"1", "true", "yes"}:
        logger.info("LinkedIn publishing is enabled")
        payload = publish_to_linkedin()
    else:
        logger.info("LinkedIn publishing is disabled; skipping publish step")

    output_dir = ensure_directory("Output/automation")
    manifest_path = output_dir / "pipeline_manifest.json"
    manifest_path.write_text(
        "\n".join([
            "{",
            f'  "post": {generated_post!r},',
            f'  "carousel": {str(carousel_path)!r},',
            f'  "html_files": {str([str(path) for path in html_files])!r},',
            f'  "png_files": {str([str(path) for path in png_files])!r},',
            f'  "pdf": {str(pdf_path)!r},',
            f'  "hashtags": {hashtags!r},',
            f'  "linkedin_publish_payload": {str(payload)!r}',
            "}",
        ]) + "\n",
        encoding="utf-8",
    )

    logger.info("Pipeline completed successfully")
    result = PipelineResult(
        post=generated_post,
        carousel=str(carousel_path),
        html_files=[str(path) for path in html_files],
        png_files=[str(path) for path in png_files],
        pdf=str(pdf_path),
        hashtags=hashtags,
        manifest=str(manifest_path),
    )
    if payload is not None:
        result["linkedin_payload"] = payload
    return result
