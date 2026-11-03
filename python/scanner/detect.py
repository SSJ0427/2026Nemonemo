"""3~4단계: 문서 영역 검출 + 꼭짓점 정렬 (담당: 신승준)

앱(Dart)의 lib/pipeline/detect.dart 와 같은 동작을 유지할 것.
"""
from __future__ import annotations

import cv2
import numpy as np

# 문서로 인정할 최소 면적 (처리 이미지 면적 대비 비율)
MIN_AREA_RATIO = 0.10

# approxPolyDP 의 epsilon = APPROX_EPS * 둘레
APPROX_EPS = 0.02

# 면적 상위 몇 개의 윤곽선만 검사할지
TOP_K = 5


def find_document(edges: np.ndarray) -> np.ndarray | None:
    """엣지 맵에서 문서(꼭짓점 4개인 볼록 다각형)를 찾는다.

    Returns:
        corners: float32 (4, 2) 배열, 처리 이미지 좌표계. 정렬되지 않은 상태.
        못 찾으면 None.
    """
    h, w = edges.shape[:2]
    min_area = MIN_AREA_RATIO * h * w

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:TOP_K]

    for c in contours:
        if cv2.contourArea(c) < min_area:
            break
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, APPROX_EPS * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            return approx.reshape(4, 2).astype(np.float32)

    # TODO(신승준): 4각형이 안 나올 때 convexHull / minAreaRect 로 근사하는 대안
    return None


def order_corners(corners: np.ndarray) -> np.ndarray:
    """꼭짓점을 좌상, 우상, 우하, 좌하 순서로 정렬한다.

    좌상: x+y 최소, 우하: x+y 최대, 우상: y-x 최소, 좌하: y-x 최대
    """
    pts = np.asarray(corners, dtype=np.float32).reshape(4, 2)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()  # y - x
    return np.array(
        [pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]],
        dtype=np.float32,
    )
