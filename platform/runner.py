import multiprocessing
import sys
import logging
from pathlib import Path
from typing import Optional

from config import Config, Paths

# Настройка логирования
def setup_logging(paths: Paths):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(paths.logs / 'app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def cli_mode(archive_path: str, output_dir: Optional[str] = None):
    """CLI режим для тестирования EXE"""
    from core.pipeline import analyze_archive
    
    paths = Config.get_paths()
    setup_logging(paths)
    
    print(f"🔄 Анализ архива: {archive_path}")
    analyze_archive(archive_path, output_dir or str(paths.reports))
    print("✅ Готово!")

def main():
    """Главная точка входа приложения"""
    multiprocessing.freeze_support()  # 🎯 КРИТИЧНО для PyInstaller!
    
    paths = Config.get_paths()
    setup_logging(paths)
    
    # CLI режим
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        if len(sys.argv) < 3:
            print("Использование: PhotoAnalyzer.exe --cli <archive.zip> [output_dir]")
            sys.exit(1)
        cli_mode(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        return
    
    # Desktop GUI режим (Виктория)
    try:
        from frontend.ui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError:
        print("GUI не готов. Запуск CLI режима.")
        cli_mode("test.zip")  # Заглушка

if __name__ == '__main__':
    main()
