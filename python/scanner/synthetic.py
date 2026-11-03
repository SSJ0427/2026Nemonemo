"""테스트용 합성 문서 사진 생성기.

실제 테스트셋이 모이기 전에도 파이프라인을 검증할 수 있게, 기울어진 문서 사진을 만들어 준다.
Python/Dart 결과 비교용 골든 데이터(data/golden)도 이걸로 만든다.
"""
from __future__ import annotations

import cv2
import numpy as np


def make_document(width: int = 420, height: int = 594, seed: int = 0) -> np.ndarray:
    """글줄이 있는 흰 문서 이미지(BGR)"""
    rng = np.random.default_rng(seed)
    doc = np.full((height, width, 3), 245, np.uint8)
    y = 50
    while y < height - 40:
        x = 40
        while x < width - 60:
            w = int(rng.integers(20, 70))
            cv2.rectangle(doc, (x, y), (min(x + w, width - 40), y + 10), (40, 40, 40), -1)
            x += w + 12
        y += 28
    return doc


def make_photo(corners: np.ndarray, size: tuple[int, int] = (1200, 900), seed: int = 0,
               shadow: bool = True) -> np.ndarray:
    """문서를 corners(좌상, 우상, 우하, 좌하) 위치에 원근 변환으로 붙인 '사진'을 만든다.

    size: (width, height)
    """
    rng = np.random.default_rng(seed)
    w, h = size
    bg = rng.integers(60, 100, (h, w, 3), dtype=np.uint8)
    bg = cv2.GaussianBlur(bg, (0, 0), 3)

    doc = make_document(seed=seed)
    dh, dw = doc.shape[:2]
    src = np.array([[0, 0], [dw - 1, 0], [dw - 1, dh - 1], [0, dh - 1]], np.float32)
    m = cv2.getPerspectiveTransform(src, np.asarray(corners, np.float32))
    warped = cv2.warpPerspective(doc, m, (w, h))
    mask = cv2.warpPerspective(np.full((dh, dw), 255, np.uint8), m, (w, h))
    photo = np.where(mask[..., None] > 0, warped, bg)

    if shadow:  # 한쪽이 어두워지는 조명
        grad = np.linspace(1.0, 0.55, w, dtype=np.float32)[None, :, None]
        photo = np.clip(photo.astype(np.float32) * grad, 0, 255).astype(np.uint8)
    return photo


DEFAULT_CORNERS = np.array([[310, 140], [880, 190], [960, 800], [230, 760]], np.float32)
