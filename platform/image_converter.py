import cv2
import numpy as np
from PIL import Image
from PIL.Image import Image as PILImage
from pathlib import Path
import logging
from typing import Optional
from platform.config import Config

logger = logging.getLogger(__name__)

def convert_to_tiff(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Конвертирует любое фото → TIFF без потерь для CV анализа
    JPG/PNG/RAW → TIFF (16-bit grayscale для sharpness)
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(Config.TIFF_OUTPUT)
    
    # Поддерживаемые форматы
    if input_path.suffix.lower() not in Config.SUPPORTED_INPUT:
        raise ValueError(f"Неподдерживаемый формат: {input_path.suffix}")
    
    logger.info(f"🔄 Конвертация {input_path.name} → TIFF")
    
    # 1. Загрузка (OpenCV для RAW/CR2)
    if input_path.suffix.lower() in {'.cr2', '.nef', '.arw'}:
        # RAW через OpenCV
        img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    else:
        # JPG/PNG через PIL
        with Image.open(input_path) as pil_img:
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # 2. Предобработка для CV
    height, width = img.shape[:2]
    if max(height, width) > 2048:
        scale = 2048 / max(height, width)
        new_size = (int(width * scale), int(height * scale))
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_LANCZOS4)
    
    # 3. Сохраняем TIFF 16-bit grayscale (идеально для sharpness)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(
        str(output_path), 
        gray, 
        [cv2.IMWRITE_TIFF_COMPRESSION, cv2.IMWRITE_TIFF_COMPRESSION_NONE]
    )
    
    logger.info(f"✅ TIFF готов: {output_path}")
    return output_path

def batch_convert(photos: list[Path], temp_dir: Path) -> list[Path]:
    """Batch конвертация для multiprocessing"""
    tiff_paths = []
    for photo in photos:
        tiff_path = temp_dir / f"{photo.stem}{Config.TIFF_OUTPUT}"
        tiff_paths.append(convert_to_tiff(photo, tiff_path))
    return tiff_paths
