"""2단계: 엣지 검출 (담당: 한시원)

앱(Dart)의 lib/pipeline/edges.dart 와 같은 동작을 유지할 것.
"""
from __future__ import annotations

import cv2
import numpy as np

# 중앙값 기반 자동 임계값의 폭. lower = (1 - SIGMA) * median, upper = (1 + SIGMA) * median
SIGMA = 0.33

# 끊어진 엣지를 잇기 위한 모폴로지 커널 크기
MORPH_KSIZE = 3


def auto_canny_thresholds(gray: np.ndarray, sigma: float = SIGMA) -> tuple[int, int]:
    """밝기 중앙값을 기준으로 Canny 임계값을 자동으로 정한다."""
    median = float(np.median(gray))
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    return lower, upper


def detect_edges(gray: np.ndarray) -> np.ndarray:
    """그레이스케일 이미지에서 문서 경계 엣지 맵(0/255)을 만든다."""
    lower, upper = auto_canny_thresholds(gray)
    edges = cv2.Canny(gray, lower, upper)

    # TODO(한시원): dilate vs morphologyEx(CLOSE), 커널 크기/반복 횟수 비교 실험
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (MORPH_KSIZE, MORPH_KSIZE))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.dilate(edges, kernel, iterations=1)
    return edges
