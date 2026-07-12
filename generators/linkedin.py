from pathlib import Path
from typing import Optional

from generators.gemini_service import GeminiService
from generators.prompt_loader import load_prompt
from scheduler.schedule import build_output_path, resolve_path


def read_prompt(prompt_name: str = "linkedin") -> str:
    """Load a prompt from the prompts folder using a reusable helper."""
    return load_prompt(prompt_name)


def normalize_output_dir(output_dir: str | Path | None = None) -> str:
    """Normalize the output directory to the project's Posts folder while remaining backward-compatible."""
    if output_dir is None:
        return "Posts"
    if isinstance(output_dir, Path):
        return str(output_dir)

    cleaned = str(output_dir).strip().strip('"').strip("'")
    if not cleaned:
        return "Posts"
    if cleaned.lower() == "posts":
        return "Posts"
    return cleaned


def read_topic_from_file(topic_file: str | Path | None) -> Optional[str]:
    """Read the selected topic title from a best-topic markdown file when available."""
    if not topic_file:
        return None

    path = Path(topic_file)
    if not path.exists():
        return None

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Title:**"):
            return line.split("**Title:**", 1)[1].strip()
        if line.startswith("Title:"):
            return line.split("Title:", 1)[1].strip()

    return None


def build_linkedin_prompt(
    prompt_name: str = "linkedin",
    topic: Optional[str] = None,
    topic_source: Optional[str] = None,
    topic_link: Optional[str] = None,
    topic_file: Optional[str | Path] = None,
) -> str:
    """Build a topic-aware LinkedIn prompt while preserving the existing default prompt."""
    template = read_prompt(prompt_name)
    topic_title = topic or read_topic_from_file(topic_file) or "Artificial Intelligence for Beginners"
    source_text = topic_source or "a credible source"
    link_text = topic_link or ""

    return (
        template.replace("{{TOPIC}}", topic_title)
        .replace("{{SOURCE}}", source_text)
        .replace("{{LINK}}", link_text)
    )


def generate_linkedin_post(
    prompt_name: str = "linkedin",
    model: str = "gemini-3.5-flash",
    topic: Optional[str] = None,
    topic_source: Optional[str] = None,
    topic_link: Optional[str] = None,
    topic_file: Optional[str | Path] = None,
) -> str:
    # Keep the Gemini call path centralized in the reusable service.
    service = GeminiService(model=model)
    prompt = build_linkedin_prompt(
        prompt_name=prompt_name,
        topic=topic,
        topic_source=topic_source,
        topic_link=topic_link,
        topic_file=topic_file,
    )
    return service.generate_content(prompt)


def save_linkedin_post(post: str, output_dir: str = "Posts") -> str:
    output_path = build_output_path(output_dir=normalize_output_dir(output_dir))
    with output_path.open("w", encoding="utf-8") as file:
        file.write(post)

    relative_path = output_path.relative_to(resolve_path("."))
    return relative_path.as_posix()


def generate_and_save_linkedin_post(
    prompt_name: str = "linkedin",
    output_dir: str = "Posts",
    post_content: Optional[str] = None,
    topic: Optional[str] = None,
    topic_source: Optional[str] = None,
    topic_link: Optional[str] = None,
    topic_file: Optional[str | Path] = None,
) -> str:
    # Keep existing behavior intact while allowing the research workflow to pass custom content.
    post = post_content if post_content is not None else generate_linkedin_post(
        prompt_name=prompt_name,
        topic=topic,
        topic_source=topic_source,
        topic_link=topic_link,
        topic_file=topic_file,
    )
    print(post)

    filename = save_linkedin_post(post, output_dir=output_dir)
    print("\n✅ LinkedIn Post Saved Successfully!")
    print("📂 File:", filename)
    return filename