"""[전성재] 테스트셋 평가

data/raw 의 사진을 전체 파이프라인으로 처리하고, data/labels.json 의 정답 꼭짓점과 비교한다.
성공 기준: 네 꼭짓점의 평균 오차가 문서 대각선 길이의 SUCCESS_RATIO 이하.
labels.json 의 tags(배경/조명/각도 등)로 조건별 성공률도 계산한다.

사용법:  python evaluate.py
결과:    results/evaluation.csv, 콘솔 요약
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from scanner import scan_frame  # noqa: E402

LABELS = ROOT / "data" / "labels.json"
SUCCESS_RATIO = 0.02


def load_labels() -> dict[str, dict]:
    if not LABELS.exists():
        return {}
    return {item["image"]: item for item in json.loads(LABELS.read_text(encoding="utf-8"))["images"]}


def corner_error(found: np.ndarray, gt: np.ndarray) -> float:
    """평균 꼭짓점 오차 / 대각선 길이"""
    diag = max(np.linalg.norm(gt[2] - gt[0]), np.linalg.norm(gt[3] - gt[1]))
    return float(np.linalg.norm(found - gt, axis=1).mean() / diag)


def is_success(found: np.ndarray | None, label: dict | None) -> bool:
    if found is None:
        return False
    if label is None:  # 정답이 없으면 검출 여부만 본다
        return True
    return corner_error(found, np.array(label["corners"], np.float32)) <= SUCCESS_RATIO


def main() -> None:
    images = sorted((ROOT / "data" / "raw").glob("*.jp*g"))
    labels = load_labels()
    if not images:
        print("data/raw 에 사진이 없습니다. data/README.md 참고")
        return

    rows, by_tag = [], defaultdict(lambda: [0, 0])
    for path in images:
        fr = scan_frame(cv2.imread(str(path)))
        label = labels.get(path.name)
        ok = is_success(fr.corners_full, label)
        err = (corner_error(fr.corners_full, np.array(label["corners"], np.float32))
               if fr.corners is not None and label else None)
        tags = label.get("tags", []) if label else []
        rows.append({"image": path.name, "detected": fr.corners is not None, "success": ok,
                     "error_ratio": None if err is None else round(err, 4), "tags": "|".join(tags)})
        for t in tags or ["(태그 없음)"]:
            by_tag[t][0] += ok
            by_tag[t][1] += 1

    out = ROOT / "python" / "results"
    out.mkdir(exist_ok=True)
    with open(out / "evaluation.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    total_ok = sum(r["success"] for r in rows)
    print(f"전체 성공률: {total_ok}/{len(rows)} = {total_ok / len(rows):.1%}  (정답 있는 사진 {len(labels)}장)")
    for tag, (ok, n) in sorted(by_tag.items()):
        print(f"  {tag:<16} {ok}/{n} = {ok / n:.1%}")
    print(f"→ {out / 'evaluation.csv'}")


if __name__ == "__main__":
    main()
