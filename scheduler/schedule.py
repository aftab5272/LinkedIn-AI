from datetime import datetime
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_path(relative_path: PathLike) -> Path:
    path = Path(relative_path)
    if path.is_absolute():
        return path
    return get_project_root() / path


def ensure_directory(path: PathLike) -> Path:
    directory = resolve_path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def build_output_path(output_dir: PathLike = "posts", filename_prefix: str = "linkedin_post", extension: str = ".md") -> Path:
    output_directory = ensure_directory(output_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return output_directory / f"{filename_prefix}_{timestamp}{extension}"