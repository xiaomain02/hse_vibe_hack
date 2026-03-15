# platform/runner.py
"""
Platform runner для PhotoAnalyzer (папки с фото)
CLI: PhotoAnalyzer.exe --cli <папка_с_фото>
GUI: PhotoAnalyzer.exe  
multiprocessing + AppData + логи + Иринин analyze_folder()
"""

import multiprocessing
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import Config, Paths

# 🎯 ИМПОРТ ОТ ИРИНЫ
from core.pipeline import analyze_folder

logger = logging.getLogger(__name__)

def setup_logging(paths: Paths):
    """Логи в AppData + консоль"""
    log_file = paths.logs / f"photo_analyzer_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger.info(f"🚀 PhotoAnalyzer v{Config.VERSION} запущен")

def cli_mode(folder_path: str, output_dir: Optional[str] = None):
    """CLI режим — анализ ПАПКИ (НЕ архива!)"""
    # ✅ АБСОЛЮТНЫЙ ИМПОРТ
    from core.pipeline import analyze_folder
    from platform.config import Config, Paths  # ← АБСОЛЮТНЫЙ!
    
    paths = Config.get_paths()
    setup_logging(paths)
    
    folder = Path(folder_path)
    if not folder.exists():
        logger.error(f"❌ Папка не найдена: {folder}")
        sys.exit(1)
    
    output = Path(output_dir or str(paths.reports / folder.name))
    output.mkdir(exist_ok=True, parents=True)
    
    logger.info(f"📁 Анализ папки: {folder}")  # ✅ ПАПКА!
    logger.info(f"📤 Результат: {output}")
    
    try:
        result_stats = analyze_folder(str(folder), str(output))
        logger.info(f"✅ Анализ завершён: {result_stats}")
    except Exception as e:
        logger.error(f"💥 Ошибка: {e}", exc_info=True)
        sys.exit(1)

def gui_mode():
    """GUI режим — Виктория"""
    try:
        from frontend.ui.main_window import MainWindow
        app = MainWindow()
        app.run()
        logger.info("🖥️ GUI завершён")
    except ImportError:
        logger.warning("GUI не готов")
        print("💡 CLI: PhotoAnalyzer.exe --cli <папка_с_фото>")
        sys.exit(0)

def print_usage():
    """Справка CLI"""
    print(f"""
🖼️  PhotoAnalyzer v{Config.VERSION}

Использование:
  PhotoAnalyzer.exe --cli <папка_с_фото> [папка_результата]

Примеры:
  PhotoAnalyzer.exe --cli "C:\\Photos\\Wedding"
  PhotoAnalyzer.exe --cli "C:\\Photos\\Event" "C:\\Output"
    """)

def main():
    """Точка входа приложения"""
    multiprocessing.freeze_support()  # КРИТИЧНО для EXE!
    
    paths = Config.get_paths()
    Config.cleanup_temp()
    
    # CLI режим
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        if len(sys.argv) < 3:
            print_usage()
            sys.exit(1)
        cli_mode(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        return
    
    # GUI по умолчанию
    gui_mode()

if __name__ == '__main__':
    main()
