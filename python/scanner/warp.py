"""5단계: 원근 변환 (담당: 채성우)

촬영 시 한 번, 원본 고해상도 이미지에 적용한다.
앱(Dart)의 lib/pipeline/warp.dart 와 같은 동작을 유지할 것.
"""
from __future__ import annotations

import cv2
import numpy as np


def warp_document(img: np.ndarray, corners: np.ndarray) -> np.ndarray:
    """정렬된 꼭짓점(좌상, 우상, 우하, 좌하; 원본 좌표계)으로 문서를 정면 시점으로 편다."""
    tl, tr, br, bl = np.asarray(corners, dtype=np.float32)

    width = int(round(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))))
    height = int(round(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))))
    width, height = max(width, 1), max(height, 1)

    # TODO(채성우): A4 등 표준 비율로 맞추는 옵션 검토
    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
                   dtype=np.float32)
    m = cv2.getPerspectiveTransform(np.array([tl, tr, br, bl], dtype=np.float32), dst)
    return cv2.warpPerspective(img, m, (width, height), flags=cv2.INTER_LINEAR)
