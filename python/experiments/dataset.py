"""[한시원] 실험 공용 데이터 로더

- data/raw 에 사진이 있으면 그 사진과 data/labels.json 의 정답·태그를 쓴다.
- 없거나 --synthetic 을 주면 scanner.synthetic.make_condition_set() 의 조건별 합성 사진을 쓴다.

각 항목은 (이름, BGR 이미지, 정답 꼭짓점 또는 None, 태그 목록).
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from evaluate import load_labels  # noqa: E402
from scanner.synthetic import make_condition_set  # noqa: E402


def load_dataset(synthetic: bool = False, per_condition: int = 6):
    """(항목 목록, 출처 설명)을 돌려준다."""
    images = [] if synthetic else sorted((ROOT / "data" / "raw").glob("*.jp*g"))
    if images:
        labels = load_labels()
        items = []
        for path in images:
            label = labels.get(path.name)
            gt = None if label is None else np.array(label["corners"], np.float32)
            items.append((path.name, cv2.imread(str(path)), gt, label.get("tags", []) if label else []))
        return items, f"data/raw 실제 사진 {len(items)}장 (정답 {sum(i[2] is not None for i in items)}장)"
    items = make_condition_set(per_condition)
    return items, f"합성 조건별 사진 {len(items)}장 (조건 {len(items) // per_condition}종 x {per_condition}장, 1920x1440)"


def wants_synthetic() -> bool:
    return "--synthetic" in sys.argv
