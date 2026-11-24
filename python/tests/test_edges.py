"""엣지 검출(Otsu 기반 Canny 임계값)과 조건별 합성 세트 검사 (담당: 한시원)"""
import numpy as np
import pytest

from evaluate import SUCCESS_RATIO, corner_error
from scanner import detect_edges, find_document, order_corners, preprocess
from scanner.edges import CANNY_MIN_UPPER, OTSU_LOW_RATIO, otsu_canny_thresholds
from scanner.synthetic import CONDITIONS, make_scene


def test_otsu_thresholds_have_floor_on_flat_image():
    flat = np.full((120, 160), 90, np.uint8)
    lower, upper = otsu_canny_thresholds(flat)
    assert upper == CANNY_MIN_UPPER
    assert lower == int(CANNY_MIN_UPPER * OTSU_LOW_RATIO)


def test_otsu_thresholds_follow_document_background_split():
    img = np.full((100, 100), 60, np.uint8)
    img[20:80, 20:80] = 240
    lower, upper = otsu_canny_thresholds(img)
    assert 60 <= upper < 240
    assert lower == int(upper * OTSU_LOW_RATIO)


@pytest.mark.parametrize("condition", CONDITIONS)
def test_make_scene_corners_inside_image(condition):
    img, corners, tags = make_scene(condition, seed=0, size=(640, 480))
    assert img.shape == (480, 640, 3)
    assert tags == [condition]
    assert np.all(corners >= 0) and np.all(corners[:, 0] < 640) and np.all(corners[:, 1] < 480)
    np.testing.assert_allclose(order_corners(corners), corners)


# 손가림은 detect 대안 단계(PR #1) 범위라 제외
@pytest.mark.parametrize("condition", [c for c in CONDITIONS if c != "손가림"])
def test_detects_document_in_condition_scene(condition):
    img, gt, _ = make_scene(condition, seed=0)
    gray, ratio = preprocess(img)
    corners = find_document(detect_edges(gray))
    assert corners is not None, f"{condition}: 검출 실패"
    assert corner_error(order_corners(corners) * ratio, gt) <= SUCCESS_RATIO
