from pathlib import Path

from Research.engine import run_daily_research
from Research.topic_selection import read_best_topic_metadata
from generators.carousel import generate_and_save_carousel
from generators.carousel_renderer import render_carousel_html
from generators.image_renderer import render_html_slides_to_png
from generators.linkedin import generate_and_save_linkedin_post
from generators.pdf_generator import merge_pngs_to_pdf


def main() -> None:
    try:
        run_daily_research()
    except Exception as exc:
        print(f"Research workflow warning: {exc}")

    best_topic_file = Path(__file__).resolve().parent / "Research" / "best_topic.md"
    topic_details = read_best_topic_metadata(best_topic_file)

    if topic_details:
        generated_post = generate_and_save_linkedin_post(
            prompt_name="linkedin",
            output_dir="Posts",
            topic=topic_details.get("title"),
            topic_source=topic_details.get("source"),
            topic_link=topic_details.get("link"),
            topic_file=best_topic_file,
        )
    else:
        generated_post = generate_and_save_linkedin_post(prompt_name="linkedin", output_dir="Posts")

    latest_post_file = Path(__file__).resolve().parent / "Posts" / Path(generated_post).name
    if latest_post_file.exists():
        carousel_path = generate_and_save_carousel(latest_post_file)
        html_files = render_carousel_html(carousel_path)
        png_files = render_html_slides_to_png(Path(__file__).resolve().parent / 'Output' / 'carousel' / 'html')
        pdf_path = merge_pngs_to_pdf(Path(__file__).resolve().parent / 'Output' / 'carousel' / 'png')
        print(f"Carousel saved to: {carousel_path}")
        print(f"Carousel HTML slides saved to: {Path(__file__).resolve().parent / 'Output' / 'carousel' / 'html'}")
        print(f"Carousel PNG slides saved to: {Path(__file__).resolve().parent / 'Output' / 'carousel' / 'png'}")
        print(f"Carousel PDF saved to: {pdf_path}")
        for html_file in html_files:
            print(f" - {html_file}")
        for png_file in png_files:
            print(f" - {png_file}")


if __name__ == "__main__":
    main()