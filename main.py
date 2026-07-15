from Research.engine import run_daily_research
from orchestrator import run_pipeline


def main() -> None:
    research_result = run_daily_research()
    print("Research completed:", research_result)
    result = run_pipeline()
    print("Pipeline completed successfully")
    print("Post:", result.get("post"))
    print("Carousel:", result.get("carousel"))
    print("PDF:", result.get("pdf"))
    print("Manifest:", result.get("manifest"))


if __name__ == "__main__":
    main()