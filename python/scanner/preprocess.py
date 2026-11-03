"""1단계: 전처리 (담당: 한시원)

라이브 루프에서 매 프레임 호출되므로 속도가 중요하다.
앱(Dart)의 lib/pipeline/preprocess.dart 와 같은 동작을 유지할 것.
"""
from __future__ import annotations

import cv2
import numpy as np

# 처리용 이미지의 긴 변 길이(px). 속도/정확도 트레이드오프 실험 대상.
PROCESS_SIZE = 480

# 블러 커널 크기. 실험 대상 (3, 5, 7 ...).
BLUR_KSIZE = 5


def preprocess(img: np.ndarray, process_size: int = PROCESS_SIZE) -> tuple[np.ndarray, float]:
    """원본 이미지를 처리용 그레이스케일 이미지로 변환한다.

    Args:
        img: BGR(3채널) 또는 그레이스케일(1채널) 이미지.
             앱에서는 카메라 YUV의 Y 평면이 이미 그레이스케일이므로 1채널로 들어온다.
        process_size: 리사이즈 후 긴 변 길이.

    Returns:
        gray: 리사이즈 + 블러가 적용된 그레이스케일 이미지
        ratio: 원본 크기 / 처리 크기. 처리 이미지에서 찾은 좌표에 곱하면 원본 좌표가 된다.
    """
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    h, w = gray.shape[:2]
    ratio = max(h, w) / float(process_size)
    if ratio > 1.0:
        gray = cv2.resize(gray, (round(w / ratio), round(h / ratio)), interpolation=cv2.INTER_AREA)
    else:
        ratio = 1.0

    # TODO(한시원): GaussianBlur / medianBlur / bilateralFilter 비교 실험
    gray = cv2.GaussianBlur(gray, (BLUR_KSIZE, BLUR_KSIZE), 0)
    return gray, ratio
