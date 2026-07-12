from scheduler.schedule import resolve_path


def load_prompt(prompt_name: str, prompts_folder: str = "prompts") -> str:
    """Load a prompt file from the prompts directory by name or path."""
    prompts_dir = resolve_path(prompts_folder)
    normalized_name = prompt_name.strip()

    # Build a list of possible locations so the loader stays flexible.
    candidate_paths = []

    if normalized_name.startswith("prompts/"):
        candidate_paths.append(resolve_path(normalized_name))
    else:
        candidate_paths.append(prompts_dir / normalized_name)

        if not normalized_name.endswith(".txt"):
            candidate_paths.append(prompts_dir / f"{normalized_name}_prompt.txt")
            candidate_paths.append(prompts_dir / f"{normalized_name}.txt")

    for candidate in candidate_paths:
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as file:
                return file.read()

    raise FileNotFoundError(f"Prompt not found: {prompt_name}")
