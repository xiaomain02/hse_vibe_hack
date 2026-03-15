from importlib.resources import path

import cv2
import numpy as np
import mediapipe as mp
import rawpy
import os


# from mediapipe import solutions as mp_solutions

# ---------- Highlight detection (16-bit) ----------
def detect_blown_highlights(img):
    if img.dtype == np.uint16:
        white = 65535.0
    else:
        white = 255.0

    b, g, r = cv2.split(img.astype(np.float32))
    luminance = 0.114 * b + 0.587 * g + 0.299 * r

    threshold = 0.96 * white
    highlight_mask = (luminance > threshold).astype(np.uint8)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        highlight_mask, connectivity=8
    )

    min_area = 50
    valid_regions = []

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > min_area:
            valid_regions.append(i)

    gray = luminance / white
    lap = cv2.Laplacian(gray, cv2.CV_32F)

    gradient_variances = []
    for region_id in valid_regions:
        region_mask = (labels == region_id)
        values = lap[region_mask]
        if len(values) > 0:
            gradient_variances.append(np.var(values))

    if len(gradient_variances) == 0:
        return 0.0

    mean_variance = np.mean(gradient_variances)
    highlight_area = np.sum(highlight_mask)
    total_pixels = highlight_mask.size
    area_ratio = highlight_area / total_pixels

    score = area_ratio * (1 / (1 + mean_variance))
    return score


# ---------- Blur metrics ----------
import cv2
import numpy as np


def variance_of_laplacian(img):
    lap = cv2.Laplacian(img, cv2.CV_64F)
    score = np.var(lap)
    return score


def tenengrad(img, gradient_threshold=15):
    gx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)

    g = np.sqrt(gx ** 2 + gy ** 2)

    # suppress noise gradients
    g[g < gradient_threshold] = 0

    return np.mean(g)


def preprocess(img):
    """
    Light denoising while preserving edges
    """
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img


def blur_score(img):
    img = preprocess(img)

    scores = []

    # multi-scale evaluation reduces noise sensitivity
    for scale in [1.0, 0.5, 0.25]:

        if scale != 1.0:
            scaled = cv2.resize(img, None, fx=scale, fy=scale,
                                interpolation=cv2.INTER_AREA)
        else:
            scaled = img

        lap = variance_of_laplacian(scaled)
        ten = tenengrad(scaled)

        score = 0.6 * lap + 0.4 * ten
        scores.append(score)

    # robust aggregation
    final_score = np.median(scores)

    print(f"Blur scores per scale: {scores}")
    print(f"Final blur score: {final_score}")

    return final_score


# ---------- Blur checks ----------
def face_is_blurry(gray, bbox, w, h):
    x = int(bbox.xmin * w)
    y = int(bbox.ymin * h)
    bw = int(bbox.width * w)
    bh = int(bbox.height * h)
    face = gray[y:y + bh, x:x + bw]
    # print(f"Face size: {face.size}")
    if face.size < 100:
        return True
    score = blur_score(face)
    print(f"Face blur score: {score}")
    return score < 20


def image_is_blurry(gray):
    score = blur_score(gray)
    print(f"Blur score: {score}")
    return score < 20


# ---------- Image loading and conversion ----------
# def load_and_convert_image(path):
#     ext = os.path.splitext(path)[1].lower()
#     raw_formats = [".cr2", ".nef", ".arw", ".dng", ".raf", ".rw2"]

#     img = None

#     if ext in raw_formats:
#         try:
#             with rawpy.imread(path) as raw:
#                 rgb = raw.postprocess(output_bps=16, no_auto_bright=True)
#             img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
#             # сохраняем TIFF
#             tiff_path = os.path.splitext(path)[0] + "_converted.tiff"
#             cv2.imwrite(tiff_path, img)
#         except rawpy.LibRawFileUnsupportedError:
#             print(f"RAW файл не поддерживается: {path}")
#             return None
#         except Exception as e:
#             print(f"Ошибка при обработке RAW: {e}")
#             return None
#     else:
#         img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
#         if img is None:
#             print(f"Не удалось открыть изображение: {path}")
#             return None
#         tiff_path = os.path.splitext(path)[0] + "_converted.tiff"
#         cv2.imwrite(tiff_path, img)

#     return img


def load_raw_fast(path, downsample=4):
    with rawpy.imread(path) as raw:
        # Get Bayer RAW sensor data
        raw_img = raw.raw_image_visible.astype(np.float32)

        # Black / white levels
        black = np.mean(raw.black_level_per_channel)
        white = raw.white_level

        # Normalize to 0–1
        norm = (raw_img - black) / (white - black)
        norm = np.clip(norm, 0, 1)

        # Convert to full 16-bit
        img16 = (norm * 65535).astype(np.uint16)

        # Downsample
        if downsample > 1:
            img16 = img16[::downsample, ::downsample]

    return img16


# ---------- Main quality check ----------
def check_image_quality(path):
    ext = os.path.splitext(path)[1].lower()
    raw_formats = [".cr2", ".nef", ".arw", ".dng", ".raf", ".rw2"]

    if ext in raw_formats:
        img = load_raw_fast(path)
        img = cv2.cvtColor(img, cv2.COLOR_BAYER_BG2BGR)

    else:
        img = cv2.imread(path)

    if img is None:
        print("Не удалось загрузить изображение")
        return False

    # ---------- Highlight detection ----------
    highlight_score = detect_blown_highlights(img)
    if highlight_score > 0.1:
        print(f"Слишком много пересветов: {highlight_score}")
        return False

    # ---------- Convert to 8-bit for Mediapipe ----------
    if img.dtype == np.uint16:
        img8 = (img / 256).astype(np.uint8)
    else:
        img8 = img

    gray = cv2.cvtColor(img8, cv2.COLOR_BGR2GRAY)
    h, w = img8.shape[:2]

    mp_face = mp.solutions.face_detection
    with mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detector:
        results = face_detector.process(cv2.cvtColor(img8, cv2.COLOR_BGR2RGB))

        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                # print(face_is_blurry(gray, bbox, w, h))
                ans = False
                if face_is_blurry(gray, bbox, w, h):
                    print("Лицо размыто")
                else:
                    print("Лицо в порядке")
                    ans = True
            if not ans:
                return False

        else:
            if image_is_blurry(gray):
                print("Изображение размыто")
                return False

    return True
