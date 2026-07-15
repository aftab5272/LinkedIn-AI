from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


logger = logging.getLogger("linkedin_publisher")


@dataclass
class LinkedInPublishPayload:
    post_file: Path
    post_text: str
    hashtags: list[str]
    carousel_file: Path | None
    carousel_images: list[Path]
    pdf_file: Path | None
    needs_publish: bool = True


class LinkedInPublisherError(RuntimeError):
    pass


def _load_latest_post(posts_dir: str = "Posts") -> Path:
    posts_path = Path(posts_dir)
    if not posts_path.exists() or not posts_path.is_dir():
        raise LinkedInPublisherError(f"Posts directory not found: {posts_path}")

    post_files = sorted(posts_path.glob("linkedin_post_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not post_files:
        raise LinkedInPublisherError("No generated LinkedIn posts were found.")
    return post_files[0]


def _load_hashtags(post_text: str, hashtags: Iterable[str] | None = None) -> list[str]:
    if hashtags:
        return [tag for tag in hashtags if tag.startswith("#")]

    extracted = [tag.strip() for tag in post_text.split() if tag.startswith("#")]
    if not extracted:
        raise LinkedInPublisherError("No hashtags found in the LinkedIn post.")
    return extracted


def _find_carousel_file(output_dir: str = "Output/carousel") -> Path | None:
    carousel_json = Path(output_dir) / "carousel.json"
    if carousel_json.exists():
        return carousel_json
    return None


def _find_carousel_images(output_dir: str = "Output/carousel/png") -> list[Path]:
    png_dir = Path(output_dir)
    if not png_dir.exists():
        return []
    return sorted(png_dir.glob("slide-*.png"))


def _get_linkedin_credentials() -> dict[str, str]:
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    if not any([client_id, client_secret, access_token]):
        raise LinkedInPublisherError(
            "LinkedIn credentials are not set in environment variables. "
            "Set LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, or LINKEDIN_ACCESS_TOKEN."
        )

    return {
        "client_id": client_id or "",
        "client_secret": client_secret or "",
        "access_token": access_token or "",
    }


def _prepare_payload() -> LinkedInPublishPayload:
    post_file = _load_latest_post()
    post_text = post_file.read_text(encoding="utf-8")
    hashtags = _load_hashtags(post_text)
    carousel_file = _find_carousel_file()
    carousel_images = _find_carousel_images()
    pdf_file = Path("Output/carousel/pdf/linkedin_carousel.pdf")
    if not pdf_file.exists():
        pdf_file = None

    return LinkedInPublishPayload(
        post_file=post_file,
        post_text=post_text,
        hashtags=hashtags,
        carousel_file=carousel_file,
        carousel_images=carousel_images,
        pdf_file=pdf_file,
    )


def publish_to_linkedin(use_browser_fallback: bool = False) -> LinkedInPublishPayload:
    logger.info("Preparing LinkedIn publish payload")
    payload = _prepare_payload()

    try:
        credentials = _get_linkedin_credentials()
        logger.info("LinkedIn credentials loaded from environment")
        logger.debug("LinkedIn credentials keys: %s", list(credentials.keys()))

        if credentials.get("access_token"):
            logger.info("Access token available; publishing via LinkedIn API to be implemented.")
        else:
            logger.info("LinkedIn API credentials incomplete; browser automation can be plugged in later.")

        payload.needs_publish = True
        return payload

    except LinkedInPublisherError as exc:
        if use_browser_fallback:
            logger.warning("LinkedIn API unavailable: %s. Browser fallback enabled.", exc)
            payload.needs_publish = True
            return payload
        logger.error("LinkedIn publishing preparation failed: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Unexpected error while preparing LinkedIn payload: %s", exc)
        raise LinkedInPublisherError("Failed to prepare LinkedIn publish payload") from exc
