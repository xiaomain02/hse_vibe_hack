# platform/runner.py
"""
Platform runner для PhotoAnalyzer (папки с фото)
CLI: PhotoAnalyzer.exe --cli <папка_с_фото>
GUI: PhotoAnalyzer.exe
multiprocessing + AppData + логи + analyze_folder()
"""

import multiprocessing
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from app_platform.config import Config, Paths
from core.pipeline import analyze_folder

logger = logging.getLogger(__name__)


def setup_logging(paths: Paths):
    """Логи в AppData + консоль."""
    log_file = paths.logs / f"photo_analyzer_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger.info("PhotoAnalyzer v%s запущен", Config.VERSION)


def cli_mode(folder_path: str, output_dir: Optional[str] = None):
    """CLI режим — анализ папки с фото."""
    paths = Config.get_paths()
    setup_logging(paths)

    folder = Path(folder_path)
    if not folder.exists():
        logger.error("Папка не найдена: %s", folder)
        sys.exit(1)

    output = Path(output_dir or str(paths.reports / folder.name))
    output.mkdir(exist_ok=True, parents=True)

    logger.info("Анализ папки: %s", folder)
    logger.info("Результат: %s", output)

    try:
        result_stats = analyze_folder(str(folder), str(output))
        logger.info("Анализ завершён: %s", result_stats)
        print(result_stats)
    except Exception as e:
        logger.error("Ошибка: %s", e, exc_info=True)
        sys.exit(1)


def gui_mode():
    """GUI режим — запуск frontend/app.py."""
    try:
        from frontend.app import run_app

        run_app()
        logger.info("GUI завершён")
    except ImportError as e:
        logger.warning("GUI не готов: %s", e)
        print("CLI: PhotoAnalyzer.exe --cli <папка_с_фото>")
        sys.exit(0)


def print_usage():
    """Справка CLI."""
    print(
        f"""
PhotoAnalyzer v{Config.VERSION}

Использование:
  PhotoAnalyzer.exe --cli <папка_с_фото> [папка_результата]

Примеры:
  PhotoAnalyzer.exe --cli "C:\\Photos\\Wedding"
  PhotoAnalyzer.exe --cli "C:\\Photos\\Event" "C:\\Output"
"""
    )


def main():
    """Точка входа приложения."""
    multiprocessing.freeze_support()

    paths = Config.get_paths()
    setup_logging(paths)
    Config.cleanup_temp()

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        if len(sys.argv) < 3:
            print_usage()
            sys.exit(1)

        cli_mode(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        return

    gui_mode()


if __name__ == "__main__":
    main()
