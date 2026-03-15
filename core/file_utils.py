from pathlib import Path
from typing import Iterable

from platform.config import Config


def find_images(folder: Path) -> list[Path]:
    """
    Ищет все поддерживаемые изображения в папке и подпапках.
    Поддерживаемые расширения берутся из platform.config.Config.
    """
    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(f"Папка не найдена: {folder}")

    if not folder.is_dir():
        raise ValueError(f"Указанный путь не является папкой: {folder}")

    image_files: list[Path] = []

    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in Config.SUPPORTED_INPUT:
            image_files.append(path)

    return sorted(image_files)


def relative_names(paths: Iterable[Path], base_folder: Path) -> list[str]:
    base_folder = Path(base_folder)
    return [str(path.relative_to(base_folder)) for path in paths]