"""[한시원] 블러 종류 × Canny 임계값 폭 비교 실험

테스트셋(data/raw)의 모든 사진에 대해 조합별 검출 성공 여부와 처리 시간을 기록한다.
정답이 있으면(data/labels.json) 꼭짓점 오차로 성공을 판정하고, 없으면 '4각형 검출 여부'만 본다.

사용법:  python experiments/edge_params.py
결과:    results/edge_params.csv
"""
import csv
import itertools
import sys
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from evaluate import is_success, load_labels  # noqa: E402
from scanner import detect, edges, order_corners  # noqa: E402
from scanner.preprocess import PROCESS_SIZE  # noqa: E402

BLURS = {
    "gaussian5": lambda g: cv2.GaussianBlur(g, (5, 5), 0),
    "median5": lambda g: cv2.medianBlur(g, 5),
    "bilateral": lambda g: cv2.bilateralFilter(g, 9, 75, 75),
}
SIGMAS = [0.2, 0.33, 0.5]


def resize_gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    ratio = max(h, w) / PROCESS_SIZE
    return cv2.resize(gray, (round(w / ratio), round(h / ratio)), interpolation=cv2.INTER_AREA), ratio


def main() -> None:
    images = sorted((ROOT / "data" / "raw").glob("*.jp*g"))
    if not images:
        print("data/raw 에 사진이 없습니다. data/README.md 참고")
        return
    labels = load_labels()
    out = ROOT / "python" / "results"
    out.mkdir(exist_ok=True)

    rows = []
    for (blur_name, blur), sigma in itertools.product(BLURS.items(), SIGMAS):
        edges.SIGMA = sigma
        ok, times = 0, []
        for path in images:
            gray, ratio = resize_gray(cv2.imread(str(path)))
            t0 = time.perf_counter()
            corners = detect.find_document(edges.detect_edges(blur(gray)))
            times.append((time.perf_counter() - t0) * 1000)
            found = None if corners is None else order_corners(corners) * ratio
            ok += is_success(found, labels.get(path.name))
        rows.append({"blur": blur_name, "sigma": sigma, "success": ok, "total": len(images),
                     "rate": round(ok / len(images), 3), "ms_mean": round(float(np.mean(times)), 2)})
        print(rows[-1])

    with open(out / "edge_params.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"→ {out / 'edge_params.csv'}")


if __name__ == "__main__":
    main()
