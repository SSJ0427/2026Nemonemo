"""6단계: 화질 개선 (담당: 채성우)

앱(Dart)의 lib/pipeline/enhance.dart 와 같은 동작을 유지할 것.
"""
from __future__ import annotations

import cv2
import numpy as np

MODES = ("color", "gray", "global", "otsu", "adaptive")

SHADOW_KSIZE = 25
ADAPTIVE_BLOCK = 31
ADAPTIVE_C = 15
GLOBAL_THRESH = 127


def remove_shadow(gray: np.ndarray, ksize: int = SHADOW_KSIZE) -> np.ndarray:
    """모폴로지 닫힘으로 배경(조명)을 추정하고 원본을 나누어 그림자를 제거한다."""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
    background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    background = cv2.medianBlur(background, 21)
    return cv2.divide(gray, background, scale=255)


def enhance(warped: np.ndarray, mode: str = "adaptive") -> np.ndarray:
    """보정된 문서 이미지의 화질을 개선한다.

    mode:
        color    - 컬러 유지 (밝기만 보정)
        gray     - 그림자 제거된 그레이스케일
        global   - 전역 임계값 이진화
        otsu     - Otsu 이진화
        adaptive - 적응형 이진화
    """
    if mode not in MODES:
        raise ValueError(f"mode 는 {MODES} 중 하나여야 합니다: {mode!r}")

    if mode == "color":
        if warped.ndim == 2:
            return warped
        # TODO(채성우): 컬러 모드 개선 (LAB 의 L 채널만 그림자 제거 등)
        lab = cv2.cvtColor(warped, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        lab = cv2.merge([remove_shadow(l), a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY) if warped.ndim == 3 else warped
    flat = remove_shadow(gray)

    if mode == "gray":
        return flat
    if mode == "global":
        return cv2.threshold(flat, GLOBAL_THRESH, 255, cv2.THRESH_BINARY)[1]
    if mode == "otsu":
        return cv2.threshold(flat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return cv2.adaptiveThreshold(flat, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, ADAPTIVE_BLOCK, ADAPTIVE_C)
