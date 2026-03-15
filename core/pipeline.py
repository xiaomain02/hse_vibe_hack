from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from platform.config import Config
from platform.image_converter import batch_convert
from core.file_utils import find_images
from core.report import save_lines
from cv.analyzer import analyze_image

logger = logging.getLogger(__name__)


def analyze_folder(folder_path: str, output_dir: str | None = None) -> dict[str, Any]:
    """
    Основной пайплайн:
    1. Найти фото в папке
    2. Конвертировать их в TIFF через platform.image_converter
    3. Отдать TIFF в CV
    4. Сохранить good_photos.txt и bad_photos.txt
    5. Вернуть путь к good_photos.txt как основной результат
    """
    input_folder = Path(folder_path)

    if not input_folder.exists():
        raise FileNotFoundError(f"Папка не найдена: {input_folder}")

    if not input_folder.is_dir():
        raise ValueError(f"Ожидалась папка, а не файл: {input_folder}")

    paths = Config.get_paths()
    reports_dir = Path(output_dir) if output_dir else paths.reports
    reports_dir.mkdir(parents=True, exist_ok=True)

    temp_job_dir = paths.temp / f"job_{input_folder.name}"
    temp_job_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Старт анализа папки: %s", input_folder)

    image_paths = find_images(input_folder)

    if not image_paths:
        raise ValueError("В выбранной папке не найдено поддерживаемых изображений")

    logger.info("Найдено изображений: %s", len(image_paths))

    good_photos: list[str] = []
    bad_photos: list[str] = []
    conversion_errors: list[str] = []
    analysis_errors: list[str] = []

    # 1. Конвертация в TIFF
    converted_map: dict[Path, Path] = {}

    for image_path in image_paths:
        try:
            tiff_paths = batch_convert([image_path], temp_job_dir)
            if not tiff_paths:
                raise RuntimeError("batch_convert не вернул TIFF-файл")

            converted_map[image_path] = tiff_paths[0]

        except Exception as exc:
            relative_name = str(image_path.relative_to(input_folder))
            conversion_errors.append(relative_name)
            bad_photos.append(f"{relative_name} - conversion_error")
            logger.exception("Ошибка конвертации %s: %s", image_path, exc)

    logger.info("Успешно конвертировано в TIFF: %s", len(converted_map))

    # 2. CV-анализ
    for original_path, tiff_path in converted_map.items():
        relative_name = str(original_path.relative_to(input_folder))

        try:
            result = analyze_image(tiff_path)

            if result.get("is_good", False):
                good_photos.append(relative_name)
            else:
                reason = result.get("reason") or "unknown"
                bad_photos.append(f"{relative_name} - {reason}")

        except Exception as exc:
            analysis_errors.append(relative_name)
            bad_photos.append(f"{relative_name} - analysis_error")
            logger.exception("Ошибка анализа %s: %s", original_path, exc)

    # 3. Сохранение отчётов
    good_txt_path = reports_dir / "good_photos.txt"
    bad_txt_path = reports_dir / "bad_photos.txt"

    save_lines(good_photos, good_txt_path)
    save_lines(bad_photos, bad_txt_path)

    logger.info("Анализ завершён. good=%s bad=%s", len(good_photos), len(bad_photos))

    return {
        "input_folder": str(input_folder),
        "total_found": len(image_paths),
        "converted_successfully": len(converted_map),
        "conversion_errors": len(conversion_errors),
        "analysis_errors": len(analysis_errors),
        "good_count": len(good_photos),
        "bad_count": len(bad_photos),
        "good_txt": str(good_txt_path),
        "bad_txt": str(bad_txt_path),
        "returned_to_user": str(good_txt_path),
    }


def analyze_archive(archive_path: str, output_dir: str | None = None) -> dict[str, Any]:
    """
    Временная заглушка для совместимости с current runner.py.
    Сейчас runner Сони ожидает analyze_archive(...), хотя вы уже
    перешли на сценарий с папкой.

    Пока можно:
    - либо передавать сюда путь к папке,
    - либо позже заменить runner на analyze_folder.
    """
    archive_or_folder = Path(archive_path)

    if archive_or_folder.is_dir():
        return analyze_folder(str(archive_or_folder), output_dir=output_dir)

    raise NotImplementedError(
        "Сейчас проект работает с папкой фотографий, а не с архивом. "
        "Либо передай путь к папке, либо обнови runner.py на analyze_folder(...)."
    )