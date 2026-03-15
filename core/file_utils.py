from pathlib import Path
from app_platform.config import Config


def find_images(folder: Path) -> list[Path]:
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