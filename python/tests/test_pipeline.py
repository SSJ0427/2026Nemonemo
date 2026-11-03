import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from scanner import (CornerTracker, detect_edges, enhance, find_document, order_corners,
                     preprocess, scan, warp_document)
from scanner.synthetic import DEFAULT_CORNERS, make_photo

GOLDEN = Path(__file__).resolve().parents[2] / "data" / "golden"


@pytest.fixture
def photo():
    return make_photo(DEFAULT_CORNERS)


def test_preprocess_resizes_and_returns_ratio(photo):
    gray, ratio = preprocess(photo)
    assert gray.ndim == 2
    assert max(gray.shape) == 480
    assert ratio == pytest.approx(1200 / 480)


def test_preprocess_accepts_gray_input(photo):
    gray, _ = preprocess(cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY))
    assert gray.ndim == 2


def test_detects_document_corners(photo):
    gray, ratio = preprocess(photo)
    corners = find_document(detect_edges(gray))
    assert corners is not None
    found = order_corners(corners) * ratio
    err = np.linalg.norm(found - DEFAULT_CORNERS, axis=1).max()
    assert err < 15, f"꼭짓점 오차 {err:.1f}px"


def test_no_document_returns_none():
    blank = np.full((600, 800, 3), 80, np.uint8)
    gray, _ = preprocess(blank)
    assert find_document(detect_edges(gray)) is None


def test_order_corners_any_input_order():
    tl, tr, br, bl = DEFAULT_CORNERS
    shuffled = np.array([br, tl, bl, tr])
    np.testing.assert_allclose(order_corners(shuffled), DEFAULT_CORNERS)


def test_warp_output_size():
    img = np.zeros((900, 1200, 3), np.uint8)
    out = warp_document(img, DEFAULT_CORNERS)
    tl, tr, br, bl = DEFAULT_CORNERS
    expected_w = round(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    expected_h = round(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    assert out.shape[:2] == (expected_h, expected_w)


@pytest.mark.parametrize("mode", ["color", "gray", "global", "otsu", "adaptive"])
def test_enhance_modes(photo, mode):
    out = enhance(photo, mode)
    if mode == "color":
        assert out.ndim == 3
    else:
        assert out.ndim == 2
    if mode in ("global", "otsu", "adaptive"):
        assert set(np.unique(out)) <= {0, 255}


def test_full_scan(photo):
    result, fr = scan(photo)
    assert result is not None
    assert fr.corners_full is not None


def test_tracker_becomes_stable_and_survives_dropouts():
    t = CornerTracker(stable_frames=5, max_missed=2)
    stable = False
    for _ in range(10):
        _, stable = t.update(DEFAULT_CORNERS + np.random.uniform(-1, 1, (4, 2)))
    assert stable
    smoothed, stable = t.update(None)  # 한 프레임 놓쳐도 결과 유지
    assert smoothed is not None and not stable
    for _ in range(3):
        smoothed, _ = t.update(None)
    assert smoothed is None


@pytest.mark.skipif(not (GOLDEN / "golden.json").exists(), reason="골든 데이터 없음")
def test_golden_matches():
    """Dart 구현(app/test/golden_test.dart)과 같은 기준 데이터로 비교한다."""
    spec = json.loads((GOLDEN / "golden.json").read_text(encoding="utf-8"))
    for case in spec["cases"]:
        img = cv2.imread(str(GOLDEN / case["image"]))
        gray, ratio = preprocess(img)
        corners = find_document(detect_edges(gray))
        assert corners is not None, case["image"]
        found = order_corners(corners) * ratio
        err = np.linalg.norm(found - np.array(case["corners"]), axis=1).max()
        assert err < spec["tolerance_px"], f'{case["image"]}: {err:.1f}px'
