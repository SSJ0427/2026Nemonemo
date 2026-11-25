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


# ---------------------------------------------------------------------------
# 조건별 합성 테스트셋 (담당: 한시원)
#
# 실제 사진(data/raw)이 모이기 전에 전처리·엣지 파라미터와 처리 해상도를 비교하기 위한 세트.
# 태그 이름은 data/README.md 의 촬영 가이드 태그와 맞췄다. 실제 사진 결과를 대신하지는 않으므로
# 파라미터 확정은 실제 사진으로 다시 확인한 뒤에 한다.
# ---------------------------------------------------------------------------

CONDITIONS = [
    "어두운배경", "밝은배경", "비슷한색배경", "그림자", "기울기큼",
    "노이즈", "흐림", "질감배경", "손가림", "저조도",
]


def random_corners(rng: np.random.Generator, size: tuple[int, int], skew: float = 0.08) -> np.ndarray:
    """화면 안쪽에 놓인 문서의 네 꼭짓점(좌상, 우상, 우하, 좌하). skew 가 클수록 많이 기울어진다."""
    w, h = size
    dh = rng.uniform(0.62, 0.80) * h          # 문서 세로 길이
    dw = dh * 210 / 297 * rng.uniform(0.95, 1.15)
    cx = w / 2 + rng.uniform(-0.08, 0.08) * w
    cy = h / 2 + rng.uniform(-0.05, 0.05) * h
    base = np.array([[-dw / 2, -dh / 2], [dw / 2, -dh / 2], [dw / 2, dh / 2], [-dw / 2, dh / 2]])
    a = np.deg2rad(rng.uniform(-12, 12))
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    pts = base @ rot.T + [cx, cy]
    pts += rng.uniform(-skew, skew, (4, 2)) * [dw, dh]   # 원근 왜곡
    margin = 0.03 * min(w, h)
    pts[:, 0] = np.clip(pts[:, 0], margin, w - 1 - margin)
    pts[:, 1] = np.clip(pts[:, 1], margin, h - 1 - margin)
    return pts.astype(np.float32)


def _background(rng: np.random.Generator, size: tuple[int, int], lo: int, hi: int,
                texture: bool = False) -> np.ndarray:
    w, h = size
    bg = rng.integers(lo, hi, (h, w, 3), dtype=np.uint8)
    bg = cv2.GaussianBlur(bg, (0, 0), 3)
    if texture:  # 나뭇결 책상처럼 가는 줄무늬 + 잔무늬
        y = np.arange(h, dtype=np.float32)[:, None]
        x = np.arange(w, dtype=np.float32)[None, :]
        stripes = 22 * np.sin(y / 3.0 + 4 * np.sin(x / 90.0))
        grain = rng.normal(0, 14, (h, w)).astype(np.float32)
        bg = np.clip(bg.astype(np.float32) + (stripes + grain)[..., None], 0, 255).astype(np.uint8)
    return bg


def make_scene(condition: str, seed: int = 0, size: tuple[int, int] = (1920, 1440)
               ) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """조건 하나에 해당하는 합성 사진을 만든다.

    Returns:
        photo: BGR 이미지, corners: 정답 꼭짓점 (4, 2) 원본 픽셀 좌표, tags: 조건 태그 목록
    """
    if condition not in CONDITIONS:
        raise ValueError(f"알 수 없는 조건: {condition}")
    rng = np.random.default_rng(1000 * (CONDITIONS.index(condition) + 1) + seed)
    w, h = size
    corners = random_corners(rng, size, skew=0.20 if condition == "기울기큼" else 0.08)

    bg_range = {"밝은배경": (150, 190), "비슷한색배경": (205, 225)}.get(condition, (55, 100))
    bg = _background(rng, size, *bg_range, texture=condition == "질감배경")

    doc = make_document(seed=seed)
    dh, dw = doc.shape[:2]
    src = np.array([[0, 0], [dw - 1, 0], [dw - 1, dh - 1], [0, dh - 1]], np.float32)
    m = cv2.getPerspectiveTransform(src, corners)
    warped = cv2.warpPerspective(doc, m, (w, h), flags=cv2.INTER_LINEAR)
    mask = cv2.warpPerspective(np.full((dh, dw), 255, np.uint8), m, (w, h))
    photo = np.where(mask[..., None] > 0, warped, bg).astype(np.float32)

    # 조명: 기본은 약한 한쪽 그림자, '그림자'는 강하게, '저조도'는 전체적으로 어둡게
    strength = {"그림자": 0.60, "저조도": 0.20}.get(condition, 0.25)
    direction = rng.uniform(0, 2 * np.pi)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = ((xx - w / 2) * np.cos(direction) + (yy - h / 2) * np.sin(direction)) / max(w, h) + 0.5
    photo *= (1.0 - strength * np.clip(t, 0, 1))[..., None]
    if condition == "저조도":
        photo *= 0.35

    if condition == "손가림":  # 손가락이 한쪽 꼭짓점 근처를 가린다
        k = int(rng.integers(0, 4))
        out = corners[k] - corners.mean(axis=0)
        out /= np.linalg.norm(out)
        axes = (int(0.035 * w), int(0.10 * h))      # (손가락 반폭, 반길이)
        cx, cy = corners[k] + out * axes[1] * 0.35   # 손가락 끝이 꼭짓점을 덮도록 바깥에서 들어온다
        angle = float(np.degrees(np.arctan2(out[1], out[0]))) - 90
        cv2.ellipse(photo, (int(cx), int(cy)), axes, angle, 0, 360, (120, 150, 200), -1)

    if condition in ("노이즈", "저조도"):
        sigma = 12 if condition == "노이즈" else 6
        photo += rng.normal(0, sigma, photo.shape).astype(np.float32)
    photo = np.clip(photo, 0, 255).astype(np.uint8)

    if condition == "흐림":  # 손떨림(모션) 블러
        k = 15
        kernel = np.zeros((k, k), np.float32)
        cv2.line(kernel, (0, k // 2), (k - 1, k // 2), 1.0, 1)
        rot = cv2.getRotationMatrix2D((k / 2 - 0.5, k / 2 - 0.5), float(rng.uniform(0, 180)), 1.0)
        kernel = cv2.warpAffine(kernel, rot, (k, k))
        photo = cv2.filter2D(photo, -1, kernel / kernel.sum())

    return photo, corners, [condition]


def make_condition_set(per_condition: int = 6, size: tuple[int, int] = (1920, 1440)):
    """CONDITIONS 각각 per_condition 장씩 만든다. [(이름, 사진, 정답 꼭짓점, 태그)]"""
    out = []
    for cond in CONDITIONS:
        for i in range(per_condition):
            img, corners, tags = make_scene(cond, seed=i, size=size)
            out.append((f"syn_{CONDITIONS.index(cond):02d}_{i:02d}.jpg", img, corners, tags))
    return out
