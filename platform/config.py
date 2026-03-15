# platform/config.py
import os
import sys
from pathlib import Path
from typing import Tuple, NamedTuple
from datetime import timedelta

class Paths(NamedTuple):
    jobs: Path
    temp: Path  
    logs: Path
    reports: Path

class Config:
    APP_NAME = "PhotoAnalyzer"
    VERSION = "0.1.0"
    
    # Лимиты системы
    MAX_RAM_GB = 4
    MAX_THREADS = 8
    TEMP_TTL_HOURS = 1
    
    @classmethod
    def get_paths(cls) -> Paths:
        """Стандартные пути приложения"""
        if os.name == 'nt':  # Windows
            base = Path(os.getenv('APPDATA', '.')) / cls.APP_NAME
        else:  # Linux/Mac
            base = Path.home() / f'.{cls.APP_NAME.lower()}'
        
        base.mkdir(exist_ok=True)
        
        paths = Paths(
            jobs=base / 'jobs',
            temp=base / 'temp', 
            logs=base / 'logs',
            reports=base / 'reports'
        )
        
        for path in paths:
            path.mkdir(exist_ok=True)
        
        return paths
    
    @classmethod
    def cleanup_temp(cls):
        """Очистка temp файлов старше 1ч"""
        paths = cls.get_paths()
        cutoff = timedelta(hours=cls.TEMP_TTL_HOURS)
        
        for temp_file in paths.temp.glob('*'):
            if datetime.now().timestamp() - temp_file.stat().st_mtime > cutoff.total_seconds():
                temp_file.unlink()

    # TIFF конвертация
    TIFF_QUALITY = 100      # Без потерь
    TIFF_COMPRESSION = 'NONE'  # или 'LZW' для сжатия
    MAX_RESOLUTION = (2048, 2048)  # Для CV анализа
    SUPPORTED_INPUT = {'.jpg', '.jpeg', '.png', '.cr2', '.nef', '.arw', '.raf'}
    TIFF_OUTPUT = '.tif'
