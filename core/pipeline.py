from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from platform.config import Config
from core.file_utils import find_images
from core.report import save_lines
from cv.analyzer import analyze_image

logger = logging.getLogger(__name__)


def analyze_folder(folder_path: str, output_dir: str | None = None) -> dict[str, Any]:
    """
    Основной пайплайн:
    1. Найти фото в папке
    2. Передать каждое фото в CV
    3. Сохранить good_photos.txt и bad_photos.txt
    4. Вернуть путь к good_photos.txt как основной результат
    """
    input_folder = Path(folder_path)

    if not input_folder.exists():
        raise FileNotFoundError(f"Папка не найдена: {input_folder}")

    if not input_folder.is_dir():
        raise ValueError(f"Ожидалась папка, а не файл: {input_folder}")

    paths = Config.get_paths()
    reports_dir = Path(output_dir) if output_dir else paths.reports
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Старт анализа папки: %s", input_folder)

    image_paths = find_images(input_folder)

    if not image_paths:
        raise ValueError("В выбранной папке не найдено поддерживаемых изображений")

    logger.info("Найдено изображений: %s", len(image_paths))

    good_photos: list[str] = []
    bad_photos: list[str] = []
    analysis_errors: list[str] = []

    for image_path in image_paths:
        relative_name = str(image_path.relative_to(input_folder))

        try:
            result = analyze_image(image_path)

            if result.get("is_good", False):
                good_photos.append(relative_name)
            else:
                reason = result.get("reason") or "unknown"
                bad_photos.append(f"{relative_name} - {reason}")

        except Exception as exc:
            analysis_errors.append(relative_name)
            bad_photos.append(f"{relative_name} - analysis_error")
            logger.exception("Ошибка анализа %s: %s", image_path, exc)

    good_txt_path = reports_dir / "good_photos.txt"
    bad_txt_path = reports_dir / "bad_photos.txt"

    save_lines(good_photos, good_txt_path)
    save_lines(bad_photos, bad_txt_path)

    logger.info("Анализ завершён. good=%s bad=%s", len(good_photos), len(bad_photos))

    return {
        "input_folder": str(input_folder),
        "total_found": len(image_paths),
        "analysis_errors": len(analysis_errors),
        "good_count": len(good_photos),
        "bad_count": len(bad_photos),
        "good_txt": str(good_txt_path),
        "bad_txt": str(bad_txt_path),
        "returned_to_user": str(good_txt_path),
    }


def analyze_archive(archive_path: str, output_dir: str | None = None) -> dict[str, Any]:
    """
    Временная заглушка для совместимости с runner.py,
    если он всё ещё вызывает analyze_archive(...).
    """
    archive_or_folder = Path(archive_path)

    if archive_or_folder.is_dir():
        return analyze_folder(str(archive_or_folder), output_dir=output_dir)

    raise NotImplementedError(
        "Сейчас проект работает с папкой фотографий, а не с архивом."
    )