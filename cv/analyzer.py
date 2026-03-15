from pathlib import Path
from typing import Any

from cv.cv_processing import check_image_quality


def analyze_image(image_path: Path) -> dict[str, Any]:
    try:
        is_good = check_image_quality(str(image_path))

        if is_good:
            return {
                "is_good": True,
                "reason": None,
            }

        return {
            "is_good": False,
            "reason": "quality_check_failed",
        }

    except Exception as e:
        return {
            "is_good": False,
            "reason": f"cv_error: {str(e)}",
        }