from pathlib import Path

from generators.gemini_service import GeminiService
from generators.linkedin import generate_and_save_linkedin_post
from Research.topic_selector import select_best_topic, select_topics


def build_topic_prompt(topic: str) -> str:
    """Create a Gemini prompt that turns a research topic into a LinkedIn post."""
    return (
        f"Write a concise LinkedIn post about this topic: {topic}\n\n"
        "Use a professional and engaging tone."
    )


def create_post_from_research(research_file: str | Path, output_dir: str = "posts") -> str:
    """Read a research file, choose a topic, and generate a LinkedIn post from it."""
    topic = select_best_topic(research_file)
    topic_prompt = build_topic_prompt(topic)

    service = GeminiService()
    post_content = service.generate_content(topic_prompt)
    return generate_and_save_linkedin_post(output_dir=output_dir, post_content=post_content)


def create_multiple_posts_from_research(research_file: str | Path, output_dir: str = "posts", count: int = 5) -> list[str]:
    """Generate several distinct posts from different research topics and return their saved paths."""
    topics = select_topics(research_file, count=count)
    service = GeminiService()
    saved_files: list[str] = []

    for index, topic in enumerate(topics, start=1):
        topic_prompt = build_topic_prompt(topic)
        post_content = service.generate_content(topic_prompt)
        output_path = generate_and_save_linkedin_post(
            output_dir=output_dir,
            post_content=post_content,
        )
        saved_files.append(output_path)

    return saved_files


def create_posts_index(post_files: list[str], output_dir: str = "posts") -> str:
    """Create an index markdown file listing all generated posts."""
    index_path = Path(output_dir) / "index.md"
    lines = ["# Generated LinkedIn Posts", ""]

    for post_file in post_files:
        post_name = Path(post_file).name
        lines.append(f"- [{post_name}]({post_file})")

    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(index_path)
