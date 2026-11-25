"""2단계: 엣지 검출 (담당: 한시원)

앱(Dart)의 lib/pipeline/edges.dart 와 같은 동작을 유지할 것.
"""
from __future__ import annotations

import cv2
import numpy as np

# 중앙값 기반 자동 임계값의 폭. lower = (1 - SIGMA) * median, upper = (1 + SIGMA) * median
# (11.25 실험 이후 기본 방식은 Otsu. 비교 실험용으로 남겨 둔다)
SIGMA = 0.33

# 기본 Canny 임계값: upper = Otsu 임계값, lower = upper * OTSU_LOW_RATIO
# 근거: docs/실험기록/edge_블러_임계값_모폴로지.md (밝은·비슷한색 배경에서 중앙값 방식은 임계값이 너무 높아짐)
OTSU_LOW_RATIO = 0.5

# 화면이 거의 균일해 Otsu 값이 0 근처로 떨어질 때 잡음까지 엣지가 되는 것을 막는 upper 하한
CANNY_MIN_UPPER = 30

# 끊어진 엣지를 잇기 위한 모폴로지 커널 크기
MORPH_KSIZE = 3


def auto_canny_thresholds(gray: np.ndarray, sigma: float = SIGMA) -> tuple[int, int]:
    """밝기 중앙값을 기준으로 Canny 임계값을 자동으로 정한다."""
    median = float(np.median(gray))
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    return lower, upper


def otsu_canny_thresholds(gray: np.ndarray, low_ratio: float = OTSU_LOW_RATIO) -> tuple[int, int]:
    """Otsu 이진화 임계값(문서와 배경을 가르는 밝기)을 Canny upper 로 쓴다."""
    t, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    upper = max(int(t), CANNY_MIN_UPPER)
    return int(upper * low_ratio), upper


def detect_edges(gray: np.ndarray) -> np.ndarray:
    """그레이스케일 이미지에서 문서 경계 엣지 맵(0/255)을 만든다."""
    lower, upper = otsu_canny_thresholds(gray)
    edges = cv2.Canny(gray, lower, upper)

    # 모폴로지는 none/close3/dilate3/close5+dilate3 와 비교해 차이가 없어(실험기록 참고) 현재 방식 유지
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (MORPH_KSIZE, MORPH_KSIZE))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.dilate(edges, kernel, iterations=1)
    return edges
