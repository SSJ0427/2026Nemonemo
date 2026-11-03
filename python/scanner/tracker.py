"""실시간 안정화: 프레임 간 꼭짓점 흔들림 보정 + 자동 촬영 판단 (담당: 신승준)

앱(Dart)의 lib/pipeline/tracker.dart 와 같은 동작을 유지할 것.
Python 에서는 동영상 파일이나 연속 사진으로 실험한다 (experiments/tracker_video.py).
"""
from __future__ import annotations

import numpy as np


class CornerTracker:
    """정렬된 꼭짓점(4, 2)을 프레임마다 받아 부드럽게 만들고, 안정 여부를 알려준다.

    Args:
        alpha: EMA 가중치. 클수록 새 프레임을 많이 반영(반응 빠름, 흔들림 큼).
        move_tol: 이 값(px, 처리 이미지 기준)보다 적게 움직이면 '정지'로 본다.
        stable_frames: 연속으로 정지한 프레임이 이만큼 쌓이면 is_stable=True.
        max_missed: 검출 실패가 이만큼 연속되기 전까지는 이전 결과를 유지.
    """

    def __init__(self, alpha: float = 0.5, move_tol: float = 4.0,
                 stable_frames: int = 10, max_missed: int = 5) -> None:
        self.alpha = alpha
        self.move_tol = move_tol
        self.stable_frames = stable_frames
        self.max_missed = max_missed
        self.reset()

    def reset(self) -> None:
        self.smoothed: np.ndarray | None = None
        self.still_count = 0
        self.missed = 0

    def update(self, corners: np.ndarray | None) -> tuple[np.ndarray | None, bool]:
        """새 프레임의 검출 결과를 반영한다.

        Returns:
            smoothed: 보정된 꼭짓점 (없으면 None)
            is_stable: 자동 촬영해도 될 만큼 안정적인지
        """
        if corners is None:
            self.missed += 1
            self.still_count = 0
            if self.missed > self.max_missed:
                self.smoothed = None
            return self.smoothed, False

        corners = np.asarray(corners, dtype=np.float32)
        self.missed = 0

        if self.smoothed is None:
            self.smoothed = corners.copy()
            self.still_count = 0
            return self.smoothed, False

        # TODO(신승준): 칼만 필터 등 다른 보정 방식, 갑자기 다른 사각형으로 바뀌는 경우 처리
        movement = float(np.max(np.linalg.norm(corners - self.smoothed, axis=1)))
        self.smoothed = self.alpha * corners + (1.0 - self.alpha) * self.smoothed

        self.still_count = self.still_count + 1 if movement < self.move_tol else 0
        return self.smoothed, self.still_count >= self.stable_frames
