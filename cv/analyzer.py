from pathlib import Path
from typing import Any


def analyze_image(tiff_path: Path) -> dict[str, Any]:
    """
    CV-команда потом заменит это на реальный анализ.
    На вход получает TIFF.
    На выход возвращает:
    {
        "is_good": bool,
        "reason": str | None
    }
    """
    return {
        "is_good": True,
        "reason": None,
    }